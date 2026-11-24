"""Interpretable, recency-weighted independent Poisson baseline.

Research baseline, NOT an empirically validated or production betting model.
No LLM can alter or generate probabilities here.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from .data import Match


@dataclass(frozen=True)
class GoalModel:
    cutoff: date
    weighted_home_goals: float
    weighted_away_goals: float
    weighted_matches: float
    team_home_for: dict[str, float]
    team_home_against: dict[str, float]
    team_home_count: dict[str, float]
    team_away_for: dict[str, float]
    team_away_against: dict[str, float]
    team_away_count: dict[str, float]
    match_count: int


def train(matches: list[Match], as_of: date, half_life_days: float = 365.0) -> GoalModel:
    """Train only on fixture dates STRICTLY before as_of (prevents same-day leakage)."""
    if half_life_days <= 0:
        raise ValueError("half_life_days must be positive")
    past = [m for m in matches if m.date < as_of]
    if not past:
        raise ValueError("No completed historical matches before the forecast cutoff")
    home_for, home_against, home_n = {}, {}, {}
    away_for, away_against, away_n = {}, {}, {}
    total_home, total_away, total_weight = 0.0, 0.0, 0.0
    for m in past:
        age = (as_of - m.date).days
        weight = math.exp(-math.log(2.0) * age / half_life_days)
        total_home += weight * m.home_goals
        total_away += weight * m.away_goals
        total_weight += weight
        for key, value in ((home_for, m.home_goals), (home_against, m.away_goals), (home_n, 1.0)):
            key[m.home_team] = key.get(m.home_team, 0.0) + weight * value
        for key, value in ((away_for, m.away_goals), (away_against, m.home_goals), (away_n, 1.0)):
            key[m.away_team] = key.get(m.away_team, 0.0) + weight * value
    return GoalModel(as_of, total_home / total_weight, total_away / total_weight,
                     total_weight, home_for, home_against, home_n,
                     away_for, away_against, away_n, len(past))


def expected_goals(model: GoalModel, home: str, away: str, shrink_matches: float = 6.0) -> tuple[float, float, dict]:
    """Empirical attack/defence factors with shrinkage to competition means."""
    if home.casefold() == away.casefold() or not home.strip() or not away.strip():
        raise ValueError("Two different, non-empty teams required")
    if shrink_matches <= 0:
        raise ValueError("shrink_matches must be positive")
    home_base = max(model.weighted_home_goals, 0.10)
    away_base = max(model.weighted_away_goals, 0.10)

    def ratio(total: dict, counts: dict, team: str, prior: float) -> float:
        count = counts.get(team, 0.0)
        return (total.get(team, 0.0) + prior * shrink_matches) / (count + shrink_matches) / prior

    # Home-team scoring / its opponent's away conceding; vice versa for away goals.
    home_attack = ratio(model.team_home_for, model.team_home_count, home, home_base)
    away_defence = ratio(model.team_away_against, model.team_away_count, away, home_base)
    away_attack = ratio(model.team_away_for, model.team_away_count, away, away_base)
    home_defence = ratio(model.team_home_against, model.team_home_count, home, away_base)
    expected_home = home_base * home_attack * away_defence
    expected_away = away_base * away_attack * home_defence
    # Unrecognized teams get a conservative prior instead of fabricated team history.
    home_n = model.team_home_count.get(home, 0.0)
    away_n = model.team_away_count.get(away, 0.0)
    return expected_home, expected_away, {
        "prior_matches": model.match_count,
        "home_team_weighted_home_games": round(home_n, 2),
        "away_team_weighted_away_games": round(away_n, 2),
        "home_team_unseen": home_n == 0.0,
        "away_team_unseen": away_n == 0.0,
        "low_data_warning": home_n < 3.0 or away_n < 3.0 or model.match_count < 50,
        "model_assumption": "Independent goal counts; does not yet model lineup, xG, tactics or correlated scores.",
    }


def poisson_probs(lam: float, limit: int) -> list[float]:
    if not (0 < lam < 100) or not math.isfinite(lam):
        raise ValueError("Invalid goal intensity")
    probabilities = [math.exp(-lam)]
    for goal in range(1, limit + 1):
        probabilities.append(probabilities[-1] * lam / goal)
    return probabilities


def forecast(model: GoalModel, home: str, away: str, *, max_display_scores: int = 5) -> dict:
    if max_display_scores < 1:
        raise ValueError("max_display_scores must be positive")
    expected_home, expected_away, diagnostics = expected_goals(model, home, away)
    limit = max(20, int(max(expected_home, expected_away) + 12 * math.sqrt(max(expected_home, expected_away))))
    p_home, p_away = poisson_probs(expected_home, limit), poisson_probs(expected_away, limit)
    mass = sum(p_home) * sum(p_away)
    # Compute all markets from the same scoreline grid, ensuring coherence.
    outcomes = {"H": 0.0, "D": 0.0, "A": 0.0}
    over_25, btts = 0.0, 0.0
    top = []
    for i, ph in enumerate(p_home):
        for j, pa in enumerate(p_away):
            probability = ph * pa / mass
            outcomes["H" if i > j else "A" if i < j else "D"] += probability
            over_25 += probability if i + j >= 3 else 0
            btts += probability if i >= 1 and j >= 1 else 0
            top.append((probability, i, j))
    top.sort(reverse=True)
    return {
        "model": "weighted_poisson_baseline_v0.1",
        "as_of": model.cutoff.isoformat(),
        "home_team": home,
        "away_team": away,
        "expected_goals": {"home": round(expected_home, 4), "away": round(expected_away, 4)},
        "probabilities": {"home_win": round(outcomes["H"], 6), "draw": round(outcomes["D"], 6),
                          "away_win": round(outcomes["A"], 6), "over_2_5": round(over_25, 6),
                          "under_2_5": round(1 - over_25, 6), "both_teams_score": round(btts, 6)},
        "top_scorelines": [{"score": f"{i}-{j}", "probability": round(p, 6)} for p, i, j in top[:max_display_scores]],
        "diagnostics": {**diagnostics, "truncated_score_mass": round(1 - mass, 12)},
        "notice": "Research forecast, not a betting recommendation. Historical backtests do not establish reliable current-match accuracy.",
    }
