# Feature Specification: Department Activity Reports & Excel Workbooks

**Feature Branch**: `042-department-activity-reports`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "یک feature منسجم برای «ثبت و مدیریت رکوردهای فعالیت روزانه دپارتمانهای ۵ گانه کارگاه (ابنیه/civil، برق/electrical، مکانیک/mechanical، ماشینآلات/machinery، انبار/warehouse) همراه با ثبت فیلد مقدار اجرا، دانلود ورکبوکهای رسمی اکسل (.xlsx) گزارشات روزانه با جمع احجام و گزارشات هفتگی چندزبانه با شیتهای روزانه، شیت جمعبندی و فرمولهای بومی محاسباتی (=SUM)، خروجی اکسل فیلترشده با استانداردهای خط فارسی و RTL، و ورود دستهای دادهها از طریق تمپلیت اکسل با اعتبارسنجی سطر-محور و تضمین تراکنش اتمیک (All-or-Nothing Rollback)»"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Daily Department Records & Single Excel Daily Report (Priority: P1)

As a technical office engineer or discipline supervisor (Civil, Electrical, Mechanical, Machinery, Warehouse), I want to record daily field activities including the actual executed quantity, and immediately download an official single-day Excel (.xlsx) report with a formal project header and automatic total volume summation, so that discipline-specific daily progress can be archived, verified, and audited by project supervision without interfering with other departments.

**Why this priority**: Core daily site operations require recording the actual volume/quantity of executed work (e.g., cubic meters of concrete, meters of conduit), not just the unit. Without `executed_quantity`, daily volume tracking and official daily Excel submissions to project consultants are impossible.

**Independent Test**: Can be tested independently by creating an activity record with an executed quantity in any non-warehouse department (using either `civil` or `buildings` slug), and downloading the daily `.xlsx` report for a specific selected date, verifying that the spreadsheet contains project header metadata, the recorded item, and a total volume row calculating the sum.

**Acceptance Scenarios**:

1. **Given** a project member with `edit_reports` permission in the Civil department (`/projects/:businessId/buildings` or `/projects/:businessId/civil`),
   **When** they open the activity creation form, enter activity description "بتن‌ریزی فونداسیون", select contractor "پارس سازه", specify location "بلوک شرقی", enter executed quantity "45.500", and unit "مترمکعب", and submit the form,
   **Then** the record is successfully saved with `executed_quantity = 45.500`, department identifier `civil` (aliased to `buildings`), and the activity appears in the department table with its executed quantity.
2. **Given** activity records exist for date `2026-10-17` in the Electrical department,
   **When** the user selects date `2026-10-17` and requests the daily report via `GET .../reports/daily/?department=electrical&date=2026-10-17`,
   **Then** the system returns a valid Excel workbook (`.xlsx`) with HTTP 200, containing an official project header (project name, department, date), a table of records for that date, and a bottom summary row with native `=SUM(...)` formula aggregating numeric executed quantities.
3. **Given** an existing project requesting daily reports using `department=civil` or `department=buildings`,
   **When** either slug is passed in the query parameter,
   **Then** the server treats both slugs identically, returns HTTP 200 with the civil engineering records, and never returns HTTP 400 Bad Request due to slug alias mismatch.
4. **Given** a user recording items in the Warehouse department (`department=warehouse`),
   **When** they save warehouse records,
   **Then** warehouse-specific inventory tracking fields (`material_type`, `quantity_in`, `quantity_out`, `unit`, `supplier`, `consumption_location`) remain enforced, while non-warehouse `executed_quantity` remains isolated to non-warehouse departments.

---

### User Story 2 - Multi-Sheet Weekly Department Workbook with Native Calc Formulas (Priority: P1)

As a discipline supervisor and project site manager, I want to download a consolidated weekly Excel workbook for any chosen work week (Saturday through Friday) containing separate tabs for each day of the week, a consolidated summary sheet, and native spreadsheet calculation formulas (`=SUM(...)`), so that weekly progress meetings and engineering audits can review both daily granularity and weekly rollups with dynamic recalculation capabilities.

**Why this priority**: Project weekly coordination meetings and contractor payment reviews require multi-day cross-sectional visibility in editable spreadsheet format. Static PDFs prevent auditing calculations, formula-driven verification, and merging into main contract spreadsheets.

