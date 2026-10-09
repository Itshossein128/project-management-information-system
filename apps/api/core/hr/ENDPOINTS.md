# HR Endpoints

Project-scoped base: `/api/v1/projects/{project_pk}/` (includes leave/OT and HR capacity routes).

## Permission codes

| Codename | Use |
| :--- | :--- |
| `view_hr` | Read dossier, allocations, exceptions, rates (amounts redacted without wage) |
| `edit_hr` | Create/update allocations, dossier, exceptions (draft/submit) |
| `approve_hr` | Approve/reject capacity exceptions |
| `view_wage` | See wage/rate amounts on membership and approved rates |
| `edit_wage` | Write wage fields on membership and approved labor rates |

Leave/overtime continue to use `view_reports` / `edit_reports` / `approve_reports`.

Optional project capability: `hr` (see project capabilities API).

## Person dossier

**Chosen surface (v1):** project-scoped dossier under the project URL only. A separate org-level `/api/v1/users/{user_id}/dossier/` is deferred; use the project route below.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `people/{user_id}/dossier/` | GET | Person dossier (target must be project member or allocated). Requires `view_hr`, **or** self-read of own dossier without `view_hr`. |
| `people/{user_id}/dossier/` | PATCH | Update skills, qualifications, org unit, supervisor, status, default capacity. Requires `edit_hr`. |

Capacity exception approve may return `soft_sod_warn: true` when approver is the same user who created the exception (still allowed).

Allocation ≠ project membership ≠ attendance ≠ activity progress.

## Resource allocations

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `resource-allocations/` | GET | List allocations (filters: person_id, wbs_id, activity_id, status, from, to). |
| `resource-allocations/` | POST | Create allocation; 409 `capacity_conflict` when over capacity without approved exception. |
| `resource-allocations/{id}/` | GET/PATCH/DELETE | Detail, update, soft-delete. |
| `resource-allocations/capacity-preview/` | GET | Query: person_id, from, to, capacity_percent — committed/available preview. |

## Capacity exceptions

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `capacity-exceptions/` | GET/POST | List / create (optional `submit: true`). |
| `capacity-exceptions/{id}/submit/` | POST | Draft → submitted (reason required). |
| `capacity-exceptions/{id}/approve/` | POST | Submitted → approved (`approve_hr`). |
| `capacity-exceptions/{id}/reject/` | POST | Submitted → rejected (`approve_hr`). |

Approved exception id may be passed as `capacity_exception_id` on allocation create/update.

## Approved labor rates & estimate

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `approved-labor-rates/` | GET/POST | CRUD band; amounts visible with `view_wage`; write requires `edit_wage`. |
| `approved-labor-rates/{id}/` | DELETE | Soft-delete rate. |
| `labor-cost-estimate/` | POST | `{ person_id, approved_hours, as_of? }` — uses approved rate only; `missing_approved_rate` when none. |

Wage on legacy assignment list: `GET /api/v1/users/{user_id}/assignments/` — wage fields omitted without `view_wage` on that project.

## Overtime Requests

| Endpoint | Method | Action | Description |
| :--- | :--- | :--- | :--- |
| `overtime-requests/` | GET | list | Retrieves the list of overtime requests, filtering by current user (`my_requests=true`) or by `status` if requested. Ordered by `-overtime_date`. |
| `overtime-requests/` | POST | create | Creates a new overtime request, assigning the project and current user. |
| `overtime-requests/<uuid:pk>/` | PATCH | partial_update | Updates an overtime request. Allowed only if the request is in draft status. |
| `overtime-requests/<uuid:pk>/` | DELETE | destroy | Deletes an overtime request. Allowed only if the request is in draft status. |
| `overtime-requests/<uuid:pk>/submit/` | POST | submit | Custom action to submit a draft overtime request for supervisor review. |
| `overtime-requests/<uuid:pk>/supervisor-approve/` | POST | supervisor_approve | Custom action for a supervisor to either approve or reject the overtime request. Requires `approved` boolean and optional `notes`. |
| `overtime-requests/<uuid:pk>/manager-approve/` | POST | manager_approve | Custom action for a manager to final approve or reject the overtime request, potentially adjusting hours via `approved_hours`. |

## Leave Requests

| Endpoint | Method | Action | Description |
| :--- | :--- | :--- | :--- |
| `leave-requests/` | GET | list | Retrieves the list of leave requests, filtering by current user (`my_requests=true`) or by `status` if requested. Ordered by `-leave_date`. |
| `leave-requests/` | POST | create | Creates a new leave request, assigning the project and current user. |
| `leave-requests/<uuid:pk>/` | PATCH | partial_update | Updates a leave request. Allowed only if the request is in draft status. |
| `leave-requests/<uuid:pk>/` | DELETE | destroy | Deletes a leave request. Allowed only if the request is in draft status. |
| `leave-requests/<uuid:pk>/submit/` | POST | submit | Custom action to submit a draft leave request for supervisor review. |
| `leave-requests/<uuid:pk>/supervisor-approve/` | POST | supervisor_approve | Custom action for a supervisor to either approve or reject the leave request. Requires `approved` boolean. |
| `leave-requests/<uuid:pk>/manager-approve/` | POST | manager_approve | Custom action for a manager to final approve or reject the leave request. Requires `approved` boolean. |
| `leave-requests/<uuid:pk>/security-approve/` | POST | security_approve | Custom action for security to approve or reject the physical exit of the user. Requires `approved` boolean. |
