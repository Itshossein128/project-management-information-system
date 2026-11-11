# Tasks: Import Safety and History

**Input**: Design documents from `/specs/052-a7-p2-import-safety/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/import-safety.md, quickstart.md

**Tests**: Required by the specification's independent tests, the plan, and quickstart.md. Write the new assertions before the behavior they describe, and run them on the pytest database only.

**Organization**: Tasks follow user-story priority. Story 1 is the safety gate. Later stories add honest repeats, archive, recheck, failure, and attribution on that gate.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

## Path Conventions

- API: `apps/api/core/`
- Web: `apps/web/src/`
- Feature: `specs/052-a7-p2-import-safety/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Keep this phase pointed at its own feature directory.

- [x] T001 Confirm `output/a7-implementation/phase-map.json` contains key `a7-p2-import-safety` with `feature_directory` `specs/052-a7-p2-import-safety` and audit ids P08, W04, S05, I06, I07, I08, I11, I14, I18, without rewriting other phases

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: One shared safety module and the bilingual refusal text both file families will call.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Create `apps/api/core/schedule/services/import_safety.py` with a replacement check that returns the first of `wbs_has_progress`, `wbs_has_cost`, `wbs_has_documents`, `wbs_has_activities`, and `baseline_history_protected`. `baseline_history_protected` applies when a baseline has `is_locked` or a non-empty `approved_at`. A bare parent/child work-breakdown edge is not a refusal
- [x] T003 [P] Add Persian translations for those codes plus `project_archived`, `import_not_permitted`, and `import_actor_missing` in `apps/api/core/locale/fa/LC_MESSAGES/django.po`, and compile `apps/api/core/locale/fa/LC_MESSAGES/django.mo`. The code strings stay language-independent

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Replacement keeps existing history (Priority: P1) 🎯 MVP

**Goal**: Confirmed replacement from `.xml`, `.mpp`, and `.xer` does not physically delete activities, progress, cost, documents, or locked baseline rows. An unprotected project is soft-deleted like a forced template replacement.

**Independent Test**: On project code `A7P2-IMPORT-SAFETY` inside the pytest database, compare counts before and after replacement for a project that has an activity, progress, cost, a document, and a locked approved baseline, then repeat for a project with none of those.

### Tests for User Story 1

- [x] T004 [US1] Add failing protected and unprotected replacement assertions to `apps/api/core/schedule/tests/test_a7_p2_import_safety.py` for `.xml`, `.mpp`, and `.xer`, using project code `A7P2-IMPORT-SAFETY` only in that test database. Protected attempts leave every prior count unchanged and return one of `wbs_has_progress`, `wbs_has_cost`, `wbs_has_documents`, `wbs_has_activities`, or `baseline_history_protected`. Unprotected attempts report `wbs_nodes_removed` and `activities_removed`

### Implementation for User Story 1

- [x] T005 [P] [US1] In `apps/api/core/schedule/services/msp_import.py`, refuse replacement before any write when `import_safety` returns a code, and otherwise soft-delete live activities and live work-breakdown nodes from the deepest node upward with the confirming user. Do not call queryset `delete()` on activities, relationships, or work-breakdown nodes
- [x] T006 [P] [US1] Apply that same refuse-or-soft-delete path in `apps/api/core/schedule/services/p6_import.py` so `.xer` cannot keep the hard-delete path

**Checkpoint**: User Story 1 is testable on its own. An empty-project success does not satisfy it

---

## Phase 4: User Story 2 - Repeating a file does not pretend the plan changed (Priority: P1)

**Goal**: Append, a repeated file, and a repeated request do not create duplicate activities or relationships, do not publish a current baseline when nothing was added, and do not look like a changed plan.

**Independent Test**: Import one file, append it again, and read the completed job id. Counts of activities, relationships, and the current baseline stay honest.

### Tests for User Story 2

- [x] T007 [US2] Extend `apps/api/core/schedule/tests/test_a7_p2_import_safety.py` so overlapping append creates no duplicate activity or relationship, sets `nothing_changed` true and `schedule_version_changed` false, and creates no baseline when no node, activity, or relationship was added. Reading the finished job id returns the stored outcome and does not apply the file again. A later confirm creates a new job. A second start while the same user, project, mode, and file bytes are still pending or running returns the existing job id

### Implementation for User Story 2

