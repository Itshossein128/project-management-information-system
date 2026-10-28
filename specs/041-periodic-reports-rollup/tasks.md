# Tasks: Automated Periodic Reports Rollup, Figure Provenance, and Controlled Override Audit

**Input**: Design documents from `specs/041-periodic-reports-rollup/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`  

**Organization**: Tasks are grouped by foundational phase and user stories (US1 through US6) to enable sequential or parallel execution with strict TDD verification.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story identifier (US1..US6)
- File paths are explicitly specified for every task.

---

## Phase 1: Setup & Data Modeling (Shared Infrastructure)

**Purpose**: Database models, migrations, and basic serialization for periodic reports and figure provenance.

- [X] T001 Update `ProjectPeriodReport` and `PeriodReportFigure` models in `apps/api/core/schedule/models.py` with `status` (choices including `approved`), `serial_number`, `warnings` list, `approved_by`, `approved_at`, `calculated_value`, `is_overridden`, and `unit_of_measure`.
- [X] T002 Add `PeriodReportFigureSourceItem` model in `apps/api/core/schedule/models.py` linking to `PeriodReportFigure` with foreign keys to `DailyReport`, `DailyReportLabor`, `DailyReportEquipment`, `DailyReportMaterial`, `DailyReportActivity`, `DailyReportIncident` using `on_delete=models.PROTECT`.
- [X] T003 Generate and execute Django schema migration for `schedule` models in `apps/api/core/schedule/migrations/` using `manage.py makemigrations` and `manage.py migrate`.
- [X] T004 [P] Update figure and report serializers in `apps/api/core/schedule/period_report_views.py` to include `warnings`, `serial_number`, `approved_at`, `approved_by`, `calculated_value`, `is_overridden`, and `unit_of_measure`.

---

## Phase 2: Foundational Safety & Test Harness

**Purpose**: Shared permission boundaries and test fixtures.

- [X] T005 Update permission handling in `apps/api/core/schedule/period_report_views.py` ensuring figure override checks for `edit_reports` or `approve_reports` permissions.
- [X] T006 Establish baseline test fixtures with approved and draft daily reports in `apps/api/core/schedule/tests/test_period_reports.py`.

---

## Phase 3: User Story 1 - Automated Weekly Site Report Generation from Approved Daily Records (Priority: P1)

**Goal**: Automatically compute 5 mandatory sections (completed activities, critical delays, labor & machinery hours, materials delivered & consumed, lookahead plan) from approved daily reports.

**Independent Test**: Generate weekly report with approved daily reports, verify all 5 sections populated directly from daily child records.

- [X] T007 [US1] Write test in `apps/api/core/schedule/tests/test_period_reports.py` verifying that weekly generation aggregates labor man-hours, machinery operating/idle hours, material delivered/consumed quantities, and completed activities.
- [X] T008 [US1] Implement daily report labor & machinery aggregation in `apps/api/core/schedule/services/period_report_service.py` (`_labor_machinery_rollup`) grouping by contractor and trade/equipment.
- [X] T009 [US1] Implement daily report materials aggregation in `apps/api/core/schedule/services/period_report_service.py` (`_materials_rollup`) grouping by material description/ref and unit.
- [X] T010 [US1] Implement completed activities extraction in `apps/api/core/schedule/services/period_report_service.py` (`_completed_activities_rollup`) for activities finishing in the period.
- [X] T011 [US1] Wire weekly section composition in `apps/api/core/schedule/services/period_report_service.py` to return the 5 mandatory weekly sections.

---

## Phase 4: User Story 2 - Strict Daily Report Approval Gate and Header Warnings (Priority: P1)

**Goal**: Strictly exclude unapproved/draft daily reports and generate localized Persian warning messages in the report header.

**Independent Test**: Generate weekly report where 2 days are unapproved or missing; verify volumes exclude those days and header `warnings` list contains explicit Persian notices.

