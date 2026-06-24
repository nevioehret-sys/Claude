"use client";

import { useState } from "react";
import { PredictionResponse } from "@/lib/types";
import RecommendationCard from "@/components/RecommendationCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [homeTeam, setHomeTeam] = useState("Deutschland");
  const [awayTeam, setAwayTeam] = useState("Brasilien");
  const [homeOdds, setHomeOdds] = useState(2.8);
  const [drawOdds, setDrawOdds] = useState(3.3);
  const [awayOdds, setAwayOdds] = useState(2.5);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runPrediction() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/api/predictions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          home_team: homeTeam,
          away_team: awayTeam,
          home_strength: { attack: 1.25, defence: 0.95, elo_rating: 2050 },
          away_strength: { attack: 1.3, defence: 0.9, elo_rating: 2120 },
          market_odds: {
            home_win: homeOdds,
            draw: drawOdds,
            away_win: awayOdds,
          },
          n_simulations: 50000,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unbekannter Fehler");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>WM Prognose Engine</h1>
      <p>KI-gestützte Wahrscheinlichkeiten, Value Bets und Monte-Carlo-Simulation für die FIFA WM.</p>

      <div className="card">
        <div className="grid">
          <div>
            <div className="label">Heimteam</div>
            <input value={homeTeam} onChange={(e) => setHomeTeam(e.target.value)} />
          </div>
          <div>
            <div className="label">Auswärtsteam</div>
            <input value={awayTeam} onChange={(e) => setAwayTeam(e.target.value)} />
          </div>
          <div>
            <div className="label">Quote Heimsieg</div>
            <input type="number" step="0.01" value={homeOdds} onChange={(e) => setHomeOdds(parseFloat(e.target.value))} />
          </div>
          <div>
            <div className="label">Quote Unentschieden</div>
            <input type="number" step="0.01" value={drawOdds} onChange={(e) => setDrawOdds(parseFloat(e.target.value))} />
          </div>
          <div>
            <div className="label">Quote Auswärtssieg</div>
            <input type="number" step="0.01" value={awayOdds} onChange={(e) => setAwayOdds(parseFloat(e.target.value))} />
          </div>
        </div>
        <br />
        <button onClick={runPrediction} disabled={loading}>
          {loading ? "Berechne..." : "Prognose berechnen"}
        </button>
        {error && <p style={{ color: "#e05656" }}>{error}</p>}
      </div>

      {result && (
        <>
          <div className="card">
            <div className="grid">
              <div>
                <div className="label">Heimsieg</div>
                <div className="value">{(result.home_win_pct * 100).toFixed(1)}%</div>
              </div>
              <div>
                <div className="label">Unentschieden</div>
                <div className="value">{(result.draw_pct * 100).toFixed(1)}%</div>
              </div>
              <div>
                <div className="label">Auswärtssieg</div>
                <div className="value">{(result.away_win_pct * 100).toFixed(1)}%</div>
              </div>
            </div>
            <p>
              Erwartete Tore: {result.home_team} {result.expected_goals_home} – {result.expected_goals_away}{" "}
              {result.away_team} · BTTS: {(result.btts_pct * 100).toFixed(1)}% · Konfidenz:{" "}
              {result.confidence_score}/100
            </p>
          </div>

          {result.recommendations.message ? (
            <div className="card">
              <strong>{result.recommendations.message}</strong>
            </div>
          ) : (
            <>
              <RecommendationCard title="EMPFOHLENER TIPP" rec={result.recommendations.recommended_tip} />
              <RecommendationCard title="SICHERSTER TIPP" rec={result.recommendations.safest_tip} />
              <RecommendationCard title="BESTE VALUE BET" rec={result.recommendations.best_value_bet} />
              <RecommendationCard title="BESTER AUSSENSEITER" rec={result.recommendations.best_underdog} />
            </>
          )}
        </>
      )}
    </main>
  );
}
