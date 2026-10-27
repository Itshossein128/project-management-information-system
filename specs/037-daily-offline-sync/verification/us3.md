# US3 evidence so far (T031–T033, T035, T037)

T006 was RED before dispatch existed:

`pytest sub_reports/tests/test_offline_sync_foundation.py::test_identical_replay_returns_same_receipt_and_changed_payload_is_rejected`

Observed: HTTP 404, `v2 sync operations endpoint is disabled`.

After dispatch, with `V2_OFFLINE_SYNC_ENABLED` set only by the test modules:

`pytest sub_reports/tests/test_offline_sync_foundation.py sub_reports/tests/test_sync_operations_api.py sub_reports/tests/test_sync_operation_idempotency.py --reuse-db`

Result: 12 passed.

Client acknowledgements:

`node --experimental-strip-types --test apps/web/src/app/lib/__tests__/syncOperations.test.ts`

Result: 3 passed.

Section writers and the browser check:

`pytest sub_reports/tests/test_sync_section_writers.py --reuse-db` passed. One batch creates activity, labor, material, machinery, concrete, general, issue, visit, incident, and note rows. An empty list payload returns `snapshot_replacement_forbidden` and leaves the existing activity in place.

`pnpm exec playwright test --config=e2e/playwright.config.ts e2e/tests/unit-offline-ten-operations.spec.ts` passed. Ten seeded operations (one report plus three activity, labor, and material rows) synced after reload, and the server rows matched those values once each. The Playwright API process sets `V2_OFFLINE_SYNC_ENABLED=true`. The default setting stays off.

The client posts `/v1/projects/{id}/daily-reports/sync-operations/v2/` through the API prefix, so the request is not doubled. Automatic sync reads the signed-in user id from `auth_user` when `auth_user_id` is absent.

## Reconnect verification, 2026-10-27

`unit-offline-ten-operations.spec.ts` was strengthened to disconnect before seeding ten row operations and their report prerequisite, then reconnect without reloading. With a newly migrated and seeded disposable PostgreSQL database, a dedicated API process with v2 enabled, and the existing Vite server, Playwright reported **1 passed**. The test checked all 11 operations reached `synced` and verified the ten row values on the server.

In the subsequent pass the same test additionally compared each of the ten operation IDs, client IDs and returned server IDs to the rows on the server; it passed in an isolated database and Redis instance. This is still not full T034/SC-01 evidence: the test seeds IndexedDB instead of entering rows through the form and does not assert preservation of an unrelated row. T034 and T038 remain open.
