"""World-Cup-specific context adjustments applied on top of base ratings.

These are multiplicative/additive nudges to attack/defence/elo inputs that
capture tournament dynamics not present in club-football training data.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Stage(str, Enum):
    GROUP = "group_stage"
    ROUND_OF_16 = "round_of_16"
    QUARTER_FINAL = "quarter_final"
    SEMI_FINAL = "semi_final"
    FINAL = "final"


@dataclass
class MotivationContext:
    must_win: bool = False
    already_qualified: bool = False
    nothing_to_play_for: bool = False
    rivalry_factor: float = 0.0  # 0-1, derived from historical-rivalry intensity


@dataclass
class FatigueContext:
    rest_days: int = 5
    travel_distance_km: float = 0.0
    altitude_change_m: float = 0.0
    extra_time_last_match: bool = False


@dataclass
class SquadContext:
    key_players_injured: int = 0
    key_players_suspended: int = 0
    avg_squad_age: float = 27.0
    squad_market_value_eur_m: float = 0.0


def motivation_multiplier(ctx: MotivationContext) -> float:
    multiplier = 1.0
    if ctx.must_win:
        multiplier += 0.06
    if ctx.already_qualified:
        multiplier -= 0.10
    if ctx.nothing_to_play_for:
        multiplier -= 0.15
    multiplier += ctx.rivalry_factor * 0.03
    return max(0.7, multiplier)


def fatigue_multiplier(ctx: FatigueContext) -> float:
    multiplier = 1.0
    if ctx.rest_days < 3:
        multiplier -= 0.08
    elif ctx.rest_days >= 5:
        multiplier += 0.02

    if ctx.travel_distance_km > 5000:
        multiplier -= 0.04
    if ctx.altitude_change_m > 1500:
        multiplier -= 0.05
    if ctx.extra_time_last_match:
        multiplier -= 0.03
    return max(0.75, multiplier)


def squad_quality_multiplier(ctx: SquadContext) -> float:
    multiplier = 1.0
    multiplier -= 0.025 * ctx.key_players_injured
    multiplier -= 0.02 * ctx.key_players_suspended
    return max(0.6, multiplier)


def apply_context_adjustments(
    base_attack: float,
    base_defence: float,
    motivation: MotivationContext,
    fatigue: FatigueContext,
    squad: SquadContext,
) -> tuple[float, float]:
    attack_mult = motivation_multiplier(motivation) * fatigue_multiplier(fatigue) * squad_quality_multiplier(squad)
    defence_mult = 1 / (fatigue_multiplier(fatigue) * squad_quality_multiplier(squad))
    return base_attack * attack_mult, base_defence * defence_mult
