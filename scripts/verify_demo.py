"""Check the full synthetic-data demo over real local HTTP connections.

Run after FastAPI (9011) and Next.js (3011) have started. Uses stdlib only.
"""
from __future__ import annotations

import json
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_URL = "http://127.0.0.1:9011"
WEB_URL = "http://127.0.0.1:3011"


def request_json(url: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=body, headers=headers, method="POST" if body else "GET")
    with urlopen(request, timeout=8) as response:
        if response.status != 200:
            raise RuntimeError(f"Unexpected HTTP status {response.status}: {url}")
        result = json.load(response)
    if not isinstance(result, dict):
        raise RuntimeError(f"Unexpected response body: {url}")
    return result


def wait_for(url: str, seconds: int = 45) -> None:
    end_time = time.monotonic() + seconds
    last_error: Exception | None = None
    while time.monotonic() < end_time:
        try:
            request_json(url)
            return
        except (URLError, HTTPError, OSError, ValueError, RuntimeError) as exc:
            last_error = exc
            time.sleep(0.5)
    raise RuntimeError(f"Service not ready at {url}: {last_error}")


def verify() -> None:
    wait_for(API_URL + "/health")
    wait_for(WEB_URL + "/api/teams")

    api_teams = request_json(API_URL + "/v1/teams")
    web_teams = request_json(WEB_URL + "/api/teams")

    for catalog in (api_teams, web_teams):
        if catalog.get("dataset_label") != "Synthetic demonstration data":
            raise AssertionError("Synthetic dataset label is missing")
        teams = catalog.get("teams")
        if not isinstance(teams, list) or not {"Demo City", "Demo East"} <= set(teams):
            raise AssertionError("Expected fictional team names are missing")
        if catalog.get("last_match_date") != "2025-07-18":
            raise AssertionError("Unexpected synthetic dataset date")

    if api_teams != web_teams:
        raise AssertionError("Next.js team proxy changed the backend catalog")

    payload = {
        "home_team": "Demo City",
        "away_team": "Demo East",
        "as_of": "2025-07-19",
    }
    api_forecast = request_json(API_URL + "/v1/forecast", payload)
    web_forecast = request_json(WEB_URL + "/api/forecast", payload)

    if api_forecast != web_forecast:
        raise AssertionError("Frontend proxy changed the backend forecast response")

    if web_forecast.get("dataset_label") != "Synthetic demonstration data":
        raise AssertionError("Synthetic forecast not labeled")
    if "fictional" not in web_forecast.get("notice", "").lower():
        raise AssertionError("Synthetic-data disclaimer not returned")

    expected_goals = web_forecast.get("expected_goals", {})
    if not isinstance(expected_goals, dict) or not all(
        isinstance(expected_goals.get(team), (int, float)) and expected_goals[team] > 0
        for team in ("home", "away")
    ):
        raise AssertionError("Expected-goals output is missing or invalid")

    probabilities = web_forecast.get("probabilities", {})
    if not isinstance(probabilities, dict):
        raise AssertionError("Outcome probabilities missing")
    total = sum(probabilities.get(outcome, -1) for outcome in ("home_win", "draw", "away_win"))
    if abs(total - 1.0) > 0.002:
        raise AssertionError(f"Outcome probabilities do not sum to one: {total}")

    print("Synthetic demo smoke test passed: Python API -> Next.js proxies -> forecast")
    health = request_json(API_URL + "/health")
    source = health.get("data_source")
    if source not in ("csv", "postgres"):
        raise AssertionError(f"Unexpected API data source: {source!r}")
    if health.get("configured") is not True:
        raise AssertionError("Configured data source is not ready")
    print(f"Fictional data provenance verified; API source: {source}.")
    print("No external bookmaker or football-data provider was used.")


if __name__ == "__main__":
    try:
        verify()
    except Exception as exc:
        print(f"Demo smoke test FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
