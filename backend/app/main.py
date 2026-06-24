from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.backtest import router as backtest_router
from app.api.predictions import router as predictions_router

app = FastAPI(
    title="WM Prognose Engine",
    description="KI-gestützte Fußball-Prognose-API: Ensemble-Modell, Value Bets, Monte-Carlo-Simulation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predictions_router)
app.include_router(backtest_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
