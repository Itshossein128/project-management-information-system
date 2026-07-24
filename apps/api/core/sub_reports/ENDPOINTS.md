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