"""Paired, match-day clustered uncertainty analysis of Elo versus Poisson.

No parameter selection is performed using the held-out 2024/25 results.
Uses the same CSV, Poisson journal and Elo configuration procedure as compare_elo.py.
"""
from __future__ import annotations

import argparse
import json
import random
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
OUTCOMES = ("home_win", "draw", "away_win")


OUTCOME_CODES = {"H": "home_win", "D": "draw", "A": "away_win"}


def percentile(sorted_values: list[float], fraction: float) -> float:
    """Linearly interpolated empirical quantile of an already sorted sample."""
    if not sorted_values or not 0 <= fraction <= 1:
        raise ValueError("Provide a nonempty sorted sample and a quantile from 0 to 1")
    x = (len(sorted_values) - 1) * fraction
    low = int(x)
    high = min(low + 1, len(sorted_values) - 1)
    weight = x - low
    return sorted_values[low] * (1 - weight) + sorted_values[high] * weight


def bootstrap_by_date(rows: list[dict], repeats: int = 3000, seed: int = 42) -> dict:
    """Resample entire match dates, preserving within-day fixture dependence.

    Deltas are (Elo - Poisson). For Brier/log loss, negative favours Elo.
    Not a test of future transferability; CI is a descriptive sampling estimate.
    """
    if not rows:
        raise ValueError("No fixtures to resample")
    if repeats < 100:
        raise ValueError("At least 100 resamples required")
    by_day = defaultdict(list)
    for row in rows:
        by_day[row["date"]].append(row)
    dates = sorted(by_day)
    rng = random.Random(seed)
    fields = ("brier_delta", "log_loss_delta", "accuracy_delta")
    blocks = {
        day: (len(by_day[day]), {f: sum(float(r[f]) for r in by_day[day]) for f in fields})
        for day in dates
    }
    distributions = {f: [] for f in fields}
    for _ in range(repeats):
        sample = [rng.choice(dates) for _ in dates]
        count = sum(blocks[d][0] for d in sample)
        for field in fields:
            distributions[field].append(sum(blocks[d][1][field] for d in sample) / count)

    results = {}
    for field, values in distributions.items():
        values.sort()
        results[field] = {
            "observed_difference": round(sum(float(r[field]) for r in rows) / len(rows), 6),
            "lower_95": round(percentile(values, 0.025), 6),
            "upper_95": round(percentile(values, 0.975), 6),
        }
    return {"fixture_count": len(rows), "match_dates": len(dates),
            "bootstrap_resamples": repeats, "random_seed": seed,
            "delta_elo_minus_poisson": results}


