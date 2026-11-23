import pytest
from fastapi.testclient import TestClient
from football_intel.api import app


def test_health(monkeypatch):
    monkeypatch.delenv("FOOTBALL_CSV_PATH", raising=False)
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_missing_data_not_hidden(monkeypatch):
    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "csv")
    monkeypatch.delenv("FOOTBALL_CSV_PATH", raising=False)

    response = TestClient(app).post(
        "/v1/forecast",
        json={
            "home_team": "A",
            "away_team": "B"
        }
    )

    assert response.status_code == 503


def test_forecast_endpoint(monkeypatch, tmp_path):
    path = tmp_path / "fixtures.csv"
    rows = "Date,HomeTeam,AwayTeam,FTHG,FTAG\n"
    for day in range(1, 20):
        rows += f"2025-01-{day:02d},A,B,{day % 4},{day % 3}\n"
    path.write_text(rows, encoding="utf-8")
    monkeypatch.setenv("FOOTBALL_CSV_PATH", str(path))
    response = TestClient(app).post("/v1/forecast", json={"home_team": "A", "away_team": "B", "as_of": "2025-02-01"})
    assert response.status_code == 200
    assert response.json()["model"] == "weighted_poisson_baseline_v0.1"
