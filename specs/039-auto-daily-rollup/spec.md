# Feature Specification: Daily Report Auto-Rollup & Activity Master Log Sync

**Feature Branch**: `039-auto-daily-rollup`  
**Created**: 2026-10-28  
**Status**: Draft  
**Input**: User description: "موتور تجمیع خودکار ساب‌ریپورت‌های دیسیپلین‌ها در گزارش روزانه جامع پروژه (Daily Report Auto-Rollup)، مدیریت شل روزانه از طریق تقویم و تاریخ (by-date)، قفل‌گذاری ردیف‌های مشتق‌شده، سلسله‌مراتب شرایط جوی، و همگام‌سازی بلادرنگ بانک جامع فعالیت‌ها (ACTIVITY Master Log بر اساس اکسل شیراز)"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Guaranteed Date Shell Access via By-Date & Elimination of Manual Report Creation (Priority: P1)

As a site engineer, project manager, or viewer, I want to access any daily report simply by selecting a date and shift on the calendar, with the system instantly provisioning a valid draft aggregated shell if one does not already exist, so that I never encounter 404 errors when inspecting project dates and no user can accidentally create detached, blank daily reports outside the discipline sub-report workflow.

**Why this priority**: Core access gate (G01). Currently, navigating to dates without pre-existing reports triggers a 404 Not Found error and requires elevated write privileges to execute an out-of-band POST request, while leaving legacy blank creation pathways open. Providing a zero-error date lookup guarantees seamless inspection for all authorized project members.

**Independent Test**: Can be tested by navigating to an unrecorded calendar date via the date endpoint and verifying that an initialized, valid draft summary shell with HTTP 200 is immediately returned, while legacy blank POST requests are rejected with a standardized error code.

**Acceptance Scenarios**:

1. **Given** an authorized user (including read-only viewers with `view_reports` access) navigating the daily reports calendar,  
   **When** they select a date and shift (e.g. `date=2026-10-22`, `shift=1`) for which no report record currently exists,  
   **Then** the system automatically generates an initialized daily report shell with `is_auto_summary=True`, status `DRAFT`, aggregates any existing discipline sub-reports, and returns HTTP 200 OK with the report payload.
2. **Given** an existing daily report for a specified date and shift,  
   **When** a user queries the by-date endpoint with matching `date` and `shift` query parameters,  
   **Then** the system returns the existing report record with HTTP 200 OK.
3. **Given** an API consumer attempting to create a legacy blank daily report via `POST /api/v1/projects/{project_pk}/daily-reports/` without discipline sub-report payload,  
   **When** the request is submitted,  
   **Then** the server rejects the operation with HTTP 400 Bad Request, returning the error code `auto_summary_only` and bilingual explanatory guidance.
4. **Given** the daily reports list view in the user interface,  
   **When** the page renders,  
   **Then** no standalone "New Daily Report" manual creation button is visible, and all report access is mediated through the date-selector interface.

---

### User Story 2 - Contractor-Keyed Labor Aggregation and Contractor Tracking (Priority: P1)

As a site HR officer or technical office manager, I want the automatic daily rollup engine to bucket and aggregate manpower by the unique combination of job title and subcontractor, so that different subcontractors employing workers under the same job title remain clearly differentiated on separate rows in the daily master report.

**Why this priority**: Data integrity and financial accuracy (G02). Currently, labor rollups merge all workers sharing a job title into a single row and drop subcontractor references, corrupting subcontractor billing, contractor timesheets, and daily headcount verification.

**Independent Test**: Can be tested by submitting sub-reports containing labor under the same job title (e.g. "Rebar Worker / آرماتوربند") from two distinct subcontractors, executing the rollup, and verifying that the resulting consolidated report contains two distinct labor rows preserving each subcontractor's name, reference ID, and headcount.

**Acceptance Scenarios**:

