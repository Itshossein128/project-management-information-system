# Field Reports Endpoints

Daily reports, offline sync, approval workflow, and related field-data APIs (weather, equipment, labor analytics). All routes are nested under:

`/api/v1/projects/{project_pk}/`

## Permissions

| Action | Permission | Notes |
|--------|------------|-------|
| List/retrieve daily reports, child rows, PDF, analytics | `view_reports` + `IsProjectMember` | Read paths require project membership |
| Create/update/delete reports and child rows, sync-batch | `edit_reports` | Writes do not require membership check |
| Submit | `edit_reports` | Reporter action |
| Review / approve / reject | `approve_reports` | Approver action |

## Daily Reports

Base path: `daily-reports/`

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `daily-reports/` | GET | List reports. Filters: `date_from`, `date_to`, `status`, `prepared_by`. Ordered by `-report_date`. |
| `daily-reports/` | POST | Create header. **Unique constraint:** one non-deleted report per `(project, report_date, shift)`. Returns `409`-style `ConflictError` on duplicate. |
| `daily-reports/{pk}/` | GET | Full report with prefetched child rows (activities, labor, equipment, materials, concrete, labor-camp, incidents). |
| `daily-reports/{pk}/` | PATCH | Update header. Only allowed when status is `draft` or `rejected`. |
| `daily-reports/{pk}/` | DELETE | Soft-delete. Only allowed when status is `draft`. |
| `daily-reports/{pk}/submit/` | POST | Submit for approval. Validates at least one activity, equipment start/end pairs, and labor-camp counts before transition. |
| `daily-reports/{pk}/review/` | POST | Mark `under_review`. Body: optional `notes`. Requires current status `submitted`. |
| `daily-reports/{pk}/approve/` | POST | Approve. Requires `submitted` or `under_review`. Triggers progress recalculation (Celery / event consumer). |
| `daily-reports/{pk}/reject/` | POST | Reject. Body: `reason` (min 10 chars). Requires `submitted` or `under_review`. |
| `daily-reports/{pk}/pdf/` | GET | Export report as PDF attachment. |
| `daily-reports/sync-batch/` | POST | Offline batch sync (see below). |

### Approval workflow

```
draft ──submit──► submitted ──review──► under_review
  ▲                    │                      │
  │                    └────approve───────────┘──► approved
  └────reject (reason ≥ 10 chars)◄── submitted / under_review
```

Rejected reports return to an editable state (`draft`-equivalent for PATCH/child edits).

### Child row endpoints

Nested under `daily-reports/{report_pk}/`. All child writes require parent status `draft` or `rejected`.

| Path suffix | Methods | Notes |
| :--- | :--- | :--- |
| `activities/` | GET, POST | Activity progress rows |
| `activities/{pk}/` | PATCH, DELETE | Soft-delete |
| `labor/` | GET, POST | Supports **batch POST** (array body) with upsert keys `(labor_category, job_title)` |
| `labor/{pk}/` | PATCH, DELETE | |
| `equipment/` | GET, POST | |
| `equipment/{pk}/` | PATCH, DELETE | |
| `materials/` | GET, POST | Includes optional `unit_cost` |
| `materials/{pk}/` | PATCH, DELETE | |
| `concrete-logs/` | GET, POST | |
| `concrete-logs/{pk}/` | PATCH, DELETE | |
| `labor-camp/` | GET, POST | |
| `labor-camp/{pk}/` | PATCH, DELETE | |
| `incidents/` | GET, POST | |
| `incidents/{pk}/` | PATCH, DELETE | |

### Offline sync (`sync-batch`)

**POST** `daily-reports/sync-batch/`

Request body: JSON **array** of report payloads (same shape as create + nested child arrays). Each item may include `local_id` for client-side deduplication.

Per-item result statuses:

| Status | Meaning |
|--------|---------|
| `created` | New server report inserted |
| `merged` | Merged into existing draft/rejected report (matched by `local_id` or `(report_date, shift)`) |
| `conflict` | Server report exists but is not mergeable (e.g. already `approved`, or status not in `{draft, rejected}`) |
| `skipped` | Duplicate `local_id` within the same batch |
| `error` | Validation failure (invalid date, header errors, child validation) |

Conflict responses include `server_payload` and `conflict_fields` for the frontend merge UI (`sync-conflicts.tsx`).

## Reference data

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `manpower/job-titles/` | GET | Fixed labor job titles for the Shiraz grid. Filter: `category`. |
| `weather/` | GET, POST | Project weather log |
| `weather/{pk}/` | GET, PATCH, DELETE | |

## Standalone forms & analytics (Sprint 10+)

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `manpower/` | GET, POST | Standalone manpower entries |
| `manpower/{pk}/` | PATCH, DELETE | |
| `labor-camp/` | GET, POST | Standalone labor-camp reports |
| `labor-camp/{pk}/` | PATCH, DELETE | |
| `equipment-log/` | GET, POST | Equipment usage log |
| `equipment-log/summary/` | GET | Aggregated equipment log KPIs |
| `equipment-log/{pk}/` | PATCH, DELETE | |
| `equipment/` | GET, POST | Equipment registry CRUD |
| `equipment/{pk}/` | GET, PATCH, DELETE | |
| `equipment-utilization/` | GET | Utilization by date range |
| `equipment-utilization/summary/` | GET | Fleet summary KPIs |
| `personnel-summary/` | GET | Personnel rollup |
| `labor-productivity/` | GET | Productivity by activity/discipline/job title |
| `activity-log/` | GET | Filtered activity log export |
| `activity-log/filters/` | GET | Filter option metadata |

## Frontend routes

- `/projects/{id}/daily-reports` — list
- `/projects/{id}/daily-reports/new` — create form
- `/projects/{id}/daily-reports/{reportId}` — edit/view
- `/projects/{id}/sync-conflicts` — offline conflict resolution

## Operational notes

- **Shift values:** `day`, `night`, `full` (default `full`).
- **Progress side effect:** approving a report enqueues progress recalculation for linked activities.
- **Auto costs:** approved labor entries with `daily_rate` feed `cost_control.ActualCost` (see `cost_control/ENDPOINTS.md`).
- **Photo attachments:** activity photos require MinIO/S3 (`storage` app); not available in Docker-less cloud dev.
