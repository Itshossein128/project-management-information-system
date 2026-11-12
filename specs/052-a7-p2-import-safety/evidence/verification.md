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

## Integrated handoff recheck — 2026-11-12

From `apps/api/core`, with the repository `.env` exported:

```bash
../.venv/bin/python -m pytest schedule/tests/test_a7_p2_import_safety.py schedule/tests/test_a7_p3_import_fidelity.py schedule/tests/test_mpp_import.py schedule/tests/test_p6_import.py schedule/tests/test_msp_import.py schedule/tests/test_mpp_equivalence.py -q --reuse-db
```

Final result: **49 passed, no skips, 2 dependency deprecation warnings**, in 94.10 seconds. This includes actual native MPP conversion and stored MPP/XML comparison; the final comparison also covers actual and forecast dates, percent, critical/slack values, calendar assignment, weight, and normalized warning codes and row identities. Converter failures other than the two known missing-runtime/configuration cases now fail the reference checks instead of being skipped.

Django reports **4.2.11**. `manage.py showmigrations projects --plan` shows `projects.0020_activity_import_fidelity_fields` applied. `manage.py makemigrations projects schedule --check --dry-run` exits 0 with no changes. The repository-wide migration check exits 1 because of unrelated `storage.StoredFile.source` drift; no migration was generated or applied for it.

The employer-file SHA-256 remains `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`. The run used the pytest PostgreSQL database and its in-memory cache fixture. It did not import into shared projects, repeat browser checks, verify Redis integration, or exercise a separate worker. The [handoff](../handoff.md) records the verified local baseline and those limits.
