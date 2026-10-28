# Feature Specification: Automated Periodic Reports Rollup, Figure Provenance, and Controlled Override Audit

**Feature Branch**: `041-periodic-reports-rollup`  
**Created**: 2026-10-28  
**Status**: Draft  
**Input**: User description: "یک feature منسجم برای «تولید خودکار گزارشات دوره‌ای کارگاه (هفتگی شنبه تا جمعه و ماهانه شمسی) از تجمیع گزارش‌های روزانه تأییدشده، اعمال زنجیره ردپای داده‌ها و ارقام (Figure Provenance) با قید محافظت از حذف (Protected FK)، فرآیند ممیزی و بازنویسی کنترل‌شده ارقام (Figure Override) با الزام دلیل حداقل ۱۰ کاراکتری و حفظ مقدار اولیه، و درج شماره سریال رسمی و اخطارهای هدر»"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Weekly Site Report Generation from Approved Daily Records (Priority: P1)

As a Project Manager or Site Superintendent, I want the system to automatically generate the standard weekly site report from the approved daily reports of the preceding workweek (Saturday through Friday), so that weekly reporting requires no tedious manual consolidation, human transcription errors are eliminated, and all field metrics reflect verified site operations.

**Why this priority**: Core operational value (US-PR-04, G01). Periodic reports currently do not pull any field metrics from daily site reports. Site superintendents must manually calculate man-hours, machinery operating hours, and material quantities, resulting in inaccurate progress documents, disputed contractor claims, and hours of administrative overhead.

**Independent Test**: Can be tested by creating approved daily reports for a Saturday–Friday workweek containing labor, equipment, and material rows, generating a weekly report, and verifying that all 5 mandatory sections are automatically computed and populated directly from approved daily records.

**Acceptance Scenarios**:

1. **Given** approved daily reports for a Saturday-to-Friday workweek with labor allocations, equipment operations, and material deliveries/consumption,  
   **When** the user generates a weekly progress report for this workweek,  
   **Then** the system produces a report containing five mandatory sections:  
     1. Summary of work activities completed during the week.  
     2. Critical activities experiencing delay or schedule variance.  
     3. Aggregated table of human labor man-hours and machinery operational/idle hours grouped by contractor and trade.  
     4. Delivered and consumed material quantities grouped by material type and engineering unit.  
     5. Next workweek plan and operational priorities.
2. **Given** work activities completed during the reporting week,  
   **When** the weekly report is generated,  
   **Then** the completed activities section explicitly lists each activity completed within the period along with its actual completion date and final verified physical volume.
3. **Given** scheduled activities on the critical path that have negative schedule variance or unapproved delays,  
   **When** the weekly report is generated,  
   **Then** the critical activities section highlights each delayed critical activity with its baseline finish date, forecast finish date, and calculated delay in days.
4. **Given** multiple subcontractors logging labor and equipment across the week,  
   **When** the labor and machinery section is compiled,  
   **Then** the figures display total regular hours, overtime hours, and equipment operating hours broken down by contractor organization and trade skill.

---

### User Story 2 - Strict Daily Report Approval Gate and Header Warnings (Priority: P1)

As a Supervising Engineer or Quality Auditor, I want the periodic rollup engine to strictly exclude unapproved (draft or pending) daily site reports and visibly warn about missing or unapproved dates in the report header, so that executive and contractual reports never incorporate unverified draft data.

**Why this priority**: Essential data governance (US-PR-04, G02). Incomplete or unapproved draft reports can introduce arbitrary numbers into legal project documentation. Disclosing missing days in the header guarantees transparency and legal defensibility.

**Independent Test**: Can be tested by having 5 approved daily reports and 2 draft/missing daily reports in a weekly cycle, generating the weekly report, and verifying that the draft days' volumes are omitted from cumulative sums while an explicit Persian warning banner listing the unapproved dates appears in the report header.

**Acceptance Scenarios**:

1. **Given** a 7-day reporting cycle where one or more days remain in `draft` or `submitted` status (unapproved),  
   **When** the weekly report is generated,  
   **Then** data from unapproved daily reports are excluded from labor, equipment, material, and progress calculations.
2. **Given** unapproved or missing daily reports in the period,  
   **When** the report is generated and displayed,  
   **Then** the report header contains an explicit warning banner: «گزارش روز [تاریخ شمسی] تأیید نشده است و احجام آن در این گزارش لحاظ نگردید».
3. **Given** all days in the reporting cycle have fully approved daily reports,  
   **When** the weekly report is generated,  
   **Then** the warnings list in the report header is empty, and the report reflects complete site coverage.

