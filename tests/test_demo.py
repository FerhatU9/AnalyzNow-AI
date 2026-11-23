"""Portfolio demonstration and team-catalog smoke tests."""
from pathlib import Path

import psycopg
from fastapi.testclient import TestClient

from football_intel.api import app

SYNTHETIC_DATA = Path(__file__).resolve().parents[1] / "data" / "synthetic_demo.csv"


def test_synthetic_catalog_is_clearly_labeled(monkeypatch):
    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "csv")
    monkeypatch.setenv("FOOTBALL_CSV_PATH", str(SYNTHETIC_DATA))

    response = TestClient(app).get("/v1/teams")

    assert response.status_code == 200
    body = response.json()
    assert body["dataset_label"] == "Synthetic demonstration data"
    assert body["last_match_date"] == "2025-07-18"
    assert len(body["teams"]) == 6
    assert "Demo North" in body["teams"]
    assert "Demo South" in body["teams"]


def test_synthetic_forecast_cannot_be_mistaken_for_real_matches(monkeypatch):
    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "csv")
    monkeypatch.setenv("FOOTBALL_CSV_PATH", str(SYNTHETIC_DATA))

    response = TestClient(app).post(
        "/v1/forecast",
        json={
            "home_team": "Demo North",
            "away_team": "Demo South",
            "as_of": "2025-07-01",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["dataset_label"] == "Synthetic demonstration data"
    assert "fictional" in body["notice"]
    assert body["expected_goals"]["home"] > 0


def test_catalog_reports_missing_csv_configuration(monkeypatch):
    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "csv")
    monkeypatch.delenv("FOOTBALL_CSV_PATH", raising=False)

    response = TestClient(app).get("/v1/teams")
    assert response.status_code == 503


def test_catalog_hides_database_error_details(monkeypatch):
    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "postgres")

    def fail(_as_of):
        raise psycopg.OperationalError("private database host details")

    monkeypatch.setattr("football_intel.api.load_matches_from_database", fail)
    response = TestClient(app).get("/v1/teams")

    assert response.status_code == 503
    assert "private database" not in response.text
