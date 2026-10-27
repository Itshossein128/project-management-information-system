# T007 — migration baseline RED

Date: 2026-10-27. Scope: local disposable PostgreSQL test database; no product migration or product model was changed by this test task.

Run from `apps/api/core`:

```bash
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
export TEST_DATABASE_NAME=test_offline_migration_037_1793115043_1266297
../.venv/bin/python -m pytest sub_reports/tests/test_offline_sync_migrations.py -q --tb=short
```

Result: **3 failed in 110.71s**. Each failure was an explicit behavioral assertion, not a setup, collection or import failure:

1. `test_expand_preserves_historical_data_and_backfills_tokens`: `Feature 037 needs an additive migration after 0011 for receipts and revision backfill`.
2. `test_receipt_schema_enforces_scoped_operation_identity`: `A durable receipt with project, actor and operation_id is required for replay safety`.
3. `test_receipt_survives_old_application_reads_and_enforces_identity`: `A durable receipt is needed before rollback can preserve replay evidence`.

The first test actually constructed pre-feature rows using historical migration models: an approved historical version, current correction with shared lineage/supersedes and summary reference, activity, labor, material and attachment reference. It reached the assertion after taking a baseline snapshot. The test defines the subsequent checks for forward migration/backfill, preserved values and links, reading with the old model, pre-receipt schema rollback and reapplication; none was reached in this RED run. The receipt tests define checking database uniqueness and actual duplicate insertion, plus preservation of identity, fingerprint and outcome after an old-model read. These portions were not reached because no receipt model exists. The same-operation/different-actor assertion was added while this run was already in progress and was not executed; it lies beyond the same failing receipt prerequisite.

The named revision token aliases and receipt field aliases are test conventions, not a settled product schema; any additional non-null receipt fields require an explicit realistic fixture. Reading through a historical Django model against an expanded schema is a compatibility probe, **not** proof of deployment rollback or journal retention during a real application rollback. No receipt existed and no post-migration rollback, restore, uniqueness or data-preservation path was proven by this RED. After implementation, execute this test unchanged where practical, explicitly populate any additional required receipt data, and separately prove supported rollback/restore with real receipts. Do not reverse a schema in a way that destroys retained receipt history.
