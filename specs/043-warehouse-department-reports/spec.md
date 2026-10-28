# Feature Specification: Warehouse Department Reports

**Feature Branch**: `043-warehouse-department-reports`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "یک feature منسجم برای «مدیریت تخصصی گزارشات و گردش مصالح دپارتمان انبار و تدارکات کارگاه (Warehouse Department Reports) شامل شیت بالانس تجمعی مصالح (Cumulative Material Balance Sheet) در گزارش هفتگی اکسل با تجمیع بر اساس (نوع مصالح، واحد)، محاسبه پویای موجودی اول دوره، کل ورودی، کل خروجی و فرمول بومی اکسل برای مانده پای کار (=Opening + In - Out)، اعتبارسنجی مقادیر با کد خطای ساختاریافته سرور at_least_one_quantity_must_be_positive و پیام فارسی مصوب، صدور گزارش روزانه انبار با فرمت کارگاه شیراز و محاسبه تراز خالص روزانه مصالح، اندپوینت وبسرویس استعلام مانده جاری انبار (GET .../warehouse-balance/)، بهبود تجربه کاربری فرانتاند با قالببندی ارقام و برچسبهای اختصاصی، و بهروزرسانی کامل درخت تصمیمگیری (Decision Tree)»"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record Material Movement with Validation of Positive Quantities (Priority: P1)

As a site warehouse keeper or procurement officer, I want to record material receipts (inbound) and material requisitions (outbound) using the 8 specialized warehouse fields, and receive a strict, localized validation error if both quantities are non-positive, so that material movements are accurately tracked and bogus zero-movement records are prevented.

**Why this priority**: Preventing corrupt or empty movement records and enforcing domain validation at the server boundary is critical for inventory integrity and audit compliance.

**Independent Test**: Submit a warehouse movement record with both inbound and outbound set to 0 and verify the server rejects the request with HTTP 400, error code `at_least_one_quantity_must_be_positive`, and the Persian message «حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد». Then submit valid inbound and outbound records independently and verify both succeed.

**Acceptance Scenarios**:

1. **Given** 500 bags of Portland Cement Type 2 arrive at the construction site, **When** the warehouse officer submits `material_type="سیمان تیپ 2"`, `quantity_in=500`, `quantity_out=0`, `unit="کیسه 50 کیلویی"`, `supplier="کارخانه سیمان فارس"` and bill of lading details, **Then** the record is successfully saved and inbound quantity is credited.
2. **Given** 100 bags of cement are requisitioned for concrete pouring, **When** the warehouse officer records `quantity_in=0`, `quantity_out=100`, `consumption_location="بتن‌ریزی فونداسیون بلوک A"` and the recipient foreman, **Then** the record is successfully saved and outbound quantity is deducted from the site balance.
3. **Given** a warehouse record creation or batch Excel import where both `quantity_in` and `quantity_out` are 0, negative, or empty, **When** the user submits the form or uploads the file, **Then** the system rejects the operation, halts persistence, and returns structured error code `at_least_one_quantity_must_be_positive` with message «حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد».

---

### User Story 2 - Weekly Cumulative Material Balance Sheet in Excel (Priority: P1)

As a project manager, site supervisor, or inventory auditor, I want to export the weekly department activity report workbook where the 8th worksheet is a dedicated "Cumulative Material Balance Sheet" aggregating movements by material type and unit, computing opening balances prior to the week, total weekly inputs and outputs, and providing native spreadsheet formulas for closing balance and column totals, so that material stock, consumption rates, and site shortages can be audited without manual arithmetic.

**Why this priority**: Construction projects require continuous reconciliation between delivered materials and consumed quantities. The weekly balance sheet is the core auditing deliverable submitted to executive management and client consultants.

**Independent Test**: In a project with existing material movements prior to the target week and active movements during the week, trigger the weekly report export for the warehouse department. Open the generated spreadsheet, inspect sheet 8 ("بالانس تجمعی مصالح"), and verify the presence of opening balance, weekly inputs, weekly outputs, dynamic closing formula `=D{row}+E{row}-F{row}`, and column sum formulas.

**Acceptance Scenarios**:

