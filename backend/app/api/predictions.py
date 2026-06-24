from __future__ import annotations

from fastapi import APIRouter

from app.core.ensemble import EnsembleConfig, TeamStrength, confidence_score, ensemble_match_probabilities
from app.core.monte_carlo import simulate_match
from app.core.poisson import (
    btts_probability,
    over_under_probabilities,
    score_matrix as build_score_matrix,
    top_correct_scores,
    most_likely_total_goals,
)
from app.core.recommendation import build_recommendations
from app.core.worldcup_context import (
    FatigueContext,
    MotivationContext,
    SquadContext,
    apply_context_adjustments,
)
from app.schemas.prediction import PredictionRequest, PredictionResponse

router = APIRouter(prefix="/api/predictions", tags=["predictions"])

OU_LINES = [0.5, 1.5, 2.5, 3.5, 4.5]


@router.post("", response_model=PredictionResponse)
def predict_match(payload: PredictionRequest) -> PredictionResponse:
    home_attack, home_defence = apply_context_adjustments(
        payload.home_strength.attack,
        payload.home_strength.defence,
        MotivationContext(**payload.home_motivation.model_dump()),
        FatigueContext(**payload.home_fatigue.model_dump()),
        SquadContext(
            key_players_injured=payload.home_squad.key_players_injured,
            key_players_suspended=payload.home_squad.key_players_suspended,
            avg_squad_age=payload.home_squad.avg_squad_age,
            squad_market_value_eur_m=payload.home_squad.squad_market_value_eur_m,
        ),
    )
    away_attack, away_defence = apply_context_adjustments(
        payload.away_strength.attack,
        payload.away_strength.defence,
        MotivationContext(**payload.away_motivation.model_dump()),
        FatigueContext(**payload.away_fatigue.model_dump()),
        SquadContext(
            key_players_injured=payload.away_squad.key_players_injured,
            key_players_suspended=payload.away_squad.key_players_suspended,
            avg_squad_age=payload.away_squad.avg_squad_age,
            squad_market_value_eur_m=payload.away_squad.squad_market_value_eur_m,
        ),
    )

    home = TeamStrength(attack=home_attack, defence=home_defence, elo_rating=payload.home_strength.elo_rating)
    away = TeamStrength(attack=away_attack, defence=away_defence, elo_rating=payload.away_strength.elo_rating)

    config = EnsembleConfig(neutral_venue=payload.neutral_venue)
    result = ensemble_match_probabilities(home, away, config)

    matrix = result["score_matrix"]
    probs = result["probabilities"]
    conf = confidence_score(probs, result["model_breakdown"])

    mc = simulate_match(matrix, n_simulations=payload.n_simulations)

    market_probs = {
        "home_win": probs["home_win"],
        "draw": probs["draw"],
        "away_win": probs["away_win"],
        "btts_yes": btts_probability(matrix),
    }
    ou = over_under_probabilities(matrix, OU_LINES)
    for line, p in ou.items():
        market_probs[f"over_{line}"] = p["over"]
        market_probs[f"under_{line}"] = p["under"]

    recommendations = build_recommendations(market_probs, payload.market_odds, conf)

    return PredictionResponse(
        home_team=payload.home_team,
        away_team=payload.away_team,
        home_win_pct=round(probs["home_win"], 4),
        draw_pct=round(probs["draw"], 4),
        away_win_pct=round(probs["away_win"], 4),
        expected_goals_home=round(result["lambda_home"], 3),
        expected_goals_away=round(result["lambda_away"], 3),
        btts_pct=round(market_probs["btts_yes"], 4),
        over_under=ou,
        top_exact_scores=top_correct_scores(matrix, top_n=10),
        most_likely_total_goals=most_likely_total_goals(matrix),
        confidence_score=conf,
        monte_carlo=mc,
        recommendations=recommendations,
    )
