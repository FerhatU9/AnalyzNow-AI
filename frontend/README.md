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
- `src/app/api/market-odds/route.ts` — on-demand bookmaker market proxy.
- `src/components/market-odds.tsx` — bookmaker market display with timestamps, empty results, and errors.
- `src/app/globals.css` — application styling.
- `src/app/layout.tsx` — shared page layout.

## Current scope

The interface provides dataset-aware home/away team selectors, a historical cutoff date, expected goals, match-outcome probability bars and likely scorelines. If the team API is unavailable, forecast controls remain disabled and a connection error is displayed. The separate Live Market Intelligence panel is included on the integration branch. It loads bookmaker prices only when requested, and its market probabilities must not be mistaken for model forecasts. Successful live-provider browser verification remains pending.

The available teams come from the configured backend data source. For the fictional local demonstration, see [Reproducible Demo](../docs/DEMO.md). The interface is intended for **local development**; public deployment, authentication, accessibility audits and end-to-end browser tests are future work.

See the [system architecture](../docs/ARCHITECTURE.md) and [development roadmap](../docs/ROADMAP.md).
