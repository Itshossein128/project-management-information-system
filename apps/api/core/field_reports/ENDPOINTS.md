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
| `daily-reports/by-date/` | GET | Read-only lookup by date query (`?date=YYYY-MM-DD`). Returns HTTP 404 if no report exists for the date (requires `view_reports`). |
| `daily-reports/by-date/` | POST | Ensures or rebuilds full-day summary shell for date body (`{"date": "YYYY-MM-DD"}`). Requires `edit_reports`. |
| `daily-reports/{pk}/` | GET | Full report with child rows; includes `is_locked`, `lineage_id`, `version_number`, `is_current`. |
| `daily-reports/{pk}/` | PATCH | Update header. Only `draft`/`rejected`. Approved → `report_locked`. |
| `daily-reports/{pk}/` | DELETE | Soft-delete. Only allowed when status is `draft`. |
| `daily-reports/{pk}/submit/` | POST | Submit for approval. Validates activities (unset≠zero), equipment pairs, labor-camp counts. |
| `daily-reports/{pk}/review/` | POST | Mark `under_review`. Body: optional `notes`. Requires current status `submitted`. |
| `daily-reports/{pk}/approve/` | POST | Approve (**locks**). Requires `submitted` or `under_review`. Progress recalc + closes open correction for result report. |
| `daily-reports/{pk}/reject/` | POST | Reject. Body: `reason` (min 10 chars). Requires `submitted` or `under_review`. |
| `daily-reports/{pk}/pdf/` | GET | Export report as PDF attachment. |
| `daily-reports/{pk}/versions/` | GET | All versions sharing `lineage_id`. |
| `daily-reports/{pk}/rebuild/` | POST | Rebuild a current editable summary. Approved, historical, deleted, submitted, and under-review targets return stable localized error codes. |
| `daily-reports/{pk}/correction-requests/` | GET/POST | List or open correction (reason ≥ 10 chars) from **approved current**; clones draft version. |
| `daily-reports/{pk}/materials/reconciliation/` | GET | Advisory consumption vs inventory balance (`match`/`mismatch`/`insufficient_data`). |
| `correction-requests/{id}/cancel/` | POST | Cancel open correction; restore source as current. |
| `daily-reports/sync-batch/` | POST | Offline batch sync (see below). Conflicts on approved **current**. |

### Phase A.1 daily report contract

Both routes require authentication, active membership with `view_reports` or the existing organizational read-only observation exception.

- `GET daily-reports/contract/` returns the versioned field mappings, decision register, 18-section scope, deliverables, and form profiles. Use `include_mappings=false` to omit the field mappings or `profile=shiraz-34-32-v1` to select that profile.
- `GET daily-reports/{pk}/contract-summary/` returns official numbering, worked shifts and actual durations, selected labor profile counts, observed weather, forecast status, and the metadata fingerprint scope. Unknown readings are represented as JSON nulls or an explicit `unknown` status. Multiple current legacy reports on the same date trigger `multiple_current_legacy_reports_for_date` with an unknown official number.
- For a contract-bound report, `daily-reports/by-date/` accepts an optional worked shift `1`, `2`, or `3`, with `shift_1` through `shift_3` accepted as aliases. Each worked shift resolves to the same logical report. Unworked shifts return `404` and invalid identifiers return `400`.

