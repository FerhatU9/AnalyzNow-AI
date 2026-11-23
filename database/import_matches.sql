
BEGIN;

CREATE TEMP TABLE imported_matches (
    match_date TEXT,
    home_team TEXT,
    away_team TEXT,
    home_goals TEXT,
    away_goals TEXT
);

\copy imported_matches FROM '/tmp/epl_matches.csv' WITH (FORMAT csv, HEADER true)

INSERT INTO teams (name)
SELECT DISTINCT TRIM(team_name)
FROM (
    SELECT home_team AS team_name FROM imported_matches
    UNION ALL
    SELECT away_team FROM imported_matches
) AS names
ON CONFLICT (name) DO NOTHING;

INSERT INTO matches (
    match_date,
    home_team_id,
    away_team_id,
    home_goals,
    away_goals
)
SELECT
    r.match_date::DATE,
    home.id,
    away.id,
    r.home_goals::INTEGER,
    r.away_goals::INTEGER
FROM imported_matches r
JOIN teams home ON home.name = TRIM(r.home_team)
JOIN teams away ON away.name = TRIM(r.away_team)
ON CONFLICT (match_date, home_team_id, away_team_id)
DO UPDATE SET
    home_goals = EXCLUDED.home_goals,
    away_goals = EXCLUDED.away_goals;

COMMIT;
