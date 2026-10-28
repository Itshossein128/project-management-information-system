# Data Model & Architecture Specification: Shiraz Excel Parity & Official PDF Standardization

## 1. Domain Entities & Value Objects

### 1.1 Shiraz Daily Report Document (`DailyReportExportDocument`)
Represents the exported binary artifact (FILE 4 `.xlsx` or official `.pdf`) generated from a `DailyReport` record.
- **Attributes**:
  - `report_id`: UUID
  - `project_id`: UUID
  - `project_name`: String
  - `contract_number`: String (e.g., `1402/25319/ص`)
  - `report_date`: Jalali & Gregorian Date
  - `day_of_week`: Persian day name (e.g., `یکشنبه`)
  - `shift`: `day` | `night` | `full`
  - `status`: `draft` | `submitted` | `under_review` | `approved` | `rejected`
  - `audit_hash`: 16-character hexadecimal SHA-256 fingerprint
  - `filename`: `daily-report-{report_date}-{shift}.xlsx` or `.pdf`

### 1.2 Shiraz Discipline Sub-Report Export (`DisciplineSubReportExport`)
Represents the exported binary spreadsheet artifact generated from a `DisciplineSubReport` and its `DisciplineSubReportActivity` rows.
- **FILE 5 (Civil / Buildings)**:
  - Header: Contractor company (`شرکت پی‌چین`), form code, revision number, discipline (`اجرای ابنیه`), date, weather.
  - Columns:
    1. `ردیف` (Sequential Integer)
    2. `شیفت` (Shift string or integer)
    3. `پیمانکار / اکیپ` (`crew_name`)
    4. `استادکار` (`foreman_count`)
    5. `کارگر` (`worker_count`)
    6. `قطعه` (`parcel` / `zone`)
    7. `بلوک` (`block`)
    8. `طبقه` (`floor`)
    9. `شرح فعالیت` (`activity_description`)
    10. `واحد` (`unit`)
    11. `مقدار` (`quantity`)
    12. `درصد اجرا` (`execution_percentage`, formatted as `0.0%`)
- **FILE 6 (Electrical)**:
  - Header: Contractor company, discipline (`اجرای تأسیسات برقی`), date, weather.
  - Columns:
    1. `ردیف` (Sequential Integer)
    2. `شیفت` (Integer 1/2/3)
    3. `نام اکیپ / پیمانکار` (`crew_name`)
    4. `استادکار` (`foreman_count`)
    5. `کارگر` (`worker_count`)
    6. `بلوک` (`block`)
    7. `طبقه` (`floor`)
    8. `شرح فعالیت` (`activity_description`)
    9. `واحد` (`unit`)
    10. `مقدار` (`quantity`)
    *(Note: strictly excludes `قطعه` and `درصد اجرا`)*

### 1.3 Shiraz Master Activity Database Export (`ActivityLogExportDocument` / FILE 1)
Represents the flat cumulative activity log exported to Excel.
- Columns:
  1. `ردیف` (Row number)
  2. `تاریخ` (Jalali date)
  3. `شرح فعالیت` (Activity description)
  4. `شیفت` (Shift)
  5. `پیمانکار` (Subcontractor name)
  6. `نفرات` (Worker headcount)
  7. `قطعه` (Parcel / Zone)
  8. `بلوک` (Block)
  9. `طبقه` (Floor)
  10. `موقعیت` (Location detail)
  11. `مقدار` (Executed quantity or `*`)
  12. `واحد` (Measurement unit)

---

## 2. Service Architecture

### 2.1 `ShirazFile4ExcelBuilder`
- **Location**: `apps/api/core/field_reports/shiraz_file4_excel.py`
- **Responsibilities**:
  - Instantiates `openpyxl.Workbook` and sets `ws.sheet_view.rightToLeft = True`.
  - Sets unified project header (rows 1–8).
  - Populates Section A with the 34 fixed Shiraz indirect staff roles, shift 1/2/3 counts, absent counts, and `=SUM(...)` formula.
  - Populates Section B with the 32 fixed Shiraz direct worker roles, shift counts, subtotal `=SUM(...)`, and grand total manpower `=SUM(indirect_subtotal, direct_subtotal)`.
  - Populates Section C (Incoming Materials).
  - Populates Section D (Concrete Casting Volumes).
  - Populates Section E (Machinery & Equipment status and hours).
  - Populates Section F (Daily Executed Activities).
  - Returns `(bytes, filename)`.

### 2.2 `ShirazSubReportExcelBuilder`
- **Location**: `apps/api/core/sub_reports/shiraz_subreport_excel.py`
- **Responsibilities**:
  - Differentiates by `unit` / `discipline`:
    - If `unit == SpecialtyUnit.BUILDINGS` or `discipline == 'civil'`: builds FILE 5 layout with `قطعه` and `درصد اجرا` (formatted `0.0%`).
    - If `unit == SpecialtyUnit.ELECTRICAL` or `discipline == 'electrical'`: builds FILE 6 layout without `قطعه` or `درصد اجرا`.
    - If other units (mechanical, machinery, etc.): builds appropriate standardized sub-report layout.
  - Returns `(bytes, filename)`.

### 2.3 `ActivityLogExcelBuilder`
- **Location**: `apps/api/core/field_reports/shiraz_file1_excel.py`
- **Responsibilities**:
  - Fetches filtered `DailyReportActivity` records.
  - Builds flat spreadsheet matching Shiraz FILE 1 (`ACTIVITY` sheet).
  - Returns `(bytes, filename)`.

### 2.4 PDF Generator Enhancements
- **Location**: `apps/api/core/field_reports/pdf.py`
- **Responsibilities**:
  - Calculates deterministic SHA-256 `audit_hash`.
  - Applies 3-tier signature block at the concluding page.
  - Applies canvas draft watermark callback when `report.status != 'approved'`.
  - Generates standardized attachment filename: `daily-report-{report_date}-{shift}.pdf`.

---

## 3. API Endpoints & View Mappings

| Method | Endpoint | View / Handler | Permission | Description |
|---|---|---|---|---|
| `GET` | `/api/v1/projects/{project_pk}/daily-reports/{id}/excel/` | `DailyReportViewSet.excel` | `view_reports` + `IsProjectMember` | Downloads Shiraz FILE 4 Excel workbook |
| `GET` | `/api/v1/projects/{project_pk}/units/{unit}/daily-reports/{id}/excel/` | `UnitReportViewSet.excel` | `view_reports` + `IsProjectMember` | Downloads FILE 5 (Civil) or FILE 6 (Electrical) Excel |
| `GET` | `/api/v1/projects/{project_pk}/activity-log/excel/` | `ActivityLogExcelView.get` | `view_reports` + `IsProjectMember` | Downloads filtered cumulative activities Excel (FILE 1) |
| `GET` | `/api/v1/projects/{project_pk}/daily-reports/{id}/pdf/` | `DailyReportViewSet.pdf` | `view_reports` + `IsProjectMember` | Downloads standardized PDF with signatures, audit hash, and watermark |
