# Browser verification with Playwright

Playwright runs **real Chromium browser tests** against the local AnalyzNow AI website. Its tests cover a labeled fictional-data forecast, unavailable team API, failed forecast API, and navigation to the Data Health and Model Quality pages.

## Development setup

First start the isolated Docker demonstration with Docker Desktop:

```powershell
docker compose -f compose.demo.yaml up -d --wait
```

The Playwright dependency is pinned in `frontend/package.json` and locked in `frontend/package-lock.json`. From the repository root, install it using the lockfile, download Chromium, and execute the suite:

```powershell
cd frontend
npm.cmd ci
npx.cmd playwright install chromium
npx.cmd playwright test
```

Run in headless mode by default. To inspect the visible Chromium browser:

```powershell
npx.cmd playwright test --headed
```

If the tests fail, preserve their output and share the exact failure. Do not edit their expected results merely to force a pass. They should run only against a local or isolated fictional-data backend, never an unapproved live service.

## Pull request requirement

**Local verification (2026-11-24):** Four Chromium browser tests passed against the user's running Docker demonstration. The tests verify forecast rendering, correctly labeled synthetic data, failed team API behavior, failed forecast API behavior, and dashboard navigation. GitHub Actions must independently pass `npm ci`, Chromium installation, isolated Compose startup, and the Playwright suite on the final pull-request head before merging.

The Docker stack must be shut down using `docker compose -f compose.demo.yaml down` when no longer needed. Never remove the PostgreSQL demo or historical volumes to address an unrelated browser failure.

## Limits

These smoke tests do not validate numerical forecasting accuracy, accessibility compliance, multiple browser engines, production hosting, bookmaker data or real team information.
