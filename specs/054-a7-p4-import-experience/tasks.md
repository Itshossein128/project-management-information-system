# Tasks: Schedule Import Experience

**Input**: Design documents from `/specs/054-a7-p4-import-experience/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/import-experience.md, quickstart.md

**Tests**: Required by the specification's independent tests, the plan, and quickstart.md. Write each story's pytest assertions before the behavior they describe. Use project code `A7P4-IMPORT-EXPERIENCE` only inside the pytest database. Do not modify `real-data/plan.mpp`. Do not import into a shared or UAT project. Django stays 4.2.11. No migration.

**Organization**: Tasks follow the user-story order in spec.md. Story 1 is the recognizable file and preview. Later stories add reconcilable figures, translated recovery, one bound attempt, and keyboard layout.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)

## Path Conventions

- API: `apps/api/core/`
- Web: `apps/web/src/`
- Feature: `specs/054-a7-p4-import-experience/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Keep this phase pointed at its own feature directory.

- [x] T001 Confirm `output/a7-implementation/phase-map.json` contains key `a7-p4-import-experience` with `feature_directory` `specs/054-a7-p4-import-experience` and audit ids I02, I10, I15, I16, I17, without rewriting other phases

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The handoff gate, the error code the screen translates, and the message catalog every story uses.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Confirm `specs/052-a7-p2-import-safety/handoff.md` and `specs/053-a7-p3-import-fidelity/handoff.md` both exist and state that the integrated import baseline is ready. If either file is missing, stop. Do not create those handoffs in this feature, and do not start T003
- [x] T003 [P] In `apps/web/src/app/lib/api-client.ts`, keep `error.code` on the Error thrown by `apiFormData` when the JSON body has `error.code`. Callers that only read `message` stay unchanged
- [x] T004 [P] Add missing `scheduleImport` strings to `apps/web/src/app/locales/en.json` and `apps/web/src/app/locales/fa.json` for codes `invalid_file_type`, `file_too_large`, `mpp_corrupt`, `mpp_password_protected`, `mpp_unsupported`, `msp_invalid_xml`, `processing_timeout`, `conversion_failed`, `import_failed`, `project_archived`, `import_not_permitted`, `import_actor_missing`, `wbs_has_progress`, `wbs_has_cost`, `wbs_has_documents`, `wbs_has_activities`, `baseline_history_protected`, and `duplicate_relation`, plus the wizard title, recognized kinds `mpp`, `xml`, and `xer`, figure labels, interrupted-status text, retry-status text, and the activities link. The code strings stay language-independent. Persian and English must carry the same meaning

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Confirm a file the planner can recognize (Priority: P1) 🎯 MVP

**Goal**: The existing journey names the file and the kind the server accepted, shows the structure and the add or replace choice, and refuses to confirm a stale preview or a blocking file. Leaving before confirm does not change the project.

**Independent Test**: For one readable `.xml`, `.mpp`, and `.xer` file, walk from file choice through preview to the confirmation step without confirming. The file name, kind, mode, and structure are visible. A different file cannot reuse the previous preview. The project is unchanged after leaving.

### Tests for User Story 1

- [x] T005 [US1] Add failing preview assertions to `apps/api/core/schedule/tests/test_a7_p4_import_experience.py` for a readable `.xml` and `.xer` file, and for `.mpp` when the converter runs. `recognized_kind` is exactly `xml`, `xer`, or `mpp` for the parser that accepted the file. A rejected upload has no `recognized_kind`. Preview leaves work-package, activity, and relationship counts unchanged. Use project code `A7P4-IMPORT-EXPERIENCE` only in the pytest database

### Implementation for User Story 1

- [x] T006 [US1] Add `recognized_kind` to the preview body in `apps/api/core/schedule/services/msp_import.py` and `apps/api/core/schedule/services/p6_import.py`. Accepted values are only `mpp`, `xml`, and `xer`. A rejected upload has no `recognized_kind`. Do not add a route, wizard, or parser
- [x] T007 [US1] In `apps/web/src/app/lib/api/msp.ts` and `apps/web/src/components/wbs/msp-import-wizard.tsx`, show the file name, the translated `recognized_kind`, the preview structure, and the add and replace descriptions before confirm. Disable confirm while `blocking` has any entry. Changing the file or going back clears the preview so the previous preview cannot be confirmed. Ignore a preview response whose file name, size, and lastModified no longer match the file that was sent. Closing before confirm does not call start

**Checkpoint**: User Story 1 is testable on its own. A stale preview or a blocking file cannot be confirmed

---

