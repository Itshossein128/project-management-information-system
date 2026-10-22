# Feature Specification: Automated Project Daily Report Summary

**Feature Branch**: `028-auto-daily-report-summary`

**Created**: 2026-10-18

**Status**: Draft

**Input**: User description: "گزارش روزانه باید جمع‌بندی گزارش روزانه‌ی واحدهای تخصصی باشد. این جمع‌بندی باید به صورت خودکار انجام شود. پس در صفحه‌ی گزارش روزانه، دکمه‌ی گزارش جدید نباید وجود داشته باشد. گزارش روزانه باید مثل فایل xlsxی که فرستادم باشد."

**Reference artifact**: Excel workbook «گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز» (one sheet per calendar day; layout described under Key Entities / Assumptions).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View auto-aggregated daily report for a date (Priority: P1)

A project manager or authorized viewer opens the project daily-report area, picks or opens a calendar date, and sees a single project-level daily report that consolidates that day’s specialty-unit (رشته / واحد تخصصی) daily reports into one summary, structured like the reference Excel daily sheet—not a blank form they fill from scratch.

**Why this priority**: This is the core product change: project daily report becomes a derived summary, not a separately authored document.

**Independent Test**: With at least one submitted specialty-unit report for a date, open that date’s project daily report and verify the summary sections are populated from those specialty reports without creating a new report manually.

**Acceptance Scenarios**:

1. **Given** specialty-unit daily reports exist and are submitted for project P on date D, **When** an authorized user opens the project daily report for D, **Then** they see one aggregated project daily report for D whose content reflects those specialty reports.
2. **Given** the user is on the project daily-report list/page, **When** they look for a way to create a brand-new daily report, **Then** no “گزارش جدید” / “New report” (or equivalent create) control is shown.
3. **Given** specialty reports for date D later change (edit/resubmit), **When** the user reopens or refreshes the project daily report for D, **Then** the summary reflects the updated specialty data without requiring a separate manual rebuild step.

---

### User Story 2 - Browse daily reports by date like the Excel workbook (Priority: P1)

A user browses project daily reports as a sequence of days (analogous to Excel sheets named by date). Each day shows the same sectional layout as the reference workbook: header, work hours/shifts, site status, weather, indirect and direct labor, incoming materials, concrete poured, executed site activities, general site activities, issues/notes, visits, and approval/management areas as applicable.

**Why this priority**: The user explicitly requires the project daily report to match the attached xlsx layout and day-based organization.

**Independent Test**: Open several dates and compare visible sections and fields to the reference Excel day sheet; confirm day-level browsing works without a create-new flow.

**Acceptance Scenarios**:

1. **Given** multiple dates have specialty data (or historical aggregated reports), **When** the user opens the daily-report area, **Then** they can navigate/list by date and open each day’s summary.
2. **Given** a day’s aggregated report is open, **When** the user reviews the screen, **Then** the main sections match the reference template (see Key Entities) sufficiently that a field supervisor recognizes it as the same daily report form.
3. **Given** a date has no specialty-unit reports yet, **When** the user looks at that date, **Then** the system does not invent a manually creatable empty report via a “new report” button; instead it shows an empty/partial summary state or indicates that no specialty data exists for that day (per Assumptions).

---

### User Story 3 - Specialty units remain the source of truth for entry (Priority: P2)

Specialty-unit users continue to enter their own daily reports in the specialty/sub-report flows. The project daily report does not replace those entry screens; it only aggregates them.

**Why this priority**: Aggregation only works if specialty reports remain the authoring surface; clarifies boundary with existing sub-report UX.

**Independent Test**: Create/submit specialty reports for a day; confirm project daily report updates; confirm specialty entry UI still allows creating specialty reports.

**Acceptance Scenarios**:

1. **Given** a specialty-unit user needs to record work for date D, **When** they use the specialty daily-report flow, **Then** they can still create and submit their unit’s report (create controls remain there, not on the project daily-report page).
2. **Given** only some specialty units have submitted for date D, **When** the project daily report for D is viewed, **Then** available units’ data appear in the summary and missing units are clearly absent or marked incomplete rather than blocking the whole view.

---

