# Verification: A.7-P2 import safety

**Date**: 2026-11-11

## Pytest

Command from `apps/api/core`, with `DATABASE_URL` loaded from the repository `.env`:

`../.venv/bin/python -m pytest schedule/tests/test_a7_p2_import_safety.py schedule/tests/test_mpp_import.py schedule/tests/test_p6_import.py schedule/tests/test_msp_import.py -q`

Result: **29 passed**.

The new file uses project codes that start with `A7P2-IMPORT-SAFETY` only inside the pytest database. It covers protected replacement for progress, cost, documents, activities, and a locked approved baseline; `.xml`, `.mpp`, and `.xer`; unprotected soft-delete; repeat append; in-flight replay; archive; permission loss after queue; cross-project hiding; preview and mid-write rollback; and attribution.

Calling `run_msp_import_task.apply` inside pytest runs the same function a worker would call. It does **not** prove a separately running worker process.

Django stayed on 4.2. No migration was added.

## Browser

Signed-in session on `http://localhost:5173`. Disposable project `A7P2-IMPORT-SAFETY` (`23b06975-5367-471a-805d-54b8cff189a7`) with a locked baseline dated 2026-01-03. The existing UAT project was not imported into.

On `/projects/23b06975-5367-471a-805d-54b8cff189a7/wbs`, the import wizard accepted `a7p2-plan.xml`, showed the preview, and replace was confirmed.

- Persian: the confirmation step showed «نمی‌توان برنامه‌ای را جایگزین کرد که خط مبنای قفل‌شده یا مصوب دارد.» The wizard stayed on that step.
- English: the same confirmation showed “Cannot replace a schedule that has a locked or approved baseline.” both in the dialog and in the alert.

After both attempts, the project still had 0 work-breakdown nodes and 0 activities.
