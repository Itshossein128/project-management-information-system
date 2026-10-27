# Quickstart: validation and evidence

These commands are validation entry points, not claims of execution. Run against the final implementation tree. Existing suites below are a baseline and do not by themselves prove this feature. Add canonical tests through the implementation workflow; run their exact paths after they exist. Never replace a failing acceptance assertion with a skip/stub. If a historical test expects a destructive behavior now prohibited by spec, rewrite it with explicit rationale and equivalent or stronger assertions.

## Prerequisites and isolation

Use repo root `/home/hossein/Desktop/projects/building-management`. Preserve existing work and use a **fresh unique test database name**, with one pytest process per test DB. PostgreSQL and Redis must be available and project root `.env` must be sourced; do not print secrets. Optional MinIO/RabbitMQ evidence is separate. Do not run destructive tests on real project data. API venv must retain Django 4.2.11; do not install incompatible dev requirements wholesale.

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
export TEST_DATABASE_NAME="test_offline037_$(date +%s)_$$"
export AUDIT_LOG_ASYNC=false
export CELERY_TASK_ALWAYS_EAGER=true
../.venv/bin/python -m pytest field_reports/tests/test_sync_batch.py sub_reports/tests/test_unit_report_concurrency.py sub_reports/tests/test_unit_report_permissions.py -q
```

Record these baseline suite outcomes separately from new contract tests; the old suite contains expectations that may need reasoned replacement. For migration checks use a disposable DB/backup, not an occupied shared test DB:

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
../.venv/bin/python manage.py makemigrations --check --dry-run
```

In an isolated database apply migrations, exercise real legacy fixtures, validate values/relations/receipt uniqueness and rollback/restore; dry-run alone does not prove data preservation. For browser DB upgrade use a persistent profile seeded with the actual previous schema, including ambiguous/missing actor and interrupted upgrade; verify recovery and compatible rollback or export without clearing storage.

## Required test runs and expected evidence

- Canonical RED→GREEN for G01–G13: unit transformation (trailing slash POST, per-ID out-of-order/missing/duplicate/unknown ack), dependency ordering, idempotency and payload mismatch, atomic invalid header and row, missing snapshot and targeted delete, errors and retry. Tests should assert exact persisted IDs, payloads and state, not only counts. Existing `apps/web/src/app/lib/__tests__/offlineDB.test.ts` is limited weather normalization; run canonical TypeScript tests with the installed Node 25 type stripping, for example `node --experimental-strip-types --test apps/web/src/app/lib/__tests__/offlineDB.test.ts`; add each new test path explicitly. This runner requires tests/imports compatible with native type stripping; browser IndexedDB tests still need an actual browser.
- API integration: verify successful/validation/conflict/retryable cases, authorized/unauthorized project and cross-account access, safe legacy consumers, all derived create/PATCH/DELETE/batch paths, including empty arrays. Verify metadata allowlist, current statuses and untouched provenance/attachment references. Explicitly test transaction rollback and no receipt for a failed mutation.
- PostgreSQL race: extend existing `sub_reports/tests/test_unit_report_concurrency.py` or a dedicated canonical suite using two truly independent connections, barriers and transactional test setup. Exercise approve versus sync, current-version switch versus mutation/ensure, two concurrent first drafts, same operation simultaneous replay and independent rows. Assert database state, history, receipt and IDs; simulated interleaving alone does not satisfy SC-04.
- Browser: use existing app-specific config, not root config (root `testDir` is different). From project root:

```bash
cd /home/hossein/Desktop/projects/building-management
pnpm exec playwright test --config apps/web/e2e/playwright.config.ts apps/web/e2e/tests/offline-sync.spec.ts apps/web/e2e/tests/unit-report-source-truth.spec.ts
pnpm typecheck
```

Existing cases are baseline only. Add and run new canonical browser scenarios that authenticate online, cache effective config/references, enter offline via same unit pages, save ten changes, refresh and close/reopen same persistent profile offline, reconnect automatically, and compare exact operations, values and IDs on server. Separately exercise one invalid row among nine, correction/retry without resending successes, full conflict comparisons, server choice and authorized correction, syncing crash before/after server commit, two tabs and account switching. Run both locales with keyboard and accessible names, including pending yellow cloud. Use real network control/server, not banner-only assertions. Verify worker/service availability and seeded authorized project; capture trace and commands and identify missing service limitations.
- Run full relevant final-tree backend, frontend/typecheck, integration and migration suites once changes are complete; report exact commands, counts and failures. Exercise production-like deployment separately only if authorized and safe; no live evidence should be inferred from local tests. Record browser, backend, migration, typecheck and live environment separately; MinIO/file upload is outside feature but preservation of existing attachment references must be checked.

## Local backup and server rollback

Export the current IndexedDB stores with `exportOfflineBackup()` and restore them with `restoreOfflineBackup()`. Do not delete the database or assume a version downgrade opens the newer schema. A server rollback must leave `OfflineOperationReceipt` rows in place so a repeated operation id returns the original result instead of applying the change twice.

## Acceptance checklist for evidence

SC-01 ten exact successes, zero missing/false ack/duplicates/unrelated deletes; SC-02 100% local data and statuses after refresh/restart; SC-03 nine success plus corrected tenth without replay; SC-04 no unauthorized locked data or history mutation under real races; SC-05 server choice does not resend and correction retains work until ack; SC-06 crash before/after commit recovers without duplicate; SC-07 both locales from current unit pages. Cite logs and test names per criterion and state any unexecuted case explicitly.
