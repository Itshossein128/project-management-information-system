# Feature Specification: Shiraz Excel Forms Parity & Official PDF Standardization

**Feature Branch**: `044-shiraz-excel-parity-pdf`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "یک feature منسجم برای «انطباق ساختار گزارشگیری سامانه با فرمهای اکسل شیراز (Shiraz Excel Forms Parity) شامل تولید فایل اکسل گزارش روزانه کل کارگاه منطبق بر تمپلیت FILE 4 با ۳۴ ردیف نیروی ستادی، ۳۲ ردیف نیروی کارگری، ماشینآلات، مصالح، بتنریزی و فعالیتها همراه با فرمولهای بومی جمع، ساخت فایلهای اکسل تفکیکشده سابریپورتهای ابنیه (FILE 5 با ستون درصد اجرا 0.0% و قطعه) و تأسیسات برقی (FILE 6)، تولید گزارش رسمی چاپی و PDF با ۳ بلوک امضای دیجیتال (تنظیمکننده، بررسیکننده، تأییدکننده)، شناسه یکتای امنیتی (Audit Hash) و واترمارک پیشنویس، همگامسازی فیلترهای چندبعدی در URL مرورگر (useSearchParams)، خروجی اکسل دیتابیس جامع فعالیتها (FILE 1)، و بهروزرسانی کامل درخت تصمیمگیری (Decision Tree)»"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Whole-Site Daily Report Excel Export with Shiraz FILE 4 Parity (Priority: P1)

As a resident site supervision consultant and client technical office auditor, I need the exported master daily report spreadsheet to strictly match the physical and electronic layout of Shiraz National Housing FILE 4 (including standard right-to-left layout, 34 staff labor rows, 32 craft labor rows, incoming materials, concrete casting, equipment status, and activity tables with native spreadsheet sum formulas), so that daily site logs can be submitted, audited, and archived without format friction or manual data re-entry.

**Why this priority**:
Site daily reporting at industrial scale (such as the 2,000-unit Shiraz project) requires contractual parity with approved physical forms. Without FILE 4 spreadsheet export, technical offices cannot exchange standardized digital reports with external consultants and auditors, blocking official progress sign-offs.

**Independent Test**:
Can be fully tested by selecting any completed or approved daily report in the web application or API, triggering the FILE 4 Excel download, and opening the resulting `.xlsx` document in a spreadsheet viewer: the worksheet displays RTL direction, complete project header, exactly 34 indirect staff rows with `=SUM(...)` formulas, 32 direct worker rows with `=SUM(...)` formulas, a grand total manpower sum formula, and accurate tables for materials, concrete volume, equipment, and daily activities.

**Acceptance Scenarios**:

1. **Given** an authorized user (`view_reports` permission and project membership) is viewing a daily report,  
   **When** the user clicks "خروجی اکسل (FILE 4)" or sends a retrieval request for the report's Excel export,  
   **Then** the system returns a downloadable spreadsheet workbook with `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` and filename formatted as `daily-report-{report_date}-{shift}.xlsx` (e.g., `daily-report-1403-11-14-shift1.xlsx` or ISO equivalent).

2. **Given** the exported master daily report workbook is opened in a spreadsheet application,  
   **When** the worksheet layout and view options are inspected,  
   **Then** the sheet orientation is right-to-left (`RTL`), Persian typography and numerals are applied uniformly, and rows 1 to 8 contain the unified project header (project name, contract number, Jalali date, day of week, shifts 1/2/3 operating hours, site operational status with inactive reason if applicable, and atmospheric weather with minimum/maximum temperature).

3. **Given** Section A (Indirect Staff Manpower) and Section B (Direct Labor Manpower) in the exported FILE 4 sheet,  
   **When** the row structure and calculation cells are audited,  
   **Then** Section A contains all 34 fixed Shiraz staff titles (from branch manager to guest) with their recorded shift counts, absent counts, and a subtotal row evaluating the native formula `=SUM(...)`; Section B contains all 32 fixed Shiraz worker titles with recorded counts and a subtotal row evaluating `=SUM(...)`; and the grand total manpower cell evaluates `=SUM(...)` adding indirect and direct subtotals.

