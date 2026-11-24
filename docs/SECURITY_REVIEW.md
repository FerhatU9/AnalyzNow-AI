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
- [x] Gitleaks v8.30.1 passed on GitHub Actions on 2026-11-23 (run 45223539407). The job reported **46 commits scanned, ~854 KB, no leaks found**. This covers history reachable from fetched Git references only; it may miss unreachable objects from previous force pushes, GitHub-owned pull refs not fetched, and credentials outside the repository. A manual historical-data and sensitive-file inspection is still outstanding.
- [x] Inspect tracked-file trees for **all nine branches** accessible on 2026-11-24 (including `main`, research and market branches). GitHub's recursive trees were complete, and the inspection found no tracked `.env` secret files, database dumps, private keys or raw external football-result datasets. Only the declared `.env.example`, fictional demo CSV, template manifest and aggregate dashboard JSON appeared in the research/market branch file inventories. This is a **filename/inventory check**, not an inspection of all file contents or unreachable historical Git objects.
- [x] On 2026-11-24, review GitHub-visible changes across **all nine branch histories** (78 distinct reachable commits). A focused examination of commit metadata and available changed-line patches found no high-confidence private-key markers, known API-token formats or password-bearing URLs. Filenames flagged as sensitive were `.env.example` templates, not tracked real `.env` files. Twelve changed-file entries had no text patch: lockfile additions, binary favicon files and zero-content-change renames. The current `.env.example`, `.gitignore`, security workflow and development odds route were also inspected. **This is a targeted manual review, not proof that all arbitrary secrets or sensitive information are absent.**
- [ ] Verify historical file contents, ignored local files and unreachable Git objects as appropriate before changing repository visibility; `.gitignore` does not erase secrets from history.
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

**Upstream license and provider-terms check (2026-11-24):** OpenFootball's `football.json` repository publishes `LICENSE.md` under CC0 1.0. The Odds API's published terms allow data use in user-facing dashboards but prohibit reselling/repackaging it as a standalone raw-data product or feed. This is not authorization for a publicly hosted unauthenticated market-data API; provider-account terms and any rights related to the intended live deployment still require review. No live provider prices or credentials appeared in the inspected tracked-file inventories. These observations do not constitute legal advice.
