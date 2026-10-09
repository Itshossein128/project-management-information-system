# Quickstart: Multi-Level Budget

## Prerequisites

- Postgres + Redis; API venv; migrated `cost_control`
- Project with `view_costs` / `edit_costs` / `approve_costs` member
- Optional: WBS, CBS, Contract for multi-level lines

## Happy path (manual / API)

1. `POST /budget-versions/` kind=`initial` → draft
2. `POST …/lines/` or `/budgets/bulk/` with `version_id` → add WBS/CBS lines
3. `POST …/submit/` → `POST …/approve/` as approver → `is_control=true`
4. `GET /budgets/remaining/` → see remaining before commitments
5. Attempt `PATCH` line on control version → `budget_version_locked`
6. `POST /budget-change-requests/` with reason, impact, affected_lines → submit → approve → new revised control version
7. `POST /budgets/transfers/` net-zero move between two lines on control version
8. `GET /budget-versions/compare/?left=&right=` → diffs

## Pytest focus

```bash
cd apps/api/core && ../.venv/bin/python -m pytest cost_control/tests/test_budget_versions.py cost_control/tests/test_budget_change_requests.py cost_control/tests/test_remaining_transfer.py -q
```

## UI

Costs → Budget tab: version selector, submit/approve actions, remaining panel, change-request panel; grid read-only when viewing approved control (edit only on draft).
