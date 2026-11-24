# AnalyzNow AI — Ensemble Evaluation

## Purpose

Check whether an **exploratory, fixed equal-weight average** of Elo and Poisson probabilities improves the measured quality of historical three-way forecasts. The original models, code and published demo are not modified by this experiment.

## Method

- Match the historical CSV to the existing Poisson walk-forward backtest journal using date, fixture and actual result. Reject duplicate or missing fixtures.
- Select Elo hyperparameters on the earlier validation season, using the same logic as the existing Elo comparison.
- Calculate a simple arithmetic average for each of the three outcomes: `0.5 * Elo + 0.5 * Poisson`.
- Evaluate Elo, Poisson and the ensemble on the identical 380 matches of 2024/25.
- Compare Brier score, log loss and most likely outcome accuracy. Calculate uncertainty intervals by resampling **whole match days** with a fixed seed.
- Calculate average predicted draw frequency versus observed draw frequency.

## Run locally

From the project root, after unpacking the files:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_ensemble.py
.\.venv\Scripts\python.exe -m scripts.evaluate_ensemble
```

This requires the same local CSV and `outputs/epl_2024_25_evaluation.json` used for the earlier Elo work. It creates `outputs/ensemble_evaluation.json` containing aggregated scores, not provider odds or fixture-level licensed content.

## Research limitation

**The 2024/25 scores were already inspected before this blending hypothesis was proposed.** Although the weight is fixed at 50:50 and not chosen by optimizing the held-out season, this evaluation is exploratory and should not be presented as independent evidence of future superiority.

Before changing the live model, freeze a candidate method and evaluate it on a later genuinely unseen season, or use a rigorously designed multiple-season rolling-origin study. Do not tune on 2024/25 and then claim it was untouched test data.

A confidence interval spanning zero does not establish improvement. A narrow interval in a single season also does not guarantee generalization to future seasons, leagues or bookmaker markets.