4. **Given** the daily report contains records of incoming materials (Section C), concrete pours (Section D), machinery/equipment (Section E), and executed activities (Section F),  
   **When** inspecting these sections in the generated spreadsheet,  
   **Then** Section C lists material name, quantity, unit, supplier, and bill of lading; Section D details concrete grade, poured volume in cubic meters, parcel, block, floor, application element, and total volume; Section E details equipment name, status (active, standby, breakdown), ownership, active hours, and repair hours; and Section F details sequential index, activity description, shift, contractor name, crew headcount, parcel/zone, block, floor, unit, and executed quantity.

---

### User Story 2 - Discipline-Specific Sub-Report Excel Exports for Civil (FILE 5) and Electrical (FILE 6) (Priority: P1)

As a site civil supervisor or electrical installation supervisor, I need to export dedicated, standardized spreadsheet files for my department's daily sub-reports matching Shiraz templates (FILE 5 for Civil with parcel and percentage formatting, and FILE 6 for Electrical without parcel or percentage), so that each trade can independently maintain and audit its engineering work logs.

**Why this priority**:
Civil and electrical site teams work under separate subcontracts and distinct supervisors. Civil activities require parcel-level tracking and explicit percentage completion (`execution_percentage`), whereas electrical works focus on cable length, conduit runs, and crew sizing without parcels or percentage scales. Matching these specific sheet designs is essential for daily handover between subcontractors and general contractors.

**Independent Test**:
Can be independently tested by accessing the discipline daily sub-report panel for both civil and electrical units, downloading their respective Excel exports, and validating that Civil produces FILE 5 layout (with `قطعه` and `درصد اجرا` styled as `0.0%`) while Electrical produces FILE 6 layout (with electrical activity descriptions, counts, and measurements, but without parcel or percentage columns).

**Acceptance Scenarios**:

1. **Given** a civil discipline daily sub-report with recorded contractor activities,  
   **When** the supervisor clicks "دانلود گزارش اکسل ساب‌ریپورت ابنیه (FILE 5)" or requests the sub-report Excel endpoint,  
   **Then** the generated spreadsheet adheres to Shiraz FILE 5 structure: right-to-left orientation, contractor header ("شرکت پی‌چین"), and columns for row index, shift, contractor/crew name, master craftsman count (`استادکار`), laborer count (`کارگر`), parcel (`قطعه`), block (`بلوک`), floor (`طبقه`), activity description (`شرح فعالیت`), unit of measurement, quantity, and execution percentage (`درصد اجرا`) formatted with native spreadsheet percentage styling (`0.0%`).

2. **Given** an electrical discipline daily sub-report with recorded installations (conduits, wiring, junction boxes, switchboards),  
   **When** the supervisor clicks "دانلود گزارش اکسل ساب‌ریپورت تأسیسات برقی (FILE 6)" or requests the sub-report Excel endpoint,  
   **Then** the generated spreadsheet adheres to Shiraz FILE 6 structure: right-to-left orientation, trade header ("اجرای تأسیسات برقی"), columns for row index, integer shift, crew name, master craftsmen, laborers, block, floor, electrical activity description, measurement unit (meters, units, items), and executed quantity, strictly omitting parcel and execution percentage columns.

---

### User Story 3 - Official Standardized PDF Export with Digital Signatures, Audit Hash & Draft Watermark (Priority: P1)

As a project manager and resident engineer, I need the exported PDF daily report to include formal three-tier digital signature blocks (Prepared by Site Supervisor, Reviewed by Technical Office, Approved by Project Manager), a cryptographic audit verification fingerprint (SHA-256 hash), a diagonal "DRAFT" watermark for unapproved reports, and standardized filename conventions, so that printouts and archived electronic PDFs are legally compliant, tamper-evident, and auditable.

**Why this priority**:
Field reports in governmental and multi-tenant housing programs serve as legal basis for monthly contractor payments and claims. Unsigned or arbitrarily named PDFs without audit hashes risk document tampering, disputes, and audit rejection.

**Independent Test**:
Can be independently tested by exporting a daily report in `draft` status (verifying the diagonal draft watermark across pages), advancing the report through submission, review, and approval, and then re-exporting the approved PDF (verifying that the watermark disappears, the three signature blocks display exact usernames and timestamps, the audit fingerprint is embedded, and the filename matches `daily-report-{report_date}-{shift}.pdf`).

**Acceptance Scenarios**:

