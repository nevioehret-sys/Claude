"""Poisson and Dixon-Coles goal models.

Poisson: P(X=k) = exp(-lambda) * lambda^k / k!
Dixon-Coles adds a low-score correction tau(x, y, rho) for (0,0),(1,0),(0,1),(1,1)
to fix the independence assumption of plain Poisson, which underestimates draws.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import poisson

MAX_GOALS = 10


def expected_goals(
    home_attack: float,
    home_defence: float,
    away_attack: float,
    away_defence: float,
    home_advantage: float,
    league_avg_goals: float = 1.35,
) -> tuple[float, float]:
    """Combine attack/defence strength ratings into expected goals (lambda_home, lambda_away).

    Ratings are relative to league average (1.0 = average).
    """
    lambda_home = league_avg_goals * home_attack * away_defence * home_advantage
    lambda_away = league_avg_goals * away_attack * home_defence
    return max(lambda_home, 0.05), max(lambda_away, 0.05)


def dixon_coles_tau(x: int, y: int, lambda_home: float, lambda_away: float, rho: float) -> float:
    if x == 0 and y == 0:
        return 1 - lambda_home * lambda_away * rho
    if x == 0 and y == 1:
        return 1 + lambda_home * rho
    if x == 1 and y == 0:
        return 1 + lambda_away * rho
    if x == 1 and y == 1:
        return 1 - rho
    return 1.0


def score_matrix(
    lambda_home: float,
    lambda_away: float,
    rho: float = -0.13,
    max_goals: int = MAX_GOALS,
) -> np.ndarray:
    """Return a (max_goals+1) x (max_goals+1) matrix of P(home=i, away=j), Dixon-Coles adjusted."""
    home_probs = poisson.pmf(np.arange(max_goals + 1), lambda_home)
    away_probs = poisson.pmf(np.arange(max_goals + 1), lambda_away)
    matrix = np.outer(home_probs, away_probs)

    for x in range(2):
        for y in range(2):
            tau = dixon_coles_tau(x, y, lambda_home, lambda_away, rho)
            matrix[x, y] *= tau

    matrix /= matrix.sum()
    return matrix


def outcome_probabilities(matrix: np.ndarray) -> dict[str, float]:
    home_win = float(np.tril(matrix, -1).sum())
    draw = float(np.trace(matrix))
    away_win = float(np.triu(matrix, 1).sum())
    return {"home_win": home_win, "draw": draw, "away_win": away_win}


def btts_probability(matrix: np.ndarray) -> float:
    return float(matrix[1:, 1:].sum())


def over_under_probabilities(matrix: np.ndarray, lines: list[float]) -> dict[str, dict[str, float]]:
    n = matrix.shape[0]
    total_goals = np.add.outer(np.arange(n), np.arange(n))
    result = {}
    for line in lines:
        over = float(matrix[total_goals > line].sum())
        result[str(line)] = {"over": over, "under": 1 - over}
    return result


def top_correct_scores(matrix: np.ndarray, top_n: int = 10) -> list[dict]:
    n = matrix.shape[0]
    flat = [
        {"home": i, "away": j, "probability": float(matrix[i, j])}
        for i in range(n)
        for j in range(n)
    ]
    flat.sort(key=lambda x: x["probability"], reverse=True)
    return flat[:top_n]


def most_likely_total_goals(matrix: np.ndarray) -> int:
    n = matrix.shape[0]
    totals = np.zeros(2 * n - 1)
    for i in range(n):
        for j in range(n):
            totals[i + j] += matrix[i, j]
    return int(np.argmax(totals))
