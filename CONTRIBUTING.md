# AnalyzNow AI — Contribution Standards

This repository represents a working software product under development. Make changes that can be understood, tested and reproduced. Do not manufacture commits, claims, metrics or demonstrations to make the history look more active.

## Naming and presentation

- Use **AnalyzNow AI** for the product, interface, documentation titles and GitHub descriptions.
- Use `analyznow-ai` for package identifiers and `analyznow` for corresponding local database identifiers after their migration.
- Give source files and folders meaningful technical names that describe their roles (for example `market_odds.py` and `docs/DATA_PIPELINE.md`).
- Do not name files or sections using temporary stage labels such as starter, draft, or cosmetic revision tags. Keep valid dependency/model versions where they are technically necessary.
- Remove unused framework template assets and stale setup instructions when replacing them.

## Engineering workflow

1. Describe the change, its expected behavior and any data/security implications.
2. Work on a focused Git branch; preserve `main` until the change is reviewed.
3. Implement the feature or fix with suitable tests and clear error handling.
4. Run the relevant local checks and review the staged diff for credentials or unintended files.
5. Open a pull request with a factual summary, validation evidence and known limitations.
6. Verify GitHub Actions; merge only after the required compatibility or migration checks.
7. Use concise, change-specific commit messages, for example `AnalyzNow AI: Add fixture matching tests`. Do not make empty commits simply to increase contribution counts.

### Local checks

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
```

From `frontend/`:

```powershell
npm.cmd run lint
npm.cmd run build
```

A successful local build does not replace a database integration test or deployment verification. Tests that depend on PostgreSQL require a healthy local database and are run separately.

## Documentation required for every verified milestone

Update documentation **in the same pull request as the implemented milestone**:

| Change | Documentation to update |
| --- | --- |
| New functionality, setup change, user-facing interface | `README.md`, and `frontend/README.md` where relevant |
| New endpoint, component, service or data flow | `docs/ARCHITECTURE.md` |
| New provider, dataset, transformation, schema or rights restriction | `docs/DATA_PIPELINE.md` and relevant provenance notes |
| Validated model or evaluation change | `README.md` with data window, sample size, baselines, methodology and limitations |
| Milestone completion, changed priorities or known blockers | `docs/ROADMAP.md` |
| Environment variable added or changed | `.env.example` with placeholders only |

Documentation updates must reflect what was actually run and verified, not what is only planned. Never commit real API keys, passwords, private data, generated builds, model claims without evidence or third-party data without appropriate permissions.

## Readiness gates

- **Local implementation complete:** targeted tests pass and behavior can be demonstrated locally.
- **Repository review complete:** documentation accurately matches the source, CI passes, no sensitive data is tracked, and clean-checkout setup is reproducible.
- **Public portfolio ready:** the application has a clear, usable demonstration, credible test evidence, honest model limitations, a consistent product identity and reviewed repository history.
- **Commercial deployment ready:** requires additional security, authentication, operational monitoring, data licensing, reliability, recovery and legal review.

A private GitHub repository with passing tests is a positive engineering milestone, not by itself evidence of public or commercial readiness.
