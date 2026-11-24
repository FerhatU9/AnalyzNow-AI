# AnalyzNow AI — Reproducible Local Demo

This walkthrough runs the historical forecasting interface with **fictional** football teams and scores. It requires neither PostgreSQL nor an odds-provider API key. It is a functionality demonstration, **not** evidence that the model predicts real matches accurately.

## Prerequisites

- Python 3.11+ and Node.js 20.9+ installed.
- A clean checkout of this branch and two terminal windows.
- Follow the main README for Python dependency installation.

## Terminal 1 — API

From the repository root in Windows PowerShell:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
$env:FOOTBALL_DATA_SOURCE = "csv"
$env:FOOTBALL_CSV_PATH = "data/synthetic_demo.csv"
.\.venv\Scripts\python.exe -m uvicorn football_intel.api:app --host 127.0.0.1 --port 9011
```

If you already use an existing local `.env`, **do not replace it** with the example. The two `$env:` commands override source settings only for the running PowerShell session.

The teams endpoint at http://127.0.0.1:9011/v1/teams returns the six fictional demo clubs and labels the source `Synthetic demonstration data`. Historical forecast API documentation is available at http://127.0.0.1:9011/docs.

## Terminal 2 — Dashboard

Create `frontend/.env.local` with:

```dotenv
FOOTBALL_API_URL=http://127.0.0.1:9011
```

Then run:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev -- --hostname 127.0.0.1 --port 3011
```

Open http://127.0.0.1:3011.

The team selectors should show fictional clubs such as Demo City and Demo East. The source label must read **Synthetic demonstration data**, and the initial historical cutoff is **2025-07-19**, after the final fictional match in the bundled dataset. Select two different teams and click **Generate Forecast**.

**Observed local test (2026-11-23):** Demo City vs Demo East rendered successfully with 1.60/1.00 expected goals, 51.3% home-win, 25.0% draw and 23.7% away-win probabilities. The synthetic-data warning was visible. This result demonstrates browser/API integration in the developer's environment. On **2026-11-24**, the developer independently cloned `research/elo-evaluation` into `AnalyzNow_Review`, installed Python and npm dependencies, ran FastAPI at `127.0.0.1:9021` and Next.js at `127.0.0.1:3021` using only the synthetic CSV, and confirmed the same forecast in the browser. The `/model-quality` page also rendered. A separately run `scripts/verify_demo.py --api-url http://127.0.0.1:9021 --web-url http://127.0.0.1:3021` passed. This verifies a separate local checkout on the same computer; it does not reproduce external-data research or prove production deployment readiness.

The live bookmaker-odds panel is developed on a separate feature branch and requires its own integration checks and provider credentials. No live bookmaker data is part of this demo.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

For comparison, the original developer database contained 1,520 Premier League results from 2021/22–2024/25. Those results are **not included** in this GitHub repository. The synthetic mode is intended to make the application runnable without redistributing external match records or requiring a personal PostgreSQL environment.

## Boundaries

- The synthetic dataset contains intentionally artificial match outcomes; they must never appear as real Premier League results.
- The independent-Poisson model is a research baseline without robust modern fixture validation, calibration or commercial reliability claims.
- This runs locally, not on a public production server. Security, accessibility, and deployment reviews remain separate.
