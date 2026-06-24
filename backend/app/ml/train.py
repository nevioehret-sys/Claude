"""Training pipeline for the gradient-boosted ensemble members.

Trains XGBoost, LightGBM, CatBoost, and a Random Forest as multiclass
classifiers (home_win / draw / away_win) on historical match features, then
calibrates each with isotonic regression on a held-out validation split.

NOTE: This module defines the full training pipeline structure. Running it
end-to-end requires a historical match dataset (FEATURE_COLUMNS + labeled
outcomes) which is not bundled in this repository — wire up `load_training_data`
to your data warehouse / CSV exports before calling `train_all_models`.
"""
from __future__ import annotations

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from app.ml.features import FEATURE_COLUMNS

LABEL_MAP = {"away_win": 0, "draw": 1, "home_win": 2}
INV_LABEL_MAP = {v: k for k, v in LABEL_MAP.items()}


def load_training_data(csv_path: str) -> tuple[pd.DataFrame, pd.Series]:
    """Expects a CSV with FEATURE_COLUMNS plus an 'outcome' column in
    {'home_win', 'draw', 'away_win'}."""
    df = pd.read_csv(csv_path)
    X = df[FEATURE_COLUMNS]
    y = df["outcome"].map(LABEL_MAP)
    return X, y


def build_models(random_state: int = 42) -> dict:
    return {
        "xgboost": XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="multi:softprob",
            num_class=3,
            reg_lambda=1.0,
            random_state=random_state,
            eval_metric="mlogloss",
        ),
        "lightgbm": LGBMClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.03,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="multiclass",
            num_class=3,
            random_state=random_state,
        ),
        "catboost": CatBoostClassifier(
            iterations=300,
            depth=5,
            learning_rate=0.03,
            loss_function="MultiClass",
            random_state=random_state,
            verbose=False,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=400,
            max_depth=8,
            min_samples_leaf=10,
            random_state=random_state,
        ),
    }


def train_all_models(X: pd.DataFrame, y: pd.Series, output_dir: str, random_state: int = 42) -> dict:
    """Trains all four classifiers with an 80/20 chronological split (no shuffle, to
    avoid leaking future-tournament information into validation), and persists each
    model + its validation predictions for downstream calibration fitting."""
    split_idx = int(len(X) * 0.8)
    X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]

    models = build_models(random_state)
    results = {}

    for name, model in models.items():
        model.fit(X_train, y_train)
        val_probs = model.predict_proba(X_val)
        joblib.dump(model, f"{output_dir}/{name}.joblib")
        results[name] = {
            "model": model,
            "val_probs": val_probs,
            "val_labels": y_val.to_numpy(),
        }

    return results


def predict_probabilities(model, feature_row: pd.DataFrame) -> dict[str, float]:
    probs = model.predict_proba(feature_row)[0]
    return {INV_LABEL_MAP[i]: float(p) for i, p in enumerate(probs)}