## Phase 4: User Story 2 - Read a result that matches what was stored (Priority: P1)

**Goal**: Preview and the finished result show the same control figures as the saved project. A relationship that was not kept is not shown as stored. Replace shows the read-only removal projection, or the refusal, before confirm.

**Independent Test**: Confirm one authored file with a known hand count, including one duplicate and one omitted relationship. Every displayed figure matches the saved project and the hand-counted reference. An add that stores nothing new says the plan did not change.

### Tests for User Story 2

- [x] T008 [US2] Extend `apps/api/core/schedule/tests/test_a7_p4_import_experience.py` so preview `relationships_kept` equals finished `relations_created` for the same file and mode. `created_links` is not the number compared with stored relationships. `rows_read`, created packages, created activities, `duplicate_count`, and `rows_omitted` match the preview, the finished result, and the saved rows. An add of codes that already exist reports duplicates, stores nothing new, and sets `nothing_changed` true. Replace on a project with progress, cost, a document, activities, or a locked baseline returns the existing protection code, writes nothing, and shows removed counts as zero. Replace on a project with none of those protections reports the live rows removed and the rows stored. A `duplicate_relation` is not included in `relations_created`

### Implementation for User Story 2

- [x] T009 [P] [US2] In `apps/api/core/schedule/services/import_fidelity.py`, add `rows_read` as the schedule rows in the file before omission, `relationships_kept` as the links that will be inserted, `duplicate_count` as existing codes and already stored links, and `rows_omitted` as omitted rows and links that are not duplicates. `rows_omitted` has the same meaning as `omitted_count`. `relationships_kept` is zero when every link was omitted or already stored. `duplicate_count` is zero when nothing in the file matches the project. Keep `created_links` as the resolver link list
- [x] T010 [US2] In `apps/api/core/schedule/services/msp_import.py` and `apps/api/core/schedule/services/p6_import.py`, pass already stored predecessor and successor activity-code pairs into that plan and add the replacement projection from T011 to both preview bodies. Put the new counts on the preview and on the finished job result. The finished `relationships_kept` equals `relations_created`. Do not present `created_links` as the number stored. Preview does not write and does not create a job
- [x] T011 [P] [US2] In `apps/api/core/schedule/services/import_safety.py`, add a read-only replacement projection. `replacement.blocked` is the first existing protection code, or null when replace is allowed. `replacement.wbs_nodes_removed`, `replacement.activities_removed`, and `replacement.relations_removed` are the live rows the current replace path would soft-delete, and zero when blocked. The function does not write. The start call still enforces the same gate
- [x] T012 [P] [US2] In `apps/api/core/schedule/services/shared_import.py`, when the predecessor and successor pair is already stored, add warning code `duplicate_relation` with the successor code as the row. The existing relationship stays. It is not counted in `relations_created`. Do not detect it by an English "Duplicate" substring
- [x] T013 [US2] In `apps/web/src/components/wbs/msp-import-wizard.tsx` and `apps/web/src/app/lib/api/msp.ts`, show `rows_read`, created work packages, created activities, `relationships_kept` or `relations_created`, `duplicate_count`, and `rows_omitted` on the preview and the finished result. Show removed counts only while replace is selected. While add is selected, show removed counts as zero. When `replacement.blocked` is set and replace is selected, show that code and disable confirm. From a result that stored work, link to the existing project work-breakdown route and the existing project activities route in `apps/web/src/app/routeVars.ts`. An unchanged plan says the plan did not change

**Checkpoint**: User Stories 1 and 2 both hold. The stored-relationship figure equals the relationships kept

---

## Phase 5: User Story 3 - Recover in the active language (Priority: P1)

**Goal**: Warnings look different from blocking failures. File, permission, archive, duplicate, and save failures use the active language and offer a next step. The planner does not see an internal code or an exception string.

**Independent Test**: In Persian and in English, produce one warning, one blocking preview, one refused replacement, and one rejected file. The message, the visual distinction, and the next step match. The project is unchanged after each rejection or refusal.

### Tests for User Story 3

- [x] T014 [US3] Extend `apps/api/core/schedule/tests/test_a7_p4_import_experience.py` so an oversized P6 file returns `file_too_large` and a wrong-kind P6 file returns `invalid_file_type`, both as `{error: {code, message}}`. Assert `apps/web/src/app/locales/en.json` and `apps/web/src/app/locales/fa.json` each contain every code listed in T004, and that the code keys are identical in both files

### Implementation for User Story 3

