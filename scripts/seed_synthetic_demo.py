"""Seed the isolated Docker demo database with fictional football results.

Only runs when explicitly enabled, and refuses unexpected existing databases.
Never use this utility for a historical or production database.
"""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import psycopg

from football_intel.data import load_matches, teams_in


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "synthetic_demo.csv"
SCHEMA = ROOT / "database" / "schema.sql"


def main() -> None:
    if os.getenv("FOOTBALL_DEMO_SEED") != "1":
        raise SystemExit("Refusing to seed: FOOTBALL_DEMO_SEED must be 1")
    if os.getenv("POSTGRES_DB") != "analyznow_demo":
        raise SystemExit("Refusing to seed anything except analyznow_demo")

    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        raise SystemExit("POSTGRES_PASSWORD is required")

    matches = load_matches(CSV)
    team_names = teams_in(matches)

    with psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname="analyznow_demo",
        user=os.getenv("POSTGRES_USER", "analyznow_demo"),
        password=password,
        connect_timeout=10,
    ) as connection:
        for statement in SCHEMA.read_text(encoding="utf-8").split(";"):
            if statement.strip():
                connection.execute(statement)

        existing_teams = {
            row[0] for row in connection.execute("SELECT name FROM teams")
        }
        existing_match_count = connection.execute(
            "SELECT COUNT(*) FROM matches"
        ).fetchone()[0]
        if existing_match_count or existing_teams:
            if existing_teams == set(team_names) and existing_match_count == len(matches):
                print("Fictional demo dataset already present; no changes made.")
                return
            raise RuntimeError(
                "Refusing to overwrite unexpected database content. "
                "Stop and inspect the dedicated demo volume."
            )

        for name in team_names:
            connection.execute(
                "INSERT INTO teams (name) VALUES (%s) ON CONFLICT DO NOTHING",
                (name,),
            )

        team_ids = dict(connection.execute("SELECT name, id FROM teams").fetchall())
        connection.executemany(
            """
            INSERT INTO matches (
                match_date, home_team_id, away_team_id, home_goals, away_goals
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (match_date, home_team_id, away_team_id)
            DO NOTHING
            """,
            [
                (
                    match.date,
                    team_ids[match.home_team],
                    team_ids[match.away_team],
                    match.home_goals,
                    match.away_goals,
                )
                for match in matches
            ],
        )
        print(f"Seeded {len(matches)} fictional matches across {len(team_names)} demo clubs.")


if __name__ == "__main__":
    main()