---

### User Story 3 - Granular Figure Provenance Breakdown and Source Deletion Protection (Priority: P1)

As a Technical Auditor or Contracts Reviewer, I want every rolled-up number in a periodic report to provide an itemized audit trail (Figure Provenance) linking back to the exact daily source records, and I want the system database to prevent accidental or malicious deletion of those underlying source records, so that the legal and financial integrity of reported figures cannot be compromised.

**Why this priority**: Core legal defensibility and data integrity (US-PR-06, G03). Currently, report figures are stored without relation to their constituent source items, and source daily records can be deleted, leaving orphan figures and broken audit trails.

**Independent Test**: Can be tested by inspecting a weekly figure (e.g., 180 m³ concrete poured), requesting the figure provenance detail, verifying the breakdown shows the exact source days, item IDs, quantities, creators, and approvers, and subsequently attempting to delete an underlying daily report record and confirming that deletion is strictly blocked by referential integrity.

**Acceptance Scenarios**:

1. **Given** an aggregated figure in a weekly or monthly report (e.g., 180 m³ of foundation concrete),  
   **When** the user clicks or queries the figure provenance detail,  
   **Then** the system presents an itemized list of all constituent daily records, detailing for each source item:  
     - Source date in Solar Hijri (Shamsi) format  
     - Source daily report reference code  
     - Specific contributed volume / value  
     - Author/creator of the source record  
     - Supervising engineer who approved the source record.
2. **Given** a daily site report record that is linked as a provenance source item in a generated periodic report,  
   **When** any user attempts to delete that daily report or its child execution items,  
   **Then** the operation is rejected by the database with a protected referential integrity error, preventing source record deletion while a periodic report references it.
3. **Given** an attempt to directly modify a generated figure without using the authorized override workflow,  
   **When** an update request is sent to the figure record,  
   **Then** the system rejects the modification with error `figure_immutable`.

---

### User Story 4 - Controlled Figure Override Audit Workflow and Preservation of Calculated Values (Priority: P1)

As a Project Controls Manager or Project Director, I want a formalized workflow to override calculated report figures with a mandatory justification of at least 10 characters, while permanently preserving the original calculated value and visibly flagging overridden figures with an asterisk and footnote, so that negotiated adjustments (e.g., consultant site agreements) can be reflected without concealing the initial computed truth.

**Why this priority**: Essential auditability and dispute management (US-PR-07, G04, G06). Discrepancies between theoretical calculations and consultant field agreements occur regularly. Allowing overrides without enforcing minimum rationale length or overwriting the original value destroys the audit trail and invites fraudulent adjustments.

**Independent Test**: Can be tested by attempting to override a figure with a 3-character reason (verifying rejection with `override_reason_required`), then submitting a 15-character valid justification, verifying that `calculated_value` remains intact, `value` reflects the overridden value, `is_overridden` is set to true, an override record is logged, and the presentation layer displays an asterisk with a footnote referencing the reason and author.

**Acceptance Scenarios**:

1. **Given** a calculated figure in a periodic report,  
   **When** an authorized user attempts to override the figure with an empty reason or a text shorter than 10 characters (e.g., "OK" or "modified"),  
   **Then** the system rejects the override with HTTP 400 and error code `override_reason_required`, displaying: «دلیل بازنویسی باید حداقل ۱۰ کاراکتر باشد».
2. **Given** a user lacking the `edit_reports` or `approve_reports` permission,  
   **When** the user attempts to submit a figure override,  
   **Then** the system rejects the request with HTTP 403 Forbidden.
3. **Given** an authorized user providing a valid justification (≥ 10 characters) and a new figure value,  
   **When** the override is submitted,  
   **Then** the system:  
     - Preserves the initial computed value in `calculated_value` without modification  
     - Sets the active `value` to the new overridden value  
     - Marks the figure as overridden (`is_overridden = True`)  
     - Creates an immutable audit record containing the old value, new value, override timestamp, justification text, and user identifier  
     - Flags the figure in the UI and exported document with an asterisk (*) linked to a footnote containing the justification and author.

---

### User Story 5 - Comprehensive Monthly Status Report, SPI/CPI Performance Indices, and Serialized Release (Priority: P2)

As an Executive Director, Technical VP, or Client Representative, I want a comprehensive monthly project status report integrating physical progress S-curves, financial IPC commitments, daily HSE incidents, QC inspection summaries, and variance analysis (SPI and CPI), culminating in an approved official release stamped with a unique serial number and generation timestamp, so that project governance meets corporate and contractual standards.

