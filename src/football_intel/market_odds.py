
"""Retrieve and analyze real Premier League market odds."""

from datetime import datetime, timezone
from statistics import mean
import json
import math
import os

from dotenv import load_dotenv
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


ODDS_URL = (
    "https://api.the-odds-api.com/v4/"
    "sports/soccer_epl/odds"
)


def remove_margin(decimal_odds: dict) -> dict:
    """Convert decimal odds into normalized probabilities."""

    if len(decimal_odds) != 3 or any(
        not math.isfinite(float(price)) or float(price) <= 1
        for price in decimal_odds.values()
    ):
        raise ValueError("Three valid decimal odds are required")

    implied = {
        outcome: 1 / float(price)
        for outcome, price in decimal_odds.items()
    }

    total = sum(implied.values())

    return {
        outcome: probability / total
        for outcome, probability in implied.items()
    }


def _parse_utc(value: object) -> datetime | None:
    """Parse a timezone-aware provider timestamp, without guessing its zone."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def analyze_event(event: dict) -> dict | None:
    """Calculate the market consensus for one fixture."""

    if not isinstance(event, dict):
        return None

    event_id = event.get("id")
    home = event.get("home_team")
    away = event.get("away_team")
    kickoff = _parse_utc(event.get("commence_time"))

    if not (
        isinstance(event_id, str) and event_id.strip()
        and isinstance(home, str) and home.strip()
        and isinstance(away, str) and away.strip()
        and home != away and kickoff is not None
    ):
        return None

    bookmakers = event.get("bookmakers")
    if not isinstance(bookmakers, list):
        return None

    estimates = []
    updates = []
    seen_bookmakers = set()

    for bookmaker in bookmakers:
        if not isinstance(bookmaker, dict):
            continue

        bookmaker_id = bookmaker.get("key") or bookmaker.get("title")
        if not isinstance(bookmaker_id, str) or not bookmaker_id.strip():
            continue
        if bookmaker_id in seen_bookmakers:
            continue

        markets = bookmaker.get("markets")
        if not isinstance(markets, list):
            continue

        for market in markets:
            if not isinstance(market, dict) or market.get("key") != "h2h":
                continue
            outcomes = market.get("outcomes")
            if not isinstance(outcomes, list):
                continue

            prices = {}
            for outcome in outcomes:
                if not isinstance(outcome, dict):
                    continue
                name = outcome.get("name")
                if not isinstance(name, str):
                    continue

                if name == home:
                    prices["home_win"] = outcome.get("price")
                elif name == away:
                    prices["away_win"] = outcome.get("price")
                elif name.casefold() == "draw":
                    prices["draw"] = outcome.get("price")

            if len(prices) == 3:
                try:
                    estimate = remove_margin(prices)
                except (ValueError, TypeError, OverflowError):
                    continue

                seen_bookmakers.add(bookmaker_id)
                estimates.append(estimate)
                updated = _parse_utc(
                    market.get("last_update") or bookmaker.get("last_update")
                )
                if updated is not None:
                    updates.append(updated)
                break

    if not estimates:
        return None

    probabilities = {
        outcome: round(
            mean(estimate[outcome] for estimate in estimates),
            4,
        )
        for outcome in ("home_win", "draw", "away_win")
    }

    return {
        "event_id": event_id,
        "home_team": home,
        "away_team": away,
        "kickoff": event["commence_time"],
        "bookmakers_compared": len(estimates),
        "latest_odds_update": (
            max(updates).isoformat().replace("+00:00", "Z") if updates else None
        ),
        "market_probabilities": probabilities,
    }


def fetch_premier_league_odds() -> list:
    """Fetch current odds for upcoming Premier League matches."""

    load_dotenv()

    api_key = os.getenv("ODDS_API_KEY")

    if not api_key:
        raise ValueError("ODDS_API_KEY is missing from .env")

    parameters = urlencode({
        "apiKey": api_key,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal",
    })

    url = f"{ODDS_URL}?{parameters}"

    try:
        with urlopen(url, timeout=15) as response:
            events = json.load(response)
    except HTTPError as exc:
        raise RuntimeError(
            f"Odds provider returned HTTP {exc.code}"
        ) from None
    except URLError:
        raise RuntimeError(
            "Cannot connect to the odds provider"
        ) from None
    except (ValueError, UnicodeError):
        raise RuntimeError("Odds provider returned invalid JSON") from None

    if not isinstance(events, list):
        raise RuntimeError("Odds provider returned an unexpected response")

    now = datetime.now(timezone.utc)
    results = []
    seen_events = set()

    for event in events:
        analysis = analyze_event(event)
        if analysis is None:
            continue

        kickoff = _parse_utc(analysis["kickoff"])
        if kickoff is None or kickoff <= now:
            continue

        event_id = analysis["event_id"]
        if event_id in seen_events:
            continue

        seen_events.add(event_id)
        results.append(analysis)

    return sorted(results, key=lambda fixture: fixture["kickoff"])


if __name__ == "__main__":
    results = fetch_premier_league_odds()

    if results:
        print(json.dumps(results[:5], indent=2))
    else:
        print("No upcoming matches with complete 1X2 odds found.")
