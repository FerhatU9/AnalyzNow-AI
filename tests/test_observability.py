"""API observability contracts: no credentials, paths or payloads in logs."""
from __future__ import annotations

import json
import re

from fastapi.testclient import TestClient

from football_intel.api import app
from football_intel import observability


def test_request_id_and_safe_success_log(monkeypatch):
    events = []
    monkeypatch.setattr(observability.LOGGER, "info", lambda message: events.append(json.loads(message)))
    client = TestClient(app)

    response = client.get("/health?secret=never-log-this")
    assert response.status_code == 200
    request_id = response.headers["x-request-id"]
    assert re.fullmatch(r"[0-9a-f]{32}", request_id)

    event = events[-1]
    assert event["event"] == "http_request"
    assert event["request_id"] == request_id
    assert event["method"] == "GET"
    assert event["route"] == "/health"
    assert event["status_code"] == 200
    assert event["duration_ms"] >= 0
    assert "never-log-this" not in json.dumps(event)
    assert "secret" not in json.dumps(event)


def test_client_supplied_request_id_is_not_reflected(monkeypatch):
    events = []
    monkeypatch.setattr(observability.LOGGER, "info", lambda message: events.append(json.loads(message)))
    response = TestClient(app).get("/health", headers={"X-Request-ID": "untrusted-id"})
    assert response.status_code == 200
    assert response.headers["x-request-id"] != "untrusted-id"
    assert events[-1]["request_id"] == response.headers["x-request-id"]


def test_failed_request_has_status_and_no_request_body(monkeypatch):
    events = []
    monkeypatch.setattr(observability.LOGGER, "info", lambda message: events.append(json.loads(message)))
    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "csv")
    monkeypatch.delenv("FOOTBALL_CSV_PATH", raising=False)

    response = TestClient(app).post(
        "/v1/forecast",
        json={"home_team": "Do-not-log-home", "away_team": "Do-not-log-away"},
    )
    assert response.status_code == 503
    assert "x-request-id" in response.headers
    event = events[-1]
    assert event["route"] == "/v1/forecast"
    assert event["status_code"] == 503
    assert "Do-not-log" not in json.dumps(event)


def test_unmatched_url_not_logged(monkeypatch):
    events = []
    monkeypatch.setattr(observability.LOGGER, "info", lambda message: events.append(json.loads(message)))
    response = TestClient(app).get("/private-name-should-not-appear")
    assert response.status_code == 404
    assert events[-1]["route"] == "<unmatched>"
    assert "private-name-should-not-appear" not in json.dumps(events[-1])
