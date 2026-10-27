# Tasks: Daily Report Correction Lineage and Lossless Cloning

**Input**: Design documents from `specs/035-correction-lineage-cloning/`
**Prerequisites**: [plan.md](./plan.md) (required), [spec.md](./spec.md) (required for user stories), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify development environment, database services, and baseline state before feature work.

- [X] T001 Verify active PostgreSQL (port 5433) and Redis (port 6379) services and environment configuration in `apps/api/core/config/settings.py`
- [X] T002 Run schema-drift baseline check using `manage.py makemigrations --check --dry-run` in `apps/api/core`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model invariants and routing foundations required by all correction workflows.

**⚠️ CRITICAL**: Must complete before user story implementation begins.

- [X] T003 Verify field definitions and soft-delete inheritance (`ChildRowModel`, `AuditSoftDeleteModel`) across child models in `apps/api/core/field_reports/models.py`
- [X] T004 Verify canonical and alias URL routes for correction cancellation in `apps/api/core/field_reports/urls.py`

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 - Lossless Preservation of All Work Details during Correction (Priority: P1) 🎯 MVP

**Goal**: Ensure opening a correction on an approved report duplicates 100% of active child rows and their detail attributes without data loss.

**Independent Test**: Start a correction from an approved current report containing activity rows (with contractor, crew, headcounts, parcel), machinery rows, general activities, visits, and incidents; verify the new draft retains every active row and attribute.

### Tests for User Story 1

- [X] T005 [P] [US1] Add unit test in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py` verifying exact duplication of the 5 activity fields (`contractor_ref_id`, `crew_name`, `foreman_count`, `worker_count`, `parcel`), machinery summary rows, general activities, visits, and incident severities upon correction
- [X] T006 [P] [US1] Add unit test in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py` verifying that soft-deleted child rows in source reports are excluded from the cloned draft

### Implementation for User Story 1

- [X] T007 [US1] Implement complete `CHILD_CLONE_SPECS` mappings for `DailyReportActivity`, `DailyReportMachineryRow`, `DailyReportGeneralActivity`, `DailyReportVisit`, and `DailyReportIncident` in `apps/api/core/field_reports/services/correction_service.py`
- [X] T008 [US1] Update `_clone_children` in `apps/api/core/field_reports/services/correction_service.py` to ensure atomic cloning of all active child rows into the newly created draft report

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently — corrections never lose child data.

---

## Phase 4: User Story 2 - Safe and Traceable Cancellation of an Open Correction (Priority: P1)

**Goal**: Provide an authorized workflow to cancel a correction draft (version > 1), soft-deleting the draft, reinstating the predecessor approved version as current, and navigating to its view.

**Independent Test**: Open a correction on an approved report, verify the presence of the cancellation action on the draft, trigger the confirmation dialog, confirm cancellation, and verify that the draft is deleted and the preceding approved version is restored as current.

### Tests for User Story 2

- [X] T009 [P] [US2] Add backend unit tests in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py` for `cancel_correction` service verifying draft soft-deletion, restoration of source report as `is_current = True`, and setting correction status to `CANCELLED`
- [X] T010 [P] [US2] Add permission and cross-project isolation tests in `apps/api/core/field_reports/tests/test_daily_report_summary_permissions.py` ensuring viewer roles cannot cancel corrections and cross-project requests return 404/403

### Implementation for User Story 2

- [X] T011 [US2] Implement `cancel_correction` service in `apps/api/core/field_reports/services/correction_service.py` with `select_for_update` row locking, draft soft-deletion, source reactivation, and timestamp tracking
- [X] T012 [US2] Implement `DailyReportCorrectionCancelView` in `apps/api/core/field_reports/daily_report_views.py` enforcing project scope and permission checks
- [X] T013 [P] [US2] Implement `cancelCorrectionRequest` API client in `apps/web/src/app/lib/api/daily-reports.ts` targeting `/${PATHS.API_PROJECTS}/${projectId}/correction-requests/${correctionId}/cancel/`
- [X] T014 [US2] Implement cancellation UI in `apps/web/src/components/daily_reports/ApprovalStatusBar.tsx` with conditional display on draft v2+, confirmation modal, error handling, success notification, and redirection to the restored approved report
- [X] T015 [US2] Add browser E2E test in `apps/web/e2e/tests/daily-report.spec.ts` exercising opening a correction, verifying the cancel button, confirming cancellation, and validating redirect back to the approved version

**Checkpoint**: At this point, User Stories 1 AND 2 work independently — corrections can be opened without data loss and safely cancelled.

---

## Phase 5: User Story 4 - Deterministic Protection against Concurrent Corrections (Priority: P2)

**Goal**: Reject duplicate correction requests on the same lineage with HTTP 400 and `code='correction_already_open'`.

**Independent Test**: Attempt to open a second correction on an approved report while an open correction draft already exists; verify an immediate HTTP 400 rejection with `correction_already_open` and zero duplicate drafts.

### Tests for User Story 4

- [X] T016 [P] [US4] Add backend unit test in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py` asserting that attempting to open a second correction on an open lineage returns HTTP 400 with `code='correction_already_open'`