1. **Given** any daily report requested via PDF export,  
   **When** the server generates the PDF response,  
   **Then** the HTTP header `Content-Disposition` sets the attachment filename strictly to `daily-report-{report_date}-{shift}.pdf`, and the document renders in standard A4 portrait/landscape format with Persian RTL typography.

2. **Given** a daily report that has completed its approval workflow (`status = approved`),  
   **When** viewing the final page of the exported PDF,  
   **Then** the document concludes with three distinct formal signature boxes side-by-side:
   - Box 1: "تنظیم‌کننده (سرپرست کارگاه)" displaying the submitter's full name, role, and exact submission timestamp (`submitted_at`).
   - Box 2: "بررسی‌کننده (دفتر فنی)" displaying the reviewer's full name, role, and exact review timestamp (`reviewed_at`).
   - Box 3: "تأییدکننده (مدیر پروژه / ناظر مقیم)" displaying the approver's full name, role, exact approval timestamp (`approved_at`), and the unique Audit Security Hash (`کد رهگیری امنیتی`).

3. **Given** a daily report in any non-approved state (`draft`, `submitted`, `under_review`, `rejected`),  
   **When** the PDF document is generated and viewed,  
   **Then** every page contains a semi-transparent, diagonal background watermark reading "پیش‌نویس — غیرقابل استناد رسمی (DRAFT)", preventing unauthorized official use of unratified site data.

4. **Given** an approved daily report whose records, dates, lineage, or approval metadata are altered,  
   **When** recalculating the audit security fingerprint (SHA-256 of report identity, lineage, date, shift, status, and approval metadata),  
   **Then** the resulting audit hash does not match the printed fingerprint on the document, providing unambiguous proof of modification.

---

### User Story 4 - Multi-Dimensional Activity Log Filtering with Full URL State Persistence & Master Activity Export (FILE 1) (Priority: P2)

As a technical director and project auditor, I need to filter site activities and daily reports across multiple combined dimensions (date range, discipline, contractor, parcel, zone, block, status) with immediate bi-directional synchronization in browser URL query parameters, view real-time summary aggregates (total quantities and man-days), and export the filtered activity dataset to a flat Excel workbook matching Shiraz FILE 1 (ACTIVITY), so that investigative queries can be shared directly via link and analyzed offline.

**Why this priority**:
Auditing daily site operations requires analyzing cross-cutting slices of data (e.g., all civil works by contractor X in zone 10 over the past 30 days). When filters live only in transient component state, refreshing the browser or sharing a URL resets the query, severely degrading collaborative workflows. Furthermore, technical offices require flat master database exports (FILE 1) to build custom executive dashboards.

**Independent Test**:
Can be independently tested by applying a multi-attribute filter on the activity log and daily reports list, copying the browser URL, opening it in a private or separate browser window, and verifying that all filter inputs and result tables initialize identically with total quantity metrics displayed, and clicking "خروجی اکسل دیتابیس فعالیت‌ها (FILE 1)" downloads all matching records in a structured flat spreadsheet.

**Acceptance Scenarios**:

1. **Given** a user navigates to the Daily Reports list or the Project Activity Log (`project-activity-log.tsx`),  
   **When** the user changes any filter (such as `date_from`, `date_to`, `status`, `discipline`, `contractor`, `parcel`, `zone`, `block`),  
   **Then** the web URL query string updates synchronously via browser search params without a full-page reload, maintaining history and back/forward navigation.

2. **Given** a user opens a bookmarked or shared URL containing query parameters (e.g. `?discipline=CIVIL&contractor=Khabazi&date_from=2026-09-01&parcel=10`),  
   **When** the page loads,  
   **Then** the input fields, selects, and pickers automatically initialize to those parameter values, and the query fetches and presents only the records satisfying all applied conditions in under 2 seconds.

3. **Given** the filtered activity log displays matching records,  
   **When** viewing the table header area,  
   **Then** a prominent summary bar displays cumulative aggregates: total worker count (man-days) and breakdown of total quantities grouped by their unit of measurement (e.g., cubic meters of concrete, kilograms of rebar, linear meters of piping).

4. **Given** a user is viewing the filtered Project Activity Log,  
   **When** the user clicks "خروجی اکسل دیتابیس جامع فعالیت‌ها (FILE 1)",  
   **Then** the application downloads an Excel spreadsheet matching Shiraz FILE 1 (ACTIVITY sheet): RTL orientation, containing columns for row number, Jalali date, activity description, shift, contractor name, worker headcount, parcel, block, floor, location, quantity, and unit.

