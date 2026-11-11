# Traceability: A.7-P1

Code version at the start of this phase: `b4ec9b9`. The changes below are uncommitted on `develop`. Django remains 4.2.11.

| Id | Source requirement | Expected behavior | Result | Task | Evidence |
| --- | --- | --- | --- | --- | --- |
| P01 | FR-PRJ-001 | Save and reopen a complete project | Preserved. The reference scenario stores identity, purpose, scope, deliverables, employer, dates, contract number, amount, currency, manager, owning unit, and contract type, then reads them back | T003 | `projects/tests/test_a7_p1_reference_project.py` passed |
| P02 | FR-PRJ-007 | Duplicate code is refused and no partial project remains | Preserved and included in the reference scenario | T003 | Same test: second `A7P1-REF` returns 400 and the row count stays 1 |
| P03 | FR-PRJ-002/003; 008 FR-002/008/010 | Draft, submit, reject, approve, suspend, complete, archive | Preserved. No life-cycle code was changed | T005 | `test_project_registration_lifecycle.py` and `test_project_status_undo.py` passed |
| P04 | FR-PRJ-003; SC-PRJ-002 | Manager, scope, and amount are required together; an amount alone does not activate | Preserved | T005 | `test_submit_and_approve_with_gates` inside the lifecycle module passed |
| P05 | FR-PRJ-004 | Binding commitment and locked baseline stay blocked before approval and during suspension | Preserved. This phase did not change those gates | T005 | `test_project_archive_restore.py` includes the readiness gate check and was re-run in this session |
| P06 | FR-PRJ-005 | Six charter sections round-trip | Preserved and repeated on `A7P1-REF` | T003, T004 | Charter module and the reference scenario passed |
| P07 | FR-PRJ-006; SC-PRJ-003 | Direct edit of protected approved facts is refused; an approved request changes the value; reject or cancel does not | Preserved | T005 | `test_project_registration_change_request.py` passed |
| P09 | FR-RPA-001–006/014 | Restore returns to the prior state; unauthorized and stale confirmation are refused | Preserved. No archive code was changed | T005 | `test_project_archive_restore.py` and `test_project_archive_restore_permissions.py` re-run |
| P10 | FR-RPA-007–013 | Records, baselines, and a repeated action do not create a second effect | Preserved | T005 | `test_project_archive_restore_preservation.py` and `test_project_archive_restore_retries.py` re-run |
| P11 | FR-UPS-001–015 | Resume and undo completion stay separate, with reason, confirmation, and role rules | Preserved | T005 | `test_project_status_undo.py` passed. Browser Persian/English for those screens was not repeated |
| W01 | FR-WBS-001/003 | At least three levels, distinct from activity and cost classification | Preserved on the reference project | T006, T007 | Reference scenario and `test_wbs_structure_fields.py` passed |
| W02 | FR-WBS-002/004 | Responsible person and completion criterion round-trip | Preserved on the reference package | T006, T007 | Same tests |
| W03 | FR-WBS-005 | Duplicate code, foreign parent, and a cyclic move are refused | Duplicate and cycle already returned 400. A foreign parent previously raised an unhandled lookup error. It now returns 400 `invalid_parent` | T006 | Reference scenario. Existing cycle tests also passed |
| W05 | FR-WBS-007 | Editing a template does not change a project that already received it; a dependent replace stays blocked | Preserved. No template code was changed | T007 | `test_wbs_template_immutability.py` passed |
| W06 | FR-WBS from 004 | A successful move updates parent, depth, order, and dependent codes | Preserved. Move code was not changed except the foreign-parent rejection | T007 | Existing move coverage in `wbs/tests/test_services.py` was not re-run in this session. The cyclic move refusal was re-run |
| M01 | FR-DATA-003; FR-PRJ-001 | Staff alone must not create an organization unit. The allowed steward can, and the new unit can be selected on a project | Code already denied staff. The test expected 201. The test and the permission text now match the constitution and A.6: staff receives 403 and no row is stored. HR create and project selection are covered | T002, T008, T003 | `test_create_organization_unit_as_staff` and the reference scenario passed |
| M02 | FR-DATA-003; SC-DATA-004 | Contract type and measurement unit are manageable and validated | A new or changed project contract type must be an active catalog code. Blank and unchanged legacy values remain. Stewards can create a measurement unit on the organization-references screen | T009–T014 | Unit tests, legacy contract-type test, and the browser create flow |
| M03 | FR-DATA-003 versus FR-PRJ-002 | Do not turn project status into an open list | Decision recorded in research.md: project status stays the approved life cycle. Organization unit, contract type, and measurement unit are the manageable catalogs. No status route was added | T015 | `test_status_choices_include_lifecycle` passed. No new status value |
| M04 | Existing dynamic-table workbook | Use it only if the reference journey needs it. Do not merge it with work-breakdown import | The reference journey does not use a dynamic table. No workbook path was added or merged | T015 | No code change. Not a failed test |
| D01 | A.7.01 | Fingerprint, version, hand-counted examples, and a field matrix. Historical counts are not targets | `real-data/plan.mpp` was not modified. SHA-256 `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`, 777216 bytes. UIDs 8055, 8084, 8102, and 8120 are present summary tasks; the import activity map contains only leaves. The 83/79 counts stay historical | T016–T018, T028 | `evidence/test_control_figures.py` reads the MSPDI Summary flag without calling the importer |

## M01 policy

Constitution 1.1.0 and `IsHrOrAdmin` say the staff marker alone does not grant organization administration. Writers remain superuser and groups `admin`, `hr`, and `business-setup`. The historical test was the inconsistent artifact.

## M03 interpretation

The older base-data wording that statuses should be manageable catalogs does not replace the approved project life cycle. A steward cannot add a project status that has no transition.
