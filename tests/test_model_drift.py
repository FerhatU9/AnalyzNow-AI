"""Tests of the read-only, descriptive forecasting diagnostics."""
import json

import pytest

from scripts.evaluate_model_drift import load_journal, metrics, season_diagnostics, summarize


def row(day, actual, home, draw, away):
    return {
        "date": day, "actual": actual,
        "forecast": {"home_win": home, "draw": draw, "away_win": away},
    }


def test_perfect_multiclass_scores():
    data = [row("2024-01-01", "H", 1, 0, 0), row("2024-01-02", "D", 0, 1, 0)]
    result = metrics(data)
    assert result["matches"] == 2
    assert result["brier"] == 0
    assert result["log_loss"] == 0
    assert result["accuracy"] == 1


def test_actual_minus_predicted_is_signed():
    data = [row("2024-01-01", "D", .5, .25, .25), row("2024-01-02", "D", .5, .25, .25)]
    result = metrics(data)
    assert result["outcomes"]["draw"]["observed_minus_predicted"] == .75
    assert result["outcomes"]["home_win"]["observed_minus_predicted"] == -.5


def test_first_and_second_halves_do_not_overlap():
    data = [row(f"2024-01-0{i}", "H", .6, .2, .2) for i in range(1, 5)]
    result = season_diagnostics(data)
    assert result["first_half"]["matches"] == 2
    assert result["second_half"]["matches"] == 2
    assert result["overall"]["matches"] == 4


def test_reject_overlapping_seasons():
    first = [row("2024-06-02", "H", .5, .25, .25)]
    second = [row("2024-05-02", "D", .5, .25, .25)]
    with pytest.raises(ValueError, match="end before"):
        summarize(first, second)


def test_parse_rounding_and_sort(tmp_path):
    path = tmp_path / "journal.json"
    values = [row("2025-03-04", "A", .333333, .333333, .333334), row("2025-03-02", "H", .5, .25, .25)]
    path.write_text(json.dumps({"individual_forecasts": values}), encoding="utf-8")
    data = load_journal(path)
    assert data[0]["date"] == "2025-03-02"
    assert data[-1]["date"] == "2025-03-04"


@pytest.mark.parametrize("probs", [(.5, .5, .5), (-.1, .5, .6), (float("nan"), .4, .6)])
def test_reject_invalid_probabilities(tmp_path, probs):
    path = tmp_path / "journal.json"
    path.write_text(json.dumps({"individual_forecasts": [row("2024-01-01", "H", *probs)]}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_journal(path)
