# Migration evidence (T073)

From `apps/api/core`, with the project `.env` loaded:

`pytest sub_reports/tests/test_offline_sync_migrations.py --reuse-db`

Included in the combined run with the concurrent replay test: 4 passed in 60.18s. That module checks apply/backfill, historical rows, and receipt retention across the supported rollback path.

`../.venv/bin/python manage.py makemigrations --check --dry-run`

Result: `No changes detected`.

IndexedDB: the interruption browser test reopened the same Chromium profile and still had the local snapshot. The legacy browser test restored an ambiguous payload through `restoreOfflineBackup` without clearing the store. A full version-3 to current upgrade of the production database name is covered by `apps/web/src/app/lib/__tests__/offlineMigration.test.ts` when that file is run against the Vite origin; it was not re-run in this pass.
