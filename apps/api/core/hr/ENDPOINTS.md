# HR Endpoints

This document outlines the API endpoints defined in the HR application (`apps/api/core/hr/urls.py`). These endpoints are nested under a specific project context (`/api/projects/<project_pk>/hr/`).

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
