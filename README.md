# Building Management (IPCAS) — Monorepo

Monorepo for the IPCAS construction project management platform: React Router web app + Django API.

## Structure

```
apps/web/     React Router 7 + Vite frontend
apps/api/     Django 4.2 + DRF backend (IPCAS Sprint 1 foundation)
docs/         Engineering blueprint and scope map
infra/        Traefik gateway config
packages/     Shared packages (future)
```

## Dev modes

| Mode | Command | API | Gateway | MinIO / RabbitMQ |
|------|---------|-----|---------|------------------|
| **Local dev** | `pnpm dev` | `:8000` direct | No | Not started (storage/events need Docker) |
| **Full stack** | `docker compose up --build` | via Traefik `:8080` | Yes | Yes (+ `worker` consumes events) |

Set `AUDIT_LOG_ASYNC=true` (default in Docker) to publish audit entries to RabbitMQ; the `worker` service persists them. Use `AUDIT_LOG_ASYNC=false` for synchronous audit writes (CI tests use this).

Integration tests: `python manage.py test events authentication audit storage` (requires Postgres; RabbitMQ + MinIO for `*_integration` modules).

Smoke test (full stack): `bash scripts/smoke-stack.sh` after `docker compose up`.

## Current scope vs blueprint

Sprint 1 (Infrastructure & Auth) is implemented: full blueprint UUID schema, JWT with revocation, Traefik gateway, tenancy middleware, audit log (sync or async via RabbitMQ), MinIO storage, RabbitMQ events + worker consumer. See [docs/ipcas-scope-map.md](docs/ipcas-scope-map.md).

**API:** `/api/v1/projects/` (UUID). **Frontend routes:** `/projects/{uuid}/...`

## Prerequisites

- Node 20+, pnpm 9+
- Python 3.12+
- Docker (PostgreSQL, optional full stack)

## Quick start

```bash
cp .env.example .env
pnpm install

pnpm db:up
cd apps/api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ../..

pnpm db:migrate
pnpm db:seed
pnpm dev        # web :5173 + api :8000
```

Verify blueprint tables:

```bash
cd apps/api/core && ../.venv/bin/python manage.py verify_blueprint_schema
```

## Docker (full stack: Postgres, RabbitMQ, MinIO, API, Web, Traefik)

```bash
docker-compose up --build
# Traefik entry: http://localhost:8080
# API direct:    http://localhost:8000
# Web direct:    http://localhost:3000
```

## Customer PC deployment (no cloud host)

For demos or evaluation on a customer machine, use the launcher scripts in [`customer/`](customer/README.md):

| Step | Windows | Mac / Linux |
|------|---------|-------------|
| First install | `customer\install.bat` | `bash customer/install.sh` |
| Start | `customer\start.bat` | `bash customer/start.sh` |
| Stop | `customer\stop.bat` | `bash customer/stop.sh` |
| Update from Git | `customer\update.bat` | `bash customer/update.sh` |

Requires Docker Desktop + Git clone of this repo. Entry URL: **http://localhost:8080**. Demo login: `+10000000001` / `devpass123`.

Uses `docker-compose.customer.yml` (standalone demo stack, auto-seed, restart policies). See [customer/README.md](customer/README.md).

## Scripts

| Command | Description |
|---------|-------------|
| `pnpm dev` | Start web + API |
| `pnpm db:up` | Start Postgres only |
| `pnpm db:migrate` | Run Django migrations |
| `pnpm db:seed` | Seed dev RBAC (`seed_rbac_dev`) |
| `pnpm typecheck` | Web TypeScript check |
| `pnpm build` | Production web build |

## Environment

Copy `.env.example` to `.env`. `DATABASE_URL` is **required** (PostgreSQL only). Default dev Postgres runs on host port **5433**.

## Dev logins (after seed)

Password: `devpass123` — mobiles `+10000000001` (admin) through `+10000000004`.
