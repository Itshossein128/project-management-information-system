# Building Management (IPCAS) — Monorepo

Monorepo for the IPCAS construction project management platform: React Router web app + Django API.

## Structure

```
apps/web/     React Router 7 + Vite frontend
apps/api/     Django 4.2 + DRF backend
docs/         Engineering blueprint and scope map
packages/     Shared packages (future)
```

## Current scope vs blueprint

This codebase implements an **early foundation** (businesses, HR, department activity logs, dynamic tables). The full IPCAS target is documented in [docs/IPCAS_Engineering_Blueprint.md](docs/IPCAS_Engineering_Blueprint.md). See [docs/ipcas-scope-map.md](docs/ipcas-scope-map.md) for term mappings and gap analysis.

**Do not confuse:** `Business` (code) = `Project` (blueprint); department activity logs ≠ IPCAS daily field reports.

## Prerequisites

- Node 20+, pnpm 9+
- Python 3.12+
- Docker (for PostgreSQL)

## Quick start

```bash
cp .env.example .env
pnpm install

# PostgreSQL
pnpm db:up

# API venv (first time)
cd apps/api && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ../..

pnpm db:migrate
pnpm db:seed    # dev RBAC groups (first time)
pnpm dev        # web :5173 + api :8000
```

## Docker (all services)

```bash
docker compose up --build
# web http://localhost:3000  api http://localhost:8000
```

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

Copy `.env.example` to `.env`. `DATABASE_URL` is **required** (PostgreSQL only; no SQLite). Default dev Postgres runs on host port **5433** (`docker-compose`) so it does not clash with a system Postgres on 5432.

## Former repositories

Squash-imported from `building-management-front` and `building-management-back`.