1. **Given** a civil sub-report with 4 rebar workers under Contractor "A" and a structural sub-report with 2 rebar workers under Contractor "B",  
   **When** the automatic daily rollup process aggregates manpower for the day,  
   **Then** the consolidated daily report labor table displays two distinct rows: one with 4 workers attributed to Contractor "A", and one with 2 workers attributed to Contractor "B".
2. **Given** multiple sub-reports with rebar workers assigned to the exact same subcontractor (same contractor reference and same standardized job title),  
   **When** the daily rollup is executed,  
   **Then** the system sums the headcount into a single bucketed row for that contractor and job title.
3. **Given** daily report labor records persisted from aggregation,  
   **When** retrieved via the API or viewed in the UI,  
   **Then** each labor row explicitly contains the contractor reference (`contractor_ref`), contractor name (`contractor_name`), labor category, standardized job title, and total present count.

---

### User Story 3 - Strict Read-Only Locking and Protection for Derived Collections (Priority: P1)

As a data integrity auditor or compliance officer, I want all child records derived from discipline sub-reports (activities, labor, materials, machinery, concrete) to be strictly immutable against direct modification in the master daily report, so that users cannot cause discrepancies between the discipline source-of-truth and the executive daily summary.

**Why this priority**: Architectural integrity (G03). Prevents drift and out-of-sync mutations. The UI currently exposes manual editing grids on auto-summaries, and the API returns non-standard error codes.

**Independent Test**: Can be tested by sending POST or DELETE requests to child endpoints of an auto-summary daily report and asserting that HTTP 400 with the exact error code `derived_collection_read_only` is returned, while the UI hides or disables row mutation controls when `is_auto_summary=True`.

**Acceptance Scenarios**:

1. **Given** a daily report marked with `is_auto_summary=True`,  
   **When** a client sends a POST request to add a row to activities, labor, materials, machinery, or concrete child endpoints,  
   **Then** the server responds with HTTP 400 Bad Request, returning error code `derived_collection_read_only` and bilingual message: «این ردیف‌ها از ساب‌ریپورت‌های دیسیپلین مشتق شده‌اند؛ لطفاً از طریق ساب‌ریپورت مربوطه اقدام نمایید» / "These rows are derived from discipline sub-reports; please manage them through the respective sub-report."
2. **Given** a daily report marked with `is_auto_summary=True`,  
   **When** a client sends a DELETE request to delete a derived row from any child endpoint,  
   **Then** the server rejects the operation with HTTP 400 Bad Request and the error code `derived_collection_read_only`.
3. **Given** a user opening the daily report editing interface (`/projects/:projectId/daily-reports/:reportId/edit`) for an auto-summary report,  
   **When** the component evaluates `is_auto_summary=True`,  
   **Then** the user is either seamlessly redirected to the structured `DailyReportSummaryView` or presented with a locked read-only grid where "Add Row" and "Delete Row" controls are completely hidden.

---

### User Story 4 - Shiraz Excel Sheet 1 (ACTIVITY Master Log) Alignment and Real-Time Invalidation (Priority: P1)

As a project controls and scheduling engineer, I want the project-wide Activity Master Log (`/projects/:projectId/activity-log`) to match the exact 12-column structure of Shiraz Excel Sheet 1 (including source discipline and site parcel/zone), with instant cache invalidation upon report approval, so that physical progress data reflects executed site activities immediately without a 5-minute stale cache delay.

**Why this priority**: Compliance with contract specifications and Shiraz Excel blueprint standards (G04). The activity master log is the primary feeder for physical progress tracking. Missing `source_discipline` and `parcel` columns, combined with a 300-second non-invalidating cache, prevents real-time site oversight.

**Independent Test**: Can be tested by approving a daily report containing activities with source discipline and parcel information, immediately querying `/activity-log/`, and verifying that the new activities appear with correct `source_discipline` and `parcel` values without waiting for cache expiration, and that multi-select filtering by discipline and parcel returns accurate subsets.

