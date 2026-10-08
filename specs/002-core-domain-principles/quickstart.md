# Quickstart Validation: Core Domain Principles & Glossary

**Feature**: `002-core-domain-principles`  
**Date**: 2026-10-07

## Purpose

Runnable validation guide for implementers after TDD stories land. **Do not run implementation from Spec Kit**; use this during `/speckit-implement`.

## Prerequisites

- Postgres on `5433` and Redis online (see `AGENTS.md`)
- API venv + `.env` with `DATABASE_URL`, `AUDIT_LOG_ASYNC=false`, `CELERY_TASK_ALWAYS_EAGER=true`
- Migrated + seeded DB (`pnpm db:migrate`, `pnpm db:seed`)
- Auth token for a project member and a user with `edit_project` (or admin)

## TDD loop (per story)

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest <path-to-new-failing-tests> -q
# expect FAIL
# implement minimal code
../.venv/bin/python -m pytest <path-to-new-failing-tests> -q
# expect PASS
```

## Suggested verification map

| Story | Automated | Manual / UI |
|-------|-----------|-------------|
| US1 Glossary | Locale key assertions / snapshot of critical keys | Spot-check WBS, costs, IPC labels fa/en |
| US2 Record hygiene | Soft-delete + tenancy pytest on WBS/sample model | Attempt delete approved row in UI |
| US3 Currency | `currency_mix_forbidden` unit/API tests | Amounts show unit on costs/cash views |
| US4 Unset vs zero | Serializer round-trip tests | Empty vs `0` on a sample numeric field |
| US5 Notifications | Create/list payload contract tests | Notification panel shows owner/due/link |
| US6 Capabilities | Disable → mutate 403/409; GET history 200 | Nav hides capability; history readable |
| US7 Fiscal + duplicate | Lock 409; corrective path; duplicate warning | Settings close period; retry tx with ack |

## Smoke commands (after implement)

```bash
# API tests for this feature (paths finalized in tasks.md)
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest projects/tests/test_core_principles_*.py notifications/tests/test_actionable_*.py common/tests/test_money*.py -q

# Frontend typecheck
pnpm typecheck
```

## Expected outcomes

- All story acceptance scenarios covered by automated tests that failed before implementation.
- SC-001–SC-008 checklist can be marked with evidence (pytest output + optional screenshot notes).
- No ERP/Excel work included.

## References

- [spec.md](./spec.md)
- [data-model.md](./data-model.md)
- [contracts/](./contracts/)
- [plan.md](./plan.md)