**Why this priority**: Executive decision support and stakeholder reporting (US-PR-05, G05). Monthly reports currently lack HSE incident rollups, QC quality inspection summaries, CPI calculations, and formal release serialization.

**Independent Test**: Can be tested by generating a monthly report for a Solar Hijri month with recorded progress, cost, daily safety incidents, and QC inspections, verifying that SPI and CPI indices are computed, HSE and QC summaries are populated, and upon official approval, a unique serial number and timestamp watermark are affixed to all output pages.

**Acceptance Scenarios**:

1. **Given** project records across a Solar Hijri month,  
   **When** a monthly progress report is generated,  
   **Then** the report compiles seven comprehensive chapters:  
     1. Overall physical progress (planned vs. actual cumulative) with S-curve data points  
     2. Financial status, Interim Payment Certificates (IPC), and cash flow liquidity  
     3. HSE incident summary (lost time injuries, near misses, environmental events) consolidated from daily incident logs  
     4. Quality control (QC) inspection results, non-conformance reports (NCR), and material test statuses  
     5. Schedule and cost variance analysis including Schedule Performance Index (SPI) and Cost Performance Index (CPI)  
     6. Critical risks, technical obstacles, and required executive decisions  
     7. Lookahead operational forecast for the upcoming month.
2. **Given** a monthly report ready for executive release,  
   **When** the designated authority approves the report,  
   **Then** the status transitions to `approved`, an immutable unique official serial number (e.g., `REP-PRJ01-140508-M01`) is generated, and the serial number along with the exact extraction timestamp is displayed on all pages and exported documents.
3. **Given** a monthly report that has been approved with an official serial number,  
   **When** any user attempts to edit or re-rollup that report version,  
   **Then** the system prevents modifications, requiring any subsequent updates to supersede the report into a new revision.

---

### User Story 6 - Solar Hijri (Jalali) Workweek Scheduling and Structured Presentation (Priority: P2)

As a Field Planning Engineer working in Iran, I want the periodic report selector to automatically default to Solar Hijri Saturday-to-Friday workweeks and Jalali calendar months, and I want complex figures presented in structured cards and tables rather than raw JSON strings, so that the operational UI is clear, intuitive, and locale-compliant.

**Why this priority**: Usability, locale compliance, and Constitution Principle III (G07). The UI currently defaults to Gregorian Monday-Sunday intervals and renders structured JSON objects as raw strings in table cells.

**Independent Test**: Can be tested by opening the periodic reports dashboard, verifying that the period picker offers Saturday-to-Friday week intervals and Jalali month selections, and verifying that multi-field figures (such as machinery hours or next-week plans) render as formatted tables/cards with Persian typography.

**Acceptance Scenarios**:

1. **Given** a user opening the periodic report generation interface,  
   **When** selecting the "Weekly" report type,  
   **Then** the period defaults to the current or most recent Saturday-to-Friday workweek according to the Solar Hijri (Jalali) calendar.
2. **Given** a user selecting the "Monthly" report type,  
   **When** choosing a month,  
   **Then** the period selector aligns with the start (1st) and end (29th/30th/31st) of the chosen Solar Hijri month (e.g., Farvardin to Esfand).
3. **Given** report figures containing multi-attribute structured data (e.g., critical activities list, next week lookahead, machinery breakdown),  
   **When** viewed in the report details panel,  
   **Then** the system formats each item into dedicated responsive cards and tables with localized Persian headers, numbers, and status badges, completely avoiding raw JSON string dumps.

---

### Edge Cases

