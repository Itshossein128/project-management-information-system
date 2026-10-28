# Quickstart Verification Guide: Physical Progress Measurement

## Environment & Prerequisites

PostgreSQL 16 and Redis must be running:
```bash
sudo pg_ctlcluster 16 main start
sudo redis-server /etc/redis/redis.conf --daemonize yes
```

Ensure Python virtual environment is loaded:
```bash
source apps/api/.venv/bin/activate
```

Use a unique test database for each concurrent checkout/session. Do not reuse
the shared `test_ipcas` database when another pytest process may be running:

```bash
export TEST_DATABASE_NAME=test_ipcas_feature040_20261028
```

---

## 1. Automated Backend Test Suites

Run Django pytest suites for progress measurement and validation:
```bash
cd apps/api/core
set -a && [ -f ../../../.env ] && source ../../../.env && set +a
../.venv/bin/python -m pytest --reuse-db schedule/tests/test_measurement_methods.py schedule/tests/test_progress_validation.py schedule/tests/test_progress_four_way.py contracts/tests/test_ipc_service.py
```

Expected Outcome: All tests pass with 0 failures.

If test database setup reports `DuplicateTable`, `DuplicateColumn`, or
`pg_type_typname_nsp_index`, stop competing pytest processes and recreate only
the isolated database named by `TEST_DATABASE_NAME`, then rerun one process.

---

## 2. API End-to-End Scenarios

### Scenario A: Enforcing Approved Measurement Method
1. Create a WBS Activity with 0 or unapproved measurement definition.
2. Submit `POST /api/v1/projects/:projectId/progress/manual/` with `actual_progress = 20`.
   - **Expected**: HTTP 400 with code `measurement_not_approved`.
3. Submit `POST /api/v1/projects/:projectId/activities/:activityId/measurement/approve/` with quantity and unit.
   - **Expected**: HTTP 200 with approved status.
4. Resubmit manual progress.
   - **Expected**: HTTP 201 Created.

### Scenario B: 100% Ceiling Enforcement (No Clamping)
1. Activity has cumulative progress of 95%.
2. Submit manual progress or daily report row claiming 10% (cumulative 105%).
   - **Expected**: HTTP 400 with code `progress_exceeds_100`.
   - **Verification**: Query progress rows; previous progress remains 95% (not clamped to 100%).

### Scenario C: Strict IPC Auto-Population
1. Activity has 50% claimed actual progress, but only 40% approved progress.
2. Call `auto_populate_ipc(ipc_id)` for the period.
   - **Expected**: The generated `IPCItem` has `qty_current` corresponding to the 40% approved delta.
   - The unapproved 10% claimed progress is completely excluded.

### Scenario D: Technical Approval in UI
1. User with `approve_reports` opens Activity Progress Table.
2. Clicks "تأیید فنی پیشرفت".
3. Submits verified percentage and test sheet reference.
   - **Expected**: HTTP 200; `approved_progress_pct` updates immediately.
4. Submitting with basis `"photo"`:
   - **Expected**: HTTP 400 with code `photo_not_technical_approval`.

---

## 3. Frontend Build Verification

```bash
pnpm --filter web build
```

Expected Outcome: Clean build without errors.
