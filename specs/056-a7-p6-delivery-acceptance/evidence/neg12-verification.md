# NEG-12 viewer read-only acceptance — 2026-11-15

Base HEAD `d459cc0c25601e347421d1f2edab196d35f5936f`, with existing staged/unstaged work preserved. No deployment or employer sign-off is claimed.

## Backend

From `apps/api/core`, source root .env and set `TEST_DATABASE_NAME=test_a7_viewer`:

```bash
../.venv/bin/python -m pytest schedule/tests/test_a7_viewer_readonly_acceptance.py schedule/tests/test_a7_p6_delivery_acceptance.py -k 'not positive' -q
```

Result: **2 passed, 1 deselected (100.68s)**. The focused test provisions an ordinary active viewer and an unlocked baseline with actual baseline-activity rows. Positive controls verify successful project, charter, WBS, activity, baseline, Gantt and schedule-status reads. Fifteen actual mutation routes are denied with 403: project PATCH/DELETE, charter PUT, baseline create/approve, baseline-activity PATCH/DELETE, WBS create/PATCH/DELETE, activity PATCH and MSP/P6 preview/start. Content snapshots compare project, charter, WBS, activity/relation, baseline and baseline-activity records and both import-job models after every attempt. The current integrated negative journey also passed.

## Browser

```bash
umask 077
python3 ops/a7-p5/seed-viewer-browser.py > /tmp/a7-neg12-auth.json
VITE_API_BASE_URL=http://127.0.0.1:18000/api pnpm --filter web dev --host 127.0.0.1 --port 15173
# In a separate shell:
A7P6_BROWSER_FIXTURES=/tmp/a7-neg12-auth.json A7P6_API_ORIGIN=http://127.0.0.1:18000 pnpm exec playwright test --config e2e/playwright.a7-p6.config.ts --grep 'viewer project and baseline'
```

Final result: **2 passed (12.7s)**, Persian at 1280×800 and English at 390×844. The fixture viewer is not the owner, is not an administrator, and has exactly the default viewer role on the disposable project. The project contains a retained charter, WBS, activity and unlocked baseline with a snapshot row, so hidden write controls are caused by authorization rather than absent data or a locked baseline.

The actual settings page shows disabled project name and purpose fields and no save button. WBS displays its existing row with no import action. The actual Gantt page displays the baseline while snapshot-create and approve-lock controls are absent. Valid read requests return 200.

To test bypassing the UI, each test sends all 15 mutation attempts via browser `fetch` with the viewer's stored login token, including real XML/XER files via FormData. Every request returns 403. A direct read-only database comparison confirms unchanged project, charter, scheduling/baseline records and both job ID sets, including terminal jobs. The snapshot helper now explicitly includes the charter.

The relevant running isolated API modules matched the local source by SHA-256: projects views/serializers, schedule baseline/activity/import views, WBS views and project permissions. Current local web code was used. No product-code defect was found in these tested paths; missing acceptance coverage was completed. The result does not replace full OPS-04 operational acceptance or human employer sign-off.

The temporary private JWT fixture is removed after verification. Existing shared/production services are unchanged.