**Independent Test**: Can be tested independently by requesting a weekly report for a specific week starting date (`week_start=2026-10-17`), verifying that the downloaded `.xlsx` file has 8 distinct sheets (7 daily sheets named Saturday to Friday plus 1 Summary sheet), with each daily sheet containing that day's records and the Summary sheet referencing daily totals with active `=SUM(...)` formulas.

**Acceptance Scenarios**:

1. **Given** a supervisor on the Mechanical department page selecting the work week starting on Saturday `2026-10-17`,
   **When** they click "دانلود گزارش هفتگی" (Download Weekly Report),
   **Then** the system requests `GET .../reports/weekly/?department=mechanical&week_start=2026-10-17` and delivers a `.xlsx` workbook titled with project code, department, and week range.
2. **Given** the downloaded weekly `.xlsx` workbook,
   **When** opened in any standard spreadsheet application,
   **Then** the workbook contains exactly 8 worksheets: seven daily sheets (labeled with Persian weekday and Gregorian/Solar dates: شنبه، یکشنبه، دوشنبه، سه‌شنبه، چهارشنبه، پنجشنبه، جمعه) and one final "جمعبندی هفتگی" (Weekly Summary) sheet.
3. **Given** daily sheets populated with executed activity items across the 7-day period,
   **When** inspecting the total rows of daily sheets and the aggregation columns of the Summary sheet,
   **Then** numeric total cells contain active native spreadsheet formulas (e.g., `=SUM(E5:E18)` or cross-sheet references) rather than hardcoded static text, allowing instant recalculation when values are modified locally.
4. **Given** a week where no activity occurred on Tuesday and Friday,
   **When** the weekly workbook is generated,
   **Then** the sheets for Tuesday and Friday render with formal project headers and a clean "رکوردی در این روز ثبت نشده است" indicator with zeroed sum formulas, preserving the standard 8-sheet structure without corruption.

---

### User Story 3 - Filtered Export & Atomic Batch Import with Row-Level Feedback (Priority: P1)

As a site technical office data clerk, I want to export filtered department activity tables to RTL-styled Excel sheets with Persian typography and import bulk activity records using a standard Excel template under strict all-or-nothing atomic transaction guarantees and row-specific validation feedback, so that bulk data entry is efficient, secure, and immune to partial data corruption.

**Why this priority**: Field personnel often prepare records offline or in batch spreadsheets. If an import fails midway and saves partial rows (Partial Import), duplicate entries and corrupted data lines occur on subsequent attempts. Strict atomic rollback and row-level Persian diagnostics are crucial for data integrity.

**Independent Test**: Can be tested independently by uploading an Excel template with valid rows plus an intentional format error on row 4, verifying that the server rejects the entire file with an HTTP 400 response stating «خطا در سطر ۴: مقدار اجرا باید عددی باشد», and confirming that 0 records are created in the database.

**Acceptance Scenarios**:

1. **Given** a user has filtered the Electrical department activity grid by contractor "پارس کابل" and date range `2026-10-01` to `2026-10-15`,
   **When** they click "خروجی اکسل" (Export to Excel),
   **Then** the system generates a `.xlsx` file containing only the filtered rows, formatted with Right-to-Left (RTL) worksheet orientation, standard Persian column headers, project metadata header, and the `executed_quantity` column.
2. **Given** a valid bulk activity spreadsheet adhering to the system template with 25 rows of Civil activities,
   **When** an authorized user with `edit_reports` permission uploads the file via `POST .../import-excel/`,
   **Then** the system validates all 25 rows within a single atomic database transaction, persists all 25 records, and returns HTTP 200 with a localized success message confirming 25 records created.
3. **Given** an uploaded Excel file where rows 1-3 are valid but row 4 contains non-numeric text in the `executed_quantity` column ("ده متر"),
   **When** the batch import endpoint processes the file,
   **Then** the entire transaction is rolled back (0 rows saved to the database), and the server returns HTTP 400 with a structured error response: `{"detail": "خطا در سطر ۴: مقدار اجرا باید عددی باشد", "errors": [{"row": 4, "field": "executed_quantity", "message": "مقدار اجرا باید عددی باشد"}]}`.
4. **Given** an uploaded Excel file where row 7 specifies a contractor not assigned to the active project,
   **When** batch import validates the file,
   **Then** the transaction rolls back completely and returns a localized error: `{"detail": "خطا در سطر ۷: پیمانکار مشخص شده در این پروژه معتبر نیست"}`.
