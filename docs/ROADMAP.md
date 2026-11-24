# AnalyzNow AI — Development Roadmap

This roadmap distinguishes **locally verified work** from work still under development. Acceptance requires a repeatable run, passing relevant tests, reviewed changes and an accurate description of limitations.

| Workstream | Current result | Next acceptance gate |
| --- | --- | --- |
| Environment and tooling | Python, Node.js, Docker, VS Code and Git configured locally | Setup reproducible from a clean checkout |
| Historical data ingestion | Four EPL seasons restored to local PostgreSQL (1,520 results); separate five-season OpenFootball snapshot used for later-season research | Independently reproduce source snapshot and verify data-use rights |
| Forecasting baseline | Poisson walk-forward model retained for application forecasts; Elo and 50/50 ensemble benchmarked on 2024/25 and frozen-config 2025/26 results (380 each) in draft PR #8 | Independently reproduce research journals; do not promote ensemble without convincing validation |
| PostgreSQL integration | Renamed local PostgreSQL database restored from backup with 1,520 matches confirmed | Re-run database-dependent tests and verify FastAPI and frontend against the migrated database |
| API and dashboard | Synthetic forecasting and dataset-aware team selectors; Model Quality dashboard and navigation in draft PR #8; full-stack smoke, lint and build passed CI for the research branch | Validate clean-checkout browser behavior, data-page refresh and accessibility |
| Market data | On-demand EPL odds endpoint and margin normalization; separate market-dashboard feature is draft PR #5 (not merged) | Verify integration, error handling and provider licensing before any merge or public exposure |
| Model-versus-market comparison | Not implemented | Exact fixture matching and point-in-time data alignment |
| GitHub and CI | Private repo; draft PR #8 passed Python, frontend, full-stack demo, Python/npm dependency audits and Gitleaks on its initial code head | Recheck CI after documentation edits, review data rights and reconcile open PRs before public release |
| Verified news and RAG | Not implemented | Source licensing, fact verification and retrieval benchmark |
| AI match analysis | Not implemented | Grounded summaries with audited citations and fixed model probabilities |
| Deployment and operations | Not implemented | Authentication, security, monitoring, backups and licensing review |

## Documentation updates at each milestone

Every completed milestone is accompanied by documentation changes in the same pull request. Update the main README for user-visible features and setup, architecture notes for component or API changes, data documentation for source/schema changes, and this roadmap for verified status and outstanding work. Record test results and limitations without calling unverified work complete. See [Contribution Standards](../CONTRIBUTING.md).

## Immediate development priorities

1. Reproduce the Model Quality research reports from a clean external-data snapshot; retain provenance and avoid committing restricted data.
2. Run an independent clean-checkout browser walkthrough for synthetic forecasting and the Model Quality page.
3. Review both draft pull requests independently; keep the bookmaker panel separate from historical statistical forecasts.
4. Complete repository-history, secrets, licensing and security review before making source code public.
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
