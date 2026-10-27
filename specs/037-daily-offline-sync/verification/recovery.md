# US8 recovery evidence (T062–T070)

`node --experimental-strip-types --test apps/web/src/app/lib/__tests__/offlineClaims.test.ts` passed (2). A second tab cannot take a live lease. After expiry the new owner gets a higher fencing token and the old token cannot acknowledge. Syncing operations return to pending. Another actor's operations are not visible.

`pytest sub_reports/tests/test_sync_concurrent_replay.py sub_reports/tests/test_offline_sync_migrations.py --reuse-db` passed (4). Two PostgreSQL connections posting the same operation created one report and one receipt, and both results named that report id.

`pnpm exec playwright test --config=e2e/playwright.config.ts e2e/tests/unit-offline-interruption.spec.ts e2e/tests/unit-offline-legacy-upgrade.spec.ts` passed. Closing the persistent profile and reopening it kept the local note, and the operation was no longer stuck in `syncing`. Export/restore kept the ambiguous legacy payload, and another actor's pending list did not contain it.

Not executed here: two browser tabs sending at the same moment, an expired JWT against the live API, and a revoked membership during an in-flight request. Server idempotency covers the duplicate-effect half of those cases. Signing out does not delete IndexedDB; auto-sync does not send when the access token is missing.
