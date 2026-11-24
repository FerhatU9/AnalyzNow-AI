"""Unit tests for the fixed, research-only Elo/Poisson blend."""
import pytest

from scripts.evaluate_ensemble import (
    equal_weight_blend, validate_probabilities, summarize, compare_against,
)


def forecast(h: float, d: float, a: float) -> dict:
    return {"home_win": h, "draw": d, "away_win": a}


def test_equal_weight_average_and_probability_total():
    a = forecast(0.60, 0.20, 0.20)
    b = forecast(0.40, 0.30, 0.30)
    result = equal_weight_blend(a, b)
    assert result == pytest.approx(forecast(0.5, 0.25, 0.25))
    assert sum(result.values()) == pytest.approx(1.0)


def test_same_models_give_same_forecast():
    p = forecast(0.50, 0.20, 0.30)
    assert equal_weight_blend(p, p) == pytest.approx(p)


@pytest.mark.parametrize("bad", [
    forecast(0.8, 0.5, -0.3),
    forecast(0.2, 0.2, 0.2),
    forecast(float('nan'), 0.4, 0.6),
    {"home_win": 0.5, "draw": 0.5},
    forecast(True, 0.4, 0.6),
])
def test_invalid_input_is_rejected(bad):
    with pytest.raises(ValueError):
        validate_probabilities(bad)
    with pytest.raises(ValueError):
        equal_weight_blend(bad, forecast(0.4, 0.3, 0.3))


def test_summary_and_date_clustered_comparison():
    rows = [
        {"date": "2024-08-16", "actual": "H", "elo": forecast(.6, .2, .2),
         "poisson": forecast(.4, .3, .3), "ensemble": forecast(.5, .25, .25)},
        {"date": "2024-08-16", "actual": "D", "elo": forecast(.5, .3, .2),
         "poisson": forecast(.4, .4, .2), "ensemble": forecast(.45, .35, .2)},
        {"date": "2024-08-17", "actual": "A", "elo": forecast(.3, .2, .5),
         "poisson": forecast(.5, .2, .3), "ensemble": forecast(.4, .2, .4)},
    ]
    metrics = summarize(rows, "ensemble")
    assert metrics["outcome_accuracy"] == pytest.approx(1/3, abs=1e-6)
    assert metrics["average_draw_probability"] == pytest.approx((.25+.35+.2)/3, abs=1e-6)
    results = compare_against(rows, "poisson", repeats=100, seed=4)
    assert results["fixture_count"] == 3
    assert results["match_dates"] == 2
    assert results == compare_against(rows, "poisson", repeats=100, seed=4)
