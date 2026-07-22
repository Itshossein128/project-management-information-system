# IPCAS Scope Map

Maps the **engineering blueprint** to the **monorepo implementation**.

## Terminology

| Blueprint | Code (monorepo) | Notes |
|-----------|-----------------|-------|
| Project | `projects.Project` | API: `/api/v1/projects/` (UUID) |
| `project_members` | `master_data.ProjectMember` | API: `.../members/` |
| `project_positions` | `master_data.ProjectPosition` | API: `.../positions/` |
| `users` | `authentication.User` | UUID PK; login via `username` or `mobile` |
| `daily_reports` | `field_reports.DailyReport` | Online UI at `/projects/{id}/daily-reports` (Sprint 4) |
| Materials ledger | `resources.Material` + legacy `Item` | Legacy global `Item` deprecated; see deprecation below |

## Legacy inventory deprecation (`/api/items/`)

The global `inventory.Item` API at `/api/items/` is **deprecated**. New work must use project-scoped `resources.Material` at `/api/v1/projects/{uuid}/materials/`. The legacy endpoint stays mounted until frontend callers finish migrating to material-balance; then remove `inventory.Item` and `/api/items/`.

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
| **UI-01** Design system / tokens | Done — CSS tokens (`apps/web/src/design/tokens/`) + Shadcn-style primitives in `components/ui/` (button, input, select, drawer, data-table, etc.); Dialog/Tabs/DropdownMenu deferred until a feature needs them |
| **UI-02** Project list + creation wizard | Done |
| **UI-15** Members management | Done — `project-members.tsx`; global roles in `settings-roles.tsx` |
| **Sprint 2 hardening** | Done — permission guard fix, `view_wbs` on WBS reads, project settings UI, WBS root bootstrap, `/home` → `/projects` |

## Sprint 3 completion checklist (Activities & Schedule Baseline)

| Task | Status |
|------|--------|
| **C-03** Activity CRUD + relation graph validation | Done |
| **C-04** Baseline import (P6 XER + MSP XML) | Done — MSP XML + P6 XER import |
| **UI-03** WBS tree editor (inline edit, drag-and-drop) | Done — inline edit + HTML5 drag **reparent** (`sorted_child`; sibling before/after reorder not shipped) |
| **partial O-01** PWA / IndexedDB bootstrap | Partial — offline DB + cache warm |

**Deferred (Module 2 nuance):** Activity ↔ BoQ linkage is not modeled on `Activity` yet; schedule baseline does not depend on it.

## Sprint 4 completion checklist (Daily Report Online)

| Task | Status |
|------|--------|
| **C-05** Daily report API + sub-entities | Done — activities, labor, equipment, materials (+`unit_cost`), concrete, labor-camp, incidents; unique `(project, date, shift)` |
| **C-06** Approval workflow + event publish | Done — draft → submit → review → approve/reject; `daily-report.approved` published; rejection cleared on resubmit |
| **C-07** Progress recalculation on approval | Done — direct Celery enqueue on approve + event consumer handler (idempotent) |
| **UI-04** Multi-discipline daily report form | Done — 7-tab form + photo attach/preview on activities; materials unit cost column |
| **E2E** Create & approval workflow | Done — list/form smoke + submit→approve (`daily-report.spec.ts`) |

Known gaps (non-blocking): labor model is Shiraz job-title grid (not blueprint type/discipline); photo upload needs MinIO; multi-discipline = entity tabs (not civil/electrical sub-reports).

See module docs: `apps/api/core/field_reports/ENDPOINTS.md`.

## Sprint 5 completion checklist (Offline Sync)

| Task | Status |
|------|--------|
| **O-01** Service Worker + PWA manifest | Partial — SW in prod; foreground sync via `useAutoSync` (not SW BackgroundSync) |
| **O-02** Batch sync endpoint | Done — shift-aware upsert, header merge, conflict snapshot |
| **O-03** Conflict review UI | Done — `sync-conflicts.tsx` + field-level merge from server snapshot |
| **O-04** Sync status indicator | Done — persistent `data-testid="offline-indicator"` badge |
| **Offline parity** | Done — labor tab (category-safe queue), photo queue, cached reference reads |

## Sprint 6 completion checklist (Physical Progress & S-Curve)

| Task | Status |
|------|--------|
| **C-08** Weighted progress + S-curve endpoint | Done — `schedule/progress_views.py` |
| **K-01** EVM KPIs (partial) | Done — SPI, CPI, EAC, VAC via `/progress/kpis/` |
| **UI-05** Progress dashboard | Done — `/projects/{id}/progress` |

