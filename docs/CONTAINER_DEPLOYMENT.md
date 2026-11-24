# AnalyzNow AI — Containerized Demonstration

This is an **isolated local demonstration** of the complete application: PostgreSQL, a one-time fictional-results loader, FastAPI and Next.js. It does not connect to the existing historical PostgreSQL volume or download real results. It is not a publicly hosted or production-hardened service.

## Requirements

- Docker Desktop with Linux containers and Docker Compose v2
- Repository checkout on the `feature/full-stack-containers` branch until the pull request is merged
- A local `.env` containing `POSTGRES_PASSWORD` (never commit this file)

From the repository root in PowerShell:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `.env` and set a strong local `POSTGRES_PASSWORD` value. If you already have a working `.env`, **do not replace or reset it**. The isolated demonstration uses a separate database and volume, but obtains its demo password from that local file.

## Start all services

```powershell
docker compose -f compose.demo.yaml config --quiet
docker compose -f compose.demo.yaml up --build -d --wait
docker compose -f compose.demo.yaml ps
```

Open the dashboard at http://127.0.0.1:3011 and the API reference at http://127.0.0.1:9011/docs. The fictional team catalog is labeled **Synthetic demonstration data**. Select different Demo teams and click **Generate Forecast**. The same fictional-only warnings and data-freshness information should be visible.

The dashboard's Next.js server communicates with FastAPI over Docker's internal network at `http://api:9011`. FastAPI accesses PostgreSQL at `postgres:5432`. Only dashboard port 3011 and API port 9011 are exposed, bound to local `127.0.0.1`. The demo database itself is **not** exposed on a host port.

## Verify and stop

```powershell
.\.venv\Scripts\python.exe scripts/verify_demo.py
docker compose -f compose.demo.yaml down
```

Alternatively, with Python installed and on your PATH, run `python scripts/verify_demo.py`. The checker must report a successful synthetic forecast across the API and Next.js proxies.

`down` stops and removes the demo containers but **preserves** the demo database volume. Do **not** use `down -v` while investigating data, and do not use this workflow to restore or modify the existing historical PostgreSQL volume. The main `compose.yaml` remains unchanged.

## How the data is protected

- The demo runs under a separate Compose project `analyznow-ai-demo` with its own database, user and named volume.
- The seeder refuses to run unless `FOOTBALL_DEMO_SEED=1` and `POSTGRES_DB=analyznow_demo`; it refuses unexpected existing database records rather than replacing them.
- The fictional CSV is supplied from the repository. No bookmaker API calls or real football dataset downloads are part of startup.
- Docker builds exclude local `.env`, caches, external data, backup files and generated output through `.dockerignore`.
- Containerization does **not** provide authentication, rate limiting, network hardening, image-vulnerability scanning, or cloud deployment. Never expose these demo services to the public internet.

## Troubleshooting

```powershell
docker compose -f compose.demo.yaml ps
docker compose -f compose.demo.yaml logs --tail=100 api web seed postgres
```

If your existing local API or dashboard already uses ports 9011 or 3011, stop those local processes before starting the containers. The Docker Compose demo deliberately uses the familiar application ports to make the existing smoke test reusable. If Compose cannot start, **do not remove Docker volumes as a fix**. Review the error and share the relevant logs.

## Verification status

**Verified 2026-11-24:** GitHub Actions successfully built and started the isolated container stack and passed the synthetic HTTP smoke test. The developer independently confirmed on Windows/Docker Desktop that PostgreSQL, FastAPI and Next.js reported healthy and that `python scripts/verify_demo.py` passed. An existing local API/UI port conflict was resolved by stopping the two previously running development servers; the existing historical database and other Docker services were not changed. This is local/demo readiness, **not** public hosting or production security verification.