**Acceptance Scenarios**:

1. **Given** executed activities aggregated from discipline sub-reports with designated `source_discipline` and `parcel` fields,  
   **When** the serialized activity log row is generated,  
   **Then** the output payload includes: row ID, report ID, Jalali report date, day name, activity description, work shift, subcontractor name, headcount, parcel (`parcel`), block, floor, location detail, executed quantity, unit of measurement, source discipline (`source_discipline`), and report view reference.
2. **Given** an engineer inspecting the Activity Master Log view (`/projects/:projectId/activity-log`),  
   **When** the table is displayed,  
   **Then** dedicated columns for "دیسیپلین" (Source Discipline) and "قطعه" (Parcel) are rendered alongside activity description, location, subcontractor, and quantity.
3. **Given** an engineer seeking specific activities in the Activity Master Log,  
   **When** they apply filters by discipline (e.g. `source_discipline=CIVIL`) and/or parcel (e.g. `parcel=قطعه 10`),  
   **Then** the returned activity log dataset and UI table accurately filter records matching both criteria.
4. **Given** a cached Activity Master Log response for a project,  
   **When** a project supervisor approves a daily report (`POST .../approve_report/`),  
   **Then** the system immediately purges all cached activity log keys for that project, ensuring subsequent reads reflect newly approved activities in real time.

---

### User Story 5 - Weather Severity Hierarchy & Manager Override Integrity (Priority: P2)

As a resident site engineer or project manager, I want the daily rollup to select the most severe weather condition among submitted discipline reports while preserving any manual weather or temperature override I designate, tagged with an explicit audit source, so that official site weather records reflect peak adverse conditions without overwriting deliberate managerial adjustments.

**Why this priority**: Contractual dispute mitigation and weather record integrity (G06). Extreme weather triggers contractual delays. The rollup must automatically detect adverse weather while honoring verified site manager overrides tagged with `'overridden_by_manager'`.

**Independent Test**: Can be tested by aggregating sub-reports with differing weather conditions (`cloudy` vs. `rainy`) to confirm `rainy` is selected, then applying a manager override with `weather_override=True`, triggering a subsequent rollup, and asserting that the manager's value is retained with `weather_source='overridden_by_manager'`.

**Acceptance Scenarios**:

1. **Given** multiple discipline sub-reports for the same date with varying weather conditions (e.g. Civil reports `cloudy` and Electrical reports `stormy`),  
   **When** the daily rollup service executes,  
   **Then** the system adopts the condition with the highest severity based on the strict hierarchy `clear < cloudy < rainy < snowy < stormy` (selecting `stormy`).
2. **Given** a daily report where the site manager has manually specified the weather condition and temperature (`weather_override=True`),  
   **When** a new discipline sub-report is submitted or an automated rollup is re-triggered,  
   **Then** the rollup does not replace the manager's values, persists metadata `weather_source='overridden_by_manager'`, and displays a distinct "بازنویسی توسط مدیر" (Overridden by Manager) indicator badge in the user interface.

---

### User Story 6 - Discipline Completeness Feedback & Missing Units Alerting (Priority: P2)

As a technical office coordinator, I want clear visual banners indicating whether all active project disciplines have submitted their sub-reports for the day, including a prominent green confirmation banner once all units have submitted, so that I have immediate situational awareness of reporting completeness before finalizing executive summaries.

**Why this priority**: Operational clarity (G05). While an orange banner displays missing disciplines, when all units complete submission, the UI currently returns `null`, leaving users in doubt whether data is fully aggregated or silent errors occurred.

**Independent Test**: Can be tested by viewing an incomplete daily summary to verify the orange missing disciplines warning, then submitting the final required discipline sub-report, refreshing the view, and confirming the display of a green success confirmation banner stating «تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند».

**Acceptance Scenarios**:

