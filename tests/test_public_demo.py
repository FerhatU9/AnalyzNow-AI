"""Safety controls for the public synthetic-only demonstration."""
from fastapi.testclient import TestClient
from football_intel.api import app


def test_public_demo_disables_live_market_odds(monkeypatch):
    monkeypatch.setenv("ANALYZNOW_PUBLIC_DEMO", "1")
    monkeypatch.delenv("ODDS_API_KEY", raising=False)
    response = TestClient(app).get("/v1/market-odds")
    assert response.status_code == 404
    assert "public demonstration" in response.json()["detail"]


def test_normal_missing_provider_behavior_is_unchanged(monkeypatch):
    monkeypatch.delenv("ANALYZNOW_PUBLIC_DEMO", raising=False)
    monkeypatch.delenv("ODDS_API_KEY", raising=False)
    response = TestClient(app).get("/v1/market-odds")
    assert response.status_code == 503


def test_public_synthetic_csv_identified_as_fictional(monkeypatch):
    from pathlib import Path

    synthetic = Path(__file__).resolve().parents[1] / "data" / "synthetic_demo.csv"
    monkeypatch.setenv("ANALYZNOW_PUBLIC_DEMO", "1")
    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "csv")
    monkeypatch.setenv("FOOTBALL_CSV_PATH", str(synthetic))

    catalog = TestClient(app).get("/v1/teams")
    assert catalog.status_code == 200
    assert catalog.json()["dataset_label"] == "Synthetic demonstration data"
    assert "Demo City" in catalog.json()["teams"]
