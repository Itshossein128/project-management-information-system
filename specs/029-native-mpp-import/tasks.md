# Tasks: Native Microsoft Project MPP Import

**Input**: Design documents from `/specs/029-native-mpp-import/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: **TDD requested** — for each user story, write tests first and confirm they FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

Monorepo: `apps/api/core/` (Django API), `apps/web/src/` (React SPA)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependencies, fixture layout, and settings hooks for MPP conversion

- [x] T001 Add `mpxj` (and document JRE requirement) to `apps/api/requirements.txt` and note install/`java -version` in `specs/029-native-mpp-import/quickstart.md`
- [x] T002 [P] Create fixture directory skeleton `apps/api/core/schedule/tests/fixtures/mpp/` with `README.md` listing required corpus themes (hierarchy, milestones, deps, dates/durations/progress, paired XML, rejection set)
- [x] T003 [P] Add `MPP_CONVERT_TIMEOUT_SECONDS` setting (default 60, env-overridable) in `apps/api/core/config/settings.py`
- [x] T004 [P] Add English/Persian stub locale keys for MPP import errors and wizard help in `apps/web/src/locales/en.json` and `apps/web/src/locales/fa.json` (and Django `apps/api/core/locale/fa/LC_MESSAGES/` stubs if used for API messages)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared validation, conversion service shell, error codes, and additive job field — MUST complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests first (foundation)

- [x] T005 [P] Write failing unit tests for MSP upload accepting `.mpp` with size ≤ 50 MB and rejecting wrong content in `apps/api/core/common/tests/test_validators.py`
- [x] T006 [P] Write failing unit tests for MPP→MSPDI conversion error mapping (password, corrupt, unsupported, timeout) in `apps/api/core/schedule/tests/test_mpp_convert.py`

### Implementation (foundation)

- [x] T007 Extend `validate_msp_upload` (or sibling) in `apps/api/core/common/validators.py` to allow extensions `{.xml,.mpp}`, enforce max size 50 MB, and sniff content (do not trust client MIME alone) per `specs/029-native-mpp-import/data-model.md` validation rules
- [x] T008 Add additive `error_code` on `BaseImportJob` as `CharField(max_length=64, blank=True, default='')` in `apps/api/core/schedule/models.py` and create migration under `apps/api/core/schedule/migrations/`
- [x] T009 Implement `apps/api/core/schedule/services/mpp_convert.py`: lazy JVM/MPXJ lifecycle, MPP→MSPDI bytes, wall-clock timeout from `MPP_CONVERT_TIMEOUT_SECONDS`, map failures to codes `mpp_corrupt` | `mpp_password_protected` | `mpp_unsupported` | `processing_timeout` | `conversion_failed`; **never** bypass password protection
- [x] T010 Implement MSP-family dispatch helper in `apps/api/core/schedule/services/msp_import.py` (or thin wrapper module) that routes `.xml` → `parse_msp_xml` and `.mpp` → convert then `parse_msp_xml`, returning `ParseResult`
- [x] T011 Wire foundation: run `apps/api/core/common/tests/test_validators.py` and `apps/api/core/schedule/tests/test_mpp_convert.py` until T005–T006 pass against T007–T010

**Checkpoint**: Validators + converter + `error_code` field ready; user stories can proceed

---

## Phase 3: User Story 1 — Import native MPP through existing wizard (Priority: P1) 🎯 MVP

**Goal**: Permitted user uploads `.mpp`, previews, confirms append/replace, sees progress and success summary with created WBS/activities/relations/warnings

**Independent Test**: With `edit_wbs`, upload a valid fixture `.mpp`, complete preview → import → summary; project WBS/activities match preview; no Microsoft Project required

### Tests for User Story 1 ⚠️

> **Write these tests FIRST; ensure they FAIL before implementation**

- [x] T012 [P] [US1] Contract/API test: `POST .../import/msp/preview/` accepts valid `.mpp` and returns `wbs_tree` / `activities` / `warnings` in `apps/api/core/schedule/tests/test_mpp_import.py`
- [x] T013 [P] [US1] Integration test: start MSP import with `.mpp` + poll status → `done` with `wbs_nodes_created`, `activities_created`, `relations_created`, `warnings` in `apps/api/core/schedule/tests/test_mpp_import.py`
- [x] T014 [P] [US1] Frontend unit/integration test: wizard accepts `.mpp` and routes to MSP APIs (not P6) in `apps/web/src/app/lib/api/msp.test.ts` (create if missing) and/or component test beside `apps/web/src/components/wbs/msp-import-wizard.tsx`

### Implementation for User Story 1

- [x] T015 [US1] Update MSP preview/start views in `apps/api/core/schedule/views.py` to accept `.mpp` via validated upload + dispatch helper; keep preview non-mutating; return existing preview DTO
- [x] T016 [US1] Update `run_msp_import_task` path in `apps/api/core/schedule/tasks.py` to convert MPP bytes before `execute_msp_import` when filename/content is MPP; persist `error_code` on failure
- [x] T017 [US1] Update `apps/web/src/app/lib/api/msp.ts` so `.mpp` uses MSP preview/start/status (only `.xer` → P6)
- [x] T018 [US1] Update `apps/web/src/components/wbs/msp-import-wizard.tsx`: accept `.mpp` in picker/drop; show filename; show preparing/processing while preview pending; disable duplicate submit; keep append/replace + progress/summary flow
- [x] T019 [US1] Document `.mpp` on MSP routes in `apps/api/core/schedule/ENDPOINTS.md`
- [x] T020 [US1] Confirm T012–T014 pass; manually smoke happy path per `specs/029-native-mpp-import/quickstart.md` scenario 1

**Checkpoint**: MVP — valid MPP can be previewed and imported end-to-end

---

## Phase 4: User Story 2 — MPP and MSP XML equivalence (Priority: P1)

**Goal**: Same representative schedule as `.mpp` and `.xml` yields equivalent supported WBS, activities, relationships, and warnings; hierarchy/milestones/deps preserved

**Independent Test**: Paired fixtures preview/import under same mode; no unexplained differences in supported fields; nested summaries map to WBS, leaves/milestones to activities

### Tests for User Story 2 ⚠️

> **Write these tests FIRST; ensure they FAIL before implementation**

- [x] T021 [P] [US2] Add paired MPP + MSP XML fixtures under `apps/api/core/schedule/tests/fixtures/mpp/` covering nested hierarchy, milestones, dependencies, dates, durations, progress, critical/slack when present
- [x] T022 [P] [US2] Write failing equivalence tests comparing `build_preview` / execute outcomes for paired MPP vs XML in `apps/api/core/schedule/tests/test_mpp_equivalence.py`
- [x] T023 [P] [US2] Write failing mapping assertion tests: summary→WBS, leaf/milestone→activity under parent in `apps/api/core/schedule/tests/test_mpp_equivalence.py`

### Implementation for User Story 2

- [x] T024 [US2] Adjust `apps/api/core/schedule/services/mpp_convert.py` (and dispatch) so MSPDI output preserves fields already supported by `parse_msp_xml` (UIDs, names, outline/WBS, summary flag, dates, durations, % complete, predecessors type/lag, critical/slack)
- [x] T025 [US2] Fix any mapping gaps without changing domain rules (summary→WBS / leaf→activity) in `apps/api/core/schedule/services/msp_import.py` / `shared_import.py` only if equivalence gaps are converter-side vs parser-side
- [x] T026 [US2] Confirm T022–T023 pass (SC-003) by running `apps/api/core/schedule/tests/test_mpp_equivalence.py`

**Checkpoint**: Equivalence corpus green for supported fields

---

## Phase 5: User Story 3 — Format guidance and safe rejection (Priority: P1)

**Goal**: Clear accepted-format copy; reject corrupt/renamed/password/unsupported/oversized with distinct localized codes; no partial project mutation

**Independent Test**: Bad fixtures each fail with correct `error.code` and unchanged WBS/activity counts

### Tests for User Story 3 ⚠️

> **Write these tests FIRST; ensure they FAIL before implementation**

- [x] T027 [P] [US3] API tests for rejection codes `invalid_file_type`, `mpp_corrupt`, `mpp_password_protected`, `mpp_unsupported`, `file_too_large` on preview in `apps/api/core/schedule/tests/test_mpp_import.py`
- [x] T028 [P] [US3] Assert rejected preview/import leaves zero new WBS/activities/relations/baselines in `apps/api/core/schedule/tests/test_mpp_import.py`
- [x] T029 [P] [US3] Frontend test: help/accept lists `.mpp`/`.xml`/`.xer` and no longer claims MPP unsupported in `apps/web/src/components/wbs/msp-import-wizard.tsx` (test file alongside or existing harness)

### Implementation for User Story 3

- [x] T030 [US3] Map converter/validator exceptions to API error envelope `{ error: { code, message, details } }` in `apps/api/core/schedule/views.py` per `specs/029-native-mpp-import/contracts/msp-mpp-import-api.md`
- [x] T031 [US3] Localize API messages for each error code (fa/en) via Django gettext / existing i18n in `apps/api/core/` and web locale strings
- [x] T032 [US3] Update wizard help, `accept`, and client extension check in `apps/web/src/components/wbs/msp-import-wizard.tsx`; surface fatal errors with recovery (choose another file / export XML / retry) per `contracts/msp-mpp-import-ui.md`
- [x] T033 [US3] Add rejection fixtures (corrupt, wrong-content+`.mpp` name, password-protected, oversized stub, unreadable genuine MPP) under `apps/api/core/schedule/tests/fixtures/mpp/`
- [x] T034 [US3] Confirm T027–T029 pass via `apps/api/core/schedule/tests/test_mpp_import.py` and wizard tests under `apps/web/src/components/wbs/`

**Checkpoint**: Safe rejection taxonomy + UX copy complete

---

## Phase 6: User Story 4 — Permissions, isolation, auditability (Priority: P1)

**Goal**: `edit_wbs` + membership enforced server-side; no cross-project job access; import attempts traceable via `MspImportJob` (+ `error_code`)

**Independent Test**: Deny `edit_wbs` → 403; poll other project’s job → 404/403; successful/failed MPP jobs visible only in owning project

### Tests for User Story 4 ⚠️

> **Write these tests FIRST; ensure they FAIL before implementation**

- [x] T035 [P] [US4] Permission tests: user without `edit_wbs` cannot preview or start MPP import in `apps/api/core/schedule/tests/test_mpp_import.py`
- [x] T036 [P] [US4] IDOR tests: member of project B cannot GET status for project A’s `MspImportJob` in `apps/api/core/schedule/tests/test_mpp_import.py`
- [x] T037 [P] [US4] Auditability tests: failed and successful MPP jobs persist `filename`, `status`, `error_code` (when failed), and result counts when done in `apps/api/core/schedule/tests/test_mpp_import.py`

### Implementation for User Story 4

- [x] T038 [US4] Verify/adjust `MspImportPreviewView` / `MspImportStartView` / `MspImportStatusView` permissions and `get_object_or_404(..., project_id=)` in `apps/api/core/schedule/views.py` (status response includes `error_code` when failed per API contract)
- [x] T039 [US4] Ensure job create sets `created_by`, `filename`, `replace_existing`, `file_data`; failures set `error_code` + `error_message` in `apps/api/core/schedule/views.py` and `apps/api/core/schedule/tasks.py`
- [x] T040 [US4] Confirm T035–T037 pass (SC-007) via `apps/api/core/schedule/tests/test_mpp_import.py`

**Checkpoint**: Authorization and audit trail solid for MPP

---

## Phase 7: User Story 5 — Append/replace, progress, failure atomicity (Priority: P2)

**Goal**: Append/replace match XML behavior; progress reported; timeout/failure leaves no partial structures; XML/XER regressions still pass

**Independent Test**: Append skips duplicates; replace follows current rules; forced failure/timeout → no partial WBS/activities; XML/XER tests green

### Tests for User Story 5 ⚠️

> **Write these tests FIRST; ensure they FAIL before implementation**

- [x] T041 [P] [US5] Append-mode test with overlapping WBS/activity codes for MPP in `apps/api/core/schedule/tests/test_mpp_import.py`
- [x] T042 [P] [US5] Replace-mode test for MPP matching current MSP XML replace safety rules in `apps/api/core/schedule/tests/test_mpp_import.py`
- [x] T043 [P] [US5] Atomicity/timeout tests: simulated conversion timeout or execute failure leaves no partial domain rows; subsequent import still works in `apps/api/core/schedule/tests/test_mpp_import.py` / `test_mpp_convert.py`
- [x] T044 [P] [US5] Regression: ensure existing cases in `apps/api/core/schedule/tests/test_msp_import.py` and `apps/api/core/schedule/tests/test_p6_import.py` remain green (add MPP-related guard only if a regression appears)

### Implementation for User Story 5

- [x] T045 [US5] Confirm MPP import reuses `execute_msp_import(..., replace=)` unchanged for append/replace in `apps/api/core/schedule/tasks.py` / `msp_import.py`
- [x] T046 [US5] Enforce conversion timeout cleanup so failed jobs do not block later imports; map to `processing_timeout` / `conversion_failed` in `apps/api/core/schedule/services/mpp_convert.py` and `tasks.py`
- [x] T047 [US5] Confirm T041–T044 pass (SC-004–SC-006) via `apps/api/core/schedule/tests/test_mpp_import.py`, `test_mpp_convert.py`, `test_msp_import.py`, `test_p6_import.py`

**Checkpoint**: Operational safety for replace/append and failures

---

## Phase 8: User Story 6 — Accessible bilingual wizard states (Priority: P3)

**Goal**: Keyboard + RTL/LTR usable across states; warnings visually distinct from fatals; recovery paths present

**Independent Test**: Keyboard-only happy path and fatal-error recovery in fa RTL and en LTR; warning banner ≠ error styling

### Tests for User Story 6 ⚠️

> **Write these tests FIRST; ensure they FAIL before implementation**

- [x] T048 [P] [US6] Component tests: processing state, warning vs error styling hooks, recovery actions wired in `apps/web/src/components/wbs/msp-import-wizard.tsx` (dedicated test file e.g. `msp-import-wizard.test.tsx`)
- [x] T049 [P] [US6] Locale presence tests: fa/en strings for help, errors, recovery in `apps/web/src/locales/fa.json` and `apps/web/src/locales/en.json`

### Implementation for User Story 6

- [x] T050 [US6] Polish wizard UX in `apps/web/src/components/wbs/msp-import-wizard.tsx`: distinct warning vs fatal UI; recovery CTAs; ensure primary controls are keyboard-reachable in all steps
- [x] T051 [US6] Verify RTL/LTR layout for wizard copy and controls (manual browser note or Playwright smoke if harness exists under `e2e/`)
- [x] T052 [US6] Confirm T048–T049 pass; record SC-008 evidence note in `specs/029-native-mpp-import/quickstart.md` validation log section if added

**Checkpoint**: Accessibility and bilingual UX complete

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Docs, corpus completeness, typecheck, quickstart validation

- [x] T053 [P] Update `apps/api/core/schedule/ENDPOINTS.md` and any operator notes for JRE/MPXJ deployment (link from `specs/029-native-mpp-import/quickstart.md`)
- [x] T054 [P] Complete compatibility corpus coverage checklist (≥95% supported fixtures preview OK) under `apps/api/core/schedule/tests/fixtures/mpp/`
- [x] T055 Run full focused pytest suite: `schedule/tests/test_msp_import.py`, `test_p6_import.py`, `test_mpp_*.py`, `common/tests/test_validators.py`
- [x] T056 Run `pnpm typecheck` for web changes under `apps/web/`
- [x] T057 Execute `specs/029-native-mpp-import/quickstart.md` scenario matrix and record pass/fail evidence
- [x] T058 [P] Update empty-state copy if needed in `apps/web/src/components/wbs/wbs-empty-state.tsx` so it does not imply MPP is unsupported

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup — **BLOCKS** all user stories
- **US1 (Phase 3)**: After Foundational — **MVP**
- **US2 (Phase 4)**: After Foundational; practically after US1 converter path exists (shares `mpp_convert` / dispatch)
- **US3 (Phase 5)**: After Foundational; benefits from US1 API wiring for error envelope
- **US4 (Phase 6)**: After Foundational; can parallel with US3 once preview/start exist
- **US5 (Phase 7)**: After US1 execute path; builds on append/replace + timeout
- **US6 (Phase 8)**: After US1 wizard basics; polish UX
- **Polish (Phase 9)**: After desired stories complete

### User Story Dependencies

| Story | Depends on | Independently testable? |
|-------|------------|-------------------------|
| US1 | Phase 2 | Yes — happy-path MPP import |
| US2 | Phase 2 + converter (US1 impl helpful) | Yes — paired fixtures only |
| US3 | Phase 2 + API error surface | Yes — rejection fixtures only |
| US4 | Phase 2 + MSP endpoints | Yes — permission/IDOR fixtures |
| US5 | US1 execute path | Yes — append/replace/timeout cases |
| US6 | US1 wizard | Yes — UI/locale checks |

### Within Each User Story

1. Write tests → confirm FAIL  
2. Implement → confirm PASS  
3. Checkpoint before next priority story when sequencing solo

### Parallel Opportunities

- T002–T004 (setup) in parallel  
- T005–T006 (foundation tests) in parallel  
- After Phase 2: US2/US3/US4 test-writing can proceed in parallel on different files  
- T053–T054, T058 in polish can run in parallel  

---

## Parallel Example: User Story 1

```bash
# TDD — launch failing tests together:
Task: "T012 Contract/API preview .mpp in schedule/tests/test_mpp_import.py"
Task: "T013 Integration start+status .mpp in schedule/tests/test_mpp_import.py"
Task: "T014 Frontend .mpp routes to MSP APIs"

