"""Trace historical forecast coverage without changing model probabilities.

All dates describe the data available before the requested forecast cutoff.
No external data provider is called and no future or same-day match is counted.
"""
from __future__ import annotations

from datetime import date
from typing import Iterable

from .data import Match


def forecast_provenance(
    matches: Iterable[Match],
    cutoff: date,
    *,
    home_team: str,
    away_team: str,
    diagnostics: dict,
    stale_after_days: int = 90,
) -> dict:
    """Summarize exactly the completed fixtures eligible for this forecast."""
    if stale_after_days < 1:
        raise ValueError("stale_after_days must be positive")
    eligible = [match for match in matches if match.date < cutoff]
    if not eligible:
        raise ValueError("Cannot describe a forecast without earlier match results")

    latest = max(match.date for match in eligible)
    age = (cutoff - latest).days
    known_home = any(
        match.home_team == home_team or match.away_team == home_team
        for match in eligible
    )
    known_away = any(
        match.home_team == away_team or match.away_team == away_team
        for match in eligible
    )
    low_data = bool(diagnostics.get("low_data_warning", False))
    warnings: list[str] = []
    if age > stale_after_days:
        warnings.append(
            "Historical results are more than 90 days old relative to the forecast cutoff; "
            "the forecast does not represent current team form."
        )
    if not known_home or not known_away:
        warnings.append(
            "At least one selected team has no match history before the cutoff; "
            "the model relies on competition-wide averages for missing team information."
        )
    if low_data:
        warnings.append(
            "Limited historical match coverage may make these probabilities less reliable."
        )

    return {
        "latest_training_match": latest.isoformat(),
        "days_since_latest_match": age,
        "historical_matches_used": len(eligible),
        "stale_after_days": stale_after_days,
        "is_stale": age > stale_after_days,
        "home_team_has_history": known_home,
        "away_team_has_history": known_away,
        "low_data_warning": low_data,
        "warnings": warnings,
    }