See module docs: `apps/api/core/schedule/ENDPOINTS.md` (progress, activities, imports, Gantt).

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

See module docs: `apps/api/core/cost_control/ENDPOINTS.md`.

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

All paths are under `/api/v1/projects/{projectId}/` unless noted.

- Contracts: `GET/POST .../contracts/`
- Contract detail: `GET/PATCH/DELETE .../contracts/{contractId}/`
- BoQ bulk: `POST .../contracts/{contractId}/items/`
- Change orders: `POST .../contracts/{contractId}/change-orders/`, `PATCH .../change-orders/{changeOrderId}/`, `POST .../change-orders/{changeOrderId}/approve|reject/`
- IPCs: `GET/POST .../ipcs/`
- IPC detail: `GET/PATCH .../ipcs/{ipcId}/`
- IPC line items: `PATCH .../ipcs/{ipcId}/items/{itemId}/`
- IPC workflow: `POST .../ipcs/{ipcId}/populate|submit|approve|pay|reject`
- Manual deductions: `POST/PATCH/DELETE .../ipcs/{ipcId}/deductions/` (list returned on IPC detail; no standalone GET)
- PDF: `GET .../ipcs/{ipcId}/pdf/`

### Sprint 8 frontend routes

- `/projects/{id}/contracts` — list + KPIs
- `/projects/{id}/contracts/new` — create form
- `/projects/{id}/contracts/{contractId}` — detail (info, BoQ, change orders, IPC wizard)
- `/projects/{id}/ipcs/{ipcId}` — IPC detail + workflow

## Sprint 9 completion checklist (Cash Flow & Procurement) — blueprint Sprint 9

| Task | Status |
|------|--------|
| **C-11** Cash flow transaction API + gap analysis | Done — `cash_flow/` app + `/projects/{id}/cash-flow` UI |
| **C-15** Procurement request workflow (PR → PO → delivery) | Done — `MaterialRequest` workflow + `PurchaseOrder` model; `/projects/{id}/procurement` UI |
| **UI-08** Cash flow chart + gap analysis view | Done — `project-cash-flow.tsx` |

### Sprint 9 API paths (cash flow & procurement)

**Cash flow** (`view_cashflow` / `edit_cashflow`):

- `GET/POST .../cash-flow/` — list + summary
- `POST/PATCH/DELETE .../cash-flow/transactions/{id}/`
- `GET .../cash-flow/monthly/`, `.../forecast/`, `PUT .../forecast/{YYYY-MM}/`
- `GET .../cash-flow/gap-analysis/`, `.../receivables/`

**Procurement** (`view_procurement` / `edit_procurement` / `approve_procurement`):

- `GET/POST .../material-requests/` — PR list/create
- `PATCH/DELETE .../material-requests/{id}/`
- `POST .../material-requests/{id}/approve|place-order|deliver|cancel/`

### Sprint 9 frontend routes (cash flow & procurement)

- `/projects/{id}/cash-flow` — transactions, forecast, gap analysis
- `/projects/{id}/procurement` — PR → approval → PO → delivery workflow

---

## Sprint 9 early delivery (blueprint Sprints 11–13 pulled forward)

| Task | Status |
|------|--------|
| **C-16** Subcontractor registry + scorecard + risk flag engine | Done — `subcontractors/` CRUD, scores, warnings, risk-summary |
| **K-03** Configurable alert rule engine | Done — `alerts/services/alert_engine.py` (16 alert types incl. Sprint 13 critical path / IPC approval / procurement) |
| **K-05** Alert acknowledgement + log API | Done — alert log list, acknowledge, active counts; rule delete in UI |
| **E-06** Economic P&L snapshot generator | Done — `economic/services/snapshot_service.py` + nightly Celery task |
| **E-07** Monte Carlo simulation | Done — async `POST .../economic/simulate/` |
| **UI-09** Gantt chart (read-only, baseline comparison) | Done — frappe-gantt + baseline comparison table + PDF export |
| **UI-11** Economic dashboard | Done — `/projects/{id}/economic` (3 profit layers, simulation) |
| **UI-12** Alert center + rule configuration | Done — `/projects/{id}/alerts` |
| **Tests** | Done — backend tests + `e2e/tests/sprint9.spec.ts` |

### Sprint 9 early delivery API paths (subcontractors, alerts, economic, gantt)

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

### Sprint 9 early delivery frontend routes (subcontractors, alerts, economic, gantt)

