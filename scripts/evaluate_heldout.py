"""Frozen Elo + Poisson ensemble benchmark on 2025/26 Premier League results.

No model refitting or hyperparameter selection is performed on 2025/26 results.
The component Elo predictions are walk-forward by fixture day; Poisson predictions
are read from the existing strict-date backtest journal.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from football_intel.data import Match, load_matches
from football_intel.elo import EloConfig, walk_forward_elo
from scripts.evaluate_ensemble import (
    compare_against,
    equal_weight_blend,
    summarize,
    validate_probabilities,
)

# These choices were fixed BEFORE evaluating the new 2025/26 season.
FROZEN_ELO = EloConfig(k_factor=32.0, home_advantage=40.0)
TEST_START = date(2025, 8, 1)
TEST_END_EXCLUSIVE = date(2026, 7, 1)
EXPECTED_TEST_MATCHES = 380
DEFAULT_CSV = Path(
    "data/openfootball/epl_2021_2026/processed/"
    "epl_2021-22_2022-23_2023-24_2024-25_2025-26.csv"
)
DEFAULT_JOURNAL = Path("outputs/epl_2025_26_evaluation.json")
DEFAULT_OUTPUT = Path("outputs/heldout_2025_26_evaluation.json")
OUTCOMES = ("home_win", "draw", "away_win")


def join_predictions(matches: list[Match], journal: dict) -> list[dict]:
    """Match both model predictions to the same completed fixture and result."""
    if journal.get("test_from") != TEST_START.isoformat():
        raise ValueError("Backtest journal must start at 2025-08-01")
    records = journal.get("individual_forecasts")
    if not isinstance(records, list):
        raise ValueError("Backtest journal is missing individual forecasts")

    historical = [m for m in matches if m.date < TEST_START]
    testing = [m for m in matches if TEST_START <= m.date < TEST_END_EXCLUSIVE]
    if len(historical) < 760:
        raise ValueError("Need at least 760 matches before the test season")
    if len(testing) != EXPECTED_TEST_MATCHES:
        raise ValueError(
            f"Expected {EXPECTED_TEST_MATCHES} complete 2025/26 fixtures, got {len(testing)}"
        )
    if any(m.date >= TEST_END_EXCLUSIVE for m in matches):
        raise ValueError("CSV includes later seasons: use a 2021/22–2025/26 snapshot only")

    actual_by_key: dict[tuple[str, str], str] = {}
    for match in testing:
        key = (match.date.isoformat(), f"{match.home_team} vs {match.away_team}")
        if key in actual_by_key:
            raise ValueError(f"Duplicate fixture in source: {key}")
        actual_by_key[key] = match.outcome

    poisson_by_key: dict[tuple[str, str], dict] = {}
    for record in records:
        if not isinstance(record, dict) or not all(
            key in record for key in ("date", "fixture", "forecast", "actual")
        ):
            raise ValueError("Invalid backtest forecast record")
        key = (record["date"], record["fixture"])
        if key in poisson_by_key:
            raise ValueError(f"Duplicate Poisson forecast: {key}")
        poisson_by_key[key] = record

    if set(actual_by_key) != set(poisson_by_key):
        raise ValueError("Poisson journal and source fixture set do not match exactly")

    # This function predicts before matches on each date, and only updates Elo
    # ratings after that day's fixtures. The config is not reselected here.
    elo_by_key = walk_forward_elo(matches, FROZEN_ELO)
    rows = []
    for key in sorted(actual_by_key):
        result = actual_by_key[key]
        recorded = poisson_by_key[key]
        if recorded["actual"] != result:
            raise ValueError(f"Poisson journal result mismatch for {key}")
        poisson = {name: recorded["forecast"][name] for name in OUTCOMES}
        elo = elo_by_key[key]
        validate_probabilities(poisson)
        validate_probabilities(elo)
        rows.append(
            {
                "date": key[0],
                "fixture": key[1],
                "actual": result,
                "poisson": poisson,
                "elo": elo,
                "ensemble": equal_weight_blend(elo, poisson),
            }
        )
    return rows


def evaluate(
    csv_path: Path, journal_path: Path, *, resamples: int = 3000, seed: int = 42
) -> dict:
    matches = load_matches(csv_path)
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    rows = join_predictions(matches, journal)
    metrics = {name: summarize(rows, name) for name in ("poisson", "elo", "ensemble")}
    return {
        "project": "AnalyzNow AI",
        "analysis": "2025/26 post-selection walk-forward comparison",
        "test_start": TEST_START.isoformat(),
        "test_end_exclusive": TEST_END_EXCLUSIVE.isoformat(),
        "test_matches": len(rows),
        "match_dates": len({r["date"] for r in rows}),
        "frozen_elo_configuration": {
            "k_factor": FROZEN_ELO.k_factor,
            "home_advantage": FROZEN_ELO.home_advantage,
            "starting_rating": FROZEN_ELO.starting_rating,
        },
        "ensemble_weights": {"elo": 0.5, "poisson": 0.5},
        "metrics": metrics,
        "ensemble_minus_poisson": compare_against(rows, "poisson", resamples, seed),
        "ensemble_minus_elo": compare_against(rows, "elo", resamples, seed),
        "note": (
            "All parameters fixed before examining 2025/26 test results. "
            "This is a completed future-season retrospective evaluation, "
            "not proof of future live accuracy or a betting recommendation."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matches", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--poisson-journal", type=Path, default=DEFAULT_JOURNAL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--resamples", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.resamples < 100:
        parser.error("Provide at least 100 bootstrap resamples")
    report = evaluate(args.matches, args.poisson_journal, resamples=args.resamples, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("\nAnalyzNow AI — 2025/26 out-of-sample evaluation")
    print(f"Matched fixtures: {report['test_matches']} across {report['match_dates']} dates")
    print("Frozen Elo: K=32.0, home advantage=40.0; ensemble=50% Elo + 50% Poisson")
    print("Model        Brier     Log loss   Accuracy   Draw probability")
    for name, stats in report["metrics"].items():
        print(
            f"{name:<12} {stats['brier']:<9.6f} {stats['log_loss']:<10.6f} "
            f"{stats['outcome_accuracy']:<9.1%} {stats['average_draw_probability']:.1%}"
        )
    for competitor, key in (("Poisson", "ensemble_minus_poisson"), ("Elo", "ensemble_minus_elo")):
        print(f"\nEnsemble minus {competitor} (negative loss differences favor ensemble):")
        intervals = report[key]["delta_elo_minus_poisson"]
        for name, result in intervals.items():
            print(
                f"  {name:<15} {result['observed_difference']:+.6f} "
                f"| 95% interval [{result['lower_95']:+.6f}, {result['upper_95']:+.6f}]"
            )
    print(f"\nReport saved to {args.output}")


if __name__ == "__main__":
    main()
