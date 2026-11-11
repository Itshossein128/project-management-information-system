# Quickstart: A.7-P1 verification

Tests use the Django test database created by pytest. Do not point them at the development database.

Working directory for every command below: `apps/api/core`.

The installed interpreter is `apps/api/.venv/bin/python`. From `apps/api/core` that path is `../.venv/bin/python`. `../../.venv` is `apps/.venv` and is not the project environment.

PostgreSQL must be reachable through `DATABASE_URL` in the repository `.env`. Redis must be running because the cache backend is Redis. Pytest creates and destroys its own database.

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  master_data/tests/test_org_refs.py \
  master_data/tests/test_units.py \
  projects/tests/test_a7_p1_reference_project.py \
  projects/tests/test_project_registration_lifecycle.py \
  projects/tests/test_project_registration_charter.py \
  projects/tests/test_project_registration_change_request.py \
  projects/tests/test_project_status_undo.py \
  projects/tests/test_projects.py \
  wbs/tests/test_wbs_structure_fields.py \
  wbs/tests/test_wbs_cycle_move.py \
  wbs/tests/test_services.py \
  project_templates/tests/test_wbs_template_immutability.py \
  ../../../specs/051-a7-p1-project-reference/evidence/test_control_figures.py \
  -q
```

The reference scenario creates project code `A7P1-REF` only inside that test database.

The schedule contract test reads the unchanged employer file and, for the four historical predecessor UIDs, a read-only MSPDI conversion. It does not call the importer. Java and the installed `mpxj` package are required for that one check.

After the measurement-unit form changes, open `/settings/org-refs` as an organization steward in Persian and in English. Confirm the measurement-unit heading, symbol label, and list. Do not create a catalog row in the shared development database just to produce proof; the isolated pytest database covers create, refusal, selection, and reopen.
