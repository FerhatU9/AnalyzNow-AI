# Browser verification with Playwright

Playwright runs **real Chromium browser tests** against the local AnalyzNow AI website. Its tests cover a labeled fictional-data forecast, unavailable team API, failed forecast API, and navigation to the Data Health and Model Quality pages.

## Development setup

First start the isolated Docker demonstration with Docker Desktop:

```powershell
docker compose -f compose.demo.yaml up -d --wait
```

In the `frontend` directory, install the test runner and download its browser:

```powershell
cd frontend
npm.cmd install --save-dev --save-exact @playwright/test@1.65.1
npx.cmd playwright install chromium
npx.cmd playwright test
```

Run in headless mode by default. To inspect the visible Chromium browser:

```powershell
npx.cmd playwright test --headed
```

If the tests fail, preserve their output and share the exact failure. Do not edit their expected results merely to force a pass. They should run only against a local or isolated fictional-data backend, never an unapproved live service.

## Pull request requirement

The development branch initially contains the test specification and runner configuration only. Installing the pinned dev dependency updates **both** `frontend/package.json` and `frontend/package-lock.json`; commit both files together. GitHub Actions must then run `npm ci`, install Chromium with OS dependencies, start the isolated Compose stack, and execute Playwright successfully before the feature is approved.

The Docker stack must be shut down using `docker compose -f compose.demo.yaml down` when no longer needed. Never remove the PostgreSQL demo or historical volumes to address an unrelated browser failure.

## Limits

These smoke tests do not validate numerical forecasting accuracy, accessibility compliance, multiple browser engines, production hosting, bookmaker data or real team information.
