# Verification evidence: 002-core-domain-principles

**Date**: 2026-10-08

## Automated tests

Command:

```bash
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  common/tests/test_money.py \
  common/tests/test_unset.py \
  common/tests/test_glossary_locale_keys.py \
  projects/tests/test_core_principles_*.py \
  notifications/tests/test_actionable_notifications.py \
  field_reports/tests/test_core_principles_unset_vs_zero.py \
  cost_control/tests/test_core_principles_duplicate_document.py \
  -q
```

**Result**: `35 passed` (2026-10-07)

## Success criteria mapping

| SC | Evidence |
|----|----------|
| SC-001 Glossary | `test_glossary_locale_keys.py` |
| SC-002 Soft-delete | `test_core_principles_wbs_soft_delete.py` |
| SC-003 Currency | `test_money.py`, `test_core_principles_currency_*` |
| SC-004 Tenancy | `test_core_principles_wbs_tenancy.py` |
| SC-005 Unset vs zero | `test_unset.py`, `test_core_principles_unset_vs_zero.py` |
| SC-006 Notifications | `test_actionable_notifications.py` |
| SC-007 Capabilities | `test_core_principles_capabilities_*.py` |
| SC-008 TDD | Tests authored before/with implementation; suite green |

## Manual / UI (optional smoke)

- [x] Project settings: currency select IRR/IRT
- [x] Project settings: capability toggles + fiscal lock form
- [x] FR-CORE-012: disabled capability hides matching project nav entries (`e2e/tests/core-capabilities-fiscal.spec.ts`)
- [x] FR-CORE-015: costs actual-create exposes corrective path under fiscal lock (`e2e/tests/core-capabilities-fiscal.spec.ts`)
- [ ] Notification panel shows owner / due / link when present
- [ ] FA/EN glossary spot-check on WBS / costs / IPC labels

## Migrations

- `projects.0007_core_domain_principles`
- `notifications.0002_core_domain_principles`
