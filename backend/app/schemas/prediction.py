from __future__ import annotations

from pydantic import BaseModel, Field


class TeamStrengthInput(BaseModel):
    attack: float = Field(..., gt=0, description="Attack rating relative to league average (1.0 = average)")
    defence: float = Field(..., gt=0, description="Defence rating relative to league average (1.0 = average)")
    elo_rating: float = Field(..., gt=0)


class MotivationInput(BaseModel):
    must_win: bool = False
    already_qualified: bool = False
    nothing_to_play_for: bool = False
    rivalry_factor: float = 0.0


class FatigueInput(BaseModel):
    rest_days: int = 5
    travel_distance_km: float = 0.0
    altitude_change_m: float = 0.0
    extra_time_last_match: bool = False


class SquadInput(BaseModel):
    key_players_injured: int = 0
    key_players_suspended: int = 0
    avg_squad_age: float = 27.0
    squad_market_value_eur_m: float = 0.0


class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    home_strength: TeamStrengthInput
    away_strength: TeamStrengthInput
    home_motivation: MotivationInput = MotivationInput()
    away_motivation: MotivationInput = MotivationInput()
    home_fatigue: FatigueInput = FatigueInput()
    away_fatigue: FatigueInput = FatigueInput()
    home_squad: SquadInput = SquadInput()
    away_squad: SquadInput = SquadInput()
    neutral_venue: bool = True
    stage: str = "group_stage"
    market_odds: dict[str, float] = Field(default_factory=dict)
    n_simulations: int = 100_000


class ExactScore(BaseModel):
    home: int
    away: int
    probability: float


class PredictionResponse(BaseModel):
    home_team: str
    away_team: str
    home_win_pct: float
    draw_pct: float
    away_win_pct: float
    expected_goals_home: float
    expected_goals_away: float
    btts_pct: float
    over_under: dict[str, dict[str, float]]
    top_exact_scores: list[ExactScore]
    most_likely_total_goals: int
    confidence_score: int
    monte_carlo: dict
    recommendations: dict
