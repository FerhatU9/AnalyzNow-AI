# AnalyzNow AI — System Architecture

## Implemented local system

```mermaid
flowchart TD
  A[OpenFootball historical EPL results] --> B[Validation and provenance]
  B --> C[(PostgreSQL: teams and matches)]
  C --> D[Python Poisson forecasting engine]
  D --> E[FastAPI /v1/forecast]
  E --> F[Next.js server route]
  F --> G[React forecast dashboard]
  H[The Odds API] --> I[Odds normalization and bookmaker summary]
  I --> J[FastAPI /v1/market-odds]
  J --> M[Next.js /api/market-odds proxy]
  M --> N[On-demand market dashboard]
  K[Walk-forward backtest] -.-> D
  L[Pytest] -.-> E
  L -.-> J
```

**Important boundary:** A separate on-demand bookmaker-odds view is implemented on the feature branch, pending end-to-end verification. Historical forecasts and live market probabilities remain separate; the system does not blend their probabilities.

## Data model

`teams` stores a unique club name and generated identifier. `matches` stores the fixture date, references to the home and away clubs, and completed match scores. Uniqueness and nonnegative-score constraints help maintain integrity. The database currently represents completed results, not fixtures with kickoff timestamps, source revisions or multiple competitions.

The Python data access module requests only results with dates **strictly earlier** than the forecast cutoff. The forecast model computes expected goals and a distribution over likely scores, then derives home/draw/away and other goal probabilities.

## HTTP interfaces

- `POST /v1/forecast` accepts home team, away team and an optional historical cutoff date.
- `GET /v1/market-odds` retrieves current EPL bookmaker prices and converts them to margin-normalized 1X2 market probabilities.
- The Next.js frontend calls its local `/api/forecast` server route, which forwards requests to FastAPI.
- The new `/api/market-odds` server route forwards user-triggered bookmaker requests to FastAPI without exposing the provider API key in browser code.
- `GET /health` reports process status; it is not a full database or provider availability check.

## Engineering safeguards

- Forecasts use only data dated before their cutoff, avoiding same-day/future result leakage.
- LLMs must never invent or directly overwrite numerical model probabilities.
- Tests cover API behavior, mathematical functions, historical results, error handling and market-data responses.
- Bookmaker prices and timestamps must be treated as source data, not evidence of a guaranteed advantage.
- API keys and the PostgreSQL password are loaded from local environment configuration and must not be committed.

## Planned architecture

```mermaid
flowchart TD
  A[Licensed statistics and current fixtures] --> B[Validated data platform]
  C[Verified club and player news] --> D[Source verification]
  B --> E[Calibrated forecasting models]
  D --> F[Time-aware evidence retrieval / RAG]
  G[Historical bookmaker odds snapshots] --> H[Market evaluation]
  E --> I[Match analysis orchestration]
  F --> I
  H --> I
  I --> J[Citation and numerical consistency checks]
  J --> K[Versioned match reports and dashboard]
  L[Monitoring, audit logs and access controls] -.-> K
```

Additional planned capabilities include properly licensed current data, calibrated models, player availability, LangGraph research workflows, pgvector retrieval, saved forecasts, authentication and secure cloud deployment. These are **not** included in the current local application.