- [X] T012 [US2] Write tests in `apps/api/core/schedule/tests/test_period_reports.py` verifying unapproved daily reports are excluded and header warnings are emitted.
- [X] T013 [US2] Implement calendar day coverage checker and warning generator in `apps/api/core/schedule/services/period_report_service.py` appending `«گزارش روز [تاریخ شمسی] تأیید نشده است و احجام آن در این گزارش لحاظ نگردید»` and `«هیچ گزارش روزانه‌ای برای بازه انتخابی ثبت نشده است»`.
- [X] T014 [US2] Enforce daily report status filter (`status=ReportStatus.APPROVED`) on all daily queries in `period_report_service.py`.

---

## Phase 5: User Story 3 - Granular Figure Provenance Breakdown and Source Deletion Protection (Priority: P1)

**Goal**: Record itemized provenance source items (`PeriodReportFigureSourceItem`) and enforce referential deletion protection on daily source records.

**Independent Test**: Query figure provenance endpoint, verify item breakdown with daily source records, and attempt to delete a linked daily report record to verify deletion rejection with `ProtectedError`.

- [X] T015 [US3] Write tests in `apps/api/core/schedule/tests/test_period_reports.py` verifying figure provenance breakdown endpoint and deletion protection (`ProtectedError`).
- [X] T016 [US3] Create `PeriodReportFigureSourceItem` entries during figure rollup in `apps/api/core/schedule/services/period_report_service.py` linking directly to daily records.
- [X] T017 [US3] Implement figure provenance breakdown endpoint (`GET /api/v1/projects/{project_pk}/progress-reports/figures/{figure_id}/sources/`) in `apps/api/core/schedule/period_report_views.py`.
- [X] T018 [US3] Add URL route for figure provenance breakdown in `apps/api/core/schedule/urls.py`.

---

## Phase 6: User Story 4 - Controlled Figure Override Audit Workflow and Preservation of Calculated Values (Priority: P1)

**Goal**: Enforce $\ge 10$-character justification requirement, preserve `calculated_value`, log override audit trail, and display footnote flag.

**Independent Test**: Attempt override with < 10 characters (verify HTTP 400 rejection), submit valid override (verify `calculated_value` preserved, `is_overridden=True`, audit log created).

- [X] T019 [US4] Write tests in `apps/api/core/schedule/tests/test_period_reports.py` testing reason length validation, permission checks, and `calculated_value` preservation.
- [X] T020 [US4] Update `apply_figure_override` in `apps/api/core/schedule/services/period_report_service.py` to validate reason $\ge 10$ chars (`override_reason_required`), preserve `calculated_value`, and set `is_overridden=True`.
- [X] T021 [US4] Restrict `ProgressReportFigureOverrideView` in `apps/api/core/schedule/period_report_views.py` to users holding `edit_reports` or `approve_reports`.

---

## Phase 7: User Story 5 - Comprehensive Monthly Status Report, SPI/CPI Performance Indices, and Serialized Release (Priority: P2)

**Goal**: Compile 7 monthly chapters (including daily HSE incidents, QC summaries, EVM SPI/CPI) and implement official release approval with immutable serial number.

**Independent Test**: Generate monthly report, verify HSE incident rollup, QC inspection summary, SPI/CPI calculations, and call approve endpoint to verify official serial number generation.

- [X] T022 [US5] Write tests in `apps/api/core/schedule/tests/test_period_reports.py` for monthly report comprehensive chapters (HSE rollup, QC summary, SPI/CPI) and report approval.
- [X] T023 [US5] Implement HSE incident rollup (`_hse_summary`) and QC inspection summary (`_qc_summary`) in `apps/api/core/schedule/services/period_report_service.py`.
- [X] T024 [US5] Implement EVM CPI & SPI calculation with fallback to `not_recorded` in `apps/api/core/schedule/services/period_report_service.py`.
- [X] T025 [US5] Implement official report approval endpoint (`POST /api/v1/projects/{project_pk}/progress-reports/{report_id}/approve/`) in `apps/api/core/schedule/period_report_views.py` and service `approve_period_report` generating unique official serial number (`REP-{PROJECT_CODE}-{JALALI_YEAR_MONTH}-{SEQ}`).
- [X] T026 [US5] Add approval URL route in `apps/api/core/schedule/urls.py`.

