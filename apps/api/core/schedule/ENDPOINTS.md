# Schedule Endpoints

Activity CRUD, baseline import (MSP/P6), physical progress dashboard, S-curve, Gantt, and manual progress entry. All routes are nested under:

`/api/v1/projects/{project_pk}/`

## Permissions

| Area | View | Edit |
|------|------|------|
| Activities, progress reads, Gantt, import status | `view_activities` + `IsProjectMember` | — |
| Activity create/update/delete, relations, manual progress | `edit_activities` | Required for writes |

Progress KPI endpoints use `view_dashboard` (see `progress_views.py`).

## Activities

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `activities/` | GET | List activities. Supports WBS/status/date filters via query params. |
| `activities/` | POST | Create activity linked to WBS node. |
| `activities/{activity_id}/` | GET | Activity detail with relations. |
| `activities/{activity_id}/` | PATCH | Partial update. |
| `activities/{activity_id}/` | DELETE | Soft-delete (validates no blocking dependencies). |
| `activities/weight-summary/` | GET | Weight distribution summary for progress calculation. |
| `activities/network/` | GET | Activity relation graph for network view. |
| `activities/{activity_id}/relations/` | POST | Create predecessor/successor relation. Validates cycle detection. |
| `activities/{activity_id}/relations/{relation_id}/` | DELETE | Soft-delete relation. |

## Baseline import

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `import/msp/preview/` | POST | Preview MSP XML import (multipart file). Uses `validate_msp_upload`. |
| `import/msp/` | POST | Start async MSP import job. Returns `task_id`. |
| `import/msp/status/{task_id}/` | GET | Poll import job status. |
| `import/p6/preview/` | POST | Preview P6 XER import. Uses `validate_p6_upload`. |
| `import/p6/` | POST | Start async P6 import. |
| `import/p6/status/{task_id}/` | GET | Poll P6 import status. |

Local dev: set `CELERY_TASK_ALWAYS_EAGER=true` to run imports inline without a Celery worker.

## Progress dashboard (Sprint 6)

| Endpoint | Method | Query params | Description |
| :--- | :--- | :--- | :--- |
| `progress/` | GET | `as_of` (Jalali or Gregorian) | Weighted progress snapshot for the project. |
| `progress/s-curve/` | GET | `date_from`, `date_to`, `interval` (`daily`\|`weekly`\|`monthly`), `force_refresh` | S-curve time series. May include `warning` when data is sparse. |
| `progress/activities/` | GET | `as_of`, `wbs_id`, `status`, `is_behind` | Per-activity breakdown with planned vs actual. |
| `progress/kpis/` | GET | `as_of`, `force_refresh` | EVM KPIs (SPI, CPI, EAC, VAC). Cached 30 min. |
| `progress/history/` | GET | — | Progress history keyed by approved daily reports. |
| `progress/manual/` | POST | — | Manual progress entry (see below). |

### Manual progress entry

**POST** `progress/manual/`

Required body fields:

```json
{
  "activity_id": "<uuid>",
  "report_date": "1404-01-15",
  "actual_progress": 0.75
}
```

Optional: `cumulative_quantity`, `notes`.

- `actual_progress` accepts `0–1` or `0–100` (values &gt; 1 are divided by 100).
- Creates/updates `ActivityProgress` with `source=manual`.
- Invalidates S-curve cache for the project.

Progress from approved daily reports uses `source=daily_report` and is recalculated on report approval.

## Gantt (Sprint 9)

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `gantt/` | GET | Task list for frappe-gantt UI. Optional `baseline_id`. |
| `gantt/pdf/` | GET | PDF table export of schedule. |

## Frontend routes

- `/projects/{id}/progress` — progress dashboard (S-curve, KPIs, activity table)
- `/projects/{id}/schedule/gantt` — read-only Gantt with baseline selector

## Operational notes

- **Date parsing:** All progress endpoints accept Jalali (`1404-01-15`) or Gregorian ISO dates via `common.jalali.parse_jalali_or_gregorian`.
- **Cache:** S-curve and KPI responses are Redis-cached; pass `force_refresh=true` after bulk data changes.
- **N+1 optimizations:** KPI endpoint aggregates in `evm_service` (documented in view: 12 → 3 queries).