1. **Given** warehouse movements exist across past and current weeks, **When** the weekly Excel report is requested for the warehouse department, **Then** the 8th worksheet is titled «بالانس تجمعی مصالح» (Cumulative Material Balance) and aggregates all items by `(material_type, unit)` rather than supplier breakdown.
2. **Given** sheet 8 of the weekly report, **When** an auditor inspects each material row, **Then** column 4 displays the Opening Balance (computed as all inbound minus all outbound prior to the week start date), column 5 displays Total Weekly Inbound, column 6 displays Total Weekly Outbound, and column 7 displays Closing Balance containing the native formula `=D{row}+E{row}-F{row}`.
3. **Given** a material type was delivered in prior weeks (with positive historical balance) but has zero new transactions in the selected week, **When** the weekly balance sheet is generated, **Then** that material still appears in the balance sheet displaying its valid opening balance and an identical closing balance.
4. **Given** the bottom summary row of the balance sheet, **When** opened in any compatible spreadsheet software, **Then** the totals for Opening Balance, Total Inbound, Total Outbound, and Closing Balance are computed using native `=SUM(...)` formulas.

---

### User Story 3 - Daily Warehouse Report with Shiraz Site Format & Net Daily Balance (Priority: P1)

As a project manager or site warehouse keeper, I want to download the daily warehouse report formatted to Shiraz construction site standards, featuring official Persian headers and a dedicated summary section calculating the Net Daily Balance (`=Total_In - Total_Out`), so that daily material absorption versus consumption is clearly visible on the official sign-off sheet.

**Why this priority**: Shiraz regional construction contracts require standard daily inventory sign-off sheets that clearly separate total daily intake from disbursements and show whether site net inventory grew or shrank that day.

**Independent Test**: Download the daily activity report for the warehouse department for a day with recorded inflows and outflows. Inspect the spreadsheet header and footer to verify the official Shiraz title and the two-tiered footer showing Total In, Total Out, and Net Daily Flow (`=In - Out`) with distinct highlight formatting.

**Acceptance Scenarios**:

1. **Given** warehouse records recorded on a specific date, **When** the user clicks "دانلود گزارش روزانه انبار (شیراز)", **Then** an RTL spreadsheet is downloaded with sheet title and main banner reading «گزارش روزانه گردش مصالح و انبار کارگاه — پروژه {proj_name}».
2. **Given** the bottom calculation rows of the daily report, **When** the table concludes, **Then** the first summary row displays `=SUM(D5:D{n})` for total inbound and `=SUM(F5:F{n})` for total outbound.
3. **Given** the daily report summary footer, **When** the net daily balance row is inspected, **Then** it presents the title «تراز خالص گردش مصالح روز (خالص افزایش / کاهش موجودی):» with native formula `=D{sum_row}-F{sum_row}` formatted with bold emphasis and prominent borders.

---

### User Story 4 - Real-Time Material Balance Query Endpoint (Priority: P2)

As a technical office engineer or project administrator, I want to query the current warehouse stock balance for all materials in a project via a fast, authenticated web service, optionally filtering by cutoff date or searching material names, so that client applications and third-party dashboards can display real-time stock levels without parsing Excel files.

**Why this priority**: Enables headless inspection, live stock indicators, and programmatic verification of inventory levels across site departments.

**Independent Test**: Make an authenticated HTTP GET request to `/api/v1/projects/{project_id}/department-activity-records/warehouse-balance/` with test data. Verify the response contains a JSON list of items grouped by `(material_type, unit)` with accurate `total_in`, `total_out`, `current_balance`, and `last_movement_date`.

**Acceptance Scenarios**:

1. **Given** an authenticated project member with report viewing permission (`view_reports`), **When** sending a GET request to the warehouse balance endpoint for a project, **Then** the server returns HTTP 200 with an array of material balance summaries containing material name, unit, total inbound, total outbound, current balance, and latest transaction date.
2. **Given** the `as_of_date` query parameter (e.g., `?as_of_date=2026-10-15`), **When** the query is evaluated, **Then** all receipts and dispatches after that date are excluded from the calculated balance.
3. **Given** a `search` query parameter (e.g., `?search=سیمان`), **When** the query is executed, **Then** only materials whose `material_type` contains the search term (case-insensitive and Arabic/Persian letter agnostic) are returned.
4. **Given** a user who is not a member of the project or lacks `view_reports` permission, **When** attempting to access the endpoint, **Then** the server denies access with HTTP 403 Forbidden.

---

### User Story 5 - Enhanced Warehouse UI Experience & Action Button Disambiguation (Priority: P2)