### User Story 4 - Approvals and management notes on the summary (Priority: P3)

Authorized roles can complete summary-level actions that exist on the Excel form (e.g. supervisor confirmations, management opinion) without re-entering aggregated labor/activity rows.

**Why this priority**: The reference form includes approval and management sections that are project-level, not specialty-authored; needed for operational closure but secondary to aggregation itself.

**Independent Test**: With an aggregated report present, an authorized approver records confirmation/management note; aggregated numeric/activity rows remain derived from specialty sources.

**Acceptance Scenarios**:

1. **Given** an aggregated daily report for date D, **When** an authorized user records a summary-level confirmation or management note, **Then** that metadata is saved on the project daily report and visible on subsequent views.
2. **Given** aggregated labor/activity/material rows were derived from specialty reports, **When** a user without override permission views the report, **Then** those derived rows are not presented as free-form editable “create from scratch” fields.

---

### Edge Cases

- No specialty-unit reports for the selected date: show empty/partial summary; do not offer “create new project daily report.”
- Only a subset of specialty units submitted: aggregate what exists; indicate incompleteness.
- Specialty report withdrawn, rejected, or deleted after aggregation: summary updates (or clears affected rows) automatically on next refresh/rebuild.
- Conflicting weather/site-status values across specialty reports for the same day: apply documented reconciliation rule (see Assumptions).
- Holiday/weekend with zero activity but specialty “تعطیل” entries: still show a day summary reflecting submitted specialty content.
- Duplicate or overlapping activity rows from multiple units: include all contributed rows (union), preserving unit/contractor attribution where available.
- User with view permission but no specialty-entry permission: can view aggregated report; cannot create specialty reports.
- Export/print expectation: user can obtain a day view that matches the Excel sectional structure (export may follow in a later iteration if not in MVP—see Assumptions).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST treat the project-level daily report as an automatic summary of that project’s specialty-unit (واحد تخصصی / رشته) daily reports for the same calendar date—not as a separately authored blank daily report.
- **FR-002**: System MUST update the project daily report summary automatically when contributing specialty-unit reports for that date are created, updated, submitted, or removed, without requiring the user to press a “create new” or “rebuild” control on the project daily-report page.
- **FR-003**: The project daily-report user interface MUST NOT offer a “گزارش جدید” / “New report” (or equivalent) control to manually create a project-level daily report.
- **FR-004**: System MUST present the project daily report in a layout equivalent to the reference Excel daily sheet, including at least these sections when data exists:
  - Header (report title, date, weekday, project name, contract number)
  - Work hours / shifts
  - Site status (active / inactive)
  - Weather conditions
  - Indirect (staff) labor by job title with present/leave counts
  - Direct labor by job title with present/leave counts
  - Incoming materials
  - Concrete poured volumes
  - Executed site activities (description, shift, contractor, headcount, location fragment/block/floor, quantity, unit, notes)
  - General site activities
  - Issues / remarks
  - Project visits
  - Confirmation / approval and management opinion areas
- **FR-005**: System MUST organize project daily reports by calendar date (one logical report per project per day), analogous to one Excel sheet per day in the reference workbook.
- **FR-006**: Users MUST continue to author day-level operational detail through specialty-unit daily report flows; the project daily-report page is for viewing the consolidated summary (plus allowed summary-level metadata per FR-009).
- **FR-007**: System MUST aggregate quantitative fields that share the same category key (e.g. same job title present/leave counts) by summing across contributing specialty reports for that date, unless a field is explicitly non-additive (e.g. narrative notes), in which case values are concatenated or listed with source attribution.
- **FR-008**: System MUST list activity and material line items contributed by specialty reports in the summary (union of rows), preserving enough attribution (e.g. contractor, location, originating unit) for a reviewer to understand the source.
- **FR-009**: Authorized users MUST be able to record project-level confirmation/approval and management opinion on the aggregated daily report without re-entering aggregated labor/activity rows.
- **FR-010**: System MUST restrict viewing and summary-level actions on project daily reports to users with the appropriate project permissions; lack of specialty-entry permission MUST NOT by itself block viewing an aggregated report they are otherwise allowed to see.
- **FR-011**: When no specialty-unit reports exist for a date, the system MUST NOT require or invite manual creation of an empty project daily report; it MUST show a clear empty or “no specialty data” state for that date.
- **FR-012**: System MUST make incompleteness visible when expected specialty units have not yet submitted for the day (e.g. missing-unit indicator or partial-summary banner).

