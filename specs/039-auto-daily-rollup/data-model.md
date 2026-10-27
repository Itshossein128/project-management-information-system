# Data Model: Daily Report Auto-Rollup & Activity Master Log Sync

**Feature Branch**: `039-auto-daily-rollup`  
**Date**: 2026-10-28  
**Spec Reference**: `specs/039-auto-daily-rollup/spec.md`

---

## 1. Entity Modifications & Additions

### 1.1 `DailyReportLabor` (`daily_report_labor`)

Extends the existing manpower child table in `field_reports/models.py`.

```text
DailyReportLabor
├── id: UUID (PK)
├── report: ForeignKey(DailyReport, on_delete=CASCADE, related_name='labor_entries', null=True, blank=True)
├── project: ForeignKey('projects.Project', on_delete=CASCADE, null=True, blank=True)
├── report_date: DateField(null=True, blank=True)
├── labor_category: CharField(max_length=10, choices=LaborCategory.choices)
├── job_title: CharField(max_length=120)
├── custom_title: CharField(max_length=120, blank=True, default='')
├── contractor_ref: ForeignKey('projects.Stakeholder', on_delete=SET_NULL, null=True, blank=True, related_name='daily_report_labor_entries')  <-- NEW
├── contractor_name: CharField(max_length=120, blank=True, default='')                                                                       <-- NEW
├── shift_1_count: PositiveIntegerField(default=0)
├── shift_2_count: PositiveIntegerField(default=0)
├── shift_3_count: PositiveIntegerField(default=0)
├── total_count: PositiveIntegerField(default=0)
├── work_hours: DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
├── overtime_hours: DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
├── daily_rate: DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
├── absence_count: PositiveIntegerField(null=True, blank=True)
├── source_set_complete: BooleanField(default=False)
├── source_sub_report: ForeignKey('sub_reports.DisciplineSubReport', on_delete=SET_NULL, null=True, blank=True)
├── source_discipline: CharField(max_length=20, blank=True, default='')
├── is_derived: BooleanField(default=False)
└── is_deleted: BooleanField(default=False)
```

#### Constraints
Update `Meta.constraints`:
- Replace old unique constraint:
  - Old: `fields=['report', 'labor_category', 'job_title']`
  - New: `fields=['report', 'labor_category', 'job_title', 'contractor_ref']` with condition `is_deleted=False, report__isnull=False` (handles multiple contractors with distinct rows; nullable contractor handles direct company labor).

#### Bucketing Logic in Rollup
```python
bucket_key = (
    row.labor_category,
    resolved_code_or_title,
    row.contractor_ref_id,
)
```
- If `row.contractor_ref` is present:
  - `contractor_ref = row.contractor_ref`
  - `contractor_name = row.contractor_ref.name` (or related stakeholder name)
- If `row.contractor_ref` is `None`:
  - `contractor_ref = None`
  - `contractor_name = "نفر شرکت"`

---

### 1.2 `DailyReport` Metadata Extensions

The `DailyReport` model already has `is_auto_summary = BooleanField(default=False)` and `weather_override = BooleanField(default=False)`.
In this feature, the serialization and rollup metadata schema (`aggregation_meta`) is standardized:

```text
AggregationMeta
├── is_auto_summary: Boolean
├── aggregated_at: String (ISO 8601 UTC)
├── aggregated_at_jalali: String (Jalali localized, e.g. "۱۴۰۵/۰۸/۰۶ - ۱۱:۳۰")  <-- NEW
├── is_partial: Boolean
├── expected_disciplines: List[String]
├── contributing_disciplines: List[String]
├── missing_disciplines: List[String]
├── completeness: Object (state: empty|partial|complete, contributing_units, missing_units)
├── weather_source: "overridden_by_manager" | "derived"                       <-- STANDARDIZED
└── site_status_source: "override" | "derived"
```

---

### 1.3 `DailyReportActivity` & Activity Log Projection

`DailyReportActivity` already contains `source_discipline` and `parcel`. The Activity Master Log projection maps these fields directly to Shiraz Excel Sheet 1 (`ACTIVITY`):

```text
ActivityMasterLogRow
├── id: UUIDString
├── report_id: UUIDString
├── report_date: String (Jalali "YYYY/MM/DD")
├── day_name: String (e.g. "دوشنبه" / "Monday")
├── source_discipline: String ("CIVIL", "ELECTRICAL", "MECHANICAL", etc.)       <-- NEW IN EXPORT & LOG
├── parcel: String (Zone/Parcel identifier, e.g. "قطعه ۱۰")                     <-- NEW IN EXPORT & LOG
├── zone: String
├── block: String
├── floor: String
├── location: String
├── activity_description: String
├── shift: String ("shift_1", "shift_2", "shift_3", "full")
├── subcontractor: String (Contractor name or "نفر شرکت")
├── headcount: Integer (Nullable)
├── quantity: Float (Nullable; None indicates unmeasured / "*")
├── unit: String (Nullable)
├── activity_code: String (Nullable)
├── activity_name: String (Nullable)
└── report_status: String ("APPROVED")
```

---

### 1.4 Materials Summary Projection

In `DailyReportDetailSerializer.get_materials_summary(report)`:

```text
MaterialsSummaryResponse
├── main_table: List[DailyReportMaterial] (Resolved Receipts)
├── details: List[DailyReportMaterial] (Issues & Unresolved Receipts)
└── grouped_summary: List[GroupedMaterialSummaryItem]                          <-- NEW
    ├── material_ref_id: UUID (Nullable)
    ├── material_description: String
    ├── unit: String
    ├── total_received: Decimal
    ├── total_consumed: Decimal
    └── net_quantity: Decimal (total_received - total_consumed)
```

---

## 2. Validation Rules & State Transitions

1. **Date Shell Provisioning (`GET /by-date/`)**:
   - Given `project_id`, `date`, and optional `shift`:
   - If a current non-deleted `DailyReport` exists matching `(project_id, report_date, shift)`, return it.
   - If no matching `DailyReport` exists, execute `ensure_daily_report_summary(project_id, report_date, shift=shift, user=request.user)` inside an atomic transaction.
   - Return HTTP 200 OK with the full serialized report shell.

2. **Derived Child Mutation Guard**:
   - If `report.is_auto_summary == True`, direct `POST` or `DELETE` to child collection endpoints (`activities`, `labor`, `materials`, `equipment`, `concrete-logs`) MUST reject immediately with:
     - HTTP Status: `400 Bad Request`
     - Error Code: `derived_collection_read_only`
     - Error Detail: `این ردیف‌ها از ساب‌ریپورت‌های دیسیپلین مشتق شده‌اند؛ لطفاً از طریق ساب‌ریپورت مربوطه اقدام نمایید`

3. **Activity Log Cache Invalidation**:
   - On `approve_report(report, user)`:
     - Clear cached pages for `activity_log:{project_id}:*`.
     - Increment `activity_log_version:{project_id}`.
   - On `reject_report(report, user)` / report revocation:
     - Clear cached pages for `activity_log:{project_id}:*`.
