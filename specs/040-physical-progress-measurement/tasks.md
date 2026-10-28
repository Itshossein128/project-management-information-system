# Tasks: Physical Progress Measurement, Strict Financial Governance, and Technical Approval Workflow

**Feature**: `specs/040-physical-progress-measurement`  
**Input**: Design documents from `specs/040-physical-progress-measurement/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`)

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

---

## Phase 1: Setup & Environment

**Purpose**: Verify dependencies, environment, and schemas

- [X] T001 Verify database connection (PostgreSQL 5433) and Redis (6379) in `apps/api/core`
- [X] T002 [P] Create measurement units list endpoint in `apps/api/core/master_data/ref_views.py` and register in `apps/api/core/master_data/urls.py`

---

## Phase 2: Foundational Safety & Enum Alignment

**Purpose**: Core model enums and shared validation foundations

- [X] T003 Align `MeasurementMethod` choices to `quantity_based`, `weighted_milestones`, `evidence_based` with legacy aliases in `apps/api/core/schedule/models.py`
- [X] T004 [P] Update enum serialization and normalizers in `apps/api/core/schedule/services/measurement_service.py` to transparently map `quantity` to `quantity_based` and `evidence_percent` to `evidence_based`
- [X] T005 [P] Update frontend measurement enum types and API bindings in `apps/web/src/app/lib/api/progress.ts`

**Checkpoint**: Foundation ready; enums aligned without breaking existing tests.

---

## Phase 3: User Story 1 - Configuration & Synchronous Validation of Physical Measurement Methods (Priority: P1)

**Goal**: Configure and validate physical measurement methods (`quantity_based`, `weighted_milestones`, `evidence_based`) with unit selection, 100% milestone sum check, and synchronous blocking on unapproved activities.

### Tests for User Story 1
- [X] T006 [P] [US1] Add test for synchronous rejection (`400 measurement_not_approved`) on daily report activity rows in `apps/api/core/field_reports/tests/test_progress_validation.py`
- [X] T007 [P] [US1] Add test for measurement method approval with unit and weighted milestone 100% sum validation in `apps/api/core/schedule/tests/test_measurement_methods.py`

### Implementation for User Story 1
- [X] T008 [US1] Add synchronous validation blocking unapproved activities with `400 measurement_not_approved` («روش اندازه‌گیری این فعالیت هنوز تأیید نشده است») in `apps/api/core/field_reports/serializers.py`
- [X] T009 [US1] Add synchronous validation in sub-report activity serializers in `apps/api/core/sub_reports/serializers.py`
- [X] T010 [US1] Upgrade `MeasurementEditor.tsx` in `apps/web/src/components/progress/MeasurementEditor.tsx` with unit selector, dynamic weighted milestones table with 100% sum validation, and evidence rules textarea
- [X] T011 [US1] Integrate `MeasurementEditor` into WBS `ActivityDrawer` in `apps/web/src/components/activities/activity-drawer.tsx`

**Checkpoint**: US1 complete and verifiable independently.

---

## Phase 4: User Story 2 - Strict Financial Governance in Interim Payment Certificates (IPC) (Priority: P1)

**Goal**: Ensure Interim Payment Certificates calculate billable quantities and financial amounts strictly based on supervisor-approved progress (`approved_progress_pct`), ignoring unapproved contractor claims.

### Tests for User Story 2
- [X] T012 [P] [US2] Write unit test asserting IPC auto-population calculates `qty_current` exclusively from `approved_progress` delta and yields 0 when progress is unapproved in `apps/api/core/contracts/tests/test_ipc_service.py`

### Implementation for User Story 2
- [X] T013 [US2] Update `auto_populate_ipc` in `apps/api/core/contracts/services/ipc_service.py` to derive `qty_current` and `amount_current` strictly from `approved_progress` delta, setting 0 and logging warning when unapproved

**Checkpoint**: US2 complete; zero financial payout on unapproved claims.

---

## Phase 5: User Story 3 - Synchronous Rejection of Progress Exceeding 100% (No Clamping) (Priority: P1)

**Goal**: Synchronously reject any progress entry (manual or daily report) that causes cumulative progress to exceed 100% of approved total estimated quantity with `400 progress_exceeds_100` without clamping.

### Tests for User Story 3
- [X] T014 [P] [US3] Add unit tests for synchronous rejection of over-100% daily report rows without clamping in `apps/api/core/schedule/tests/test_progress_validation.py`

### Implementation for User Story 3
- [X] T015 [US3] Ensure exact Persian error message «مجموع پیشرفت نمی‌تواند از ۱۰۰٪ بیشتر شود؛ لطفاً مقادیر اصلاح شوند» and `progress_exceeds_100` code in `apps/api/core/schedule/services/measurement_service.py`
- [X] T016 [US3] Enforce over-100% synchronous validation in `apps/api/core/field_reports/serializers.py` (`DailyReportActivitySerializer`)
- [X] T017 [US3] Enforce over-100% synchronous validation in `apps/api/core/sub_reports/serializers.py`