1. **Given** a project with active disciplines `[CIVIL, ELECTRICAL, MECHANICAL]` where only `CIVIL` has submitted a sub-report for the day,  
   **When** the daily summary report is viewed,  
   **Then** an orange warning banner is displayed listing the unsubmitted disciplines (`ELECTRICAL`, `MECHANICAL`) and alerting the user that the summary is partial.
2. **Given** a daily summary where all active disciplines have submitted their respective sub-reports (`completeness.state === "complete"` and `is_partial === False`),  
   **When** the daily summary report is viewed,  
   **Then** the orange warning banner is dismissed and a green success banner is displayed with the confirmation text: «تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند» (All discipline reports received and aggregated).

---

### User Story 7 - Bilingual Jalali Timestamping and Consolidated Materials Summation (Priority: P2)

As a warehouse supervisor and cost accountant, I want the summary metadata to display human-readable Jalali and UTC aggregation timestamps, and the materials summary to algebraically aggregate matching incoming and consumed materials, so that material utilization and delivery totals are immediately apparent without manual tallying.

**Why this priority**: Operational efficiency and bilingual compliance (G07, Constitution Principle III). Raw ISO timestamps are difficult for field staff to read quickly, and unaggregated material rows force accountants to calculate sums manually.

**Independent Test**: Can be tested by submitting sub-reports with multiple material receipts and consumption for the same item (e.g. "سیمان تیپ ۲"), running the rollup, and verifying that `aggregated_at_jalali` is present in metadata and that the materials summary displays consolidated net received and consumed sums grouped by material.

**Acceptance Scenarios**:

1. **Given** an executed rollup operation,  
   **When** the aggregation metadata is generated,  
   **Then** it contains both the ISO timestamp `aggregated_at` and the localized, human-readable Persian timestamp `aggregated_at_jalali` (e.g. `۱۴۰۵/۰۸/۰۶ - ۱۱:۳۰`).
2. **Given** multiple discipline sub-reports recording material entries for the same material specification and unit of measurement,  
   **When** the materials summary is generated,  
   **Then** the system groups records by material identity, providing aggregated sums for total received quantities and total consumed quantities.

---

### Edge Cases

