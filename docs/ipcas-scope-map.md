# IPCAS Scope Map

Maps the **engineering blueprint** to the **monorepo implementation**.

## Terminology

| Blueprint | Code (monorepo) | Notes |
|-----------|-----------------|-------|
| Project | `projects.Project` | API: `/api/v1/projects/` (UUID) |
| `project_members` | `master_data.ProjectMember` | API: `.../members/` |
| `project_positions` | `master_data.ProjectPosition` | API: `.../positions/` |
| `users` | `authentication.User` | UUID PK; login via `username` or `mobile` |
| `daily_reports` | `field_reports.DailyReport` | Schema ready; UI still uses department logs |
| Materials ledger | `resources.Material` + legacy `Item` | Legacy global `Item` deprecated |

## Sprint 1 completion checklist

| Task | Status |
|------|--------|
| **F-01** Full DB schema (11 domains) | Done — verify with `python manage.py verify_blueprint_schema` |
| **F-02** JWT auth + refresh + logout + password reset | Done |
| **F-03** Traefik gateway + DRF throttling | Done — `docker compose up traefik` on `:8080` |
| **F-04** Project tenancy middleware | Done — `/api/v1/projects/{uuid}/` |
| **F-06** Audit log middleware | Done — writes on POST/PATCH/PUT/DELETE |
| **F-07** MinIO S3 + presigned URLs | Done — `/api/v1/projects/{id}/files/upload-url/` |
| **F-08** RabbitMQ event topology | Done — `setup_event_topology` + `EventPublisher` + `run_event_worker` consumer |

## Sprint 1 hardening (post-foundation)

| Item | Status |
|------|--------|
| Tenancy (`IsProjectMember` on project routes) | Done |
| Audit resource metadata + async via `audit.log` | Done — sync fallback when RabbitMQ unavailable |
| Auth / audit / events / storage integration tests | Done — CI runs with Postgres + RabbitMQ + MinIO |
| Full-stack smoke workflow | Done — `.github/workflows/integration-smoke.yml` |
| Role-aware DRF throttles + JSON 429 | Done |
| Traefik read/write rate limit split | Done |

## Stack alignment

| Blueprint | Monorepo |
|-----------|----------|
| PostgreSQL | Yes — `DATABASE_URL` required |
| Traefik API gateway | Yes — port 8080 in docker-compose |
| RabbitMQ | Yes — port 5672 / management 15672 |
| MinIO (S3) | Yes — port 9000 |
| Offline PWA | Not yet (Sprint 5) |

## API paths

- Projects: `GET/POST /api/v1/projects/`
- Members: `/api/v1/projects/{uuid}/members/`
- Positions: `/api/v1/projects/{uuid}/positions/`
- Auth: `/api/auth/login/`, `/api/auth/logout/`, `/api/auth/token/refresh/`
- Files: `/api/v1/projects/{uuid}/files/upload-url/`

Frontend routes use `/projects/{uuid}/...` (not `/v1/`).

See full blueprint: [IPCAS_Engineering_Blueprint.md](./IPCAS_Engineering_Blueprint.md)
