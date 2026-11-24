# AnalyzNow AI — 2025/26 Forecasting Evaluation

## Why this test matters

The existing Poisson, Elo and 50:50 ensemble comparisons used the 2024/25 Premier League season. After viewing those results, we **must not** reuse that same season as evidence of an independently confirmed ensemble improvement. The completed 2025/26 season provides a later season for testing a frozen model configuration.

The Elo parameters `k_factor=32` and `home_advantage=40` were selected during the prior research. The ensemble is fixed at 50% Elo, 50% Poisson. No settings are selected using the new season.

## Source

The project's existing OpenFootball importer downloads English Premier League results from `openfootball/football.json`. That source declares its football data public domain; keep provenance and verify any license changes before commercial redistribution. It includes all 380 completed 2025/26 league matches (source inspection 23 November 2026).

## Steps on Windows PowerShell

From the repository root on your existing `research/elo-evaluation` branch, with the previous Elo packages installed:

```powershell
.\.venv\Scripts\python.exe -m football_intel fetch-openfootball --seasons 2021-22 2022-23 2023-24 2024-25 2025-26 --dest data/openfootball/epl_2021_2026 --as-of 2026-07-01
.\.venv\Scripts\python.exe -m football_intel verify-snapshot data/openfootball/epl_2021_2026
```

This creates a **new**, ignored dataset snapshot. It does not overwrite the older 2021–2025 results or change PostgreSQL.

Next run the existing Poisson walk-forward backtest on that same five-season CSV:

```powershell
.\.venv\Scripts\python.exe -m football_intel backtest "data\openfootball\epl_2021_2026\processed\epl_2021-22_2022-23_2023-24_2024-25_2025-26.csv" --min-training 760 --test-from 2025-08-01 --output outputs\epl_2025_26_evaluation.json
```

Then run the new checks and frozen comparison:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_heldout.py
.\.venv\Scripts\python.exe -m scripts.evaluate_heldout
```

The full JSON evaluation is written to `outputs/heldout_2025_26_evaluation.json`.

## Interpretation

- Lower Brier and log loss are better.
- Accuracy is informative but less complete than probability scores.
- All forecasts use strictly older match dates. The 2025/26 season outcomes update Elo and Poisson inputs *only after* each corresponding match date.
- Match-date-clustered bootstrap intervals estimate the uncertainty of the pairwise loss differences, subject to season/league dependencies.
- A single new season is important evidence, not proof of commercial-grade predictive skill.
- Do not use fresh current bookmaker odds as if they were historical closing odds. Do not commit raw source files or output journals until licensing and privacy checks are complete.

## Scope

This is an isolated research comparison. The existing dashboard, FastAPI endpoints, PostgreSQL database and production forecast remain unchanged.