As a warehouse clerk using the web application, I want material quantities in the warehouse activity table to display with standard thousands separators, action buttons to explicitly reflect Shiraz daily report and weekly cumulative balance sheets, and form error alerts to display Persian error descriptions, so that reading figures and selecting the right export action is intuitive and error-free.

**Why this priority**: Dense numeric tables without digit grouping lead to reading mistakes (e.g. confusing 10,000 bags with 1,000 bags). Generic button labels also cause confusion between generic department reports and specialized warehouse balance workbooks.

**Independent Test**: Navigate to the warehouse department page. Verify inbound and outbound columns format numbers with commas (e.g. `1,500.00`). Verify the download buttons read «دانلود گزارش روزانه انبار (شیراز)» and «دانلود گزارش هفتگی و بالانس تجمعی مصالح (۸ شیت)». Submit an empty quantity in the modal and confirm the Persian error message appears.

**Acceptance Scenarios**:

1. **Given** warehouse activity records displayed in the table, **When** rendered on screen, **Then** `quantity_in` and `quantity_out` values are formatted with locale-appropriate thousands separators (e.g., `1,250` or `1,250.00`).
2. **Given** the warehouse department view, **When** examining the report export buttons, **Then** the buttons display distinctive labels «دانلود گزارش روزانه انبار (شیراز)» and «دانلود گزارش هفتگی و بالانس تجمعی مصالح (۸ شیت)» instead of generic department log labels.
3. **Given** a user submits a modal form with both quantities zero or negative, **When** the API responds with `at_least_one_quantity_must_be_positive`, **Then** the modal displays an inline alert with the exact message «حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد».

---

### User Story 6 - Decision Tree State Machine Completeness (Priority: P3)

As a solution architect, product auditor, or AI agent navigating the repository, I want the decision tree under `docs/decision-tree/login/submit-valid-credentials/[open-legacy-project]/[open-warehouse-department]/` to document all warehouse decision nodes, including the Shiraz daily report format, the 8th weekly cumulative balance sheet, error guards, and the new warehouse balance web query node, so that user journeys and permission gates are completely specified.

**Why this priority**: In accordance with the repository constitution and decision tree rules, every state transition, authorization boundary, and report action must have corresponding documentation in the decision tree.

**Independent Test**: Inspect the decision tree directory structure and README files under `[open-warehouse-department]/`. Confirm that `download-weekly-activity-report/README.md`, `download-daily-activity-report/README.md`, and `[create-activity-record]/README.md` are updated, and `[query-warehouse-balance]/README.md` exists with full permission and state documentation.

**Acceptance Scenarios**:

1. **Given** the decision tree at `docs/decision-tree/.../[open-warehouse-department]/`, **When** auditing `download-weekly-activity-report/README.md`, **Then** it explicitly details the 8th sheet Cumulative Material Balance structure, column breakdown, and native closing balance formula `=Opening + In - Out`.
2. **Given** `download-daily-activity-report/README.md`, **When** audited, **Then** it specifies the Shiraz site title format and the daily net balance calculation `=Total_In - Total_Out`.
3. **Given** `[create-activity-record]/README.md`, **When** audited, **Then** it documents the `at_least_one_quantity_must_be_positive` validation guard and Persian error text.
4. **Given** the balance query endpoint, **When** mapped in the decision tree, **Then** a new bracketed node `[query-warehouse-balance]/README.md` documents permissions (`view_reports`, `CanViewBusinessAssignments`), input parameters, output schema, and transitions.

---

### Edge Cases