---

### User Story 5 - Decision Tree State Machine Synchronization (Priority: P2)

As a software system maintainer and QA automation engineer, I need the application decision tree documentation in `docs/decision-tree/` to fully incorporate the new export paths (FILE 4 Excel, FILE 5/6 sub-report Excel, PDF signatures and audit hash) and URL query state persistence nodes, so that all interaction states, permission boundaries, and navigation transitions are tracked and verified against the system's operational graph.

**Why this priority**:
Repository governance rules (`.agents/rules/decision-tree.md`) mandate that every route, permission-gated action, and interactive state transition have a corresponding node in `docs/decision-tree/`. Maintaining an accurate decision tree ensures comprehensive automated testing and prevents undocumented permission vulnerabilities.

**Independent Test**:
Can be tested by inspecting the decision tree directory hierarchy under `docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-daily-reports]/`, confirming the presence and validity of `[export-report-excel]`, updated `[export-report-pdf]`, `[export-sub-report-excel]`, and synchronized `filter-and-change-view`.

**Acceptance Scenarios**:

1. **Given** the decision tree directory for Daily Reports,  
   **When** examining the children of `[view-report]`,  
   **Then** a new decision node `[export-report-excel]/README.md` exists documenting the trigger, required permission (`view_reports` + `IsProjectMember`), expected binary `.xlsx` download of FILE 4, and return path.

2. **Given** the existing `[export-report-pdf]/README.md` node,  
   **When** reviewing its contents,  
   **Then** it documents the three-tier digital signature requirement, cryptographic audit hash verification, and draft watermark behavior.

3. **Given** the decision tree nodes for discipline sub-reports,  
   **When** examining sub-report views,  
   **Then** `[export-sub-report-excel]/README.md` is registered documenting the trade-specific exports for Civil (FILE 5) and Electrical (FILE 6).

4. **Given** the `filter-and-change-view/README.md` node,  
   **When** reviewing the navigation and state changes,  
   **Then** it documents URL query persistence (`useSearchParams`) and link shareability as an explicit state outcome.

---

### Edge Cases

- **Empty / Inactive Daily Reports**: What happens when an exported report corresponds to a day when the site was marked inactive (`وضعیت کارگاه: غیرفعال`) or weather prevented work?
  *Requirement*: The exported FILE 4 and PDF must still generate completely. The header accurately displays the inactive reason (e.g., heavy rain, national holiday); empty sections (such as concrete or materials) must display an empty table with standard headers and zero sum values without formula errors (no `#VALUE!` or `#REF!`).
- **Unmeasured Quantities (`quantity_measured = False` / `*` in historical Excel)**: What happens when an activity occurred but physical quantity was not quantified?
  *Requirement*: In FILE 4 and FILE 1 exports, the quantity cell must render as blank or the canonical symbol `*`, and unit summation in the summary bar must exclude null quantities while accurately summing headcount.
- **Reports with Long Activity Lists (Over 50 items)**: How does the system handle page breaks and cell auto-sizing in Excel and PDF?
  *Requirement*: In Excel, row heights must auto-fit activity text without truncating descriptions. In PDF, ReportLab table flows cleanly across multiple pages, repeating table headers on subsequent pages, with signature blocks pinned to the concluding page.
- **Simultaneous / Missing Approval Steps**: What happens if an approved report is exported that bypassed review (direct approval)?
  *Requirement*: The review signature box displays "عدم نیاز به بررسی دفتر فنی / تأیید مستقیم" (Direct Approval) with the approver's data populated, maintaining the three-box layout integrity.
- **Special Characters in Filenames**: How are dates, shifts, and project codes formatted in HTTP Content-Disposition headers across browsers?
  *Requirement*: Filenames must use clean ASCII/standard hyphenated strings (e.g. `daily-report-1403-11-14-shift1.xlsx` / `.pdf`), properly quoted in `Content-Disposition`, avoiding illegal filesystem characters (`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`).
