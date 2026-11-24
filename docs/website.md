# AnalyzNow AI — Public GitHub Pages showcase

A responsive, interactive showcase for the football intelligence and forecasting project.

**Live interactive showcase (verified 2026-11-24):** https://ferhatu9.github.io/AnalyzNow-AI/

This website is deliberately similar in scope to the ScoutMonitor AI GitHub Pages showcase. It provides a working fictional-team explorer and independent-Poisson forecast calculation in the visitor's browser, while the full FastAPI + PostgreSQL + Next.js application remains a separate project component.

## How the website works

- `docs/index.html` presents the product and the forecast lab.
- `docs/assets/site.css` provides responsive layouts and styling.
- `docs/assets/site.js` loads bundled CSV results, manages team selections, displays goal intensities, match outcome probabilities, scorelines and historical evidence.
- `docs/assets/forecast.mjs` contains a browser-side reproduction of the research baseline in `src/football_intel/model.py` using the same historical cutoff, 365-day half-life, team-strength shrinkage and independent-Poisson score grid.
- `docs/assets/matches.csv` is an exact copy of `data/synthetic_demo.csv`: 100 artificial results featuring six Demo clubs.

All model values originate from the fictional published CSV, not from fabricated arbitrary display figures. The site fetches only same-origin static assets; it does not make external football-data requests, execute Python or connect to private storage.

The browser-side calculations are **not** an additional validated model. The numerical output is compared with the existing Python model for multiple synthetic cases via `scripts/verify_pages_demo.py` and `.github/workflows/website.yml`. A passing test demonstrates code equivalence for those cases, not the reliability of real match predictions.

## Publish through GitHub Pages

An authorized repository administrator must enable Pages:

1. Open https://github.com/FerhatU9/AnalyzNow-AI/settings/pages
2. Under **Build and deployment**, choose **Deploy from a branch**.
3. Select **main** and the **/docs** folder, then click **Save**.
4. Once GitHub reports a successful Pages deployment, open https://ferhatu9.github.io/AnalyzNow-AI/
5. Verify the homepage displays, six fictional teams load, and choosing two different teams calculates a forecast. Check mobile layout and the GitHub link.

**Do not claim this URL is live until GitHub Pages confirms publication and the website can be opened.** Only then add its real URL to the README introduction and the GitHub repository's About → Website field.

## Run locally

Because `fetch()` generally requires HTTP rather than the local `file://` protocol, use a local web server:

```powershell
python -m http.server 8031 --directory docs
```

Open http://127.0.0.1:8031/ and test the demo. Stop the local web server with Ctrl+C.

Run the independent website parity test:

```powershell
python scripts/verify_pages_demo.py
```

Node.js 22 and Python 3.11+ are required for that cross-language verification. GitHub Actions independently runs the tests on a clean runner.

## What is and is not live

**Live on Pages, once published:** Fictional-data team selection, browser-generated probabilities, scorelines, model explanation, data-integrity disclosure, and architecture portfolio presentation.

**Not hosted on Pages:** FastAPI services, PostgreSQL, the Next.js application, external bookmaker odds, OpenTelemetry collection, live data ingestion, AI/LLM agents or user accounts.

The separate Azure deployment preparation in `docs/AZURE_DEPLOYMENT.md` remains an optional later path to hosting the actual backend-dependent app. Public GitHub Container Registry packages are build artifacts; they are not a website.

The model is a research baseline and is not validated for betting, commercial decision-making or real upcoming fixtures.
