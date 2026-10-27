---
description: "Actionable task list for Daily Report Lifecycle Lock"
---

# Tasks: Daily Report Lifecycle Lock

**Input**: Design documents from `/specs/034-daily-lifecycle-lock/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/daily-report-lifecycle-api.md](./contracts/daily-report-lifecycle-api.md), [contracts/daily-report-lifecycle-ui.md](./contracts/daily-report-lifecycle-ui.md), [quickstart.md](./quickstart.md)
**Tests**: Required. The specification explicitly mandates automated backend contracts, model persistence coverage, and browser lifecycle tests.
**Organization**: Tasks are grouped by user story in priority order (P1 stories: US1, US2, US4; P2 story: US3) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: User story traceability label (e.g. `[US1]`, `[US2]`, `[US4]`, `[US3]`)

---

## Phase 1: Setup (Shared Infrastructure & Baselines)

**Purpose**: Establish verification baselines and safety checks before mutating lifecycle logic.

- [X] T001 Record validation commands, prerequisites, and proof boundaries in `specs/034-daily-lifecycle-lock/quickstart.md`
- [X] T002 Verify schema stability and confirm no pending database migrations exist via `apps/api/core/manage.py makemigrations --check --dry-run`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and error envelopes required by all user stories before workflow implementation.

**⚠️ CRITICAL**: Must be completed before user story implementation begins.

- [X] T003 Verify and preserve application error response envelope `{error: {code, message, details}}` in `apps/api/core/config/exceptions.py`
- [X] T004 [P] Define stable lifecycle error code constants in `apps/api/core/field_reports/services/lifecycle_errors.py`

**Checkpoint**: Error handling and envelope contracts are standardized and ready for user story implementations.

---

## Phase 3: User Story 1 - Preserve an approved report during correction (Priority: P1) 🎯 MVP

**Goal**: An approved current report opens a safe next-version correction whose active child-row data is preserved, while concurrent correction attempts are deterministically refused with `400 correction_already_open`.

**Independent Test**: Create an approved current report containing active activity rows (with crew name, foreman count, worker count, parcel, contractor_ref, and source_discipline), machinery, general-activity, visit, and incident rows (with severity and provenance), plus soft-deleted rows (`is_deleted=True`). Open a correction request: confirm all active values are cloned into the successor, deleted rows are excluded, successor is current draft (version n+1), and a concurrent correction request returns HTTP 400 with `correction_already_open`.

### Tests for User Story 1

- [X] T005 [P] [US1] Add regression tests for child-row cloning, contractor_ref preservation, source_discipline preservation, incident severity/provenance, deleted-row exclusion, and HTTP 400 `correction_already_open` envelope in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py`

### Implementation for User Story 1

- [X] T006 [US1] Harden `CHILD_CLONE_SPECS` and `open_correction` in `apps/api/core/field_reports/services/correction_service.py`: lock current report via `select_for_update`, clone active semantic fields across activity, machinery, general-activity, visit, and incident rows, exclude `is_deleted=True` rows, and reject concurrent open requests with `correction_already_open` without mutating state
- [X] T007 [US1] Wire project-scoped permission checks and error response serialization for open-correction endpoint in `apps/api/core/field_reports/daily_report_views.py`

**Checkpoint**: Run US1 tests in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py`; report cloning is completely lossless and concurrent requests fail deterministically.

---

## Phase 4: User Story 2 - Cancel a correction safely (Priority: P1)

**Goal**: An authorized editor can confirm cancellation of only the current correction draft, soft-deleting the draft and restoring the approved predecessor without manual intervention.

**Independent Test**: Open a correction from an approved report; verify UI cancellation button is visible and requires confirmation; confirm cancellation; verify draft is soft-deleted, source is approved/current, user navigates to source report, and non-open cancellation attempts are rejected.

### Tests for User Story 2

- [X] T008 [P] [US2] Add unit and permission tests for cancellation guards (open status required, project match, lineage match, direct predecessor check, source restoration, result soft-deletion, and view-only denial) in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py` and `apps/api/core/field_reports/tests/test_daily_report_summary_permissions.py`
- [X] T009 [P] [US2] Add browser E2E tests for visible confirmed cancellation on correction draft (version > 1), absence on v1/normal draft, successful POST cancellation, query invalidation without 404 refetch errors, and navigation to source report in `apps/web/e2e/tests/daily-report.spec.ts`

### Implementation for User Story 2

