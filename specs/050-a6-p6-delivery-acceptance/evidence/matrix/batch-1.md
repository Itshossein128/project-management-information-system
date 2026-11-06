# Batch 1 — M01–M10 and M14

version_id: `a46161d3530edfb78c8ebf94b4786d991bea0ba7`

Inventory copied from `specs/048-a6-p4-module-access/matrix/package-1.md`. Each row is one representative operation. `result` is `pass`, `fail`, `not_run`, or `not_applicable`.

| module_id | operation | actor_kind | project_slot | surface | input_ref | expected | actual | result | na_reason | evidence_ref | defect_id | version_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M01 | account and membership lifecycle | admin, member | A | direct | synthetic membership | duplicate membership refused | suite passed | pass | | `projects/tests/test_team_lifecycle.py` in the 122-pass run | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M02 | members, roles, lookup | manager, observer | A/B | direct | synthetic member | manage_members and contact redaction | suite passed | pass | | `test_person_directory_acl.py`, `test_ui_server_parity_fixtures.py`, `test_revocation_retry.py` | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M03 | project isolation | member of A | A/B | direct | foreign project id | deny project B | suite passed | pass | | `projects/tests/test_module_access_project_scope.py` | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M04 | reporting configuration | member of A | A/B | direct | reporting-configurations | 200 on A, deny on B | 20 gap tests passed | pass | | `permissions/tests/test_a6_p6_module_gaps.py` M04 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M05 | organization units | project manager | org | direct | organization-units | read allowed, write denied | GET 200, POST 403 | pass | | `test_a6_p6_module_gaps.py` org-reference test | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M06 | dynamic tables | member of A | A/B | direct | tables | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M06 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M07 | WBS list | member of A | A/B | direct | wbs | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M07 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M08 | activity list | member of A | A/B | direct | activities | 200 on A, deny on B | gap test and `test_activity_action_split.py` passed | pass | | `test_a6_p6_module_gaps.py` M08 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M09 | daily reports | member of A | A/B | direct | daily-reports | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M09 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M10 | concrete batches | member of A | A/B | direct | concrete-batches | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M10 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M14 | POST unit-report open | editor versus viewer | A | direct | units/{unit}/daily-reports/open/ | editor opens; viewer is refused | those two tests passed; superuser break-glass approve is D005 and is not this row | pass | | `test_view_reports_cannot_mutate` and `test_edit_reports_can_open_edit_submit_delete` in `sub_reports/tests/test_unit_report_permissions.py` | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
