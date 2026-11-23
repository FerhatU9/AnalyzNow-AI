
from fastapi.testclient import TestClient

from football_intel.api import app


def test_market_odds_endpoint(monkeypatch):

    fake_fixture = {
        "event_id": "test_match",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "bookmakers_compared": 3,
        "market_probabilities": {
            "home_win": 0.5,
            "draw": 0.25,
            "away_win": 0.25,
        },
    }

    monkeypatch.setattr(
        "football_intel.api.fetch_premier_league_odds",
        lambda: [fake_fixture],
    )

    response = TestClient(app).get("/v1/market-odds")

    assert response.status_code == 200

    data = response.json()

    assert data["fixture_count"] == 1
    assert data["fixtures"][0]["bookmakers_compared"] == 3


def test_market_odds_provider_failure(monkeypatch):

    def unavailable():
        raise RuntimeError("Provider unavailable")

    monkeypatch.setattr(
        "football_intel.api.fetch_premier_league_odds",
        unavailable,
    )

    response = TestClient(app).get("/v1/market-odds")

    assert response.status_code == 502
    assert "Provider unavailable" not in response.text