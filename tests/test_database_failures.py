
import psycopg
from fastapi.testclient import TestClient

from football_intel.api import app


def test_database_connection_failure(monkeypatch):
    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "postgres")

    def unavailable_database(as_of):
        raise psycopg.OperationalError(
            "Private database connection details"
        )

    monkeypatch.setattr(
        "football_intel.api.load_matches_from_database",
        unavailable_database,
    )

    response = TestClient(app).post(
        "/v1/forecast",
        json={
            "home_team": "Arsenal FC",
            "away_team": "Chelsea FC",
            "as_of": "2025-07-01",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Football database is temporarily unavailable"
    )
    assert "Private database" not in response.text
