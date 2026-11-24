"""Local football forecasting API and optional bookmaker-data endpoints.

The application is a research tool, not a public production or betting service.
"""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .data import Match, load_matches, teams_in
from .database import load_matches_from_database
from .market_odds import fetch_premier_league_odds
from .forecast_quality import forecast_provenance
from .model import forecast, train

load_dotenv()
app = FastAPI(title="AnalyzNow AI", version="0.2.0")


class ForecastRequest(BaseModel):
    home_team: str = Field(min_length=1, max_length=120)
    away_team: str = Field(min_length=1, max_length=120)
    as_of: date | None = None


def _data_source() -> str:
    return os.getenv("FOOTBALL_DATA_SOURCE", "csv").strip().lower()


def _dataset_label() -> str:
    source = _data_source()
    if source == "postgres":
        return "Configured PostgreSQL match results"
    if source == "csv":
        path = os.getenv("FOOTBALL_CSV_PATH", "")
        demo_file = Path(__file__).resolve().parents[2] / "data" / "synthetic_demo.csv"
        if path and Path(path).resolve() == demo_file.resolve():
            return "Synthetic demonstration data"
        return "Configured CSV match results"
    return "Unknown data source"


def _load_configured_matches(as_of: date) -> list[Match]:
    source = _data_source()
    if source == "postgres":
        return load_matches_from_database(as_of)
    if source == "csv":
        csv_path = os.getenv("FOOTBALL_CSV_PATH")
        if not csv_path:
            raise HTTPException(
                status_code=503,
                detail="FOOTBALL_CSV_PATH is not configured",
            )
        return load_matches(csv_path)
    raise HTTPException(
        status_code=503,
        detail="Invalid FOOTBALL_DATA_SOURCE configuration",
    )


@app.get("/health")
def health() -> dict:
    """Process status only; does not probe database or provider availability."""
    source = _data_source()
    configured = bool(os.getenv("FOOTBALL_CSV_PATH")) if source == "csv" else (
        bool(os.getenv("POSTGRES_PASSWORD")) if source == "postgres" else False
    )
    return {"status": "ok", "version": "0.2.0", "data_source": source, "configured": configured}


@app.get("/v1/teams")
def get_teams() -> dict:
    """Return the distinct teams from the configured match source."""
    try:
        matches = _load_configured_matches(date.today())
        if not matches:
            raise HTTPException(status_code=503, detail="No match data is available")
        return {
            "teams": teams_in(matches),
            "dataset_label": _dataset_label(),
            "last_match_date": max(match.date for match in matches).isoformat(),
        }
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Football database is temporarily unavailable",
        ) from exc
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=503, detail="Match data is unavailable") from exc

@app.get("/v1/data-health")
def get_data_health() -> dict:
    """Check whether historical football data is up to date."""
    today = date.today()

    try:
        matches = _load_configured_matches(today)
        historical = [m for m in matches if m.date < today]

        if not historical:
            raise HTTPException(
                status_code=503,
                detail="No completed historical matches available",
            )

        latest = max(m.date for m in historical)
        days_old = (today - latest).days

        return {
            "dataset_label": _dataset_label(),
            "historical_matches": len(historical),
            "latest_match": latest.isoformat(),
            "days_old": days_old,
            "stale_after_days": 90,
            "is_stale": days_old > 90,
        }

    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Football database is unavailable",
        ) from exc

    except (ValueError, OSError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Historical match data is unavailable",
        ) from exc

@app.post("/v1/forecast")
def predict(payload: ForecastRequest) -> dict:
    as_of = payload.as_of or date.today()

    try:
        matches = _load_configured_matches(as_of)
        model = train(matches, as_of)
        result = forecast(model, payload.home_team, payload.away_team)
        result["data_quality"] = forecast_provenance(
            matches,
            as_of,
            home_team=payload.home_team,
            away_team=payload.away_team,
            diagnostics=result["diagnostics"],
        )
        result["dataset_label"] = _dataset_label()
        if result["dataset_label"] == "Synthetic demonstration data":
            result["notice"] = (
                "Synthetic demonstration only: scores are fictional and "
                "probabilities do not describe real football teams or fixtures."
            )
        return result
    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Football database is temporarily unavailable",
        ) from exc
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/market-odds")
def get_market_odds() -> dict:
    """Return current Premier League bookmaker probabilities."""
    try:
        fixtures = fetch_premier_league_odds()
        return {
            "competition": "Premier League",
            "market": "1X2",
            "fixture_count": len(fixtures),
            "fixtures": fixtures,
            "notice": (
                "Market probabilities are based on bookmaker odds. "
                "They are not statistical model predictions."
            ),
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=503,
            detail="Market odds configuration or data is unavailable",
        ) from exc
    except (RuntimeError, OSError) as exc:
        raise HTTPException(
            status_code=502,
            detail="Unable to retrieve current bookmaker odds",
        ) from exc
