"""Ensemble model combining Poisson/Dixon-Coles, Elo, and gradient-boosted classifiers
(XGBoost, LightGBM, CatBoost, Random Forest) into calibrated match probabilities.

Weighting strategy: a simple inverse-Brier-score weighted average across model
outputs, computed during backtesting and stored per-competition. Falls back to
equal weights when no historical weight is available (e.g. cold start).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from app.core import elo as elo_module
from app.core.poisson import outcome_probabilities, score_matrix
from app.core.calibration import ProbabilityCalibrator, normalize_multiclass

DEFAULT_WEIGHTS = {
    "poisson_dixon_coles": 0.30,
    "elo": 0.20,
    "xgboost": 0.20,
    "lightgbm": 0.15,
    "catboost": 0.10,
    "random_forest": 0.05,
}


@dataclass
class TeamStrength:
    attack: float
    defence: float
    elo_rating: float


@dataclass
class EnsembleConfig:
    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))
    home_advantage: float = 1.10
    rho: float = -0.13
    neutral_venue: bool = True


def _normalize_weights(weights: dict[str, float], available: set[str]) -> dict[str, float]:
    filtered = {k: v for k, v in weights.items() if k in available}
    total = sum(filtered.values())
    if total <= 0:
        n = len(available)
        return {k: 1 / n for k in available}
    return {k: v / total for k, v in filtered.items()}


def ensemble_match_probabilities(
    home: TeamStrength,
    away: TeamStrength,
    config: EnsembleConfig,
    ml_probabilities: dict[str, dict[str, float]] | None = None,
    calibrators: dict[str, ProbabilityCalibrator] | None = None,
) -> dict:
    """ml_probabilities: optional {'xgboost': {'home_win':..,'draw':..,'away_win':..}, ...}"""
    from app.core.poisson import expected_goals

    lambda_home, lambda_away = expected_goals(
        home.attack, home.defence, away.attack, away.defence, config.home_advantage
    )
    matrix = score_matrix(lambda_home, lambda_away, config.rho)
    poisson_probs = outcome_probabilities(matrix)
    elo_probs = elo_module.elo_to_match_probabilities(
        home.elo_rating, away.elo_rating, config.neutral_venue
    )

    model_outputs = {
        "poisson_dixon_coles": poisson_probs,
        "elo": elo_probs,
        **(ml_probabilities or {}),
    }

    weights = _normalize_weights(config.weights, set(model_outputs.keys()))

    blended = {"home_win": 0.0, "draw": 0.0, "away_win": 0.0}
    for model_name, probs in model_outputs.items():
        w = weights.get(model_name, 0.0)
        for outcome in blended:
            blended[outcome] += w * probs.get(outcome, 0.0)

    if calibrators:
        for outcome, calibrator in calibrators.items():
            blended[outcome] = float(calibrator.transform(np.array([blended[outcome]]))[0])
        blended = normalize_multiclass(blended)
    else:
        blended = normalize_multiclass(blended)

    return {
        "probabilities": blended,
        "lambda_home": lambda_home,
        "lambda_away": lambda_away,
        "score_matrix": matrix,
        "model_breakdown": model_outputs,
        "weights_used": weights,
    }


def confidence_score(probabilities: dict[str, float], model_breakdown: dict[str, dict[str, float]]) -> int:
    """0-100 confidence: combines how decisive the blended distribution is (max prob vs uniform)
    with agreement across constituent models (low variance of their predicted top outcome)."""
    max_prob = max(probabilities.values())
    decisiveness = (max_prob - 1 / 3) / (1 - 1 / 3)

    top_outcome = max(probabilities, key=probabilities.get)
    model_agreement_votes = [
        1.0 if max(probs, key=probs.get) == top_outcome else 0.0
        for probs in model_breakdown.values()
    ]
    agreement = float(np.mean(model_agreement_votes)) if model_agreement_votes else 0.5

    raw = 0.6 * decisiveness + 0.4 * agreement
    return int(round(max(0.0, min(1.0, raw)) * 100))
