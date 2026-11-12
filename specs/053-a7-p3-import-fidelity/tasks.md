# Tasks: Import Fidelity for WBS, Activities, and Schedule

**Input**: Design documents from `/specs/053-a7-p3-import-fidelity/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/import-fidelity.md, quickstart.md

**Tests**: Required by the specification's independent tests, the plan, and quickstart.md. Write each story's assertions before the behavior they describe. Use project code `A7P3-IMPORT-FIDELITY` only inside the pytest database. Do not modify `real-data/plan.mpp`.

**Organization**: Tasks follow the user-story order in spec.md. Story 1 is the parent map. Later stories add blocking rules, activity fields, date separation, schedule views, and stored file equality.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

## Path Conventions

- API: `apps/api/core/`
- Web: `apps/web/src/`
- Feature: `specs/053-a7-p3-import-fidelity/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Keep this phase pointed at its own feature directory.

- [x] T001 Confirm `output/a7-implementation/phase-map.json` contains key `a7-p3-import-fidelity` with `feature_directory` `specs/053-a7-p3-import-fidelity` and audit ids W07, S01, S02, S03, S04, S06, S07, S08, I01, I03, I04, I05, I12, I13, I21, I22, without rewriting other phases

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Nullable activity columns and one resolver both file families will call. The resolver writes nothing.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 [P] Add nullable columns on `Activity` in `apps/api/core/projects/models.py` and a new migration under `apps/api/core/projects/migrations/`: `planned_percent` is `DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)`; `is_critical` is `BooleanField(null=True, blank=True)` with no default that backfills existing rows; `total_slack_days` and `free_slack_days` are `IntegerField(null=True, blank=True)`. Do not backfill. Django stays 4.2.11
- [x] T003 [P] Create `apps/api/core/schedule/services/import_fidelity.py` with a pure `resolve` function that returns work packages, activities, links, blocking codes, warnings with row identity, and created/omitted/warned counts. It must not touch the database. Include every code in `specs/053-a7-p3-import-fidelity/contracts/import-fidelity.md`
- [x] T004 [P] Add Persian strings for every code in that contract to `apps/api/core/locale/fa/LC_MESSAGES/django.po`, compile `apps/api/core/locale/fa/LC_MESSAGES/django.mo`, and add the same codes to `apps/web/src/app/locales/en.json` and `apps/web/src/app/locales/fa.json`. The code strings stay language-independent

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - The file's parent is the stored parent (Priority: P1) 🎯 MVP

**Goal**: Preview and the saved schedule use the parent identifier in the file. A leaf with no resolvable parent is not stored and is not attached to another row.

**Independent Test**: On project code `A7P3-IMPORT-FIDELITY`, import `specs/051-a7-p1-project-reference/evidence/fixtures/branch.xml` and `branch.xer`. Each child sits under the parent named in the file in both the preview and the saved rows. Reordering those parent identifiers does not move the child. `relation.xml` and `relation.xer` report `activity_without_parent` and store no activity.

### Tests for User Story 1

- [x] T005 [US1] Add failing parent assertions to `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py` for `branch.xml`, `branch.xer`, a reordered copy of those parent identifiers, `relation.xml`, and `relation.xer`. Saved and preview parents match the file. A leaf with no resolvable parent is `activity_without_parent` and creates no activity. Use project code `A7P3-IMPORT-FIDELITY` only in the pytest database

### Implementation for User Story 1

- [x] T006 [US1] In `apps/api/core/schedule/services/import_fidelity.py`, set a Microsoft Project parent from the outline number without its last segment, matched to another row's outline number. Set a Primavera work-package parent from `parent_wbs_id` and an activity's package from `wbs_id`. Do not use row order, code sort, the last node at a level, or the first or last package. A summary with no parent is a root. A leaf with no resolvable parent stays `activity_without_parent`
- [x] T007 [US1] Make `build_preview` and `execute_msp_import` in `apps/api/core/schedule/services/msp_import.py`, and `execute_p6_import` in `apps/api/core/schedule/services/p6_import.py`, consume that resolved plan. Remove the fallback that treats every row as a summary when no summary exists, and remove the fallbacks that attach an activity to the first or last package

