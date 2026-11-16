# NEG-08 / NEG-11 verification — 2026-11-15

Local current working tree at base HEAD `d459cc0c25601e347421d1f2edab196d35f5936f`. Existing staged and unstaged work was preserved. Technical scenario acceptance is separate from employer sign-off and overall OPS-04 acceptance.

## Real browser and worker

```bash
umask 077
python3 ops/a7-p5/browser-recovery-fixture.py seed > /tmp/a7-neg0811-auth.json
VITE_API_BASE_URL=http://127.0.0.1:18000/api pnpm --filter web dev --host 127.0.0.1 --port 15173
# In another shell:
A7P6_BROWSER_FIXTURES=/tmp/a7-neg0811-auth.json A7P6_API_ORIGIN=http://127.0.0.1:18000 pnpm exec playwright test --config e2e/playwright.a7-p6.config.ts --grep 'real worker import|planner cannot read'
```

Final result: **3 passed (51.5s)**. The test account is an ordinary project-A planner, with no administrator group or membership in B. Fixture B contains real activity, baseline, baseline-activity and completed-job records plus unique private markers.

NEG-08 runs for both MSP XML and P6 XER. A real browser previews and confirms upload. The existing isolated `before_prepare` fault barrier holds a real separately running worker after claim; the helper refuses to arm while other jobs or fault tests are active. No synthetic RUNNING row, manual session injection or response mocking is used. The test verifies persisted session task_id, the worker's RUNNING record, actual browser offline interruption, reconnect via the retry control, document reload and the browser's own 200/RUNNING polling of the same task. It then releases the barrier and observes the same job DONE and the completed-result UI. Job ID sets and browser start-request count prove exactly one new job and one start request per format. Barrier release is in finally and has the existing bounded runtime timeout.

NEG-11 uses valid authenticated positive controls on A and denied reads on B for WBS, activities, baselines, Gantt and schedule status. B's job status is denied both on B and when its ID is borrowed on A. Borrowed B activity and baseline IDs cannot reveal B's data through A. A forged baseline-row PATCH returns 404 and a direct database snapshot confirms B's domain and baseline rows remain unchanged. Actual `/projects/:id/schedule/gantt` and `/projects/:id/schedule/status` browser navigation checks both own-project data loads and foreign-project denial; private fixture markers never appear.

The locally relevant runtime modules matched the running isolated API by SHA-256: import_operations, import views, baseline views, Gantt views/service, schedule-status views and project permissions. Current local web code was used. This targeted run does not re-establish the full OPS-04 resource/retention matrix for the entire changed tree.

Private JWT fixture files are temporary and removed after verification. No shared or production service configuration was changed.

## Backend

From `apps/api/core`, root .env sourced, `TEST_DATABASE_NAME=test_a7_neg0811`:

```bash
../.venv/bin/python -m pytest schedule/tests/test_a7_cross_project_schedule_isolation.py schedule/tests/test_a7_p6_delivery_acceptance.py -k 'not positive' -q
```

The focused test covers real routes with valid foreign activity/baseline/job IDs, baseline PATCH and DELETE, both MSP/P6 job status scopes, and before/after database content. The integrated negative journey covers the remaining existing acceptance boundaries. Final result: **2 passed, 1 deselected (89.66s)**.
