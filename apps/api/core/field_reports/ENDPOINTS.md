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
| `daily-reports/` | GET | List reports. Filters: `date_from`, `date_to`, `status`, `prepared_by`, `lineage_id`, `is_current` (default `true` on list). Ordered by `-report_date`. |
| `daily-reports/` | POST | Create header (`work_front`, `location_notes`, …). **Unique constraint:** one non-deleted **current** report per `(project, report_date, shift)`. Returns `409` `duplicate_current_report` on duplicate. |
| `daily-reports/{pk}/` | GET | Full report with child rows; includes `is_locked`, `lineage_id`, `version_number`, `is_current`. |
| `daily-reports/{pk}/` | PATCH | Update header. Only `draft`/`rejected`. Approved → `report_locked`. |
| `daily-reports/{pk}/` | DELETE | Soft-delete. Only allowed when status is `draft`. |
| `daily-reports/{pk}/submit/` | POST | Submit for approval. Validates activities (unset≠zero), equipment pairs, labor-camp counts. |
| `daily-reports/{pk}/review/` | POST | Mark `under_review`. Body: optional `notes`. Requires current status `submitted`. |
| `daily-reports/{pk}/approve/` | POST | Approve (**locks**). Requires `submitted` or `under_review`. Progress recalc + closes open correction for result report. |
| `daily-reports/{pk}/reject/` | POST | Reject. Body: `reason` (min 10 chars). Requires `submitted` or `under_review`. |
| `daily-reports/{pk}/pdf/` | GET | Export report as PDF attachment. |
| `daily-reports/{pk}/versions/` | GET | All versions sharing `lineage_id`. |
| `daily-reports/{pk}/correction-requests/` | GET/POST | List or open correction (reason ≥ 10 chars) from **approved current**; clones draft version. |
| `daily-reports/{pk}/materials/reconciliation/` | GET | Advisory consumption vs inventory balance (`match`/`mismatch`/`insufficient_data`). |
| `correction-requests/{id}/cancel/` | POST | Cancel open correction; restore source as current. |
| `daily-reports/sync-batch/` | POST | Offline batch sync (see below). Conflicts on approved **current**. |

### Approval workflow

```
draft ──submit──► submitted ──review──► under_review
  ▲                    │                      │
  │                    └────approve───────────┘──► approved (locked)
  └────reject (reason ≥ 10 chars)◄── submitted / under_review

approved ──correction-request──► new draft version (is_current) ──► … ──► approved
prior approved remains readable (is_current=false)
```

Rejected reports return to an editable state (`draft`-equivalent for PATCH/child edits).

### Child row endpoints

Nested under `daily-reports/{report_pk}/`. All child writes require parent status `draft` or `rejected`.

| Path suffix | Methods | Notes |
| :--- | :--- | :--- |
| `activities/` | GET, POST | Includes `responsible_user`/`responsible_name`; `quantity_measured` unset≠zero |
| `activities/{pk}/` | PATCH, DELETE | Soft-delete |
| `labor/` | GET, POST | Batch upsert; optional `absence_count` (null = not recorded) |
| `labor/{pk}/` | PATCH, DELETE | |
| `equipment/` | GET, POST | |
| `equipment/{pk}/` | PATCH, DELETE | |
| `materials/` | GET, POST | Types: `receipt`/`issue`/`waste`/`return`; optional `consumption_location` |
| `materials/{pk}/` | PATCH, DELETE | |
| `concrete-logs/` | GET, POST | |
| `concrete-logs/{pk}/` | PATCH, DELETE | |
| `labor-camp/` | GET, POST | |
| `labor-camp/{pk}/` | PATCH, DELETE | |
| `incidents/` | GET, POST | Types include `site_instruction`/`barrier`; `follow_up_owner_*`, `due_date` |
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