- `/projects/{id}/subcontractors` — registry with risk badges
- `/projects/{id}/subcontractors/{subId}` — detail (scores, warnings, radar chart, financials)
- `/projects/{id}/alerts` — alert center + rule editor
- `/projects/{id}/economic` — 3-layer P&L + Monte Carlo results
- `/projects/{id}/schedule/gantt` — read-only Gantt with baseline selector + PDF export

### Sprint 9 early delivery operational notes

- **Alert evaluation:** `run_daily_alert_checks` Celery beat task scans all active projects; `monitor_cash_gaps` watches cash-flow forecasts. Real-time re-checks fire via Django signals on daily-report approval, actual-cost save, inventory transaction, subcontractor score, and correspondence save.
- **Cooldown:** Each `AlertRule` has `cooldown_hours` (default 24) — duplicate `trigger_reference` within cooldown is suppressed.
- **Economic snapshots:** `generate_daily_snapshots` Celery task runs nightly for active projects. Snapshots are also generated on first `GET .../economic/snapshot/` for a date.
- **Monte Carlo:** Requires Celery worker (`CELERY_TASK_ALWAYS_EAGER=true` runs inline in local dev without RabbitMQ).
- **Risk flag criteria:** overall score &lt; 6, unresolved written/final/suspension warnings, suspended status, or &gt;15% progress lag vs plan on linked contract activities.

See module docs: `apps/api/core/alerts/ENDPOINTS.md`, `economic/ENDPOINTS.md`, `subcontractors/ENDPOINTS.md`, `cash_flow/ENDPOINTS.md`.

## Sprint 10 completion checklist (Materials, Equipment & HR)

| Task | Status |
|------|--------|
| **C-13** Inventory ledger + running balance + consumption analytics | Done — `resources/` balance + `material-balance/consumption/`; ADJUST included in balance; running balance project-scoped |
| **C-13** Tests | Done — `resources/tests/test_balance.py` |
| **C-14** Equipment registry + utilization API | Done — `equipment/`, `equipment-utilization/`; log vs daily-report dedupe |
| **C-14** Tests | Done — `field_reports/tests/test_equipment_utilization.py` |
| **Labor productivity API** | Done — `labor-productivity/` with per-activity hour allocation by qty share |
| **UI-04** Daily report labor/equipment tab polish | Done — idle hours, registry combobox with equipment FK, work_hours columns |
| **Equipment + labor dashboards** | Done — `equipment-utilization`, `labor-productivity` routes |
| **HR approval UI** | Done — leave/overtime approve+reject; backend status gates + `approve_reports` |
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


## Sprint 11 completion checklist (Subcontractors, Risks & Documents)

| Task | Status |
|------|--------|
| **C-16** Subcontractor scorecard + risk flag engine | Done — early delivery (Sprint 9); `subcontractors/` |
| **C-17** Risk/delay register API + claim documentation linker | Done — `risk-events/`, matrix, `related_daily_report` / `related_correspondence` |
| **C-17** Tests | Done — `risk/tests/test_risk_register.py`, `test_risk_matrix_unit.py` |
| **C-18** Document version control + correspondence tracker | Done — durable object keys + fresh download URLs; `access_level` enforced |
| **C-18** Tests | Done — `documents/tests/test_documents.py` |
| **UI-13** Document archive + correspondence tracker | Done — upload, create/respond, overdue filter |
| **UI-14** Risk register & matrix view | Done — `/projects/{id}/risk-register` |

### Sprint 11 API paths

- Risk events: `GET/POST .../risk-events/`
- Risk matrix: `GET .../risk-events/matrix/`
- Barriers (legacy): `GET/POST .../barriers/`
- Documents: `GET/POST .../documents/`, `POST .../documents/{id}/revisions/`
- Correspondence: `GET/POST .../correspondence/`, `POST .../correspondence/{id}/respond/`

### Sprint 11 frontend routes

- `/projects/{id}/risk-register` — probability × severity matrix + event list
- `/projects/{id}/documents` — archive upload + correspondence write path
- `/projects/{id}/barriers` — barrier logs
- `/projects/{id}/subcontractors` — scorecards


## Sprint 12 completion checklist (Economic Engine & Simulation)

