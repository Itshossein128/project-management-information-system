# Contract: Segregation of Duties & Roles

## Roles

System roles (seed / `permissions.constants.DEFAULT_ROLE_PERMISSIONS`) MUST include or map:

| `role_name` | FR label |
|-------------|----------|
| (admin group) | System admin |
| `executive_approver` | Executive / approver |
| `project_manager` | Project manager |
| `project_controls` | Project controls |
| `planning_engineer` | (retained; controls-adjacent) |
| `site_specialist` / `site_supervisor` | Site specialist |
| `finance_manager` | Finance |
| `hr_officer` or HR-capable role | HR |
| `procurement_officer` | Procurement / contracts |
| `supervisor_consultant` | Supervisor / consultant |
| `viewer` | Viewer |
| `document_controller` | (retained) |

Catalog: `GET /api/v1/permissions/` / roles APIs continue to list codes.

## SoD helper

`permissions.sod.assert_not_self_final_approve(created_by_id, actor) -> None`

Raises `CodedValidationError` with `code=sod_self_approve` when `created_by_id` equals `actor.id` (and both non-null).

### Apply on final approve

| Endpoint / service | Creator |
|--------------------|---------|
| IPC approve | `ipc.created_by` |
| Cost / payment final approve | payment or actual-cost creator |
| Project change-request approve | `change_request.created_by` |
| Workflow instance final approve | `instance.started_by` (or subject creator when defined) |
| Capacity exception approve | `exception.created_by` (hard-block) |

### Response

```json
HTTP 400
{ "code": "sod_self_approve", "message": "..." }
```

Global break-glass: only `is_superuser` may bypass in v1 (documented); normal admin group does **not** bypass unless product later expands policy.

## Viewer

- May call pack/KPI GET with `view_dashboard`.
- Must not receive permission for approve_* actions via viewer role defaults.
