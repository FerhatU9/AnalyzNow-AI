# Codex repository instructions

This repository is a statistics-first football research application. It is NOT production ready.

- Never fabricate sport statistics, claims, external data permissions, test results, or probabilities.
- Ensure a forecast is trained ONLY on results available prior to forecast cutoff. The current implementation supports date-only cutoff, strictly earlier days.
- LLMs may summarize verified source material, but NEVER directly overwrite model-generated probabilities.
- No automatic scraping, real-money placement, gambling affiliate marketing, or paid-license assumptions.
- Do not commit .env, user accounts, secrets, downloaded sports-data, or provider content without permission.
- Keep changes small; add automated tests; run pytest and show evidence before claiming success.
- Do not deploy or execute destructive commands without explicit user approval.
- Use `docs/ROADMAP.md` for upcoming work, `docs/ARCHITECTURE.md` for contracts.
