# AnalyzNow AI

**Football intelligence · Statistical forecasting · Bookmaker market analysis**

AnalyzNow AI is a football research application that turns historical match results into probabilistic forecasts and provides a separate view of bookmaker-implied market expectations. The project combines a Python forecasting engine, PostgreSQL, FastAPI and a Next.js dashboard.

**Status:** Active development. Local forecasting, database integration, the web dashboard and market-data retrieval have been exercised. The application is **not deployed publicly**, and its forecasts have not been validated for betting or commercial decision-making.

## What the application does

| Capability | Current status |
| --- | --- |
| Historical Premier League data ingestion and source snapshots | Implemented; four completed seasons imported locally |
| PostgreSQL storage and SQL queries | Implemented; 1,520 match records across 26 clubs in the local dataset |
| Independent-Poisson forecasting model | Implemented; expected goals, match outcome and goal-market probabilities |
| Walk-forward historical evaluation | Implemented; evaluated on 760 Premier League fixtures from 2023/24–2024/25 |
| FastAPI forecasting endpoint | Implemented and exercised with PostgreSQL data |
| Next.js interactive forecasting dashboard | Implemented and exercised locally |
| Current bookmaker odds retrieval and margin normalization | Implemented; API endpoint and calculation tests passing |
| Live bookmaker market dashboard | Implemented on the feature branch; pending end-to-end local verification |
| Integrated model-versus-market forecasting | Not implemented; fixtures and prediction dates are not yet aligned |
| Verified team news, RAG, LangGraph match analysis | Planned |
| Public deployment, authentication and production monitoring | Not yet implemented |

The current Poisson model uses **historical final scores**, not a full expected-goals (xG) event dataset. Its numerical output is separate from bookmaker odds. No combined model or profitable betting edge has been established.

## Technology

- **Backend and modelling:** Python, FastAPI, Pydantic, pytest, and standard Python statistical/numerical code.
- **Data:** PostgreSQL 17, Psycopg, SQL, Docker Compose, OpenFootball historical results.
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS.
- **Market data:** The Odds API, bookmaker margin normalization and multi-bookmaker summaries.
- **Engineering:** Git, GitHub Actions workflow, documented source provenance and automated checks.

Refer to [System Architecture](docs/ARCHITECTURE.md), [Development Roadmap](docs/ROADMAP.md), [Technical Research](docs/RESEARCH.md) and [Contribution Standards](CONTRIBUTING.md). Documentation is reviewed alongside each verified feature milestone; roadmap status is not changed until tests and evidence support it.

## Local development (Windows)

### Requirements

Python 3.11 or later, Docker Desktop, Node.js 20.9 or later, npm, Git and VS Code. Use PowerShell from the repository root unless otherwise indicated.

