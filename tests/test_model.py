from datetime import date, timedelta
import pytest
from football_intel.data import Match
from football_intel.model import train, forecast
from football_intel.backtest import backtest, score_forecast


def matches(n=100):
    teams = ["A", "B", "C", "D"]
    start = date(2024, 1, 1)
    result = []
    for i in range(n):
        home = teams[i % 4]
        away = teams[(i + 1 + (i // 4) % 3) % 4]
        if home == away:
            away = teams[(i + 1) % 4]
        result.append(Match(start + timedelta(days=i // 2), home, away, i % 4, (i + 1) % 3))
    return result


def test_probabilities_are_coherent():
    model = train(matches(), date(2025, 1, 1))
    result = forecast(model, "A", "B")
    p = result["probabilities"]
    assert abs(sum(p[key] for key in ("home_win", "draw", "away_win")) - 1) < 2e-6
    assert abs(p["over_2_5"] + p["under_2_5"] - 1) < 2e-6
    assert 0 <= p["both_teams_score"] <= 1
    assert result["expected_goals"]["home"] > 0


def test_no_future_data_leakage():
    historical = matches(90)
    cutoff = date(2024, 2, 20)
    original = forecast(train(historical, cutoff), "A", "B")
    altered = historical + [Match(date(2025, 1, 1), "A", "B", 50, 0)]
    after = forecast(train(altered, cutoff), "A", "B")
    assert original == after


def test_no_same_date_data_leakage():
    historical = matches(90)
    cutoff = date(2024, 2, 20)
    original = forecast(train(historical, cutoff), "A", "B")
    altered = historical + [Match(cutoff, "A", "B", 60, 0)]
    after = forecast(train(altered, cutoff), "A", "B")
    assert original == after


def test_backtest_against_baseline():
    result = backtest(matches(), min_training_matches=30)
    assert result["n_test_matches"] > 0
    assert result["first_test_date"] <= result["last_test_date"]
    assert result["model_brier"] >= 0
    assert result["baseline_log_loss"] >= 0


def test_reject_self_match():
    model = train(matches(), date(2025, 1, 1))
    with pytest.raises(ValueError):
        forecast(model, "A", "A")


def test_proper_scoring_rule():
    assert score_forecast({"home_win": .8, "draw": .1, "away_win": .1}, "H")[1] < score_forecast({"home_win": .2, "draw": .4, "away_win": .4}, "H")[1]


def test_backtest_start_date_filters_evaluation_not_training():
    historical = matches(110)
    result = backtest(historical, min_training_matches=30, test_from=date(2024, 2, 10))
    assert result["n_test_matches"] > 0
    assert result["first_test_date"] >= "2024-02-10"
    assert result["test_from"] == "2024-02-10"


def test_unseen_team_is_flagged():
    model = train(matches(100), date(2025, 1, 1))

    result = forecast(model, "New FC", "B")

    diagnostics = result["diagnostics"]

    assert diagnostics["home_team_unseen"] is True
    assert diagnostics["away_team_unseen"] is False
    assert diagnostics["low_data_warning"] is True