- **Negative Quantities**: What happens if a user submits negative numbers for `quantity_in` or `quantity_out`? The system immediately rejects the record with a validation error; quantities must be $\ge 0$.
- **Both Quantities Zero**: What happens if both `quantity_in=0` and `quantity_out=0`? The system rejects the mutation and returns error code `at_least_one_quantity_must_be_positive` with the Persian message.
- **Both Quantities Positive in Same Record**: What happens if a single transaction records both receipt and immediate transfer (`quantity_in > 0` and `quantity_out > 0`)? The system allows this valid operational event; both values are stored and accounted for in the cumulative balance.
- **Material with Past Activity but Zero Current Week Activity**: Does an item with prior inventory appear in the weekly balance sheet if no transactions occurred this week? Yes, it appears in sheet 8 with its computed Opening Balance, zero Inbound, zero Outbound, and Closing Balance equal to Opening Balance.
- **Negative Running Balance (Overshipment / Data Entry Lag)**: What happens if disbursements exceed recorded receipts (Closing Balance < 0)? The native Excel formula correctly computes the negative number and displays it; the balance web service returns the computed decimal without crashing.
- **Different Units for Same Material Name**: What happens if "Cement" is recorded in "بسته‌های 50 کیلویی" in some records and "تن" in others? Because grouping is strictly by `(material_type, unit)`, the system generates two separate, internally consistent balance rows rather than improperly adding bags to metric tons.
- **Empty Inventory / No Records**: What happens when downloading reports or querying balance for a project with no warehouse records? The system produces a valid, clean spreadsheet with headers and formula cells evaluating to 0, or returns an empty JSON list (`[]`) with HTTP 200.
- **Unauthorized Tenant / Cross-Project Access**: What happens if a user tries to query warehouse balance for a project they do not belong to? The system blocks access with HTTP 403 Forbidden, enforcing project boundary isolation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST enforce that every warehouse department activity record contains valid entries for: `date`, `material_type`, `unit`, and `supplier` or `consumption_location` as appropriate.
- **FR-002**: The system MUST validate that at least one of `quantity_in` or `quantity_out` is strictly greater than zero ($> 0$), and neither quantity is negative ($< 0$).
- **FR-003**: When both `quantity_in` and `quantity_out` are less than or equal to zero, the system MUST halt processing and return the structured error code `at_least_one_quantity_must_be_positive` accompanied by the exact Persian message: «حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد».
- **FR-004**: The error code `at_least_one_quantity_must_be_positive` and its Persian description MUST be enforced consistently across all mutation channels: single record creation/update API, bulk Excel import processing, and modal forms.
- **FR-005**: In the weekly Excel activity report workbook for the warehouse department, the 8th worksheet MUST be generated under the title «بالانس تجمعی مصالح» (Cumulative Material Balance).
- **FR-006**: The 8th worksheet MUST aggregate warehouse records by unique `(material_type, unit)` tuples across the project, independent of supplier breakdown.
- **FR-007**: The 8th worksheet MUST compute the Opening Balance for each `(material_type, unit)` by summing all historical inbound quantities and subtracting all historical outbound quantities recorded strictly prior to the selected `week_start` date.
- **FR-008**: The 8th worksheet MUST display every material having historical records or prior opening balance in the project, even if zero movements occurred during the selected week.
- **FR-009**: The 8th worksheet MUST include columns:
  1. ردیف (Row index)
  2. نوع مصالح (Material Type)
  3. واحد (Unit of Measure)
  4. موجودی اول دوره (Opening Balance)
  5. کل ورودی دوره (Total Inbound during week)
  6. کل خروجی دوره (Total Outbound during week)
  7. مانده پای کار / موجودی پایان دوره (Closing Balance)
  8. توضیحات و وضعیت اقلام (Notes / Item Status)
- **FR-010**: The Closing Balance column in the 8th worksheet MUST contain the native spreadsheet formula `=D{row}+E{row}-F{row}` so that downstream users can audit calculations dynamically.
- **FR-011**: The 8th worksheet MUST provide a final summary row computing totals for Opening Balance, Total Inbound, Total Outbound, and Closing Balance using native `=SUM(...)` formulas.
- **FR-012**: In the daily Excel activity report for the warehouse department, the workbook MUST be formatted according to Shiraz construction site standards, featuring the official sheet header «گزارش روزانه گردش مصالح و انبار کارگاه — پروژه {proj_name}».
- **FR-013**: The daily report MUST include a two-tiered calculation footer:
  1. Tier 1: Total Inbound (`=SUM(D5:D{n})`) and Total Outbound (`=SUM(F5:F{n})`).
  2. Tier 2: Daily Net Balance («تراز خالص گردش مصالح روز (خالص افزایش / کاهش موجودی):») using native formula `=D{sum_row}-F{sum_row}` formatted with bold emphasis and prominent borders.
