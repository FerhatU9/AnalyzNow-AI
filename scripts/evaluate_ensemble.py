"""Exploratory fixed 50:50 Elo/Poisson ensemble on matched past fixtures.

This follows earlier held-out comparisons. Because their test-season scores have
already been inspected, treat this as research, NOT independent confirmation.
Run from the project root: python -m scripts.evaluate_ensemble
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path

from football_intel.backtest import score_forecast
from football_intel.data import load_matches
from football_intel.elo import select_config, walk_forward_elo
from scripts.evaluate_elo_uncertainty import bootstrap_by_date

OUTCOMES = ("home_win", "draw", "away_win")
ACTUAL_TO_OUTCOME = {"H": "home_win", "D": "draw", "A": "away_win"}
DEFAULT_CSV = Path(
    "data/openfootball/epl_2021_2025/processed/"
    "epl_2021-22_2022-23_2023-24_2024-25.csv"
)
DEFAULT_POISSON = Path("outputs/epl_2024_25_evaluation.json")
DEFAULT_OUTPUT = Path("outputs/ensemble_evaluation.json")


def validate_probabilities(p: dict[str, float]) -> None:
    if not isinstance(p, dict) or set(OUTCOMES) - set(p):
        raise ValueError("Missing match outcome probabilities")
    values = [p[name] for name in OUTCOMES]
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value < 0
        or value > 1
        for value in values
    ):
        raise ValueError("Invalid match outcome probability")
    if abs(sum(values) - 1.0) > 1e-5:
        raise ValueError("Probabilities do not sum to one")


def equal_weight_blend(elo: dict[str, float], poisson: dict[str, float]) -> dict[str, float]:
    """A prespecified fixed average; no weights are optimized on test results."""
    validate_probabilities(elo)
    validate_probabilities(poisson)
    result = {label: (elo[label] + poisson[label]) / 2.0 for label in OUTCOMES}
    validate_probabilities(result)
    return result


def summarize(rows: list[dict], name: str) -> dict[str, float]:
    if not rows:
        raise ValueError("No matches to evaluate")
    brier = 0.0
    log_loss = 0.0
    correct = 0
    for row in rows:
        prob = row[name]
        b, loss = score_forecast(prob, row["actual"])
        brier += b
        log_loss += loss
        correct += int(max(OUTCOMES, key=prob.__getitem__) == ACTUAL_TO_OUTCOME[row["actual"]])
    n = len(rows)
    return {
        "brier": round(brier / n, 6),
        "log_loss": round(log_loss / n, 6),
        "outcome_accuracy": round(correct / n, 6),
        "average_draw_probability": round(sum(row[name]["draw"] for row in rows) / n, 6),
        "actual_draw_frequency": round(sum(row["actual"] == "D" for row in rows) / n, 6),
    }


def compare_against(rows: list[dict], other: str, repeats: int, seed: int) -> dict:
    deltas = []
    for row in rows:
        blend_brier, blend_loss = score_forecast(row["ensemble"], row["actual"])
        other_brier, other_loss = score_forecast(row[other], row["actual"])
        correct = ACTUAL_TO_OUTCOME[row["actual"]]
        deltas.append({
            "date": row["date"],
            "brier_delta": blend_brier - other_brier,
            "log_loss_delta": blend_loss - other_loss,
            "accuracy_delta": (
                int(max(OUTCOMES, key=row["ensemble"].__getitem__) == correct)
                - int(max(OUTCOMES, key=row[other].__getitem__) == correct)
            ),
        })
    return bootstrap_by_date(deltas, repeats=repeats, seed=seed)


def build_rows(matches_path: Path, journal_path: Path, validation_from: date, test_from: date) -> tuple[list[dict], dict]:
    matches = load_matches(matches_path)
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    if journal.get("test_from") != test_from.isoformat():
        raise ValueError("Journal cutoff does not match the requested evaluation season")
    records = journal.get("individual_forecasts")
    if not isinstance(records, list) or not records:
        raise ValueError("Poisson backtest has no match-level forecasts")

    settings, _ = select_config(matches, validation_from, test_from)
    elo_forecasts = walk_forward_elo(matches, settings)
    actuals = {}
    for match in matches:
        if match.date >= test_from:
            key = (match.date.isoformat(), f"{match.home_team} vs {match.away_team}")
            if key in actuals:
                raise ValueError(f"Repeated historical fixture: {key}")
            actuals[key] = match.outcome
    poisson = {}
    for record in records:
        key = (record["date"], record["fixture"])
        if key in poisson:
            raise ValueError(f"Duplicate journal fixture: {key}")
        poisson[key] = record
    if not actuals or set(actuals) != set(poisson):
        raise ValueError("Historical match CSV and backtest journal do not match")

    rows = []
    for key in sorted(actuals):
        record = poisson[key]
        if record["actual"] != actuals[key]:
            raise ValueError(f"Actual match result disagreement: {key}")
        elo = elo_forecasts[key]
        p = {label: record["forecast"][label] for label in OUTCOMES}
        rows.append({
            "date": key[0], "actual": actuals[key],
            "elo": elo, "poisson": p,
            "ensemble": equal_weight_blend(elo, p),
        })
    return rows, {"k_factor": settings.k_factor, "home_advantage": settings.home_advantage}


def evaluate(matches_path: Path, journal_path: Path, validation_from: date, test_from: date,
             repeats: int = 3000, seed: int = 42) -> dict:
    rows, settings = build_rows(matches_path, journal_path, validation_from, test_from)
    metrics = {name: summarize(rows, name) for name in ("poisson", "elo", "ensemble")}
    return {
        "project": "AnalyzNow AI",
        "evaluation_type": "Exploratory fixed-weight 50:50 ensemble on previously reviewed test season",
        "validation_from": validation_from.isoformat(),
        "test_from": test_from.isoformat(),
        "matches": len(rows),
        "distinct_match_dates": len({r["date"] for r in rows}),
        "elo_settings_selected_on_validation": settings,
        "metrics": metrics,
        "ensemble_minus_poisson": compare_against(rows, "poisson", repeats, seed),
        "ensemble_minus_elo": compare_against(rows, "elo", repeats, seed),
        "research_limit": (
            "2024/25 results for both component models were viewed before this ensemble was proposed. "
            "A better score is exploratory, not a pristine held-out improvement. "
            "Validate a frozen approach on later unseen fixtures or rolling-origin seasons."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a fixed 50:50 Elo and Poisson ensemble")
    parser.add_argument("--matches", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--poisson-journal", type=Path, default=DEFAULT_POISSON)
    parser.add_argument("--validation-from", type=date.fromisoformat, default=date(2023, 8, 1))
    parser.add_argument("--test-from", type=date.fromisoformat, default=date(2024, 8, 1))
    parser.add_argument("--resamples", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = evaluate(args.matches, args.poisson_journal, args.validation_from, args.test_from,
                      repeats=args.resamples, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nAnalyzNow AI — exploratory ensemble benchmark")
    print(f"Matched matches: {report['matches']} across {report['distinct_match_dates']} dates")
    print("Blend: 50% Elo + 50% Poisson; neither existing model changed")
    print("Model                Brier     Log loss   Accuracy   Avg draw probability")
    for name, vals in report["metrics"].items():
        print(f"{name:<19} {vals['brier']:<9.6f} {vals['log_loss']:<10.6f} "
              f"{vals['outcome_accuracy']:<9.1%} {vals['average_draw_probability']:.1%}")
    for other, key in (("Poisson", "ensemble_minus_poisson"), ("Elo", "ensemble_minus_elo")):
        print(f"\nEnsemble minus {other}: negative loss difference favours ensemble")
        estimates = report[key]["delta_elo_minus_poisson"]
        for label, values in estimates.items():
            print(f"  {label:<16}: {values['observed_difference']:+.6f} "
                  f"| 95% interval [{values['lower_95']:+.6f}, {values['upper_95']:+.6f}]")
    print("\nRESEARCH ONLY: existing test season already reviewed; later untouched data needed.")
    print(f"Aggregate report saved to {args.output}")


if __name__ == "__main__":
    main()