- **Deeply Filtered Activity Queries with Zero Results**: What happens when a user shares a URL whose query returns zero rows?
  *Requirement*: The UI must present a localized "هیچ فعالیتی با فیلترهای مشخص‌شده یافت نشد" empty state, URL parameters remain preserved, summary bar displays zero values, and clicking Excel export yields an empty formatted workbook with column headers intact rather than a 500/404 error.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an authorized export endpoint (`GET /api/v1/projects/{project_pk}/daily-reports/{id}/excel/`) that returns a fully formatted Microsoft Excel spreadsheet (`.xlsx`) adhering to Shiraz template FILE 4.
- **FR-002**: The FILE 4 Excel workbook MUST configure right-to-left worksheet orientation (`ws.sheet_view.rightToLeft = True`) and use Persian-compatible typography.
- **FR-003**: The FILE 4 Excel header (Rows 1–8) MUST present project name, contract number, Jalali date, Persian day of the week, shifts 1–3 operating hours, workshop operational status (active/inactive with reason), and atmospheric weather conditions with minimum and maximum temperatures.
- **FR-004**: The FILE 4 Excel Section A MUST populate all 34 standard Shiraz indirect/staff labor positions (from branch manager to guest) with recorded shift numbers, absence count, and an Excel native `=SUM(...)` subtotal formula row.
- **FR-005**: The FILE 4 Excel Section B MUST populate all 32 standard Shiraz direct/craft labor positions with recorded counts, an Excel native `=SUM(...)` subtotal formula row, and a grand total manpower row summing Sections A and B using a native spreadsheet addition formula.
- **FR-006**: The FILE 4 Excel workbook MUST include formatted tables for Incoming Materials (Section C), Concrete Casting Volumes (Section D), Machinery/Equipment status and operating hours (Section E), and Daily Executed Activities (Section F) with proper borders and alignments.
- **FR-007**: System MUST provide an authorized sub-report Excel export endpoint (`GET /api/v1/projects/{project_pk}/units/{unit}/daily-reports/{id}/excel/`) generating trade-specific spreadsheets for Civil (FILE 5) and Electrical (FILE 6).
- **FR-008**: The Civil sub-report Excel (FILE 5) MUST include columns for Row Number, Shift, Contractor/Crew Name, Master Craftsmen, Laborers, Parcel (`قطعه`), Block (`بلوک`), Floor (`طبقه`), Activity Description, Unit, Quantity, and Execution Percentage (`درصد اجرا`) formatted with spreadsheet percentage styling (`0.0%`).
- **FR-009**: The Electrical sub-report Excel (FILE 6) MUST include columns for Row Number, Shift, Crew Name, Master Craftsmen, Laborers, Block, Floor, Electrical Activity Description, Unit, and Quantity, and MUST NOT include parcel or execution percentage columns.
- **FR-010**: System MUST enforce that both whole-site and sub-report Excel downloads require `view_reports` permission and verified project membership (`IsProjectMember`).
- **FR-011**: System MUST set the HTTP `Content-Disposition` attachment filename for PDF downloads strictly to `daily-report-{report_date}-{shift}.pdf`.
- **FR-012**: System MUST generate an unapproved daily report PDF (`draft`, `submitted`, `under_review`, `rejected`) with a prominent, semi-transparent diagonal watermark across each page stating "پیش‌نویس — غیرقابل استناد رسمی (DRAFT)".
- **FR-013**: System MUST omit the draft watermark when generating a PDF for a daily report whose status is `approved`.
- **FR-014**: The daily report PDF MUST include a formal three-tier signature section on its concluding page comprising three discrete boxes:
  1. "تنظیم‌کننده (سرپرست کارگاه)": submitter name, role, and submission timestamp.
  2. "بررسی‌کننده (دفتر فنی)": reviewer name, role, and review timestamp.
  3. "تأییدکننده (مدیر پروژه / ناظر مقیم)": approver name, role, approval timestamp, and cryptographic audit hash.