### Implementation for User Story 4

- [X] T017 [US4] Update `open_correction` in `apps/api/core/field_reports/services/correction_service.py` to return `ValidationError` with HTTP 400 and code `correction_already_open` when an active correction exists

**Checkpoint**: At this point, User Story 4 protects the lineage against concurrent correction requests.

---

## Phase 6: User Story 3 - Full Provenance and Clarity in Version Lineage (Priority: P2)

**Goal**: Expose enriched version history with modifier name, version-bound correction justification (v1 isolated with no reason), and localized Jalali approval timestamp.

**Independent Test**: Open the version history panel on a multi-version report lineage; verify that each version displays modifier name, version-bound reason, and Jalali approval date/time, and v1 displays no correction reason.

### Tests for User Story 3

- [X] T018 [P] [US3] Add backend unit tests in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py` verifying that version history exposes `modifier_name`, result-bound `correction_reason`, and `approved_at`, while version 1 retains a null reason

### Implementation for User Story 3

- [X] T019 [US3] Update `list_versions` in `apps/api/core/field_reports/services/correction_service.py` to prefetch modifier and correction result relations in bounded queries
- [X] T020 [US3] Update `DailyReportVersionSerializer` in `apps/api/core/field_reports/serializers.py` to serialize `modifier_name`, result-bound `correction_reason`, and `approved_at`
- [X] T021 [P] [US3] Update TypeScript interfaces in `apps/web/src/app/lib/api/daily-reports.ts` for `DailyReportVersion`
- [X] T022 [US3] Update version history list in `apps/web/src/components/daily_reports/ApprovalStatusBar.tsx` to render modifier name, justification reason (or "ثبت اولیه"), status badges, and Jalali formatted approval timestamps
- [X] T023 [US3] Add browser E2E assertions in `apps/web/e2e/tests/daily-report.spec.ts` verifying version history UI, modifier name, reason, and Jalali date rendering

**Checkpoint**: All 4 user stories are now complete, providing lossless cloning, safe cancellation, concurrency protection, and rich audit lineage.

---

## Phase 7: Polish & Cross-Cutting Verification

**Purpose**: Execute end-to-end verification, static analysis, accessibility review, and knowledge graph updates.

- [X] T024 Run schema-drift check `apps/api/core/manage.py makemigrations --check --dry-run` to ensure zero database schema changes
- [X] T025 Run the full backend correction and permission test suite in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py` and `apps/api/core/field_reports/tests/test_daily_report_summary_permissions.py`
- [X] T026 Run Playwright E2E browser lifecycle suite (`apps/web/e2e/tests/daily-report.spec.ts -g "daily report lifecycle"`)
- [X] T027 Run static typecheck `pnpm typecheck` and verify zero TypeScript compiler errors
- [X] T028 Run `git diff --check` and verify zero whitespace, formatting, or newline anomalies
- [X] T029 Execute bilingual and accessibility pass verifying RTL layouts, Jalali date formatting, keyboard focusability, and permission-denied views
- [X] T030 Run `graphify update .` to update the AST knowledge graph

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately — verifies database and baseline.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories.
- **User Stories (Phase 3+)**: Depend on Foundational phase completion.
  - Phase 3 (US1 - Lossless Cloning) delivers the MVP foundation for safe corrections.
  - Phase 4 (US2 - Correction Cancellation) enables exit and rollback of correction drafts.
  - Phase 5 (US4 - Concurrency Protection) secures lineages against dual-draft races.
  - Phase 6 (US3 - Version Lineage) enriches historical transparency across all versions.
- **Polish (Phase 7)**: Depends on all user stories completing.