- **Zero Sub-Reports on Requested Date**: When querying `/by-date/` for a date where no discipline sub-reports exist, the system creates a valid draft shell with `is_auto_summary=True`, empty child collections, `is_partial=True`, and a completeness state listing all active disciplines as missing, returning HTTP 200 OK.
- **Concurrent Sub-Report Submissions**: When two discipline supervisors submit reports simultaneously, rollup recalculations must use database transaction locking (`select_for_update`) on the daily report shell to prevent race conditions or duplicate rows in derived collections.
- **Unknown Job Titles or Direct Labor**: When a labor record contains an unmapped or custom job title without a standard code, the bucket key falls back cleanly to `(labor_category, raw_job_title, contractor_ref)` without crashing or dropping the contractor reference.
- **Unmeasured Activities (`quantity = None` / `*`)**: In accordance with Shiraz Excel Sheet 1 conventions, when an activity was performed without measurable progress units (`مقدار = *`), the system stores `quantity=None` with `quantity_measured=False`, displaying "—" or "*" in the activity log table without breaking numeric column calculations.
- **Multiple Shifts on Same Date**: When a project operates multi-shift work (e.g. Day Shift = 1, Night Shift = 2), querying `/by-date/?date=YYYY-MM-DD&shift=2` provisions or retrieves the specific shift's shell independently of Shift 1.
- **Subcontractor Unassigned (`contractor_ref = None`)**: When direct company labor is logged without an external subcontractor reference, the system groups by `contractor_ref=None` and labels the contractor as "نفر شرکت" (Direct / Company Labor) to prevent grouping direct staff with third-party contractor crews.
- **Revocation / Rejection of Approved Daily Report**: If an approved daily report is revoked or transitioned back to draft, the activity log cache for the project is immediately purged so unapproved activities are no longer visible in the master log.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST return HTTP 200 OK with a newly initialized, valid draft daily report shell (`is_auto_summary=True`, `status="DRAFT"`) upon `GET /api/v1/projects/{project_pk}/daily-reports/by-date/?date={YYYY-MM-DD}&shift={1|2|3}` if no daily report currently exists for the requested project, date, and shift.
- **FR-002**: System MUST permit users with standard read authorization (`view_reports`) to retrieve and view the auto-generated daily report shell via the by-date endpoint without requiring report creation or edit permissions.
- **FR-003**: System MUST support the optional `shift` query parameter on `GET .../by-date/`, defaulting to `ReportShift.FULL` (or Shift 1 if multi-shift) when omitted.
- **FR-004**: System MUST reject direct creation of blank, unrolled daily reports via `POST /api/v1/projects/{project_pk}/daily-reports/` without sub-report payload, responding with HTTP 400 Bad Request and error code `auto_summary_only`.
- **FR-005**: System MUST aggregate labor records into summary buckets using the composite key `(labor_category, resolved_job_title, contractor_ref)`.
- **FR-006**: System MUST persist and expose `contractor_ref` and `contractor_name` on each `DailyReportLabor` record in the database model, serializer, and UI presentation, ensuring headcounts from different contractors are never merged into a single row.
- **FR-007**: System MUST lock all derived child collections (activities, labor, materials, machinery, concrete) of daily reports having `is_auto_summary=True` against direct creation or deletion through child endpoints, returning HTTP 400 Bad Request with error code `derived_collection_read_only` and bilingual message: «این ردیف‌ها از ساب‌ریپورت‌های دیسیپلین مشتق شده‌اند؛ لطفاً از طریق ساب‌ریپورت مربوطه اقدام نمایید».
- **FR-008**: Frontend UI MUST prevent manual row modification on auto-summary reports (`is_auto_summary=True`) within `DailyReportForm.tsx` and route `/projects/:projectId/daily-reports/:reportId/edit`, redirecting to `DailyReportSummaryView` or hiding "Add Row" and "Delete Row" actions.
- **FR-009**: System MUST serialize the Project Activity Master Log (`/projects/:projectId/activity-log`) conforming to Shiraz Excel Sheet 1 (`ACTIVITY`) columns, explicitly including `source_discipline`, `parcel`, block, floor, location detail, activity description, shift, subcontractor, headcount, quantity, unit, and report view reference.
- **FR-010**: System MUST provide multi-select filtering support by `source_discipline` and `parcel` on the Activity Master Log API endpoint and within the frontend filter bar component.
- **FR-011**: System MUST invalidate and purge all cached responses for the project activity log immediately upon execution of `approve_report` on any daily report within that project.
- **FR-012**: System MUST select the most severe weather condition among submitted discipline sub-reports using the hierarchy `clear < cloudy < rainy < snowy < stormy`.
- **FR-013**: System MUST preserve site manager manual weather overrides (`weather_override=True`) across rollup recalculations, recording metadata `weather_source='overridden_by_manager'` and displaying an explanatory badge in the UI.
- **FR-014**: Frontend UI MUST render an orange alert banner (`IncompletenessBanner`) enumerating missing discipline sub-reports when reporting for active disciplines is incomplete (`is_partial=True`).
- **FR-015**: Frontend UI MUST render a green success banner with the message «تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند» (All discipline reports received and aggregated) when all active discipline sub-reports have been received and incorporated (`is_partial=False` and `completeness.state === "complete"`).
- **FR-016**: System MUST include a localized Persian date-time string `aggregated_at_jalali` in aggregation metadata alongside the UTC ISO timestamp `aggregated_at`.
- **FR-017**: System MUST group and algebraically sum received and consumed quantities of identical materials within the materials summary projection.

### Key Entities