**Checkpoint**: US3 complete; cumulative progress over 100% is hard-rejected at entry.

---

## Phase 6: User Story 4 - Supervising Engineer Technical Approval Workflow in UI (Priority: P1)

**Goal**: Implement technical approval action and modal dialog in `ActivityProgressTable.tsx` for users with `approve_reports` permission, and reject photo-only claims.

### Tests for User Story 4
- [X] T018 [P] [US4] Add test verifying photo-only technical approval rejection (`photo_not_technical_approval`) and approved percentage recording in `apps/api/core/schedule/tests/test_measurement_methods.py`

### Implementation for User Story 4
- [X] T019 [US4] Enhance `technical_approve_progress` in `apps/api/core/schedule/services/measurement_service.py` and `apps/api/core/schedule/measurement_views.py` to support explicit approved percentage and reject `basis="photo"` with Persian message
- [X] T020 [US4] Update frontend `technicalApproveProgress` API function in `apps/web/src/app/lib/api/progress.ts` to accept report date and evidence payload
- [X] T021 [US4] Add Technical Approve button and modal dialog in `apps/web/src/components/progress/ActivityProgressTable.tsx` gated by `approve_reports` permission

**Checkpoint**: US4 complete; supervisors can technically approve progress directly from UI.

---

## Phase 7: User Story 5 - Four-Way Progress Calculation and Period Physical Quantity Reporting (Priority: P2)

**Goal**: Compute and display `period_quantity` alongside all four progress percentages in the progress breakdown API and table.

### Tests for User Story 5
- [X] T022 [P] [US5] Add test asserting `period_quantity` is returned in `get_activity_progress_breakdown` in `apps/api/core/schedule/tests/test_progress_four_way.py`

### Implementation for User Story 5
- [X] T023 [US5] Compute and return `period_quantity` in `get_activity_progress_breakdown` in `apps/api/core/schedule/services/progress_service.py`
- [X] T024 [US5] Update `ActivityProgressRow` type in `apps/web/src/app/lib/api/progress.ts` with `period_quantity: number | null`
- [X] T025 [US5] Add visible "حجم دوره" column in `apps/web/src/components/progress/ActivityProgressTable.tsx`

**Checkpoint**: US5 complete; period physical quantity visible in API and UI.

---

## Phase 8: Polish & Cross-Cutting Verification

**Purpose**: Run full validation across backend and frontend

- [X] T026 Execute Django pytest suites (`pytest --reuse-db`) for schedule, contracts, and field_reports
- [X] T027 Execute frontend build (`pnpm --filter web build`)
- [X] T028 Update task progress markers to `[X]` in `tasks.md`

## Phase 9: Convergence

- [X] T029 [US5] Implement weighted-milestone achievement input and exact weighted period/cumulative progress calculation for daily reports, sub-reports, and progress breakdowns per FR-023 / US5-AC3 (missing)
- [X] T030 [US3] Make daily-report and sub-report synchronous ceiling validation sum all applicable same-day approved and in-flight rows, excluding the row being updated, without permitting over-100% writes per FR-009 and the multiple-disciplinary-sub-reports edge case (partial)
- [X] T031 [US2] Add a structured, persisted IPC warning/provenance signal for claimed progress with zero supervisor approval and expose it to IPC inspection per FR-014 (partial)
- [X] T032 [P] [US1/US3/US5] Add canonical focused regression tests for measurement validation, four-way progress, technical approval, weighted milestones, and concurrent same-day ceiling enforcement; update the offline-sync fixture to establish an approved measurement basis per Principle VI (partial)
- [X] T033 [US2] Persist approved-progress percentage, technical approval timestamp, and technical approval record reference on IPC items so auditor inspection can trace each payable line per US2-AC3 / FR-019 (missing)
- [X] T034 [US1/US5] Normalize the approved measurement method in daily-report progress recalculation so standardized `quantity_based` versions are processed instead of being skipped by the legacy enum comparison (contradicts)

---

## Dependencies & Execution Order

- **Phase 1 (Setup)**: Pre-requisite for all phases.
- **Phase 2 (Foundational)**: Prerequisite for User Stories.
- **Phase 3 (US1)**: First MVP increment.
- **Phase 4 (US2)**: Financial governance increment.
- **Phase 5 (US3)**: Hard limit enforcement.
- **Phase 6 (US4)**: Technical approval UI/API.
- **Phase 7 (US5)**: Four-way progress & period quantity.
- **Phase 8 (Polish)**: Full cross-cutting verification.