- [x] T008 [P] [US2] In `apps/api/core/schedule/services/import_safety.py`, create the import baseline only when the attempt adds at least one node, activity, or relationship. `is_locked` stays false and `approved_at` stays empty. Set `is_current` true only when the project has no locked or approved current baseline; otherwise store `is_current` false. Fill `baseline_id`, `duplicates`, `schedule_version_changed`, and `nothing_changed` as in `specs/052-a7-p2-import-safety/contracts/import-safety.md`
- [x] T009 [P] [US2] In `apps/api/core/schedule/services/shared_import.py`, set `relations_created` from the number of relationships actually inserted, and list skipped codes in `duplicates` instead of counting attempts that `ignore_conflicts` drops
- [x] T010 [P] [US2] In `apps/api/core/schedule/views.py`, return the existing pending or running job with HTTP 202 when the same project, user, mode, and file bytes are already queued. Compute the hash in memory and do not store it. A completed job is not reused
- [x] T011 [P] [US2] In `apps/web/src/components/wbs/msp-import-wizard.tsx`, `apps/web/src/app/locales/en.json`, and `apps/web/src/app/locales/fa.json`, show a no-change result when `nothing_changed` is true and do not use the sentence that says the plan was imported successfully

**Checkpoint**: User Stories 1 and 2 both hold. A repeat that adds nothing does not become the current baseline

---

## Phase 5: User Story 3 - An archived project stays unchanged (Priority: P1)

**Goal**: A member with `edit_wbs` cannot change an archived project through preview, start, or confirm. A system administrator gains no new exception.

**Independent Test**: Archive a project with schedule history. Attempt preview, start, and confirm as a member, as a system administrator without membership, and as a system administrator who is an active member with `edit_wbs`.

### Tests for User Story 3

- [x] T012 [US3] Extend `apps/api/core/schedule/tests/test_a7_p2_import_safety.py` so an archived project plus an active member with `edit_wbs` refuses start and confirm with `project_archived` and leaves counts unchanged. Preview adds no work-breakdown, activity, relationship, progress, cost, document, or baseline row. A system administrator who is not an active member is refused. A system administrator who is an active member with `edit_wbs` is not refused for archive alone and still hits the User Story 1 history gate. Persian and English messages exist for `project_archived`

### Implementation for User Story 3