- **FR-014**: The system MUST provide an authenticated HTTP GET endpoint at `/api/v1/projects/{project_pk}/department-activity-records/warehouse-balance/` accessible to users with project `view_reports` permission.
- **FR-015**: The balance endpoint MUST return a list of items aggregated by `(material_type, unit)` containing: material type, unit of measure, total inbound quantity, total outbound quantity, net current balance, and latest movement date.
- **FR-016**: The balance endpoint MUST support an optional `as_of_date` query parameter (defaulting to the current date) that restricts balance computation to records on or before that date.
- **FR-017**: The balance endpoint MUST support an optional `search` query parameter that filters results by material name using case-insensitive, locale-normalized matching.
- **FR-018**: The web frontend table for the warehouse department MUST format numeric values in the inbound and outbound columns using localized thousands separators (e.g. `#,##0.00`).
- **FR-019**: The web frontend for the warehouse department MUST provide distinct, descriptive action button labels:
  - «دانلود گزارش روزانه انبار (شیراز)»
  - «دانلود گزارش هفتگی و بالانس تجمعی مصالح (۸ شیت)»
- **FR-020**: The web frontend creation and edit modals MUST capture the `at_least_one_quantity_must_be_positive` server error code and render the server-provided Persian error message clearly to the user.
- **FR-021**: The repository decision tree under `docs/decision-tree/login/submit-valid-credentials/[open-legacy-project]/[open-warehouse-department]/` MUST be updated to document the Shiraz daily report, the 8th sheet weekly balance, the positive quantity error code, and the new `[query-warehouse-balance]` decision node.

### Key Entities

- **Warehouse Movement Record**: An atomic transaction representing the receipt, dispatch, or internal transfer of materials on a construction site. Attributes include: `date`, `material_type`, `quantity_in`, `quantity_out`, `unit`, `supplier`, `consumption_location`, `description`.
- **Cumulative Material Balance Summary**: An aggregated view of warehouse inventory for a specific project and `(material_type, unit)` pair, tracking historical receipts, historical disbursements, opening balance for a given timeframe, current stock on site, and last active transaction date.
- **Shiraz Daily Warehouse Report**: A single-day official site ledger formatted for Shiraz construction practices, displaying 8-column itemized movements and a dual-tier footer detailing total receipts, total disbursements, and daily net material variance.
- **Weekly Cumulative Balance Workbook**: An 8-worksheet Excel workbook where sheets 1 through 7 represent daily site logs (Saturday through Friday) and sheet 8 represents the full project material balance sheet with dynamic accounting formulas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of warehouse record submissions with both inbound and outbound non-positive ($\le 0$) are rejected with HTTP 400, returning error code `at_least_one_quantity_must_be_positive` and the exact approved Persian text.
- **SC-002**: 100% of generated weekly warehouse Excel workbooks contain the 8th worksheet titled «بالانس تجمعی مصالح» with valid native formulas `=D{row}+E{row}-F{row}` in every row of the closing balance column.
- **SC-003**: 100% of materials with existing inventory prior to the selected week appear in the weekly balance sheet with their correct opening balance, even when zero transactions took place during that week.
- **SC-004**: 100% of generated daily warehouse Excel reports display the Shiraz site banner and include the native Daily Net Balance formula `=D{sum_row}-F{sum_row}`.
- **SC-005**: Warehouse stock balance inquiries for projects with up to 5,000 recorded movements display results in under 1 second.
- **SC-006**: In the web UI, warehouse numerical values display standard digit grouping, and report download buttons clearly identify Shiraz daily format and weekly cumulative balance sheets.
- **SC-007**: 100% of relevant decision tree nodes in `docs/decision-tree/.../[open-warehouse-department]/` are synchronized with the actual routes, permissions, formulas, and error codes.

## Assumptions

- **Department Isolation**: These balance calculations, Shiraz formatting, and the `at_least_one_quantity_must_be_positive` validation apply specifically to the `warehouse` department. Non-warehouse departments retain their existing generic activity log fields (`executed_quantity`, `location`, `contractor`) and summary logic.
- **Calendar Basis**: Weekly workbooks continue to follow the standard Iranian Saturday-to-Friday calendar week (`week_start` on Saturday).
- **Material Matching**: Material identity is governed by exact string matching on `(material_type, unit)` (after whitespace normalization). Materials with the same name but different units are intentionally listed as separate balance rows.
- **Formula vs. Cached Value**: Spreadsheet consumers require native formulas so that manual adjustments or offline recalculations in Excel/LibreOffice behave predictably.
- **Authorization**: Access to the warehouse balance endpoint requires the standard project-level `view_reports` permission alongside project membership (`IsProjectMember`, `HasProjectPermission`).
- **Data Retention & Integrity**: Deleting or editing past movement records alters subsequent opening balance calculations dynamically; no stale denormalized snapshot is persisted without dynamic recalculation.
