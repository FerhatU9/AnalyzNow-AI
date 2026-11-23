
CREATE TABLE IF NOT EXISTS teams (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS matches (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    match_date DATE NOT NULL,

    home_team_id BIGINT NOT NULL
        REFERENCES teams(id),

    away_team_id BIGINT NOT NULL
        REFERENCES teams(id),

    home_goals INTEGER NOT NULL
        CHECK (home_goals >= 0),

    away_goals INTEGER NOT NULL
        CHECK (away_goals >= 0),

    CONSTRAINT different_teams
        CHECK (home_team_id <> away_team_id),

    CONSTRAINT unique_match
        UNIQUE (match_date, home_team_id, away_team_id)
);

CREATE INDEX IF NOT EXISTS idx_matches_date
ON matches (match_date);
