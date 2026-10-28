# Technical Research: Department Activity Reports & Excel Workbooks

**Feature Branch**: `042-department-activity-reports`  
**Date**: 2026-10-28  
**Spec Reference**: `specs/042-department-activity-reports/spec.md`  
**Standards**: `reports_documentation/atomic-specs/SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md`, `reports_gaps/09/GAP-SPEC-09-DEPARTMENT-ACTIVITY-REPORTS.md`

---

## 1. Technology Choices & Libraries

### 1.1 Excel Generation Engine: `openpyxl`
- **Current State**: The legacy implementation generated PDF files via ReportLab for daily and weekly reports, while only using openpyxl in `write_only=True` mode for basic unstyled exports.
- **Selection**: `openpyxl` is already a core dependency (`openpyxl==3.1.5` in `apps/api/requirements.txt`).
- **Capabilities Required**:
  1. **Right-to-Left (RTL) Orientation**: Excel worksheets must have sheet view RTL enabled:
     ```python
     ws.sheet_view.rightToLeft = True
     ```
  2. **Styling & Persian Typography**:
     - Fonts: Font family preference `'Vazirmatn', 'Tahoma', 'Segoe UI', sans-serif`.
     - Header block: Navy primary background (`#1E3A8A` or `#2563EB`) with white bold text, centered alignment, and thin borders.
     - Zebra striping: Alternating light fill (`#F8FAFC` vs `#FFFFFF`) for data rows.
     - Number formats: Decimal quantity format `#,##0.000` or `0.000` and date format `YYYY-MM-DD`.
  3. **Spreadsheet Formulas (`=SUM(...)`)**:
     - `openpyxl` writes formula strings directly: `cell.value = f"=SUM(E{start_row}:E{end_row})"`
     - Dynamic cross-sheet formulas for weekly summary:
       `=SUM('شنبه'!E{row}, 'یکشنبه'!E{row}, ...)` or summing across daily sheets.

### 1.2 Date & Calendar Calculations (Persian Saturday-to-Friday Work Week)
- **Persian Week Alignment**: In the Iranian civil and construction calendar, the standard work week starts on **Saturday** (شنبه) and ends on **Friday** (جمعه).
- **Date Handling**:
  - `date`: Accepts Gregorian ISO format `YYYY-MM-DD` and optional Jalali format via `common.jalali.parse_date_optional`.
  - `week_start`: Represents the Saturday date. If an arbitrary date is provided, the backend can either accept it as the week anchor or normalize to the preceding Saturday if requested, with `week_start` defining the 7-day window `[week_start, week_start + 6 days]`.
  - Day sheets:
    1. شنبه (Saturday) - `day 0`
    2. یکشنبه (Sunday) - `day 1`
    3. دوشنبه (Monday) - `day 2`
    4. سه‌شنبه (Tuesday) - `day 3`
    5. چهارشنبه (Wednesday) - `day 4`
    6. پنجشنبه (Thursday) - `day 5`
    7. جمعه (Friday) - `day 6`
    8. خلاصه هفتگی (Weekly Summary)

---

## 2. Architecture & Data Integrity Decisions

### 2.1 Model Migration & `executed_quantity`
- In `DepartmentActivityRecord`:
  ```python
  executed_quantity = models.DecimalField(
      max_digits=12,
      decimal_places=3,
      null=True,
      blank=True,
      default=Decimal('0.000'),
      verbose_name=_('Executed Quantity'),
  )
  ```
- **Warehouse vs Non-Warehouse Distinction**:
  - Warehouse records: track `quantity_in` and `quantity_out` with `material_type` and `supplier`.
  - Non-warehouse (`buildings`/`civil`, `electrical`, `mechanical`, `machinery`): track `executed_quantity`, `unit`, `location`, `contractor`, `activity_description`.
  - In serialization and validation, non-warehouse departments store non-negative `executed_quantity` (defaulting to 0.000 if blank or null).

### 2.2 Department Slug Normalization (`civil` <-> `buildings`)
- The backend choice in `inventory.models.Department` was historically `buildings`, while SPEC-09 and frontend routes frequently refer to `civil`.
- **Decision**:
  - Normalize slug in service layer and viewsets:
    ```python
    def normalize_department(dept: str | None) -> str | None:
        if not dept:
            return None
        dept_clean = dept.strip().lower()
        if dept_clean == 'civil':
            return 'buildings'
        return dept_clean
    ```
  - Also ensure queries for `civil` or `buildings` filter with `department__in=['buildings', 'civil']` so records created under either legacy or canonical representation are retrieved interchangeably.
  - Return HTTP 200 for both `?department=civil` and `?department=buildings`.

