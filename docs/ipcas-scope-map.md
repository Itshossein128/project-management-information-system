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

## Sprint 9 completion checklist (Subcontractors, Alerts, Economic Engine & Gantt)

| Task | Status |
|------|--------|
| **C-16** Subcontractor registry + scorecard + risk flag engine | Done — `subcontractors/` CRUD, scores, warnings, risk-summary |
| **K-03** Configurable alert rule engine | Done — `alerts/services/alert_engine.py` (12+ alert types) |
| **K-05** Alert acknowledgement + log API | Done — alert log list, acknowledge, active counts |
| **E-06** Economic P&L snapshot generator | Done — `economic/services/snapshot_service.py` + nightly Celery task |
| **E-07** Monte Carlo simulation | Done — async `POST .../economic/simulate/` |
| **UI-09** Gantt chart (read-only, baseline comparison) | Done — frappe-gantt UI + PDF export |
| **UI-11** Economic dashboard | Done — `/projects/{id}/economic` (3 profit layers, simulation) |
| **UI-12** Alert center + rule configuration | Done — `/projects/{id}/alerts` |
| **Tests** | Done — `alerts/tests/`, `economic/tests/`, `subcontractors/tests/`, `schedule/tests/test_gantt.py` |

### Sprint 9 API paths (subcontractors, alerts, economic, gantt)

All paths are under `/api/v1/projects/{id}/` unless noted.

**Subcontractors** (`view_contracts` / `edit_contracts`):

- `GET/POST .../subcontractors/` — list (filters: `status`, `discipline`, `risk_only=true`) or create
- `GET .../subcontractors/risk-summary/` — at-risk subcontractors (cached 1h)
- `GET/PATCH/DELETE .../subcontractors/{id}/` — detail, update, soft-delete
- `GET/POST .../subcontractors/{id}/scores/` — performance scores + trend
- `PATCH/DELETE .../subcontractors/{id}/scores/{scid}/`
- `GET/POST .../subcontractors/{id}/warnings/`
- `PATCH .../subcontractors/{id}/warnings/{wid}/` — resolve warnings

**Alerts** (`view_project` / `edit_project`):

- `GET/POST .../alert-rules/` — list (project + system rules) or create project rule
- `PATCH/DELETE .../alert-rules/{rid}/` — update; delete only project-owned rules
- `GET .../alerts/` — log (query: `acknowledged=false`, `alert_type`, `date_from`, `date_to`; max 200)
- `GET .../alerts/active/` — unacknowledged counts by type (cached 5 min)
- `POST .../alerts/{lid}/acknowledge/`

**Economic** (`view_dashboard`):

- `GET .../economic/snapshot/` — P&L snapshot (`?as_of=` Jalali or Gregorian; generates on demand)
- `GET .../economic/history/` — snapshot time series
- `GET .../economic/financing-cost/` — payment delay / financing cost
- `GET .../economic/inflation-indices/` — latest index values
- `POST .../economic/simulate/` — Monte Carlo (`iterations`, `scenario_params`) → `202` + `task_id`
- `GET .../economic/simulate/status/{task_id}/`
- `GET .../economic/simulate/latest/`
- `PUT /api/v1/inflation-indices/{name}/{date}/` — admin upsert (staff only)

**Schedule / Gantt** (`view_activities`):

- `GET .../gantt/` — task data for chart (`?baseline_id=` optional)
- `GET .../gantt/pdf/` — PDF table export

### Sprint 9 frontend routes (subcontractors, alerts, economic, gantt)

- `/projects/{id}/subcontractors` — registry with risk badges
- `/projects/{id}/subcontractors/{subId}` — detail (scores, warnings, radar chart, financials)
- `/projects/{id}/alerts` — alert center + rule editor
- `/projects/{id}/economic` — 3-layer P&L + Monte Carlo results
- `/projects/{id}/schedule/gantt` — read-only Gantt with baseline selector + PDF export

### Sprint 9 operational notes

- **Alert evaluation:** `run_daily_alert_checks` Celery beat task scans all active projects; `monitor_cash_gaps` watches cash-flow forecasts. Real-time re-checks fire via Django signals on daily-report approval, actual-cost save, inventory transaction, subcontractor score, and correspondence save.
- **Cooldown:** Each `AlertRule` has `cooldown_hours` (default 24) — duplicate `trigger_reference` within cooldown is suppressed.
- **Economic snapshots:** `generate_daily_snapshots` Celery task runs nightly for active projects. Snapshots are also generated on first `GET .../economic/snapshot/` for a date.
- **Monte Carlo:** Requires Celery worker (`CELERY_TASK_ALWAYS_EAGER=true` runs inline in local dev without RabbitMQ).
- **Risk flag criteria:** overall score &lt; 6, unresolved written/final/suspension warnings, suspended status, or &gt;15% progress lag vs plan on linked contract activities.

See module docs: `apps/api/core/alerts/ENDPOINTS.md`, `economic/ENDPOINTS.md`, `subcontractors/ENDPOINTS.md`.

## Sprint 9 completion checklist (Cash Flow & Procurement)

| Task | Status |
|------|--------|
| **C-11** Cash flow transaction API + gap analysis | Done — `cash_flow/` app + `/projects/{id}/cash-flow` UI |
| **C-15** Procurement request workflow (PR → PO → delivery) | Partial — `MaterialRequest` status fields only; full workflow deferred |
| **UI-08** Cash flow chart + gap analysis view | Done — `project-cash-flow.tsx` |

## Sprint 10 completion checklist (Materials, Equipment & HR)

| Task | Status |
|------|--------|
| **C-13** Inventory ledger + running balance + consumption analytics | Done — `resources/` balance + `material-balance/consumption/` |
| **C-13** Tests | Done — `resources/tests/test_balance.py` |
| **C-14** Equipment registry + utilization API | Done — `equipment/`, `equipment-utilization/` |
| **C-14** Tests | Done — `field_reports/tests/test_equipment_utilization.py` |
| **Labor productivity API** | Done — `labor-productivity/` |
| **UI-04** Daily report labor/equipment tab polish | Done — idle hours, registry combobox, work_hours columns |
| **Equipment + labor dashboards** | Done — `equipment-utilization`, `labor-productivity` routes |
| **HR approval UI** | Done — leave/overtime approve actions in web UI |
| **Nav grouping** | Done — Resources section in project sidebar |

### Sprint 10 API paths

- Materials consumption: `GET /api/v1/projects/{id}/material-balance/consumption/`
- Equipment registry: `GET/POST /api/v1/projects/{id}/equipment/`
- Equipment utilization: `GET /api/v1/projects/{id}/equipment-utilization/`
- Utilization summary: `GET /api/v1/projects/{id}/equipment-utilization/summary/`
- Labor productivity: `GET /api/v1/projects/{id}/labor-productivity/`

### Sprint 10 frontend routes

- `/projects/{id}/material-balance` — balance + consumption% + low-stock alert link
- `/projects/{id}/equipment-utilization` — fleet KPIs + registry CRUD
- `/projects/{id}/labor-productivity` — productivity by activity/discipline/job title
- Resources nav: equipment log, manpower, labor camp, leave, overtime

See full blueprint: [IPCAS_Engineering_Blueprint.md](./IPCAS_Engineering_Blueprint.md)
