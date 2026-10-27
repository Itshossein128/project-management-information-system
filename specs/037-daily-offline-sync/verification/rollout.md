# Rollout notes (T076)

No deployment was performed.

`V2_OFFLINE_SYNC_ENABLED` defaults to false. The versioned route returns 404 until that setting is turned on. Playwright's API process sets it for browser tests only.

Server rollback must keep `OfflineOperationReceipt`. Deleting receipts would let the same operation id create a second business row. The migration test covers receipt retention. `makemigrations --check --dry-run` reported no pending model changes.

Local rollback is `exportOfflineBackup()` followed later by `restoreOfflineBackup()`. Do not delete `ipcas-offline` and do not open an older IndexedDB version over a newer one.

Not verified live: a production database, MinIO attachment bytes, two simultaneous browser tabs, and a revoked membership during an open request.