- [X] T010 [US2] Harden `cancel_correction` in `apps/api/core/field_reports/services/correction_service.py` to lock request, result, and source, require open status, verify result belongs to same project and lineage and directly supersedes source, soft-delete result via `DailyReport.all_objects`, and restore source as current
- [X] T011 [US2] Implement `DailyReportCorrectionCancelView` in `apps/api/core/field_reports/daily_report_views.py` with project permission checks (`edit_reports`), route registration in `apps/api/core/field_reports/urls.py`, and returning the updated request with `source_report_id`
- [X] T012 [P] [US2] Add typed API helper `cancelCorrectionRequest(projectId, correctionId)` and correction-request listing in `apps/web/src/app/lib/api/daily-reports.ts`
- [X] T013 [US2] Implement confirmed cancellation modal in `apps/web/src/components/daily_reports/ApprovalStatusBar.tsx` that discovers the open request matching current draft, requests explicit confirmation, invalidates affected queries before navigation to prevent dead-resource 404, and navigates to `source_report_id`
- [X] T014 [US2] Wire cancellation props and route handling through `apps/web/src/components/daily_reports/DailyReportForm.tsx` and `apps/web/src/app/routes/daily-report-view.tsx`

**Checkpoint**: At this point, User Stories 1 and 2 are fully functional and verifiable independently.

---

## Phase 5: User Story 4 - Receive precise lifecycle validation (Priority: P1)

**Goal**: Workflow errors return stable machine codes with localized bilingual messages, submit validates measured-without-quantity with the exact Persian message, and unset quantities render as distinct badges across all activity views.

**Independent Test**: Attempt submit on non-draft report (assert `report_not_in_submittable_state`); attempt reject without reason (assert `rejection_reason_required`); attempt reject with reason < 10 chars (assert `rejection_reason_min_length_10`); attempt submit with measured activity and blank quantity (assert `quantity_unset_invalid` and Persian message); submit with quantity 0 (assert success); check activity table in edit, read-only, and summary modes to verify «ثبت‌نشده» badge and visible numeric 0.

### Tests for User Story 4

- [X] T015 [P] [US4] Add submit/reject lifecycle error contract tests in `apps/api/core/field_reports/tests/test_approval_workflow.py` for `report_not_in_submittable_state`, `rejection_reason_required`, `rejection_reason_min_length_10`, `quantity_unset_invalid` (with exact Persian message and `Accept-Language` English translation), and valid explicit zero submit
- [X] T016 [P] [US4] Add model and serializer persistence tests in `apps/api/core/field_reports/tests/test_daily_report_gaps_status_unset.py` verifying `quantity_measured=false` clears quantity, explicit 0 remains 0, and null is never coerced to zero
- [X] T017 [P] [US4] Add browser E2E test scenarios in `apps/web/e2e/tests/daily-report.spec.ts` asserting unset badge (`ثبت‌نشده` / `Not recorded`) and explicit 0 across editable grid cells, read-only grid cells, and daily-report summary view

### Implementation for User Story 4

- [X] T018 [US4] Update activity row serialization in `apps/api/core/field_reports/serializers.py` so a measured activity with null quantity is allowed during draft editing without coercion, and numeric 0 is preserved
- [X] T019 [US4] Implement submit-time and reject-time validation with localized error messages (supporting Persian and English `Accept-Language`) in `apps/api/core/field_reports/daily_report_views.py` for `report_not_in_submittable_state`, `rejection_reason_required`, `rejection_reason_min_length_10`, and `quantity_unset_invalid` (with message: «مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود»)
- [X] T020 [P] [US4] Create reusable localized badge component in `apps/web/src/components/daily_reports/UnsetQuantityBadge.tsx` with translations in `apps/web/src/app/locales/fa.json` (`ثبت‌نشده`) and `apps/web/src/app/locales/en.json` (`Not recorded`)
- [X] T021 [US4] Integrate `UnsetQuantityBadge` for null/not-measured quantities in both editable and read-only cell states in `apps/web/src/components/daily_reports/EditableGrid.tsx` and `apps/web/src/components/daily_reports/ActivityTab.tsx`, while preserving numeric zero and active editing input
- [X] T022 [P] [US4] Integrate `UnsetQuantityBadge` for activity quantities in `apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx`, replacing the plain-dash fallback

**Checkpoint**: Run US4 backend and browser scenarios; workflow errors and quantity distinctions are fully validated.

---

## Phase 6: User Story 3 - Understand version lineage (Priority: P2)

**Goal**: Version history exposes complete, correctly attributed lineage metadata (modifier name, result-bound correction reason, Jalali approval date-time, and unavailable state for root version) in one accessible panel.

**Independent Test**: Create and approve a corrected version; open version history from either version; verify modifier full name, result-bound reason on successor, unavailable indicator on root version, current/locked badges, and readable Jalali date-time for Persian locale.

### Tests for User Story 3

- [X] T023 [P] [US3] Add API contract tests for `GET /{report_pk}/versions/` in `apps/api/core/field_reports/tests/test_daily_report_gaps_correction.py` asserting ordered versions, modifier name, result-bound correction reason, root null reason, approval timestamp, and project permission checks
- [X] T024 [P] [US3] Add browser E2E assertions in `apps/web/e2e/tests/daily-report.spec.ts` for expanded version-history panel verifying modifier, correction reason, localized unavailable fallback for root/unapproved versions, and Jalali formatted approval date-time

### Implementation for User Story 3

