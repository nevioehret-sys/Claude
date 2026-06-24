"""Feature engineering for the gradient-boosted model layer (XGBoost / LightGBM /
CatBoost / Random Forest). Produces one feature row per match from team-level
inputs. These features feed the classifiers that participate in the ensemble
alongside Poisson/Dixon-Coles and Elo.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "fifa_rank_diff",
    "elo_diff",
    "spi_diff",
    "xg_diff",
    "xga_diff",
    "shots_diff",
    "shots_on_target_diff",
    "possession_diff",
    "pass_accuracy_diff",
    "ppda_diff",
    "form_5_diff",
    "form_10_diff",
    "form_20_diff",
    "home_strength",
    "away_strength",
    "h2h_home_win_rate",
    "squad_value_diff",
    "avg_age_diff",
    "injuries_diff",
    "suspensions_diff",
    "rest_days_diff",
    "travel_distance_km",
    "motivation_score_diff",
]


@dataclass
class TeamMatchInputs:
    fifa_rank: float
    elo_rating: float
    spi_rating: float
    xg: float
    xga: float
    shots: float
    shots_on_target: float
    possession: float
    pass_accuracy: float
    ppda: float
    form_5: float
    form_10: float
    form_20: float
    home_advantage: float
    h2h_win_rate: float
    squad_value_m: float
    avg_age: float
    injuries: int
    suspensions: int
    rest_days: int
    motivation_score: float


def build_feature_row(home: TeamMatchInputs, away: TeamMatchInputs, travel_distance_km: float = 0.0) -> dict:
    return {
        "fifa_rank_diff": away.fifa_rank - home.fifa_rank,  # lower rank number = stronger
        "elo_diff": home.elo_rating - away.elo_rating,
        "spi_diff": home.spi_rating - away.spi_rating,
        "xg_diff": home.xg - away.xg,
        "xga_diff": away.xga - home.xga,
        "shots_diff": home.shots - away.shots,
        "shots_on_target_diff": home.shots_on_target - away.shots_on_target,
        "possession_diff": home.possession - away.possession,
        "pass_accuracy_diff": home.pass_accuracy - away.pass_accuracy,
        "ppda_diff": away.ppda - home.ppda,  # lower PPDA = more intense pressing
        "form_5_diff": home.form_5 - away.form_5,
        "form_10_diff": home.form_10 - away.form_10,
        "form_20_diff": home.form_20 - away.form_20,
        "home_strength": home.home_advantage,
        "away_strength": away.home_advantage,
        "h2h_home_win_rate": home.h2h_win_rate,
        "squad_value_diff": home.squad_value_m - away.squad_value_m,
        "avg_age_diff": home.avg_age - away.avg_age,
        "injuries_diff": away.injuries - home.injuries,
        "suspensions_diff": away.suspensions - home.suspensions,
        "rest_days_diff": home.rest_days - away.rest_days,
        "travel_distance_km": travel_distance_km,
        "motivation_score_diff": home.motivation_score - away.motivation_score,
    }


def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=FEATURE_COLUMNS)
    return df.fillna(0.0)
