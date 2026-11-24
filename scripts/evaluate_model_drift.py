"""Compare forecasting diagnostics across dated, precomputed backtest journals.

This script does not fit or tune a model and never alters the source journals.
Run from the repository root. Requires Python standard library only.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

OUTCOMES = {"H": "home_win", "D": "draw", "A": "away_win"}
LABELS = tuple(OUTCOMES.values())


def load_journal(path: Path) -> list[dict]:
    report = json.loads(path.read_text(encoding="utf-8"))
    entries = report.get("individual_forecasts")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{path}: individual_forecasts must be a nonempty list")
    cleaned = []
    for i, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            raise ValueError(f"{path}, row {i}: expected a match record")
        try:
            day = date.fromisoformat(entry["date"])
            actual = entry["actual"]
            forecast = entry["forecast"]
            probs = {key: float(forecast[key]) for key in LABELS}
        except (ValueError, KeyError, TypeError, AttributeError) as exc:
            raise ValueError(f"{path}, row {i}: invalid match record") from exc
        if actual not in OUTCOMES or any(not math.isfinite(v) or not 0 <= v <= 1 for v in probs.values()):
            raise ValueError(f"{path}, row {i}: outcome/probability outside allowed range")
        if not math.isclose(sum(probs.values()), 1, abs_tol=0.00001):
            raise ValueError(f"{path}, row {i}: outcome probabilities do not sum to 1")
        cleaned.append({"date": day.isoformat(), "actual": actual, "forecast": probs,
                        "fixture": str(entry.get("fixture", ""))})
    cleaned.sort(key=lambda row: (row["date"], row["fixture"]))
    return cleaned


def metrics(matches: list[dict]) -> dict:
    """Three-class multiclass Brier and log loss; no future data is used."""
    if not matches:
        raise ValueError("Cannot score an empty group")
    brier, logloss, correct = 0.0, 0.0, 0
    actuals = Counter()
    probability_totals = Counter()
    predicted_classes = Counter()
    for item in matches:
        actual = OUTCOMES[item["actual"]]
        probs = item["forecast"]
        brier += sum((probs[key] - float(key == actual)) ** 2 for key in LABELS)
        logloss -= math.log(max(probs[actual], 1e-12))
        best = max(LABELS, key=probs.get)
        correct += best == actual
        predicted_classes[best] += 1
        actuals[actual] += 1
        for key in LABELS:
            probability_totals[key] += probs[key]
    n = len(matches)
    return {
        "matches": n,
        "brier": round(brier / n, 6),
        "log_loss": round(logloss / n, 6),
        "accuracy": round(correct / n, 6),
        "outcomes": {
            key: {
                "average_predicted": round(probability_totals[key] / n, 6),
                "observed_frequency": round(actuals[key] / n, 6),
                "observed_minus_predicted": round((actuals[key] - probability_totals[key]) / n, 6),
                "actual_matches": actuals[key],
                "predicted_as_most_likely": predicted_classes[key],
            }
            for key in LABELS
        },
    }


def season_diagnostics(rows: list[dict]) -> dict:
    by_month = defaultdict(list)
    for row in rows:
        by_month[row["date"][:7]].append(row)
    # Keep fixtures sharing one date in the same diagnostic period.
    days = sorted({row["date"] for row in rows})
    if len(days) < 2:
        raise ValueError("Need at least two distinct match dates for season diagnostics")
    midpoint = days[len(days) // 2]
    earlier = [row for row in rows if row["date"] < midpoint]
    later = [row for row in rows if row["date"] >= midpoint]
    return {
        "overall": metrics(rows),
        "first_half": metrics(earlier),
        "second_half": metrics(later),
        "by_month": {month: metrics(group) for month, group in sorted(by_month.items())},
    }


def summarize(first: list[dict], second: list[dict]) -> dict:
    first_dates = {x["date"] for x in first}
    second_dates = {x["date"] for x in second}
    if max(first_dates) >= min(second_dates):
        raise ValueError("Expected the first season to end before the second begins")
    a = season_diagnostics(first)
    b = season_diagnostics(second)
    return {
        "method": "Read-only descriptive review of saved walk-forward Poisson predictions",
        "caution": "Changes between seasons may reflect fixture mix and randomness; no model is tuned here.",
        "earlier": a,
        "later": b,
        "later_minus_earlier": {
            key: round(b["overall"][key] - a["overall"][key], 6)
            for key in ("brier", "log_loss", "accuracy")
        },
    }


def show(results: dict) -> None:
    print("\nANALYZNOW AI — POISSON SEASON DIAGNOSTICS")
    print("=========================================")
    for name in ("earlier", "later"):
        overall = results[name]["overall"]
        print(f"\n{name.upper()}: {overall['matches']} matches")
        print(f"Brier {overall['brier']:.6f}  Log loss {overall['log_loss']:.6f}  Accuracy {overall['accuracy']:.1%}")
        print("Outcome   Predicted   Actual   Difference")
        for label in LABELS:
            v = overall["outcomes"][label]
            print(f"{label:9s} {v['average_predicted']:8.1%}  {v['observed_frequency']:7.1%}  {v['observed_minus_predicted']:+9.1%}")
        for half in ("first_half", "second_half"):
            s = results[name][half]
            print(f"  {half}: {s['matches']} matches; Brier {s['brier']:.6f}; log loss {s['log_loss']:.6f}")
    print("\nLATER MINUS EARLIER (positive losses = worse):")
    print(json.dumps(results["later_minus_earlier"], indent=2))
    print("\nMonthly summaries are saved in the JSON report; small monthly groups require caution.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--earlier", type=Path, default=Path("outputs/epl_2024_25_evaluation.json"))
    parser.add_argument("--later", type=Path, default=Path("outputs/epl_2025_26_evaluation.json"))
    parser.add_argument("--output", type=Path, default=Path("outputs/model_drift.json"))
    args = parser.parse_args()
    result = summarize(load_journal(args.earlier), load_journal(args.later))
    show(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"\nReport saved to {args.output}")


if __name__ == "__main__":
    main()
