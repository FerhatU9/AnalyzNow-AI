"""Strict date-based walk-forward evaluation and league-frequency baseline."""
from __future__ import annotations

import math
from collections import Counter
from datetime import date
from .data import Match
from .model import train, forecast


def score_forecast(p: dict[str, float], actual: str) -> tuple[float, float]:
    labels = {"H": "home_win", "D": "draw", "A": "away_win"}
    if actual not in labels:
        raise ValueError(f"Unknown outcome {actual!r}")
    truth = {label: (1.0 if outcome == actual else 0.0) for outcome, label in labels.items()}
    brier = sum((p[key] - value) ** 2 for key, value in truth.items())
    log_loss = -math.log(max(p[labels[actual]], 1e-12))
    return brier, log_loss


def backtest(matches: list[Match], min_training_matches: int = 80, test_from: date | None = None) -> dict:
    """Backtest complete fixtures by date; no train row on/test-after same date."""
    if min_training_matches < 1:
        raise ValueError("min_training_matches must be >= 1")
    ordered = sorted(matches, key=lambda m: m.date)
    days = sorted({m.date for m in ordered})
    evaluated = []
    for day in days:
        previous = [m for m in ordered if m.date < day]
        if len(previous) < min_training_matches or (test_from is not None and day < test_from):
            continue
        current = [m for m in ordered if m.date == day]
        model = train(previous, as_of=day)
        counts = Counter(m.outcome for m in previous)
        base = {"home_win": (counts["H"] + 1) / (len(previous) + 3),
                "draw": (counts["D"] + 1) / (len(previous) + 3),
                "away_win": (counts["A"] + 1) / (len(previous) + 3)}
        for match in current:
            probabilities = forecast(model, match.home_team, match.away_team)["probabilities"]
            score = score_forecast(probabilities, match.outcome)
            base_score = score_forecast(base, match.outcome)
            evaluated.append({"fixture": f"{match.home_team} vs {match.away_team}",
                              "date": match.date.isoformat(), "actual": match.outcome,
                              "model_brier": score[0], "model_log_loss": score[1],
                              "baseline_brier": base_score[0], "baseline_log_loss": base_score[1],
                              "forecast": {key: probabilities[key] for key in ("home_win", "draw", "away_win")}})
    if not evaluated:
        raise ValueError(f"Insufficient historical fixtures to evaluate with min_training_matches={min_training_matches}")
    n = len(evaluated)
    return {"model": "weighted_poisson_baseline_v0.1",
            "method": "Walk-forward by fixture date; training uses strictly earlier dates; Laplace-smoothed past H/D/A league rates baseline",
            "test_from": test_from.isoformat() if test_from else None,
            "n_test_matches": n, "first_test_date": evaluated[0]["date"], "last_test_date": evaluated[-1]["date"],
            "model_brier": round(sum(e["model_brier"] for e in evaluated) / n, 6),
            "baseline_brier": round(sum(e["baseline_brier"] for e in evaluated) / n, 6),
            "model_log_loss": round(sum(e["model_log_loss"] for e in evaluated) / n, 6),
            "baseline_log_loss": round(sum(e["baseline_log_loss"] for e in evaluated) / n, 6),
            "note": "Evaluation is only meaningful when run on adequate, legally permitted, real-world histories.",
            "individual_forecasts": evaluated}
