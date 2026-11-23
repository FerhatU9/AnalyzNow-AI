
"""Integration tests for PostgreSQL and FastAPI."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from football_intel.api import app
from football_intel.database import load_matches_from_database


def test_postgresql_historical_matches():
    cutoff = date(2025, 7, 1)

    matches = load_matches_from_database(cutoff)

    assert len(matches) == 1520
    assert all(match.date < cutoff for match in matches)


def test_postgresql_forecast_api(monkeypatch):
    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "postgres")

    response = TestClient(app).post(
        "/v1/forecast",
        json={
            "home_team": "Arsenal FC",
            "away_team": "Chelsea FC",
            "as_of": "2025-07-01",
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["home_team"] == "Arsenal FC"
    assert data["away_team"] == "Chelsea FC"

    probabilities = data["probabilities"]

    assert sum([
        probabilities["home_win"],
        probabilities["draw"],
        probabilities["away_win"],
    ]) == pytest.approx(1.0, abs=0.0001)
