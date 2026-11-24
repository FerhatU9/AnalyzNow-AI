# AnalyzNow AI — Development Roadmap

This roadmap distinguishes **locally verified work** from work still under development. Acceptance requires a repeatable run, passing relevant tests, reviewed changes and an accurate description of limitations.

| Workstream | Current result | Next acceptance gate |
| --- | --- | --- |
| Environment and tooling | Python, Node.js, Docker, VS Code and Git configured locally | Synthetic demonstration reproduced from a separate clean checkout; keep release setup instructions current |
| Historical data ingestion | Four EPL seasons restored to local PostgreSQL (1,520 results); separate five-season OpenFootball snapshot used for later-season research | Fresh-download 2024/25 and 2025/26 research checks reproduced; retain provenance and review rights before any wider data redistribution |
| Forecasting baseline | Poisson walk-forward model retained for application forecasts; Elo and 50/50 ensemble benchmarked on 2024/25 and frozen-config 2025/26 results (380 each) merged via PR #8 | Preserve historical reproducibility evidence; do not promote ensemble without convincing validation |
| PostgreSQL integration | Renamed local PostgreSQL database restored from backup with 1,520 matches confirmed | Re-run database-dependent tests and verify FastAPI and frontend against the migrated database |
| API and dashboard | Synthetic forecasting and dataset-aware team selectors; Model Quality dashboard merged in PR #8; forecast freshness/coverage and Data Health dashboard merged in PR #9. Local browser tests verified the forecast warning, Data Health display and backend-unavailable error; 88 local Python tests and six PR CI/security jobs passed | Maintain stable warnings and test coverage; do not claim updated PR #9 clean-checkout browser testing |
| Market data | On-demand EPL odds endpoint and margin normalization; separate market-dashboard feature is draft PR #5 (not merged) | Verify integration, error handling and provider licensing before any merge or public exposure |
| Model-versus-market comparison | Not implemented | Exact fixture matching and point-in-time data alignment |
| GitHub and CI | Private repo; PRs #8 and #9 merged, and all six PR #9 CI/security jobs passed at commit `9208e70` on 2026-11-24 | Recheck CI on the release-documentation PR and finish manual security/data-rights review before public-source release |
| Verified news and RAG | Not implemented | Source licensing, fact verification and retrieval benchmark |
| AI match analysis | Not implemented | Grounded summaries with audited citations and fixed model probabilities |
| Deployment and operations | Not implemented | Authentication, security, monitoring, backups and licensing review |

## Documentation updates at each milestone

Every completed milestone is accompanied by documentation changes in the same pull request. Update the main README for user-visible features and setup, architecture notes for component or API changes, data documentation for source/schema changes, and this roadmap for verified status and outstanding work. Record test results and limitations without calling unverified work complete. See [Contribution Standards](../CONTRIBUTING.md).

## Immediate development priorities

1. Complete manual repository-history, secrets, data-rights and security review before changing repository visibility, including scrutiny of other branches and pull-request history.
2. Align public-source release documentation with the merged `main` branch; capture a real application screenshot and review repository description, topics, license and disclosure of limitations.
3. Keep the provider-dependent market dashboard in draft PR #5 and outside the initial public-source feature scope; note that separate private-branch content will still become visible if the repository is made public.
4. Review the release-documentation pull request and verify passing CI on its final head.
5. Add targeted frontend tests, accessibility checks and a documented model-monitoring refresh workflow.
6. Develop time-aligned market/model comparisons only after acquiring properly licensed historical odds snapshots.

## Future research and engineering

- Investigate calibration and stability of the evaluated Elo/Poisson ensemble; consider Dixon–Coles and xG only with robust out-of-sample evidence and appropriate data rights.
- Add verified team news, player availability and contextual match intelligence.
- Implement time-aware RAG, LangGraph-based research orchestration and source-grounded reports.
- Add monitoring, model tracking, rate limits, authentication and secure hosting.
- Evaluate public usability and commercial licensing only after legal, data-security and reliability reviews.

## Project readiness

The application is **under active development**. For an evidence-based portfolio publication review see [Public Release Checklist](PUBLIC_RELEASE_CHECKLIST.md). Working local functionality is not equivalent to a public production service or a validated betting product. The private GitHub repository may be developed incrementally; a public portfolio milestone requires clean documentation, secret scanning, passing CI, reproducible setup and a usable demonstration.
