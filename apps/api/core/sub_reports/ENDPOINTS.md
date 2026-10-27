# Sub-Reports Endpoints

This module manages Discipline Sub-Reports for projects. It allows project members to create, view, submit, approve, and reject reports regarding the work done by different disciplines.

All endpoints require project-scoped permissions. The view permissions are:
- `view_reports`: For listing and retrieving sub-reports.
- `edit_reports`: For creating, updating, and submitting sub-reports.
- `approve_reports`: For approving and rejecting sub-reports.

The base path for these endpoints typically looks like `/api/projects/<project_id>/sub-reports/`.

## Endpoints

### 1. List Sub-Reports
- **Method:** `GET`
- **Path:** `/`
- **Description:** Returns a paginated list of discipline sub-reports for a specific project.
- **Query Parameters:**
  - `discipline`: Filter by discipline (e.g., `civil`, `electrical`, `mechanical`, `plumbing`, `hvac`, `finishing`).
- **Permissions:** Requires `view_reports` project permission.

### 2. Create Sub-Report
- **Method:** `POST`
- **Path:** `/`
- **Description:** Creates a new discipline sub-report along with its nested activities.
- **Payload:** Accepts `report_date`, `discipline`, `weather_condition`, `form_code`, `revision_number`, `linked_daily_report`, and a list of `activities`.
- **Permissions:** Requires `edit_reports` project permission.

### 3. Retrieve Sub-Report
- **Method:** `GET`
- **Path:** `/<uuid:pk>/`
- **Description:** Returns the details of a specific sub-report, including its activities and the count of activities.
- **Permissions:** Requires `view_reports` project permission.

### 4. Update Sub-Report
- **Method:** `PATCH`
- **Path:** `/<uuid:pk>/`
- **Description:** Updates the details of a specific sub-report. If `activities` are provided, the old activities are soft-deleted and replaced by the new ones.
- **Permissions:** Requires `edit_reports` project permission.

### 5. Delete Sub-Report
- **Method:** `DELETE`
- **Path:** `/<uuid:pk>/`
- **Description:** Soft deletes a discipline sub-report.
- **Permissions:** Requires `edit_reports` project permission.

### 6. Submit Sub-Report
- **Method:** `POST`
- **Path:** `/<uuid:pk>/submit/`
- **Description:** Transitions a draft sub-report to the `SUBMITTED` state.
- **Permissions:** Requires `edit_reports` project permission.

### 7. Approve Sub-Report
- **Method:** `POST`
- **Path:** `/<uuid:pk>/approve/`
- **Description:** Approves a previously submitted sub-report, transitioning it to the `APPROVED` state.
- **Permissions:** Requires `approve_reports` project permission.

### 8. Reject Sub-Report
- **Method:** `POST`
- **Path:** `/<uuid:pk>/reject/`
- **Description:** Rejects a previously submitted sub-report, transitioning it to the `REJECTED` state.
- **Payload:** Requires a `rejection_reason` (minimum 10 characters).
- **Permissions:** Requires `approve_reports` project permission.

## Feature 033 section rows

Canonical unit reports (`/api/v1/projects/{project_pk}/units/{unit}/daily-reports/{id}/…`) expose section collections. View requires `view_reports`. Create and delete require `edit_reports` and an editable draft or rejected current version.

| Path | Error codes |
|---|---|
| `concrete/` | `volume_must_be_positive`, `sampling_requires_test_information`, `reference_not_in_project_scope` |
| `issues/` | `barrier_owner_and_due_date_required` |
| `visits/` | — |
| `hse-incidents/` | `hse_immediate_action_required`, `invalid_severity` |
| `general-activities/` | — |
| `attachments/` | `unsupported_file_format`, `file_too_large`, `attachment_row_not_in_version`, `reference_not_in_project_scope`, `submitted_report_locked` |

Submit of a version with declared concrete sampling creates or reuses a same-project `risk.Inspection`. Submit of a version with an HSE row creates one `notifications.Notification` per incident. Attachment bytes are not sent to MinIO when object storage is unavailable; the row stores a local storage key and checksum only.

## Versioned offline sync

`POST /api/v1/projects/{project_id}/daily-reports/sync-operations/v2/` is disabled unless `V2_OFFLINE_SYNC_ENABLED` is true. It requires `edit_reports` for the current actor. Each operation commits alone. `synced_ids` lists only operation ids whose outcome is `success`. Stable outcomes are `success`, `validation_error`, `conflict` (`sync_conflict`, including `conflict_report_approved` and `non_current_report`), and `blocked_dependency`. An empty list is `snapshot_replacement_forbidden`. The same operation id and payload replays the stored receipt. A changed payload returns `operation_id_reused`. `correct_transfer` opens the official correction draft and does not patch an approved row. Legacy `sync-batch/` still rejects derived summary writes with `derived_readonly`.

Rolling a server release back must keep the receipt table. Do not delete receipts to undo a sync, and do not downgrade IndexedDB. Clients export a backup and restore it with a reader that understands the current schema.

## Operational Notes
- **Weather Condition Standards:** `weather_condition` uses the five standardized Shiraz categories: `clear`, `cloudy`, `rainy`, `snowy`, `stormy`. Contributing sub-report weather conditions are automatically reconciled during daily-report summary generation using severity order `stormy > snowy > rainy > cloudy > clear`.
