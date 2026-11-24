"""Forecast freshness is based only on data strictly before the cutoff."""
from datetime import date, timedelta

from fastapi.testclient import TestClient

from football_intel.api import app
from football_intel.data import Match
from football_intel.forecast_quality import forecast_provenance


def sample_matches(days_ago: int) -> list[Match]:
    cutoff = date(2026, 11, 24)
    return [
        Match(cutoff - timedelta(days=days_ago), "Home", "Away", 2, 1),
        Match(cutoff, "Home", "Away", 7, 0),
        Match(cutoff + timedelta(days=1), "Home", "Away", 1, 0),
    ]


def provenance(matches: list[Match], **kwargs) -> dict:
    return forecast_provenance(
        matches, date(2026, 11, 24),
        home_team=kwargs.get("home_team", "Home"),
        away_team=kwargs.get("away_team", "Away"),
        diagnostics=kwargs.get("diagnostics", {"low_data_warning": False}),
    )


def test_excludes_same_day_and_future_matches():
    result = provenance(sample_matches(10))
    assert result["historical_matches_used"] == 1
    assert result["latest_training_match"] == "2026-11-14"
    assert result["days_since_latest_match"] == 10
    assert result["is_stale"] is False
    assert result["warnings"] == []


def test_stale_data_warning_uses_strict_ninety_day_threshold():
    assert provenance(sample_matches(90))["is_stale"] is False
    old = provenance(sample_matches(91))
    assert old["is_stale"] is True
    assert "more than 90 days" in old["warnings"][0]


def test_missing_team_and_low_data_are_disclosed():
    result = provenance(
        sample_matches(5), away_team="Unknown",
        diagnostics={"low_data_warning": True},
    )
    assert result["home_team_has_history"] is True
    assert result["away_team_has_history"] is False
    assert result["low_data_warning"] is True
    assert len(result["warnings"]) == 2


def test_no_earlier_results_is_rejected():
    import pytest
    with pytest.raises(ValueError, match="earlier match"):
        provenance([Match(date(2026, 11, 24), "Home", "Away", 1, 0)])


def test_api_returns_data_quality_without_changing_probabilities(monkeypatch, tmp_path):
    csv = tmp_path / "history.csv"
    rows = ["Date,HomeTeam,AwayTeam,FTHG,FTAG"]
    for i in range(20):
        day = date(2025, 1, 1) + timedelta(days=i)
        rows.append(f"{day.isoformat()},Home,Away,{i % 3},{i % 2}")
    csv.write_text("\n".join(rows) + "\n", encoding="utf-8")
    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "csv")
    monkeypatch.setenv("FOOTBALL_CSV_PATH", str(csv))
    response = TestClient(app).post(
        "/v1/forecast",
        json={"home_team": "Home", "away_team": "Away", "as_of": "2026-11-24"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data_quality"]["historical_matches_used"] == 20
    assert body["data_quality"]["latest_training_match"] == "2025-01-20"
    assert body["data_quality"]["is_stale"] is True
    probabilities = body["probabilities"]
    assert abs(sum(probabilities[k] for k in ("home_win", "draw", "away_win")) - 1) < 0.00001
