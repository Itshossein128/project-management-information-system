# Phase 0 Research: Warehouse Department Reports

**Feature Branch**: `043-warehouse-department-reports`  
**Date**: 2026-10-28  
**Status**: Completed  

---

## 1. Technology Choices & Frameworks

- **Backend**: Python 3.12, Django 4.2.11, Django REST Framework (DRF) 3.14.
- **Spreadsheet Generation**: `openpyxl` (version 3.1.2+).
- **Frontend**: React Router 7, Vite, TypeScript 5+, Tailwind CSS, Radix UI.
- **Validation**: DRF `CodedValidationError` inheriting from `rest_framework.exceptions.ValidationError`.

---

## 2. Openpyxl Formula Syntax & Workbook Construction

### 2.1. Weekly Report Sheet 8: Cumulative Material Balance («بالانس تجمعی مصالح»)
- **Sheet Index**: 8th worksheet (following Saturday through Friday sheets).
- **Sheet Properties**: RTL mode enabled (`ws.sheet_view.rightToLeft = True`).
- **Columns (8 columns)**:
  - Column A: ردیف (`Row Index`)
  - Column B: نوع مصالح (`Material Type`)
  - Column C: واحد (`Unit`)
  - Column D: موجودی اول دوره (`Opening Balance`)
  - Column E: کل ورودی دوره (`Total Inbound`)
  - Column F: کل خروجی دوره (`Total Outbound`)
  - Column G: مانده پای کار / موجودی پایان دوره (`Closing Balance`)
  - Column H: توضیحات و وضعیت اقلام (`Notes`)
- **Native Excel Formula for Closing Balance**:
  For data row `r`:
  ```excel
  =D{r}+E{r}-F{r}
  ```
- **Native Excel Formulas for Total Summary Row**:
  For total row `s_row`:
  - Column D: `=SUM(D5:D{s_row - 1})`
  - Column E: `=SUM(E5:E{s_row - 1})`
  - Column F: `=SUM(F5:F{s_row - 1})`
  - Column G: `=SUM(G5:G{s_row - 1})`

### 2.2. Daily Report: Shiraz Site Format & Net Daily Balance
- **Title Banner**:
  `گزارش روزانه گردش مصالح و انبار کارگاه — پروژه {proj_name}`
- **Columns (9 columns)**:
  1. ردیف, 2. تاریخ, 3. نوع مصالح, 4. مقدار ورودی, 5. واحد, 6. مقدار خروجی, 7. محل مصرف, 8. تامین‌کننده, 9. توضیحات
- **Calculation Footer (Two-Tiered)**:
  - **Tier 1 (Totals)**:
    - Label (cols 1-3 merged): `مجموع ورودی روز:`
    - Col 4: `=SUM(D5:D{r-1})`
    - Label (col 5): `مجموع خروجی روز:`
    - Col 6: `=SUM(F5:F{r-1})`
  - **Tier 2 (Net Daily Flow)**:
    - Label (cols 1-5 merged): `تراز خالص گردش مصالح روز (خالص افزایش / کاهش موجودی):`
    - Col 6: `=D{r}-F{r}` (where `{r}` is the Tier 1 total row index).
    - Styling: Prominent border, `FONT_TOTAL`, bold, center-aligned.

---

## 3. Dynamic Opening Balance Calculation

### 3.1. Business Rule
Opening stock for any material tuple `(material_type, unit)` prior to `week_start` is defined as:
$$\text{Opening Balance} = \sum_{\text{date} < \text{week\_start}} \text{quantity\_in} - \sum_{\text{date} < \text{week\_start}} \text{quantity\_out}$$

### 3.2. Query Strategy
Using Django ORM aggregation:
```python
from decimal import Decimal
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

prior_aggregates = (
    DepartmentActivityRecord.objects.filter(
        project_id=project_pk,
        department__in=dept_filter,
        date__lt=week_start,
    )
    .values('material_type', 'unit')
    .annotate(
        total_in=Coalesce(Sum('quantity_in'), Value(Decimal('0'))),
        total_out=Coalesce(Sum('quantity_out'), Value(Decimal('0'))),
    )
)
opening_balances = {
    (item['material_type'].strip(), item['unit'].strip()): item['total_in'] - item['total_out']
    for item in prior_aggregates
}
```
All material tuples with `opening_balance != 0` OR having transactions during the week are included in Sheet 8, satisfying FR-007 and FR-008.

---

## 4. Structured Error Handling & Validation Code

### 4.1. Error Code Specification
- Machine-readable code: `at_least_one_quantity_must_be_positive`
- Persian message: `حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد`
- HTTP Status: `400 Bad Request`

### 4.2. DRF Exception Architecture
In DRF, `ValidationError` wraps field errors. To ensure the custom exception handler preserves `at_least_one_quantity_must_be_positive`:
```python
from rest_framework.exceptions import ErrorDetail
from config.exceptions import CodedValidationError

fa_msg = 'حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد'
err_detail = ErrorDetail(fa_msg, code='at_least_one_quantity_must_be_positive')
errors['quantity_in'] = [err_detail]
errors['quantity_out'] = [err_detail]
raise CodedValidationError(errors, code='at_least_one_quantity_must_be_positive')
```

### 4.3. Excel Import Processing
In `import_activities_from_xlsx`:
```python
if quantity_in <= 0 and quantity_out <= 0:
    row_errors['quantity_in'] = 'حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد'
    row_errors['quantity_out'] = 'حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد'
    row_errors['code'] = 'at_least_one_quantity_must_be_positive'
```
And `DepartmentActivityImportView` formats the response containing `error.code = 'at_least_one_quantity_must_be_positive'`.

---

## 5. Warehouse Stock Balance Web Service

### 5.1. Route & Permissions
- URL: `GET /api/v1/projects/{project_pk}/department-activity-records/warehouse-balance/`
- Guard: `IsAuthenticated`, `IsProjectMember`, `HasProjectPermission`, `CanViewBusinessAssignments`, `IsVisitorReadOnly`, `IsHrOrAdminOrReadOnly`
- Permission codename: `view_reports`

### 5.2. Query Parameters
- `as_of_date`: Optional ISO date (`YYYY-MM-DD` or Jalali). If omitted, defaults to `timezone.localdate()`.
- `search`: Optional string for case-insensitive substring search on `material_type`.

### 5.3. Aggregation Algorithm
Group by `(material_type, unit)`:
```python
qs = DepartmentActivityRecord.objects.filter(
    project_id=project_pk,
    department='warehouse',
    date__lte=as_of_date,
)
if search_term:
    qs = qs.filter(material_type__icontains=search_term)

balance_items = (
    qs.values('material_type', 'unit')
    .annotate(
        total_in=Coalesce(Sum('quantity_in'), Value(Decimal('0'))),
        total_out=Coalesce(Sum('quantity_out'), Value(Decimal('0'))),
        last_movement_date=Max('date'),
    )
    .order_by('material_type', 'unit')
)
```
For each item:
`current_balance = total_in - total_out`.

---

## 6. Frontend UX Enhancements

1. **Number Formatting**:
   Format `quantity_in` and `quantity_out` using `Number(val).toLocaleString('fa-IR', { minimumFractionDigits: 0, maximumFractionDigits: 3 })`.
2. **Action Buttons**:
   Display distinct Persian labels for warehouse department:
   - Daily: `دانلود گزارش روزانه انبار (شیراز)`
   - Weekly: `دانلود گزارش هفتگی و بالانس تجمعی مصالح (۸ شیت)`
3. **Modal Error Alert**:
   Capture `err.code === 'at_least_one_quantity_must_be_positive'` and render Persian error message directly.
