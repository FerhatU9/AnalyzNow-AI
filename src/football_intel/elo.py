"""Independent Elo benchmark for three-way football match outcomes.

The rating update uses only final results from earlier fixture dates.
No market feed, external model, or additional Python dependency is required.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Iterable

from .backtest import score_forecast
from .data import Match


@dataclass(frozen=True)
class EloConfig:
    k_factor: float = 20.0
    home_advantage: float = 75.0
    starting_rating: float = 1500.0

    def __post_init__(self) -> None:
        if self.k_factor <= 0:
            raise ValueError("k_factor must be positive")
        if not 0 <= self.home_advantage <= 250:
            raise ValueError("home_advantage must be between 0 and 250 Elo points")


def expected_home_score(home_rating: float, away_rating: float, advantage: float) -> float:
    """Expected Elo score (win=1, draw=0.5, loss=0)."""
    return 1.0 / (1.0 + 10 ** ((away_rating - home_rating - advantage) / 400.0))


def outcome_probabilities(expected: float, historical_draw_rate: float) -> dict[str, float]:
    """A coherent 1X2 bridge from Elo's expected score to probabilities.

    Draw likelihood decreases as one side becomes a stronger favourite.
    This is a benchmark assumption, not a calibrated production market model.
    """
    if not 0 < expected < 1 or not 0 <= historical_draw_rate <= 1:
        raise ValueError("Expected score and historical draw rate are out of range")
    draw = min(4 * expected * (1 - expected) * historical_draw_rate,
               2 * min(expected, 1 - expected))
    home = expected - draw / 2
    away = 1 - expected - draw / 2
    return {"home_win": home, "draw": draw, "away_win": away}


def walk_forward_elo(matches: Iterable[Match], config: EloConfig) -> dict[tuple[str, str], dict[str, float]]:
    """Predict before each match day; update ratings only after all that day's games.

    The returned key is (ISO date, displayed fixture) matching the current
    Poisson backtest journal; duplicate fixture keys are explicitly rejected.
    """
    by_date: dict[date, list[Match]] = defaultdict(list)
    for match in matches:
        by_date[match.date].append(match)

    ratings: dict[str, float] = {}
    predictions: dict[tuple[str, str], dict[str, float]] = {}
    completed_matches = 0
    historical_draws = 0

    for day in sorted(by_date):
        day_games = by_date[day]
        draw_rate = (historical_draws + 1) / (completed_matches + 3)
        ratings_before_day = dict(ratings)
        changes: dict[str, float] = defaultdict(float)
        day_predictions: list[tuple[Match, float]] = []

        for match in day_games:
            home_rating = ratings_before_day.get(match.home_team, config.starting_rating)
            away_rating = ratings_before_day.get(match.away_team, config.starting_rating)
            expected = expected_home_score(home_rating, away_rating, config.home_advantage)
            prediction = outcome_probabilities(expected, draw_rate)
            key = (day.isoformat(), f"{match.home_team} vs {match.away_team}")
            if key in predictions:
                raise ValueError(f"Duplicate fixture key {key!r}")
            predictions[key] = prediction
            day_predictions.append((match, expected))

        # Collect rating changes without revealing any same-day match result
        # to another fixture's prediction.
        for match, expected in day_predictions:
            actual = 1.0 if match.outcome == "H" else 0.5 if match.outcome == "D" else 0.0
            delta = config.k_factor * (actual - expected)
            changes[match.home_team] += delta
            changes[match.away_team] -= delta
            historical_draws += int(match.outcome == "D")
            completed_matches += 1
        for club, change in changes.items():
            ratings[club] = ratings_before_day.get(club, config.starting_rating) + change

    return predictions


def select_config(
    matches: list[Match],
    validation_from: date,
    test_from: date,
) -> tuple[EloConfig, list[dict]]:
    """Choose Elo settings using only validation fixtures, never test fixtures."""
    if validation_from >= test_from:
        raise ValueError("Validation must precede the held-out evaluation period")
    training_matches = [m for m in matches if m.date < test_from]
    validation = [m for m in training_matches if m.date >= validation_from]
    if not validation or not any(m.date < validation_from for m in training_matches):
        raise ValueError("Provide historical training and separate validation matches")

    candidates: list[dict] = []
    for k_factor in (12.0, 20.0, 32.0):
        for home_advantage in (40.0, 75.0, 110.0):
            settings = EloConfig(k_factor=k_factor, home_advantage=home_advantage)
            predictions = walk_forward_elo(training_matches, settings)
            brier_total = 0.0
            log_total = 0.0
            for match in validation:
                key = (match.date.isoformat(), f"{match.home_team} vs {match.away_team}")
                brier, log_loss = score_forecast(predictions[key], match.outcome)
                brier_total += brier
                log_total += log_loss
            candidates.append({
                "k_factor": k_factor, "home_advantage": home_advantage,
                "validation_matches": len(validation),
                "brier": brier_total / len(validation),
                "log_loss": log_total / len(validation),
            })
    candidates.sort(key=lambda candidate: (candidate["log_loss"], candidate["brier"]))
    winning = candidates[0]
    return EloConfig(k_factor=winning["k_factor"], home_advantage=winning["home_advantage"]), candidates
