# Data Model & Query Specification: Warehouse Department Reports

**Feature Branch**: `043-warehouse-department-reports`  
**Date**: 2026-10-28  
**Status**: Completed  

---

## 1. Domain Entities & Schemas

### 1.1. Underlying Entity: `DepartmentActivityRecord`
The existing `DepartmentActivityRecord` model stored in `inventory.models` persists material transactions for `department="warehouse"`.

| Field Name | Type | Constraints | Description |
|:---|:---|:---|:---|
| `id` | `BigAutoField` | PK | Record ID |
| `project` | `ForeignKey(Project)` | Indexed, `on_delete=CASCADE` | Project boundary |
| `department` | `CharField(32)` | `'warehouse'` | Department classifier |
| `date` | `DateField` | Indexed, Not Null | Transaction date |
| `material_type` | `CharField(255)` | Not Null | Material identifier (e.g. «سیمان تیپ 2») |
| `unit` | `CharField(64)` | Not Null | Unit of measure (e.g. «کیسه 50 کیلویی») |
| `quantity_in` | `DecimalField(14, 3)` | Default 0.000, $\ge 0$ | Material received |
| `quantity_out` | `DecimalField(14, 3)` | Default 0.000, $\ge 0$ | Material dispatched |
| `consumption_location` | `CharField(255)` | Optional | Where material is consumed |
| `supplier` | `CharField(255)` | Optional | Source supplier or carrier |
| `description` | `TextField` | Optional | Bill of lading / receipt notes |
| `created_at` / `updated_at` | `DateTimeField` | Auto | Audit timestamps |

---

## 2. Dynamic Opening Stock Calculation

### 2.1. Logic & Mathematical Formulation
For a project $P$ and cutoff date $D_{start} = \text{week\_start}$:
$$\text{OpeningStock}(P, m, u) = \sum_{r \in R_{\text{prior}}} r.\text{quantity\_in} - \sum_{r \in R_{\text{prior}}} r.\text{quantity\_out}$$
where $R_{\text{prior}} = \{r \in \text{Records} \mid r.project = P \land r.department = \text{'warehouse'} \land r.date < D_{start} \land r.material = m \land r.unit = u\}$.

### 2.2. Query Specification
```python
prior_qs = (
    DepartmentActivityRecord.objects.filter(
        project_id=project_pk,
        department='warehouse',
        date__lt=week_start,
    )
    .values('material_type', 'unit')
    .annotate(
        total_in=Coalesce(Sum('quantity_in'), Value(Decimal('0'))),
        total_out=Coalesce(Sum('quantity_out'), Value(Decimal('0'))),
    )
)
```

---

## 3. Cumulative Material Balance Sheet (Weekly Report - Sheet 8)

### 3.1. Structure of Sheet 8 («بالانس تجمعی مصالح»)
Aggregates all material movements for the week alongside opening balances, grouped strictly by `(material_type.strip(), unit.strip())`.

| Col | Header (Persian) | Source / Calculation | Format / Formula |
|:---:|:---|:---|:---|
| **A** | ردیف | Row index ($1, 2, \dots$) | Center, Integer |
| **B** | نوع مصالح | `material_type` | Right, Text |
| **C** | واحد | `unit` | Center, Text |
| **D** | موجودی اول دوره | `opening_balance` ($\text{In} - \text{Out}$ before `week_start`) | Center, Numeric `#,##0.000` |
| **E** | کل ورودی دوره | $\sum \text{quantity\_in}$ during week | Center, Numeric `#,##0.000` |
| **F** | کل خروجی دوره | $\sum \text{quantity\_out}$ during week | Center, Numeric `#,##0.000` |
| **G** | مانده پای کار / موجودی پایان دوره | Computed Closing Stock | Native Formula: `=D{row}+E{row}-F{row}` |
| **H** | توضیحات و وضعیت اقلام | Notes or balance status | Right, Text |

### 3.2. Summary Row
At row $S = \text{last\_row} + 1$:
- Columns A–C merged: `مجموع کل گردش مصالح انبار:`
- Column D: `=SUM(D5:D{S-1})`
- Column E: `=SUM(E5:E{S-1})`
- Column F: `=SUM(F5:F{S-1})`
- Column G: `=SUM(G5:G{S-1})`

---

## 4. Daily Warehouse Report (Shiraz Format)

### 4.1. Header & Title Banner
- Row 1: `گزارش روزانه گردش مصالح و انبار کارگاه — پروژه {proj_name}`
- Row 2: `تاریخ گزارش: {date_fa} ({date_iso}) | کد کارگاه: {proj_code}`
- Row 4: Column headers (9 columns)

### 4.2. Footer Calculations
- **Summary Row 1 (Tier 1 Totals)**:
  - Columns 1–3 merged: `مجموع ورودی روز:`
  - Column 4: `=SUM(D5:D{r-1})`
  - Column 5: `مجموع خروجی روز:`
  - Column 6: `=SUM(F5:F{r-1})`
- **Summary Row 2 (Tier 2 Net Daily Balance)**:
  - Columns 1–5 merged: `تراز خالص گردش مصالح روز (خالص افزایش / کاهش موجودی):`
  - Column 6: `=D{tot_row}-F{tot_row}`
  - Style: Highlighted background, bold font, all borders.

---

## 5. Warehouse Stock Balance Web Service

### 5.1. DTO / Response Structure
```typescript
interface WarehouseBalanceItem {
  material_type: string;
  unit: string;
  total_in: number;
  total_out: number;
  current_balance: number;
  last_movement_date: string | null;
}
```

### 5.2. Query Pipeline
```python
qs = DepartmentActivityRecord.objects.filter(
    project_id=project_pk,
    department='warehouse',
    date__lte=as_of_date,
)
if search:
    qs = qs.filter(material_type__icontains=search.strip())

items = (
    qs.values('material_type', 'unit')
    .annotate(
        total_in=Coalesce(Sum('quantity_in'), Value(Decimal('0'))),
        total_out=Coalesce(Sum('quantity_out'), Value(Decimal('0'))),
        last_movement_date=Max('date'),
    )
    .order_by('material_type', 'unit')
)
```
Result serialization computes:
`current_balance = item['total_in'] - item['total_out']`.

---

## 6. Validation Error Model

When `quantity_in <= 0 and quantity_out <= 0`:
```json
{
  "error": {
    "code": "at_least_one_quantity_must_be_positive",
    "message": "حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد",
    "details": {
      "quantity_in": ["حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد"],
      "quantity_out": ["حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد"]
    }
  }
}
```
In Excel batch import:
```json
{
  "error": {
    "code": "at_least_one_quantity_must_be_positive",
    "message": "خطا در سطر ۲: حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد",
    "details": [
      {
        "row": 2,
        "code": "at_least_one_quantity_must_be_positive",
        "errors": {
          "quantity_in": "حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد",
          "quantity_out": "حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد"
        }
      }
    ]
  },
  "created": 0,
  "errors": [...]
}
```
