# AnalyzNow AI — Public Portfolio Release Checklist

The goal of this checklist is a credible **public source-code portfolio**, not a public hosted forecasting service. Any checked item must have evidence. Do not claim production security, commercial data rights or accurate betting recommendations.

## Verified in this development cycle

- [x] Product naming, dependency manifests and source tree are consistently organized in the active repository.
- [x] GitHub Actions passed Python tests for research PR #8 (initial head `07b0782`); developer-local full suite: **79 passed**, one non-blocking FastAPI deprecation warning.
- [x] GitHub Actions passed Next.js lint and production build for research PR #8; the developer also verified the new `/model-quality` page locally.
- [x] GitHub Actions full-stack smoke test passed on a fresh Ubuntu runner for PR #8: installs Python/npm dependencies, builds Next.js, starts FastAPI and Next.js locally, verifies team catalog consistency, sends a synthetic forecast through the API and frontend proxy, and checks probability totals and provenance labels. This does **not** independently verify rendered browser interactions.
- [x] The developer separately restored **1,520 historical matches** to the renamed local PostgreSQL database and passed **2 PostgreSQL integration tests**.
- [x] A no-provider-key, no-database demonstration is implemented using an explicitly labeled synthetic data file.
- [x] Synthetic team selection and API failures are covered by automated tests.
- [x] Documentation distinguishes historical statistical forecasts, fictional demo results and live market probabilities. The Model Quality page displays aggregate 2024/25 exploratory and 2025/26 frozen-setting evaluation metrics, not live predictions.
- [x] Developer-local browser test on 2026-11-23: the team catalog loaded, Demo City vs Demo East forecast rendered with cutoff 2025-07-19, expected goals 1.60/1.00 and outcome probabilities 51.3%/25.0%/23.7%. The synthetic-data label was visible. This verifies the tested local environment, **not** a fresh checkout.

## Required before public visibility

- [ ] Independently run the documented browser walkthrough from a fresh checkout. The full-stack HTTP workflow has passed CI on a clean runner, but manual browser interaction on a separate environment has not yet been verified.
- [ ] Verify the existing market dashboard feature separately against the real backend. Test successful data, empty fixtures, missing API key and provider failure without publishing licensed bookmaker data.
- [ ] Review current branches **and reachable Git history** for API keys, PostgreSQL passwords, environment files, private outputs and unlicensed datasets. Gitleaks v8.30.1 completed a reachable-history scan of 46 commits (~854 KB) without findings on 2026-11-23; manual data/secret checks and unreachable-history considerations still remain. Git ignore rules alone do not remove earlier commits.
- [x] On the initial research PR #8 head (`07b0782`), GitHub Actions dependency security completed successfully for Python and npm, and Gitleaks passed. These automated audits are not a comprehensive security review; recheck them after subsequent changes.
- [ ] Complete manual review of credential history, licensed datasets, provider terms and other sensitive material beyond automated scanning.
- [ ] Confirm upstream football data licenses and whether additional attribution, branding or redistribution restrictions apply to anything included publicly.
- [ ] Validate a clean-checkout setup on a second machine or isolated environment, without reliance on a developer's existing PostgreSQL volume.
- [ ] Ensure the main README matches the **merged** default branch and accurately labels all planned features. Draft PR #8 updates its descriptions; merge and recheck before public release.
- [ ] Merge reviewed pull requests after required checks, rather than publishing code from an unmerged branch.
- [ ] Review GitHub repository description, pinned topics, license, issue/reporting expectations and a real screenshot or short demonstration captured from a tested build.

## Product limitations to disclose

- The model is a recency-weighted independent-Poisson research baseline; historic backtest scores do not prove future predictive performance.
- The default database example covers 2021/22–2024/25; separate local 2025/26 historical matches support research metrics. Neither demonstrates current-season form.
- The bundled CSV is deliberately fictional and does not support any real-world accuracy claim.
- Commercial odds usage and republishing require confirmation of provider contract terms.
- Public hosted deployment, authentication, monitoring, user data management, market/model alignment and commercial operations are not yet implemented.

## Readiness decision

**Current decision: private; public portfolio approval pending the unchecked gates above.**

Draft PR #8 contains the model-research and Model Quality milestones. Its original head passed full-stack HTTP CI, frontend checks, Python tests, dependency audits and history scanning. These checks must be reconfirmed for the latest documentation commits. Independent clean-checkout research regeneration, separate market-feature review, browser verification, and manual data-rights/secrets review remain outstanding.
