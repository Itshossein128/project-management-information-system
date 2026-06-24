---
name: Monorepo Migration Plan
overview: Consolidate building-management-front and building-management-back into a new GitHub monorepo with apps/web + apps/api, PostgreSQL as the sole database (dev, Docker, CI), aligned to IPCAS_Engineering_Blueprint.md via a documented scope map.
todos:
  - id: scaffold-root
    content: "Create new repo root: pnpm-workspace.yaml, root package.json, unified .gitignore, .env.example, docs/ipcas-scope-map.md"
    status: in_progress
  - id: move-apps
    content: Squash-copy frontend to apps/web and backend to apps/api; add thin apps/api/package.json
    status: completed
  - id: unify-config
    content: Externalize Django settings to env vars; switch DATABASES to PostgreSQL via DATABASE_URL; align CORS + VITE_API_BASE_URL; merge and fix Cursor rules (Django not FastAPI)
    status: pending
  - id: postgres
    content: Add psycopg + dj-database-url to requirements; docker-compose postgres service; CI postgres service; document migrate/seed workflow
    status: pending
  - id: blueprint-docs
    content: Add docs/ipcas-scope-map.md and root README scope section; relocate IPCAS_Engineering_Blueprint.md to monorepo docs/
    status: pending
  - id: docker
    content: Fix apps/web Dockerfile for pnpm; add apps/api Dockerfile with migrate-on-start; root docker-compose.yml with postgres + api + web
    status: completed
  - id: ci
    content: Add .github/workflows/ci.yml with path-filtered web and api jobs; api job uses Postgres 16 service container
    status: pending
  - id: publish
    content: Push to new GitHub repo; archive building-management-front and building-management-back
    status: pending
isProject: false
---

# Monorepo Migration Plan

## Current state