# Then implement API then web:
Task: "T015–T016 views + tasks"
Task: "T017–T018 msp.ts + msp-import-wizard.tsx"
```

---

## Parallel Example: User Story 3

```bash
Task: "T027 Rejection code API tests"
Task: "T028 No-mutation assertions"
Task: "T029 Wizard accept/help tests"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup  
2. Complete Phase 2: Foundational (CRITICAL)  
3. Complete Phase 3: US1 (TDD)  
4. **STOP and VALIDATE** quickstart scenario 1  
5. Demo MPP upload → preview → import  

### Incremental Delivery

1. Setup + Foundational → foundation ready  
2. US1 → MVP demo  
3. US2 → equivalence trust  
4. US3 → safe rejection UX  
5. US4 → security/audit  
6. US5 → replace/append/atomicity  
7. US6 → a11y/i18n polish  
8. Phase 9 → evidence pack  

### Parallel Team Strategy

1. Team finishes Setup + Foundational together  
2. Then:  
   - Dev A: US1 → US5  
   - Dev B: US2 fixtures/equivalence  
   - Dev C: US3 + US4 tests/impl  
   - Dev D: US6 + locales  

---

## Notes

- [P] = different files, no incomplete-task dependencies  
- [USn] maps to spec user stories  
- TDD: every story’s tests must fail before its implementation tasks  
- Do not bypass MPP passwords (`setRespectPasswordProtection(false)` forbidden)  
- Do not change summary→WBS / leaf→activity rules  
- Commit after each task or logical TDD pair  
- Suggested MVP scope: **Phases 1–3 (US1) only**
