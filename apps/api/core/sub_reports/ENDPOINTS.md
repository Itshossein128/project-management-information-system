# Sub-Reports Endpoints

Discipline sub-reports (civil, electrical, mechanical, etc.) with nested activity rows and an approval workflow. All routes are nested under:

`/api/v1/projects/{project_pk}/sub-reports/`

## Permissions

| Action | Permission | Notes |
|--------|------------|-------|
| List / retrieve | `view_reports` + `IsProjectMember` | Filter: `?discipline=` |
| Create / update / delete / submit | `edit_reports` | Submit via `WorkflowViewSetMixin` |
| Approve / reject | `approve_reports` | Reject body: `rejection_reason` (min 10 chars) |

## Workflow mixin

`DisciplineSubReportViewSet` uses `WorkflowViewSetMixin` for `submit`, `approve`, and `reject`. Template methods delegate to `sub_reports/services.py` (`submit_sub_report`, `approve_sub_report`, `reject_sub_report`).

Unlike daily reports, sub-reports have **no** `review` step: `draft` → `submitted` → `approved` | `rejected`.

## Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `sub-reports/` | GET | Paginated list. Query: `discipline`. Ordered by `-report_date`. |
| `sub-reports/` | POST | Create with nested `activities` array. |
| `sub-reports/{pk}/` | GET | Detail with activities and activity count. |
| `sub-reports/{pk}/` | PATCH | Update header; replacing `activities` soft-deletes old rows. |
| `sub-reports/{pk}/` | DELETE | Soft-delete. |
| `sub-reports/{pk}/submit/` | POST | `draft` → `submitted`. |
| `sub-reports/{pk}/approve/` | POST | `submitted` → `approved`. |
| `sub-reports/{pk}/reject/` | POST | `submitted` → `rejected`. Body: `rejection_reason`. |

## Payload (create / update)

Required: `report_date`, `discipline`, `activities` (list). Optional: `weather_condition`, `form_code`, `revision_number`, `linked_daily_report`.

Discipline values: `civil`, `electrical`, `mechanical`, `plumbing`, `hvac`, `finishing`.