| Repo                                                                                   | Remote                      | Stack                           | Integration                                                       |
| -------------------------------------------------------------------------------------- | --------------------------- | ------------------------------- | ----------------------------------------------------------------- |
| [building-management](file:///home/hossein/Desktop/projects/mehdi/building-management) | `building-management-front` | React Router 7 + Vite + pnpm    | HTTP to `VITE_API_BASE_URL` (default `http://localhost:8000/api`) |
| [inventory-backend](file:///home/hossein/Desktop/projects/mehdi/inventory-backend)     | `building-management-back`  | Django 4.2 + DRF + SQLite (dev) | CORS allows `localhost:5173` — **monorepo target: PostgreSQL**    |

No shared code today — coupling is API-only. Neither repo has CI; the frontend Dockerfile is broken (expects `package-lock.json` but only `pnpm-lock.yaml` exists).

**Blueprint reference:** [IPCAS_Engineering_Blueprint.md](file:///home/hossein/Desktop/projects/mehdi/building-management/IPCAS_Engineering_Blueprint.md) describes the full target system (18 modules, microservices, PostgreSQL, offline PWA). The coded app is an **early foundation slice** — not a partial implementation of most modules. The monorepo must document this gap explicitly so future work does not confuse current `Business` / department logs with blueprint `Project` / daily reports / WBS.

---

## IPCAS Blueprint vs Current Code — Alignment Audit

### Executive summary

| Blueprint scope                      | Current code status                                                           |
| ------------------------------------ | ----------------------------------------------------------------------------- |
| 18 feature modules                   | ~2 modules partially started (Foundation + partial Field Report + partial HR) |
| ~70 DB tables / 11 domains           | ~12 Django models across 3 apps                                               |
| Microservices + message bus          | Single Django monolith                                                        |
| PostgreSQL + Redis + S3 + TimeSeries | SQLite today; **monorepo switches to PostgreSQL**; no Redis/S3 yet            |
| Offline PWA + WebSocket              | Web SPA only, no PWA                                                          |
| API base `/v1/projects`              | API base `/api/businesses`                                                    |

**Critical terminology mismatch (do not gloss over in monorepo docs):**

| Blueprint term                         | Current code term                                            | Notes                                                                      |
| -------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------- |
| `Project`                              | `Business`                                                   | Same concept (multi-tenant project scope); different naming everywhere     |
| `project_members`                      | `UserBusinessAssignment`                                     | Assignment adds wage/tools/dates; blueprint is membership + separate roles |
| `project_positions`                    | `BusinessJobPosition`                                        | Per-business job titles — aligned in intent                                |
| `daily_reports`                        | `DepartmentActivityRecord`                                   | **Not equivalent** — see Module 4 below                                    |
| `materials` + `inventory_transactions` | `Item` (global) + `DynamicTableRow` + `SpaceMaterialRequest` | Three parallel concepts, none match blueprint ledger                       |
| `users.username` + `email`             | `User.phone_number` login                                    | Different auth identity model                                              |

**Monorepo rule:** Do **not** rename `Business` → `Project` during the squash merge. Add `docs/ipcas-scope-map.md` at root mapping terms and flagging what is blueprint-target vs implemented.

---

### Section 1 — System Architecture

| Blueprint                         | Current                             | Gap / mismatch                                                                        |
| --------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------- |
| Web + Mobile PWA + Tablet         | React Router 7 web SPA only         | No PWA, Service Worker, IndexedDB (blueprint §1.3, tasks O-01–O-04)                   |
| API Gateway, rate limiting        | Django `runserver` / WSGI directly  | No gateway (F-03)                                                                     |
| 6 microservices + Economic Engine | Single Django app (`core/`)         | Monolith is correct **for now**; blueprint is target architecture                     |
| Kafka/RabbitMQ event bus          | None                                | No `daily-report.approved` events (F-08)                                              |
| PostgreSQL, Redis, S3, TimeSeries | SQLite file `core/db.sqlite3` today | **Monorepo merge adopts PostgreSQL** for dev, Docker, and CI (Redis/S3 remain future) |
| JWT/OAuth2                        | JWT via `simplejwt`                 | Partially aligned (F-02)                                                              |
| Offline-first field sync          | None                                | Not started                                                                           |

**Monorepo action:** Cursor rules in `inventory-backend` still describe FastAPI + MongoDB — **must be corrected** to Django + DRF + PostgreSQL during Phase 3 merge.

---

### Section 2 — Database Domains (11 domains)

| Domain                 | Blueprint tables                                                  | Current models                                                                         | Status                                                                                                                    |
| ---------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **1 Master Data**      | `users`, `roles`, `project_members`, `project_positions`, `units` | `authentication.User`, Django `Group`, `UserBusinessAssignment`, `BusinessJobPosition` | **Partial** — no `units`; user uses phone not username/email; roles are global Groups not per-project role junction table |
| **2 Project & WBS**    | `projects`, `wbs`, `activities`, `activity_relations`             | `Business` (name/slug only)                                                            | **Missing** — no project metadata (employer, dates, contract amount), no WBS, no activities                               |
| **3 Schedule**         | baselines, floats, critical path                                  | None                                                                                   | **Missing**                                                                                                               |
| **4 Daily Reports**    | `daily_reports` + labor/equipment/material/incident sub-tables    | `DepartmentActivityRecord`                                                             | **Misaligned** — see Module 4                                                                                             |
| **5 Resources**        | `materials`, `inventory_transactions`, `suppliers`                | `Item`, `Category`, `SpaceMaterialRequest`, dynamic tables                             | **Partial / fragmented**                                                                                                  |
| **6 Cost Control**     | budgets, actual_costs, cost_pools                                 | None                                                                                   | **Missing**                                                                                                               |
| **7 Contracts & IPCs** | contracts, ipcs, deductions                                       | None                                                                                   | **Missing**                                                                                                               |
| **8 Cash Flow**        | cash_transactions, forecasts                                      | None                                                                                   | **Missing**                                                                                                               |
| **9 Economic Engine**  | inflation, snapshots, simulation                                  | None                                                                                   | **Missing**                                                                                                               |
| **10 Risk & Delays**   | `risk_events`                                                     | None                                                                                   | **Missing**                                                                                                               |
| **11 Alerts**          | `alert_rules`, `alert_log`                                        | None                                                                                   | **Missing**                                                                                                               |

**Dynamic schema (`TableDefinition`, `FieldDefinition`, `DynamicTableRow`):** Not in blueprint as-is. Closest blueprint concept is BoQ / contract items — current implementation is a **generic EAV-style layer**, useful but not a substitute for WBS or `materials`.

---

### Section 3 — API Design

| Blueprint convention               | Current API                                                         | Mismatch                                                        |
| ---------------------------------- | ------------------------------------------------------------------- | --------------------------------------------------------------- |
| `GET /projects`                    | `GET /api/businesses/`                                              | Path + resource name                                            |
| `GET /projects/{id}/members`       | `GET /api/businesses/{id}/assignments/`                             | Different shape (wage, tools, dates)                            |
| `GET /projects/{id}/daily-reports` | `GET /api/businesses/{id}/department-activity-records/?department=` | Different resource, department filter instead of unified report |
| `GET /projects/{id}/wbs`           | None                                                                | Missing                                                         |
| `GET /projects/{id}/kpis`          | None                                                                | Missing                                                         |
| Pagination `per_page`              | `page` + `page_size` (DRF)                                          | Minor naming difference                                         |
| Amounts as numeric strings         | JSON numbers                                                        | Minor                                                           |

**Implemented API surface (not in blueprint paths):**

- `/api/auth/*` — register, login, refresh, users, profile (blueprint assumes auth but doesn't list these paths)
- `/api/relations/` — dynamic table relations (blueprint has `activity_relations` only)
- `/api/items/` — legacy global inventory (blueprint is project-scoped)
- `/api/businesses/{id}/tables/{slug}/rows/*` — dynamic data CRUD + Excel

**Monorepo action:** `packages/api-types` must generate from **actual** `/api/schema/` (drf-spectacular), not blueprint paths. Add OpenAPI tag cleanup: remove stale "MongoDB" tag in settings.

---

### Section 4 — Feature Modules (1–18)

#### Module 1 — Project Foundation — **PARTIAL (~15%)**

| Blueprint feature                  | Code                                                 | Gap                                                                    |
| ---------------------------------- | ---------------------------------------------------- | ---------------------------------------------------------------------- |
| Full project metadata              | `Business`: name, slug, timestamps only              | Missing employer, contractor, dates, contract amount, location, status |
| Mid-project onboarding / cut-off   | None                                                 | Missing                                                                |
| Cost pools                         | None                                                 | Missing                                                                |
| Project list scoped to user access | `GET /api/businesses/` returns all for any auth user | RBAC gap                                                               |
| UI: creation wizard                | `business-create.tsx` — minimal name form            | Missing metadata fields                                                |

**Frontend:** `/home` business picker, `/businesses` admin — maps to blueprint project list, gated by `business-setup` role.

---

#### Module 2 — WBS & Activities — **NOT STARTED**

No WBS tree, activities, predecessors, P6/MSP import. Dynamic `TableDefinition` is **not** a WBS substitute.

---

#### Module 3 — Schedule Control — **NOT STARTED**

No baselines, Gantt, float, critical path, SPI at schedule level.

---

#### Module 4 — Daily Field Report — **PARTIAL (~20%), MISALIGNED**

| Blueprint                                            | Current (`DepartmentActivityRecord`)                                        |
| ---------------------------------------------------- | --------------------------------------------------------------------------- |
| Unified `daily_reports` per project/date/shift       | Per-department activity logs (6 fixed departments)                          |
| Sub-entities: labor, equipment, materials, incidents | Single flat record: date, location, activity, contractor, unit, description |
| Weather, shift, approval workflow (draft→approved)   | No workflow; create-only UI (no edit/delete in UI)                          |
| Links to WBS `activity_id`                           | No activity link                                                            |
| Offline mobile form                                  | None                                                                        |
| Photo attachments                                    | None                                                                        |
| `POST .../sync-batch`                                | None                                                                        |
| Approval triggers progress recalc                    | None                                                                        |

**Frontend:** `department-page.tsx` — filters, Excel import/export, PDF daily/weekly reports. This is a **department activity log**, not IPCAS daily field report.

**Naming risk:** Calling this "daily report" in UI/docs will confuse sprint planning (blueprint Sprint 4–5). Use "department activity log" in `docs/ipcas-scope-map.md`.

---

#### Module 5 — Physical Progress Control — **NOT STARTED**

No weighted progress, S-curve, variance alerts. Department PDF reports are activity listings, not progress curves.

---

#### Module 6 — Cost & Budget Control — **NOT STARTED**

Assignment model has `wage`/`wage_type` fields (HR data) but no budgets, actual costs, EVM.

---

#### Module 7 — Cash Flow — **NOT STARTED**

---

#### Module 8 — Contracts & IPCs — **NOT STARTED**

---

#### Module 9 — Human Resources — **PARTIAL (~25%)**

| Blueprint                          | Current                                                        |
| ---------------------------------- | -------------------------------------------------------------- |
| Daily headcount by discipline      | Not implemented                                                |
| Planned vs actual labor-hours      | Not implemented                                                |
| Labor productivity metrics         | Not implemented                                                |
| Workforce reports by subcontractor | Not implemented                                                |
| Per-project membership + roles     | `UserBusinessAssignment` + `BusinessJobPosition` — **partial** |
| App-wide HR user admin             | `hr/users.tsx` — list, create, Excel import                    |

**Gaps:**

- App-level `/hr/job-positions` is a **placeholder** (no API)
- Business-level job positions CRUD exists; assignment create/update/delete hooks exist but **no UI**
- `engineer`, `accountant` roles defined in frontend but **unused** in guards
- `site_engineer` exists in backend migrations but not in frontend `roles.ts`

---

#### Module 10 — Equipment — **NOT STARTED**

No equipment registry or utilization logs.

---

#### Module 11 — Materials & Warehouse — **PARTIAL (~15%), MISALIGNED**

| Blueprint                                             | Current                                                          |
| ----------------------------------------------------- | ---------------------------------------------------------------- |
| `inventory_transactions` ledger (in/out/waste/adjust) | None                                                             |
| Running balance per material per project              | None                                                             |
| Critical stock alerts                                 | None                                                             |
| Warehouse department                                  | `business-warehouse.tsx` = **activity log**, not stock inventory |

**Three separate implementations (none match blueprint):**

1. **Legacy global** `Item` + `/api/items/` — not business-scoped
2. **Dynamic tables** — optional `warehouse` template creates Locations + Inventory tables as generic rows
3. **`SpaceMaterialRequest`** — backend CRUD exists (`/api/businesses/{id}/space-material-requests/`) but **zero frontend routes** — dead API from UI perspective

**Monorepo action:** Document that `warehouse` department route ≠ Module 11. Plan either a new `space-material-requests` UI or rename routes to avoid confusion.

---

#### Module 12 — Procurement — **NOT STARTED**

`SpaceMaterialRequest` fields resemble a material request grid but lack PR→PO→delivery workflow.

---

#### Module 13 — Subcontractor Control — **NOT STARTED**

`contractor` field on activity records is free text only.

---

#### Module 14 — Delays, Barriers & Risk — **NOT STARTED**

---

#### Module 15 — Document Control — **NOT STARTED**

---

#### Module 16 — Economic Engine — **NOT STARTED**

---

#### Module 17 — Dashboard & Alerts — **NOT STARTED**

| Blueprint                     | Current                                                                                       |
| ----------------------------- | --------------------------------------------------------------------------------------------- |
| Executive 10-KPI dashboard    | `/home` = business picker only                                                                |
| Role-based dashboard variants | i18n keys exist (`visitorSection`, `managerSection`, `commentorSection`) but **not rendered** |
| 15+ alert rules               | None                                                                                          |

---

#### Module 18 — Access Control — **PARTIAL (~30%)**

| Blueprint                          | Current                                                                                       |
| ---------------------------------- | --------------------------------------------------------------------------------------------- |
| System → Project → Custom override | Global Django Groups only; per-business via assignment visibility                             |
| Permission matrix by module + CRUD | `usePermission()` defined but **never used**; backend dynamic rows use `IsAuthenticated` only |
| Per-project multiple roles         | One assignment per user per business                                                          |
| Audit trail                        | None                                                                                          |
| Role templates by project type     | None                                                                                          |

**Role alignment table:**

| Blueprint / backend Group | Frontend `ROLES` enum | Enforced in UI/API?                     |
| ------------------------- | --------------------- | --------------------------------------- |
| `admin`                   | `admin`               | HR routes, backend HR endpoints         |
| `hr`                      | `hr`                  | HR routes                               |
| `manager`                 | `manager`             | Dynamic table row edit only             |
| `visitor`                 | `visitor`             | Backend read-only guard; minimal UI use |
| `commentor`               | **missing from enum** | i18n + backend class exist; **unused**  |
| `business-setup`          | `business-setup`      | Business admin routes                   |
| `engineer`, `accountant`  | defined               | **unused**                              |
| `site_engineer`           | **missing**           | Backend migration only                  |

**Auth gaps (both repos):**

- Password reset: `POST /api/auth/reset-password/` returns **501**; forgot-password logs token to console
- Token refresh endpoint exists; frontend `restoreSession` is **no-op**
- JWT blacklist configured but `token_blacklist` app not installed

---

### Section 5–6 — Engineering Tasks & Sprint Plan vs Reality

The blueprint assumes **13 sprints × 2 weeks** with a 10-person team. Current code roughly corresponds to **fragments of Sprint 1–2**:

| Sprint / tasks                       | Relevant current work                    | Still missing from sprint goal                                                              |
| ------------------------------------ | ---------------------------------------- | ------------------------------------------------------------------------------------------- |
| Sprint 1 (F-01–F-08)                 | JWT login, SQLite DB, CORS               | Full schema, gateway, S3, audit log, message bus — **Postgres addressed in monorepo merge** |
| Sprint 2 (C-01, UI-02, UI-15)        | Business CRUD, assignments, partial RBAC | WBS, members with roleIds, access control admin UI                                          |
| Sprint 4–5 (daily report + offline)  | Department activity logs (online only)   | Unified daily report, approval workflow, offline sync                                       |
| Sprint 10 (materials, equipment, HR) | HR assignments partial                   | Inventory ledger, equipment, labor metrics                                                  |

**Monorepo README should state:** sprint plan in blueprint is the **delivery roadmap**, not a description of what is already built.

---

### Cross-cutting code issues to fix or document during merge

| Issue                                    | Location                                               | Blueprint impact                         |
| ---------------------------------------- | ------------------------------------------------------ | ---------------------------------------- |
| Orphan route files not wired             | `auth.routes.ts`, `business.routes.ts`, `hr.routes.ts` | Cleanup opportunity; no blueprint impact |
| `i18Sync.tsx` not mounted                | `src/components/i18Sync.tsx`                           | i18n works via `i18n.ts` directly        |
| Dead `src/app/i18.ts` stub               | frontend                                               | Remove or wire                           |
| Stale OpenAPI "MongoDB" tag              | `core/config/settings.py`                              | Misdocuments architecture                |
| Backend cursor rules say FastAPI/MongoDB | `inventory-backend/.cursor/rules/`                     | Misleads future IPCAS implementation     |
| README on backend outdated               | `inventory-backend/README.md`                          | Lists future features that exist         |

---

### Monorepo-specific alignment actions (add to migration)

1. **Add `docs/ipcas-scope-map.md`** — term mapping, module status table (this audit), "do not rename during merge" list.
2. **Move blueprint to `docs/IPCAS_Engineering_Blueprint.md`** — single source of truth at monorepo root.
3. **Root README** — "Current implementation scope" vs "Blueprint target" sections with link to scope map.
4. **Fix Cursor rules** — Django/DRF/PostgreSQL-target; remove FastAPI/MongoDB guidance from backend rule.
5. **Do not** introduce blueprint `/projects` API paths during merge — plan as a separate API versioning task (v2 or alias layer).
6. **`packages/api-types`** — generate from live OpenAPI only; optionally add comment headers linking types to blueprint module numbers later.
7. **Label UI honestly** — avoid "Daily Report" / "Inventory" labels for department logs until Module 4/11 are properly implemented (can be a follow-up PR, not blocking merge).

```mermaid
flowchart TB
  subgraph implemented [Implemented today]
    Auth[JWT Auth + Groups]
    Biz[Business CRUD]
    Schema[Dynamic Tables]
    DeptLog[Department Activity Logs]
    HR[HR Users + Assignments partial]
  end
  subgraph blueprint [IPCAS Blueprint target]
    WBS[WBS + Activities]
    DailyReport[Unified Daily Reports]
    Cost[Cost + EVM]
    IPC[Contracts + IPCs]
    Econ[Economic Engine]
  end
  Biz -.->|"rename target: Project"| WBS
  DeptLog -.->|"evolve toward"| DailyReport
  Schema -.->|"not substitute for"| WBS
```

---

## Target layout

```
building-management/                 # new GitHub repo (squash import)
├── apps/
│   ├── web/                       # former building-management-front
│   │   ├── package.json
│   │   ├── pnpm-lock.yaml
│   │   ├── vite.config.ts
│   │   ├── Dockerfile
│   │   └── src/
│   └── api/                       # former inventory-backend
│       ├── requirements.txt
│       ├── runserver.sh
│       └── core/                  # Django project (unchanged internal layout)
├── packages/                      # empty for now; future shared TS types from /api/schema/
├── docs/
│   ├── IPCAS_Engineering_Blueprint.md   # moved from apps/web
│   └── ipcas-scope-map.md               # blueprint vs code mapping (new)
├── .github/workflows/
│   ├── ci.yml
│   └── docker.yml                 # optional
├── docker-compose.yml
├── .env.example
├── pnpm-workspace.yaml
├── package.json                   # root orchestration only
├── README.md
└── .gitignore
```

```mermaid
flowchart LR
  subgraph monorepo [building-management monorepo]
    Web[apps/web]
    Api[apps/api]
    PG[(PostgreSQL)]
  end
  Web -->|"VITE_API_BASE_URL /api"| Api
  Api --> PG
  Dev[docker-compose] --> Web
  Dev --> Api
  Dev --> PG
```

**Why this structure:** `apps/*` is the standard for polyglot monorepos. Keeping Django's `core/` package inside `apps/api/` avoids a large internal rename. `packages/` is reserved for future OpenAPI-generated TypeScript types without blocking the initial merge.

## Tooling choices

| Layer              | Tool                                                                        | Rationale                                                               |
| ------------------ | --------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| JS workspace       | **pnpm workspaces**                                                         | Frontend already uses pnpm + `pnpm-lock.yaml`                           |
| Task orchestration | **Root `package.json` + `concurrently`**                                    | Only 2 apps; Turborepo/Nx adds complexity with little gain at this size |
| Python deps        | **`requirements.txt` in `apps/api`** + `psycopg[binary]`, `dj-database-url` | PostgreSQL driver + `DATABASE_URL` parsing                              |
| Database           | **PostgreSQL 16** (Docker locally; managed Postgres in prod)                | Matches IPCAS blueprint; no SQLite fallback                             |
| Local dev          | **`docker-compose.yml`** with `postgres`, `api`, `web`                      | Postgres required before API starts                                     |
| CI                 | **GitHub Actions**                                                          | Neither repo has CI today; add from scratch                             |

Root [`package.json`](file:///home/hossein/Desktop/projects/mehdi/building-management/package.json) scripts (conceptual):

```json
{
  "scripts": {
    "dev": "concurrently -n web,api -c blue,green \"pnpm --filter web dev\" \"pnpm --filter api dev\"",
    "dev:web": "pnpm --filter web dev",
    "dev:api": "pnpm --filter api dev",
    "build": "pnpm --filter web build",
    "typecheck": "pnpm --filter web typecheck"
  }
}
```

`apps/api/package.json` is a thin wrapper so pnpm can run the Python server:

```json
{
  "name": "api",
  "private": true,
  "scripts": {
    "dev": "bash ./runserver.sh",
    "migrate": "cd core && ../.venv/bin/python manage.py migrate",
    "seed": "cd core && ../.venv/bin/python manage.py seed_rbac_dev"
  }
}
```

Root `package.json` adds DB lifecycle helpers:

```json
{
  "scripts": {
    "db:up": "docker compose up -d postgres",
    "db:migrate": "pnpm --filter api migrate",
    "db:seed": "pnpm --filter api seed",
    "dev": "concurrently -n web,api -c blue,green \"pnpm --filter web dev\" \"pnpm --filter api dev\""
  }
}
```

**Local dev workflow:** `pnpm db:up` → wait for Postgres healthy → `pnpm db:migrate` → `pnpm db:seed` (first time) → `pnpm dev`.

## Migration steps (squash import)

### Phase 1 — Scaffold new repo

1. Create a new directory `building-management/` (sibling to current repos or replace after copy).
2. `git init` on `main`.
3. Add root files:
   - [`pnpm-workspace.yaml`](https://pnpm.io/pnpm-workspace_yaml): `packages: ["apps/*", "packages/*"]`
   - Root `package.json` with `concurrently` dev dependency
   - Unified [`.gitignore`](file:///home/hossein/Desktop/projects/mehdi/building-management/.gitignore) merging both repos (`.env`, `node_modules`, `build`, `.react-router`, `.venv`, `__pycache__`) — drop `db.sqlite3` from tracked concerns; keep ignored for legacy local files
   - [`.env.example`](file:///home/hossein/Desktop/projects/mehdi/building-management) documenting all cross-app vars including **PostgreSQL** (see below)

### Phase 2 — Move applications

1. **Frontend → `apps/web/`**
   - Copy entire [building-management](file:///home/hossein/Desktop/projects/mehdi/building-management) tree except `.git/`
   - Rename package in `apps/web/package.json` to `"name": "web"`
   - Move [`.npmrc`](file:///home/hossein/Desktop/projects/mehdi/building-management/.npmrc) to root or keep in `apps/web` (Liara mirror registry)
   - No source path changes needed — `@/` and `~/*` aliases are relative to `apps/web/`

2. **Backend → `apps/api/`**
   - Copy entire [inventory-backend](file:///home/hossein/Desktop/projects/mehdi/inventory-backend) tree except `.git/`
   - Update [`runserver.sh`](file:///home/hossein/Desktop/projects/mehdi/inventory-backend/runserver.sh) paths if needed (`.venv` stays at `apps/api/.venv`)
   - Add missing `drf-spectacular-sidecar` to [`requirements.txt`](file:///home/hossein/Desktop/projects/mehdi/inventory-backend/requirements.txt) (referenced in settings but not pinned)

   - Add missing `drf-spectacular-sidecar` to [`requirements.txt`](file:///home/hossein/Desktop/projects/mehdi/inventory-backend/requirements.txt) (referenced in settings but not pinned)
   - Add **`psycopg[binary]>=3.1`** and **`dj-database-url>=2.1`** for PostgreSQL

### Phase 3 — Unify configuration + PostgreSQL

**Environment variables** (root `.env.example`):

| Variable               | App | Purpose                                  |
| ---------------------- | --- | ---------------------------------------- |
| `VITE_API_BASE_URL`    | web | API base URL (build-time)                |
| `SECRET_KEY`           | api | Django secret                            |
| `DEBUG`                | api | Dev mode                                 |
| `ALLOWED_HOSTS`        | api | Host allowlist                           |
| `CORS_ALLOWED_ORIGINS` | api | Must include web origin                  |
| `FRONTEND_URL`         | api | Password-reset links (future)            |
| `DATABASE_URL`         | api | **Required.** Postgres connection string |

Example `.env.example` values:

```bash
DATABASE_URL=postgres://ipcas:ipcas@localhost:5432/ipcas
POSTGRES_USER=ipcas
POSTGRES_PASSWORD=ipcas
POSTGRES_DB=ipcas
```

**Backend settings** — refactor [`core/config/settings.py`](file:///home/hossein/Desktop/projects/mehdi/inventory-backend/core/config/settings.py):

Replace hardcoded SQLite block with:

```python
import dj_database_url
import os

DATABASES = {
    "default": dj_database_url.config(
        default=os.environ["DATABASE_URL"],
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

- Remove `django.db.backends.sqlite3` entirely — **no SQLite fallback** (aligns with blueprint).
- Existing `JSONField` usage (`DynamicTableRow.data`, `UserBusinessAssignment.tools`) works natively on PostgreSQL.
- No model/migration changes expected for the SQLite → Postgres switch (Django migrations are DB-agnostic for current schema).

**`runserver.sh`** — load root `.env` if present (e.g. `set -a; source ../../.env 2>/dev/null; set +a`) so `DATABASE_URL` is available when running API outside Docker.

**Frontend API client** — no code change needed; [`api-client.ts`](file:///home/hossein/Desktop/projects/mehdi/building-management/src/app/lib/api-client.ts) already reads `VITE_API_BASE_URL`.

**Cursor rules** — merge [`.cursor/rules/`](file:///home/hossein/Desktop/projects/mehdi/building-management/.cursor/rules) from both repos into monorepo root; update paths from `core/` → `apps/api/core/` and `src/` → `apps/web/src/`. **Rewrite backend rule** to match actual stack (Django 4.2 + DRF + SQLite/Postgres), not FastAPI/MongoDB aspirational text.

**Blueprint docs (Phase 3b)** — create `docs/ipcas-scope-map.md` from the audit above; move [IPCAS_Engineering_Blueprint.md](file:///home/hossein/Desktop/projects/mehdi/building-management/IPCAS_Engineering_Blueprint.md) to `docs/`; add scope disclaimer to root README.

### Phase 4 — Docker (with PostgreSQL)

1. **Web Dockerfile** ([current file](file:///home/hossein/Desktop/projects/mehdi/building-management/Dockerfile)) — rewrite for pnpm:
   - `corepack enable && corepack prepare pnpm@latest --activate`
   - `COPY pnpm-lock.yaml` instead of `package-lock.json`
   - `pnpm install --frozen-lockfile`
   - Set build arg `VITE_API_BASE_URL` for production API URL

2. **API Dockerfile** (new `apps/api/Dockerfile`):
   - Python 3.12 slim base
   - `pip install -r requirements.txt`
   - Entrypoint script: wait for Postgres (`pg_isready` or retry loop) → `manage.py migrate` → `gunicorn config.wsgi:application` from `core/`

3. **`docker-compose.yml`** at root — **three services**:

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-ipcas}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-ipcas}
      POSTGRES_DB: ${POSTGRES_DB:-ipcas}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: ./apps/api
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgres://${POSTGRES_USER:-ipcas}:${POSTGRES_PASSWORD:-ipcas}@postgres:5432/${POSTGRES_DB:-ipcas}
      CORS_ALLOWED_ORIGINS: http://localhost:5173
    ports:
      - "8000:8000"

  web:
    build: ./apps/web
    depends_on: [api]
    environment:
      VITE_API_BASE_URL: http://localhost:8000/api
    ports:
      - "5173:5173" # or 3000 for production build

volumes:
  pgdata:
```

**Dev without full compose:** developers can run only `docker compose up -d postgres` and point local API at `DATABASE_URL=postgres://ipcas:ipcas@localhost:5432/ipcas`.

### Phase 5 — CI/CD

Add [`.github/workflows/ci.yml`](file:///home/hossein/Desktop/projects/mehdi/building-management):

```yaml
# Conceptual jobs
jobs:
  web:
    - pnpm install --frozen-lockfile
    - pnpm --filter web typecheck
    - pnpm --filter web build

  api:
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: ipcas
          POSTGRES_PASSWORD: ipcas
          POSTGRES_DB: ipcas_test
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U ipcas -d ipcas_test"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    env:
      DATABASE_URL: postgres://ipcas:ipcas@localhost:5432/ipcas_test
      SECRET_KEY: ci-test-secret
    steps:
      - pip install -r apps/api/requirements.txt
      - python apps/api/core/manage.py check
      - python apps/api/core/manage.py migrate
      - python apps/api/core/manage.py test
```

Path filters (`paths: apps/web/**`, `apps/api/**`) keep CI fast as the repo grows.

### Phase 6 — Publish and archive

1. Create new GitHub repo (e.g. `Itshossein128/building-management`).
2. Single squash commit: `chore: initial monorepo import from front + back repos`.
3. Push `main`.
4. Archive `building-management-front` and `building-management-back` on GitHub with README pointers to the new repo.
5. Update local clones: remove old folders or repoint remotes.

## Post-migration improvements (optional, not blocking)

Aligned to blueprint gaps identified above:

| Priority | Item                                                                      | Blueprint module |
| -------- | ------------------------------------------------------------------------- | ---------------- |
| High     | Wire `SpaceMaterialRequest` UI or remove dead API                         | Module 11/12     |
| High     | Complete RBAC: `usePermission`, assignment CRUD UI, business list scoping | Module 18        |
| High     | Finish password reset + token refresh                                     | F-02             |
| Medium   | Rename UI labels: "department activity log" vs "daily report"             | Module 4         |
| Medium   | `packages/api-types` from `/api/schema/`                                  | API contract     |
| Low      | `Business` → `Project` rename (API v2)                                    | Module 1         |
| Low      | WBS, schedule, cost modules per sprint plan                               | Modules 2–8      |

Also: **Biome**, **Vitest**, **`uv`** for Python — tooling only, not blueprint features.

## Risks and mitigations

| Risk                                                                           | Mitigation                                                 |
| ------------------------------------------------------------------------------ | ---------------------------------------------------------- |
| Broken web Docker today                                                        | Fix as part of Phase 4 before relying on containers        |
| Hardcoded Django settings                                                      | Externalize in Phase 3; **require `DATABASE_URL`**         |
| Postgres not running locally                                                   | Document `pnpm db:up`; API entrypoint waits for healthy DB |
| Existing SQLite dev data not migrated                                          | Fresh `migrate` + `seed_rbac_dev` on new Postgres volume   |
| `drf_spectacular_sidecar` missing from requirements                            | Add during backend move                                    |
| Liara npm mirror in `.npmrc`                                                   | Keep at root; document for CI (`pnpm install` respects it) |
| Cursor plans reference old paths                                               | Update `.cursor/plans/` and rules in Phase 3               |
| Blueprint terminology vs code (`Project`/`Business`, daily report vs dept log) | Add `docs/ipcas-scope-map.md`; do not rename during merge  |
| Misleading cursor rules (FastAPI/MongoDB)                                      | Rewrite backend rule to Django/DRF in Phase 3              |
| `SpaceMaterialRequest` API with no UI                                          | Document as dead surface; plan UI or deprecate             |
| Warehouse route implies stock inventory                                        | Document mismatch with Module 11 in scope map              |

## Verification checklist

After migration, confirm:

- [ ] `docker compose up -d postgres` starts healthy Postgres on `:5432`
- [ ] `pnpm install` at root succeeds
- [ ] `pnpm db:migrate` applies all migrations to PostgreSQL
- [ ] `pnpm db:seed` creates dev RBAC groups/users (first-time setup)
- [ ] `pnpm dev` starts web on `:5173` and API on `:8000` against Postgres
- [ ] Login flow works (`POST /api/auth/login/`)
- [ ] `pnpm --filter web typecheck` passes
- [ ] `python apps/api/core/manage.py check` passes with `DATABASE_URL` set
- [ ] `docker compose up` serves web + api + postgres together
- [ ] CI green on `main` (api job uses Postgres service)

## Estimated effort

| Phase                   | Effort         |
| ----------------------- | -------------- |
| Scaffold + move (1–2)   | ~1 hour        |
| Config + PostgreSQL (3) | ~2.5 hours     |
| Docker (4)              | ~2.5 hours     |
| CI (5)                  | ~1.5 hours     |
| Publish + archive (6)   | ~30 min        |
| **Total**               | **~1.25 days** |
