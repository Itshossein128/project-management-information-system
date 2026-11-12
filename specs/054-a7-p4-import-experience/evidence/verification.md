# Verification: A.7-P4 import experience

**Date**: 2026-11-12

## Pytest

From `apps/api/core`, with `DATABASE_URL` loaded from the repository `.env`:

```bash
../.venv/bin/python -m pytest schedule/tests/test_a7_p4_import_experience.py schedule/tests/test_a7_p3_import_fidelity.py schedule/tests/test_a7_p2_import_safety.py schedule/tests/test_msp_import.py schedule/tests/test_p6_import.py schedule/tests/test_mpp_import.py -q
```

Result: **54 passed**, 2 warnings, in 76.26s.

The new file uses project codes that start with `A7P4-IMPORT-EXPERIENCE` only inside the pytest database. It covers recognized kind for XML, XER, and MPP, preview that writes nothing, replacement figures, a protected replace, P6 `invalid_file_type` and `file_too_large`, the shared Persian and English code catalog, and in-flight replay. Django is **4.2.11**. No migration was added.

Calling the import task inside pytest, and the local API that runs that task inside the request, does **not** prove a separately running worker.

`real-data/plan.mpp` was not modified. Its SHA-256 remains `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`.

## Browser

See [browser.md](browser.md). Headless Chromium exercised the disposable project `A7P4-IMPORT-EXPERIENCE` (`91884a98-0f32-4e73-b2ef-b6f075f18ce6`) in Persian and English, at desktop and phone widths, including keyboard activation of Preview and Import and an interrupted status request. A second file dropped during an in-flight preview was not separately timed. The API test covers the in-flight replay.

## Final-tree recheck in this implementation session

The same pytest command was repeated after the changes: **54 passed, no skips**, 2 dependency deprecation warnings, in **93.50s**. `pnpm typecheck` also passed (exit 0). `git diff --check` passed. Django is 4.2.11; no migration was added. The original MPP SHA-256 remains the value above.

The request callbacks now capture their originating account, project, file, mode, and recognized kind. Stale previews are discarded after close/reopen or context changes. The immediate request lock prevents overlapping actions before React renders pending state. Closing during start retains the original task for recovery. Polling clears its timer and uses the current completion callback without restarting when the parent rerenders. A finished or failed attempt has an explicit localized choose-another-file action; unavailable browser storage does not turn a successful start into a failure.

**Feature completion remains blocked at T021.** The real native MPP browser import failed on the existing WBS tree-path collision (`wbs_path_key`, `005M`) in the disposable local database. Passing backend tests do not establish that this populated-database journey succeeds. No WBS tree repair or shared-project mutation was attempted. Extension configuration was checked before and after implementation: `hooks: {}`, so no hooks were dispatched.

## Root-cause correction and final acceptance recheck

The prior T021 blocker is resolved. Integrated WBS and import pytest: **74 passed**, no skips, 2 dependency warnings, 94.29 seconds; full command is in [wbs-path-root-cause.md](wbs-path-root-cause.md). All four language/width browser combinations now pass XML, real native MPP and XER. The first MPP success created 6 packages, 72 activities and 72 relationships; repeated imports created none. Database reads confirmed the stored figures. No reset, tree rebuild, dependency upgrade, or migration was needed. `projects` migration dry-run reported no changes; the repository-wide check separately detects existing storage model drift and no migration was generated. Frontend code is unchanged since the passing typecheck. Extension configuration still has no before/after hooks.
