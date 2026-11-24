"""Elo benchmark safeguards: probability validity and no future/same-day leakage."""
from datetime import date, timedelta

import pytest

from football_intel.data import Match
from football_intel.elo import (
    EloConfig, expected_home_score, outcome_probabilities,
    select_config, walk_forward_elo,
)


def fixture(day: date, home: str, away: str, h: int, a: int) -> Match:
    return Match(day, home, away, h, a)


def test_probabilities_are_coherent():
    for expected in (0.01, 0.2, 0.5, 0.8, 0.99):
        probabilities = outcome_probabilities(expected, historical_draw_rate=0.25)
        assert sum(probabilities.values()) == pytest.approx(1.0)
        assert all(0 <= value <= 1 for value in probabilities.values())
        assert probabilities["home_win"] + 0.5 * probabilities["draw"] == pytest.approx(expected)


def test_home_advantage_increases_expected_score():
    neutral = expected_home_score(1500, 1500, 0)
    advantage = expected_home_score(1500, 1500, 75)
    assert neutral == pytest.approx(0.5)
    assert advantage > neutral


def test_same_date_result_cannot_influence_another_forecast():
    day = date(2024, 8, 12)
    past = [fixture(day - timedelta(days=3), "A", "B", 1, 0)]
    day_1 = fixture(day, "A", "C", 1, 0)
    day_2 = fixture(day, "A", "D", 0, 0)
    before = walk_forward_elo(past + [day_1, day_2], EloConfig())
    changed = walk_forward_elo(past + [fixture(day, "A", "C", 10, 0), day_2], EloConfig())
    key = (day.isoformat(), "A vs D")
    assert before[key] == changed[key]


def test_future_results_cannot_change_earlier_predictions():
    day = date(2024, 8, 12)
    past = [fixture(day - timedelta(days=3), "A", "B", 1, 0)]
    target = fixture(day, "A", "C", 0, 1)
    future = fixture(day + timedelta(days=3), "A", "C", 50, 0)
    old = walk_forward_elo(past + [target], EloConfig())
    new = walk_forward_elo(past + [target, future], EloConfig())
    assert old[(day.isoformat(), "A vs C")] == new[(day.isoformat(), "A vs C")]


def test_validation_selection_does_not_look_at_test_results():
    matches = []
    start = date(2022, 8, 1)
    for i in range(80):
        day = start + timedelta(days=i * 14)
        matches.append(fixture(day, "A", "B", 2 if i % 3 else 0, i % 2))
    validation = date(2023, 8, 1)
    test = date(2024, 8, 1)
    chosen_a, choices_a = select_config(matches, validation, test)
    edited = [fixture(m.date, m.home_team, m.away_team, 9, 0)
              if m.date >= test else m for m in matches]
    chosen_b, choices_b = select_config(edited, validation, test)
    assert chosen_a == chosen_b
    assert choices_a == choices_b


def test_bad_config_is_rejected():
    with pytest.raises(ValueError):
        EloConfig(k_factor=0)