5. **Given** a user with read-only permission (`view_reports`) but lacking `edit_reports` permission,
   **When** they attempt to POST an Excel file to `.../import-excel/`,
   **Then** the server denies access with HTTP 403 Forbidden, preventing unauthorized data modification.

---

### Edge Cases

- **Missing Date Parameters**: If `GET .../reports/daily/` is called without `date`, the system defaults to the current operational project date or previous calendar day, while still returning valid `.xlsx` format.
- **Unparseable or Invalid Date Format**: If `date` or `week_start` contains invalid characters or impossible dates (e.g., `2026-02-31`), the API returns HTTP 400 Bad Request with a clear Persian message: `فرمت تاریخ نامعتبر است (الگوی معتبر: YYYY-MM-DD)`.
- **Zero Records in Date Window**: When no activities exist for the selected day or week, the system generates a valid `.xlsx` workbook containing official headers, empty table structures, and a total row showing 0, avoiding HTTP 500 or corrupted files.
- **Corrupted or Tampered Upload Files**: If an uploaded file is not a valid `.xlsx` file (e.g., renamed text file or CSV), the parser immediately aborts before transaction opening with HTTP 400: `فایل ارسالی یک فایل معتبر اکسل (.xlsx) نمی‌باشد`.
- **Large Batch Files**: Spreadsheets containing up to 5,000 rows are validated within memory and processed in a single transaction without exceeding server request timeouts. Files exceeding the maximum allowed size (e.g., > 10 MB or > 5,000 rows) are rejected with HTTP 413 or HTTP 400 before processing.
- **Mixed Persian / English Numerals**: Batch import parser normalizes Eastern Arabic / Persian numerals (۰۱۲۳۴۵۶۷۸۹) into standard numeric decimals before validation to avoid rejecting valid user inputs.
- **Cross-Tenant Project Isolation**: If an imported file references a contractor ID or location belonging to another project, the system strictly rejects the row to enforce tenant boundary isolation.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST record positive decimal `executed_quantity` (with up to 3 decimal places) for non-warehouse departments (`civil`/`buildings`, `electrical`, `mechanical`, `machinery`) in both backend storage and frontend entry forms.
- **FR-002**: System MUST accept both `civil` and `buildings` as equivalent, valid department query parameters and identifiers across all department activity endpoints without rejecting either with HTTP 400.
- **FR-003**: System MUST provide single-day official department report downloads exclusively in Office Open XML spreadsheet format (`.xlsx`) with MIME type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.
- **FR-004**: System MUST inject an active spreadsheet formula (`=SUM(...)`) into the total volume row of single-day report spreadsheets to dynamically compute the sum of executed quantities.
- **FR-005**: System MUST accept an explicit `date=YYYY-MM-DD` query parameter on `GET .../reports/daily/` and filter activity records strictly for that date.
- **FR-006**: System MUST provide weekly department reports exclusively in multi-sheet `.xlsx` format containing 8 worksheets: seven daily sheets (Saturday through Friday) and one consolidated Summary sheet.
- **FR-007**: System MUST accept an explicit `week_start=YYYY-MM-DD` query parameter on `GET .../reports/weekly/` to define the 7-day period (from `week_start` through `week_start + 6 days`).
- **FR-008**: System MUST inject native spreadsheet formulas (`=SUM(...)`) into the Weekly Summary worksheet linking or aggregating values from the individual daily worksheets.
- **FR-009**: System MUST allow users to download a filtered `.xlsx` export of the active department table reflecting all active UI filters (contractor, date range, location, search query).
- **FR-010**: All generated and exported `.xlsx` spreadsheets MUST apply Right-to-Left (RTL) sheet view orientation, Persian header labels, and clean Persian font styling (e.g., Vazirmatn / Shabnam / Tahoma fallback).
- **FR-011**: System MUST provide an official downloadable Excel template matching the required column schema for bulk activity import for each department type.
- **FR-012**: System MUST validate every row in uploaded batch spreadsheets against required fields, valid contractor bindings, valid calendar dates, and positive decimal numbers for `executed_quantity`.
- **FR-013**: Batch import MUST execute inside an all-or-nothing atomic transaction (`@transaction.atomic`); if any single row contains a validation error, 100% of rows MUST be rolled back and 0 rows persisted.
- **FR-014**: Upon batch import validation failure, the system MUST return structured row-indexed error messages in Persian identifying the exact row number and invalid field (e.g., «خطا در سطر ۴: مقدار اجرا باید عددی باشد»).
- **FR-015**: Batch import endpoint MUST enforce `edit_reports` project permission and MUST reject users possessing only read permission (`view_reports`) with HTTP 403 Forbidden.
- **FR-016**: System MUST enforce strict project isolation: all queried, imported, or exported activities and referenced contractors MUST belong exclusively to the active `project_id`.
- **FR-017**: Frontend department pages MUST include accessible date pickers for selecting the target date for daily reports and the target week starting date for weekly reports before triggering download.
- **FR-018**: Frontend batch import UI MUST display the specific row-level Persian error message returned by the server upon import failure and clear any optimistic or partial success indicators.

