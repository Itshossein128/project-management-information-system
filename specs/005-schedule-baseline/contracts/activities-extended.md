# Contract: Activities (extended schedule fields)

**Base**: `/api/v1/projects/{project_id}/activities/`

Extends existing activity CRUD (see `apps/api/core/schedule/ENDPOINTS.md`). Relations and cycle rejection unchanged.

## Permissions

- Read: `view_activities`
- Write: `edit_activities`

## Create / update payload (additive fields)

```json
{
  "wbs_id": "<uuid>",
  "activity_code": "A-100",
  "activity_name": "Pour foundation",
  "planned_start": "2026-04-01",
  "planned_finish": "2026-04-10",
  "forecast_start": "2026-04-02",
  "forecast_finish": "2026-04-12",
  "actual_start": null,
  "actual_finish": null,
  "duration_days": 8,
  "is_milestone": false,
  "working_calendar_id": "<uuid|null>",
  "responsible": "<user-uuid|null>",
  "total_quantity": 100,
  "weight": 1.5,
  "status": "not_started"
}
```

Milestone example:

```json
{
  "activity_code": "M-1",
  "activity_name": "Foundation complete",
  "is_milestone": true,
  "duration_days": 0,
  "planned_start": "2026-04-10",
  "planned_finish": "2026-04-10",
  "wbs_id": "<uuid>"
}
```

## Response

Same as today, plus: `duration_days`, `is_milestone`, `forecast_start`, `forecast_finish`, `working_calendar_id`. Planned, actual, and forecast fields MUST all appear distinctly (null allowed).

## Validation errors

| Code | When |
|------|------|
| `impossible_planned_dates` | planned_finish < planned_start (non-milestone) |
| `impossible_forecast_dates` | forecast_finish < forecast_start |
| `non_working_day` | start/finish not a working day on resolved calendar |
| `invalid_milestone` | `is_milestone` true but `duration_days` ≠ 0 |
| `wbs_required` | missing WBS (existing) |
| `relation_cycle` | existing on relation POST |

Updating forecast MUST NOT clear or rewrite planned/actual fields unless those fields are also sent in the same PATCH.
