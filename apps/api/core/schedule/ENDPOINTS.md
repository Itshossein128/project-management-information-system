# Schedule Endpoints

Activity CRUD, working calendars, baselines / change requests, schedule status, baseline import (MSP/P6), physical progress dashboard, S-curve, Gantt, and manual progress entry. All routes are nested under:

`/api/v1/projects/{project_pk}/`

## Permissions

| Area | View | Edit |
|------|------|------|
| Activities, calendars, baselines, change requests, schedule-status, progress reads, Gantt, import status | `view_activities` + `IsProjectMember` | — |
| Activity create/update/delete, relations, calendars write, baseline create/approve-lock, change-request submit/approve/reject, manual progress | `edit_activities` | Required for writes |

Progress KPI endpoints use `view_dashboard` (see `progress_views.py`).

## Activities

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `activities/` | GET | List activities. Supports WBS/status/date filters via query params. |
| `activities/` | POST | Create activity linked to WBS node. Additive fields: `duration_days`, `is_milestone`, `forecast_start`/`forecast_finish`, `working_calendar_id`. |
| `activities/{activity_id}/` | GET | Activity detail with relations. |
| `activities/{activity_id}/` | PATCH | Partial update. Forecast-only PATCH does not clear planned/actual. |
| `activities/{activity_id}/` | DELETE | Soft-delete (validates no blocking dependencies). |
| `activities/weight-summary/` | GET | Weight distribution summary for progress calculation. |
| `activities/network/` | GET | Activity relation graph for network view. |
| `activities/{activity_id}/relations/` | POST | Create predecessor/successor relation. Validates cycle detection. |
| `activities/{activity_id}/relations/{relation_id}/` | DELETE | Soft-delete relation. |

### Activity validation error codes

| Code | When |
|------|------|
| `impossible_planned_dates` | planned_finish &lt; planned_start (non-milestone) |
| `impossible_forecast_dates` | forecast_finish &lt; forecast_start |
| `non_working_day` | date falls on non-working day for resolved calendar |
| `invalid_milestone` | `is_milestone` true but `duration_days` ≠ 0 |

## Working calendars

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `working-calendars/` | GET | List non-deleted calendars. |
| `working-calendars/` | POST | Create calendar. `is_default=true` clears other defaults in the project. |
| `working-calendars/{calendar_id}/` | GET/PATCH/DELETE | Detail / update / soft-delete. |
| `working-calendars/{calendar_id}/exceptions/` | GET/POST | List / create calendar exceptions (holidays / extra work days). |
| `working-calendars/{calendar_id}/exceptions/{exception_id}/` | PATCH/DELETE | Update / soft-delete exception. |

| Code | When |
|------|------|
| `calendar_in_use` | Soft-delete blocked while activities reference the calendar |
| `calendar_exception_duplicate` | Same `(calendar, exception_date)` among non-deleted |

## Baselines

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `baselines/` | GET | List versions (`id`, `version_name`, `is_current`, `is_locked`, `approved_*`, `locked_*`, `source_change_request_id`). |
| `baselines/` | POST | Snapshot live activities into unlocked `BaselineActivity` rows. Body: `{ "version_name": "BL-1" }`. Optional `make_current`. |
| `baselines/{baseline_id}/approve-lock/` | POST | Set `is_locked`, `is_current`, approved/locked audit fields; demote prior current (row retained). |
| `baselines/{baseline_id}/activities/{ba_id}/` | PATCH/DELETE | Mutate snapshot row — **409 `baseline_locked`** when parent is locked. |

| Code | When |
|------|------|
| `baseline_already_locked` | Approve-lock on an already locked baseline |
| `baseline_locked` | Snapshot mutation while locked |

**Import note (MSP/P6):** Import may still create baseline snapshots. Imported baselines are left **unlocked** until an explicit `approve-lock`. There is no silent overwrite of a locked current baseline — create a new version (or approve a schedule change request) instead.

Live `PATCH activities/{id}/` never rewrites locked `BaselineActivity` rows.

## Schedule change requests

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `schedule-change-requests/` | GET/POST | List / create draft (optional `items` with proposed dates). |
| `schedule-change-requests/{id}/` | GET/PATCH | Detail / update while `draft`. |
| `schedule-change-requests/{id}/submit/` | POST | Requires non-empty `reason`, `milestone_impact`, `cost_impact`, `contract_impact`. |
| `schedule-change-requests/{id}/approve/` | POST | Apply items → new locked current baseline; prior stays locked, `is_current=false`. Body: `{ "decision_notes": "..." }`. |
| `schedule-change-requests/{id}/reject/` | POST | Reject with notes; no new baseline. |

| Code | When |
|------|------|
| `schedule_change_in_flight` | Another request is already `submitted` for the project |

## Schedule status report

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `schedule-status/` | GET | Milestone/delay report with four-way dates + `critical_path` validity. Optional `?as_of=`. |

When `critical_path.valid` is `false`, `critical_activity_ids` / `near_critical_activity_ids` are empty and `reason_codes` may include `incomplete_durations`.

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
| `gantt/` | GET | Task list for frappe-gantt UI. Optional `baseline_id`. Includes `critical_path` validity object and `is_locked` on each baseline entry. |
| `gantt/pdf/` | GET | PDF table export of schedule. |

When `critical_path.valid` is false, task `is_critical` flags are not treated as authoritative (service clears them).

## Frontend routes

- `/projects/{id}/progress` — progress dashboard (S-curve, KPIs, activity table)
- `/projects/{id}/schedule/gantt` — read-only Gantt with baseline selector

## Operational notes

- **Date parsing:** All progress endpoints accept Jalali (`1404-01-15`) or Gregorian ISO dates via `common.jalali.parse_jalali_or_gregorian`.
- **Cache:** S-curve and KPI responses are Redis-cached; pass `force_refresh=true` after bulk data changes.
- **N+1 optimizations:** KPI endpoint aggregates in `evm_service` (documented in view: 12 → 3 queries).
