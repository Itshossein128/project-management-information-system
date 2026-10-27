# Traceability (T075)

Checked tasks are not treated as proof. The rows below point at the run that exercised the behavior. Anything not listed as executed is still open.

| Item | Evidence | Status |
|---|---|---|
| G01 / US1 | `e2e/tests/unit-offline-entry.spec.ts` exists; not re-run in phase 11 | Earlier implementation, not re-executed here |
| G02 / SC-01 | `verification/us3.md`, ten-operation browser test | Executed in the US3 pass |
| G03 / G04 | `verification/aggregation.md` | Executed in the US4 pass |
| G05 / SC-04 | `verification/us6-us7.md`, approve-versus-sync threads | Executed in the US6 pass |
| G06 / SC-03 | `verification/us5.md` | Partial: eight row successes plus a report, and browser error display; not the complete nine-row correction scenario |
| G07 / G08 / SC-02 | `verification/us2.md` | Executed in the US2 pass |
| G09 | US3 ack tests and US5 stable codes | Executed in those passes |
| SC-05 | `verification/us6-us7.md` conflict browser test and correction replay | Executed in the US7 pass |
| SC-06 / G11 | `verification/recovery.md` | Profile reopen and single concurrent receipt executed; two-tab and revoked-permission browser cases not executed |
| SC-07 | `unit-offline-status.spec.ts` re-run in this pass (pending cloud, English label, keyboard focus) | Partial: one unit page, not all six units |
| G13 | This file | Live production and incomplete validation are not acceptance |

Phase 12 was intentionally removed by the user. It is not part of the current task scope.

On reinspection, several checked tasks described broader browser and race coverage than the recorded tests demonstrate. Their checkboxes were reopened in `tasks.md`; the existing evidence above remains limited to the cases explicitly described in the linked reports. In particular, the original ten-operation browser case seeded a report and nine rows, then reloaded; it did not establish automatic reconnection without refresh.

The current unit-entry Playwright suite was run with a disposable migrated and seeded database: one test failed waiting for the offline indicator and one passed. The failure snapshot showed a React Router `Failed to fetch` error during route discovery after disconnect; it did not reach the local save assertions. The passing storage-failure case conditionally skips its assertions if the input is absent, so it is not proof of recovery. T018 remains open. Current source also uses `offline-user` as a fallback for some queued writes and omits the actor filter in the draft list when `auth_user_id` is absent; T067 remains open pending behavioral tests and correction.