- **Missing Daily Reports in Period**: If no daily reports exist for the entire week or month, the report generation must succeed with zeroed/empty rollup sections and generate a critical warning: «هیچ گزارش روزانه‌ای برای بازه انتخابی ثبت نشده است».
- **All Days Unapproved**: If daily reports exist but all are in `draft` status, the report rolls up zero volumes and appends warning messages for every single day.
- **Mid-Week Scope or Contractor Changes**: If a subcontractor or trade was active for only 2 out of 7 days, the labor/machinery breakdown must accurately sum only those active days without dividing by 7 or assuming full-week presence.
- **Concurrent Overrides on the Same Figure**: If two authorized users attempt to override the same figure simultaneously, optimistic locking or transaction isolation must ensure that the second submission receives a concurrency conflict (`409 conflict` or stale version check) and prompts the user to refresh.
- **Superseding an Existing Period Report**: If a periodic report is regenerated for an already-generated period, the previous unapproved report must be marked as `superseded`, while retaining its history and any attached figure overrides.
- **Retroactive Daily Report Approval**: If a daily report that was in `draft` during the initial weekly rollup is subsequently approved, the existing weekly report remains unchanged until explicitly regenerated by an authorized user, preventing silent background mutations of historical reports.
- **Negative or Zero Override Values**: If an override value is entered for a metric that cannot logically be negative (e.g., labor hours or concrete quantity < 0), the system must reject the value with a domain validation error.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Weekly Report Automated Rollup (G01, G02)
- **FR-001**: The system MUST support generating weekly progress reports based on a Saturday-to-Friday workweek boundary in the Solar Hijri (Jalali) calendar.
- **FR-002**: The system MUST aggregate physical and field metrics exclusively from daily site reports that have reached the `approved` status within the specified period.
- **FR-003**: The system MUST automatically exclude any daily site reports in `draft`, `submitted`, or unapproved status from all rollup calculations.
- **FR-004**: The system MUST populate the weekly report with five mandatory sections: (1) Completed Activities Summary, (2) Critical Activities Delay and Deviation, (3) Labor and Machinery Working Hours, (4) Delivered and Consumed Materials, and (5) Next Workweek Lookahead Plan.
- **FR-005**: For labor and machinery, the system MUST compute total regular hours, overtime hours, and operating/idle machinery hours grouped by contractor organization and trade/equipment category.
- **FR-006**: For materials, the system MUST compute total delivered volumes and consumed volumes during the week, grouped by material type and engineering unit.
- **FR-007**: For activities, the system MUST identify all activities with actual finish dates falling within the workweek and include them in the Completed Activities section.
- **FR-008**: For critical path activities, the system MUST extract activities where schedule variance is negative or forecast finish exceeds planned finish, detailing the calculated delay.
- **FR-009**: The system MUST inspect the reporting interval for unapproved or missing daily reports, and populate the report header's `warnings` list with explicit localized messages: «گزارش روز [تاریخ شمسی] تأیید نشده است و احجام آن در این گزارش لحاظ نگردید».

#### Figure Provenance and Deletion Protection (G03)
- **FR-010**: The system MUST maintain a granular provenance breakdown (`PeriodReportFigureSourceItem`) for every aggregated figure in a periodic report.
- **FR-011**: Each provenance item MUST record: link to parent figure, source entity type (`daily_labor`, `daily_machinery`, `daily_material`, `daily_activity`), source record primary key, source date, contributed quantity/value, creator user ID, and approving supervisor ID.
- **FR-012**: The system MUST provide an inquiry endpoint/interface returning the full provenance breakdown for any selected figure.
- **FR-013**: The database schema MUST enforce referential integrity protection (`PROTECT`) on daily report source records linked to active periodic report figures, preventing accidental or intentional physical deletion of source records.
- **FR-014**: The system MUST enforce figure immutability, rejecting direct modifications to generated figures with error code `figure_immutable`.

#### Controlled Figure Override Workflow (G04, G06)
- **FR-015**: The system MUST provide a dedicated, secure override endpoint/action to modify periodic report figures.
- **FR-016**: The override action MUST require authorization check for `edit_reports` or `approve_reports` permissions, strictly denying users with only lower-level permissions (such as `edit_activities`).
- **FR-017**: The override action MUST validate that the justification text (`override_reason`) is at least 10 characters long, rejecting blank or shorter reasons with error code `override_reason_required`.
- **FR-018**: When a figure is overridden, the system MUST preserve the original computed value in `calculated_value`, assign the new value to `value`, and set `is_overridden = True`.
- **FR-019**: The system MUST record every override in an immutable audit log (`PeriodReportFigureOverride`), storing: figure reference, previous value, new overridden value, justification reason, overriding user, and timestamp.
- **FR-020**: The user interface and exported documents MUST render an asterisk (*) adjacent to any overridden figure and provide an explanatory footnote referencing the justification and author.

#### Monthly Comprehensive Report and Executive Release (G05)
- **FR-021**: The system MUST support generating monthly progress reports aligned with Solar Hijri calendar months.
- **FR-022**: The monthly report MUST compile comprehensive chapters covering: (1) Physical progress S-curve, (2) Financial status, commitments, and Interim Payment Certificates (IPC), (3) Daily HSE incident log rollup (Lost Time Injuries, near misses, environmental incidents), (4) Quality Control (QC) inspection summaries, (5) Variance analysis including Schedule Performance Index (SPI) and Cost Performance Index (CPI), (6) Critical risks and decision bottlenecks, and (7) Next month lookahead forecast.
- **FR-023**: The system MUST compute both SPI (`EV / PV`) and CPI (`EV / AC`) for the reporting period, rendering «ثبت‌نشده» (not recorded) if cost or planned value data is unavailable, avoiding deceptive zero values.
- **FR-024**: The system MUST support a formal approval workflow for monthly reports, transitioning the report to `approved` status.
- **FR-025**: Upon approval, the system MUST assign an immutable, unique official serial number (e.g., `REP-[PROJECT_CODE]-[JALALI_YEAR_MONTH]-[SEQUENCE]`) and imprint the serial number along with the exact generation timestamp on every page of the output.

