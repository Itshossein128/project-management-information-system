# US5 evidence (T045–T049)

`node --experimental-strip-types --test apps/web/src/app/lib/__tests__/offlineRowRetry.test.ts` passed. A field error keeps its code across a JSON reload. A correction gets a new operation id, points at the failed operation with `supersedes_operation_id`, and does not change the original payload. Only that new pending operation is selected to send.

`pytest sub_reports/tests/test_sync_operation_validation.py --reuse-db` passed. Eight labor creates plus the report header succeed. The activity with a negative quantity returns `quantity_must_be_positive` on `quantity`, with a localized message and the client id. A later operation that depends on that failure is `blocked_dependency` and creates no row. Resending the activity under a new operation id that supersedes the failed one commits one activity and does not replay the labor rows.

`pnpm exec playwright test --config=e2e/playwright.config.ts e2e/tests/unit-offline-row-retry.spec.ts` passed. The electrical page shows `quantity: quantity_must_be_positive` and does not show a success toast when the server is unreachable.
