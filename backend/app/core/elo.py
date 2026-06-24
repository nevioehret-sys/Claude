"""Elo rating system adapted for international football (World Cup tuned).

Expected score: E_home = 1 / (1 + 10^(-(R_home - R_away + HFA) / 400))
Update: R' = R + K * goal_diff_weight * (actual - expected)
"""
from __future__ import annotations

import math

HOME_FIELD_ADVANTAGE = 60.0  # elo points, reduced for neutral WM venues
BASE_K = 30.0

TOURNAMENT_WEIGHT = {
    "friendly": 1.0,
    "qualifier": 2.5,
    "group_stage": 3.5,
    "round_of_16": 4.0,
    "quarter_final": 4.25,
    "semi_final": 4.5,
    "final": 5.0,
}


def expected_score(rating_home: float, rating_away: float, neutral_venue: bool = True) -> float:
    hfa = 0.0 if neutral_venue else HOME_FIELD_ADVANTAGE
    diff = rating_home - rating_away + hfa
    return 1.0 / (1.0 + 10 ** (-diff / 400.0))


def goal_diff_multiplier(goal_diff: int) -> float:
    """Elo goal-difference weighting (as used by eloratings.net)."""
    abs_diff = abs(goal_diff)
    if abs_diff <= 1:
        return 1.0
    if abs_diff == 2:
        return 1.5
    return (11 + abs_diff) / 8.0


def update_ratings(
    rating_home: float,
    rating_away: float,
    goals_home: int,
    goals_away: int,
    stage: str = "group_stage",
    neutral_venue: bool = True,
) -> tuple[float, float]:
    expected_home = expected_score(rating_home, rating_away, neutral_venue)
    if goals_home > goals_away:
        actual_home = 1.0
    elif goals_home == goals_away:
        actual_home = 0.5
    else:
        actual_home = 0.0

    k = BASE_K * TOURNAMENT_WEIGHT.get(stage, 3.0)
    g = goal_diff_multiplier(goals_home - goals_away)
    delta = k * g * (actual_home - expected_home)

    return rating_home + delta, rating_away - delta


def elo_to_match_probabilities(rating_home: float, rating_away: float, neutral_venue: bool = True) -> dict[str, float]:
    """Approximate 1X2 from Elo using a draw-margin heuristic (logistic spread)."""
    expected_home = expected_score(rating_home, rating_away, neutral_venue)
    diff = rating_home - rating_away + (0.0 if neutral_venue else HOME_FIELD_ADVANTAGE)

    draw_peak = 0.27
    draw_width = 600.0
    draw_prob = draw_peak * math.exp(-(diff ** 2) / (2 * draw_width ** 2))

    home_win = expected_home * (1 - draw_prob)
    away_win = (1 - expected_home) * (1 - draw_prob)

    total = home_win + draw_prob + away_win
    return {"home_win": home_win / total, "draw": draw_prob / total, "away_win": away_win / total}
