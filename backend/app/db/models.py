from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fifa_code: Mapped[str] = mapped_column(String(3), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    confederation: Mapped[str] = mapped_column(String(20))
    fifa_rank: Mapped[int | None] = mapped_column(Integer)
    elo_rating: Mapped[float] = mapped_column(Numeric(7, 2), default=1500)
    spi_rating: Mapped[float | None] = mapped_column(Numeric(7, 2))
    squad_market_value_eur_m: Mapped[float | None] = mapped_column(Numeric(10, 2))
    avg_squad_age: Mapped[float | None] = mapped_column(Numeric(4, 1))
    head_coach: Mapped[str | None] = mapped_column(String(100))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Tournament(Base):
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column(Integer)
    host_country: Mapped[str | None] = mapped_column(String(50))
    start_date: Mapped[Date | None] = mapped_column(Date)
    end_date: Mapped[Date | None] = mapped_column(Date)


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id"))
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    stage: Mapped[str] = mapped_column(String(30))
    kickoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    venue: Mapped[str | None] = mapped_column(String(100))
    neutral_venue: Mapped[bool] = mapped_column(Boolean, default=True)
    weather_temp_c: Mapped[float | None] = mapped_column(Numeric(4, 1))
    weather_condition: Mapped[str | None] = mapped_column(String(30))
    altitude_m: Mapped[int | None] = mapped_column(Integer)
    home_goals: Mapped[int | None] = mapped_column(Integer)
    away_goals: Mapped[int | None] = mapped_column(Integer)
    home_goals_et: Mapped[int | None] = mapped_column(Integer)
    away_goals_et: Mapped[int | None] = mapped_column(Integer)
    penalty_winner_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    status: Mapped[str] = mapped_column(String(20), default="scheduled")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    model_version: Mapped[str] = mapped_column(String(30))
    home_win_prob: Mapped[float] = mapped_column(Numeric(6, 5))
    draw_prob: Mapped[float] = mapped_column(Numeric(6, 5))
    away_win_prob: Mapped[float] = mapped_column(Numeric(6, 5))
    expected_goals_home: Mapped[float] = mapped_column(Numeric(5, 2))
    expected_goals_away: Mapped[float] = mapped_column(Numeric(5, 2))
    btts_prob: Mapped[float] = mapped_column(Numeric(6, 5))
    most_likely_total_goals: Mapped[int] = mapped_column(Integer)
    confidence_score: Mapped[int] = mapped_column(Integer)
    score_matrix_json: Mapped[dict | None] = mapped_column(JSONB)
    monte_carlo_json: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MarketOdds(Base):
    __tablename__ = "market_odds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"))
    bookmaker: Mapped[str | None] = mapped_column(String(50))
    market: Mapped[str] = mapped_column(String(30))
    odds: Mapped[float] = mapped_column(Numeric(7, 3))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ValueBetRecord(Base):
    __tablename__ = "value_bets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prediction_id: Mapped[int] = mapped_column(ForeignKey("predictions.id"))
    market: Mapped[str] = mapped_column(String(30))
    probability: Mapped[float] = mapped_column(Numeric(6, 5))
    fair_odds: Mapped[float] = mapped_column(Numeric(7, 3))
    market_odds: Mapped[float] = mapped_column(Numeric(7, 3))
    edge_pct: Mapped[float] = mapped_column(Numeric(6, 2))
    expected_value: Mapped[float] = mapped_column(Numeric(6, 4))
    kelly_stake_pct: Mapped[float] = mapped_column(Numeric(6, 2))
    value_class: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
