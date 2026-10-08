# Quickstart validation: Daily Site Report Gap Closure

**Feature**: `007-daily-report-gaps`  
**Date**: 2026-10-08

Use this after implementation to prove FR-DR gap closure end-to-end. Design contracts: [contracts/](./contracts/). Data model: [data-model.md](./data-model.md).

## Prerequisites

- Postgres + Redis running; API venv; `.env` sourced (`DATABASE_URL`, etc.)
- Migrated DB with seed users/projects (`pnpm db:migrate`, `pnpm db:seed` if needed)
- Auth token for a project member with `edit_reports` + `approve_reports` (or two users)
- Project with at least one schedule activity and optional material with balance

## Setup

```bash
# from repo root — start services per AGENTS.md, then:
pnpm dev:api
pnpm dev:web
```

API docs: `http://localhost:8000/api/docs/`  
Base path: `/api/v1/projects/{projectId}/daily-reports/`

## Scenario A — Header + responsible + unset quantity (US1 / SC-001 / SC-004)

1. `POST daily-reports/` with `work_front`, weather, date, shift → **201**, status `draft`.
2. `POST .../activities/` with responsible_name, `quantity_measured=true`, quantity `10` → **201**.
3. `POST .../activities/` with `quantity_measured=false`, quantity `null` → **201**; GET shows null not `0`.
4. Attempt activity with `quantity_measured=true` and null quantity on submit → validation error `quantity_unset_invalid`.
5. Open form on mobile-width viewport: header work front + activity responsible editable.

**Expected**: Draft complete; unset ≠ zero.

## Scenario B — Lock + correction request (US2 / SC-002)

1. Submit → approve report (existing workflow) → `status=approved`, `is_locked=true`, `is_current=true`.
2. `PATCH` header or child → **403/400** `report_locked`.
3. `POST .../correction-requests/` with reason ≥ 10 chars → **201**, `result_report_id`, source `is_current=false`.
4. Edit result draft; submit; approve → result `approved` + `is_current=true`; source remains readable via `GET .../versions/`.
5. Second open correction while one open → **409** `correction_already_open`.

**Expected**: No direct edit of locked; prior version retained.

## Scenario C — Return, absence, site event (US3 / SC-003)

1. On a draft: material row `transaction_type=return` + `consumption_location`.
2. Labor row with `absence_count=2` (and another with `null`).
3. Incident/site event with `incident_type=barrier`, owner name, `due_date`.
4. GET detail → all three visible.
5. `GET .../materials/reconciliation/` → items with `match|mismatch|insufficient_data` (advisory).

**Expected**: Fields persist; reconciliation does not block save.

## Scenario D — Status copy + timestamps (US4)

1. Create draft; note `report_date` vs `created_at`.
2. Submit; note `submitted_at`.
3. Approve; UI shows locked label; `approved_at` set and distinct from `report_date`.

**Expected**: Locked semantics clear in fa/en; timestamps separate.

## Automated checks (implement time)

```bash
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest field_reports/tests/test_daily_report_gaps_*.py -q
```

Optional UI smoke: create → approve → correction path in Playwright if e2e added.

## Out of scope for this quickstart

- Weekly/monthly progress reports (08)
- HR named-person capacity (006)
- Full warehouse stock blocks
