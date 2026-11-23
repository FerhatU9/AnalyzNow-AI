"""Development API. Deliberately no network ingestion, authentication, or production claim."""

from __future__ import annotations

import os
import psycopg

from .database import load_matches_from_database
from .market_odds import fetch_premier_league_odds

from datetime import date
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .data import load_matches
from .model import train, forecast

app = FastAPI(title="AnalyzNow AI", version="0.2.0")


class ForecastRequest(BaseModel):
    home_team: str = Field(min_length=1, max_length=120)
    away_team: str = Field(min_length=1, max_length=120)
    as_of: date | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": "0.2.0", "data": "configured" if os.getenv("FOOTBALL_CSV_PATH") else "not configured"}


@app.post("/v1/forecast")
def predict(payload: ForecastRequest) -> dict:
    as_of = payload.as_of or date.today()
    source = os.getenv("FOOTBALL_DATA_SOURCE", "csv").lower()

    try:
        if source == "postgres":
            matches = load_matches_from_database(as_of)

        elif source == "csv":
            csv_path = os.getenv("FOOTBALL_CSV_PATH")
            if not csv_path:
                raise HTTPException(
                    status_code=503,
                    detail="FOOTBALL_CSV_PATH is not configured",
                )
            matches = load_matches(csv_path)

        else:
            raise HTTPException(
                status_code=503,
                detail="Invalid FOOTBALL_DATA_SOURCE configuration",
            )

        model = train(matches, as_of)
        return forecast(
            model,
            payload.home_team,
            payload.away_team,
        )

    except psycopg.Error as exc:
        raise HTTPException(
            status_code=503,
            detail="Football database is temporarily unavailable",
        ) from exc

    except (ValueError, OSError) as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

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
