# T006 canonical API RED evidence

Date: 2026-10-27. Test: `apps/api/core/sub_reports/tests/test_offline_sync_foundation.py` after setting the two other-project fixtures to active. The API environment came from the repository `.env`; its contents were not printed. PostgreSQL test DB `test_037_t006_1793115004_1265755` was unique to this run and managed by pytest. No product code or `tasks.md` was changed for this test.

From `apps/api/core`, the actual run was equivalent to:

```bash
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
export AUDIT_LOG_ASYNC=false CELERY_TASK_ALWAYS_EAGER=true
export TEST_DATABASE_NAME=test_037_t006_1793115004_1265755
../.venv/bin/python -m pytest sub_reports/tests/test_offline_sync_foundation.py -q --tb=short
```

Result: exit 1; **8 failed, 2 warnings in 90.53s**. All eight failures were behavioral `assert 404 == 200` for a request that should be authorized to `POST /api/v1/projects/{project_id}/daily-reports/sync-operations/v2/`. Collection, fixture setup and database initialization did not fail. The missing endpoint is a meaningful first RED, not proof that deeper assertions work or that permission rules are violated. A copy of the full command output was retained locally at `/tmp/feature037-t006-red.log` during this session; it is not a durable repository artifact.

The test file specifies the following further acceptance assertions, but they were **not reached** because the authorized request failed first:

- Identical operation replay returns the exact original success/target receipt; changing the payload under the same ID gives `operation_id_reused`, with no second report or changed header.
- A previously successful receipt cannot be read following membership revocation; active edit permission, inactive and suspended membership, viewer-only access, nonmember denial and the existing global-admin policy are checked. The permission cases first require an authorized request to succeed so a missing route cannot be misreported as a successful denial.
- The same operation ID is independently scoped to actor and project, including changed payload in each other scope.
- A cross-project report target and foreign activity reference are refused without mutating the foreign report or inserting a local row.

Re-run this **same canonical test file** after implementing the contract and inspect every assertion; only a successful execution then can establish its coverage. The currently observed RED does not prove the individual authorization, receipt, replay, fingerprint, or reference protections; it also does not prove browser behavior or whole-feature acceptance.
