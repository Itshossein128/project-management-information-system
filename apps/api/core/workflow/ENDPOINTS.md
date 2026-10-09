# Workflow & management decisions

Base: `/api/v1/projects/{project_id}/`

## Management decisions

| Method | Path | Permission |
|--------|------|------------|
| GET | `/decisions/` | `view_documents` or `view_project` |
| POST | `/decisions/` | `edit_project` |
| GET/PATCH/DELETE | `/decisions/{id}/` | read / `edit_project` |

Create requires non-blank `rationale` and `execution_owner`. Optional `related_risk`, `related_activity`, `related_contract` must belong to the same project.

## Workflow definitions

| Method | Path | Permission |
|--------|------|------------|
| GET/POST | `/workflows/definitions/` | read / `edit_project` |
| GET/PATCH | `/workflows/definitions/{id}/` | read / `edit_project` |
| POST | `/workflows/definitions/{id}/activate/` | `edit_project` |
| POST | `/workflows/definitions/{id}/retire/` | `edit_project` |

Activation fails with `incomplete_stages` when any stage lacks both `approver_user` and `approver_role`.

### Sample: `budget_change`

```json
POST /workflows/definitions/
{
  "name": "Budget change approval",
  "workflow_type": "budget_change",
  "stages": [
    {"order": 1, "name": "PM review", "approver_user": "<uuid>", "approval_mode": "any"},
    {"order": 2, "name": "Finance", "approver_role": "finance_manager", "approval_mode": "all", "on_reject": "return_previous"}
  ]
}
```

Consumers start an instance with:

```json
POST /workflows/instances/
{
  "definition": "<active-definition-uuid>",
  "subject_type": "budget_change",
  "subject_id": "<change-request-or-decision-uuid>"
}
```

## Workflow instances

| Method | Path | Permission |
|--------|------|------------|
| GET/POST | `/workflows/instances/` | read / `edit_project` |
| GET | `/workflows/instances/{id}/` | read |
| POST | `/workflows/instances/{id}/approve/` | `edit_project` |
| POST | `/workflows/instances/{id}/reject/` | `edit_project` |
| POST | `/workflows/instances/{id}/cancel/` | `edit_project` |
| GET | `/workflows/instances/{id}/log/` | read |

Query: `status`, `workflow_type`, `subject_type`, `subject_id`, `overdue=true` (in-progress with `current_due_at` in the past).

Listing with `overdue=true` also best-effort writes `AlertLog` rows (`trigger_reference` = `workflow-overdue:{instance}:{date}`) so operators can see overdue stages without a Celery worker.

## Consumer attachment (domains 09–11 / 14)

Other domains start an instance against an active project definition:

| Field | Value |
|-------|-------|
| `subject_type` | Stable string (`budget_change`, `ipc_approval`, `payment_approval`, `purchase_request`, `schedule_change`, `inspection_approval`, …) |
| `subject_id` | UUID of the consuming entity |
| `definition` | Project `WorkflowDefinition` with matching `workflow_type` |

This feature ships the engine + `budget_change` sample path. Full IPC/payment/inspection wiring remains in those domains’ plans.