**Checkpoint**: User Story 1 is testable on its own. A child under the wrong sibling fails it

---

## Phase 4: User Story 2 - Unsafe structure is stopped before the project changes (Priority: P1)

**Goal**: Finish-before-start, a cycle, a self-link, and an in-file duplicate write nothing, including in replacement mode. Warning rows are named and omitted without reparenting.

**Independent Test**: For each blocking case, project counts match the pre-confirm state. For each warning case, the named row or link is omitted and the other valid rows match the file. Preview and confirm show the same code.

### Tests for User Story 2

- [x] T008 [US2] Extend `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py` so `finish_before_start`, `structure_cycle` (parent chain, activity-link chain, and a self-link), and `duplicate_in_file` leave every project count unchanged in replace mode and do not call replacement. `predecessor_missing`, `relation_type_invalid`, `depth_exceeded`, and `empty_import` match `specs/053-a7-p3-import-fidelity/contracts/import-fidelity.md`: the named row or link is omitted, descendants of a too-deep row are not moved under an ancestor, and an empty result is not a successful plan change. Preview codes match confirm codes

### Implementation for User Story 2

- [x] T009 [US2] In `apps/api/core/schedule/services/import_fidelity.py`, `apps/api/core/schedule/services/msp_import.py`, and `apps/api/core/schedule/services/p6_import.py`, classify those cases before `guard_and_maybe_replace`. A blocking code raises and leaves the project unchanged. A duplicate against a code already stored in the project stays the existing append skip and is not `duplicate_in_file`
- [x] T010 [P] [US2] In `apps/web/src/components/wbs/msp-import-wizard.tsx`, show the blocking code's localized text from `apps/web/src/app/locales/en.json` and `apps/web/src/app/locales/fa.json` and do not show a successful plan-change message. Show warning codes with their row identity

**Checkpoint**: User Stories 1 and 2 both hold. A blocking file does not remove existing work

---

## Phase 5: User Story 3 - Supported facts arrive on the activity (Priority: P1)

**Goal**: Duration, milestone, planned percent, critical, and slack are stored on the activity. A snapshot-only value does not pass. Delay and duration convert only when they are an exact number of eight-hour days.

**Independent Test**: Import `milestone.xml`, `milestone.xer`, a link lag of 4800, and a delay that is not an exact number of days. Read the saved activity fields, not only `BaselineActivity`.

### Tests for User Story 3

- [x] T011 [US3] Extend `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py` so `milestone.xml` stores `duration_days` 0 and `is_milestone` true, and `milestone.xer` stores `duration_days` 0 and `is_milestone` false. `PT16H0M0S` is 2 days, `PT8H0M0S` is 1 day, and `PT0H0M0S` is 0 days. Microsoft Project `LinkLag` 4800 stores `lag_days` 1. A lag or Primavera hour count that does not divide evenly by the eight-hour day is `lag_not_whole_days` or `duration_not_whole_days` and is not rounded or forced up to 1. `planned_percent` outside 0 through 100 is `invalid_percent` and stays null. A milestone flag with a non-zero duration is `milestone_duration_conflict`, keeps the duration, and leaves `is_milestone` false. A file with a calendar warns `calendar_not_applied` once and leaves `working_calendar` null. `Activity.weight` stays null

### Implementation for User Story 3

