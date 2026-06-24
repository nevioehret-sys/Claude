-- World Cup Prediction Platform - PostgreSQL schema

CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    fifa_code VARCHAR(3) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    confederation VARCHAR(20) NOT NULL,
    fifa_rank INT,
    elo_rating NUMERIC(7,2) DEFAULT 1500,
    spi_rating NUMERIC(7,2),
    squad_market_value_eur_m NUMERIC(10,2),
    avg_squad_age NUMERIC(4,1),
    head_coach VARCHAR(100),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tournaments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    host_country VARCHAR(50),
    start_date DATE,
    end_date DATE
);

CREATE TABLE tournament_teams (
    tournament_id INT REFERENCES tournaments(id),
    team_id INT REFERENCES teams(id),
    group_name VARCHAR(2),
    already_qualified_knockout BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (tournament_id, team_id)
);

CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    tournament_id INT REFERENCES tournaments(id),
    home_team_id INT REFERENCES teams(id),
    away_team_id INT REFERENCES teams(id),
    stage VARCHAR(30) NOT NULL,
    kickoff_at TIMESTAMPTZ NOT NULL,
    venue VARCHAR(100),
    neutral_venue BOOLEAN DEFAULT TRUE,
    weather_temp_c NUMERIC(4,1),
    weather_condition VARCHAR(30),
    altitude_m INT,
    home_goals INT,
    away_goals INT,
    home_goals_et INT,
    away_goals_et INT,
    penalty_winner_team_id INT REFERENCES teams(id),
    status VARCHAR(20) DEFAULT 'scheduled'
);

CREATE TABLE match_team_stats (
    match_id INT REFERENCES matches(id),
    team_id INT REFERENCES teams(id),
    xg NUMERIC(5,2),
    xga NUMERIC(5,2),
    shots INT,
    shots_on_target INT,
    possession_pct NUMERIC(5,2),
    pass_accuracy_pct NUMERIC(5,2),
    ppda NUMERIC(6,2),
    form_5 NUMERIC(4,2),
    form_10 NUMERIC(4,2),
    form_20 NUMERIC(4,2),
    rest_days INT,
    travel_distance_km NUMERIC(8,2),
    key_players_injured INT DEFAULT 0,
    key_players_suspended INT DEFAULT 0,
    must_win BOOLEAN DEFAULT FALSE,
    nothing_to_play_for BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (match_id, team_id)
);

CREATE TABLE head_to_head (
    team_a_id INT REFERENCES teams(id),
    team_b_id INT REFERENCES teams(id),
    match_id INT REFERENCES matches(id),
    PRIMARY KEY (team_a_id, team_b_id, match_id)
);

CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    match_id INT REFERENCES matches(id),
    model_version VARCHAR(30) NOT NULL,
    home_win_prob NUMERIC(6,5),
    draw_prob NUMERIC(6,5),
    away_win_prob NUMERIC(6,5),
    expected_goals_home NUMERIC(5,2),
    expected_goals_away NUMERIC(5,2),
    btts_prob NUMERIC(6,5),
    most_likely_total_goals INT,
    confidence_score INT,
    score_matrix_json JSONB,
    monte_carlo_json JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE market_odds (
    id SERIAL PRIMARY KEY,
    match_id INT REFERENCES matches(id),
    bookmaker VARCHAR(50),
    market VARCHAR(30) NOT NULL,
    odds NUMERIC(7,3) NOT NULL,
    captured_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE value_bets (
    id SERIAL PRIMARY KEY,
    prediction_id INT REFERENCES predictions(id),
    market VARCHAR(30) NOT NULL,
    probability NUMERIC(6,5),
    fair_odds NUMERIC(7,3),
    market_odds NUMERIC(7,3),
    edge_pct NUMERIC(6,2),
    expected_value NUMERIC(6,4),
    kelly_stake_pct NUMERIC(6,2),
    value_class VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE backtest_runs (
    id SERIAL PRIMARY KEY,
    tournament_id INT REFERENCES tournaments(id),
    model_version VARCHAR(30) NOT NULL,
    brier_score NUMERIC(6,5),
    log_loss NUMERIC(6,5),
    calibration_error NUMERIC(6,5),
    hit_rate NUMERIC(5,4),
    roi_pct NUMERIC(7,2),
    yield_pct NUMERIC(7,2),
    run_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_matches_tournament ON matches(tournament_id);
CREATE INDEX idx_predictions_match ON predictions(match_id);
CREATE INDEX idx_market_odds_match ON market_odds(match_id);
CREATE INDEX idx_value_bets_prediction ON value_bets(prediction_id);
