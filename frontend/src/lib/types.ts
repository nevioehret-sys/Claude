export interface ExactScore {
  home: number;
  away: number;
  probability: number;
}

export interface Recommendation {
  market: string;
  probability: number;
  fair_odds: number;
  market_odds: number;
  edge_pct: number;
  expected_value: number;
  kelly_stake_pct: number;
  confidence_score: number;
  value_class: string;
}

export interface Recommendations {
  recommended_tip: Recommendation | null;
  top_3: Recommendation[];
  safest_tip: Recommendation | null;
  best_value_bet: Recommendation | null;
  best_underdog: Recommendation | null;
  best_combination: {
    legs: string[];
    combined_probability: number;
    combined_odds: number;
    expected_value: number;
  } | null;
  not_recommended: Recommendation[];
  message: string | null;
}

export interface PredictionResponse {
  home_team: string;
  away_team: string;
  home_win_pct: number;
  draw_pct: number;
  away_win_pct: number;
  expected_goals_home: number;
  expected_goals_away: number;
  btts_pct: number;
  over_under: Record<string, { over: number; under: number }>;
  top_exact_scores: ExactScore[];
  most_likely_total_goals: number;
  confidence_score: number;
  monte_carlo: Record<string, unknown>;
  recommendations: Recommendations;
}
