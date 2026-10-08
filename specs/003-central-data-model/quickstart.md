# Quickstart Validation: Central Data Model

**Feature**: `003-central-data-model`  
**Date**: 2026-10-07

## Purpose

Validation guide for `/speckit-implement`. **Do not implement from this Spec Kit pass.**

## Prerequisites

- Feature **002** money/soft-delete helpers available (or equivalent)
- Postgres + Redis; migrated DB; seeded users
- Auth as project member with cost/contract/project edit as needed

## Suggested test map

| Story | Automated focus |
|-------|-----------------|
| US1 Navigation/portfolio | navigation endpoint; activity embeds; portfolio summary ≥2 projects |
| US2 IPC collections | two collections; original IPC amounts unchanged; remaining |
| US3 CBS/commitment/payment | CBS tree CRUD; commitment≠actual; payment remaining |
| US4 References | ContractType create + contract FK; Unit select |
| US5 Org/Stakeholder | OrganizationUnit create; stakeholder CRUD; owning_unit on project |

## Smoke commands (after implement)

```bash
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  projects/tests/test_central_data_*.py \
  contracts/tests/test_ipc_collections*.py \
  cost_control/tests/test_cbs*.py \
  cost_control/tests/test_commitment*.py \
  master_data/tests/test_org_refs*.py \
  -q
pnpm typecheck
```

## Expected outcomes

- SC-001–SC-005 evidenced by pytest (and optional UI smoke)
- No ERP/Excel scope creep

## References

- [spec.md](./spec.md) · [data-model.md](./data-model.md) · [contracts/](./contracts/) · [plan.md](./plan.md)
