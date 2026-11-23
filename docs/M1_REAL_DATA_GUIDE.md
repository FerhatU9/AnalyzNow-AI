# AnalysNow AI — M1: first authorized real football dataset

**Current status:** provider adapter and verification unit-tested offline. A full real-data download/backtest has **not been run by the project authoring environment** due to outbound network restrictions. Run the commands below on Windows and check the result before treating M1 as achieved.

## What we've built

- OpenFootball CC0 Premier League season downloader (one request per season), with official repository URLs only.
- Strict score parser supporting both `{"ft": [home, away]}` and `[home, away]` forms.
- Results on/after the cutoff day are excluded, even if a future result appears in the source.
- Undecided/unplayed fixtures are excluded; inconsistent scores, dates, teams and duplicates fail rather than being repaired.
- Saves unchanged source JSON for each season, one combined five-column CSV, and a manifest with timestamps and SHA-256 hashes.
- Explicit 380-match completeness warning for each finished EPL season; verify `PASS_380_RESULTS` for all four years.
- Offline snapshot verifier, date-safe walk-forward backtest and an optional test-start date.

## 1. Extract v0.2 and open it in VS Code

Download **AnalysNow_AI_v0.2.zip** and extract into a **new folder**, e.g. `C:\Projects\AnalysNow_AI_v0.2`. Do not overwrite a folder where you've made your own edits. Open the extracted folder in VS Code, then go to **Terminal > New Terminal** (PowerShell). These commands run in the extracted folder.

If you have not set up a virtual environment in this *new* folder:

```powershell
py -3 -m venv .venv
```

Install and check with the environment's Python directly, so PowerShell activation is unnecessary:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
```

Expected locally before real-data download: **27 tests passing** (the exact number may increase as code changes).

## 2. Download original results and produce a normalized CSV

```powershell
.\.venv\Scripts\python.exe -m football_intel fetch-openfootball --as-of 2025-07-01
```

The command downloads four **completed** English Premier League seasons: 2021/22, 2022/23, 2023/24 and 2024/25. It does *not* need an API key. It creates a NEW directory `data\openfootball\epl_2021_2025`, including a `manifest.json`, raw source snapshots and a combined CSV. It refuses to overwrite that directory if it already exists: this protects reproducibility. Use a different `--dest` for a fresh snapshot.

The combined file path is:

```text
data\openfootball\epl_2021_2025\processed\epl_2021-22_2022-23_2023-24_2024-25.csv
```

Inspect the `manifest.json`: each finished season should ideally report `PASS_380_RESULTS`. A 380-match season is an expected-count check, **not** an independent accuracy check. If one season says `WARNING_EXPECTED_380`, stop and inspect the source before drawing performance conclusions.

Note: Raw GitHub `master` can change. This project stores exactly what was downloaded and its SHA-256 checksum, so comparisons can refer to an identifiable snapshot.

## 3. Verify local files have not changed

```powershell
.\.venv\Scripts\python.exe -m football_intel verify-snapshot data\openfootball\epl_2021_2025
```

Expected: `"verified": true` and a nonzero completed match count. The verifier recomputes hashes for the original JSON files and combined CSV and checks the CSV row count.

## 4. Run real-data backtesting

We will assess only matches from the **2024/25** season, after learning from earlier results. The model always trains only with scores dated *before* the match being predicted.

```powershell
.\.venv\Scripts\python.exe -m football_intel backtest data\openfootball\epl_2021_2025\processed\epl_2021-22_2022-23_2023-24_2024-25.csv --min-training 380 --test-from 2024-08-01 --output outputs\epl_2024-25_backtest.json
```

The console prints: `n_test_matches`, `model_brier`, `baseline_brier`, `model_log_loss`, `baseline_log_loss`, and a date range. **Lower is better** for both Brier and log loss. The comparison baseline is a simple historical home/draw/away outcome frequency, not a bookmaker or sophisticated competing model. We need to inspect test sample size and losses before deciding what to improve.

If the backtest is slower than expected, it is currently a transparent, unoptimized walk-forward implementation: prioritizing correctness over speed at this stage.

## 5. Run a demonstration forecast from real history

```powershell
.\.venv\Scripts\python.exe -m football_intel predict data\openfootball\epl_2021_2025\processed\epl_2021-22_2022-23_2023-24_2024-25.csv "Arsenal FC" "Chelsea FC" --as-of 2025-01-01
```

This produces a **research example**, not a recommendation or a claim about a particular upcoming fixture. A trained baseline using match results alone cannot account for xG, player availability, tactics or team news.

## 6. Optional: show forecasts in your local API

Set the CSV path and run FastAPI from a PowerShell terminal in the project root:

```powershell
$env:FOOTBALL_CSV_PATH = "data/openfootball/epl_2021_2025/processed/epl_2021-22_2022-23_2023-24_2024-25.csv"
.\.venv\Scripts\python.exe -m uvicorn football_intel.api:app --reload
```

Open http://127.0.0.1:8000/docs to interact with the endpoint. Stop with **Ctrl+C**. This development API has no authentication and must not be published publicly yet.

## M1 completion checklist

- [ ] Windows setup and test suite passed
- [ ] Four season snapshots fetched, normalized, preserved and hashed
- [ ] Provenance manifest reviewed; expected-count checks passed or investigated
- [ ] Snapshot integrity verifier passed
- [ ] Real 2024/25 walk-forward backtest completed, with sample size and metrics recorded
- [ ] Results discussed with limitations, including absence of xG, news and independent score verification

**Do not claim M1 is completed merely because the 27 offline tests pass.** Actual provider download and real results need to be exercised separately.
