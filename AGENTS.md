# AGENTS.md

## Cursor Cloud specific instructions

Monorepo (pnpm workspace): `apps/web` (React Router 7 + Vite frontend) and `apps/api` (Django 4.2 + DRF backend — IPCAS Sprint 1–3+ domains; see `docs/ipcas-scope-map.md`). Standard commands live in `README.md` / `package.json` scripts; this section only covers non-obvious cloud caveats. The update script already runs `pnpm install` (against the npmjs registry), creates the API venv at `apps/api/.venv`, installs `requirements.txt`, and creates `.env` from `.env.example`.

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
- **`.env` local-dev overrides:** after creating `.env` from `.env.example`, set `AUDIT_LOG_ASYNC=false` (sync audit writes, no RabbitMQ needed) and `CELERY_TASK_ALWAYS_EAGER=true` (run tasks inline, no Celery worker needed). Without these the app expects RabbitMQ (`:5672`) / a Celery worker. File-upload/storage endpoints still need MinIO (Docker-only) and are not exercisable locally.
- **npm registry:** the committed `.npmrc` points at the Liara mirror (`package-mirror.liara.ir`), which is unreachable from the cloud VM. Always install JS deps with `pnpm install --registry https://registry.npmjs.org/` (the update script already does this).
- **DB schema resets:** the schema uses UUID primary keys (blueprint schema). If migrations fail with errors like `relation "users" does not exist` (stale/incompatible migration history from an older checkout), drop and recreate the dev DB, then re-migrate: `sudo -u postgres psql -p 5433 -c "DROP DATABASE ipcas;" && sudo -u postgres psql -p 5433 -c "CREATE DATABASE ipcas OWNER ipcas;"`.
- **First-time DB setup:** on a fresh DB run `pnpm db:migrate` then `pnpm db:seed`. Seeding creates dev users (password `devpass123`), e.g. admin phone `+10000000001`, plus sample projects (Acme Construction, BuildCo).

### Checks / tests

- Typecheck: `pnpm typecheck` (runs `react-router typegen && tsc`). No ESLint/Biome config is present despite rules mentioning Biome.
- Django tests: `cd apps/api/core && ../.venv/bin/python manage.py test <apps>` (requires Postgres; set `AUDIT_LOG_ASYNC=false`; `*_integration` modules additionally need RabbitMQ + MinIO which are Docker-only). Verify blueprint tables with `manage.py verify_blueprint_schema`.
- E2E: `pnpm e2e` (Playwright, root config). Its `webServer` auto-starts web + API (reuses running servers) but Postgres + Redis must be up first. Install browsers once with `pnpm exec playwright install --with-deps chromium` (cached in the snapshot; not in the update script).