### 1. Python environment

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
```

The project has passed **35 standard automated tests** and **2 PostgreSQL integration tests** on the developer's Windows machine. The latter used the renamed PostgreSQL database with 1,520 historic results. Automated GitHub CI checks have also passed; the live market browser feature still needs end-to-end verification.

### 2. Local configuration and PostgreSQL

**Existing installations:** Read [Local Database Migration](docs/DATABASE_MIGRATION.md) before starting Docker with updated identifiers. Changing the Compose project name does not rename or transfer an existing PostgreSQL volume.

If `.env` does not already exist, copy `.env.example` to `.env` and replace the password placeholder with your own local development password. **Existing local installations:** the PostgreSQL account and Compose project must be migrated before switching to the new database identifiers. Follow [Database Migration](docs/DATABASE_MIGRATION.md) rather than replacing a working `.env` or deleting a volume.

```powershell
Copy-Item .env.example .env
# Edit POSTGRES_PASSWORD in .env before starting the database.
docker compose up -d
docker compose ps
```

The database is bound to `127.0.0.1:5433` for local use. The database container stores its files in a Docker volume. Never commit `.env` or API credentials.

### 3. Historical results and schema

For a new database, create its tables:

```powershell
docker compose cp database/schema.sql postgres:/tmp/schema.sql
docker compose exec -T postgres psql -U analyznow -d analyznow -v ON_ERROR_STOP=1 -f /tmp/schema.sql
```

Retrieve completed Premier League results and verify the saved snapshot:

```powershell
.\.venv\Scripts\python.exe -m football_intel fetch-openfootball --as-of 2025-07-01
.\.venv\Scripts\python.exe -m football_intel verify-snapshot data\openfootball\epl_2021_2025
```

Import the processed results into PostgreSQL:

```powershell
docker compose cp "data\openfootball\epl_2021_2025\processed\epl_2021-22_2022-23_2023-24_2024-25.csv" postgres:/tmp/epl_matches.csv
docker compose cp database/import_matches.sql postgres:/tmp/import_matches.sql
docker compose exec -T postgres psql -U analyznow -d analyznow -v ON_ERROR_STOP=1 -f /tmp/import_matches.sql
```

For the specified four seasons, the expected count is **1,520 completed matches**, provided all source seasons are complete. Importing again updates matching fixture scores instead of inserting duplicate fixtures. More detail is available in [Data Pipeline](docs/DATA_PIPELINE.md). Do not repeat imports unnecessarily on an existing working database.

### 4. FastAPI backend

In a PowerShell terminal at the repository root:

```powershell
$env:FOOTBALL_DATA_SOURCE = "postgres"
.\.venv\Scripts\python.exe -m uvicorn football_intel.api:app --host 127.0.0.1 --port 9011
```

Open [FastAPI documentation](http://127.0.0.1:9011/docs). Example request for `POST /v1/forecast`:

```json
{
  "home_team": "Arsenal FC",
  "away_team": "Chelsea FC",
  "as_of": "2025-07-01"
}
```

This is a historical model demonstration based on data available before the cutoff, **not** a current Arsenal–Chelsea match prediction.

### 5. Next.js frontend

Inside `frontend`, create `.env.local` with:

```dotenv
FOOTBALL_API_URL=http://127.0.0.1:9011
```

In a **separate** PowerShell terminal:

```powershell
cd frontend
npm.cmd ci
npm.cmd run lint
npm.cmd run dev -- --hostname 127.0.0.1 --port 3011
```

Open [AnalyzNow AI dashboard](http://127.0.0.1:3011). Keep the PostgreSQL container and FastAPI terminal running while using the frontend.

## API overview

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Basic development server status (not a database readiness check) |
| `POST` | `/v1/forecast` | Generate a statistical forecast for teams and cutoff date |
| `GET` | `/v1/market-odds` | Retrieve current EPL bookmaker-implied market probabilities |

Market odds access requires `ODDS_API_KEY` in the local `.env`. Run `python -m football_intel.market_odds` to inspect the provider response; this consumes provider API quota. The forecasting dashboard provides a separate **Load market odds** button to request live bookmaker summaries on demand. The interface does not blend historical forecast probabilities with live market probabilities. The new frontend feature requires local end-to-end verification before merging.

## Testing and evaluation

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q tests/integration_postgres.py
```

The second command explicitly runs the PostgreSQL-dependent tests and requires a populated local database.

For a historical evaluation:

```powershell
.\.venv\Scripts\python.exe -m football_intel backtest data\openfootball\epl_2021_2025\processed\epl_2021-22_2022-23_2023-24_2024-25.csv --min-training 380 --test-from 2023-08-01 --output outputs\epl_2023_2025_backtest.json
```

A developer-local walk-forward evaluation on 760 Premier League matches reported a **multiclass Brier score of 0.579285**, compared with **0.646967** for a simple historical league-frequency baseline, and **log loss of 0.975758**, compared with **1.068422** for that baseline. These results have not yet been independently reproduced through CI or compared with stronger forecasting methods. They do not establish calibration, future performance, or betting profitability.

## Repository layout

```text
AnalyzNow-AI/
├── database/             PostgreSQL schema and match importer
├── data/                 Synthetic sample and data provenance guidance
├── docs/                 Architecture, roadmap, research, data pipeline
├── frontend/             Next.js dashboard and server-side API proxy
├── src/football_intel/   Forecasting, ingestion, database and market modules
├── tests/                Automated tests and optional database integration checks
├── compose.yaml          Local PostgreSQL service
├── pyproject.toml        Python package configuration
└── README.md             Project overview and setup
```

## Data rights, safety and limitations

- The OpenFootball source repository declares its football results under CC0. Data provenance is retained locally; scores have not all been independently verified.
- Live odds require an external provider API key and remain subject to provider usage and redistribution terms. Do not assume rights to republish commercial odds.
- Historical results currently stop at the end of the 2024/25 Premier League season. They are **not current-form statistics** for upcoming fixtures.
- The independent-Poisson model does not yet account for injuries, suspensions, xG event data, tactical changes or correlated goal scores.
- The application is a local research tool without public-user authentication, production security controls or deployment readiness.
- Forecasts represent uncertainty and are **not betting recommendations or guarantees of profit**. No real-money betting functionality is provided.

## Project direction

Planned work includes dynamic club selection, a market-data dashboard, time-matched statistical-versus-market comparisons, improved forecast evaluation, verified news, retrieval-augmented analysis, automated monitoring, and secure deployment. Each feature will be considered complete only when its tests and results can be independently checked. See the [Development Roadmap](docs/ROADMAP.md).

## License

Project source code is provided under the [MIT License](LICENSE). Third-party football data, bookmaker feeds and other external materials are governed by their own terms.
