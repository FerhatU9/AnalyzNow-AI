import pytest
from football_intel.data import load_matches, parse_date


def test_dates():
    assert parse_date("15/11/2026").isoformat() == "2026-11-15"
    assert parse_date("2026-11-15").isoformat() == "2026-11-15"


def test_valid_and_unplayed(tmp_path):
    path = tmp_path / "matches.csv"
    path.write_text("Date,HomeTeam,AwayTeam,FTHG,FTAG\n01/01/2026,A,B,2,1\n02/01/2026,B,A,,\n", encoding="utf-8")
    matches = load_matches(path)
    assert len(matches) == 1
    assert matches[0].outcome == "H"


def test_reject_duplicate(tmp_path):
    path = tmp_path / "matches.csv"
    row = "01/01/2026,A,B,2,1\n"
    path.write_text("Date,HomeTeam,AwayTeam,FTHG,FTAG\n" + row + row, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate"):
        load_matches(path)


def test_reject_partial_score(tmp_path):
    path = tmp_path / "matches.csv"
    path.write_text("Date,HomeTeam,AwayTeam,FTHG,FTAG\n01/01/2026,A,B,2,\n", encoding="utf-8")
    with pytest.raises(ValueError, match="incomplete"):
        load_matches(path)


def test_reject_negative_score(tmp_path):
    path = tmp_path / "matches.csv"
    path.write_text("Date,HomeTeam,AwayTeam,FTHG,FTAG\n01/01/2026,A,B,-1,1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="negative"):
        load_matches(path)
