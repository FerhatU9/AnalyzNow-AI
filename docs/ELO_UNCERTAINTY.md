# Elo versus Poisson — Paired Uncertainty Evaluation

## Purpose

Before changing the existing forecasting API, evaluate whether Elo's small apparent advantage is robust to resampling the 2024/25 fixtures. This is a **research diagnostic**, not a betting recommendation, deployment certification, or proof of future predictive skill.

## Commands

From the project root, with the existing virtual environment and local Premier League results:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_elo_uncertainty.py
.\.venv\Scripts\python.exe scripts\evaluate_elo_uncertainty.py
```

The analysis uses the same local historical CSV and Poisson journal as `scripts/compare_elo.py` and chooses Elo parameters only on the earlier 2023/24 validation period. All 380 held-out 2024/25 predictions are paired by exact date and fixture against the existing Poisson journal.

The script produces a human-readable summary and `outputs/elo_uncertainty.json` with aggregate statistics only. The data and local output remain excluded from version control.

## Method and interpretation

- Compute Brier score, log loss, and top-outcome accuracy for each model on each identical fixture.
- Calculate fixture-level **Elo minus Poisson** differences. A negative Brier/log-loss difference favours Elo; a positive accuracy difference favours Elo.
- Resample *whole match dates* with replacement, preserving within-day grouping rather than treating multiple matches on the same day as independent.
- Repeat 3,000 times using a fixed random seed, then report the central 95% percentile interval.
- Calculate each model's average home-win, draw and away-win probability against the observed frequency, without fitting a calibration correction.

A bootstrap interval spanning zero means that this sample does not reliably distinguish the models under this resampling method. Intervals that exclude zero still do not establish out-of-season superiority or control for historical dataset limitations, team changes, or temporal dependencies between dates. Multiple future seasons or pre-registered rolling evaluation windows are stronger evidence.

**Do not select model hyperparameters or blend weights using these held-out 2024/25 results.** Preserve this season as an evaluation record. No production model replacement is made by this script.
