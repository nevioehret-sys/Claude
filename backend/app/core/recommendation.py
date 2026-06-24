"""Recommendation engine: turns model probabilities + market odds into ranked,
actionable betting recommendations.

Pipeline per match:
1. Ensemble probabilities (already computed upstream).
2. Value bet scan across all offered markets.
3. Sort by Expected Value.
4. Attach confidence score.
5. Produce structured output: top tip, top 3, safest, best value, best underdog,
   best combination, and a "not recommended" list.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.core.value_bet import ValueBetResult, ValueClass, scan_markets

MIN_CONFIDENCE_FOR_TOP_PICK = 55
SAFE_BET_MIN_PROBABILITY = 0.60
UNDERDOG_MAX_PROBABILITY = 0.35


@dataclass
class Recommendation:
    market: str
    probability: float
    fair_odds: float
    market_odds: float
    edge_pct: float
    expected_value: float
    kelly_stake_pct: float
    confidence_score: int
    value_class: ValueClass


def _to_recommendation(v: ValueBetResult, confidence: int) -> Recommendation:
    return Recommendation(
        market=v.market,
        probability=round(v.probability, 4),
        fair_odds=v.fair_odds,
        market_odds=v.market_odds,
        edge_pct=v.edge_pct,
        expected_value=v.expected_value,
        kelly_stake_pct=v.kelly_stake_pct,
        confidence_score=confidence,
        value_class=v.value_class,
    )


def build_recommendations(
    probabilities: dict[str, float],
    market_odds: dict[str, float],
    confidence_score: int,
    kelly_multiplier: float = 0.25,
) -> dict:
    value_bets = scan_markets(probabilities, market_odds, kelly_multiplier)
    positive_ev = [v for v in value_bets if v.expected_value > 0]

    if not positive_ev:
        return {
            "recommended_tip": None,
            "top_3": [],
            "safest_tip": None,
            "best_value_bet": None,
            "best_underdog": None,
            "best_combination": None,
            "not_recommended": [_to_recommendation(v, confidence_score) for v in value_bets],
            "message": "KEINE WETTE EMPFOHLEN",
        }

    recommended = _to_recommendation(positive_ev[0], confidence_score)
    top_3 = [_to_recommendation(v, confidence_score) for v in positive_ev[:3]]

    safest_candidates = [v for v in positive_ev if v.probability >= SAFE_BET_MIN_PROBABILITY]
    safest = (
        _to_recommendation(max(safest_candidates, key=lambda v: v.probability), confidence_score)
        if safest_candidates
        else None
    )

    best_value = _to_recommendation(
        max(positive_ev, key=lambda v: v.edge_pct), confidence_score
    )

    underdog_candidates = [v for v in positive_ev if v.probability <= UNDERDOG_MAX_PROBABILITY]
    best_underdog = (
        _to_recommendation(max(underdog_candidates, key=lambda v: v.expected_value), confidence_score)
        if underdog_candidates
        else None
    )

    best_combination = None
    if len(positive_ev) >= 2:
        a, b = positive_ev[0], positive_ev[1]
        combined_prob = a.probability * b.probability
        combined_odds = a.market_odds * b.market_odds
        best_combination = {
            "legs": [a.market, b.market],
            "combined_probability": round(combined_prob, 4),
            "combined_odds": round(combined_odds, 2),
            "expected_value": round(combined_prob * combined_odds - 1, 4),
        }

    not_recommended = [_to_recommendation(v, confidence_score) for v in value_bets if v.expected_value <= 0]

    return {
        "recommended_tip": recommended,
        "top_3": top_3,
        "safest_tip": safest,
        "best_value_bet": best_value,
        "best_underdog": best_underdog,
        "best_combination": best_combination,
        "not_recommended": not_recommended,
        "message": None,
    }
