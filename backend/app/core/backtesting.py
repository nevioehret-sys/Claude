"""Backtesting metrics for evaluating model quality on historical World Cups
(2010, 2014, 2018, 2022).

Metrics:
- Brier Score: mean((p - outcome)^2), lower is better, 0 = perfect.
- Log Loss: -mean(outcome*log(p) + (1-outcome)*log(1-p)).
- Calibration Error (ECE): mean |observed_freq - predicted_prob| over bins.
- ROI / Yield: profit relative to total stake, assuming flat or Kelly staking.
- Trefferquote (hit rate): fraction of matches where the highest-probability
  outcome matched the actual result.
"""
from __future__ import annotations

import numpy as np


def brier_score(predicted_probs: np.ndarray, outcomes: np.ndarray) -> float:
    return float(np.mean((predicted_probs - outcomes) ** 2))


def log_loss(predicted_probs: np.ndarray, outcomes: np.ndarray, eps: float = 1e-15) -> float:
    p = np.clip(predicted_probs, eps, 1 - eps)
    return float(-np.mean(outcomes * np.log(p) + (1 - outcomes) * np.log(1 - p)))


def calibration_error(predicted_probs: np.ndarray, outcomes: np.ndarray, n_bins: int = 10) -> float:
    bins = np.linspace(0, 1, n_bins + 1)
    bin_indices = np.digitize(predicted_probs, bins) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)

    errors = []
    weights = []
    for b in range(n_bins):
        mask = bin_indices == b
        if mask.sum() == 0:
            continue
        observed = outcomes[mask].mean()
        predicted = predicted_probs[mask].mean()
        errors.append(abs(observed - predicted))
        weights.append(mask.sum())

    if not errors:
        return 0.0
    return float(np.average(errors, weights=weights))


def hit_rate(predicted_top_outcome: list[str], actual_outcome: list[str]) -> float:
    matches = sum(1 for p, a in zip(predicted_top_outcome, actual_outcome) if p == a)
    return matches / len(actual_outcome) if actual_outcome else 0.0


def roi_and_yield(stakes: np.ndarray, returns: np.ndarray) -> dict[str, float]:
    """stakes: amount staked per bet. returns: amount returned (0 if lost, stake*odds if won)."""
    total_staked = stakes.sum()
    total_returned = returns.sum()
    profit = total_returned - total_staked
    roi = profit / total_staked if total_staked > 0 else 0.0
    yield_pct = roi  # yield is ROI per bet over the whole staked volume, same formula for flat staking
    return {
        "total_staked": float(total_staked),
        "total_returned": float(total_returned),
        "profit": float(profit),
        "roi_pct": float(roi * 100),
        "yield_pct": float(yield_pct * 100),
    }


def run_backtest_report(
    predicted_probs: np.ndarray,
    outcomes: np.ndarray,
    predicted_top_outcome: list[str],
    actual_outcome: list[str],
    stakes: np.ndarray,
    returns: np.ndarray,
) -> dict:
    return {
        "brier_score": brier_score(predicted_probs, outcomes),
        "log_loss": log_loss(predicted_probs, outcomes),
        "calibration_error": calibration_error(predicted_probs, outcomes),
        "hit_rate": hit_rate(predicted_top_outcome, actual_outcome),
        **roi_and_yield(stakes, returns),
    }
