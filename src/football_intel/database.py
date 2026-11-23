
"""Read historical football matches from PostgreSQL."""

import os
from datetime import date

import psycopg
from dotenv import load_dotenv

from .data import Match


def load_matches_from_database(as_of: date) -> list[Match]:
    """Return matches played before the forecast date."""

    load_dotenv()

    password = os.getenv("POSTGRES_PASSWORD")

    if not password:
        raise ValueError("POSTGRES_PASSWORD is missing")

    with psycopg.connect(
        host="127.0.0.1",
        port=5433,
        dbname="analyznow",
        user="analyznow",
        password=password,
        connect_timeout=5,
    ) as connection:

        rows = connection.execute(
            """
            SELECT
                m.match_date,
                home.name,
                away.name,
                m.home_goals,
                m.away_goals
            FROM matches m
            JOIN teams home
                ON home.id = m.home_team_id
            JOIN teams away
                ON away.id = m.away_team_id
            WHERE m.match_date < %s
            ORDER BY m.match_date, home.name, away.name
            """,
            (as_of,),
        ).fetchall()

    return [
        Match(
            date=match_date,
            home_team=home,
            away_team=away,
            home_goals=home_goals,
            away_goals=away_goals,
        )
        for match_date, home, away, home_goals, away_goals in rows
    ]
