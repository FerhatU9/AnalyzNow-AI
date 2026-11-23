# AnalyzNow AI — Development Roadmap

This roadmap distinguishes **locally verified work** from work still under development. Acceptance requires a repeatable run, passing relevant tests, reviewed changes and an accurate description of limitations.

| Workstream | Current result | Next acceptance gate |
| --- | --- | --- |
| Environment and tooling | Python, Node.js, Docker, VS Code and Git configured locally | Setup reproducible from a clean checkout |
| Historical data ingestion | Four completed EPL seasons downloaded and imported; 1,520 results stored | Source provenance review and independent score sampling |
| Forecasting baseline | Weighted independent-Poisson model working; walk-forward evaluation on 760 fixtures | Calibration analysis, stronger baselines and leakage review |
| PostgreSQL integration | Renamed local PostgreSQL database restored from backup with 1,520 matches confirmed | Re-run database-dependent tests and verify FastAPI and frontend against the migrated database |
| API and dashboard | FastAPI and React/Next.js historical forecasts demonstrated | Team dropdowns, data validation, frontend tests and accessible UX |
| Market data | Live EPL odds retrieval and `/v1/market-odds` endpoint; 35 standard tests passed | Store timestamped odds and build dashboard display |
| Model-versus-market comparison | Not implemented | Exact fixture matching and point-in-time data alignment |
| GitHub and CI | Private repository, with Python and frontend CI jobs passing on the branding branch | Confirm safe database migration, review secrets and keep documentation current |
| Verified news and RAG | Not implemented | Source licensing, fact verification and retrieval benchmark |
| AI match analysis | Not implemented | Grounded summaries with audited citations and fixed model probabilities |
| Deployment and operations | Not implemented | Authentication, security, monitoring, backups and licensing review |

## Documentation updates at each milestone

Every completed milestone is accompanied by documentation changes in the same pull request. Update the main README for user-visible features and setup, architecture notes for component or API changes, data documentation for source/schema changes, and this roadmap for verified status and outstanding work. Record test results and limitations without calling unverified work complete. See [Contribution Standards](../CONTRIBUTING.md).

## Immediate development priorities

1. Maintain clean, current documentation and reviewed Git commits.
2. Add the bookmaker-odds endpoint to the Next.js dashboard without mixing incompatible prediction dates.
3. Replace free-text team names with a validated list from PostgreSQL.
4. Record bookmaker source, event ID, timestamps and odds snapshots; ensure no stale or mismatched data drives comparisons.
5. Update current match results and evaluate statistical-only, market-only and combined estimates on point-in-time historical snapshots.
6. Introduce repeatable migrations, CI verification, frontend tests and clearer API contracts.

## Future research and engineering

- Improve statistical forecasting with Elo, Dixon-Coles, xG features and rigorously evaluated ensemble candidates when suitable data rights permit.
- Add verified team news, player availability and contextual match intelligence.
- Implement time-aware RAG, LangGraph-based research orchestration and source-grounded reports.
- Add monitoring, model tracking, rate limits, authentication and secure hosting.
- Evaluate public usability and commercial licensing only after legal, data-security and reliability reviews.

## Project readiness

The application is **under active development**. Working local functionality is not equivalent to a public production service or a validated betting product. The private GitHub repository may be developed incrementally; a public portfolio milestone requires clean documentation, secret scanning, passing CI, reproducible setup and a usable demonstration.