#### Localization and Presentation (G07)
- **FR-026**: The user interface MUST provide a Jalali date picker and default date interval buttons for Saturday-to-Friday workweeks and Solar calendar months.
- **FR-027**: The UI MUST render multi-attribute report sections (machinery hours, lookahead plan, critical delays) using specialized, accessible data tables and cards with Persian typography, rather than raw JSON strings.

---

### Key Entities

- **`ProjectPeriodReport`**: Represents the periodic weekly or monthly report document.  
  *Key Attributes*: `project`, `kind` (`weekly` / `monthly`), `period_start`, `period_end`, `status` (`generated`, `approved`, `superseded`), `serial_number` (unique official identifier), `warnings` (list of header warning messages), `generated_by`, `approved_by`, `approved_at`, `created_at`.
- **`PeriodReportFigure`**: An individual quantitative or structured metric within a report section.  
  *Key Attributes*: `report`, `section`, `label_key`, `value` (active value), `calculated_value` (original calculated volume), `is_overridden` (boolean flag), `unit_of_measure`, `value_status` (`recorded`, `not_recorded`), `last_updated_at`.
- **`PeriodReportFigureSourceItem`**: Represents an individual constituent source item contributing to a rolled-up figure (provenance item).  
  *Key Attributes*: `figure` (FK to `PeriodReportFigure`), `source_type` (`daily_report`, `daily_labor`, `daily_machinery`, `daily_material`, `daily_activity`, `daily_incident`, `baseline_task`), `source_id` (protected link to source model), `source_date` (Gregorian/Jalali date), `source_code` (daily report human code), `contributed_quantity` (numeric or structured fraction), `created_by` (source creator), `approved_by` (source approver).
- **`PeriodReportFigureOverride`**: Immutable audit record for an authorized figure modification.  
  *Key Attributes*: `figure` (FK to `PeriodReportFigure`), `previous_value`, `overridden_value`, `reason` (minimum 10 characters), `overridden_by` (FK to User), `created_at`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of generated weekly reports accurately reflect all 5 mandatory sections derived from approved daily reports without requiring manual data compilation.
- **SC-002**: 100% of unapproved or draft daily reports in the period are excluded from weekly rollups, and 100% of such excluded dates trigger an explicit warning message in the report header.
- **SC-003**: In 100% of tested cases, users can query any rolled-up figure and view its complete itemized provenance breakdown (daily records, contributing quantities, authors, and approvers) in 1 click or request.
- **SC-004**: Database referential integrity blocks 100% of attempts to physically delete daily report source records that are linked to active periodic reports.
- **SC-005**: 100% of figure override attempts with a reason of fewer than 10 characters are rejected with a descriptive validation error.
- **SC-006**: 100% of overridden figures preserve their initial `calculated_value` intact and display an asterisk with an explanatory footnote across both UI and printed/exported views.
- **SC-007**: 100% of approved monthly reports display a unique official serial number and generation timestamp watermark across all pages.
- **SC-008**: 100% of UI report generation views default to Solar Hijri Saturday-to-Friday workweeks and Jalali months, displaying all section figures in formatted tables and cards with zero raw JSON string dumps.

---

## Assumptions

- **Calendar System**: The primary operational calendar for site reporting is the Solar Hijri (Jalali) calendar; workweeks run from Saturday (شنبه) to Friday (جمعه), while internal backend storage maintains ISO date equivalents.
- **Daily Report Lifecycle**: Daily reports follow the state machine defined in `field_reports`: only reports in `approved` status are considered final; `draft` or `submitted` reports are subject to supervisor revision and are therefore excluded from rollups.
- **EVM and Financial Data**: Monthly reports integrate available financial and schedule metrics; where Earned Value or cost data is unavailable, the system transparently indicates «ثبت‌نشده» (not recorded) rather than fabricating zero values.
- **Permissions and RBAC**: Project membership and role-based permissions (`view_dashboard`, `edit_reports`, `approve_reports`) are enforced server-side, adhering strictly to Constitution Principle I and Principle IV.
- **Referential Integrity**: Physical deletion of historical site data is strictly prevented when locked into approved reports; soft-delete or archiving mechanisms should be used if operational deactivation is required.