- [x] T012 [US3] Convert duration, `LinkLag`, slack, and Primavera hours in `apps/api/core/schedule/services/import_fidelity.py` using the unit table in `specs/053-a7-p3-import-fidelity/contracts/import-fidelity.md`. One day is 8 hours. Microsoft Project lag and slack are tenths of a minute, so 4800 is 1 day. Stop using `max(1, round(...))` and integer floor division in `apps/api/core/schedule/services/msp_import.py` and `apps/api/core/schedule/services/p6_import.py`
- [x] T013 [US3] In `apps/api/core/schedule/services/shared_import.py`, write `duration_days`, `is_milestone`, `planned_start`, `planned_finish`, `planned_percent`, `is_critical`, `total_slack_days`, and `free_slack_days` on the new `Activity`. Copy those converted values onto the working-copy rows in `baseline_rows_for` in `apps/api/core/schedule/services/import_safety.py`. Do not set `Activity.weight`. Do not call the project default calendar

**Checkpoint**: User Story 3 is testable on its own. A duration that exists only on the working copy fails it

---

## Phase 6: User Story 4 - Planned, approved, actual, and forecast stay separate (Priority: P1)

**Goal**: Planned dates come from planned fields. Actual dates are written only onto a new activity when the file has them. Forecast stays empty. An append does not change an existing actual date. The working copy stays unapproved.

**Independent Test**: Import a file with planned dates only, then a file with both planned and actual dates, then append over an activity that already has an actual date. Read all four date kinds and the working-copy lock and approval fields.

### Tests for User Story 4

- [x] T014 [US4] Extend `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py` so planned dates come only from Microsoft Project `Start`/`Finish` or Primavera `target_start_date`/`target_end_date`. Actual dates on a new activity come only from `ActualStart`/`ActualFinish` or `act_start_date`/`act_end_date`. An actual value is never copied into a planned field. `forecast_start` and `forecast_finish` stay null. Appending a duplicate code leaves that activity's actual dates unchanged. The working copy keeps `is_locked` false and `approved_at` empty

### Implementation for User Story 4

- [x] T015 [US4] In `apps/api/core/schedule/services/msp_import.py` and `apps/api/core/schedule/services/p6_import.py`, stop using `act_start_date` or `act_end_date` as a fallback for a missing target date. Pass actual dates only for a newly created activity in `apps/api/core/schedule/services/shared_import.py`. Leave forecast null. Keep the existing append skip so an existing activity is not updated

**Checkpoint**: User Stories 1 through 4 hold. Import does not become an approved baseline

---

## Phase 7: User Story 5 - Imported facts show up where the schedule is used (Priority: P2)

**Goal**: The Gantt and the milestone report show a stored milestone and its planned date. An incomplete duration stays not calculable. Earned-value formulas stay unchanged.

**Independent Test**: Import one milestone with a planned date and one activity with `duration_days` null. Open the milestone list and the critical-path gate.

### Tests for User Story 5

- [x] T016 [US5] Extend `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py` so the schedule status payload lists an imported milestone from `Activity.is_milestone` with its planned finish, and `evaluate_critical_path_validity` in `apps/api/core/schedule/services/critical_path_validity.py` returns `valid` false and an empty `critical_activity_ids` when any activity has `duration_days` null, even if `is_critical` is true. The Gantt payload includes `is_milestone`

### Implementation for User Story 5

- [x] T017 [US5] Add `is_milestone` to the task payload in `apps/api/core/schedule/services/gantt_service.py` and show that mark in `apps/web/src/app/routes/project-schedule-gantt.tsx` without changing how critical flags are chosen
- [x] T018 [P] [US5] Confirm `apps/api/core/schedule/services/status_report_service.py` already lists `Activity.is_milestone`, and do not change earned-value formulas in `apps/api/core/schedule/services/period_report_service.py` or `apps/api/core/schedule/services/evm_service.py`

**Checkpoint**: A stored milestone is visible. An incomplete network is not labeled valid

---

## Phase 8: User Story 6 - A bad file is still rejected, and twins match after save (Priority: P1)

**Goal**: Unsafe files still change nothing. A paired native file and XML file match after save. The four summary predecessors are explained and are not activity links.

**Independent Test**: Reject one unsafe file of each existing kind. Compare stored rows for a paired MPP and XML file when the converter runs. Import a summary-predecessor fixture and read `predecessor_is_summary`.

### Tests for User Story 6

