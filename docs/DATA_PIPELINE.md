# AnalyzNow AI — Historical Data Pipeline

This document describes the repeatable data flow from permitted OpenFootball result files into the local PostgreSQL database and statistical evaluation.

## Source and coverage

- Source: [OpenFootball football.json](https://github.com/openfootball/football.json), which declares its football datasets CC0.
- Competition: English Premier League.
- Completed seasons: 2021/22, 2022/23, 2023/24 and 2024/25.
- Expected complete results: 380 per season; 1,520 combined.
- Fields: match date, home club, away club, full-time home goals, full-time away goals.

Expected row counts are completeness indicators, **not independent proof that source scores are correct**.

## Download and verify

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m football_intel fetch-openfootball --as-of 2025-07-01
.\.venv\Scripts\python.exe -m football_intel verify-snapshot data\openfootball\epl_2021_2025
```

The downloader stores unchanged source files, a normalized CSV and a provenance manifest. It refuses to overwrite an existing snapshot, protecting reproducibility. For a new run, use an explicitly different destination rather than deleting a prior snapshot.

Inspect `data/openfootball/epl_2021_2025/manifest.json` for retrieval timestamps, source URLs, file hashes, total rows and per-season checks. The Git ignore rules prevent source snapshots and generated outputs from being committed by default.

## Create the PostgreSQL schema

```powershell
docker compose up -d
docker compose cp database/schema.sql postgres:/tmp/schema.sql
docker compose exec -T postgres psql -U analyznow -d analyznow -v ON_ERROR_STOP=1 -f /tmp/schema.sql
```

## Import the dataset

```powershell
docker compose cp "data\openfootball\epl_2021_2025\processed\epl_2021-22_2022-23_2023-24_2024-25.csv" postgres:/tmp/epl_matches.csv
docker compose cp database/import_matches.sql postgres:/tmp/import_matches.sql
docker compose exec -T postgres psql -U analyznow -d analyznow -v ON_ERROR_STOP=1 -f /tmp/import_matches.sql
```

Verify the count:

```powershell
docker compose exec postgres psql -U analyznow -d analyznow -c "SELECT COUNT(*) AS total_matches FROM matches;"
```

For these four seasons, the developer-local import returned 1,520 records, spanning 26 clubs. The importer uses a transaction and an upsert for matches with the same match date and teams. Score corrections can therefore update existing rows; preserving revision history is future work.

## Evaluate forecasts

```powershell
.\.venv\Scripts\python.exe -m football_intel backtest data\openfootball\epl_2021_2025\processed\epl_2021-22_2022-23_2023-24_2024-25.csv --min-training 380 --test-from 2023-08-01 --output outputs\epl_2023_2025_backtest.json
```

The backtest trains using strictly earlier match dates. Its baseline is a simple historical league-frequency forecast; it is not a sportsbook model. Results require further evaluation for calibration, uncertainty and independent reproducibility.

## Limitations and future improvements

- Date-only fixture data does not establish exact kickoff times. All same-day scores are excluded at each cutoff.
- The database does not yet track competitions, fixture IDs, observed timestamps or licensed xG data.
- Current football results and historical odds are not available in this dataset.
- Do not merge upcoming bookmaker odds with years-old team-form statistics and call it a validated current match prediction.
