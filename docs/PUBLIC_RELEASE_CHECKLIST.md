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

- [x] Independently run the synthetic browser walkthrough from a separate fresh checkout. On 2026-11-24, `AnalyzNow_Review` used FastAPI port 9021 and Next.js port 3021; browser screenshots showed the correct synthetic forecast (Demo City vs Demo East: expected goals 1.60/1.00 and 51.3%/25.0%/23.7% outcome probabilities) and the Model Quality page. This was a separate checkout on the same Windows computer, not an unrelated machine.
- [x] Keep the **market-dashboard UI** in draft PR #5, separate from the forecasting-focused public-source release. The existing backend odds route is for local development only and must not be exposed unauthenticated on the public internet.
- [ ] Before merging/deploying PR #5 separately, test successful data, empty fixtures, missing API key and provider failure without publishing proprietary bookmaker quotes.
- [x] Review tracked-file **inventories** across all nine reachable branch tips (2026-11-24): complete recursive GitHub trees contained no tracked `.env` secrets, private keys, database dumps or raw external match datasets. This is a current-tree check, not a guarantee about contents or prior commits.
- [ ] Finish historical-content and credential review across **reachable Git history**. Gitleaks v8.30.1 previously scanned 46 commits (~854 KB) without findings on 2026-11-23; the latest dependency/security workflow including secret-history scanning passed on 2026-11-24 for `6dd32d3`. Manual sensitive-content checks and unreachable-history considerations remain. Git ignore rules alone do not erase earlier commits.
- [x] On the initial research PR #8 head (`07b0782`), GitHub Actions dependency security completed successfully for Python and npm, and Gitleaks passed. These automated audits are not a comprehensive security review; recheck them after subsequent changes.
- [x] Re-run the **2025/26 held-out evaluation** on a separately downloaded OpenFootball snapshot (retrieved 2026-11-24): 1,900 completed matches from five seasons, with the source/processed file hashes verified. A new 2025/26 backtest produced 380 predictions across 114 match dates. Frozen Elo (K=32, home advantage=40), Poisson, and the 50/50 ensemble reproduced the previously published Brier, log-loss, accuracy, draw-probability and clustered uncertainty results. The developer kept the original reports unchanged by using `outputs/epl_release_check_evaluation.json` and `outputs/heldout_release_check.json`. This is a fresh **source download and local rerun**, not a separate-machine or independently fact-checked dataset validation.
- [x] Re-run the **2024/25 exploratory evaluation** using the separate `data/openfootball/epl_release_check_2025/` CSV and distinct output journals. On 2026-11-24, the developer reported 380 fixtures across 109 match dates; independently rerun Poisson Brier **0.594368**, Elo **0.590903**, ensemble **0.587464**, with matching prior log-loss, accuracy and match-day bootstrap uncertainty values. The test was exploratory and does not establish model superiority. A subsequent `verify-snapshot` screenshot confirmed `verified: true`, four seasons and 1,520 completed matches. Both seasons' local snapshot-integrity checks are now complete; upstream results have not been cross-checked independently.
- [x] Regenerate the committed Model Quality **aggregate** from existing local research journals: on 2026-11-24 the developer ran `scripts/export_model_quality.py --output outputs/recomputed_model_quality.json` and compared parsed JSON with `frontend/data/model-quality.json`; result: **MATCH**, covering 760 historical match observations. This is **not** an independent fresh-download regeneration of the underlying model forecasts.
- [x] Reviewed tracked-file trees on research PR #8 (85 files) and market PR #5 (61 files) on 2026-11-24. No tracked `.env` secrets, database dumps, private keys, or raw historical football result snapshots appeared in either tree. Tracked data comprises the explicitly fictional demo CSV, source-manifest template and aggregate dashboard JSON. This is a current-tree check, **not** a full Git-history or credential-rotation audit.
- [ ] Complete manual review of credential history, licensed datasets, provider terms and other sensitive material beyond automated scanning. **Progress (2026-11-24):** Reviewed changed-file patches from 78 distinct commits reachable from nine GitHub branch tips, inspected current configuration and security workflow, and found no high-confidence known secret patterns. `.env.example` templates, historical lockfiles, favicon binaries and rename-only entries were the expected exceptions. See `docs/SECURITY_REVIEW.md`. This does not cover arbitrary secret strings, ignored local files, unreachable Git objects or the provider account's private terms; the release gate remains open.
- [x] Review the **published** upstream source terms for a code-only portfolio: OpenFootball's `football.json` declares CC0 1.0; The Odds API's public terms permit dashboard use but restrict standalone raw-data resale. The repository does not track bookmaker prices or raw external match data. This is a published-terms review, not clearance of a specific commercial account or hosted market API.
- [ ] **Before live public hosting or odds redistribution (not required for publishing source alone):** review provider-account permissions and any applicable data/branding constraints, and implement authentication, rate limits and quotas.
- [x] Validate a clean checkout in an **isolated local folder** without relying on the existing PostgreSQL volume or API provider credentials. Both services ran against the synthetic CSV after a fresh Python/npm dependency installation; the independently run `verify_demo.py` script passed. A second physical machine has **not** been tested.
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

Latest observed PR #8 checks on 2026-11-24: Python tests, frontend checks, full-stack synthetic demo, Python/npm audits and Git-history Gitleaks checks all passed at head `d8eaac1`. These statuses must be reconfirmed after subsequent commits.

Draft PR #8 contains the model-research and Model Quality milestones. Its original head passed full-stack HTTP CI, frontend checks, Python tests, dependency audits and history scanning. These checks must be reconfirmed for the latest documentation commits. The **2025/26 historical results** were independently regenerated from a fresh source download on 2026-11-24. The 2024/25 exploratory research comparison now matches prior results. Both historical season comparisons and local snapshot-integrity checks are complete. The separate market-feature review, manual data-rights/secrets review, and release integration remain outstanding. The separate synthetic browser walkthrough was completed on 2026-11-24.