### Key Entities *(include if feature involves data)*

- **Specialty-unit daily report**: Day-scoped report authored by a specialty unit (e.g. ابنیه، برق، مکانیک، and other project units as configured). Source of operational rows (labor, activities, materials, etc.).
- **Project daily report (summary)**: Day-scoped project-level consolidation derived from specialty-unit daily reports for that date. Not manually “created” as a blank form from the project daily-report page.
- **Daily report header**: Date, weekday, project identity, contract reference, shift hours, site status, weather.
- **Labor summary line**: Job title with present and leave person-day counts; split into indirect (staff) vs direct labor groups as in the reference form.
- **Material receipt line**: Description and related quantity/details of materials received that day.
- **Concrete pour line**: Concrete type/grade and volume poured.
- **Executed activity line**: Work performed including shift, contractor, headcount, location (piece/block/floor), quantity, unit, notes.
- **General activity line**: Non-production/general site work with location, volume, unit, notes.
- **Issue / visit / approval record**: Narrative issues, visit descriptions, and confirmation/management opinion at project-summary level.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In usability checks, 100% of testers can open a day’s project daily report and identify it as the consolidated view of specialty reports without using any “create new project daily report” control.
- **SC-002**: After specialty reports for a date are submitted, the project daily summary for that date is available without an extra manual create step (observable on first open/refresh of that date’s summary).
- **SC-003**: Side-by-side review against the reference Excel day sheet: at least 90% of the named sections in FR-004 are present and correctly labeled on the project daily report view.
- **SC-004**: When two specialty units each report the same job-title present count for a day, the summary shows the correct summed total in spot checks (sample of ≥5 aggregation cases pass).
- **SC-005**: Removing the project-level “new report” control does not prevent specialty-unit users from completing their own daily entry flows (specialty create/submit still succeeds in test scenarios).
- **SC-006**: Authorized approvers can complete summary-level confirmation or management opinion in under 2 minutes once the aggregated report is open.
- **SC-007**: For a date with zero specialty submissions, users never reach a blank “create project daily report” form via a new-report button; they see an empty/no-data state instead.

## Assumptions

- “واحدهای تخصصی” maps to the product’s specialty/discipline daily reports (existing sub-report / رشته flows and related department daily entry), which remain the authoring surface.
- One project daily summary exists logically per project per calendar date; dates use the project’s operational calendar (Jalali presentation where the product already does).
- Aggregation includes submitted (and, if the product already shows drafts in specialty views, optionally draft) specialty reports per the product’s existing status model; default for MVP: include reports in statuses that are considered “available for project visibility” (typically submitted and above). If drafts are excluded, that is acceptable for MVP.
- Weather and site status: if multiple specialty reports disagree, prefer an explicit project-level override if set; otherwise use a deterministic precedence (e.g. most severe weather flag wins; site inactive if any unit marks inactive)—document in implementation notes during planning.
- Labor job-title lists in the Excel are a fixed catalog for that project’s operations; MVP aggregates by matching title/category keys already used in specialty reports rather than inventing a new catalog UI.
- Summary-level approvals and management opinion are editable on the project daily report; derived tables (labor totals, activity rows from specialties) are read-only in the summary view for MVP.
- Pixel-perfect Excel cloning (merged cells, print grid) is not required; sectional and field parity with the reference workbook is required for recognition and daily use.
- File export to `.xlsx` matching the reference workbook is desirable and may be a follow-up if not included in the first delivery; on-screen parity is in scope for this feature.
- Existing manual project daily-report create/edit paths are retired or redirected so they cannot bypass aggregation (no parallel blank create from the daily-report page).
- Reference workbook path used for analysis: user-provided Excel for پروژه ۲۰۰۰ واحدی کمیل‌آباد شیراز (day sheets with labor, materials, concrete, activities, general activities, issues, visits, approvals).