| Task | Status |
|------|--------|
| **E-01** Inflation index table + ingestion | Done — indices + staff PUT; Persian mapping indices seeded |
| **E-02** Cost-to-category inflation mapping API | Done — `economic/inflation-mappings/` (list/create/PATCH/delete) |
| **E-03** Historical cost inflation adjuster | Done — snapshot + `?refresh=1` on-demand regenerate |
| **E-04/E-05** Payment delay + financing cost | Done — `financing-cost/` + `payment-delay/` alias; configurable rate |
| **E-06** P&L snapshot nightly | Done — Celery beat `generate_daily_snapshots` |
| **E-07** Working capital forecast curve | Done — `economic/working-capital/` |
| **E-08** Monte Carlo productivity + WC P90 | Done — `monte_carlo_service` + Celery |
| **E-09** Forecast + scenario simulate API | Done — `economic/forecast/`, `economic/simulate/` |
| **E-10** Sensitivity / tornado | Done — `economic/sensitivity/` |
| **UI-11** Economic dashboard | Done — 7 tabs; mapping edit gated by `edit_cashflow` |
| **Tests** | Done — economic unit/API tests + deepened `sprint12-economic.spec.ts` |

### Sprint 12 API paths

- `GET /api/v1/projects/{id}/economic/forecast/` — inflation-adjusted EAC / EVM
- `GET /api/v1/projects/{id}/economic/working-capital/` — WC curve
- `GET /api/v1/projects/{id}/economic/cash-flow-real/` — real vs nominal outflows
- `GET/POST /api/v1/projects/{id}/economic/inflation-mappings/` — mapping list/create
- `PATCH/DELETE /api/v1/projects/{id}/economic/inflation-mappings/{mapping_id}/`
- `GET /api/v1/projects/{id}/economic/sensitivity/` — latest tornado chart data
- `GET /api/v1/projects/{id}/economic/payment-delay/` — alias of financing-cost
- `GET /api/v1/projects/{id}/economic/snapshot/?refresh=1` — force regenerate snapshot

See full blueprint: [IPCAS_Engineering_Blueprint.md](./IPCAS_Engineering_Blueprint.md)

## Sprint 13 completion checklist (Alerts, Executive Dashboard & Polish)

| Task | Status |
|------|--------|
| **K-02** Unified KPI endpoint (`/kpis`) with caching | Done — `GET .../kpis/` + `/health/` alias; Redis TTL 5 min; `projects/kpi_service.py` |
| **K-03** Alert rule engine | Done — carried from Sprint 9; 16 alert types |
| **K-04** Notification delivery (email, SMS, in-app) | Done — `notifications/services/delivery.py`; channels via `ALERT_NOTIFY_CHANNELS` (default `in_app,email`); SMS console stub |
| **K-05** Alert acknowledgement + log API | Done — carried from Sprint 9 |
| **UI-09** Gantt chart (read-only) | Done — carried from Sprint 9 |
| **UI-10** Executive dashboard with 10-KPI panel | Done — `/projects/{id}/overview` + `ExecutiveKpiPanel` |
| **UI-12** Alert center + rule configuration | Done — carried from Sprint 9; new type labels |
| **15+ alert types** | Done — added `critical_path_delay`, `ipc_approval_delayed`, `procurement_overdue` |
| **Hardening** | Done — `alert_log` indexes; `apps/api/scripts/load_smoke_kpis.py` |
| **Tests / E2E** | Done — KPI + delivery + sprint13 alert tests; `e2e/tests/sprint13.spec.ts` |
| **UAT** | Done — [sprint13-uat-checklist.md](./sprint13-uat-checklist.md) |

### Sprint 13 API paths

- `GET /api/v1/projects/{id}/kpis/` — unified KPIs (`?as_of=`, `?force_refresh=1`); permission `view_dashboard`
- `GET /api/v1/projects/{id}/health/` — alias of `/kpis/`
- Alert types (system seeds): prior 13 + `critical_path_delay`, `ipc_approval_delayed`, `procurement_overdue`

### Sprint 13 frontend routes

- `/projects/{id}/overview` — executive 10-KPI panel (permission-gated sections) + module launcher
- `/projects/{id}/alerts` — alert center (unchanged route; expanded type catalog)

### Sprint 13 operational notes

- **Channels:** `ALERT_NOTIFY_CHANNELS=in_app,email` (add `sms` to enable console SMS backend). `SMS_PROVIDER=console` by default.
- **Cache:** Unified KPIs use `project_kpis:{id}:{as_of}` (5 min). Progress EVM cache invalidation also clears `project_kpis:*`.
- **Load smoke:** `ACCESS_TOKEN=… PROJECT_ID=… python apps/api/scripts/load_smoke_kpis.py`