- **FR-015**: System MUST compute a deterministic cryptographic Audit Hash (SHA-256 fingerprint) for each report based on immutable identifiers, date, shift, status, and approval lineage, printing the fingerprint in the approved PDF signature block.
- **FR-016**: The frontend Daily Reports list page (`daily-reports-list.tsx`) MUST synchronize all filter controls (`date_from`, `date_to`, `status`, `discipline`, `contractor`, `block`) with the browser URL query string using `useSearchParams`.
- **FR-017**: The frontend Project Activity Log (`project-activity-log.tsx`) MUST synchronize all multi-dimensional filters (`date_from`, `date_to`, `discipline`, `parcel`, `zone`, `block`, `subcontractor`, `page`) with the browser URL query string using `useSearchParams`.
- **FR-018**: The Project Activity Log MUST provide an export action that downloads the full filtered activity dataset as a flat Excel spreadsheet matching Shiraz FILE 1 (ACTIVITY), retaining all applied filters.
- **FR-019**: The Project Activity Log MUST display a prominent summary bar calculating total worker headcount (man-days) and aggregated physical quantities categorized by measurement unit for the filtered result set.
- **FR-020**: The system's decision tree in `docs/decision-tree/` MUST be updated with dedicated nodes for FILE 4 Excel download (`[export-report-excel]`), trade sub-report Excel download (`[export-sub-report-excel]`), updated official PDF specifications (`[export-report-pdf]`), and URL query persistence documentation (`filter-and-change-view`).

---

### Key Entities *(include if feature involves data)*

- **DailyReportExportDocument**: Represents the generated binary artifact (FILE 4 `.xlsx` or official `.pdf`) derived from a specific `DailyReport` instance, holding the calculated audit fingerprint, export timestamp, and standard filename string.
- **DisciplineSubReportExport**: Represents the generated binary spreadsheet artifact (FILE 5 Civil or FILE 6 Electrical) derived from a `DisciplineSubReport` and its associated `DisciplineSubReportActivity` records.
- **ReportAuditFingerprint**: Represents the deterministic 16-character hexadecimal cryptographic hash calculated via SHA-256 over the tuple of `(report_id, lineage_id, report_date, shift, status, approved_at, approved_by_id)`.
- **ActivityQueryFilterSet**: Represents the multidimensional state bundle (`date_from`, `date_to`, `discipline`, `contractor`, `parcel`, `zone`, `block`, `status`, `page`) synchronized bi-directionally between the web UI and the browser URL query parameters.
- **ActivitySummaryMetrics**: Represents the client/server aggregate totals for an active activity query, containing total worker headcount (man-days) and a map of `unit_of_measure -> total_quantity`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of exported master daily report spreadsheets (FILE 4) and sub-report spreadsheets (FILE 5/6) maintain native right-to-left (`RTL`) sheet orientation and render with zero formula evaluation errors (`#REF!`, `#VALUE!`, `#NAME?`) when opened in standard spreadsheet software.
- **SC-002**: Technical office users can export and download any master daily report spreadsheet (FILE 4) or official PDF for a typical site day (15–30 activities, 20 materials/equipment rows) in under 3.0 seconds over standard broadband.
- **SC-003**: 100% of approved PDF reports contain valid three-tier digital signature blocks with verifiable audit hashes, and 100% of unapproved reports display the diagonal draft watermark.
- **SC-004**: Any bookmarked or shared activity log URL reproduces 100% identical filter inputs, pagination state, and filtered record sets when opened by another authorized project member.
- **SC-005**: 100% of exported civil sub-reports (FILE 5) feature valid percentage formatting (`0.0%`) for execution percentages, while 100% of electrical sub-reports (FILE 6) omit parcel and percentage columns in full compliance with Shiraz standards.
- **SC-006**: System decision tree documentation in `docs/decision-tree/` accurately reflects 100% of newly added export actions, permission gates, and navigation pathways with zero broken reference links.

---

## Assumptions

- **Spreadsheet Software Compatibility**: Client and consultant organizations use Microsoft Excel (2016 or newer), LibreOffice Calc, or Google Sheets capable of processing standard OpenXML (`.xlsx`) files and native `=SUM()` formulas.
- **Jalali Date Conversion**: The existing server-side and client-side Jalali calendar conversion utilities (`jdatetime`, Persian date helpers) are stable, reliable, and provide correct weekday names in Persian.
- **Staff and Labor Role Seeds**: The 34 indirect staff titles and 32 direct worker titles are predefined in the project database (via migration `0010_shiraz_labor_titles.py`) and correspond to the Shiraz reference templates.
- **Security & Authorization Model**: Project membership and the `view_reports` permission remain the authoritative authorization barrier for both viewing reports on the web and downloading binary Excel/PDF exports.
- **Print Dimensions**: The default layout for the official PDF report is designed for A4 landscape/portrait reading, with font scaling configured to prevent horizontal table clipping.
