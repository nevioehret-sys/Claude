"""Probability calibration: Platt Scaling (logistic) and Isotonic Regression.

Both are fit per-outcome-class on held-out validation predictions vs actual outcomes,
then applied to raw ensemble probabilities before they're used downstream.
"""
from __future__ import annotations

import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


class ProbabilityCalibrator:
    """Wraps Platt scaling and isotonic regression for one binary outcome (e.g. 'home_win')."""

    def __init__(self, method: str = "isotonic"):
        if method not in {"platt", "isotonic"}:
            raise ValueError("method must be 'platt' or 'isotonic'")
        self.method = method
        self._model = None

    def fit(self, raw_probs: np.ndarray, outcomes: np.ndarray) -> "ProbabilityCalibrator":
        raw_probs = np.clip(raw_probs, 1e-6, 1 - 1e-6)
        if self.method == "platt":
            logits = np.log(raw_probs / (1 - raw_probs)).reshape(-1, 1)
            self._model = LogisticRegression().fit(logits, outcomes)
        else:
            self._model = IsotonicRegression(out_of_bounds="clip").fit(raw_probs, outcomes)
        return self

    def transform(self, raw_probs: np.ndarray) -> np.ndarray:
        raw_probs = np.clip(np.asarray(raw_probs), 1e-6, 1 - 1e-6)
        if self._model is None:
            return raw_probs
        if self.method == "platt":
            logits = np.log(raw_probs / (1 - raw_probs)).reshape(-1, 1)
            return self._model.predict_proba(logits)[:, 1]
        return self._model.predict(raw_probs)

    def reliability_curve(self, raw_probs: np.ndarray, outcomes: np.ndarray, n_bins: int = 10):
        return calibration_curve(outcomes, raw_probs, n_bins=n_bins)


def normalize_multiclass(probs: dict[str, float]) -> dict[str, float]:
    """Re-normalize a dict of class probabilities (after independent calibration) to sum to 1."""
    total = sum(probs.values())
    if total <= 0:
        n = len(probs)
        return {k: 1 / n for k in probs}
    return {k: v / total for k, v in probs.items()}
