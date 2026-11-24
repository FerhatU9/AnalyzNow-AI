"""Export validated, aggregate-only model benchmarking metrics to the web app.

Reads locally saved research reports. Does not publish match-level predictions or
alter the model. Run from the repository root after completing evaluations.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

MODELS = ("poisson", "elo", "ensemble")
METRICS = ("brier", "log_loss", "outcome_accuracy", "average_draw_probability")


def read_report(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path}. Run the evaluation first.")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def read_model_scores(source: dict) -> dict:
    raw = source.get("metrics")
    if not isinstance(raw, dict):
        raise ValueError("Evaluation report has no metrics object")
    models = {}
    for name in MODELS:
        values = raw.get(name)
        if not isinstance(values, dict):
            raise ValueError(f"Missing metrics for {name}")
        scores = {}
        for field in METRICS:
            value = values.get(field)
            if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
                raise ValueError(f"Invalid {name} {field}")
            if field == "brier" and not 0 <= value <= 2:
                raise ValueError(f"Out-of-range {name} {field}")
            if field == "log_loss" and value < 0:
                raise ValueError(f"Out-of-range {name} {field}")
            if field in ("outcome_accuracy", "average_draw_probability") and not 0 <= value <= 1:
                raise ValueError(f"Out-of-range {name} {field}")
            scores[field] = round(float(value), 6)
        models[name] = scores
    return models


def read_delta_intervals(heldout: dict) -> dict:
    raw = heldout.get("ensemble_minus_poisson", {}).get("delta_elo_minus_poisson", {})
    intervals = {}
    for key in ("brier_delta", "log_loss_delta", "accuracy_delta"):
        item = raw.get(key)
        if not isinstance(item, dict):
            raise ValueError(f"Missing held-out interval: {key}")
        vals = [item.get(k) for k in ("observed_difference", "lower_95", "upper_95")]
        if any(isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v) for v in vals):
            raise ValueError(f"Invalid held-out interval: {key}")
        if not vals[1] <= vals[0] <= vals[2]:
            raise ValueError(f"Out-of-order held-out interval: {key}")
        intervals[key] = {
            "observed": round(float(vals[0]), 6),
            "lower": round(float(vals[1]), 6),
            "upper": round(float(vals[2]), 6),
            "includes_zero": vals[1] <= 0 <= vals[2],
        }
    return intervals


def generate(earlier: dict, later: dict, drift: dict) -> dict:
    reviews = []
    for label, benchmark, diagnostic_key, nfield, methodology in (
        ("2024/25", earlier, "earlier", "matches", "Exploratory: test season reviewed during model development"),
        ("2025/26", later, "later", "test_matches", "Later-season evaluation: settings and ensemble weights fixed beforehand"),
    ):
        group = drift.get(diagnostic_key)
        if not isinstance(group, dict) or not isinstance(group.get("overall"), dict):
            raise ValueError(f"Missing drift summary for {label}")
        n = benchmark.get(nfield)
        if isinstance(n, bool) or not isinstance(n, int) or n <= 0 or n != group["overall"].get("matches"):
            raise ValueError(f"Inconsistent match counts for {label}")
        first = group.get("first_half")
        second = group.get("second_half")
        outcomes = group["overall"].get("outcomes")
        if not all(isinstance(v, dict) for v in (first, second, outcomes)):
            raise ValueError(f"Incomplete drift summary for {label}")
        if first.get("matches", 0) + second.get("matches", 0) != n:
            raise ValueError(f"Half-season counts do not total {n} for {label}")
        halves = {}
        for key, values in (("first_half", first), ("second_half", second)):
            brier = values.get("brier")
            if isinstance(brier, bool) or not isinstance(brier, (float, int)) or not 0 <= brier <= 2:
                raise ValueError(f"Invalid half-season Brier score for {label}")
            halves[key] = {"matches": values["matches"], "brier": round(float(brier), 6)}
        draw = outcomes.get("draw", {}).get("observed_frequency")
        if isinstance(draw, bool) or not isinstance(draw, (float, int)) or not 0 <= draw <= 1:
            raise ValueError(f"Invalid observed draw frequency for {label}")
        reviews.append({
            "season": label,
            "methodology": methodology,
            "matches": n,
            "models": read_model_scores(benchmark),
            "poisson_halves": halves,
            "actual_draw_frequency": round(float(draw), 6),
        })

    return {
        "product": "AnalyzNow AI",
        "report_type": "Historical model evaluation — not current match predictions",
        "seasons": reviews,
        "heldout_ensemble_minus_poisson": read_delta_intervals(later),
        "limitations": (
            "2024/25 ensemble comparison was exploratory. 2025/26 used preselected settings, "
            "but a single later season does not prove robust superiority. "
            "Changes between periods do not establish the cause of performance variation. "
            "Market odds are not included in these model scores."
        ),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--exploratory", type=Path, default=Path("outputs/ensemble_evaluation.json"))
    p.add_argument("--later", type=Path, default=Path("outputs/heldout_2025_26_evaluation.json"))
    p.add_argument("--stability", type=Path, default=Path("outputs/model_drift.json"))
    p.add_argument("--output", type=Path, default=Path("frontend/data/model-quality.json"))
    args = p.parse_args()
    result = generate(read_report(args.exploratory), read_report(args.later), read_report(args.stability))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"AnalyzNow AI — model quality summary written to {args.output}")
    print(f"Historical match observations: {sum(s['matches'] for s in result['seasons'])}")
    print("Only aggregated metrics exported. Forecasting engine and saved journals unchanged.")


if __name__ == "__main__":
    main()
