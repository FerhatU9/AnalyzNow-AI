# AnalyzNow AI — Web Application

The AnalyzNow AI web application uses **Next.js, React, TypeScript and Tailwind CSS**. It provides the match-selection interface, renders model forecasts, and uses a server-side Next.js route to communicate with the Python forecasting API.

## Run locally

1. Start PostgreSQL and FastAPI as described in the [main README](../README.md).
2. Create `frontend/.env.local` with `FOOTBALL_API_URL=http://127.0.0.1:9011`.
3. In a PowerShell terminal:

```powershell
cd frontend
npm.cmd ci
npm.cmd run lint
npm.cmd run dev -- --hostname 127.0.0.1 --port 3011
```

Open http://127.0.0.1:3011.

## Application structure

- `src/app/page.tsx` — interactive forecasting page.
- `src/app/api/forecast/route.ts` — server-side proxy for `POST /v1/forecast`.
- `src/app/api/teams/route.ts` — server-side team catalog and dataset metadata proxy.
- `src/app/globals.css` — application styling.
- `src/app/layout.tsx` — shared page layout.

## Current scope

The interface provides dataset-aware home/away team selectors, a historical cutoff date, expected goals, match-outcome probability bars and likely scorelines. If the team API is unavailable, forecast controls remain disabled and a connection error is displayed. The bookmaker-odds endpoint is available from FastAPI, but has **not yet been added to this dashboard**.

The available teams come from the configured backend data source. For the fictional local demonstration, see [Reproducible Demo](../docs/DEMO.md). The interface is intended for **local development**; public deployment, authentication and full accessibility audits are future work. Four Playwright Chromium end-to-end tests have passed locally against the isolated Docker demonstration; see [Browser Testing](../docs/BROWSER_TESTING.md).

See the [system architecture](../docs/ARCHITECTURE.md) and [development roadmap](../docs/ROADMAP.md).
