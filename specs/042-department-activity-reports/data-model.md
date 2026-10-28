# Data Model & Technical Schema: Department Activity Reports

**Feature Branch**: `042-department-activity-reports`  
**Date**: 2026-10-28  

---

## 1. Entity Schema Updates

### 1.1 `DepartmentActivityRecord` (`apps/api/core/inventory/models.py`)

Added field:
```python
executed_quantity = models.DecimalField(
    max_digits=12,
    decimal_places=3,
    null=True,
    blank=True,
    default=Decimal('0.000'),
    verbose_name=_('Executed Quantity'),
    help_text=_('Quantity of work executed for non-warehouse departments.'),
)
```

#### Complete Model Field Summary:
| Field Name | Type | Constraints / Defaults | Purpose |
| :--- | :--- | :--- | :--- |
| `id` | BigAutoField | Primary Key | Record identifier |
| `project` | ForeignKey(Project) | on_delete=CASCADE, indexed | Multi-tenant project boundary |
| `department` | CharField(max_length=32) | choices=Department.choices, indexed | Department (`buildings`/`civil`, `electrical`, etc.) |
| `date` | DateField | indexed | Execution date (Gregorian) |
| `location` | CharField(max_length=255) | blank=True, default='' | Site location / working zone |
| `activity_description` | CharField(max_length=500) | blank=True, default='' | Description of activity performed |
| `contractor` | CharField(max_length=255) | blank=True, default='' | Contractor name |
| `contractor_ref` | ForeignKey(Stakeholder) | SET_NULL, null=True, blank=True | Referenced contractor entity |
| `executed_quantity` | DecimalField(12, 3) | null=True, blank=True, default=0.000 | **NEW**: Non-warehouse volume executed |
| `unit` | CharField(max_length=64) | blank=True, default='' | Unit of measurement (m3, m, kg, etc.) |
| `description` | TextField | blank=True, default='' | Additional notes / observations |
| `material_type` | CharField(max_length=255) | blank=True, default='' | Warehouse: Material description |
| `quantity_in` | DecimalField(14, 3) | default=0 | Warehouse: Inbound quantity |
| `quantity_out` | DecimalField(14, 3) | default=0 | Warehouse: Outbound quantity |
| `consumption_location`| CharField(max_length=255) | blank=True, default='' | Warehouse: Delivery/use location |
| `supplier` | CharField(max_length=255) | blank=True, default='' | Warehouse: Supplier name |
| `unit_report` | ForeignKey(DisciplineSubReport) | SET_NULL, null=True, blank=True | Linked unit report |
| `created_at` | DateTimeField | auto_now_add=True | Timestamp |
| `updated_at` | DateTimeField | auto_now=True | Timestamp |

---

## 2. Department Alias & Normalization Rules

- **Equivalence**: `civil` ≡ `buildings`
- **Inbound Parameters**: Any endpoint accepting `department=civil` or `department=buildings` normalizes the value to the canonical internal choice (`buildings`), but queries the database with `department__in=['buildings', 'civil']` to match both newly saved and existing legacy records.
- **Outbound Responses**: Serialization returns the record's department. If requested as `civil`, client views can represent it as `civil`.

---

## 3. Spreadsheet Workbook Structures

### 3.1 Daily Workbook (`reports/daily/`)
- Single sheet with RTL enabled (`ws.sheet_view.rightToLeft = True`).
- Title row: Merged header with project and department names.
- Columns:
  1. `ردیف` (Row #)
  2. `تاریخ` (Date)
  3. `شرح فعالیت` (Activity Description)
  4. `پیمانکار` (Contractor)
  5. `جبهه کاری / موقعیت` (Location)
  6. `مقدار اجرا` (Executed Quantity)
  7. `واحد` (Unit)
  8. `توضیحات` (Notes)
- Total Row:
  - Label: `مجموع احجام اجرایی:`
  - Value: `=SUM(F5:F{N})` (or column corresponding to Executed Quantity).

### 3.2 Weekly Workbook (`reports/weekly/`)
- Exactly 8 worksheets:
  - Worksheets 1–7: `شنبه`, `یکشنبه`, `دوشنبه`, `سه‌شنبه`, `چهارشنبه`, `پنجشنبه`, `جمعه`
  - Worksheet 8: `خلاصه هفتگی`
- In `خلاصه هفتگی`:
  - Columns: `ردیف`, `شرح فعالیت / پیمانکار`, `شنبه`, `یکشنبه`, `دوشنبه`, `سه‌شنبه`, `چهارشنبه`, `پنجشنبه`, `جمعه`, `مجموع کل هفته`
  - Total column formula: `=SUM(C{row}:I{row})`
  - Grand total row formula: `=SUM(...)`

### 3.3 Filtered Export Workbook (`export/`)
- Single sheet with RTL enabled.
- Persian headers:
  - For non-warehouse: `تاریخ`, `موقعیت / جبهه کاری`, `شرح فعالیت`, `پیمانکار`, `مقدار اجرا`, `واحد`, `توضیحات`
  - For warehouse: `تاریخ`, `نوع مصالح`, `مقدار ورودی`, `واحد`, `مقدار خروجی`, `محل مصرف`, `تامین‌کننده`, `توضیحات`

---

## 4. Batch Import Schema & Atomic Validation

- **Format**: `.xlsx` workbook with single sheet containing column headers on row 1 and data on rows 2+.
- **Accepted Header Aliases**:
  - `date`: `date`, `تاریخ`
  - `location`: `location`, `موقعیت`, `جبهه کاری`
  - `activity_description`: `activity_description`, `شرح فعالیت`, `فعالیت`
  - `contractor`: `contractor`, `پیمانکار`
  - `executed_quantity`: `executed_quantity`, `مقدار اجرا`, `مقدار`, `حجم`
  - `unit`: `unit`, `واحد`
  - `description`: `description`, `توضیحات`, `یادداشت`
- **Validation Pipeline**:
  1. **All-or-Nothing Atomic Wrap**: Entire file processed within `with transaction.atomic():`.
  2. **Row-by-Row Checks**:
     - Date format must parse to valid `date`.
     - `executed_quantity` must parse to positive `Decimal` (>= 0). If string or negative, error recorded.
     - Contractor resolved against active project stakeholders; if invalid or from another project, error recorded.
     - Mandatory fields (`activity_description`, `location`, `contractor`) must not be empty.
  3. **Rollback & Response**:
     - If any errors exist: transaction aborted, return HTTP 400 with first Persian error in `detail` and array of errors in `errors`.
     - If valid: all records saved, return HTTP 200 with count.
