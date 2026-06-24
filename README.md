# WM Prognose Engine

KI-gestützte Fußball-Prognose-App für die FIFA-WM: eigenständige
Wahrscheinlichkeitsberechnung, Value-Bet-Erkennung und kalibrierte Prognosen.

## Komponenten

- **backend/** — FastAPI-Service mit dem Prognose-Ensemble (Poisson/Dixon-Coles,
  Elo, XGBoost/LightGBM/CatBoost/Random Forest), Kalibrierung, Monte-Carlo-
  Simulation, Value-Bet- und Empfehlungs-Engine, sowie Backtesting-Endpunkt.
- **frontend/** — Next.js/React/TypeScript-UI zur Eingabe von Spieldaten und
  Anzeige der Prognosen und Tipp-Empfehlungen.
- **docker-compose.yml** — orchestriert PostgreSQL, Backend und Frontend.
- **ARCHITECTURE.md** — Architektur-/Datenflussdiagramme und alle Formeln.

## Schnellstart (lokal ohne Docker)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
cd frontend
npm install
npm run dev
```

## Schnellstart (Docker)

```bash
docker compose up --build
```

Backend: http://localhost:8000/docs · Frontend: http://localhost:3000

## API-Beispiel

```bash
curl -X POST http://localhost:8000/api/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "home_team": "Deutschland",
    "away_team": "Brasilien",
    "home_strength": {"attack": 1.25, "defence": 0.95, "elo_rating": 2050},
    "away_strength": {"attack": 1.30, "defence": 0.90, "elo_rating": 2120},
    "market_odds": {"home_win": 2.8, "draw": 3.3, "away_win": 2.5},
    "n_simulations": 50000
  }'
```

## Status

Poisson/Dixon-Coles, Elo, Kalibrierung, Monte-Carlo, Value-Bet- und
Empfehlungs-Engine sind vollständig implementiert und getestet. Die
Gradient-Boosting-Modelle (XGBoost/LightGBM/CatBoost/Random Forest) sind als
Trainings-Pipeline angelegt (`backend/app/ml/train.py`), benötigen aber echte
historische WM-Trainingsdaten, die nicht Teil dieses Repos sind — siehe
ARCHITECTURE.md Abschnitt 4.
