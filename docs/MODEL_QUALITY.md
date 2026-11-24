# Model Quality

The Model Quality page turns locally measured historical forecasting results into a user-visible evidence summary. It does not retrain models, update match predictions, access bookmaker APIs, or expose individual fixture records.

## Data sources

For the complete download-to-export procedure, including strict historical cutoffs, evaluation commands and comparison with the committed dashboard metrics, see [Historical Model Reproducibility](MODEL_REPRODUCIBILITY.md). That end-to-end reproduction has not yet been independently completed.

Generate the reports using the existing research scripts:

- `outputs/ensemble_evaluation.json` — 2024/25 exploratory Poisson, Elo and 50/50 ensemble comparison
- `outputs/heldout_2025_26_evaluation.json` — 2025/26 comparison with settings frozen in advance
- `outputs/model_drift.json` — descriptive split-season Poisson performance and observed draw frequencies

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_model_quality_export.py
.\.venv\Scripts\python.exe scripts\export_model_quality.py
```

The export writes **only aggregate model metrics** to `frontend/data/model-quality.json`. It checks all required fields, matching season counts, split-period counts and uncertainty interval consistency. No raw match journals, provider keys or bookmaker quotes are included in the exported data.

To view the page, run the Next.js app locally and visit `http://127.0.0.1:3011/model-quality`. The API does not need to be running for this page, but the rest of the dashboard still uses FastAPI.

If the summary file is missing, the page shows a setup message instead of displaying invented statistics. Regenerate the summary after future evaluation updates; it is not a live monitoring feed.

## Scientific boundaries

- Brier and log loss are **lower-is-better** probability metrics; accuracy is the frequency of correct top-ranked outcomes.
- The 2024/25 ensemble evaluation is exploratory because the season was reviewed during model development.
- The 2025/26 evaluation used parameters selected in advance; the ensemble's small advantage over Poisson had intervals containing zero.
- First/second-period changes are descriptive diagnostics, not evidence of a proven causal performance drift.
- Bookmaker prices, live forecasts, expected returns, and recommendations are outside the scope of this page.
- Before publishing the page, complete the repository's provenance/licensing review for the underlying match-data sources and make sure the methodology claims accurately match the actual runs.

## Source files

- `scripts/export_model_quality.py` — data validation and aggregation
- `frontend/src/app/model-quality/page.tsx` — standalone read-only server-rendered evaluation page
- `tests/test_model_quality_export.py` — aggregate validation tests

This milestone can be merged after Python tests and a real Next.js lint/build/browser check in the user's working project.
