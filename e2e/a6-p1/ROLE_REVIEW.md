# A.6.04 — Browser role review

Run from the repository root:

```bash
set -a
source .env
set +a
A6_E2E_SEED=e2e/a6-p1/seed-role-review.py \
A6_E2E_PLAYWRIGHT_CONFIG=e2e/playwright.a6-role-review.config.ts \
apps/api/.venv/bin/python e2e/a6-p1/run.py
```

The existing runner creates a uniquely named database and temporary API/web
servers, leaving the running development application unchanged. It seeds one
synthetic active member for each of the 13 default project roles. Account data
and tokens stay in a restricted temporary file and are removed on exit.

The browser signs in through the real login form. No API responses are mocked.
It closes first-visit tours through their visible close control. Authentication
rate limiting remains enabled; a 429 requires a real wait before retry.

Coverage:

- All 13 project roles visit activities, costs, documents, contracts, procurement,
  HR resource allocations, daily reports, project members, and a project they
  have not joined. The expected role matrix is explicit in the test, independent
  of the server implementation. Protected read responses are checked directly
  alongside browser controls.
- Activity edit/delete controls and read-only drawers; budget and actual-cost
  creation controls; upload drawers; contract/requisition creation links; HR
  allocation creation; draft daily-report edit controls; member management.
- An edit-only actor actually saves an activity through the browser; direct
  delete and measurement-approval requests must remain denied.
- A manager in A with only a viewer role in B, and an inactive member, cannot
  gain member-management access.
- Organization admin, HR, superuser, staff-only, and visitor accounts are checked
  for organization account administration separately from project writes.
- The existing Persian and English manager journey creates a multi-role member,
  changes grant/deny/inherit, revokes membership, and reads access history.

Results and synthetic screenshots are in `test-results/a6-role-review/` (ignored
by Git). The JSON report includes per-role observations. Do not publish traces
containing temporary authentication data as shared acceptance evidence.

For a focused rerun, set `A6_E2E_GREP` to a Playwright title pattern such as
`'edit-only activity'` or `'admin: organization'`. Playwright matches the full
test title including its file, so a leading `^admin:` does not select that test.

The final 2026-11-11 run passed all 23 scenarios in one run. It verifies menu
destinations for every project role and project switches plus deny/inherit
overrides. The admin path passed after runtime routes and React entry points
were included in initial dependency discovery. Hydration errors are now failures
and none were recorded. A.6.04 is complete for this browser walkthrough. See
`docs/delivery/A6-04-browser-role-review-2026-11-11.md`.

For a faster rerun, `A6_E2E_REUSE_DB` may name a retained database created by
this runner. It must start with `velora_a6_p1_e2e_`, already exist, and have no
connected sessions. The runner creates fresh synthetic actors and projects and
never resets that database. The default still creates a new isolated database.

Limits: this is the A.6.04 role walkthrough, not every action in every module.
It does not exercise a live object store, deliver invitation/recovery messages,
accept a customer release, or prove asynchronous worker behavior. Legacy screens
may show a controlled query error on a denied direct URL instead of a dedicated
access-denied panel; the test requires refusal and absence of protected data.
Runtime assertions include hydration mismatches. This is not an audit of every
console warning, production infrastructure, or unrelated feature.
