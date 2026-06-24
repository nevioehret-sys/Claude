"""Value bet detection: fair odds vs market odds, edge, EV, Kelly stake.

Value = (probability * market_odds) - 1
Fair odds = 1 / probability
Edge % = (probability - implied_probability) / implied_probability * 100
Kelly fraction f* = (b*p - q) / b, where b = market_odds - 1, q = 1 - p
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ValueClass(str, Enum):
    NONE = "Kein Value"
    LIGHT = "Leichter Value"
    GOOD = "Guter Value"
    STRONG = "Starker Value"


@dataclass
class ValueBetResult:
    market: str
    probability: float
    fair_odds: float
    market_odds: float
    implied_probability: float
    edge_pct: float
    expected_value: float
    kelly_fraction: float
    kelly_stake_pct: float
    value_class: ValueClass


def classify_value(ev: float, edge_pct: float) -> ValueClass:
    if ev <= 0:
        return ValueClass.NONE
    if edge_pct < 3:
        return ValueClass.LIGHT
    if edge_pct < 8:
        return ValueClass.GOOD
    return ValueClass.STRONG


def kelly_criterion(probability: float, market_odds: float, kelly_multiplier: float = 0.25) -> float:
    """Fractional Kelly (default quarter-Kelly for variance control)."""
    b = market_odds - 1
    q = 1 - probability
    if b <= 0:
        return 0.0
    f_star = (b * probability - q) / b
    return max(0.0, f_star * kelly_multiplier)


def evaluate_value_bet(market: str, probability: float, market_odds: float, kelly_multiplier: float = 0.25) -> ValueBetResult:
    probability = min(max(probability, 1e-6), 1 - 1e-6)
    fair_odds = 1 / probability
    implied_probability = 1 / market_odds
    edge_pct = (probability - implied_probability) / implied_probability * 100
    expected_value = probability * market_odds - 1
    kelly_fraction = kelly_criterion(probability, market_odds, kelly_multiplier)

    return ValueBetResult(
        market=market,
        probability=probability,
        fair_odds=round(fair_odds, 3),
        market_odds=market_odds,
        implied_probability=round(implied_probability, 4),
        edge_pct=round(edge_pct, 2),
        expected_value=round(expected_value, 4),
        kelly_fraction=round(kelly_fraction, 4),
        kelly_stake_pct=round(kelly_fraction * 100, 2),
        value_class=classify_value(expected_value, edge_pct),
    )


def scan_markets(probabilities: dict[str, float], market_odds: dict[str, float], kelly_multiplier: float = 0.25) -> list[ValueBetResult]:
    """probabilities and market_odds are keyed by the same market names, e.g. 'home_win', 'btts_yes', 'over_2.5'."""
    results = []
    for market, prob in probabilities.items():
        odds = market_odds.get(market)
        if odds is None:
            continue
        results.append(evaluate_value_bet(market, prob, odds, kelly_multiplier))
    results.sort(key=lambda r: r.expected_value, reverse=True)
    return results