def evaluate(matches_path: Path, journal_path: Path, validation_from: date,
             test_from: date, repeats: int, seed: int) -> dict:
    matches = load_matches(matches_path)
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    if journal.get("test_from") != test_from.isoformat():
        raise ValueError("Poisson journal cutoff does not match evaluation date")
    records = journal.get("individual_forecasts")
    if not isinstance(records, list) or not records:
        raise ValueError("Poisson journal is missing individual forecasts")

    settings, _ = select_config(matches, validation_from, test_from)
    elo_predictions = walk_forward_elo(matches, settings)
    outcomes = {}
    for match in matches:
        if match.date < test_from:
            continue
        key = (match.date.isoformat(), f"{match.home_team} vs {match.away_team}")
        if key in outcomes:
            raise ValueError(f"Repeated historical fixture {key}")
        outcomes[key] = match.outcome

    poisson_rows = {}
    for record in records:
        key = (record["date"], record["fixture"])
        if key in poisson_rows:
            raise ValueError(f"Duplicate journal fixture {key}")
        poisson_rows[key] = record
    if not outcomes or set(outcomes) != set(poisson_rows):
        raise ValueError("Historical CSV and Poisson forecast journal do not match")

    rows = []
    outcome_totals = {
        model: {label: {"predicted_sum": 0.0, "actual_count": 0} for label in OUTCOMES}
        for model in ("elo", "poisson")
    }
    for key, actual in sorted(outcomes.items()):
        record = poisson_rows[key]
        if record["actual"] != actual:
            raise ValueError(f"Actual outcome mismatch in journal: {key}")
        poisson = record["forecast"]
        elo = elo_predictions[key]
        for p in (elo, poisson):
            if any(label not in p for label in OUTCOMES):
                raise ValueError(f"Missing 1X2 probabilities for {key}")
            if any(not 0 <= p[label] <= 1 for label in OUTCOMES):
                raise ValueError(f"Invalid probability for {key}")
            if abs(sum(p[label] for label in OUTCOMES) - 1) > 1e-5:
                raise ValueError(f"Probabilities do not sum to one for {key}")

        elo_brier, elo_log = score_forecast(elo, actual)
        poisson_brier, poisson_log = score_forecast(poisson, actual)
        true_label = OUTCOME_CODES[actual]
        elo_correct = int(max(OUTCOMES, key=elo.__getitem__) == true_label)
        poisson_correct = int(max(OUTCOMES, key=poisson.__getitem__) == true_label)
        rows.append({"date": key[0], "brier_delta": elo_brier - poisson_brier,
                     "log_loss_delta": elo_log - poisson_log,
                     "accuracy_delta": elo_correct - poisson_correct})
        for name, p in (("elo", elo), ("poisson", poisson)):
            for label in OUTCOMES:
                outcome_totals[name][label]["predicted_sum"] += p[label]
                outcome_totals[name][label]["actual_count"] += int(label == true_label)

    uncertainty = bootstrap_by_date(rows, repeats=repeats, seed=seed)
    n = len(rows)
    calibration = {}
    for name in outcome_totals:
        calibration[name] = {}
        for label, values in outcome_totals[name].items():
            predicted = values["predicted_sum"] / n
            actual = values["actual_count"] / n
            calibration[name][label] = {
                "mean_predicted": round(predicted, 6),
                "observed_frequency": round(actual, 6),
                "observed_minus_predicted": round(actual - predicted, 6),
            }
    return {
        "project": "AnalyzNow AI",
        "data": "Historical match results loaded locally; no raw fixtures stored in this report",
        "validation_from": validation_from.isoformat(),
        "test_from": test_from.isoformat(),
        "selected_elo_settings": {"k_factor": settings.k_factor,
                                  "home_advantage": settings.home_advantage},
        "paired_match_day_bootstrap": uncertainty,
        "outcome_frequency_calibration": calibration,
        "interpretation": "Negative Elo-minus-Poisson loss delta is better for Elo. A 95% bootstrap interval spanning zero does not establish a reliable improvement. Even a nonzero interval from one league season does not prove future performance.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Elo vs Poisson held-out uncertainty")
    parser.add_argument("--matches", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--poisson-journal", type=Path, default=DEFAULT_JOURNAL)
    parser.add_argument("--validation-from", type=date.fromisoformat, default=date(2023, 8, 1))
    parser.add_argument("--test-from", type=date.fromisoformat, default=date(2024, 8, 1))
    parser.add_argument("--resamples", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("outputs/elo_uncertainty.json"))
    args = parser.parse_args()
    result = evaluate(args.matches, args.poisson_journal, args.validation_from,
                      args.test_from, args.resamples, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    b = result["paired_match_day_bootstrap"]
    print("\nAnalyzNow AI — Elo versus Poisson uncertainty")
    print(f"Matched fixtures: {b['fixture_count']} across {b['match_dates']} distinct match dates")
    print(f"Elo selected on validation: {result['selected_elo_settings']}")
    print("Negative loss differences favour Elo; positive accuracy difference favours Elo.")
    for name, vals in b["delta_elo_minus_poisson"].items():
        print(f"  {name:<17}: {vals['observed_difference']:+.6f}"
              f" | 95% interval [{vals['lower_95']:+.6f}, {vals['upper_95']:+.6f}]")
    print("\nOutcome calibration (observed frequency minus average predicted):")
    for label in OUTCOMES:
        elo = result["outcome_frequency_calibration"]["elo"][label]["observed_minus_predicted"]
        poisson = result["outcome_frequency_calibration"]["poisson"][label]["observed_minus_predicted"]
        print(f"  {label:<9} Elo {elo:+.1%} | Poisson {poisson:+.1%}")
    print("This is a single-season diagnostic, not proof of future superiority.")
    print(f"Aggregate report saved to {args.output}")


if __name__ == "__main__":
    main()