- [x] T019 [US6] Extend `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py` with a summary-predecessor fixture shaped like employer identifiers 8055, 8084, 8102, and 8120 on successor پایان. Each link is `predecessor_is_summary`, the summary stays a work package, and no activity link is created. A zero-duration form on tasks named شروع and پایان stores `duration_days` 0. Do not assert that 83 source links equal 79 stored links. Do not modify `real-data/plan.mpp`
- [x] T020 [P] [US6] Extend `apps/api/core/schedule/tests/test_mpp_equivalence.py` so a paired native file and XML file match on stored hierarchy, dates, durations, milestones, links, and warnings, not only on the preview subset. When the MPP converter cannot run, record that limit in the test output and do not treat the preview comparison as this proof. Keep the existing corrupt, password, renamed, and oversized rejections in `apps/api/core/schedule/tests/test_mpp_import.py` unchanged

### Implementation for User Story 6

- [x] T021 [US6] In `apps/api/core/schedule/services/import_fidelity.py`, classify a predecessor whose resolved row is a summary as `predecessor_is_summary` and omit that link. Keep the existing file-size, password, corrupt, renamed, and unsupported rejections in `apps/api/core/schedule/services/msp_import.py` and `apps/api/core/schedule/services/mpp_convert.py` on their current codes

**Checkpoint**: User Story 6 does not weaken file rejection or the parent rule

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Run the quickstart and the bilingual screen check after the stories are in place.

- [x] T022 Run the pytest command in `specs/053-a7-p3-import-fidelity/quickstart.md` from `apps/api/core` and keep `schedule/tests/test_a7_p2_import_safety.py` green on the final tree. Django stays 4.2.11
- [x] T023 [P] On a disposable project with code `A7P3-IMPORT-FIDELITY`, import a small file that stores one milestone and warns `calendar_not_applied`. In Persian and in English, read that warning in `apps/web/src/components/wbs/msp-import-wizard.tsx` and the same milestone and planned date on the Gantt or schedule status screen. Record the path and the result in `specs/053-a7-p3-import-fidelity/evidence/verification.md`. A synchronous import-task call is not a separately running worker

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup. Blocks every user story.
- **User Stories (Phase 3+)**: Depend on Foundational. Spec order is US1, US2, US3, US4, US5, US6.
- **Polish (Phase 9)**: Depends on the stories being present.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational. No dependency on later stories.
- **User Story 2 (P1)**: Starts after Foundational. Uses the same resolver as US1 and should land after US1 so the parent tests stay meaningful.
- **User Story 3 (P1)**: Starts after the activity columns from Foundational. Field writes assume the resolved plan from US1.
- **User Story 4 (P1)**: Starts after US3's activity writer so planned and actual dates go to the fields that writer owns.
- **User Story 5 (P2)**: Starts after US3 stores `is_milestone` and `duration_days`. It does not change the import rules.
- **User Story 6 (P1)**: The unsafe-file regression can be checked at any time. The stored twin comparison and the summary-predecessor check should run after US1 through US4.

### Within Each User Story

- Write the story's test so it fails before the implementation task.
- Do not start the next story's implementation on a file the current story is still changing.

### Parallel Opportunities

- T002, T003, and T004 touch different files and can run together after T001.
- T010 can run beside T009 after T008, because the wizard only displays codes the contract already names.
- T018 can run beside T017 after T016.
- T020 can run beside T019. T021 waits until the summary-predecessor assertion exists.

---

## Parallel Example: Foundational

