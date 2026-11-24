
"""Automated tests for AnalyzNow AI data health."""

from datetime import date, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from football_intel.api import app


client = TestClient(app)

DEMO_CSV = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "synthetic_demo.csv"
)


def test_data_health_success(monkeypatch):
    """The endpoint must report the demonstration dataset."""

    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "csv")
    monkeypatch.setenv("FOOTBALL_CSV_PATH", str(DEMO_CSV))

    response = client.get("/v1/data-health")

    assert response.status_code == 200

    data = response.json()

    assert data["dataset_label"] == "Synthetic demonstration data"
    assert data["historical_matches"] == 100
    assert data["latest_match"] == "2025-07-18"
    assert data["days_old"] == (
        date.today() - date(2025, 7, 18)
    ).days
    assert data["stale_after_days"] == 90
    assert data["is_stale"] is True


def test_data_health_missing_configuration(monkeypatch):
    """Missing dataset configuration must return an error."""

    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "csv")
    monkeypatch.delenv("FOOTBALL_CSV_PATH", raising=False)

    response = client.get("/v1/data-health")

    assert response.status_code == 503


@pytest.mark.parametrize(
    "days_old, expected_stale",
    [(90, False), (91, True)],
)
def test_freshness_threshold(
    monkeypatch, tmp_path, days_old, expected_stale
):
    """Test the boundary between fresh and outdated data."""

    match_date = date.today() - timedelta(days=days_old)
    csv_path = tmp_path / "matches.csv"

    csv_path.write_text(
        "Date,HomeTeam,AwayTeam,FTHG,FTAG\n"
        f"{match_date.isoformat()},Team A,Team B,2,1\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "csv")
    monkeypatch.setenv("FOOTBALL_CSV_PATH", str(csv_path))

    response = client.get("/v1/data-health")

    assert response.status_code == 200
    assert response.json()["is_stale"] is expected_stale
    assert response.json()["historical_matches"] == 1