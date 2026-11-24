"""Tests for the read-only, aggregate model-quality export."""
from __future__ import annotations

import json

import pytest

from scripts.export_model_quality import generate, read_report, read_model_scores


def benchmark(n: int, is_later: bool = False) -> dict:
    stats = {
        name: {
            "brier": 0.6,
            "log_loss": 1.0,
            "outcome_accuracy": 0.5,
            "average_draw_probability": 0.24,
        }
        for name in ("poisson", "elo", "ensemble")
    }
    report = {"metrics": stats}
    report["test_matches" if is_later else "matches"] = n
    if is_later:
        report["ensemble_minus_poisson"] = {
            "delta_elo_minus_poisson": {
                key: {"observed_difference": -0.01, "lower_95": -0.02, "upper_95": 0.01}
                for key in ("brier_delta", "log_loss_delta", "accuracy_delta")
            }
        }
    return report


def stability() -> dict:
    group = {
        "overall": {"matches": 4, "outcomes": {"draw": {"observed_frequency": 0.25}}},
        "first_half": {"matches": 2, "brier": 0.6},
        "second_half": {"matches": 2, "brier": 0.7},
    }
    return {"earlier": group, "later": group}


def test_export_has_only_aggregates():
    result = generate(benchmark(4), benchmark(4, True), stability())
    assert len(result["seasons"]) == 2
    assert result["seasons"][1]["models"]["ensemble"]["brier"] == 0.6
    assert "individual_forecasts" not in json.dumps(result)
    assert result["heldout_ensemble_minus_poisson"]["brier_delta"]["includes_zero"] is True


def test_disagreed_match_counts_rejected():
    with pytest.raises(ValueError, match="Inconsistent match counts"):
        generate(benchmark(5), benchmark(4, True), stability())


def test_missing_model_metric_rejected():
    earlier = benchmark(4)
    del earlier["metrics"]["poisson"]["log_loss"]
    with pytest.raises(ValueError, match="Invalid poisson log_loss"):
        generate(earlier, benchmark(4, True), stability())


def test_nonfinite_metric_rejected():
    earlier = benchmark(4)
    earlier["metrics"]["poisson"]["brier"] = float("nan")
    with pytest.raises(ValueError, match="Invalid poisson brier"):
        generate(earlier, benchmark(4, True), stability())


def test_inconsistent_halves_rejected():
    s = stability()
    s["later"]["second_half"]["matches"] = 1
    with pytest.raises(ValueError, match="Half-season"):
        generate(benchmark(4), benchmark(4, True), s)


def test_unordered_uncertainty_interval_rejected():
    later = benchmark(4, True)
    later["ensemble_minus_poisson"]["delta_elo_minus_poisson"]["brier_delta"]["lower_95"] = 0.5
    with pytest.raises(ValueError, match="Out-of-order"):
        generate(benchmark(4), later, stability())


def test_read_report_missing_path(tmp_path):
    with pytest.raises(FileNotFoundError, match="Run the evaluation"):
        read_report(tmp_path / "missing.json")


def test_missing_heldout_interval_rejected():
    later = benchmark(4, True)
    del later["ensemble_minus_poisson"]["delta_elo_minus_poisson"]["accuracy_delta"]
    with pytest.raises(ValueError, match="Missing held-out interval"):
        generate(benchmark(4), later, stability())
