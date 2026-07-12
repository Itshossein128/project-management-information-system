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
| Offline PWA | Partial — IndexedDB queue + sync UI; SW disabled in dev unless `VITE_ENABLE_SW=true` |

## Sprint 2 completion checklist (Projects, WBS & Members)

| Task | Status |
|------|--------|
| **F-05** Role & permission engine + project overrides | Done — `permissions/`, `HasProjectPermission` |
| **C-01** Project CRUD + membership APIs | Done — `projects/`, `members/`, `positions/` |
| **C-02** WBS tree API (insert, reorder, code propagation) | Done — CRUD + move + auto code propagation |
| **UI-01** Design system / tokens | Partial — Shadcn-style primitives + CSS tokens |
| **UI-02** Project list + creation wizard | Done |
| **UI-15** Members management | Done — `project-members.tsx`; global roles in `settings-roles.tsx` |

## Sprint 3 completion checklist (Activities & Schedule Baseline)

| Task | Status |
|------|--------|
| **C-03** Activity CRUD + relation graph validation | Done |
| **C-04** Baseline import (P6 XER + MSP XML) | Done — MSP XML + P6 XER import |
| **UI-03** WBS tree editor (inline edit, drag-and-drop) | Done — inline edit + HTML5 drag reparent |
| **partial O-01** PWA / IndexedDB bootstrap | Partial — offline DB + cache warm |

## Sprint 4 completion checklist (Daily Report Online)

| Task | Status |
|------|--------|
| **C-05** Daily report API + sub-entities | Done — activities, labor, equipment, materials, concrete, labor-camp, incidents |
| **C-06** Approval workflow + event publish | Done — draft → submit → review → approve/reject |
| **C-07** Progress recalculation on approval | Done — Celery task updates `ActivityProgress` |
| **UI-04** Multi-discipline daily report form | Done — 7-tab form + photo attach on activities |

## Sprint 5 completion checklist (Offline Sync)

| Task | Status |
|------|--------|
| **O-01** Service Worker + PWA manifest | Partial — SW in prod; foreground sync via `useAutoSync` (not SW BackgroundSync) |
| **O-02** Batch sync endpoint | Done — backend + frontend `syncBatch()` wired |
| **O-03** Conflict review UI | Done — `sync-conflicts.tsx` + failed-queue retry/discard |
| **O-04** Sync status indicator | Done — persistent `data-testid="offline-indicator"` badge |
| **Offline parity** | Done — labor tab, photo queue, cached reference reads |

## Sprint 6 completion checklist (Physical Progress & S-Curve)

| Task | Status |
|------|--------|
| **C-08** Weighted progress + S-curve endpoint | Done — `schedule/progress_views.py` |
| **K-01** EVM KPIs (partial) | Done — SPI, CPI, EAC, VAC via `/progress/kpis/` |
| **UI-05** Progress dashboard | Done — `/projects/{id}/progress` |

## API paths

- Projects: `GET/POST /api/v1/projects/`
- Members: `/api/v1/projects/{uuid}/members/`
- Positions: `/api/v1/projects/{uuid}/positions/`
- Auth: `/api/auth/login/`, `/api/auth/logout/`, `/api/auth/token/refresh/`
- Files: `/api/v1/projects/{uuid}/files/upload-url/`

Frontend routes use `/projects/{uuid}/...` (not `/v1/`).

## Sprint 7 completion checklist (Budget & Cost Control)

| Task | Status |
|------|--------|
| **C-09** Budget ingestion + variance engine | Done — `cost_control/` budgets, variance, summary |
| **C-10** Actual cost ledger + cost pool allocation | Done — labor auto-cost, auto-allocate API, manual allocate |
| **UI-06** Cost control screens | Done — `/projects/{id}/costs` (budget, actual, variance, pools) |
| **Tests** | Done — `cost_control/tests/` in CI |

## Sprint 8 completion checklist (Contracts & IPC)

| Task | Status |
|------|--------|
| **C-12** Contract + IPC API with deduction engine | Done — `contracts/` CRUD, IPC workflow, PDF, manual deductions |
| **C-12** IPC auto-populate from progress | Done — `ipc_service.auto_populate_ipc` |
| **C-12** IPC submit event | Done — `ipc.submitted` on submit |
| **UI-07** Contract registry UI | Done — list, create, detail, BoQ, change orders |
| **UI-07** IPC wizard + detail | Done — wizard drawer, detail page, workflow bar, PDF |
| **Tests** | Done — `contracts/tests/` (service, workflow, CRUD) |
| **Seed** | Done — `python manage.py seed_contracts_demo --project-id=<uuid>` |

### Sprint 8 API paths

- Contracts: `GET/POST /api/v1/projects/{id}/contracts/`
- Contract detail: `GET/PATCH /api/v1/projects/{id}/contracts/{id}/`
- BoQ bulk: `POST /api/v1/projects/{id}/contracts/{id}/items/`
- Change orders: `POST .../change-orders/`, `POST .../change-orders/{id}/approve/`
- IPCs: `GET/POST /api/v1/projects/{id}/ipcs/`
- IPC workflow: `POST .../ipcs/{id}/populate|submit|approve|pay|reject`
- Manual deductions: `POST/PATCH/DELETE .../ipcs/{id}/deductions/`
- PDF: `GET .../ipcs/{id}/pdf/`

### Sprint 8 frontend routes

- `/projects/{id}/contracts` — list + KPIs
- `/projects/{id}/contracts/new` — create form
- `/projects/{id}/contracts/{contractId}` — detail (info, BoQ, change orders, IPC wizard)
- `/projects/{id}/ipcs/{ipcId}` — IPC detail + workflow

See full blueprint: [IPCAS_Engineering_Blueprint.md](./IPCAS_Engineering_Blueprint.md)