- [x] T015 [US3] In `apps/api/core/schedule/views.py`, make P6 preview and start use the same `{error: {code, message}}` envelope as MSP. Known validator results use `invalid_file_type` and `file_too_large` rather than a generic validation code
- [x] T016 [US3] In `apps/web/src/components/wbs/msp-import-wizard.tsx`, translate `error.code` and each warning or blocking `code` through `scheduleImport.codes` in the active language. A known code never falls back to the server sentence or the code string. An unknown code uses one generic localized sentence, not the exception text. Move the hardcoded Persian title, extension toast, and status-poll failure string into the catalog from T004. Keep warnings visually distinct from blocking and fatal failures. After a rejection or refusal that left the project unchanged, offer choose-another-file and back. A refused replacement stays on the preview step

**Checkpoint**: User Stories 1 through 3 hold. A raw code or exception text is not the message the planner reads

---

## Phase 6: User Story 4 - One attempt stays one attempt (Priority: P2)

**Goal**: A second click, file choice, or drop does not start another attempt or swap the file. Closing the screen or switching project or account does not invent success or cancellation. A lost connection resumes the same attempt.

**Independent Test**: During preview and during the start of a save, click again, choose a second file, and drop a second file. Submit one file, switch project, and wait. Interrupt the connection and recover the same attempt. The stored project matches one intended attempt.

### Tests for User Story 4

- [x] T017 [US4] Extend `apps/api/core/schedule/tests/test_a7_p4_import_experience.py` so a second start for the same person, project, mode, and file bytes, while the first job is pending or running, returns the first task id and does not create a second job. Reading a finished job does not create another job

### Implementation for User Story 4

- [x] T018 [P] [US4] Add `apps/web/src/app/lib/import-attempt-session.ts` to remember `user_id`, `project_id`, `task_id`, `file_name`, `recognized_kind`, and `replace` in `sessionStorage`. Read it only when the signed-in user and the open project match. The record does not contain the file bytes, counts, wages, or contact details. Closing the dialog leaves the record in place
- [x] T019 [US4] In `apps/web/src/components/wbs/msp-import-wizard.tsx`, ignore another click, file choice, or drop while preview or start is in flight, and keep the file name of the request that started. Confirm sends that same file and the selected mode. Paint a status payload only when the user, project, and task id still match. Closing the dialog does not show success and does not say the attempt was cancelled. Reopening resumes that task. A network failure or unreachable status call shows an interrupted state for that task, not the fatal-error panel. Retry reads status for the remembered task and does not call start. HTTP 401, HTTP 403, and a failed job with `error_code` remain refusals

**Checkpoint**: User Stories 1 through 4 hold. A late result is not shown for a different file, project, or account

---

## Phase 7: User Story 5 - Complete the journey by keyboard in both directions (Priority: P2)

**Goal**: Keyboard-only success and recovery work in Persian right-to-left and English left-to-right, on a desktop screen and a phone-width screen. File names, codes, dates, and long messages stay readable. No date picker is added.

**Independent Test**: With a keyboard only, complete one success and one recoverable rejection in Persian and in English, on a desktop screen and on a phone-width screen. Read a long file name, a code, a date, and a long message in each combination.

### Implementation for User Story 5

- [x] T020 [US5] In `apps/web/src/components/wbs/msp-import-wizard.tsx`, move focus to the active step heading (`tabIndex={-1}`) when the step changes. Keep the file input, mode radios, and actions as named native controls using the catalog from T004. On a phone-width screen, use the full panel width, wrap the file name, and scroll the warning list. Do not add a date picker. Do not add date fields to `apps/web/src/components/templates/template-wbs-preview-tree.tsx`
- [x] T021 [US5] Run the browser journeys in `specs/054-a7-p4-import-experience/quickstart.md` on the disposable `A7P4-IMPORT-EXPERIENCE` project and write `specs/054-a7-p4-import-experience/evidence/browser.md`. Cover success, warning, recoverable rejection, refused replacement, interrupted status, and a prevented second file, in Persian and English, on a desktop width and a phone width, plus the keyboard-only success and recoverable rejection. Record the project id and any limit. A synchronous task call is not a separately running worker

**Checkpoint**: All five stories hold. The keyboard journeys are recorded for both languages and both widths

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Run the full validation set and record what it does and does not prove.

