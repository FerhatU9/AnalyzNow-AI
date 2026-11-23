# AnalyzNow AI — Public Portfolio Release Checklist

The goal of this checklist is a credible **public source-code portfolio**, not a public hosted forecasting service. Any checked item must have evidence. Do not claim production security, commercial data rights or accurate betting recommendations.

## Verified in this development cycle

- [x] Product naming, dependency manifests and source tree are consistently organized in the active repository.
- [x] GitHub Actions passed **39 Python tests** on the demo feature branch.
- [x] GitHub Actions passed Next.js lint and production build on the demo feature branch.
- [x] The developer separately restored **1,520 historical matches** to the renamed local PostgreSQL database and passed **2 PostgreSQL integration tests**.
- [x] A no-provider-key, no-database demonstration is implemented using an explicitly labeled synthetic data file.
- [x] Synthetic team selection and API failures are covered by automated tests.
- [x] Documentation distinguishes historical statistical forecasts, fictional demo results and live market probabilities.
- [x] Developer-local browser test on 2026-11-23: the team catalog loaded, Demo City vs Demo East forecast rendered with cutoff 2025-07-19, expected goals 1.60/1.00 and outcome probabilities 51.3%/25.0%/23.7%. The synthetic-data label was visible. This verifies the tested local environment, **not** a fresh checkout.

## Required before public visibility

- [ ] Independently run the instructions in [Reproducible Local Demo](DEMO.md) from a fresh checkout. Verify that team selectors load, two fictional clubs can be selected, and a forecast is displayed with the correct synthetic-data warning.
- [ ] Verify the existing market dashboard feature separately against the real backend. Test successful data, empty fixtures, missing API key and provider failure without publishing licensed bookmaker data.
- [ ] Review current branches **and reachable Git history** for API keys, PostgreSQL passwords, environment files, private outputs and unlicensed datasets. Git ignore rules alone do not remove earlier commits.
- [ ] Perform an explicit dependency security review for Python and npm; investigate actionable issues and record what was checked.
- [ ] Confirm upstream football data licenses and whether additional attribution, branding or redistribution restrictions apply to anything included publicly.
- [ ] Validate a clean-checkout setup on a second machine or isolated environment, without reliance on a developer's existing PostgreSQL volume.
- [ ] Ensure the main README matches the **merged** default branch and accurately labels all planned features.
- [ ] Merge reviewed pull requests after required checks, rather than publishing code from an unmerged branch.
- [ ] Review GitHub repository description, pinned topics, license, issue/reporting expectations and a real screenshot or short demonstration captured from a tested build.

## Product limitations to disclose

- The model is a recency-weighted independent-Poisson research baseline; historic backtest scores do not prove future predictive performance.
- Completed Premier League match results cover 2021/22–2024/25 and do not represent 2026 team form.
- The bundled CSV is deliberately fictional and does not support any real-world accuracy claim.
- Commercial odds usage and republishing require confirmation of provider contract terms.
- Public hosted deployment, authentication, monitoring, user data management, market/model alignment and commercial operations are not yet implemented.

## Readiness decision

**Current decision: private; public portfolio approval pending the unchecked gates above.**

The active demo branch improves accessibility for a reviewer, but passing automated tests alone does not establish a usable clean-checkout demo or a completed security and data-rights review.
