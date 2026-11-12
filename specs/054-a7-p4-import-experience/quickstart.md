# Quickstart: Schedule Import Experience

Validate the import screen against stored rows. A mocked status response is not the result. Use the pytest database and project code `A7P4-IMPORT-EXPERIENCE` for automated tests. Browser checks use a disposable project with that same code. Do not import into a shared or UAT project. Do not modify `real-data/plan.mpp`.

## Prerequisites

PostgreSQL and Redis are running. The API virtualenv is `apps/api/.venv`. Django stays on 4.2.11. From the repository root, export `DATABASE_URL` from `.env` before pytest.

Phase 2 and phase 3 behavior is the baseline under test. Do not start the code change until each of those features has a handoff. This guide does not create those handoffs.

The hand-counted fixtures under `specs/051-a7-p1-project-reference/evidence/fixtures/` stay read-only. Historical audit counts, including 83 source links and 79 stored relationships, are not the expected totals.

## Commands

From `apps/api/core`, after the code change:

```bash
../.venv/bin/python -m pytest schedule/tests/test_a7_p4_import_experience.py schedule/tests/test_a7_p3_import_fidelity.py schedule/tests/test_a7_p2_import_safety.py schedule/tests/test_msp_import.py schedule/tests/test_p6_import.py schedule/tests/test_mpp_import.py -q
```

No migration is expected. If a migration appears, stop and treat it as outside this feature.

## Outcomes to confirm

- Preview `relationships_kept` equals the finished `relations_created` for the same file and mode. `created_links` is not the number compared with the database.
- `rows_read`, created packages, created activities, duplicates, and omitted rows on the preview match the finished result and the stored rows.
- Add on a project that already has the same codes reports duplicates, stores nothing new, and does not say the plan changed.
- Replace on a project with progress, cost, a document, activities, or a locked baseline returns the existing protection code, writes nothing, and shows removed counts as zero.
- Replace on a project with none of those protections reports the live rows that were removed and the rows the file stored.
- A second start for the same person, project, mode, and file bytes while the first job is pending or running returns the first task id.
- P6 rejection of an oversized or wrong-kind file uses `file_too_large` or `invalid_file_type`.
- The phase 2 and phase 3 tests in the command above still pass.

## Browser

Sign in on the local web app. Open only the disposable `A7P4-IMPORT-EXPERIENCE` project. Run the web and API servers the workspace already uses. Exercise the wizard on the work-breakdown screen.

Cover these journeys in Persian and in English, on a desktop width and a phone width:

1. A readable `.xml`, `.mpp`, and `.xer` file, from choice through preview, add or replace, progress, and the result. The file name and kind stay visible. The figures match the stored project. The result opens the work breakdown and the activities.
2. A file that warns, including a calendar that is not applied or a summary predecessor. Every warning text and row is readable, and the warning is visually distinct from a blocking failure.
3. A corrupt, password-protected, oversized, or wrong-kind file. The message names the case and a next step. The project is unchanged.
4. Replace on a project whose history is protected. The refusal names the reason. The project is unchanged.
5. Interrupt the status request after confirm. The screen does not call the attempt failed. Retry shows the real outcome and does not store the file twice.
6. While preview or confirm is in progress, click again, choose a second file, and drop a second file. Only one attempt runs, and the file does not change.

Repeat the success and one recoverable rejection with the keyboard only. Focus moves to the active step. File names, codes, and a long warning stay readable in both directions.

Record what was run, the project id, and the limits in `specs/054-a7-p4-import-experience/evidence/` when verification happens. A short illustrated guide for those six journeys is part of that evidence, not a new in-product tour. This planning command does not capture those images.