- [x] T022 Run the pytest command in `specs/054-a7-p4-import-experience/quickstart.md` from `apps/api/core` and write the command, result, and limits to `specs/054-a7-p4-import-experience/evidence/verification.md`. Include the phase 2 and phase 3 tests named there. Confirm no migration was added and Django stays 4.2.11. Do not modify `real-data/plan.mpp`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on T001. T002 blocks every later task
- **User Story 1 (Phase 3)**: Depends on T002, T003, and T004
- **User Story 2 (Phase 4)**: Depends on the foundational phase. T010 depends on T006, T009, and T011 because it edits the preview builders and uses the new counts and the replacement projection. T013 depends on T007 because both edit the wizard
- **User Story 3 (Phase 5)**: Depends on the foundational phase. T016 depends on T007 and T013 because it edits the wizard
- **User Story 4 (Phase 6)**: Depends on the foundational phase. T019 depends on T016 and T018
- **User Story 5 (Phase 7)**: Depends on T019. T021 depends on T020
- **Polish (Phase 8)**: Depends on T021

### User Story Dependencies

- **User Story 1 (P1)**: First increment. No dependency on later stories
- **User Story 2 (P1)**: Service tasks T009, T011, and T012 can start after the foundational phase. The wizard result display follows User Story 1
- **User Story 3 (P1)**: The P6 error envelope can start after the foundational phase. The wizard translation follows the wizard tasks in Stories 1 and 2
- **User Story 4 (P2)**: The session module can start after the foundational phase. The wizard binding follows Story 3
- **User Story 5 (P2)**: Follows the wizard tasks. The browser record is the proof for this story

### Within Each User Story

- Pytest for a story is written and fails before that story's implementation
- Preview and result fields land before the wizard renders them
- The shared wizard file is edited by one story task at a time: T007, then T013, then T016, then T019, then T020
- Story 5 has no pytest of its own. Its proof is the browser record in T021

### Parallel Opportunities

- T003 and T004 can run together after T002
- After T008, T009, T011, and T012 can run together
- T015 can run after T014 while T018 is written, because they touch different files
- T018 can run any time after T002, including beside Story 1

---

## Parallel Example: User Story 2

```bash
# After T008 fails for the missing figures, implement the three service changes together:
Task: "Add display counts in apps/api/core/schedule/services/import_fidelity.py"
Task: "Add the read-only replacement projection in apps/api/core/schedule/services/import_safety.py"
Task: "Add duplicate_relation in apps/api/core/schedule/services/shared_import.py"

# Then wire both preview families, then the wizard:
Task: "Spread the counts through apps/api/core/schedule/services/msp_import.py and p6_import.py"
Task: "Render the figures in apps/web/src/components/wbs/msp-import-wizard.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3
3. Stop and validate User Story 1 on its own

### Incremental Delivery

1. Setup and foundation
2. User Story 1: a recognizable file and a preview that cannot go stale
3. User Story 2: figures that match stored rows
4. User Story 3: translated warnings and refusals
5. User Story 4: one attempt, recovered after a lost connection
6. User Story 5: keyboard, both languages, both widths
7. Polish: the quickstart pytest command and the evidence note

### Parallel Team Strategy

1. Complete T001 through T004 together
2. After that, one person can own the wizard chain while another owns the service files
3. Do not edit `apps/web/src/components/wbs/msp-import-wizard.tsx` from two tasks at once

---

## Notes

- [P] tasks use different files and do not depend on an unfinished task
- The wizard chain is T007 → T013 → T016 → T019 → T020
- Do not check a task complete because an earlier phase already touched the same area
- Commit after each task or logical group
- Stop at any checkpoint and validate that story before continuing

## Recheck on 2026-11-12

T021 was reopened after exercising the native employer MPP on the disposable project. The wizard reports a localized failure, but the server cannot complete the successful journey: WBS insertion violates `wbs_path_key` at `005M`. The transaction rolls back. The full native MPP success criterion remains unmet; the previous checked marker overstated browser coverage. See `evidence/browser.md`. T022's final backend suite still passes independently.

## Follow-up: Root-path collision correction (user-authorized, 2026-11-12)

- [x] T023 Reproduce the cross-project soft-deleted-root collision in isolated pytest and document the exact mutable-sort-key cause in `evidence/wbs-path-root-cause.md`
- [x] T024 Remove mutable-code sorting from `WBS`, honor structural positions in the WBS move service, and validate root insertion, tombstone children, move/renumbering, and the integrated import suites
- [x] T025 Repeat the real `real-data/plan.mpp` import in the existing disposable project, verify persisted figures and unchanged source bytes, and repeat XML/MPP/XER browser journeys in both languages and widths

The T021 blocker above is now resolved. No database reset, path rebuild, or schema migration was required. The final browser matrix passed all four combinations and the genuine MPP stored nonempty work. See `evidence/wbs-path-root-cause.md` and the final correction section of `evidence/browser.md`.
