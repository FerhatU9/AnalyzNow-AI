# AnalysNow AI — real-data integration starter v0.2

**Status: tested Poisson baseline plus offline-tested OpenFootball CC0 integration. Full-provider download and real-data backtesting require a network-enabled machine. NOT validated betting advice; NOT production-ready.**

This is the first working component of a larger statistics-first football match intelligence product. The long-term architecture combines validated probability models, verified team news, RAG, LangGraph analysis, a FastAPI backend, and a React dashboard. See [Architecture](docs/ARCHITECTURE.md), [Roadmap](docs/ROADMAP.md), and [Research](docs/RESEARCH_2026-11-18.md).

## New in v0.2 — the next practical milestone

We now have a licensed-data-friendly route to *real* Premier League results via the public-domain OpenFootball project, with original JSON snapshots, SHA-256 provenance hashes, CSV normalization, and verification. The provider adapter is tested with mocked network responses; full real-data backtesting has not been executed in this authoring environment.

**Start here: [M1 Real Data Guide](docs/M1_REAL_DATA_GUIDE.md)** — sequential Windows commands for fetching four completed Premier League seasons and evaluating the 2024/25 season. This is the next step after downloading and extracting the zip; do not repeat previous Python environment troubleshooting unless a command fails.

## Currently implemented

- Verified snapshot import workflow for OpenFootball English Premier League completed results (mock-network tested; exact source snapshots and SHA-256 manifest).
- Strict ingestion of a local results CSV (`Date`, `HomeTeam`, `AwayTeam`, `FTHG`, `FTAG`).
- Recency-weighted independent Poisson goal model with shrinkage toward league means.
- Expected goals, home/draw/away, over/under 2.5, BTTS and top scorelines; diagnostics and assumptions.
- Time-safe daily walk-forward backtest against a pre-cutoff naive league-frequency baseline, reporting Brier and log loss and optional per-match journal.
- Read-only FastAPI development endpoint and automated pytest tests.
- GitHub Actions CI scaffold, Claude Code and Codex repository guidance.

**Not implemented:** real provider-download success verification in this environment, xG, team injuries/news, RAG, LangGraph, validated prediction accuracy, React, PostgreSQL, authentication, Docker and production deployment. See roadmap. The synthetic dataset is for a code smoke test, not predictive performance evidence.

## Step-by-step: run on Windows (PowerShell)

1. Unzip the project to a directory like `C:\Projects\analysnow-ai-starter`.
2. Install Python 3.11+ and VS Code. Open a PowerShell terminal in the extracted project folder.
3. Make and activate a virtual environment:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that **terminal only**, then activate again; alternatively skip activation and use `.\.venv\Scripts\python.exe` for each command.

4. Install the package and test tools:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q
```

5. Validate the **synthetic** CSV, then run a demonstration prediction:

```powershell
analysnow validate data\synthetic_demo.csv
analysnow predict data\synthetic_demo.csv "Demo North" "Demo South" --as-of 2025-08-01
analysnow backtest data\synthetic_demo.csv --min-training 35 --output outputs\synthetic_journal.json
```

6. Start the development API (PowerShell):

```powershell
$env:FOOTBALL_CSV_PATH = "data/synthetic_demo.csv"
uvicorn football_intel.api:app --reload
```

Visit http://127.0.0.1:8000/docs and try `POST /v1/forecast` with:

```json
{
  "home_team": "Demo North",
  "away_team": "Demo South",
  "as_of": "2025-08-01"
}
```

Close the server with **Ctrl+C**. To use real data later, set `FOOTBALL_CSV_PATH` to an authorized local CSV path, and run validations and backtests. The code does not download sports data automatically.

## Important forecasting limitations

- Training uses only completed fixtures before a cutoff date. Date-only CSV data cannot distinguish match order within the same day; all same-day scores are deliberately excluded.
- There is no league ID in the starting schema. Import one *single* competition at a time, not pooled competitions of different strengths.
- A basic Poisson model assumes each team's goal count is independent, and does not yet use xG, injured players, tactics or news.
- Accuracy and calibration have NOT been evaluated on real historical football results here.
- The synthetic sample cannot demonstrate the model's usefulness or any market edge.
- The local API has no user authentication, provider access controls, rate limits or hardened deployment. Do **not** expose it publicly.

## Claude Code and Codex — Windows

These are **development assistants**, not the match analysis agents that will later run inside the product.

**Codex**: Install Node.js first, then in PowerShell:

```powershell
npm install -g @openai/codex
codex
```

Sign in with ChatGPT as prompted. Start in the project root, read `AGENTS.md`, run `/permissions` to restrict actions, and ask:

> Review `src/football_intel/model.py` and `backtest.py` for possible time leakage and numerical errors. Do not modify files yet. Report specific findings and suggested tests.

**Claude Code** (requires a paid eligible Claude plan or separately billed Anthropic Console account):

```powershell
irm https://claude.ai/install.ps1 | iex
claude --version
claude
```

Read `CLAUDE.md`, then ask:

> Review the Poisson forecasting baseline and propose a minimal dataset provenance manifest schema. Do not modify files or fetch external data until I approve a plan.

Never paste secrets into chat or commit `.env`. Use `git diff`, `python -m pytest -q` and a commit after manually reviewing changed files. Use separate agent sessions when helpful. Do not enable unattended production deployment.

## License and data provenance

This original starter code is MIT licensed; that **does not** grant rights to external football data. Only `data/synthetic_demo.csv` is bundled and is entirely artificial. See `data/README.md` and `docs/RESEARCH_2026-11-18.md`. Sources and permissions must be checked before any external data ingestion, storage, training, RAG or commercial use.

## Next phase

Run the OpenFootball fetch and offline verification on a network-enabled Windows machine using [M1 guide](docs/M1_REAL_DATA_GUIDE.md), inspect the actual completed matches and metric output, then investigate model weaknesses before considering a stronger model. Only after those results should we select stronger modeling features and add RAG/news.