- **DailyReport (Shell)**: Represents the project-level daily report container for a given date and shift. Key attributes: `project`, `report_date`, `shift`, `status` (`DRAFT`, `SUBMITTED`, `APPROVED`), `is_auto_summary` (boolean indicating rollup origin), `weather_override` (boolean), `weather_condition`, `temperature_min`, `temperature_max`, `aggregation_meta` (JSON containing timestamps, sources, and missing disciplines list).
- **DailyReportLabor**: Represents aggregated manpower hours and headcount. Key attributes: `daily_report`, `labor_category`, `job_title` (standardized or raw title), `contractor_ref` (FK/ID to contractor organization), `contractor_name` (denormalized name or "نفر شرکت"), `present_count` (integer headcount).
- **DailyReportActivity**: Represents an executed site activity copied from a discipline sub-report. Key attributes: `daily_report`, `source_discipline` (`CIVIL`, `ELECTRICAL`, `MECHANICAL`, etc.), `activity_description`, `shift`, `subcontractor_name`, `headcount`, `parcel`, `block`, `floor`, `location_detail`, `quantity`, `quantity_measured` (boolean), `unit`.
- **ActivityMasterLog Entry**: A flattened, project-wide read projection of approved daily report activities mirroring Shiraz Excel Sheet 1 (`ACTIVITY`). Key attributes: `report_date` (Jalali string), `day_name`, `source_discipline`, `activity_description`, `shift`, `subcontractor`, `headcount`, `parcel`, `block`, `floor`, `location`, `quantity`, `unit`, `report_id`.
- **DisciplineCompleteness**: Status object tracking the reporting readiness of active project disciplines. Key attributes: `active_disciplines` (list), `submitted_disciplines` (list), `missing_disciplines` (list), `state` (`empty`, `partial`, `complete`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of calendar date navigations to `/by-date/` successfully return a valid daily report shell within 2 seconds without ever throwing a 404 Not Found error, regardless of whether sub-reports existed beforehand.
- **SC-002**: 100% of read-only users with project view authorization can inspect the daily report shell without needing manual administrator intervention or elevated write permissions.
- **SC-003**: 100% of distinct subcontractors logging manpower under identical job titles remain separated in the daily labor report, with zero instances of unauthorized headcount flattening.
- **SC-004**: 100% of manual POST/DELETE requests targeting derived collections on auto-summary reports are rejected with error code `derived_collection_read_only`.
- **SC-005**: 100% of activities from newly approved daily reports are queryable and visible in the Activity Master Log within 1 second of approval, eliminating the previous 300-second cache delay.
- **SC-006**: The Activity Master Log UI provides full filtering and display coverage for all 12 Shiraz Excel Sheet 1 columns, specifically including source discipline and site parcel.
- **SC-007**: When all active project disciplines have submitted their daily reports, 100% of inspected views display the green confirmation banner confirming complete rollup.
- **SC-008**: 100% of manager manual weather overrides remain intact through subsequent sub-report submissions with verified `overridden_by_manager` metadata attribution.

---

## Assumptions

- **Active Discipline Discovery**: The list of expected discipline units for a project is derived from the project's enabled disciplines or active unit configurations; if none are explicitly configured, standard active disciplines (`CIVIL`, `ELECTRICAL`, `MECHANICAL`) serve as the default baseline.
- **Default Shift**: When no specific shift is requested in `/by-date/`, the system assumes `ReportShift.FULL` (all-day consolidated shift).
- **Direct Labor Representation**: When an activity or labor entry has no external subcontractor specified, it is treated as company direct labor ("نفر شرکت") and grouped distinctly from subcontracted personnel.
- **Permission Mapping**: Viewing auto-generated shells requires the existing project permission `view_reports`. Modifying manager overrides or approving reports requires `change_dailyreport` and `approve_dailyreport` respectively.
- **Bilingual Interface**: All user-facing error messages, table headers, filter placeholders, and status banners must provide bilingual support (Persian default, English fallback) in alignment with Constitution Principle III.
