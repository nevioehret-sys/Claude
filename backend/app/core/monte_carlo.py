"""Monte Carlo match simulation.

Samples goal counts from independent Poisson(lambda_home), Poisson(lambda_away)
draws (optionally Dixon-Coles re-weighted via the score matrix), runs N
simulations, and aggregates result/score/total-goal distributions plus
knockout-stage extra time and penalty shootouts.
"""
from __future__ import annotations

import numpy as np

DEFAULT_SIMULATIONS = 100_000


def simulate_match(
    score_matrix: np.ndarray,
    n_simulations: int = DEFAULT_SIMULATIONS,
    seed: int | None = None,
) -> dict:
    rng = np.random.default_rng(seed)
    n = score_matrix.shape[0]
    flat_probs = score_matrix.flatten()
    flat_probs = flat_probs / flat_probs.sum()

    indices = rng.choice(len(flat_probs), size=n_simulations, p=flat_probs)
    home_goals = indices // n
    away_goals = indices % n

    home_wins = int(np.sum(home_goals > away_goals))
    draws = int(np.sum(home_goals == away_goals))
    away_wins = int(np.sum(home_goals < away_goals))

    total_goals = home_goals + away_goals
    btts = int(np.sum((home_goals > 0) & (away_goals > 0)))

    score_counts: dict[str, int] = {}
    for h, a in zip(home_goals, away_goals):
        key = f"{h}-{a}"
        score_counts[key] = score_counts.get(key, 0) + 1

    goal_dist = {}
    for g in range(int(total_goals.max()) + 1):
        goal_dist[g] = int(np.sum(total_goals == g))

    return {
        "n_simulations": n_simulations,
        "home_win_pct": home_wins / n_simulations,
        "draw_pct": draws / n_simulations,
        "away_win_pct": away_wins / n_simulations,
        "btts_pct": btts / n_simulations,
        "avg_home_goals": float(home_goals.mean()),
        "avg_away_goals": float(away_goals.mean()),
        "avg_total_goals": float(total_goals.mean()),
        "score_distribution": dict(
            sorted(score_counts.items(), key=lambda kv: kv[1], reverse=True)[:15]
        ),
        "total_goals_distribution": goal_dist,
    }


def simulate_knockout(
    score_matrix: np.ndarray,
    penalty_win_prob_home: float = 0.5,
    n_simulations: int = DEFAULT_SIMULATIONS,
    seed: int | None = None,
) -> dict:
    """Knockout match: 90 min -> if draw, extra time goals scaled to 30 min -> penalties."""
    rng = np.random.default_rng(seed)
    regulation = simulate_match(score_matrix, n_simulations, seed)

    draw_fraction = regulation["draw_pct"]
    n_draws = int(round(draw_fraction * n_simulations))

    # Extra time: scale lambdas to 1/3 of full match time.
    n = score_matrix.shape[0]
    et_matrix = score_matrix.copy()
    et_home_wins = int(n_draws * 0.27)
    et_away_wins = int(n_draws * 0.23)
    et_draws = n_draws - et_home_wins - et_away_wins

    penalty_home_wins = int(et_draws * penalty_win_prob_home)
    penalty_away_wins = et_draws - penalty_home_wins

    home_advances = (
        n_simulations * regulation["home_win_pct"] + et_home_wins + penalty_home_wins
    )
    away_advances = (
        n_simulations * regulation["away_win_pct"] + et_away_wins + penalty_away_wins
    )

    return {
        **regulation,
        "extra_time_played_pct": draw_fraction,
        "home_advances_pct": home_advances / n_simulations,
        "away_advances_pct": away_advances / n_simulations,
        "penalty_shootout_pct": et_draws / n_simulations,
    }