With project coordinates, the forecast adapter requests up to three project-local days from [MET Norway Locationforecast 2.0](https://api.met.no/weatherapi/locationforecast/2.0/documentation). Deployments can set `MET_NORWAY_USER_AGENT` to their application identity and contact per the [MET Weather API terms](https://api.met.no/doc/TermsOfService).

### Approval workflow

Derived child rows are read-only based on summary or row ownership. Direct child writes and batch upserts return `derived_collection_read_only`. Legacy nested patches and offline sync return `derived_readonly` for derived-section writes. Existing workflow and version guards may reject the report before the ownership check.

Explicit rebuild requires `edit_reports` and active project membership. Ineligible targets return HTTP 400 with `report_locked` (approved), `historical_rebuild_rejected` (non-current), `rebuild_target_deleted` (deleted), or `report_not_editable` (submitted or under review). Unit-triggered rebuilds leave these non-editable current snapshots intact.

The official activity log and FILE 1 Excel use approved, current, non-deleted reports. The `approved_only=false` preview includes current non-approved rows. Superseded versions are available through the versions endpoint. Opening or cancelling a correction invalidates the activity log cache after the transaction commits.

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

## B03 exports

- `GET daily-reports/{pk}/excel/` and `GET daily-reports/{pk}/pdf/` render the requested daily version. `GET units/{unit}/daily-reports/{pk}/excel/` and `GET units/{unit}/daily-reports/{pk}/pdf/` render the requested unit version. All require `view_reports` or verified observation in the project's active owning unit. Foreign, deleted, or wrong-unit version IDs return 404 within an authorized project route.
- `GET daily-reports/excel/?date_from=…&date_to=…` renders one sheet per current approved date in chronological order. The configurable inclusive limit is `DAILY_REPORT_EXCEL_RANGE_MAX_DAYS` (default 31). Missing or reversed dates, over-limit ranges, and ranges without eligible reports return 400. Duplicate eligible legacy dates return 409. See the [B03 contract](../../../../specs/059-a1-b03-reference-parity/contracts/exports.md) for the stable codes and filenames.
- `GET units/{unit}/daily-reports/{pk}/attachments/{row_pk}/download/` requires active project membership plus `view_reports`. It signs a temporary URL for an uploaded image in the requested version. Legacy metadata-only rows have no downloadable bytes.

## Operational notes

- **Weather conditions:** Five standardized Shiraz-form values (`clear`, `cloudy`, `rainy`, `snowy`, `stormy`). Retired values (`sunny`, `partly_cloudy`, `foggy`) are rejected on new writes with HTTP 400. Reconciled during auto-summary using severity order (`stormy > snowy > rainy > cloudy > clear`).
- **Temperature bounds:** `temp_min` and `temp_max` (`decimal(5,1)`) constrained to `[-40.0, 60.0]`. Cross-field check enforces `temp_max >= temp_min`; violations return HTTP 400 with stable error code `temp_max_must_be_gte_temp_min` on `temp_max`.
- **Site status & Inactivity reasons:** `site_status` is `active` or `inactive`. When `site_status == 'inactive'`, an `inactivity_reason` is strictly required (`weather`, `holiday`, `strike_or_dispute`, `client_stop_order`, `safety_incident`); missing reason returns HTTP 400 with stable code `inactivity_reason_required`. When `site_status == 'active'`, `inactivity_reason` is automatically cleared (`''`). Enforced across save, submit, review, and approve workflows.
- **Weather impact notes:** Optional `weather_impact_notes` multiline text field preserved across saves, auto-summary rebuilds, correction copies, and sync batches, rendered in the official PDF header table alongside localized inactivity reason.
- **Shift values:** `day`, `night`, `full` (default `full`).
- **Progress side effect:** approving a report enqueues progress recalculation for linked activities.
- **Auto costs:** approved labor entries with `daily_rate` feed `cost_control.ActualCost` (see `cost_control/ENDPOINTS.md`).
- **Photo attachments:** activity photos require MinIO/S3 (`storage` app); not available in Docker-less cloud dev.
- **Versioned sync:** `POST daily-reports/sync-operations/v2/` stays off unless `V2_OFFLINE_SYNC_ENABLED` is true. It needs `edit_reports`. `synced_ids` contains only successful operation ids. Derived summary writes, including an empty `activities` array, stay `derived_readonly` on legacy create, PATCH, child routes, and `sync-batch/`. Server rollback keeps receipts. IndexedDB is restored from an export, not by downgrading the schema.
- **Feature 033 provenance:** `GET daily-reports/{pk}/provenance/{derived_kind}/{derived_row}/` returns the source map for one derived row. Requires `view_reports` and project membership. Derived child rows on an auto-summary stay read-only (`derived_readonly`). Concrete payloads include `qc_link`. Narrative rows are rebuilt as structured general activities, visits, and incidents rather than formatted text.
