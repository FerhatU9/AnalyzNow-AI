import json
from datetime import date
from pathlib import Path
import pytest

from football_intel.data import load_matches
from football_intel.providers import openfootball as of


def sample(season="2023-24", *, second_score=[1, 1]):
    first = {"date": "2023-08-11", "team1": "A FC", "team2": "B FC", "score": {"ft": [2, 0]}}
    second = {"date": "2023-08-12", "team1": "C FC", "team2": "D FC", "score": second_score}
    return json.dumps({"name": "English Premier League 2023/24", "matches": [
        first, second,
        {"date": "2023-08-11", "team1": "A FC", "team2": "C FC", "score": {}},
        {"date": "2023-08-14", "team1": "A FC", "team2": "D FC", "score": {"ft": [4, 4]}}
    ]}).encode()


def test_parse_object_array_and_unplayed():
    result = of.parse_season(sample(), season="2023-24", as_of=date(2023, 8, 14))
    assert len(result.matches) == 2
    assert result.pending == 1
    assert result.future_or_today == 1
    assert [m.home_goals for m in result.matches] == [2, 1]


def test_same_day_score_not_used():
    result = of.parse_season(sample(), season="2023-24", as_of=date(2023, 8, 12))
    assert len(result.matches) == 1
    assert result.future_or_today == 2


def test_reject_invalid_goals():
    with pytest.raises(ValueError, match="invalid final score"):
        of.parse_season(sample(second_score=[True, 0]), season="2023-24", as_of=date(2023, 8, 14))


def test_reject_duplicate_completed_fixture():
    raw = json.loads(sample())
    raw["matches"].append(raw["matches"][0])
    with pytest.raises(ValueError, match="duplicated"):
        of.parse_season(json.dumps(raw).encode(), season="2023-24", as_of=date(2023, 8, 14))


def test_reject_wrong_league():
    raw = json.loads(sample())
    raw["name"] = "German Bundesliga 2023/24"
    with pytest.raises(ValueError, match="Premier League"):
        of.parse_season(json.dumps(raw).encode(), season="2023-24", as_of=date(2023, 8, 14))


def test_reject_invalid_season():
    with pytest.raises(ValueError):
        of.season_url("2023-29")
    with pytest.raises(ValueError):
        of.season_url("../../secrets")


def test_import_creates_verifiable_snapshot(tmp_path):
    destination = tmp_path / "snapshot"
    result = of.import_seasons({"2023-24": sample()}, destination=destination, as_of=date(2023, 8, 14))
    assert result["total_completed_matches"] == 2
    assert Path(result["full_csv_path"]).is_file()
    assert len(load_matches(result["full_csv_path"])) == 2
    assert of.verify_snapshot(destination)["verified"] is True
    with pytest.raises(FileExistsError):
        of.import_seasons({"2023-24": sample()}, destination=destination, as_of=date(2023, 8, 14))
    (destination / "raw" / "2023-24.json").write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        of.verify_snapshot(destination)


def test_download_is_tested_offline(monkeypatch, tmp_path):
    fetched = []
    def fake_fetch(url):
        fetched.append(url)
        return sample()
    monkeypatch.setattr(of, "fetch_bytes", fake_fetch)
    result = of.download_seasons(["2023-24"], destination=tmp_path / "snap", as_of=date(2023, 8, 14))
    assert fetched == [of.season_url("2023-24")]
    assert result["total_completed_matches"] == 2


def test_reject_malformed_provider_data_before_writing(tmp_path):
    dest = tmp_path / "invalid"
    with pytest.raises(ValueError):
        of.import_seasons({"2023-24": b'{"oops":true}'}, destination=dest, as_of=date(2023, 8, 14))
    assert not dest.exists()


def test_missing_future_scores_not_reclassified():
    raw = json.loads(sample())
    raw["matches"][1]["score"] = None
    parsed = of.parse_season(json.dumps(raw).encode(), season="2023-24", as_of=date(2023, 8, 14))
    assert len(parsed.matches) == 1
    assert parsed.pending == 2


def test_reject_wrong_schema_score():
    raw = json.loads(sample())
    raw["matches"][0]["score"] = {"ft": [2, "0"]}
    with pytest.raises(ValueError, match="invalid final score"):
        of.parse_season(json.dumps(raw).encode(), season="2023-24", as_of=date(2023, 8, 14))


def test_reject_score_with_out_of_season_date():
    raw = json.loads(sample())
    raw["matches"][0]["date"] = "2025-10-01"
    with pytest.raises(ValueError, match="outside season window"):
        of.parse_season(json.dumps(raw).encode(), season="2023-24", as_of=date(2026, 1, 1))
