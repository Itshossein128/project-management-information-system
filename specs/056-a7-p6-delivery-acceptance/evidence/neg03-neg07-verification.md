# NEG-03 / NEG-07 verification — 2026-11-15

Local working tree based on HEAD `d459cc0c25601e347421d1f2edab196d35f5936f`; unrelated staged and unstaged work was preserved. No deployment or employer acceptance is claimed.

## Backend

From `apps/api/core`, with the root .env sourced and `TEST_DATABASE_NAME=test_a7_cycle_cancel`:

```bash
../.venv/bin/python -m pytest schedule/tests/test_a7_cycle_cancel_acceptance.py schedule/tests/test_a7_p6_delivery_acceptance.py -k 'not positive' -q
```

Result: **10 passed, 1 deselected** (81.87s). This includes the current integrated negative journey. New focused cases cover self, mutual and three-node dependency cycles in MSP XML and P6 XER, read-only preview, atomic rejection by both import executors, API failed-job status (Celery eager mode), protected-replace admission refusal, and WBS self/child/grandchild move rejection. Before/after snapshots compare stored content, including baseline activities, rather than counts alone. Both preview families preserve all MSP/P6 job records. This is not a separate-worker execution claim.

## Browser

A disposable project with an existing WBS and activity was created in the isolated `a7p5_import` database. Local current Vite used the isolated API on port 18000. The fixture JWT file was private and temporary.

```bash
A7P6_BROWSER_FIXTURES=<private-fixture-json> A7P6_API_ORIGIN=http://127.0.0.1:18000 A7P6_WEB_BASE=http://127.0.0.1:15173 pnpm exec playwright test --config e2e/playwright.a7-p6.config.ts --grep 'cancel after preview'
```

Result: **4 passed** (26.7s): XML/XER × Escape/back-then-cancel. The test directly compares project/domain records and both job-model ID sets before preview and after cancel and reopening. The snapshot helper `ops/a7-p5/snapshot-project.py` is read-only, requires the isolated database, and includes terminal jobs so a stray completed attempt cannot escape detection. It also records that the browser sent no import-start request. The previous fresh-import probe and screenshot dependency were removed from NEG-07.

No product defect was exposed in these two paths; the missing and misleading acceptance proof was completed. Both scenarios remain technical pass; employer decision remains pending. Independent-worker/cgroup verification belongs to OPS-04 and is unchanged by this focused result.
