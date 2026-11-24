"""Ensure browser-based showcase matches the repository's Python Poisson model.

This check uses only bundled fictional results and Python standard libraries,
plus the Node.js runtime already present on GitHub Actions runners.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from football_intel.data import load_matches  # noqa: E402
from football_intel.model import forecast, train  # noqa: E402


def run() -> None:
    root_data = (ROOT / "data" / "synthetic_demo.csv").read_bytes()
    site_data = (ROOT / "docs" / "assets" / "matches.csv").read_bytes()
    if root_data != site_data:
        raise AssertionError("Website CSV differs from the canonical fictional dataset")

    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    for marker in ("id=\"forecast-form\"", "id=\"home-team\"", "id=\"away-team\"",
                   "id=\"result-content\"", "Fictional", "GitHub", "assets/site.js"):
        if marker not in html:
            raise AssertionError(f"Missing website feature: {marker}")

    css = (ROOT / "docs" / "assets" / "site.css").read_text(encoding="utf-8")
    if len(css) < 2000 or "@media" not in css:
        raise AssertionError("Responsive website stylesheet is missing")

    matches = load_matches(ROOT / "data" / "synthetic_demo.csv")
    cases = [
        ("Demo City", "Demo East", "2025-07-19"),
        ("Demo North", "Demo South", "2025-05-01"),
        ("Demo United", "Demo West", "2025-06-01"),
    ]
    node_program = r"""
import fs from 'node:fs';
import {parseMatches, demoTeams, demoForecast} from './docs/assets/forecast.mjs';
const matches = parseMatches(fs.readFileSync('./docs/assets/matches.csv', 'utf8'));
const cases = JSON.parse(process.argv[1]);
if (matches.length !== 100 || demoTeams(matches).length !== 6) throw new Error('Unexpected fictional demo data');
console.log(JSON.stringify(cases.map(([home,away,cutoff]) => demoForecast(matches,home,away,cutoff))));
"""
    process = subprocess.run(
        ["node", "--input-type=module", "-e", node_program, json.dumps(cases)],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    results = json.loads(process.stdout)
    for (home, away, cutoff), result in zip(cases, results, strict=True):
        py = forecast(train(matches, date.fromisoformat(cutoff)), home, away)
        for key in ("home", "away"):
            if abs(result["expected_goals"][key] - py["expected_goals"][key]) > 0.00011:
                raise AssertionError(f"Expected goals discrepancy for {home}/{away}: {key}")
        for key in ("home_win", "draw", "away_win", "over_2_5", "under_2_5", "both_teams_score"):
            if abs(result["probabilities"][key] - py["probabilities"][key]) > 0.000002:
                raise AssertionError(f"Probability discrepancy for {home}/{away}: {key}")
        if abs(sum(result["probabilities"][k] for k in ("home_win","draw","away_win")) - 1) > 1e-9:
            raise AssertionError("Outcome probabilities do not sum to one")
        if result["historical_matches_used"] != py["diagnostics"]["prior_matches"]:
            raise AssertionError("Historical match cutoff differs from Python model")
        if [x["score"] for x in result["top_scorelines"]] != [x["score"] for x in py["top_scorelines"]]:
            raise AssertionError("Top scoreline order differs from Python model")
    print(f"GitHub Pages site verified: 100 fictional fixtures, 6 clubs, {len(cases)} Python/JavaScript forecast parity cases")


if __name__ == "__main__":
    run()
