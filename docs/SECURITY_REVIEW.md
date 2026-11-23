# AnalyzNow AI — Security and Release Review

## Scope and status

This checklist documents **verified security controls and remaining work**. A passing CI job does not constitute a penetration test or authorization for public deployment. This project targets a **public source-code portfolio** first, not an accessible production service.

## Dependency vulnerability checks

The [Dependency Security workflow](../.github/workflows/security.yml) runs on pull requests, changes to `main`, manual dispatch and a weekly schedule:

- `python -m pip_audit .` reviews known vulnerabilities in declared Python project dependencies and the resolved dependency tree.
- `npm audit --audit-level=high` audits the JavaScript dependency lockfile, including build tooling, and fails when high/critical advisories are reported.
- `gitleaks git --log-opts="--all" --redact=100` scans reachable Git references for potential committed secrets using the official Gitleaks v8.30.1 container. The checkout fetches full branch history, does not upload a raw findings report, and redacts detected values from logs.

Both use live vulnerability databases, which means results may change without code changes. Record actual GitHub Actions results before marking an audit successful. The audits do not inspect Docker base images, deployed infrastructure, configuration vulnerabilities or unreported flaws.

## Credential and repository-history review

- [ ] Examine every reachable branch and historical commit for accidental credentials, especially `.env`, `ODDS_API_KEY`, PostgreSQL passwords, cloud tokens, private keys and personal files.
- [ ] Confirm that the history-aware Gitleaks job passes on GitHub Actions and review its findings; record the scan revision and timestamp. The configured scan covers history reachable from fetched Git references, but may miss unreachable objects from previous force pushes, GitHub-owned pull refs, and credentials outside the repository.
- [ ] Verify ignored files are not tracked; `.gitignore` does not remove secrets from Git history.
- [ ] If any credential was ever exposed, rotate it at the provider first. Removing or rewriting Git history alone does not invalidate a compromised credential.
- [ ] Check local/generated outputs and historical dataset redistribution permissions.

## Branch and publication controls

- [ ] Protect `main` against deletion and force pushes; require passing `Python tests`, `Frontend checks`, `Full-stack synthetic demo`, and both dependency-audit jobs before merging.
- [ ] Use pull requests for changes to `main` and keep unreviewed feature branches outside the release.
- [ ] Keep the repository private until code, history, data rights and demonstration reviews have finished.

**Branch protection status (2026-11-23):** The owner created a rule matching `main` in GitHub's Branch settings, but GitHub explicitly labels it **Not enforced** for this private personal repository. Do not treat it as an active enforcement control. The integration lacks administration permission to change it. Use voluntary pull requests and check successful CI while private; confirm enforcement after any future plan/visibility change, before relying on the rule.

## Network and market API

- The current FastAPI service provides unauthenticated development routes.
- The on-demand odds route consumes third-party provider quota, is not rate-limited and must not be exposed as a public internet API.
- Current data is presented to a locally running dashboard. Provider data rights and the individual account plan must be checked before any public deployment or republication.
- [ ] Add authentication/authorization, rate limiting, quotas, environment isolation and operational monitoring **before public hosting**. These are **not** requirements for publishing code alone.

## Licensing and attribution

As checked 23 November 2026, [The Odds API Terms and Conditions](https://the-odds-api.com/terms-and-conditions.html) describe user-facing dashboards as supported uses, but restrict redistribution of their data as a standalone product or raw data service. This summary is not legal advice or permission for every subscription tier. Verify the account’s applicable terms, data-use scope and any retention requirements before deploying any public live-data feature.

OpenFootball source material is described in [Data Provenance](../data/README.md). The repository includes only an explicitly fictional demonstration dataset by default.
