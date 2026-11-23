"""Strict, local-only fixture ingestion. No automatic scraping or licensed data bundling."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class Match:
    date: date
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int

    @property
    def outcome(self) -> str:
        return "H" if self.home_goals > self.away_goals else ("A" if self.home_goals < self.away_goals else "D")


def parse_date(raw: str) -> date:
    value = raw.strip().split("T", 1)[0]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Invalid match date {raw!r}. Expected ISO or day/month/year.")


def load_matches(path: str | Path) -> list[Match]:
    """Read Date, HomeTeam, AwayTeam, FTHG, FTAG (or normalized field names).

    A blank goal denotes an unplayed fixture and is skipped; malformed completed
    scores, dates, names and duplicates are rejected rather than silently repaired.
    """
    matches: list[Match] = []
    seen: set[tuple[date, str, str]] = set()
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header")
        key_map = {
            "date": "date", "hometeam": "home_team", "awayteam": "away_team",
            "fthg": "home_goals", "ftag": "away_goals",
            "home_team": "home_team", "away_team": "away_team",
            "home_goals": "home_goals", "away_goals": "away_goals",
        }
        mapped = {key_map[k.strip().lower()]: k for k in reader.fieldnames if k.strip().lower() in key_map}
        required = {"date", "home_team", "away_team", "home_goals", "away_goals"}
        if not required.issubset(mapped):
            raise ValueError(f"CSV missing columns: {', '.join(sorted(required - set(mapped)))}")
        for line, row in enumerate(reader, start=2):
            if all(not str(value or "").strip() for value in row.values()):
                continue
            goals_raw = [str(row[mapped[k]] or "").strip() for k in ("home_goals", "away_goals")]
            if goals_raw == ["", ""]:  # a genuine future fixture
                continue
            if "" in goals_raw:
                raise ValueError(f"CSV line {line}: incomplete final score")
            try:
                goals = [int(value) for value in goals_raw]
                if min(goals) < 0:
                    raise ValueError("negative goals")
                day = parse_date(str(row[mapped["date"]] or ""))
                home = str(row[mapped["home_team"]] or "").strip()
                away = str(row[mapped["away_team"]] or "").strip()
                if not home or not away or home.casefold() == away.casefold():
                    raise ValueError("missing or equal team names")
            except (ValueError, TypeError) as exc:
                raise ValueError(f"CSV line {line}: invalid match: {exc}") from exc
            signature = (day, home.casefold(), away.casefold())
            if signature in seen:
                raise ValueError(f"CSV line {line}: duplicate match {signature}")
            seen.add(signature)
            matches.append(Match(day, home, away, goals[0], goals[1]))
    return sorted(matches, key=lambda match: (match.date, match.home_team, match.away_team))


def teams_in(matches: list[Match]) -> list[str]:
    return sorted({m.home_team for m in matches} | {m.away_team for m in matches})
