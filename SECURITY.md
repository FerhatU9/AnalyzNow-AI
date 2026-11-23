# Security Policy

AnalyzNow AI is a local development and research application. It is not an authenticated public service, and is **not approved for public production deployment**.

## Supported scope

The maintainers review security issues in the latest `main` branch. There is no established production support period or security service-level agreement.

## Reporting a vulnerability

Do not disclose working exploit details, API keys, database credentials or sensitive information in public issues or pull requests. Contact the repository owner privately using available GitHub profile contact methods. If GitHub private vulnerability reporting has been enabled for this repository, use that channel instead. Do not assume it is enabled.

When reporting, include affected commit, reproducible steps (with redacted secrets), observed behavior and potential impact. The maintainer will triage the report before discussing disclosure.

## Security boundaries

- The FastAPI and Next.js servers are intended for **loopback-only local use** and should not be exposed directly to the internet.
- The market-odds endpoint can spend third-party API quota and is **not rate-limited or authenticated**; do not expose it publicly.
- Secrets belong only in local environment variables or a secure deployment secret store; never commit `.env`, credentials, or database dumps.
- Published source code must not include proprietary or licensed bookmaker feeds.
- Before any public hosting, introduce authentication where appropriate, abuse controls, request quotas, secure configuration, monitoring and an explicit privacy review.

See [Security Review](docs/SECURITY_REVIEW.md) and the [Public Release Checklist](docs/PUBLIC_RELEASE_CHECKLIST.md).