- [x] T013 [P] [US3] Enforce that archive rule on start in `apps/api/core/schedule/views.py` and again before apply in `apps/api/core/schedule/tasks.py`. System administrator means superuser or the `admin` group, and still requires active membership and `edit_wbs`. Observation alone must not pass
- [x] T014 [P] [US3] Show the server refusal in `apps/web/src/components/wbs/msp-import-wizard.tsx` before the wizard treats the import as started, with Persian and English strings in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`

**Checkpoint**: Membership and `edit_wbs` do not override archive

---

## Phase 6: User Story 4 - Authority is checked again when the import is applied (Priority: P2)

**Goal**: Losing membership or permission, or archiving the project after the job is queued, stops the apply. Another project's file, preview, progress, and result stay hidden.

**Independent Test**: Queue an import, remove permission or archive the project, then let apply run. Separately request that job from another project.

### Tests for User Story 4

- [x] T015 [US4] Extend `apps/api/core/schedule/tests/test_a7_p2_import_safety.py` so removing active membership or `edit_wbs` after the job exists fails apply with `import_not_permitted` and leaves domain counts unchanged. A job id requested under another project is not returned. Submitting a file for a different project does not change this project

### Implementation for User Story 4

- [x] T016 [US4] In `apps/api/core/schedule/tasks.py`, lock the project row with `select_for_update` inside the apply transaction and recheck that the confirming user still exists, is an active member, still has `edit_wbs`, and still passes the archive rule before calling the executor. Failure uses `import_not_permitted` or `project_archived` and writes no domain rows

**Checkpoint**: A queued job cannot finish after access was removed

---

## Phase 7: User Story 5 - Preview, failure, and overlap leave one consistent project (Priority: P2)

**Goal**: Preview and cancel write nothing. A failure before or during recording rolls back. Overlapping replacements do not delete twice or touch another project.

**Independent Test**: Preview and cancel on a populated project, force a failure before write and during write, then import a valid file. Start two replacements together.

### Tests for User Story 5

- [x] T017 [US5] Extend `apps/api/core/schedule/tests/test_a7_p2_import_safety.py` so preview and cancel leave record counts unchanged, a failure before write and a failure during write restore the pre-attempt counts and leave a failed job, a later valid import can finish, and two overlapping replacements do not hard-delete the same rows or change another project. The status body stays the job that was requested

### Implementation for User Story 5

- [x] T018 [US5] Keep `execute_msp_import` and `execute_p6_import` in `apps/api/core/schedule/services/msp_import.py` and `apps/api/core/schedule/services/p6_import.py` inside `transaction.atomic`, and raise the safety refusal before soft-delete so a refusal or a mid-write exception commits nothing. Do not change the preview parsers

**Checkpoint**: One failed attempt does not block the next valid attempt

---

## Phase 8: User Story 6 - Imported records name the person who made them (Priority: P2)

**Goal**: New imported rows name the confirming member. A missing member is not replaced by the oldest account.

**Independent Test**: Import as a known member and read `created_by` and `updated_by`. Remove that user before apply and confirm no other account is written.

### Tests for User Story 6

- [x] T019 [US6] Extend `apps/api/core/schedule/tests/test_a7_p2_import_safety.py` so new work-breakdown nodes, activities, relationships, and the working-copy baseline set `created_by` and `updated_by` to the confirming member. If that user is missing when the job is applied, the job fails with `import_actor_missing`, no domain rows are written, and no other user id is stored. The failed job still shows project, file, mode, and outcome

### Implementation for User Story 6

- [x] T020 [US6] Remove the oldest-account fallback in `apps/api/core/schedule/services/msp_import.py` and `apps/api/core/schedule/services/p6_import.py`. Pass the confirming user into work-breakdown `created_by` and `updated_by`, and into activity, relationship, and baseline `created_by` and `updated_by`. If the user is missing, raise `import_actor_missing` before any domain write

**Checkpoint**: Import history names the real member or names nobody rather than the wrong account

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Regression, the quickstart command, and the bilingual refusal journey.

- [x] T021 Run the pytest command in `specs/052-a7-p2-import-safety/quickstart.md` and keep `apps/api/core/schedule/tests/test_mpp_import.py` and `apps/api/core/schedule/tests/test_p6_import.py` green on the final tree. Django stays 4.2. Do not add a migration
- [x] T022 [P] Open the import confirmation for a protected project in Persian and in English, confirm replacement, and see the refusal before project data changes. Record the path, the result, and the limit that a pytest call of the import task is not a separately running worker in `specs/052-a7-p2-import-safety/evidence/verification.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup and blocks every user story
- **User Stories (Phases 3–8)**: Depend on Foundational. Implement in priority order because later stories edit the same executors
- **Polish (Phase 9)**: Depends on the stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational. No dependency on later stories
- **User Story 2 (P1)**: After User Story 1, because both change the executors. Its repeat checks assume replacement no longer hard-deletes
- **User Story 3 (P1)**: After Foundational. Archive refusal is independent of the repeat result, but apply-time wiring lands after the executor gate exists
- **User Story 4 (P2)**: After User Story 3, because it reuses the archive check inside the locked apply step
- **User Story 5 (P2)**: After User Story 1, because rollback is about the replacement write
- **User Story 6 (P2)**: After User Story 1, because attribution is set on the rows that replacement and append create

### Within Each User Story

- Tests are written and fail before that story's implementation
- The shared service is changed before the wizard copy that displays its result
- A story is verified before the next priority begins

### Parallel Opportunities

- T002 and T003 touch different files
- T005 and T006 touch different executors after T004
- T008, T009, T010, and T011 touch different files after T007
- T013 and T014 touch the API and the wizard after T012
- T022 can be prepared beside T021, and the browser note is written after the refusal is visible

---

## Parallel Example: User Story 2

```bash
# After T007 fails for the missing result fields:
# T008 apps/api/core/schedule/services/import_safety.py
# T009 apps/api/core/schedule/services/shared_import.py
# T010 apps/api/core/schedule/views.py
# T011 apps/web/src/components/wbs/msp-import-wizard.tsx
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3
3. Stop and compare protected and unprotected projects in the pytest database

### Incremental Delivery

1. Foundation and User Story 1 stop physical deletion of history
2. User Story 2 stops a repeat from publishing an empty current baseline
3. User Story 3 closes the archived-project bypass
4. User Stories 4–6 add recheck, rollback, and attribution
5. Phase 9 runs the quickstart and the browser refusal

### Parallel Team Strategy

One implementer should take the executors in order. A second person can take the wizard tasks T011 and T014 after the API result and error codes exist.

---

## Notes

- [P] tasks are different files and do not wait on each other inside the same story
- Project code `A7P2-IMPORT-SAFETY` belongs only to the pytest database
- Do not rewrite parsers, preview layout, field mapping, or the access policy
- A synchronous pytest call of the import task is not evidence of a separate worker
