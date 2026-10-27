# Phase 0 Research: Daily Report Auto-Rollup & Activity Master Log Sync

**Feature Branch**: `039-auto-daily-rollup`  
**Date**: 2026-10-28  
**Spec Reference**: `specs/039-auto-daily-rollup/spec.md`

---

## 1. Guaranteed Date Shell Access (`GET /by-date/`)

### Decision
`GET /api/v1/projects/{project_pk}/daily-reports/by-date/?date={YYYY-MM-DD}&shift={1|2|3|full}` will guarantee an HTTP 200 response with a valid draft report shell (`is_auto_summary=True`, `status="DRAFT"`) when queried for any valid calendar date, rather than returning HTTP 404 Not Found. If no report currently exists in the database for that date and shift, the endpoint will provision a summary shell via `ensure_daily_report_summary(project_id, report_date, shift=shift, user=request.user)`.

### Rationale
- **Zero 404 navigation**: Field engineers, project managers, and read-only viewers with `view_reports` access expect date-mediated navigation where inspecting any date gives immediate situational awareness of progress, even before discipline units submit reports.
- **Elimination of blank manual reports**: Prevents users from having to make out-of-band `POST /daily-reports/` calls, which can create detached unrolled shells. `POST /daily-reports/` remains rejected with `auto_summary_only`.
- **Idempotency**: Subsequent `GET` queries on the same date will fetch the existing shell without primary key churn or duplicate row creation.

### Alternatives Considered
- *Return HTTP 404 and require frontend to POST*: Rejected because viewers with read-only permissions (`view_reports`) cannot perform POST requests, preventing them from inspecting dates that have not yet had manual drafts provisioned.
- *Generate shell in-memory without database persistence*: Rejected because child collections (derived activities, labor, materials) and completeness checks rely on consistent relational queries and foreign key bindings.

---

## 2. Contractor-Keyed Labor Aggregation and Headcount Bucketing

### Decision
Aggregate labor entries from discipline sub-reports into summary buckets using the composite key:
`(labor_category, resolved_job_title, contractor_ref_id)`
Extend `DailyReportLabor` to add:
- `contractor_ref`: foreign key to `projects.Stakeholder` (nullable, on_delete=SET_NULL)
- `contractor_name`: string field (max_length=120, blank=True, default='')

When `contractor_ref` is `None` (direct company labor), attribute `contractor_name = "نفر شرکت"` (Direct / Company Labor) and bucket under `contractor_ref=None`.
Update the uniqueness constraint on `DailyReportLabor` to include `contractor_ref` so distinct subcontractors with identical labor categories and job titles do not violate database constraints.

### Rationale
- Subcontractor invoicing, labor cost distribution, and daily manpower verification require distinct tracking per contractor. Merging headcounts under a bare job title destroys subcontractor billing auditability.
- Matching `DailyReportActivity`'s established pattern for contractor references ensures domain model consistency across `field_reports`.

### Alternatives Considered
- *Prefixing the contractor name into `job_title` (e.g. "Rebar Worker (Contractor A)")*: Rejected as fragile string concatenation that pollutes catalog job title matching and translation.
- *Separate child table for contractor labor*: Rejected because `DailyReportLabor` is already the unified labor table across the system; extending it preserves backward compatibility with reporting and export services.

---

## 3. Strict Read-Only Locking for Derived Collections

### Decision
Enforce strict server-side protection on derived child collections of auto-summary reports (`is_auto_summary=True`). Any direct mutation request (`POST`, `PUT`, `PATCH`, `DELETE`) targeting child endpoints (`activities`, `labor`, `materials`, `equipment/machinery`, `concrete-logs`) will be rejected with HTTP 400 Bad Request and error payload:
```json
{
  "detail": "این ردیف‌ها از ساب‌ریپورت‌های دیسیپلین مشتق شده‌اند؛ لطفاً از طریق ساب‌ریپورت مربوطه اقدام نمایید",
  "code": "derived_collection_read_only"
}
```
In the frontend, when `DailyReportForm.tsx` loads a report with `is_auto_summary=True`, redirect the user immediately to `DailyReportSummaryView` (`/projects/:projectId/daily-reports/:reportId`), where child rows are displayed in read-only tables and "Add Row" / "Delete Row" controls are hidden.

### Rationale
- Eliminates divergence between source-of-truth discipline sub-reports and executive daily reports.
- Standardizes the error code to `derived_collection_read_only` (aligning with FR-007 and test specifications).

