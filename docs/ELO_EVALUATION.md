# AnalyzNow AI — Elo Forecast Evaluation

## Purpose

Compare a simple Elo ratings model with the existing recency-weighted Poisson model. This is a **research comparison**, not a claim of current-match predictive accuracy or a betting recommendation.

## Setup

From the repository root, with the project's existing virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_elo.py

.\.venv\Scripts\python.exe scripts\compare_elo.py
```

The script reads the existing 2024/25 Poisson journal at `outputs/epl_2024_25_evaluation.json` and the locally downloaded match-results CSV at `data/openfootball/epl_2021_2025/processed/epl_2021-22_2022-23_2023-24_2024-25.csv`.

It writes `outputs/elo_comparison.json`; that output is ignored by Git and may contain historical match records. Do not upload or commit external match data without confirming permitted use.

## Method

- Elo starts each previously unseen team at 1,500 rating points.
- Expected outcome score uses the standard Elo home-advantage adjusted logistic formula.
- Match result scores: home win 1, draw 0.5, away win 0.
- Historical draw frequency (smoothed from earlier fixtures) and an imbalance adjustment convert expected match score to three probabilities (home/draw/away). This is a simple, uncalibrated modelling assumption.
- K-factor and home-advantage settings are selected exclusively using 2023/24 validation fixtures; earlier matches contribute to rating history.
- After selecting parameters, the Elo model evaluates 2024/25 held-out matches against the **same** fixtures from the Poisson journal.
- Predictions for all matches on a date use only previous dates. Results from a particular date do not influence other matches on that date.
- The original Poisson model and live dashboard remain unchanged.

## Interpreting results

Lower Brier score and log loss are better. Top-outcome accuracy is supplementary and may be misleading when considering probability quality. A one-season result is suggestive, not proof that one model is consistently better. Future work should include uncertainty estimates, additional untouched seasons, and comparison of calibration by outcome category.

Do not change the production forecasting API based on this experiment alone.
