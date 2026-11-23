# AnalysNow AI — executable roadmap

Status after v0.2: Phase 1 initial research completed; a functioning portion of Phases 2-4 is implemented (local CSV validator, independent Poisson benchmark, backtest, FastAPI), **not** a finished phase, RAG system, or public product.

Every phase requires code review, unit/integration tests, reproducible evidence, and documentation before calling it complete.

| Phase | Deliverable | Depends on | Acceptance evidence | Status |
| --- | --- | --- | --- | --- |
| 1. Research/legal | Provider comparison, permissions register, first architecture | None | Written sources, approved data scope | Research draft; legal review pending |
| 2. Dev + coding agents | Windows setup, Git repo, Claude Code, Codex, agent rules | 1 | Reproducible setup; both agents make reviewed small changes | Instructions/files prepared; user-local install pending |
| 3. Data platform | Licensed ingestion, metadata, PostgreSQL, migrations, tests | 1,2 | Source rights recorded; repeatable import, rejects corrupt rows | OpenFootball CC0 importer + snapshot integrity tests implemented offline; user network fetch and PostgreSQL pending |
| 4. Baselines | Independent Poisson, Elo, Dixon-Coles, walk-forward evaluation | 3 | Holdout log loss/Brier + baselines + calibration/reproducibility | Independent-Poisson starter, synthetic smoke test only |
| 5. Advanced metrics | xG, strength correction, player metrics, calibrated ensemble | 4 + rights | Out-of-time comparison, confidence intervals, ablation tests | Not started |
| 6. Verified news | Credible sources, claim provenance, freshness, contradictions | 3 | Curated claim-verification benchmark; no unlabeled claims | Not started |
| 7. Production RAG | Licensed ingestion, pgvector hybrid retrieval, reranker | 6 | Citation accuracy and freshness thresholds achieved | Not started |
| 8. Match agent graph | Deterministic stats + verified news + RAG coordination | 4,6,7 | Tool-call controls; no LLM-created numerical probabilities | Not started |
| 9. Cited reports | Reports, scenario analysis, evidential QA, versioning | 8 | Curated factuality evaluation; source lineage | Not started |
| 10. App UX | FastAPI contract, React/Next.js dashboard | 4,9 | Auth/security, API contract tests, E2E flows | Local FastAPI sample only |
| 11. MLOps/automation | Scheduled data/news refresh, MLflow, drift monitoring | 3-10 | Forecast journal, alerts, incident runbook | CI test scaffold only |
| 12. Security/deploy | Docker, cloud, backups, access control, least privilege | 10-11 | Security review, recovery drill, working URL | Not started |
| 13. Production gate | Load/reliability/legal/cost review | All | End-to-end evidence + data/odds/news licenses + counsel | Not started |
| 14. Portfolio | Public-safe repo, demo, case study, interview walkthrough | Tested milestones | Reproducible demo, accurate CV claims | Starter README only |
| 15. Expansion | Other football leagues/sports or paid features | 13 | Separate validated sport model / permissions | Deferred |

## Milestone / dependency gates

- **M0 (now)**: project starter runs locally using synthetic data; passing code tests. Not predictive evidence.
- **M1 (next; offline adapter built)**: first licensed/authorized real-results dataset imported locally with a provenance manifest; documented date, league, competitions and source rights.
- **M2**: independent benchmark compared vs market-free baseline on a sufficiently sized holdout, with per-season and calibration plots and failures documented. Not necessarily better than baseline.
- **M3**: confirmed, independently verifiable news claims and retrieval can be tested against a curated set; no made-up links/players.
- **M4**: end-to-end cited report generated, all numbers checked, with original forecast snapshot locked.
- **M5**: operationally reproducible private deployment with monitoring, backups, security checks; legal signoff for any public/commercial service.

## Initial actionable backlog

1. On user's Windows machine, open project in VS Code, create virtual environment, install project and run 14+ tests.
2. Initial competition decided: EPL. Run the explicit OpenFootball CC0 fetch (not a scraper) on your Windows machine and inspect season completeness checks. See `docs/M1_REAL_DATA_GUIDE.md`.
3. Inspect automatically written source-provenance manifest with provider, URL, CC0 declaration, download time, season, exact source hashes and normalized CSV hash.
4. Run date-based walk-forward backtest and inspect sample size / comparison to naive baseline; never infer quality from synthetic-data results.
5. Add PostgreSQL schema + migration tool; include point-in-time snapshots.
6. Have Codex independently review leakage and CSV parser; have Claude Code implement typed provider adapter, or swap roles, reviewing diffs/test output.
7. Implement richer Dixon-Coles goal model after baseline results establish weaknesses.

## Proposed evaluation gates (targets, not achieved results)

- Statistical forecasts: report out-of-time log loss, multiclass Brier, RPS, calibration bins, grouped season/competition results, sample sizes, bootstrap intervals and baseline comparisons. Choose thresholds after an empirical initial evaluation; do not declare the model reliable from a single metric.
- Team news: manually create a multi-source claim gold set, measure precision, false confirmation rate and freshness; 100% source metadata required for material claims.
- RAG: material claims must have linked primary evidence or explicitly marked uncertainty; run retrieval-relevance and citation-audit tests on curated examples with dates.
- Software: each change passes unit tests and CI; deployment requires separate API-auth, data-rights, monitoring and security reviews.
