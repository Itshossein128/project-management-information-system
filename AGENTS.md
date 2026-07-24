# AGENTS.md

## Cursor Cloud specific instructions

Monorepo (pnpm workspace): `apps/web` (React Router 7 + Vite frontend) and `apps/api` (Django 4.2 + DRF backend — IPCAS Sprint 1–3+ domains; see `docs/ipcas-scope-map.md`). Standard commands live in `README.md` / `package.json` scripts; this section only covers non-obvious cloud caveats. The update script already runs `pnpm install` (against the npmjs registry), creates the API venv at `apps/api/.venv`, installs `requirements.txt` plus the pytest tooling (see below), creates `.env` from `.env.example` (with the local-dev overrides applied), and pins Django back to 4.2.11.

**Do not `pip install -r requirements-dev.txt` as-is.** It lists `django-debug-toolbar>=7.0.0`, which requires Django>=5.2 and silently upgrades the pinned `Django==4.2.11` (breaking the runtime). `django_debug_toolbar` is not actually referenced anywhere in the code. The update script instead installs only `pytest`/`pytest-django`/`pytest-cov` (the parts of `requirements-dev.txt` that are compatible with Django 4.2). If you ever run the full dev-deps install, re-pin afterward with `apps/api/.venv/bin/pip install --force-reinstall --no-deps Django==4.2.11`.

### Services (local Docker-less dev)

Docker is **not** available in the cloud VM, so the Docker-based commands (`pnpm db:up`, `docker compose up`, Traefik/MinIO/RabbitMQ/worker) do not run here. Postgres and Redis are installed natively instead and must be started manually each session.

| Service | Start command | Port | Notes |
|---------|---------------|------|-------|
| PostgreSQL | `sudo pg_ctlcluster 16 main start` | 5433 | Required; no SQLite fallback. Configured on 5433 to match `.env.example`. Role/db `ipcas`/`ipcas` already exist. |
| Redis | `sudo redis-server /etc/redis/redis.conf --daemonize yes` | 6379 | Required — Django `CACHES` uses `RedisCache` and login/auth endpoints are rate-limited via the cache. Without Redis those endpoints error. |
| Django API | `pnpm dev:api` | 8000 | Reads root `.env`; needs `DATABASE_URL`, Redis, and the venv. API is under `/api/v1/...`; docs at `/api/docs/`, schema at `/api/schema/`. |
| Web frontend | `pnpm dev:web` | 5173 | Vite dev server. |

**Do not use `pnpm dev`** in the cloud VM: it runs `pnpm db:up` (`docker-compose up -d postgres redis`) first, which fails without Docker. Run `pnpm dev:api` and `pnpm dev:web` separately against the native Postgres/Redis instead.

Optional/Docker-only services (RabbitMQ, MinIO, Celery worker, Traefik gateway) are not needed for core local dev — see the `.env` overrides below to disable them.

### Startup gotchas

- **Start Postgres and Redis before the API** on each fresh VM boot (neither is managed by systemd here). Commands are in the table above.
- **`.env` local-dev overrides:** the update script creates `.env` from `.env.example` with `AUDIT_LOG_ASYNC=false` (sync audit writes, no RabbitMQ needed) and `CELERY_TASK_ALWAYS_EAGER=true` (run tasks inline, no Celery worker needed) already applied. It only creates `.env` when one does not exist, so if you keep an older `.env` set these two by hand. Without them the app expects RabbitMQ (`:5672`) / a Celery worker. File-upload/storage endpoints still need MinIO (Docker-only) and are not exercisable locally.
- **npm registry:** the committed `.npmrc` points at the Liara mirror (`package-mirror.liara.ir`), which is unreachable from the cloud VM. Always install JS deps with `pnpm install --registry https://registry.npmjs.org/` (the update script already does this).
- **DB schema resets:** the schema uses UUID primary keys (blueprint schema). If migrations fail with errors like `relation "users" does not exist` (stale/incompatible migration history from an older checkout), drop and recreate the dev DB, then re-migrate: `sudo -u postgres psql -p 5433 -c "DROP DATABASE ipcas;" && sudo -u postgres psql -p 5433 -c "CREATE DATABASE ipcas OWNER ipcas;"`.
- **First-time DB setup:** on a fresh DB run `pnpm db:migrate` then `pnpm db:seed`. Seeding creates dev users (password `devpass123`), e.g. admin phone `+10000000001`, plus sample projects (Acme Construction, BuildCo).

### Checks / tests

- Typecheck: `pnpm typecheck` (runs `react-router typegen && tsc`). No ESLint/Biome config is present despite rules mentioning Biome. Note: `main` currently has pre-existing `tsc` errors in `apps/web/src/components/daily_reports/DailyReportForm.tsx` (`'c' is of type 'unknown'`), so this command exits non-zero regardless of the environment.
- Django tests use **pytest**, not `manage.py test`. The test files are pytest-style (fixtures + `@pytest.mark.django_db`), so `manage.py test` discovers 0 tests. Run: `cd apps/api/core && set -a && source /workspace/.env && set +a && ../.venv/bin/python -m pytest <path>` (config in `apps/api/core/pytest.ini`; e.g. `../.venv/bin/python -m pytest projects/tests`). Requires Postgres + Redis; `*_integration` modules additionally need RabbitMQ + MinIO which are Docker-only. Verify blueprint tables with `../.venv/bin/python manage.py verify_blueprint_schema` (needs `DATABASE_URL` sourced from `.env`).
- E2E: `pnpm e2e` (Playwright, root config). Its `webServer` auto-starts web + API (reuses running servers) but Postgres + Redis must be up first. Install browsers once with `pnpm exec playwright install --with-deps chromium` (cached in the snapshot; not in the update script).
