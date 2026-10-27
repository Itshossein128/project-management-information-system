# Foundation Verification Report: Phase 2 Safety and Shared Contracts

**Feature**: 037-daily-offline-sync  
**Date**: 2026-10-27  
**Status**: Foundation Gate Passed (T005–T017 Complete; T006 Pending T035 Dispatcher)

## 1. Executive Summary

Phase 2 foundational safety controls, parent/child locking protocol, target revision tracking, idempotent receipt recording, and additive IndexedDB local schema are verified GREEN across both Django backend and browser/Playwright environments. Legacy bypasses are closed and unsafe mutations return explicit error codes without touching database state or provenance.

## 2. Test Execution and Evidence Matrix

### 2.1 Backend Foundation & Regression Suites (55 passed)
- **Command**:
  ```bash
  cd apps/api/core && set -a && source /workspace/.env && set +a && ../.venv/bin/python -m pytest \
    field_reports/tests/test_offline_legacy_protection.py \
    sub_reports/tests/test_offline_sync_migrations.py \
    sub_reports/tests/test_offline_receipt_service.py \
    field_reports/tests/test_sync_batch.py \
    sub_reports/tests/test_unit_report_permissions.py
  ```
- **Results**: `55 passed in 135.48s`
  - `test_offline_legacy_protection.py` (15 passed): Derived sections in daily reports are protected with `derived_readonly`; child POST/PATCH/DELETE and batch attempts to write derived content are rejected without creating shells.
  - `test_offline_receipt_service.py` (6 passed): Idempotent operation replay returns cached receipt on identical fingerprint; reused operation ID with modified payload is rejected with `operation_id_reused`; business mutation failure rolls back receipt.
  - `test_offline_sync_migrations.py` (3 passed): Migration backfill preserves existing sub-report data and receipts across migration application and safe rollback.
  - `test_sync_batch.py` (17 passed): Legacy batch endpoint functions correctly with safety guards preserved.
  - `test_unit_report_permissions.py` (14 passed): Scoped project membership and permissions enforced across unit sub-reports.

### 2.2 Concurrency & Locking Verification (11 passed)
- **Command**:
  ```bash
  cd apps/api/core && ../.venv/bin/python -m pytest \
    field_reports/tests/test_offline_approval_race.py \
    sub_reports/tests/test_offline_mutation_permission.py \
    sub_reports/tests/test_offline_revision_writers.py \
    sub_reports/tests/test_offline_revision_exposure.py \
    sub_reports/tests/test_offline_workflow_permission.py \
    sub_reports/tests/test_offline_lock_order.py
  ```
- **Results**: `11 passed`
  - PostgreSQL two-connection race test proves approved report wins over concurrent stale PATCH/batch without data loss.
  - Monotonic revision increment and tombstone marking verified across all unit sub-report section writers.

### 2.3 Browser Local Storage & Upgrade Verification (8 passed)
- **Command**:
  ```bash
  OFFLINE_TEST_ORIGIN=http://127.0.0.1:5198 node --test \
    apps/web/src/app/lib/__tests__/offlineMigration.test.ts \
    apps/web/src/app/lib/__tests__/offlineWrite.test.ts
  ```
- **Results**: `8 passed (5 migration, 3 write)`
  - Legacy records in `offline_queue` retain complete raw payload and status.
  - Legacy records lacking proven actor or canonical unit are quarantined from automatic replay (`getPendingQueue()` excludes them).
  - Aborted IndexedDB schema upgrade cleanly rolls back without poisoning subsequent `initDB()` retries.
  - Storage write abort in IndexedDB leaves previously stored records intact without partial commits.
  - `queueUnitReportOperation` atomically commits `LocalReportSnapshot` and `OfflineOperation` with independent UUIDs and predecessor dependency graph.

## 3. Pending Endpoint Status (T006)

- **Test**: `apps/api/core/sub_reports/tests/test_offline_sync_foundation.py`
- **Current State**: Route `/api/v1/projects/{project_pk}/daily-reports/sync-operations/v2/` is registered in `sub_reports.urls` and routed through `SyncOperationsV2View` with `V2_OFFLINE_SYNC_ENABLED` feature gate (disabled by default, returning 404 outside isolated tests).
- **Scheduled Gate**: Per task plan, T006 will transition from RED to GREEN in **Phase 5 (T035)** when the v2 multi-operation HTTP dispatcher is fully implemented.

## 4. Justified Legacy Behavior Changes

- Formerly accepted POST/PATCH operations containing derived sections (`activities`, `labor`, `materials`, `equipment`) against auto-summary daily reports are now rejected with `400 Bad Request` (`code: derived_readonly`), ensuring aggregation integrity cannot be silently corrupted by offline writes.
