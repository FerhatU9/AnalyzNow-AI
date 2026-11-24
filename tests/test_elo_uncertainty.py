"""Deterministic tests for paired match-day resampling."""
import pytest
from scripts.evaluate_elo_uncertainty import bootstrap_by_date, percentile


def test_percentile_interpolates():
    assert percentile([0.0, 10.0], 0.25) == pytest.approx(2.5)


def test_bootstrap_zero_differences():
    rows = [
        {"date": f"2024-09-0{i}", "brier_delta": 0, "log_loss_delta": 0,
         "accuracy_delta": 0} for i in range(1, 5)
    ]
    result = bootstrap_by_date(rows, repeats=100, seed=42)
    assert result["match_dates"] == 4
    for item in result["delta_elo_minus_poisson"].values():
        assert item["observed_difference"] == 0
        assert item["lower_95"] == 0
        assert item["upper_95"] == 0


def test_bootstrap_preserves_whole_match_day():
    # Two fixtures share the same day: resampling days must treat them as one block.
    rows = [
        {"date": "2024-08-01", "brier_delta": -1, "log_loss_delta": -1,
         "accuracy_delta": 1},
        {"date": "2024-08-01", "brier_delta": -1, "log_loss_delta": -1,
         "accuracy_delta": 1},
        {"date": "2024-08-02", "brier_delta": 1, "log_loss_delta": 1,
         "accuracy_delta": -1},
    ]
    output = bootstrap_by_date(rows, repeats=200, seed=10)
    assert output["fixture_count"] == 3
    assert output["match_dates"] == 2
    assert output["delta_elo_minus_poisson"]["brier_delta"]["observed_difference"] == pytest.approx(-1 / 3, abs=1e-6)
    assert output == bootstrap_by_date(rows, repeats=200, seed=10)


def test_invalid_resampling_arguments():
    with pytest.raises(ValueError):
        bootstrap_by_date([], repeats=100)
    with pytest.raises(ValueError):
        bootstrap_by_date([{"date": "2024-08-01"}], repeats=20)