```bash
Task: "Add nullable Activity columns in apps/api/core/projects/models.py"
Task: "Create the pure resolver in apps/api/core/schedule/services/import_fidelity.py"
Task: "Add bilingual code strings in django.po, en.json, and fa.json"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3.
3. Stop and run the User Story 1 parent assertions.

### Incremental Delivery

1. Foundation, then parents.
2. Add blocking and warning classification.
3. Add activity fields and exact day conversion.
4. Add date separation.
5. Show the milestone and the critical-path gate.
6. Compare stored twins and the summary-predecessor decision.
7. Run the quickstart pytest set and the Persian and English browser check.

### Parallel Team Strategy

After Foundational, one person can own the resolver and both executors while another owns wizard text and the Gantt mark. The executors are one file path per family, so those two implementation tasks stay sequential.

---

## Notes

- [P] tasks use different files and do not depend on an unfinished task.
- Each story is checked on project code `A7P3-IMPORT-FIDELITY` in the pytest database.
- Historical counts of 83 source links and 79 stored relationships are not pass targets.
- Contract changes for the next phase are calendar non-support and the summary-link decision in `specs/053-a7-p3-import-fidelity/contracts/import-fidelity.md`.


## Phase 10: Convergence

- [x] T024 CRITICAL Complete bilingual import feedback in `apps/web/src/components/wbs/msp-import-wizard.tsx`, its API types, and `apps/web/src/app/locales/en.json` / `fa.json`: replace hard-coded labels in the import flow, render each final warning with its stable code and row identity rather than only a count, and localize failed-job codes in the active language instead of relying on worker-locale text. Verify warning and failure results in both languages, including a language switch after preview, and record evidence in `specs/053-a7-p3-import-fidelity/evidence/verification.md` per Constitution III, FR-017, US5/AC3, and T010/T023 (partial)
- [x] T025 CRITICAL Trace the four new imported activity fields through `apps/api/core/schedule/serializers.py`, `apps/web/src/app/lib/api/activities.ts`, and `apps/web/src/components/activities/activity-drawer.tsx`: expose and display stored `planned_percent`, nullable `is_critical`, `total_slack_days`, and `free_slack_days` with bilingual labels and explicit unknown values, without adding an unrequested editing workflow. Add API assertions and a bilingual activity-detail check against an imported example per Constitution II, US3/AC3, FR-006, and T002/T013 (partial)
- [x] T026 CRITICAL Make an empty resolved import return an unchanged outcome before destructive replacement in `apps/api/core/schedule/services/msp_import.py` and `p6_import.py`, while retaining authorization and safety checks. Add pytest cases on a WBS-only project for an empty structure and a file whose rows are all omitted: preserve every existing node, create no working copy, retain `empty_import`, and report `nothing_changed` true. An isolated current-tree probe of `<Project><Tasks/></Project>` with replace enabled removed one root and returned `nothing_changed` false per Constitution IV, FR-004, US2/AC4, and plan: unchanged empty result (contradicts)
- [x] T027 CRITICAL Preserve resolved parent identities when sorted Treebeard insertions move earlier roots or siblings in `apps/api/core/schedule/services/msp_import.py` and `p6_import.py`; refresh or otherwise maintain cached WBS paths before further child insertion. Add stored-parent assertions for reordered multi-root and nested-summary files in both families, including insertion order root B, summary B.1, root A, summary B.1.1, leaf B.1.1.1. The current MSP probe stores a descendant whose `get_parent()` raises `WBS.DoesNotExist`; assert all stored ancestors and preview parents agree without changing other projects per FR-001, US1/AC1-2, SC-001, and T005/T007 (contradicts)
- [x] T028 CRITICAL Remove the `OutlineNumber` fallback to `WBS` in `apps/api/core/schedule/services/msp_import.py` when deriving parent identity. Keep WBS codes as codes; a dotted code with no outline parent identity must not attach a leaf to a package. Add preview and stored-result regressions for missing outline identity, mixed dotted and undotted codes, and reordered rows, preserving `activity_without_parent` and the current omission rule per FR-001, FR-003, US1/AC2/AC5, and T006 (contradicts)
- [x] T029 Add shared outcome accounting to `ResolvedPlan` and the preview/confirm API payloads in `apps/api/core/schedule/services/import_fidelity.py`, both executors, `shared_import.py`, and the wizard API types. Expose created, omitted, and warned row/link counts, preserve parser warnings, and account for project-specific append duplicates so preview and the saved outcome agree on counts, parents, and omission reasons. Add equality assertions for clean, depth-omitted, orphan, empty, and append-duplicate trials per FR-005, SC-009, US2/AC3, and T003/T007 (partial)
- [x] T030 Carry every blocking diagnostic and stable source row identifier through `ImportFidelityError`, both executors, `apps/api/core/schedule/tasks.py`, job persistence/status in `views.py`, and the wizard. Do not discard `PlanNote.row` or all but the first blocking condition; names alone must not make distinct source rows indistinguishable. Assert preview and failed-job results identify the same offending rows and codes while all project data stays unchanged per FR-004, FR-005, US2/AC1/AC3, and T008-T010 (partial)
- [x] T031 Parse supported Primavera critical flags, total float, and free float in `apps/api/core/schedule/services/p6_import.py` and populate the shared parsed-task fields consumed by `shared_import.py` and `import_safety.baseline_rows_for`. Convert float hours exactly to eight-hour days, preserve absent values as null, and warn on inexact supplied slack. Add XER assertions for stored Activity and working-copy values, including explicit false and zero, per FR-006, US3/AC3, SC-003, plan: referenced data-model field mapping, and T012/T013 (missing)
- [x] T032 Complete the imported-network validity gate in `apps/api/core/schedule/services/critical_path_validity.py` and its import-result inputs: treat a missing imported duration as incomplete even when planned dates or a critical flag are present, and retain enough provenance to detect required relationships omitted during import rather than treating their absence as a complete network. Distinguish legitimate linkless examples from omitted-link cases. Assert invalid results suppress critical/near-critical IDs on the Gantt and status report, with localized reasons, per FR-011, US5/AC2, SC-006, and T016 (partial)
- [x] T033 Classify source predecessor links before filtering successors out of the storage plan in `apps/api/core/schedule/services/import_fidelity.py`. For unchanged `real-data/plan.mpp`, report UIDs 8055, 8084, 8102, and 8120 as `predecessor_is_summary` on successor پایان in both preview and confirm, even though that successor currently has no resolvable parent; do not create activity links or convert summaries into activities. Add a fingerprint-checked employer-file regression on the pytest database and preserve existing orphan warnings per FR-014, US6/AC3, SC-008, and T019/T021 (partial)
- [x] T034 Resolve the artifact conflict between FR-003/T005-T007 (omit activities without a resolvable parent; Activity.wbs remains required) and FR-015/US6/AC5 (store zero duration on the actual employer-file شروع and پایان activities). Read-only conversion of the unchanged employer file gives these rows outline identities 1 and 8, both with no parent, so neither is stored. Obtain an explicit scope decision before changing storage or parent rules; do not invent a parent or count synthetic parented fixtures as employer-file acceptance. After that decision, add stored-result and unchanged-fingerprint evidence in `specs/053-a7-p3-import-fidelity/evidence/verification.md` per FR-003, FR-015, FR-016, US6/AC5, and T019 (contradicts)
- [x] T035 Replace the vacuous stored twin proof in `apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py` / `test_mpp_equivalence.py` with a genuine native MPP/XML pair containing resolvable packages, activities, a milestone, and supported relationships. Assert nonempty stored results and compare hierarchy, supported activity facts, date kinds, link types/delays, and normalized warning codes/row identities. The current duration-test9 pair resolves to zero packages, activities, and links, and its snapshot excludes warnings. Narrow converter-unavailable skips to known environmental failures and record actual converter coverage per FR-013, US6/AC2, SC-007, and T020 (partial)
- [x] T036 Complete the invalid-weight classification required by the spec: first resolve the missing accepted source-field and warning-code definition in the referenced import support contract, then add row-identified warnings through the shared resolver, preview, confirm, and bilingual presentation for supplied invalid parent-share weights. Keep Activity.weight null, never substitute percent complete for weight, and never guess a replacement share. Add an authored invalid-weight regression for each supported mapping established by that decision per FR-004, US2/AC4, SC-002, and T003 (missing)
