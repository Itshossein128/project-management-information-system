# US6 and US7 evidence (T050–T061)

Checklist `requirements.md` was already fully checked.

Lock race, from `apps/api/core` with `--reuse-db`:

`pytest sub_reports/tests/test_unit_report_concurrency.py::TestUnitReportConcurrency::test_approve_and_sync_keep_the_locked_row sub_reports/tests/test_sync_lock_contract.py sub_reports/tests/test_offline_correction_transfer.py`

Result: 4 passed. Approve and sync ran on two threads against PostgreSQL. The activity text stayed `original`, the report ended approved, the sync result was `conflict` / `sync_conflict`, and an approval history event was stored. Approved and non-current targets are refused. A sync operation cannot approve a draft. A user without edit permission receives 403. `correct_transfer` opens one correction draft, replay returns the same destination, and a direct update of the approved report does not patch it.

`pytest sub_reports/tests/test_unit_report_workflow.py --reuse-db` passed (18).

Conflict choice:

`node --experimental-strip-types --test apps/web/src/app/lib/__tests__/offlineConflictResolution.test.ts` passed. Selecting the server side removes only that operation and its row. An unrelated pending operation remains after a JSON reload.

`pnpm exec playwright test --config=e2e/playwright.config.ts e2e/tests/unit-offline-conflict.spec.ts` passed. The conflict screen shows activity, labor, and material rows from both sides, and the server/keep-mine actions stay disabled until the scope checkbox is confirmed.
