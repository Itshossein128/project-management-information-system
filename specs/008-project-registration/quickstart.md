# Quickstart validation: Project Registration & Kickoff

**Feature**: `008-project-registration`  
**Date**: 2026-10-08

Use after implementation to prove FR-PRJ gap closure. Contracts: [contracts/](./contracts/). Data model: [data-model.md](./data-model.md).

## Prerequisites

- Postgres + Redis; API venv; `.env` sourced
- Migrated DB; seed users with `edit_project` + `approve_project`
- `pnpm dev:api` / `pnpm dev:web` as needed

## Scenario A — Draft create + activation gates (US1)

1. `POST /api/v1/projects/` with code/name/employer/dates → **201**, `status=draft`.
2. `POST …/submit/` → `pending_approval`.
3. `POST …/approve/` without PM/scope/amount → **400** `activation_gates_failed` with `missing` list.
4. PATCH draft/pending to set PM, `scope_description`, `contract_amount`; approve → `active`, `budget_approved_at` set.
5. Attempt lock baseline on a **draft** project → **400** `project_not_active_for_baseline`.

## Scenario B — Kickoff charter (US2)

1. `PUT …/kickoff-charter/` with all six text fields → **200/201**.
2. `GET …/kickoff-charter/` → fields persist.
3. On overview UI, charter panel shows saved values.

## Scenario C — Protected field change request (US3)

1. On active project, `PATCH` `employer` or `contract_amount` → **400** `protected_field_requires_change_request`.
2. `POST …/change-requests/` with reason ≥ 10 and `proposed_changes` → **201**.
3. Submit + approve with `approve_project` → project field updated; CR `approved`.
4. Second open CR while one open → **409** `change_request_already_open`.

**UI covered:** Playwright `e2e/tests/project-registration.spec.ts` — active settings show protected fields read-only; change-request create → submit → approve updates employer.

## Scenario D — Suspend / archive (US4)

1. Active → `POST …/suspend/` → suspended; lock baseline → **400**.
2. `POST …/resume/` → active (gates still hold).
3. `POST …/archive/` → archived; non-admin PATCH → **403** `project_archived`.
4. Duplicate `project_code` on create → clear uniqueness error.

## Automated checks

```bash
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest projects/tests/test_project_registration_*.py -q
```

**Playwright (UI):** `apps/web/e2e/tests/project-registration.spec.ts` covers create-wizard FR-PRJ-001 fields (currency / owning unit / contract number / PM), draft settings identity fields + overview purpose/scope, and active-project change-request create→submit→approve for protected employer.

```bash
cd apps/web && CI= pnpm exec playwright test e2e/tests/project-registration.spec.ts --workers=1
```

## Out of scope for this quickstart

- WBS / schedule CR detail (04/05)
- Line-item budget (09)
- Full contract commercial module (10)
