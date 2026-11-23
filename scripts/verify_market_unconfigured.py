"""Check predictable odds API failures through FastAPI and the Next.js proxy.

Run with no ODDS_API_KEY set alongside the synthetic full-stack smoke test.
"""
from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def assert_missing_key(url: str) -> None:
    try:
        with urlopen(Request(url, headers={"Accept": "application/json"}), timeout=8) as response:
            raise AssertionError(f"Expected HTTP 503 but got {response.status}: {url}")
    except HTTPError as exc:
        if exc.code != 503:
            raise AssertionError(f"Expected HTTP 503 but got {exc.code}: {url}") from exc
        with exc:
            payload = json.load(exc)
        if not isinstance(payload, dict):
            raise AssertionError(f"Invalid JSON error payload: {url}")


if __name__ == "__main__":
    assert_missing_key("http://127.0.0.1:9011/v1/market-odds")
    assert_missing_key("http://127.0.0.1:3011/api/market-odds")
    print("Market provider-unconfigured paths verified through backend and frontend proxy")