---

## Phase 8: User Story 6 - Solar Hijri (Jalali) Workweek Scheduling and Structured Presentation (Priority: P2)

**Goal**: Support Saturday–Friday workweek intervals and Jalali month bounds in frontend, render header warnings, structured tables/cards, asterisk flags with footnotes, and provenance modal.

**Independent Test**: Verify frontend builds cleanly with `pnpm --filter web build` and renders structured sections without raw JSON string dumps.

- [X] T027 [P] [US6] Add Solar Hijri Saturday–Friday workweek helpers (`getSolarHijriWorkweekBounds`) and month bounds in `apps/web/src/app/lib/jalali-utils.ts`.
- [X] T028 [P] [US6] Add API client methods in `apps/web/src/app/lib/api/progress.ts` for approving reports and fetching figure provenance sources.
- [X] T029 [US6] Update `apps/web/src/components/progress/PeriodReportsPanel.tsx` to:
  - Default to Saturday–Friday Solar Hijri workweeks.
  - Display header warning banners for unapproved/missing daily reports.
  - Render structured cards and tables for labor, machinery, materials, and activities (no raw JSON string dumps).
  - Render asterisk (*) and footnotes drawer for overridden figures.
  - Add figure provenance breakdown modal dialog.
  - Add "Approve Official Report" button for monthly reports with serial number watermark.

---

## Phase 9: Polish & Cross-Cutting Verification

**Purpose**: End-to-end integration verification across backend and frontend.

- [X] T030 Run full backend pytest test suite for `schedule/tests/test_period_reports.py` against PostgreSQL and Redis.
- [X] T031 Run frontend build (`pnpm --filter web build`) to ensure zero TypeScript/JSX errors.
- [X] T032 Update decision-tree documentation in `docs/decision-tree/` to register the new report actions (approval, figure provenance, override).

## Phase 10: Convergence

- [X] T033 [US1] [US6] Add backend validation and tests for report period boundaries: weekly reports MUST be exactly Saturday through Friday and monthly reports MUST match one Solar Hijri calendar month; reject arbitrary spans with a stable validation error and preserve the Jalali/Gregorian parsing contract (FR-001, FR-021, FR-026) (partial)
- [ ] T034 [US3] Expand provenance creation and tests so every rolled-up figure that is derived from source records, including monthly QC/progress/cost/IPC/schedule inputs, has complete source identity, date, contributed value, creator, approver, and protected foreign-key coverage; ensure the inquiry endpoint exposes all populated source types (FR-010, FR-011, FR-012, FR-013) (partial)
- [X] T035 [US4] Add domain validation and concurrency-safe override semantics: reject negative values for non-negative metrics, carry a client-observed figure version/token, and return `409 conflict` for stale concurrent overrides; add focused API/service tests while preserving calculated values and immutable audit rows (edge cases, FR-017, FR-018, FR-019) (missing)
- [X] T036 [US6] Replace all remaining report-panel and provenance/footnote `JSON.stringify` fallbacks with localized, accessible structured renderers for nested values, and add component/browser assertions for zero raw JSON dumps in Persian and English views (FR-020, FR-027, SC-008, Constitution III/VII) (partial)
- [ ] T037 [US5] Implement and test the official report output/export watermark contract so approved reports expose an immutable serial number and exact generation timestamp on every rendered/exported page, and prevent approved report regeneration from mutating the released version (FR-025, SC-007, Constitution II/IV) (missing)
- [ ] T038 [US1-US6] Update `docs/decision-tree/` with the periodic-report generation, approval, provenance, override, conflict, and locked-release branches, then run the required browser-level verification for Jalali selectors, warning banners, structured sections, provenance, override footnotes, and approved serial/timestamp presentation; record the evidence boundary (T032, Constitution III/VI/VII) (missing)
