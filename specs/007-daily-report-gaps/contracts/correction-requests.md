# Contract: Daily report correction requests

**Base**: `/api/v1/projects/{project_id}/daily-reports/`

## Permissions

- Create / cancel correction: project member + `edit_reports`
- Approve / reject correction request (if distinct from report approve): `approve_reports`
- Result report follows normal submit/approve permissions

## Open correction

`POST .../daily-reports/{report_id}/correction-requests/`

Body:

```json
{
  "reason": "Correct measured quantity on activity row (min 10 chars)"
}
```

Preconditions:

- Target report `status=approved` and `is_current=true`
- No other open (`draft`/`submitted`) correction for the same `lineage_id`

Effects:

1. Create `DailyReportCorrectionRequest` with reason
2. Clone header + child rows into new `DailyReport` (`draft`, `is_current=true`, `version_number=N+1`, `supersedes=source`, same `lineage_id`)
3. Set source `is_current=false` (source remains `approved`)
4. Return correction request + `result_report_id`

**201** created  
**409** `correction_already_open`  
**400** `report_not_locked` if source not approved current  
**403** without `edit_reports`

## List / detail

`GET .../daily-reports/{report_id}/correction-requests/`  
`GET .../correction-requests/{correction_id}/` (project-scoped alternate acceptable)

Returns reason, status, source/result ids, timestamps.

## Version history

`GET .../daily-reports/{report_id}/versions/`

Returns all non-deleted reports sharing `lineage_id`, ordered by `version_number`, including status and `is_current`.

## Cancel open correction

`POST .../correction-requests/{correction_id}/cancel/`

Allowed when correction is `draft`/`submitted` and result report still `draft` (not yet re-approved). Restores source `is_current=true` and soft-deletes or marks result non-current per implementation (must not leave two currents).

## Normal workflow on result report

After correction opens, editors use existing:

- `PATCH` / child CRUD on `result_report` (draft)
- `submit` → `review` → `approve` / `reject`

On **approve** of result: result becomes locked current; source stays historical approved. Correction request status → `approved`.

## Errors

| Code | When |
|------|------|
| `report_not_locked` | Source not approved current |
| `correction_already_open` | Open correction exists for lineage |
| `report_locked` | Direct PATCH on approved report |
| `reason_required` | Reason missing or &lt; 10 chars |
