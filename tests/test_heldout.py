"""Guardrails for frozen model comparison on a later season."""

from datetime import date, timedelta

import pytest

from football_intel.data import Match
from scripts.evaluate_heldout import FROZEN_ELO, TEST_START, join_predictions


def historical_fixtures() -> list[Match]:
    matches = []
    for day in range(760):
        matches.append(Match(date(2022, 1, 1) + timedelta(days=day), "A", "B", 1, 0))
    return matches


def complete_season() -> list[Match]:
    # Use 380 unique fixture dates and distinct teams, no duplicate keys.
    return [
        Match(date(2025, 8, 1) + timedelta(days=i % 200), f"Home{i}", f"Away{i}", 1, i % 3)
        for i in range(380)
    ]


def backtest_journal(fixtures: list[Match]) -> dict:
    return {
        "test_from": "2025-08-01",
        "individual_forecasts": [
            {
                "date": m.date.isoformat(),
                "fixture": f"{m.home_team} vs {m.away_team}",
                "actual": m.outcome,
                "forecast": {"home_win": 0.50, "draw": 0.25, "away_win": 0.25},
            }
            for m in fixtures
        ],
    }


def test_frozen_settings_are_selected_before_new_season():
    assert (FROZEN_ELO.k_factor, FROZEN_ELO.home_advantage) == (32.0, 40.0)
    assert TEST_START == date(2025, 8, 1)


def test_join_builds_all_380_fixtures_and_uses_fixed_ensemble():
    fixtures = complete_season()
    rows = join_predictions(historical_fixtures() + fixtures, backtest_journal(fixtures))
    assert len(rows) == 380
    for row in rows:
        assert row["ensemble"]["home_win"] == pytest.approx(
            (row["elo"]["home_win"] + 0.5) / 2
        )
        assert sum(row["ensemble"].values()) == pytest.approx(1.0)


def test_incomplete_season_is_rejected():
    fixtures = complete_season()[:-1]
    with pytest.raises(ValueError, match="Expected 380"):
        join_predictions(historical_fixtures() + fixtures, backtest_journal(fixtures))


def test_wrong_journal_cutoff_is_rejected():
    fixtures = complete_season()
    journal = backtest_journal(fixtures)
    journal["test_from"] = "2024-08-01"
    with pytest.raises(ValueError, match="2025-08-01"):
        join_predictions(historical_fixtures() + fixtures, journal)


def test_journal_result_disagreement_is_rejected():
    fixtures = complete_season()
    journal = backtest_journal(fixtures)
    original = journal["individual_forecasts"][0]["actual"]
    journal["individual_forecasts"][0]["actual"] = "D" if original != "D" else "H"
    with pytest.raises(ValueError, match="result mismatch"):
        join_predictions(historical_fixtures() + fixtures, journal)


def test_future_season_is_rejected():
    fixtures = complete_season()
    future = Match(date(2026, 8, 1), "C", "D", 2, 1)
    with pytest.raises(ValueError, match="later seasons"):
        join_predictions(historical_fixtures() + fixtures + [future], backtest_journal(fixtures))
