"""Evaluate Elo and existing Poisson predictions on identical held-out fixtures.

Requires the historical CSV and JSON journal produced by the existing backtest.
The validation period selects Elo hyperparameters; the test season stays unseen.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from football_intel.backtest import score_forecast
from football_intel.data import load_matches
from football_intel.elo import select_config, walk_forward_elo


DEFAULT_CSV = Path(
    "data/openfootball/epl_2021_2025/processed/"
    "epl_2021-22_2022-23_2023-24_2024-25.csv"
)
DEFAULT_JOURNAL = Path("outputs/epl_2024_25_evaluation.json")
DEFAULT_OUTPUT = Path("outputs/elo_comparison.json")
OUTCOMES = ("home_win", "draw", "away_win")


def summarise(rows: list[dict], field: str) -> dict[str, float]:
    n = len(rows)
    brier = sum(score_forecast(r[field], r["actual"])[0] for r in rows) / n
    log_loss = sum(score_forecast(r[field], r["actual"])[1] for r in rows) / n
    correct = sum(
        max(OUTCOMES, key=r[field].__getitem__)
        == {"H": "home_win", "D": "draw", "A": "away_win"}[r["actual"]]
        for r in rows
    )
    return {"brier": round(brier, 6), "log_loss": round(log_loss, 6),
            "top_outcome_accuracy": round(correct / n, 6)}


def compare(matches_csv: Path, poisson_journal: Path, validation_from: date,
            test_from: date) -> dict:
    matches = load_matches(matches_csv)
    journal = json.loads(poisson_journal.read_text(encoding="utf-8"))
    records = journal.get("individual_forecasts")
    if not isinstance(records, list) or not records:
        raise ValueError("Poisson backtest journal lacks individual forecasts")
    if journal.get("test_from") != test_from.isoformat():
        raise ValueError("Poisson journal test_from differs; rerun the original backtest")

    chosen, grid = select_config(matches, validation_from, test_from)
    elo_predictions = walk_forward_elo(matches, chosen)
    test_matches = [m for m in matches if m.date >= test_from]
    actuals = {}
    for m in test_matches:
        key = (m.date.isoformat(), f"{m.home_team} vs {m.away_team}")
        if key in actuals:
            raise ValueError(f"Duplicate match {key}")
        actuals[key] = m.outcome

    poisson_rows = {}
    for row in records:
        key = (row["date"], row["fixture"])
        if key in poisson_rows:
            raise ValueError(f"Repeated Poisson journal entry {key}")
        poisson_rows[key] = row
    if set(actuals) != set(poisson_rows):
        missing = sorted(set(actuals) - set(poisson_rows))[:3]
        extra = sorted(set(poisson_rows) - set(actuals))[:3]
        raise ValueError(f"Journal and match CSV disagree; missing={missing}, unexpected={extra}")

    rows = []
    for key in sorted(actuals):
        record = poisson_rows[key]
        if record["actual"] != actuals[key]:
            raise ValueError(f"Incorrect actual outcome in journal for {key}")
        p = record["forecast"]
        for outcome in OUTCOMES:
            if outcome not in p:
                raise ValueError(f"Missing Poisson probability {outcome} for {key}")
        rows.append({"date": key[0], "fixture": key[1],
                     "actual": actuals[key],
                     "elo": elo_predictions[key],
                     "poisson": {outcome: p[outcome] for outcome in OUTCOMES}})

    elo = summarise(rows, "elo")
    poisson = summarise(rows, "poisson")
    return {
        "project": "AnalyzNow AI", "method": "Strict date-based walk-forward Elo vs Poisson",
        "validation_from": validation_from.isoformat(), "test_from": test_from.isoformat(),
        "evaluation_matches": len(rows),
        "elo_settings_selected_using_validation_only": {
            "k_factor": chosen.k_factor, "home_advantage": chosen.home_advantage,
        },
        "validation_candidates": grid,
        "held_out_results": {"elo": elo, "poisson": poisson},
        "difference_elo_minus_poisson": {
            "brier": round(elo["brier"] - poisson["brier"], 6),
            "log_loss": round(elo["log_loss"] - poisson["log_loss"], 6),
            "top_outcome_accuracy": round(elo["top_outcome_accuracy"] - poisson["top_outcome_accuracy"], 6),
        },
        "interpretation": "Lower Brier and log loss are better. A single season cannot establish robust superiority."
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="AnalyzNow AI: independent Elo model benchmark")
    parser.add_argument("--matches", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--poisson-journal", type=Path, default=DEFAULT_JOURNAL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validation-from", type=date.fromisoformat, default=date(2023, 8, 1))
    parser.add_argument("--test-from", type=date.fromisoformat, default=date(2024, 8, 1))
    args = parser.parse_args()
    result = compare(args.matches, args.poisson_journal, args.validation_from, args.test_from)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\nAnalyzNow AI — held-out Elo comparison")
    print(f"Validation begins: {result['validation_from']} (settings selected here only)")
    print(f"Test begins:       {result['test_from']} ({result['evaluation_matches']} matches)")
    print("Selected Elo configuration:", result["elo_settings_selected_using_validation_only"])
    print("\n                         Brier       Log loss     Outcome accuracy")
    for name, metrics in result["held_out_results"].items():
        print(f"{name:<24} {metrics['brier']:>8.6f}    {metrics['log_loss']:>8.6f}        {metrics['top_outcome_accuracy']:.1%}")
    difference = result["difference_elo_minus_poisson"]
    print(f"Elo minus Poisson: Brier {difference['brier']:+.6f}, log loss {difference['log_loss']:+.6f}")
    print("Lower Brier and log loss are better. This is one held-out season, not a production claim.")
    print(f"Full evaluation saved to {args.output}")


if __name__ == "__main__":
    main()