### Alternatives Considered
- *Silently ignoring child row edits on auto-summary reports*: Rejected because it misleads users into thinking their manual additions were saved.
- *Allowing manual overrides on derived child rows*: Rejected by domain governance; modifications must originate in the discipline sub-report to maintain contractor and technical responsibility.

---

## 4. Shiraz Excel Sheet 1 (`ACTIVITY`) Alignment & Real-Time Cache Invalidation

### Decision
1. **Serialization Alignment**: Update `apps/api/core/field_reports/services/activity_log.py` to include `source_discipline` and `parcel` in `serialize_activity_log_row`:
   ```python
   {
       "id": str(row.id),
       "report_id": str(report.id),
       "report_date": gregorian_to_jalali(report.report_date),
       "day_name": report.report_date.strftime('%A'),
       "source_discipline": row.source_discipline or "",
       "activity_description": row.activity_description,
       "shift": row.shift,
       "subcontractor": row.subcontractor_name,
       "headcount": row.headcount,
       "parcel": row.parcel or "",
       "zone": row.zone or "",
       "block": row.block or "",
       "floor": row.floor or "",
       "location": row.location_detail or "",
       "quantity": float(row.quantity) if row.quantity is not None else None,
       "unit": row.unit or "",
       "activity_code": row.activity_ref.activity_code if row.activity_ref_id else None,
       "activity_name": row.activity_ref.activity_name if row.activity_ref_id else None,
       "report_status": report.status,
   }
   ```
2. **Filtering Support**: Update `activity_log_queryset` to support `source_discipline` (or `discipline`) and `parcel` query parameters (supporting both single and comma-separated/multi-select values).
3. **Filter Options**: Update `ActivityLogFilterOptionsView` to return available `disciplines` and `parcels` in addition to `zones`, `blocks`, and `subcontractors`.
4. **Instant Invalidation**: In `field_reports.services.approve_report` (and rejection/revocation), invalidate the activity log cache immediately. Implement version-based cache keying `cache_key('activity_log', project_id, version, fp, page_num)` and increment the project's activity log cache version tag, plus scan and remove Redis keys for `activity_log:{project_id}:*`.

### Rationale
- Shiraz Excel Sheet 1 is the definitive contractual standard for site progress logs. Omitting `source_discipline` and `parcel` made cross-referencing with project schedules impossible.
- Stale 300-second cache after report approval caused site engineers to report that approved work was missing from the master log.

---

## 5. Weather Hierarchy and Manager Override Attribution

### Decision
1. In `daily_report_aggregation.py`, rank weather conditions using `WEATHER_SEVERITY`:
   `clear (10) < cloudy (20) < rainy (30) < snowy (40) < stormy (50)`.
2. When aggregating:
   - If `report.weather_override` is `True`, preserve existing `weather_condition`, `temp_min`, `temp_max`, and set `weather_source = 'overridden_by_manager'`.
   - If `report.weather_override` is `False`, pick the highest severity condition among contributing sub-reports, min of all `temp_min`, max of all `temp_max`, and set `weather_source = 'derived'`.
3. In `DailyReportSummaryView.tsx`, render an explicit badge «بازنویسی توسط مدیر» (Overridden by Manager) when `weather_source === 'overridden_by_manager'` or `report.weather_override` is true.

---

## 6. Discipline Completeness Confirmation Banner

### Decision
In `IncompletenessBanner.tsx`:
- When reporting is complete (`completeness.state === "complete"` or `!aggregation.is_partial`), render a prominent green success banner:
  - Text: «تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند» (All discipline reports received and aggregated).
  - Test ID: `data-testid="daily-report-complete-banner"`.
- When reporting is incomplete (`completeness.state === "partial"` or `aggregation.is_partial`), render the existing amber alert banner enumerating missing disciplines.

---

## 7. Jalali Timestamping and Materials Aggregation

### Decision
1. **Localized Jalali Timestamp**:
   In `build_aggregation_meta`, add `aggregated_at_jalali` formatted using `gregorian_to_jalali_datetime` (e.g. `۱۴۰۵/۰۸/۰۶ - ۱۱:۳۰`).
2. **Materials Algebraic Summation**:
   In `DailyReportDetailSerializer.get_materials_summary(self, obj)`, retain `main_table` and `details`, and add `grouped_summary` grouping materials by `(material_ref_id, material_description, unit)` with computed fields `total_received`, `total_consumed`, and `net_quantity`.
