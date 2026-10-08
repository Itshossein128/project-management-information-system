# Quickstart Validation: HR & Capacity Gap Closure

**Feature**: `006-hr-capacity`  
**Date**: 2026-10-08

## Purpose

Validation guide for `/speckit-implement`. **Do not implement from this Spec Kit pass.**

## Prerequisites

- Specs **002** / **004** / **005** patterns available (audit/soft-delete, WBS, activities)
- Postgres + Redis; migrated DB; seeded users
- Auth as project member with `view_hr` / `edit_hr` / `approve_hr` / `view_wage` as needed
- Existing leave/OT and daily-report progress paths functional (regression)

## Suggested test map

| Story | Automated focus |
|-------|-----------------|
| US1 Person dossier | PATCH skills/org_unit/supervisor; inactive person rejected on new allocation |
| US2 Resource allocation | Create allocation with %; list by project; membership ≠ allocation |
| US3 Capacity + exception | 80% + 50% overlap → 409; approve exception → save with flag |
| US4 Wage ACL + estimate | No `view_wage` → wage omitted; missing rate → `missing_approved_rate`; labor headcount ≠ progress |

Contracts: [person-dossier.md](./contracts/person-dossier.md), [resource-allocations.md](./contracts/resource-allocations.md), [capacity-exceptions.md](./contracts/capacity-exceptions.md), [wage-acl-and-cost-estimate.md](./contracts/wage-acl-and-cost-estimate.md).  
Data model: [data-model.md](./data-model.md).

## Smoke commands (after implement)

```bash
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  hr/tests/test_person_dossier.py \
  hr/tests/test_resource_allocations.py \
  hr/tests/test_capacity_exceptions.py \
  hr/tests/test_wage_acl_and_cost_estimate.py \
  field_reports/tests/test_core_principles_unset_vs_zero.py \
  -q
pnpm typecheck
```

Optional UI: open project allocations panel; trigger capacity conflict; approve exception; confirm wage hidden without permission; fa/en labels.

## Expected outcomes

- SC-001–SC-005 covered by automated tests
- Over-capacity silent save impossible without approved exception
- Wage/rate values absent for users without `view_wage`
- Activity progress unchanged after allocation create and labor-only report edits
