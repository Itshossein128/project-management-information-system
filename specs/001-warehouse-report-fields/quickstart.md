# Quickstart: Warehouse Report Fields

**Feature**: `001-warehouse-report-fields`  
**Date**: 2026-10-01

Validation guide after implementation. See [data-model.md](./data-model.md) and [contracts/department-activity-records.md](./contracts/department-activity-records.md) for field and API details.

## Prerequisites

- PostgreSQL and Redis running (see `AGENTS.md`)
- Root `.env` with `DATABASE_URL`, `AUDIT_LOG_ASYNC=false`, `CELERY_TASK_ALWAYS_EAGER=true`
- API venv at `apps/api/.venv`
- Dev user from seed (e.g. phone `+10000000001` / `devpass123`) and a project with warehouse access

## Setup

```bash
# From repo root
pnpm db:migrate
pnpm dev:api    # :8000
pnpm dev:web    # :5173
```

## Automated tests (TDD evidence)

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest inventory/tests.py -k "warehouse or DepartmentActivity" -q
```

**Expect**:
- Warehouse create succeeds with the eight-field payload
- Both quantities zero / negatives / missing required fields → `400`
- Non-warehouse create still requires location / activity_description / contractor
- Warehouse export headers and import create path pass
- Existing generic department activity tests still pass

## Manual API checks

1. Obtain JWT and a `project_id`.
2. `POST /api/v1/projects/{project_id}/department-activity-records/` with warehouse body from the contract → `201`.
3. `GET ...?department=warehouse` → list shows warehouse fields; legacy columns empty.
4. `GET .../export/?department=warehouse` → Excel headers match warehouse set.
5. `POST .../import/?department=warehouse` with a matching workbook → `created ≥ 1`.
6. Repeat a buildings create with the old payload → still works; warehouse-only fields empty/`0`.

## Manual UI checks

1. Open project → Warehouse department page.
2. Create form shows only: تاریخ، نوع مصالح، ورودی، واحد، خروجی، محل مصرف، تامین‌کننده، توضیحات.
3. Submit valid row → appears in table with matching columns.
4. Submit with both quantities empty/zero → validation message, no create.
5. Switch language fa/en → labels correct; date picker still works.
6. Open Buildings (or another) department → old form/columns unchanged.

## Reports

1. Create warehouse records dated yesterday and within the last 7 days.
2. Download daily and weekly reports for `department=warehouse`.
3. Confirm PDF columns reflect material movement fields, not contractor/activity description.

## Done when

- [x] Targeted pytest suite green for warehouse + regression
- [x] Migration applied on dev DB
- [x] UI create/list verified in Persian and English for warehouse
  - Evidence (2026-10-01): Playwright headless smoke against local `:5173` / project `c7c0a9b9-…` — warehouse table columns + create modal fields match warehouse set (no legacy location/contractor/activity) in both `fa` and `en`; Jalali date control present/clickable.
- [x] Non-warehouse department smoke create still works
- [x] Excel round-trip smoke for one warehouse file succeeds
