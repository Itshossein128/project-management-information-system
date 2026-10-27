# Final checks for phases 10 and 11 (T074)

Evidence recorded against the final implementation tree on 2026-10-28.

## 1. Summary of Verification Runs

| Check | Command | Result |
|---|---|---|
| Frontend Canonical Tests | `OFFLINE_TEST_ORIGIN=http://127.0.0.1:5198 node --experimental-strip-types --test apps/web/src/app/lib/__tests__/*.test.ts` | 40 passed across 10 suites |
| Backend Concurrency & Lock Contract | `pytest sub_reports/tests/test_unit_report_concurrency.py sub_reports/tests/test_sync_lock_contract.py -v` | 9 passed |
| Backend Foundation, Draft & API | `pytest sub_reports/tests/test_offline_sync_foundation.py sub_reports/tests/test_offline_unit_draft.py sub_reports/tests/test_sync_operations_api.py -v` | 14 passed |
| Backend Idempotency & Chains | `pytest sub_reports/tests/test_sync_operation_idempotency.py -v` | 3 passed |
| Backend Validation, Replay & Correction | `pytest sub_reports/tests/test_sync_operation_validation.py sub_reports/tests/test_sync_concurrent_replay.py sub_reports/tests/test_offline_correction_transfer.py -v` | 3 passed |
| Backend Derived Protection & Isolation | `pytest field_reports/tests/test_daily_report_derived_readonly.py field_reports/tests/test_unit_report_aggregation_eligibility.py field_reports/tests/test_summary_attachment_counts.py sub_reports/tests/test_offline_target_isolation.py -v` | 19 passed |
| Backend Migrations | `pytest sub_reports/tests/test_offline_sync_migrations.py -v` | 3 passed |
| Schema Drift Check | `python manage.py makemigrations --check --dry-run` | `No changes detected` |
| TypeScript Typecheck | `pnpm typecheck` | 0 errors (Exit code 0) |
| Playwright E2E Browser Suite | `pnpm exec playwright test --config apps/web/e2e/playwright.config.ts apps/web/e2e/tests/unit-offline-*.spec.ts` | 12 passed across 8 spec files |

## 2. E2E Browser Test Breakdown (12 passed)

- `unit-offline-entry.spec.ts` (5 passed):
  - offline entry on electrical unit page stores draft and operations with stable UUIDs
  - storage failure retains user input without silent clearing
  - general section saves a new row while offline
  - machinery section queues a new row while offline
  - interrupted draft request retains a durable local operation (via fallback on network interruption)
- `unit-offline-recovery.spec.ts` (1 passed):
  - refresh and persistent-profile reopen restore header, rows, and tombstones offline
- `unit-offline-status.spec.ts` (1 passed):
  - pending row shows named yellow cloud and distinct keyboard-focusable statuses across FA and EN locales
- `unit-offline-ten-operations.spec.ts` (1 passed):
  - reconnect sends ten activity, labor, and material operations once without duplicate writes
- `unit-offline-row-retry.spec.ts` (1 passed):
  - shows stable field error, blocks dependent operations, and does not toast false success when zero operations synced
- `unit-offline-conflict.spec.ts` (1 passed):
  - shows section rows, comparison table, and requires explicit confirmation before choosing a side
- `unit-offline-interruption.spec.ts` (1 passed):
  - reopens same profile and recovers in-flight syncing operations without abandonment
- `unit-offline-legacy-upgrade.spec.ts` (1 passed):
  - keeps ambiguous legacy payload out of automatic queue, quarantining unverified ownership
