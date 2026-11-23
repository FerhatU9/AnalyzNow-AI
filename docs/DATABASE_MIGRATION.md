# AnalyzNow AI — Local Database Migration

This guide preserves the historical Premier League dataset while moving a local PostgreSQL installation to the updated application identity. It is **not** part of the GitHub-hosted application: database operations must run on the machine where Docker Desktop stores the data.

## Before you begin

- Keep the original Docker volume. Never run `docker compose down -v`.
- Verify that your existing PostgreSQL dump has nonzero size and store it outside the repository.
- Save a separate copy of your private `.env` locally; do not commit it.
- Stop local FastAPI and Next.js servers during the migration.
- Perform the migration only after reviewing the proposed Git changes.

## 1. Verify the backup

From the project root in PowerShell:

```powershell
Get-Item ..\AnalyzNow_AI_database.dump | Select-Object Name, Length
```

The file must exist and be nonempty. If it is missing, use the **original working Compose configuration** and database credentials to create a fresh `pg_dump -Fc` before updating Docker configuration.

## 2. Start the updated database

The new Compose project identifier creates a separate Docker volume. The original volume remains untouched.

```powershell
docker compose up -d
docker compose ps
```

Wait until the service reports `healthy`. The new PostgreSQL database and user are both named `analyznow`. The PostgreSQL password is read from the existing local `.env`.

## 3. Restore the preserved data

```powershell
docker compose cp ..\AnalyzNow_AI_database.dump postgres:/tmp/analyznow_db.dump
docker compose exec -T postgres pg_restore -U analyznow -d analyznow --no-owner --no-acl --exit-on-error /tmp/analyznow_db.dump
docker compose exec -T postgres psql -U analyznow -d analyznow -c "SELECT COUNT(*) FROM matches;"
```

**Developer-local checkpoint:** a restore to the renamed `analyznow` database completed and `SELECT COUNT(*) FROM matches;` returned **1,520**. Application integration and browser verification are still pending.

The previously imported four Premier League seasons should contain **1,520 matches**. If restoring fails because tables already exist, stop and inspect the new database; do not automatically erase volumes or rerun destructive commands.

## 4. Verify the application

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pytest -q tests/integration_postgres.py
```

Start the FastAPI server only after PostgreSQL checks succeed. Keep the original database backup and volume until successful API and frontend tests have been completed.

## Notes

- Existing local configuration values and credentials are private and must not be uploaded to GitHub.
- The GitHub repository rename and code rename do **not** migrate a Docker database automatically.
- Recreating a new empty database is not the same as restoring historical results.
- This document describes a local migration procedure; it is not evidence that the migration has been completed on another machine.
