# Quickstart: A.7-P2 import safety

Run these checks on the pytest database. Do not point them at the development database or at a project someone is using.

Working directory: `apps/api/core`.

The interpreter is `apps/api/.venv/bin/python`. From `apps/api/core` that path is `../.venv/bin/python`.

PostgreSQL must be reachable through `DATABASE_URL` in the repository `.env`. Redis must be running because the cache backend is Redis. Pytest creates and destroys its own database.

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  schedule/tests/test_a7_p2_import_safety.py \
  schedule/tests/test_mpp_import.py \
  schedule/tests/test_p6_import.py \
  -q
```

`test_a7_p2_import_safety.py` is the new file from this plan. The other two files are the regression net and must stay green.

The new tests use project code `A7P2-IMPORT-SAFETY` only inside that test database. They must include a project that already has an activity, progress, cost, a document, and a locked approved baseline. A pass that only imports into an empty project does not satisfy the feature.

Cover, at least:

- append of overlapping codes creates no duplicate activity or relationship and no new current baseline
- reading a finished job id returns the original outcome and does not apply the file again
- a second confirm of a similar file is a new attempt
- replacement of the protected project is refused before any count changes, for `.xml`, `.mpp`, and `.xer`
- replacement of a project with no activities, progress, cost, documents, or approved baseline soft-deletes and reports removed and added counts
- two overlapping replacements do not hard-delete the same rows and do not touch another project
- removing membership or archiving the project after the job exists leaves domain rows unchanged
- a missing actor writes no domain rows and does not use another account
- a forced failure before write and during write leaves the prior counts, and a later valid attempt can finish
- preview and cancel create no domain rows

Calling the import task inside pytest proves the apply function. It does not prove a separately running worker. Say that limit in the verification report.

After the wizard change, open the import confirmation as a member of a protected project in Persian and in English. Confirm replacement and read the refusal before any schedule data changes. Use the same isolated project if the browser is pointed at a disposable database. Do not run that replacement against the shared development database.

The result and error codes consumed by the next stage are in [contracts/import-safety.md](contracts/import-safety.md).
