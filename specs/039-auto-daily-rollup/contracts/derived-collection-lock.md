# Contract: Derived Collection Mutation Guard

## Scope
Direct child row modifications (`POST`, `DELETE`, `PUT`, `PATCH`) on child endpoints of auto-summary daily reports:
- `/api/v1/projects/{project_pk}/daily-reports/{report_pk}/activities/`
- `/api/v1/projects/{project_pk}/daily-reports/{report_pk}/labor/`
- `/api/v1/projects/{project_pk}/daily-reports/{report_pk}/materials/`
- `/api/v1/projects/{project_pk}/daily-reports/{report_pk}/machinery/`
- `/api/v1/projects/{project_pk}/daily-reports/{report_pk}/concrete-logs/`

## Condition
`report.is_auto_summary == True`

## Rejection Response (HTTP 400 Bad Request)
```json
{
  "detail": "این ردیف‌ها از ساب‌ریپورت‌های دیسیپلین مشتق شده‌اند؛ لطفاً از طریق ساب‌ریپورت مربوطه اقدام نمایید",
  "code": "derived_collection_read_only"
}
```

## Exceptions & Permitted Operations
The parent report header continues to allow managerial metadata edits via `PATCH /api/v1/projects/{project_pk}/daily-reports/{report_pk}/`:
- `management_opinion`
- `general_notes`
- `weather_condition` (triggers `weather_override=True`)
- `weather_override`
- `temp_min`
- `temp_max`
- `site_status` (triggers `site_status_override=True`)
- `site_status_override`
- `inactivity_reason`
- `weather_impact_notes`
