# Verification: A.7-P1

**Date**: 2026-11-10  
**Git HEAD**: `b4ec9b9` on `develop`, plus the uncommitted files listed in `handoff.md`  
**Django**: 4.2.11  
**Database**: pytest used its own test database. Migration `projects.0019_project_approval_submitted_by` was also applied to the development database so the running API has the new nullable column. No organization-unit, contract-type, or measurement-unit row was created or deleted in that database.

## Backend

Working directory `apps/api/core`. Interpreter `../.venv/bin/python` (`apps/api/.venv`). Repository `.env` loaded. PostgreSQL and Redis were up.

```text
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

Result: `108 passed, 2 warnings in 73.21s`.

The two warnings are the existing reportlab and pandas notices.

That run includes the reference scenario (create, reopen, charter, catalog selection, three-level work breakdown, duplicate and foreign-parent and cycle refusals), the life-cycle walk with a different approver, trimmed project-code refusal on create, update, and template create, organization-unit self-parent refusal, measurement-unit create and refusal, WBS move and renumber, and the schedule control figures. The predecessor-UID check converted `real-data/plan.mpp` to MSPDI in memory, confirmed UIDs 8055, 8084, 8102, and 8120 are Summary=1, and left the employer file bytes unchanged. It does not call `execute_msp_import`.

An earlier focused run in this same tree, before the full set, reported `60 passed` for the approval, template, activation, and control-figure modules.

## Browser

The Vite app at `http://localhost:5173` and the API at `http://127.0.0.1:8000` were already running. The signed-in account was the existing development user. No catalog row was created.

Persian `/settings/org-refs`: subtitle «واحدهای سازمانی، انواع قرارداد و واحدهای اندازه‌گیری», heading «واحدهای اندازه‌گیری», symbol label «نماد», and the existing unit list. An empty measurement-unit name was blocked before a request (`valueMissing`).

English `/settings/org-refs`: subtitle «Organization units, contract types, and measurement units», heading «Measurement units», symbol label «Symbol». The same empty-name check was blocked. Chrome's validation bubble stayed «Please fill out this field.» in both languages because the browser UI language is English.

Persian and English `/projects/new`: the contract-type control opened the loaded catalog (the unset choice plus the existing contract-type rows). The form was not submitted, so no project was created and reopen was not exercised in the browser. Reopen of identity, owning unit, contract type, charter, and three work-breakdown levels is covered by `projects/tests/test_a7_p1_reference_project.py` on the pytest database.

## Not claimed

- Employer expert acceptance. This phase is ready for review.
- A browser create of a measurement unit. That would write the shared development catalog.
- Importer changes. The historical 80/83/79 figures are not pass/fail targets.
- Pending projects that were submitted before `approval_submitted_by` existed have a null submitter, so the new same-actor check applies to submissions stored after the migration.
- Celery, RabbitMQ, and MinIO. The new behavior is synchronous request handling.