### 2.3 Strict Atomic Batch Import & Persian Diagnostics
- **Previous Flaw**: Rows were inserted iteratively without transaction encapsulation. Errors in row 4 left rows 2-3 committed.
- **Atomic Solution**:
  - Encapsulate whole file processing in `@transaction.atomic`.
  - Two-phase validation:
    1. Parse workbook and validate header mapping.
    2. Validate all rows: check date format, resolve contractor by name or UUID strictly within current `project_id`, validate positive decimal for `executed_quantity`, and validate non-blank activity description and location.
    3. Accumulate errors. If any error is found in *any* row:
       - Abort transaction (or raise `ValidationError`).
       - Return HTTP 400 Bad Request with:
         ```json
         {
           "detail": "خطا در سطر ۴: مقدار اجرا باید عددی معتبر و نامنفی باشد",
           "errors": [
             {
               "row": 4,
               "field": "executed_quantity",
               "message": "مقدار اجرا باید عددی معتبر و نامنفی باشد"
             }
           ]
         }
         ```
       - Database commits 0 rows.
    4. If 100% valid, `bulk_create` (or create in atomic block) and return HTTP 200 with:
       ```json
       {
         "created": 25,
         "detail": "تعداد ۲۵ رکورد فعالیت با موفقیت ثبت شد."
       }
       ```

### 2.4 Authorization Elevation
- `DepartmentActivityImportView` inherits permissions from `_DepartmentActivityDataBase` which previously defaulted to `required_permission = 'view_reports'`.
- **Change**: Explicitly set `required_permission = 'edit_reports'` on `DepartmentActivityImportView`.
- Any user without `edit_reports` (e.g., viewers) receives HTTP 403 Forbidden.

---

## 3. Spreadsheet Design Details

### 3.1 Single-Day Report (`reports/daily/`)
- Sheet title: Persian name of department (e.g. `گزارش ابنیه`)
- Sheet RTL: `ws.sheet_view.rightToLeft = True`
- Header Block (Rows 1–3):
  - Row 1: Merged title block: `گزارش روزانه دپارتمان {department_label} — {project_name}`
  - Row 2: Metadata: `تاریخ: {persian_date} ({gregorian_date})` | `پروژه: {project_name}` | `کد کارگاه: {project_code}`
  - Row 3: Blank separator
- Table Header (Row 4):
  - ردیف (Row No)
  - شرح فعالیت (Activity Description)
  - پیمانکار (Contractor)
  - جبهه کاری / موقعیت (Location)
  - مقدار اجرا (Executed Quantity)
  - واحد (Unit)
  - توضیحات (Description)
- Data Rows (Rows 5 to N):
  - Rendered with cell borders and Persian font.
- Summary Row (Row N+1):
  - Merged columns A–D: `مجموع احجام اجرایی روز:` (Bold, background `#E2E8F0`)
  - Column E (Executed Quantity): `=SUM(E5:E{N})`
  - Columns F–G: Blank/Merged with border.

### 3.2 Weekly Report (`reports/weekly/`)
- Exactly 8 worksheets:
  1. `شنبه`
  2. `یکشنبه`
  3. `دوشنبه`
  4. `سه‌شنبه`
  5. `چهارشنبه`
  6. `پنجشنبه`
  7. `جمعه`
  8. `خلاصه هفتگی`
- Each daily sheet contains that specific day's records and its own `=SUM(E5:E{N})`.
- The `خلاصه هفتگی` sheet consolidates:
  - Table of activities/contractors across the week.
  - Columns: `ردیف`, `شرح فعالیت / پیمانکار`, `شنبه`, `یکشنبه`, `دوشنبه`, `سه‌شنبه`, `چهارشنبه`, `پنجشنبه`, `جمعه`, `مجموع کل هفته`.
  - The `مجموع کل هفته` column uses `=SUM(C{row}:I{row})`.
  - The bottom row uses `=SUM(...)` to total each day and the full week.

---

## 4. Frontend Integration Decisions

- In `department-page.tsx`:
  - Replace `.pdf` report downloads with modal/popover dialogs allowing date/week selection:
    - Daily Report Modal: Jalali date selector, triggers `GET .../reports/daily/?department={dept}&date={YYYY-MM-DD}` saving `{department}_daily_report_{date}.xlsx`.
    - Weekly Report Modal: Week start date selector, triggers `GET .../reports/weekly/?department={dept}&week_start={YYYY-MM-DD}` saving `{department}_weekly_report_{week_start}.xlsx`.
  - Filtered Export: Exports current filtered table rows directly as styled RTL `.xlsx`.
  - Import dialog: Catches atomic error responses and displays `err.response?.data?.detail` in red alert banner.
- In `department-activity-record-modal.tsx`:
  - Add `executed_quantity` numeric input field for non-warehouse departments with Persian label `مقدار اجرا` and 3 decimal precision.
