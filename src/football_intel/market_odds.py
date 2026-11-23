
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


def analyze_event(event: dict) -> dict | None:
    """Calculate the market consensus for one fixture."""

    home = event["home_team"]
    away = event["away_team"]

    estimates = []
    updates = []

    for bookmaker in event.get("bookmakers", []):
        for market in bookmaker.get("markets", []):
            if market.get("key") != "h2h":
                continue

            prices = {}

            for outcome in market.get("outcomes", []):
                name = outcome["name"]

                if name == home:
                    prices["home_win"] = outcome["price"]
                elif name == away:
                    prices["away_win"] = outcome["price"]
                elif name.casefold() == "draw":
                    prices["draw"] = outcome["price"]

            if len(prices) == 3:
                try:
                    estimates.append(remove_margin(prices))
                except (ValueError, TypeError, OverflowError):
                    continue

                updated = (
                    market.get("last_update")
                    or bookmaker.get("last_update")
                )

                if updated:
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
        "event_id": event["id"],
        "home_team": home,
        "away_team": away,
        "kickoff": event["commence_time"],
        "bookmakers_compared": len(estimates),
        "latest_odds_update": max(updates) if updates else None,
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

    if not isinstance(events, list):
        raise ValueError("Unexpected odds response format")

    now = datetime.now(timezone.utc)
    results = []

    for event in events:
        kickoff = datetime.fromisoformat(
            event["commence_time"].replace("Z", "+00:00")
        )

        if kickoff <= now:
            continue

        analysis = analyze_event(event)

        if analysis:
            results.append(analysis)

    return results


if __name__ == "__main__":
    results = fetch_premier_league_odds()

    if results:
        print(json.dumps(results[:5], indent=2))
    else:
        print("No upcoming matches with complete 1X2 odds found.")