- [X] T025 [US3] Optimize `list_versions` in `apps/api/core/field_reports/services/correction_service.py` to batch-load modifier and result-correction relations without N+1 queries
- [X] T026 [US3] Update `DailyReportVersionSerializer` in `apps/api/core/field_reports/serializers.py` to serialize `modifier_name`, `correction_reason` (result-bound only), and `approved_at`
- [X] T027 [P] [US3] Extend frontend version types in `apps/web/src/app/lib/api/daily-reports.ts` and add Jalali date-time formatting helper in `apps/web/src/app/lib/jalali-utils.ts`
- [X] T028 [US3] Render modifier, correction reason, localized unavailable fallbacks, and Jalali approval timestamp in the version history panel of `apps/web/src/components/daily_reports/ApprovalStatusBar.tsx`

**Checkpoint**: Run US3 API and browser tests; version lineage is transparent and historically accurate.

---

## Phase 7: Polish & Cross-Cutting Verification

**Purpose**: Execute end-to-end quality gates and verify compliance with constitution principles without overstating evidence boundaries.

- [X] T029 Run schema-drift check via `apps/api/core/manage.py makemigrations --check --dry-run` to ensure no unwanted migrations
- [X] T030 [P] Run focused backend pytest test suite in `apps/api/core` for `test_daily_report_gaps_correction.py`, `test_approval_workflow.py`, `test_daily_report_gaps_status_unset.py`, and `test_daily_report_summary_permissions.py`
- [X] T031 [P] Run targeted Playwright browser test suite in `apps/web/e2e/tests/daily-report.spec.ts` covering daily report lifecycle flows
- [X] T032 [P] Run static verification (`pnpm typecheck` and `git diff --check`) across the monorepo
- [X] T033 Execute manual bilingual (Persian & English) and accessibility verification per `specs/034-daily-lifecycle-lock/quickstart.md`, verifying keyboard reachability, visible focus, non-colour-only badge styling, and IDOR protection

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - establishes baselines
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **US1 (Phase 3 - P1)**: Depends on Foundational - delivers MVP data-preservation and concurrency locking
- **US2 (Phase 4 - P1)**: Depends on US1 (uses correction request lifecycle hardened by US1)
- **US4 (Phase 5 - P1)**: Depends on Foundational - can run after US2 to avoid editing shared status bar / browser suites concurrently
- **US3 (Phase 6 - P2)**: Depends on US1 & US2 - enriches version lineage after correction lifecycle is complete
- **Polish (Phase 7)**: Depends on completion of all user story phases

### User Story Dependencies

```text
Foundational (Phase 2)
  │
  ├── US1: Lossless child-row cloning & deterministic concurrency (MVP)
  │     │
  │     └── US2: Safe confirmed cancellation & predecessor restoration
  │
  ├── US4: Precise lifecycle error codes & explicit 0 vs unset semantics
  │
  └── US3: Transparent version history lineage & Jalali approval metadata
        │
        └── Polish & Cross-Cutting Verification (Phase 7)
```

---

## Parallel Opportunities

- **Setup & Foundational**: T004 can run in parallel with T003.
- **User Story 1**: T005 test definition can proceed in parallel with schema/contract validation.
- **User Story 2**: T008 (backend tests), T009 (browser tests), and T012 (API client) can be implemented in parallel.
- **User Story 4**: T015 (backend tests), T016 (model tests), T017 (browser tests), and T020 (badge component) can be worked on in parallel across backend and frontend.
- **User Story 3**: T023 (API tests), T024 (browser tests), and T027 (Jalali formatting utility) can proceed in parallel.
- **Polish**: T030 (backend suite), T031 (Playwright), and T032 (static checks) can run in parallel in separate test workers.

---

## Parallel Example: User Story 4

```bash
# Launch test creation tasks in parallel:
Task: "T015 [P] [US4] Add submit/reject lifecycle error contract tests in apps/api/core/field_reports/tests/test_approval_workflow.py"
Task: "T016 [P] [US4] Add model and serializer persistence tests in apps/api/core/field_reports/tests/test_daily_report_gaps_status_unset.py"
Task: "T017 [P] [US4] Add browser E2E test scenarios in apps/web/e2e/tests/daily-report.spec.ts"

# Frontend badge component can be built in parallel with backend serializer work:
Task: "T020 [P] [US4] Create reusable localized badge component in apps/web/src/components/daily_reports/UnsetQuantityBadge.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003, T004)
3. Complete Phase 3: User Story 1 (T005, T006, T007)
4. **STOP and VALIDATE**: Verify all child rows and metadata are preserved through correction cloning, and that duplicate correction attempts return 400 `correction_already_open`.

### Incremental Delivery

1. Foundation ready (Phases 1 & 2)
2. US1: Safe, lossless correction creation (MVP)
3. US2: Safe, confirmed cancellation flow returning to predecessor
4. US4: Stable workflow error codes and zero vs unset visual distinction
5. US3: Jalali-aware version lineage inspection
6. Polish: Full gate verification (schema, pytest, playwright, typecheck, bilingual pass)
