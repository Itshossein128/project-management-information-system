# Tasks: Reference Project and Base Data

**Input**: Design documents from `/specs/051-a7-p1-project-reference/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required by the specification and constitution. Regression tests for existing project, charter, life cycle, and work-breakdown behavior are part of the stories that preserve that behavior.

**Organization**: Tasks follow user-story priority. Stories 1–3 and 5 preserve current behavior. Story 4 and story 6 add the proven gaps and the schedule contract.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

## Path Conventions

- API: `apps/api/core/`
- Web: `apps/web/src/`
- Feature evidence: `specs/051-a7-p1-project-reference/`

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Record phase map entry `a7-p1-project-reference` → `specs/051-a7-p1-project-reference` in `output/a7-implementation/phase-map.json` without replacing other phases

## Phase 2: Foundational (Blocking Prerequisites)

- [x] T002 Align the `IsOrgRefWriterOrReadOnly` docstring in `apps/api/core/master_data/permissions.py` with the constitution: staff alone cannot write organization references

## Phase 3: User Story 1 - Register and reopen a real project (Priority: P1)

**Goal**: A complete draft, including the six charter sections, can be saved and reopened, and a duplicate code is refused.

**Independent Test**: `projects/tests/test_a7_p1_reference_project.py` plus `projects/tests/test_project_registration_charter.py`

- [x] T003 [US1] Add the `A7P1-REF` create, reopen, charter, and duplicate-code assertions to `apps/api/core/projects/tests/test_a7_p1_reference_project.py`
- [x] T004 [US1] Run `projects/tests/test_project_registration_charter.py` and keep the existing charter behavior

## Phase 4: User Story 2 - Approved life cycle (Priority: P1)

**Goal**: Submit, approval gates, and protected edits stay on the current life cycle. No parallel archive or undo design.

**Independent Test**: `projects/tests/test_project_registration_lifecycle.py`

- [x] T005 [US2] Run `projects/tests/test_project_registration_lifecycle.py`, `projects/tests/test_project_registration_change_request.py`, and `projects/tests/test_project_status_undo.py` against the final tree. Change life-cycle code only if a run shows a proven defect

## Phase 5: User Story 3 - Three-level work breakdown (Priority: P1)

**Goal**: The reference project can store three levels with a responsible person and a completion criterion. Template edits do not rewrite an applied project.

**Independent Test**: work-breakdown section of the reference scenario, `wbs/tests/test_wbs_structure_fields.py`, and `project_templates/tests/test_wbs_template_immutability.py`

- [x] T006 [US3] Cover three nested packages, a duplicate code, a foreign parent, and a cyclic move inside `apps/api/core/projects/tests/test_a7_p1_reference_project.py`
- [x] T007 [US3] Run `wbs/tests/test_wbs_structure_fields.py`, `wbs/tests/test_wbs_cycle_move.py`, and `project_templates/tests/test_wbs_template_immutability.py`

## Phase 6: User Story 4 - Governed organization references (Priority: P1)

**Goal**: Staff cannot create an organization unit. Stewards can add a unit, a contract type, and a measurement unit. A new project contract type must be an active catalog code.

**Independent Test**: `master_data/tests/test_org_refs.py`, `master_data/tests/test_units.py`, and the catalog section of the reference scenario. Browser pass on `/settings/org-refs`.

- [x] T008 [US4] Change `test_create_organization_unit_as_staff` in `apps/api/core/master_data/tests/test_org_refs.py` so a staff-only account receives 403 and no unit is stored
- [x] T009 [US4] Validate `contract_type` in `apps/api/core/projects/serializers.py` for create and update, allowing a blank value and an unchanged legacy value
- [x] T010 [US4] Add Persian messages for the new validation strings in `apps/api/core/locale/fa/LC_MESSAGES/django.po` and compile them
- [x] T011 [US4] Accept `POST /api/v1/measurement-units/` for organization-reference writers in `apps/api/core/master_data/ref_serializers.py`, `ref_views.py`, and `urls.py`
- [x] T012 [P] [US4] Add `apps/api/core/master_data/tests/test_units.py` for steward create, staff denial, blank name, and duplicate name
- [x] T013 [P] [US4] Add the measurement-unit form to `apps/web/src/app/routes/settings-org-refs.tsx` and `createMeasurementUnit` in `apps/web/src/app/lib/api/central-data.ts`
- [x] T014 [US4] In `apps/web/src/app/routes/project-create-wizard.tsx`, set contract type `EPC` from a template only when that code is in the loaded catalog

## Phase 7: User Story 5 - Project status stays governed (Priority: P2)

**Goal**: No new status catalog. The interpretation is recorded for the audit id M03.

**Independent Test**: Status choices remain those asserted by `test_status_choices_include_lifecycle`

- [x] T015 [US5] Record the life-cycle decision in `specs/051-a7-p1-project-reference/traceability.md` for M03 and do not add a status-admin route

## Phase 8: User Story 6 - Schedule reference contract (Priority: P2)

**Goal**: Fingerprint the unchanged employer file and add hand-counted XML/XER examples plus the historical mismatch list.

**Independent Test**: `specs/051-a7-p1-project-reference/evidence/test_control_figures.py` does not call the importer

- [x] T016 [P] [US6] Write `evidence/fixtures/` examples for a branch, a milestone, a relationship, a dangling predecessor, and an invalid root
- [x] T017 [US6] Write `evidence/control-figures.json` with the SHA-256 of `real-data/plan.mpp` and the hand counts
- [x] T018 [US6] Add `evidence/test_control_figures.py` to recount fixture tags and compare the employer-file hash without importing the schedule parser

## Phase 9: Polish & Cross-Cutting Concerns

- [x] T019 Write `traceability.md`, `evidence/verification.md`, and `handoff.md` with the audit id matrix, the code version, what was run, and ready-for-review status
- [x] T020 Run the quickstart pytest set on the final tree and the browser create flow for one measurement unit

## Dependencies & Execution Order

### Phase Dependencies

- Setup and the permission text come first.
- Stories 1–3 can be verified in parallel with story 4's serializer work.
- Story 6 does not depend on the API changes.
- Polish runs after the tests.

### User Story Dependencies

- US1, US2, and US3 share the reference scenario file, so T003 and T006 are edited together.
- US4 depends on T002 for the documented rule, then T008–T014.
- US5 is documentation only.
- US6 is independent.

### Parallel Opportunities

- T012 and T013 can proceed once T011's request shape is fixed.
- T016 can proceed beside the API work.

## Implementation Strategy

Preserve existing registration, life cycle, and work-breakdown code. Implement the catalog gap and the schedule contract. Do not start A.7-P2.

## Notes

- Checkbox state is implementation progress, not employer acceptance.
- Employer sign-off stays with phase 6 of A.7. This phase ends ready for review when T020 evidence is recorded.

## Phase 10: Convergence

- [x] T021 CRITICAL: Add English and Persian catalog entries for the measurement-unit heading, symbol label, and success message, and name measurement units in the organization-references subtitle in both locales, so an English session does not show Persian fallback text per Constitution III (contradicts)
- [x] T022 Refuse a project code that matches an existing code only after trimming, on create and update, with the existing understandable duplicate-code message and no new or changed row per FR-002 (partial)
- [x] T023 Refuse an organization-unit save that sets the unit as its own parent; the create check that compares the chosen parent's parent with that parent does not implement this rule per spec: organization-unit parent edge case (partial)
- [x] T024 Record the two zero-duration historical mismatches under the schedule-contract identifiers `H-DUR-شروع` and `H-DUR-پایان` per plan: schedule reference contract (partial)


## Phase 11: Convergence

- [x] T025 CRITICAL: Enforce the independent project approver required by US2 in `apps/api/core/projects/lifecycle_service.py` and the project approval API; retain the submitting actor with the current submission so the submitter cannot activate their own project merely by possessing `approve_project`, preserve the existing active-membership and permission checks, and cover same-actor refusal plus a different authorized actor succeeding without changing the project or budget-approval stamp on refusal. Update existing lifecycle tests that currently submit and approve with the same `auth_client` instead of treating those passes as separation-of-duties evidence per US2 independent approver, FR-004, and Constitution I (contradicts)
- [x] T026 CRITICAL: Complete final-tree verification for the changed reference-catalog and project-reference journey, including real browser checks in Persian and English for measurement-unit create/list, validation and refusal feedback, catalog selection and reopen; exercise the relevant reference scenario and preserved lifecycle/WBS checks after corrective code changes, then update `specs/051-a7-p1-project-reference/evidence/verification.md`, `traceability.md`, and `handoff.md` with actual commands, results, code identity, and remaining limits. The current evidence explicitly omits English browser verification and does not establish verification after T021–T024; this convergence run observed 60 selected backend tests and 4 fixture tests passing, including successful WBS move/renumber coverage, but those passes are not bilingual browser evidence. Do not modify shared development catalog data to obtain proof or claim employer acceptance per SC-001/002/003/005/006, T019/T020/T021, and Constitution III/VI (partial)
- [x] T027 Apply trimmed project-code uniqueness consistently to the existing `ProjectViewSet.from_template` / `business_meta.services.create_project_from_template` creation path as well as normal project create/update, reusing the same rule rather than adding an alternate interpretation. Add API regressions for an existing code with surrounding whitespace, an already padded legacy code, and an all-whitespace candidate; reject invalid/duplicate requests without creating a project, membership, table, or field, and keep valid template creation working per FR-002, the project-code whitespace edge case, T022, and Constitution II (partial)
- [x] T028 Correct the historical mismatch causes in `specs/051-a7-p1-project-reference/contracts/schedule-reference.md`, `evidence/control-figures.json`, and dependent research/traceability/handoff text: current read-only conversion of unchanged `real-data/plan.mpp` found UIDs 8055, 8084, 8102, and 8120 among the 80 parsed tasks as summary nodes, whereas `execute_msp_import` builds its activity UID map only from leaves. Distinguish present summary tasks from genuinely dangling predecessor identifiers, retain the historical observations and the file fingerprint, and add an independent check or reproducible source evidence for the corrected classification. Do not change the importer, remove links, or turn the historical 83/79 figures into approved targets in this phase per FR-015, US6/AC2, SC-004, and plan: independent schedule reference contract (contradicts)
- [x] T029 Repair and validate the reproducible verification instructions in `specs/051-a7-p1-project-reference/quickstart.md`: from `apps/api/core`, the documented `../../.venv/bin/python` points to the nonexistent `apps/.venv`; use a verified installed interpreter, make the working directory of each command unambiguous, and include the reference-contract tests and the final relevant verification set with an isolated test database. Record any remaining environment prerequisite rather than publishing an unexecutable handoff per plan: Testing/Constraints, T019/T020, and SC-001 (partial)
