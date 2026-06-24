from __future__ import annotations

import numpy as np
from fastapi import APIRouter
from pydantic import BaseModel

from app.core.backtesting import run_backtest_report

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


class BacktestMatchResult(BaseModel):
    predicted_prob: float
    outcome: int  # 1 if predicted class happened, else 0
    predicted_top_outcome: str
    actual_outcome: str
    stake: float
    returned: float


class BacktestRequest(BaseModel):
    tournament: str
    results: list[BacktestMatchResult]


@router.post("")
def run_backtest(payload: BacktestRequest) -> dict:
    predicted_probs = np.array([r.predicted_prob for r in payload.results])
    outcomes = np.array([r.outcome for r in payload.results])
    predicted_top = [r.predicted_top_outcome for r in payload.results]
    actual = [r.actual_outcome for r in payload.results]
    stakes = np.array([r.stake for r in payload.results])
    returns = np.array([r.returned for r in payload.results])

    report = run_backtest_report(predicted_probs, outcomes, predicted_top, actual, stakes, returns)
    return {"tournament": payload.tournament, "n_matches": len(payload.results), **report}
