# Contract: By-Date Daily Report Access & Auto-Provisioning

## Endpoint: `GET /api/v1/projects/{project_pk}/daily-reports/by-date/`

### Query Parameters
- `date` (string, required): Gregorian ISO (`YYYY-MM-DD`) or Jalali (`YYYY/MM/DD`).
- `shift` (string, optional): Shift code (`shift_1`, `shift_2`, `shift_3`, or `full`). Defaults to `full`.

### Authorization
- Authenticated user
- Project Member with `view_reports` permission (read-only inspection guaranteed)

### Behaviors
1. **Existing Report**: Returns HTTP 200 OK with the existing current report payload.
2. **Missing Report**: Provisions a new valid draft shell (`status="draft"`, `is_auto_summary=true`, `shift=requested_shift`) and returns HTTP 200 OK.
3. **Invalid Date**: Returns HTTP 400 Bad Request with `{ "date": "تاریخ الزامی است", "code": "date_required" }`.

### Success Response (HTTP 200 OK)
```json
{
  "id": "c1f7b093-0100-4000-8000-000000000001",
  "project": "b0a68d00-0000-4000-8000-000000000001",
  "report_date": "1405/08/06",
  "shift": "full",
  "status": "draft",
  "is_auto_summary": true,
  "aggregation": {
    "is_auto_summary": true,
    "aggregated_at": "2026-10-28T02:00:00Z",
    "aggregated_at_jalali": "۱۴۰۵/۰۸/۰۶ - ۱۱:۳۰",
    "is_partial": true,
    "expected_disciplines": ["CIVIL", "ELECTRICAL", "MECHANICAL"],
    "contributing_disciplines": [],
    "missing_disciplines": ["CIVIL", "ELECTRICAL", "MECHANICAL"],
    "completeness": {
      "state": "partial",
      "contributing_units": [],
      "missing_units": ["civil", "electrical", "mechanical"]
    },
    "weather_source": "derived",
    "site_status_source": "derived"
  },
  "activities": [],
  "labor_entries": [],
  "materials_summary": {
    "main_table": [],
    "details": [],
    "grouped_summary": []
  }
}
```

---

## Endpoint: `POST /api/v1/projects/{project_pk}/daily-reports/` (Manual Blank Creation)

### Rejection Contract (HTTP 400 Bad Request)
Direct creation of blank unrolled daily reports is permanently disallowed.
```json
{
  "detail": "گزارش روزانه پروژه به‌صورت خودکار از گزارش‌های واحد تخصصی ساخته می‌شود. از مسیر by-date استفاده کنید.",
  "code": "auto_summary_only"
}
```
