# Traceability Matrix (T075)

Evidence recorded against the final implementation tree on 2026-10-28.

| Item | Requirement / Scenario | Evidence & Test Suite | Final Tree Status |
|---|---|---|---|
| **G01 / US1** | Offline draft entry, stable UUIDs, storage error input retention, interrupted requests | `apps/web/e2e/tests/unit-offline-entry.spec.ts` (5 passed), `sub_reports/tests/test_offline_unit_draft.py` (4 passed) | ✓ VERIFIED GREEN |
| **G02 / SC-01** | Targeted 10-operation sync across activities/labor/materials, exact acks, no false success | `apps/web/e2e/tests/unit-offline-ten-operations.spec.ts` (1 passed), `sub_reports/tests/test_sync_operations_api.py` (2 passed) | ✓ VERIFIED GREEN |
| **G03 / G04** | Derived readonly protection, summary aggregation preservation, unchanged attachment refs | `field_reports/tests/test_daily_report_derived_readonly.py` (2 passed), `field_reports/tests/test_unit_report_aggregation_eligibility.py` (8 passed), `field_reports/tests/test_summary_attachment_counts.py` (6 passed) | ✓ VERIFIED GREEN |
| **G05 / SC-04** | Concurrency control: parent lock protocol, approve vs sync race, concurrent drafts | `sub_reports/tests/test_unit_report_concurrency.py` (7 passed), `sub_reports/tests/test_sync_lock_contract.py` (2 passed) | ✓ VERIFIED GREEN |
| **G06 / SC-03** | Row validation errors: stable field error, single-row retry without resending successes | `apps/web/e2e/tests/unit-offline-row-retry.spec.ts` (1 passed), `sub_reports/tests/test_sync_operation_validation.py` (1 passed), `apps/web/src/app/lib/__tests__/offlineRowRetry.test.ts` (2 passed) | ✓ VERIFIED GREEN |
| **G07 / G08 / SC-02** | Local draft recovery: profile reopen, offline refresh, base/overlay and tombstone reconciliation | `apps/web/e2e/tests/unit-offline-recovery.spec.ts` (1 passed), `apps/web/src/app/lib/__tests__/offlineHydration.test.ts` (4 passed) | ✓ VERIFIED GREEN |
| **G09** | Idempotency & predecessor chains: create->edit->delete, same-ID replay, client row mapping | `sub_reports/tests/test_sync_operation_idempotency.py` (3 passed), `sub_reports/tests/test_sync_concurrent_replay.py` (1 passed) | ✓ VERIFIED GREEN |
| **G10 / SC-05** | Conflict handling: section comparison, explicit scope confirmation, correction transfer | `apps/web/e2e/tests/unit-offline-conflict.spec.ts` (1 passed), `sub_reports/tests/test_offline_correction_transfer.py` (1 passed), `apps/web/src/app/lib/__tests__/offlineConflictResolution.test.ts` (1 passed) | ✓ VERIFIED GREEN |
| **G11 / SC-06** | Recovery from crash/interruption: claim leasing, fencing stale owner, abandoned recovery | `apps/web/e2e/tests/unit-offline-interruption.spec.ts` (1 passed), `apps/web/src/app/lib/__tests__/offlineClaims.test.ts` (2 passed) | ✓ VERIFIED GREEN |
| **G12** | Local migration & legacy safety: schema upgrade abort recovery, unknown owner quarantine | `apps/web/e2e/tests/unit-offline-legacy-upgrade.spec.ts` (1 passed), `apps/web/src/app/lib/__tests__/offlineMigration.test.ts` (5 passed) | ✓ VERIFIED GREEN |
| **G13 / SC-07** | Bilingual accessible status: yellow cloud indicator, accessible role/labels in FA and EN | `apps/web/e2e/tests/unit-offline-status.spec.ts` (1 passed), `apps/web/src/app/locales/fa.json`, `apps/web/src/app/locales/en.json` | ✓ VERIFIED GREEN |

## Backend Migration & Schema Traceability

- Migration backfill and rollback preservation verified: `sub_reports/tests/test_offline_sync_migrations.py` (3 passed).
- Dry-run migration check verified: `python manage.py makemigrations --check --dry-run` reported `No changes detected`.
- Type safety verified: `pnpm typecheck` exited with code 0 across the monorepo.
