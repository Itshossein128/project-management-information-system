# Verification: HR & Capacity Gap Closure

**Feature**: [spec.md](../spec.md)  
**Date**: 2026-10-08

| Success criterion | Evidence |
|-------------------|----------|
| SC-001 Capacity conflict visible | `hr/tests/test_resource_allocations.py::test_capacity_conflict_409` |
| SC-002 Exception required for over-capacity | `hr/tests/test_capacity_exceptions.py` (approve then allocate) |
| SC-003 Wage ACL | wage omit; create requires `edit_wage`; `daily_rate` redacted without `view_wage` |
| SC-004 Progress isolation | allocation + labor-headcount-only tests do not change `ActivityProgress` |
| SC-005 Dossier + allocation session | `test_person_dossier` + allocation create tests; UI route `resource-allocations` |

## Commands run

```bash
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  hr/tests/test_person_dossier.py \
  hr/tests/test_resource_allocations.py \
  hr/tests/test_capacity_exceptions.py \
  hr/tests/test_wage_acl_and_cost_estimate.py -q
# → 13 passed

pnpm exec tsc --noEmit -p apps/web/tsconfig.json
# → exit 0
```

## Spec Kit deferred (out of Specs 01–07 polish plan)

- Per-person attendance / shift ledger (FR-HR-006)
- Labor-by-contractor grid redesign