---

### Key Entities *(include if feature involves data)*

- **Department Activity Record (`DepartmentActivityRecord`)**: Represents a single unit of operational work performed on a specific date within a project department.
  - Attributes: `id` (UUID), `project` (FK), `department` (Enum: `buildings`/`civil`, `electrical`, `mechanical`, `machinery`, `warehouse`), `date` (Date), `location` (Text), `activity_description` (Text), `contractor` (Text), `contractor_ref` (FK optional), `executed_quantity` (Decimal 14,3, default 0), `unit` (Text), `description` (Text), plus warehouse-specific fields (`material_type`, `quantity_in`, `quantity_out`, `consumption_location`, `supplier`).
- **Department Daily Report Workbook**: A single-worksheet `.xlsx` artifact generated on demand.
  - Components: Project title block, department name, Persian date stamp, tabular data columns (ردیف، تاریخ، شرح فعالیت، پیمانکار، جبهه کاری، مقدار اجرا، واحد، توضیحات), and summary row with `=SUM(...)`.
- **Department Weekly Report Workbook**: An eight-worksheet `.xlsx` artifact generated on demand.
  - Components: 7 daily worksheets (شنبه تا جمعه) with daily items and daily sums; 1 summary worksheet ("جمعبندی هفتگی") aggregating weekly totals by activity/contractor using cross-sheet formulas.
- **Batch Import Payload & Result**: Multipart upload payload containing `.xlsx` workbook, and atomic response payload delivering either total created count or structured list of row-level errors (`row_number`, `column`, `error_message_fa`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of non-warehouse activity submissions support decimal executed quantity with zero data loss or precision truncation up to 3 decimal places.
- **SC-002**: 100% of generated daily and weekly department report downloads are valid Office Open XML spreadsheets (`.xlsx`) readable by Excel and LibreOffice, with 0% fallback to PDF.
- **SC-003**: 100% of weekly workbook downloads contain exactly 8 worksheets (7 daily sheets Saturday–Friday + 1 Summary sheet) with active, dynamic `=SUM(...)` formulas in calculation cells.
- **SC-004**: In batch imports containing any invalid row, exactly 0 records are committed to the database (100% atomic rollback guarantee), with 100% of failure responses reporting the exact row index and a descriptive Persian error message.
- **SC-005**: Both `civil` and `buildings` query parameters return identical 200 OK responses with zero 400 Bad Request errors across all department endpoints.
- **SC-006**: 100% of unauthorized batch import attempts without `edit_reports` permission are blocked with HTTP 403 Forbidden.
- **SC-007**: Users can configure the date or week and complete the download of a 1,000-record daily or weekly report in under 3 seconds.

---

## Assumptions

- Standard Iranian construction project work weeks run Saturday through Friday; weekly rollups partition the 7-day period starting from Saturday (`week_start`).
- Project stakeholders and supervising engineers utilize spreadsheet viewers compatible with the modern `.xlsx` (OpenPyXL / Office Open XML) standard.
- The existing contractor entity within each project is the source of truth for validating contractor names and references during batch import.
- Warehouse department records continue to utilize `quantity_in` and `quantity_out` for materials management, while non-warehouse departments utilize `executed_quantity` for physical work output.
- Server-side font metrics use standard Unicode fonts (e.g., Tahoma or Vazirmatn) embedded or specified for RTL display, ensuring proper rendering across Windows, macOS, and Linux client environments.
