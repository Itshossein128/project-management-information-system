# Migration evidence (T073)

From `apps/api/core`, with the project `.env` loaded:

`pytest sub_reports/tests/test_offline_sync_migrations.py -v`

Result: `3 passed in 124.66s`.
- `test_expand_preserves_historical_data_and_backfills_tokens`: verifies that schema expansion and token backfill preserve existing historical report data without altering business content.
- `test_receipt_schema_enforces_scoped_operation_identity`: verifies `(project, actor, operation_id)` uniqueness constraints in PostgreSQL.
- `test_receipt_survives_old_application_reads_and_enforces_identity`: verifies receipt survival across application read paths.

`python manage.py makemigrations --check --dry-run`

Result: `No changes detected` (System check warning for redis cache only).

## IndexedDB Migration Evidence

- Schema upgrade resilience: `offlineMigration.test.ts` (5 passed) verifies schema upgrade from legacy stores without data loss, safe quarantine of legacy records without verified actor ownership, and clean rollback on storage errors.
- Profile persistence: `unit-offline-recovery.spec.ts` (1 passed) and `unit-offline-interruption.spec.ts` (1 passed) verify that persistent browser profiles retain local snapshots and tombstones through restarts and reloads.
- Compatibility tools: `exportOfflineBackup` and `restoreOfflineBackup` verified via `unit-offline-legacy-upgrade.spec.ts`.
