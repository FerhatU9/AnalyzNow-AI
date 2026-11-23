
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

def test_duplicate_bookmaker_quotes_only_count_once():
    event = {
        "id": "duplicate-quote",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "commence_time": "2026-12-01T19:00:00Z",
        "bookmakers": [
            {
                "key": "example",
                "markets": [{
                    "key": "h2h",
                    "last_update": "2026-11-23T15:00:00Z",
                    "outcomes": [
                        {"name": "Arsenal", "price": 2.0},
                        {"name": "Draw", "price": 4.0},
                        {"name": "Chelsea", "price": 4.0},
                    ],
                }],
            },
            {
                "key": "example",
                "markets": [{
                    "key": "h2h",
                    "last_update": "2026-11-23T16:00:00Z",
                    "outcomes": [
                        {"name": "Arsenal", "price": 3.0},
                        {"name": "Draw", "price": 3.0},
                        {"name": "Chelsea", "price": 3.0},
                    ],
                }],
            },
        ],
    }

    result = analyze_event(event)
    assert result is not None
    assert result["bookmakers_compared"] == 1
    assert result["market_probabilities"]["home_win"] == pytest.approx(0.5)
    assert result["latest_odds_update"] == "2026-11-23T15:00:00Z"


@pytest.mark.parametrize("broken_event", [
    None,
    {},
    {"id": "bad", "home_team": "Arsenal", "away_team": "Chelsea",
     "commence_time": "invalid", "bookmakers": []},
    {"id": "bad", "home_team": "Arsenal", "away_team": "Chelsea",
     "commence_time": "2026-12-01T19:00:00", "bookmakers": []},
    {"id": "bad", "home_team": "Arsenal", "away_team": "Chelsea",
     "commence_time": "2026-12-01T19:00:00Z", "bookmakers": "bad"},
])
def test_invalid_event_is_skipped_safely(broken_event):
    assert analyze_event(broken_event) is None


def test_non_numeric_quote_is_skipped_safely():
    event = {
        "id": "bad-price",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "commence_time": "2026-12-01T19:00:00Z",
        "bookmakers": [{
            "key": "example",
            "markets": [{
                "key": "h2h",
                "outcomes": [
                    {"name": "Arsenal", "price": "not-a-price"},
                    {"name": "Draw", "price": 4.0},
                    {"name": "Chelsea", "price": 4.0},
                ],
            }],
        }],
    }
    assert analyze_event(event) is None
