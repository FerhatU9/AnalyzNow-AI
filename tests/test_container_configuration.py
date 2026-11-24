"""Container-specific configuration must preserve the existing Windows defaults."""
from __future__ import annotations

from datetime import date

from football_intel import database
from football_intel.api import _dataset_label


class DummyConnection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def execute(self, sql, args):
        return self

    def fetchall(self):
        return []


def test_postgres_connection_defaults(monkeypatch):
    for setting in ("POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER"):
        monkeypatch.delenv(setting, raising=False)
    monkeypatch.setenv("POSTGRES_PASSWORD", "test-password")
    recorded = {}

    def connect(**kwargs):
        recorded.update(kwargs)
        return DummyConnection()

    monkeypatch.setattr(database.psycopg, "connect", connect)
    assert database.load_matches_from_database(date(2025, 7, 1)) == []
    assert recorded["host"] == "127.0.0.1"
    assert recorded["port"] == 5433
    assert recorded["dbname"] == "analyznow"
    assert recorded["user"] == "analyznow"


def test_postgres_container_connection(monkeypatch):
    monkeypatch.setenv("POSTGRES_PASSWORD", "test-password")
    monkeypatch.setenv("POSTGRES_HOST", "postgres")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "analyznow_demo")
    monkeypatch.setenv("POSTGRES_USER", "analyznow_demo")
    recorded = {}

    def connect(**kwargs):
        recorded.update(kwargs)
        return DummyConnection()

    monkeypatch.setattr(database.psycopg, "connect", connect)
    assert database.load_matches_from_database(date(2025, 7, 1)) == []
    assert recorded["host"] == "postgres"
    assert recorded["port"] == 5432
    assert recorded["dbname"] == "analyznow_demo"
    assert recorded["user"] == "analyznow_demo"


def test_postgres_demo_label_requires_isolated_database(monkeypatch):
    monkeypatch.setenv("FOOTBALL_DATA_SOURCE", "postgres")
    monkeypatch.setenv("FOOTBALL_DEMO_DATASET", "1")
    monkeypatch.setenv("POSTGRES_DB", "analyznow_demo")
    assert _dataset_label() == "Synthetic demonstration data"

    monkeypatch.setenv("POSTGRES_DB", "analyznow")
    assert _dataset_label() == "Configured PostgreSQL match results"
