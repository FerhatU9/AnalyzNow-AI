
import pytest

from football_intel.market_odds import (
    remove_margin,
    analyze_event,
)


def test_remove_bookmaker_margin():
    odds = {
        "home_win": 2.0,
        "draw": 4.0,
        "away_win": 4.0,
    }

    result = remove_margin(odds)

    assert result["home_win"] == pytest.approx(0.50)
    assert result["draw"] == pytest.approx(0.25)
    assert result["away_win"] == pytest.approx(0.25)
    assert sum(result.values()) == pytest.approx(1)


def test_reject_invalid_odds():
    with pytest.raises(ValueError):
        remove_margin({
            "home_win": 0,
            "draw": 3.5,
            "away_win": 4.0,
        })


def test_analyze_bookmaker_data():
    event = {
        "id": "example",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "commence_time": "2026-12-01T19:00:00Z",
        "bookmakers": [{
            "title": "Example Bookmaker",
            "markets": [{
                "key": "h2h",
                "outcomes": [
                    {"name": "Arsenal", "price": 2.0},
                    {"name": "Draw", "price": 4.0},
                    {"name": "Chelsea", "price": 4.0},
                ],
            }],
        }],
    }

    result = analyze_event(event)

    assert result is not None
    assert result["bookmakers_compared"] == 1
    assert result["market_probabilities"]["home_win"] == 0.5