### Parallel Opportunities

- T005 and T006 can run in parallel (unit test cases in `test_daily_report_gaps_correction.py`).
- T009 and T010 can run in parallel (tests in different test files).
- T013 (frontend API client) can run in parallel with T011/T012 (backend service/view).
- T018 and T021 can run in parallel (backend test and frontend TypeScript types).
- T024, T025, T026, T027, T028 can be run in sequence or parallel validation.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Complete Phase 3 (User Story 1 - Lossless Cloning).
3. **VALIDATE**: Run `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py` to prove that no child data is lost on clone.

### Incremental Delivery

1. Foundation ready (Phases 1 & 2).
2. Add US1 → Child rows preserved losslessly upon correction (MVP!).
3. Add US2 → Editors can safely cancel an unneeded correction draft and restore approved report.
4. Add US4 → Concurrent correction requests are deterministically rejected with 400.
5. Add US3 → Version history panel provides full human context, justifications, and Jalali dates.
6. Phase 7 Polish → Full regression suite, E2E browser tests, typecheck, and graph update.

---

## Phase 8: Convergence

- [X] T031 CRITICAL: Make `CHILD_CLONE_SPECS` in `apps/api/core/field_reports/services/correction_service.py` preserve every persisted domain attribute for all registered child models—including derived/provenance markers, labor completeness, material reconciliation metadata, concrete detail/QC fields, labor-camp contractor, and incident order/notification—and add fieldwise regression coverage that fails when model fields drift from the clone registry, while continuing to exclude soft-deleted rows and handle empty collections per Constitution II / FR-002 / SC-001 / US1 (partial)
- [X] T032 CRITICAL: Localize every correction, cancellation, toast, status, and version-history string in `apps/web/src/components/daily_reports/ApprovalStatusBar.tsx` through the Persian and English catalogs, and make approval timestamps use Jalali/Persian formatting only for Persian while using Gregorian/English formatting for English, with two-locale UI coverage per Constitution III / plan: bilingual and locale-correct experience (contradicts)
- [X] T033 CRITICAL: Harden correction initiation and cancellation isolation so a correction ID from another project resolves to 403/404 even for a caller who has `edit_reports` in the URL project, then add endpoint tests for viewer/non-member initiation, dual-project IDOR attempts, both cancellation routes, and zero report/correction mutation after every denial per Constitution I and VI / FR-012 / SC-005 / T010 (partial)
- [X] T034 Replace the inline cancellation confirmation panel in `apps/web/src/components/daily_reports/ApprovalStatusBar.tsx` with the shared accessible dialog, including an announced title/description, initial focus, trapped keyboard navigation, Escape dismissal, focus restoration, and keyboard browser assertions per FR-006 / plan: accessible confirmation dialog (partial)
- [X] T035 Add a PostgreSQL transactional concurrency test that starts two simultaneous correction requests for the same approved lineage and proves exactly one succeeds, the other returns HTTP 400 with `correction_already_open`, and exactly one current draft/correction request exists per FR-004 / SC-002 / US4/AC1 (partial)
- [X] T036 Extend `apps/web/e2e/tests/daily-report.spec.ts` through an approved correction cycle so version history proves the v2 modifier, version-bound reason, localized Jalali timestamp, status/current/locked presentation, read-only historical navigation, cancellation success notification, and hidden cancellation controls for initial, approved, and read-only viewers per Constitution VI / FR-009–FR-011 / SC-004 / T023 (partial)
- [X] T037 Render accessible visual status badges in the version list and show the localized `«ثبت اولیه / Initial submission»` label for version 1 while retaining a graceful unknown-modifier placeholder in `apps/web/src/components/daily_reports/ApprovalStatusBar.tsx` per FR-009 / US3/AC2 / T022 (partial)
- [X] T038 Make cancellation retry-safe after an ambiguous network outcome by providing idempotent server reconciliation for an already-cancelled request and updating the client to recover the restored source report instead of reporting a false failure, with tests for response loss/retry and no duplicate mutation per network-drop edge case / FR-007 (contradicts)
- [X] T039 Add repeatable query-count and timing evidence for correction cloning/cancellation under 500 ms, version-history retrieval under 200 ms, and the browser cancellation-to-restored-view flow under 2 seconds, documenting the test environment and avoiding flaky wall-clock-only assertions per SC-003 / plan: performance goals (missing)
