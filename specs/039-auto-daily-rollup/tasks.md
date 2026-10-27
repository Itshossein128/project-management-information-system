# Tasks: Daily Report Auto-Rollup & Activity Master Log Sync

**Input**: Design documents from `/specs/039-auto-daily-rollup/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

Organization: Tasks are grouped by phase and user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Verification of environment and developer dependencies.

- [X] T001 Verify local PostgreSQL (port 5433) and Redis (port 6379) services are active per `AGENTS.md`.
- [X] T002 Inspect existing daily report test suites and establish baseline pytest command in `apps/api/core`.

---

## Phase 2: Foundational Safety (Model & Database Schema)

**Purpose**: Database schema extensions and constraints required by user stories.

- [X] T003 [Foundational] Extend `DailyReportLabor` model in `apps/api/core/field_reports/models.py` with `contractor_ref` (`ForeignKey('projects.Stakeholder', on_delete=SET_NULL, null=True, blank=True, related_name='daily_report_labor_entries')`) and `contractor_name` (`CharField(max_length=120, blank=True, default='')`).
- [X] T004 [Foundational] Update unique constraint in `DailyReportLabor.Meta.constraints` in `apps/api/core/field_reports/models.py` to include `contractor_ref` in `unique_active_labor_row`.
- [X] T005 [Foundational] Create and apply Django migration for `DailyReportLabor` fields in `apps/api/core/field_reports/migrations/` (`0023_daily_report_labor_contractor.py`).
- [X] T006 [Foundational] Update `DailyReportLaborSerializer` in `apps/api/core/field_reports/serializers.py` to expose `contractor_ref` and `contractor_name`.

---

## Phase 3: User Story 1 - Guaranteed Date Shell Access via By-Date & Elimination of Blank Creation (Priority: P1) 🎯 MVP

**Goal**: Navigating to any date via `GET /by-date/` returns HTTP 200 OK with a valid draft shell (`is_auto_summary=True`, `status="DRAFT"`) without 404 errors, while legacy blank POST calls remain rejected with `auto_summary_only`.

**Independent Test**: Querying `GET /by-date/?date=YYYY-MM-DD` for an unrecorded date returns 200 OK with a provisioned draft report shell.

### Tests for User Story 1
- [X] T007 [US1] Update `apps/api/core/field_reports/tests/test_daily_report_by_date.py` to assert that `GET /by-date/` provisions an auto-summary shell and returns HTTP 200 OK instead of 404, respecting requested `shift`.

### Implementation for User Story 1
- [X] T008 [US1] Update `by_date` action in `apps/api/core/field_reports/daily_report_views.py` to extract `shift` (defaulting to `ReportShift.FULL`) and call `ensure_daily_report_summary(project_id, report_date, shift=shift, user=request.user)` when no report exists, returning HTTP 200 OK.
- [X] T009 [US1] Update `ensure_daily_report_summary` signature and logic in `apps/api/core/field_reports/services/daily_report_aggregation.py` to accept and persist `shift`.
- [X] T010 [US1] Verify rejection of blank creation via `POST /daily-reports/` returning HTTP 400 with `auto_summary_only` in `apps/api/core/field_reports/daily_report_views.py`.

---

## Phase 4: User Story 2 - Contractor-Keyed Labor Aggregation and Tracking (Priority: P1)

**Goal**: Aggregate labor from discipline sub-reports by `(labor_category, resolved_job_title, contractor_ref)`, ensuring distinct subcontractors employing workers under the same job title remain separate rows.

**Independent Test**: Submit sub-reports containing labor under the same job title for two distinct contractors and assert that the consolidated report contains two distinct labor rows.

### Tests for User Story 2
- [X] T011 [US2] Create or update test in `apps/api/core/field_reports/tests/test_daily_report_contractor_ref.py` verifying that labor aggregation buckets by `(labor_category, job_title, contractor_ref)` and labels unassigned contractors as `"نفر شرکت"`.

### Implementation for User Story 2
- [X] T012 [US2] Update labor bucketing logic in `apps/api/core/field_reports/services/daily_report_aggregation.py` to key buckets by `(row.labor_category, title_code_or_raw, row.contractor_ref_id)` and populate `contractor_ref` and `contractor_name`.
- [X] T013 [US2] Update query matching in `daily_report_aggregation.py` when locating existing derived labor rows to include `contractor_ref`.
- [X] T014 [US2] Update `DailyReportSummaryView.tsx` in `apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx` to display contractor name on labor rows.

---

## Phase 5: User Story 3 - Strict Read-Only Locking and Protection for Derived Collections (Priority: P1)

**Goal**: Child records on auto-summary reports cannot be directly mutated, returning 400 with `code="derived_collection_read_only"` and Persian guidance. UI redirects or locks editing grids.

**Independent Test**: POST/DELETE requests to child endpoints on an auto-summary report return 400 `derived_collection_read_only`.

### Tests for User Story 3
- [X] T015 [US3] Update `apps/api/core/field_reports/tests/test_daily_report_derived_readonly.py` to assert that direct POST and DELETE on auto-summary child collections return 400 with error code `derived_collection_read_only`.

### Implementation for User Story 3
- [X] T016 [US3] Update error code to `derived_collection_read_only` and detail message to `«این ردیف‌ها از ساب‌ریپورت‌های دیسیپلین مشتق شده‌اند؛ لطفاً از طریق ساب‌ریپورت مربوطه اقدام نمایید»` in `apps/api/core/field_reports/daily_report_views.py`.
- [X] T017 [US3] In `apps/web/src/components/daily_reports/DailyReportForm.tsx`, add an effect that checks `report.is_auto_summary` and redirects to the summary view (`/projects/:projectId/daily-reports/:reportId`), preventing direct edits.

---

## Phase 6: User Story 4 - Shiraz Excel Sheet 1 (ACTIVITY Master Log) Alignment & Real-Time Invalidation (Priority: P1)

**Goal**: Activity master log outputs all Shiraz Excel Sheet 1 columns (including `source_discipline` and `parcel`), supports multi-select filtering, and purges its cache upon report approval.

**Independent Test**: Approving a daily report immediately clears the activity log cache and reflects new activities with `source_discipline` and `parcel`.

### Tests for User Story 4
- [X] T018 [US4] Write unit/integration tests in `apps/api/core/field_reports/tests/test_activity_log_sync.py` testing serialization of `source_discipline` and `parcel`, filtering by discipline/parcel, and cache purge upon `approve_report`.

### Implementation for User Story 4
- [X] T019 [US4] Update `serialize_activity_log_row` in `apps/api/core/field_reports/services/activity_log.py` to include `source_discipline` and `parcel`.
- [X] T020 [US4] Update `activity_log_queryset` in `apps/api/core/field_reports/services/activity_log.py` to filter by `source_discipline` and `parcel` (supporting multi-value comma-separated strings).
- [X] T021 [US4] Update `ActivityLogFilterOptionsView` in `apps/api/core/field_reports/report_views.py` to return distinct `disciplines` and `parcels`.
- [X] T022 [US4] Implement version-based and pattern-based cache invalidation for activity log in `apps/api/core/field_reports/report_views.py` and `apps/api/core/field_reports/services/__init__.py` (`approve_report` and `reject_report`).
- [X] T023 [US4] Update frontend `apps/web/src/app/lib/api/reports.ts` and `apps/web/src/app/routes/project-activity-log.tsx` to include `source_discipline` and `parcel` columns and filter dropdowns.

---

## Phase 7: User Story 5 - Weather Severity Hierarchy & Manager Override Integrity (Priority: P2)

**Goal**: Automatically select the highest severity weather condition while preserving site manager manual overrides tagged with `weather_source='overridden_by_manager'`.

**Independent Test**: Submitting sub-reports with `cloudy` and `stormy` selects `stormy`. Setting `weather_override=True` retains the manager's values and sets `weather_source='overridden_by_manager'`.

### Tests for User Story 5
- [X] T024 [US5] Add test in `apps/api/core/field_reports/tests/test_daily_report_weather_hierarchy.py` verifying severity hierarchy selection (`clear < cloudy < rainy < snowy < stormy`) and `weather_source='overridden_by_manager'` persistence.

### Implementation for User Story 5
- [X] T025 [US5] Update `_pick_weather` and weather metadata in `apps/api/core/field_reports/services/daily_report_aggregation.py` to ensure `weather_source = 'overridden_by_manager'` when `weather_override` is true.
- [X] T026 [US5] Update `DailyReportSummaryView.tsx` in `apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx` to render the "بازنویسی توسط مدیر" badge when `weather_source === 'overridden_by_manager'`.

---

## Phase 8: User Story 6 - Discipline Completeness Feedback & Missing Units Alerting (Priority: P2)

**Goal**: Render green confirmation banner when all disciplines submit reports and orange alert when incomplete.

**Independent Test**: Complete report shows green banner with text «تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند».

### Implementation for User Story 6
- [X] T027 [US6] Update `apps/web/src/components/daily_reports/summary/IncompletenessBanner.tsx` to render green success banner with text `«تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند»` and testid `daily-report-complete-banner` when `completeness.state === "complete"` or `!aggregation.is_partial`.

---

## Phase 9: User Story 7 - Bilingual Jalali Timestamping and Consolidated Materials Summation (Priority: P2)

**Goal**: Expose `aggregated_at_jalali` in aggregation metadata and calculate grouped received/consumed material totals.

**Independent Test**: Summary response contains `aggregated_at_jalali` and `materials_summary.grouped_summary`.

### Tests for User Story 7
- [X] T028 [US7] Update `apps/api/core/field_reports/tests/test_receipts_only_summary.py` to assert presence of `aggregated_at_jalali` and `grouped_summary` in `materials_summary`.

### Implementation for User Story 7
- [X] T029 [US7] Add `gregorian_to_jalali_datetime` in `apps/api/core/common/jalali.py` and populate `aggregated_at_jalali` in `build_aggregation_meta` in `apps/api/core/field_reports/services/daily_report_aggregation.py`.
- [X] T030 [US7] In `DailyReportDetailSerializer.get_materials_summary` in `apps/api/core/field_reports/serializers.py`, calculate `grouped_summary` with `total_received`, `total_consumed`, and `net_quantity` grouped by material specification and unit.

---

## Phase 10: Polish & Cross-Cutting Verification

**Purpose**: Verification of entire test suite, frontend build, and clean git state.

- [X] T031 Run backend pytest suite across all field_reports tests.
- [X] T032 Run `pnpm --filter web build` to verify frontend build passes cleanly.
- [X] T033 Verify all acceptance criteria from `spec.md` and document results.

## Phase 11: Convergence

- [X] T034 [US4] Add focused frontend coverage or a typed behavior check for multi-select Activity Master Log filters, then update `apps/web/src/app/routes/project-activity-log.tsx` and `apps/web/src/app/lib/api/reports.ts` so discipline and parcel filters support multiple selections and send comma-separated values per FR-010 (partial)
- [X] T035 [US5] Align `AggregationMeta` and related daily-report frontend types in `apps/web/src/app/lib/api/daily-reports.ts` with backend values `weather_source='overridden_by_manager'` and `aggregated_at_jalali`, and verify the manager-override rendering contract per FR-013 and FR-016 (partial)
- [X] T036 [US4] Add or update a frontend contract/rendering check and update `apps/web/src/app/routes/project-activity-log.tsx` plus `apps/web/src/app/lib/api/reports.ts` so the Activity Master Log explicitly presents the serialized ACTIVITY fields required by FR-009, including day name, location detail, shift, unit, and report reference (partial)
