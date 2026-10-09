# Contract: Management Decisions & Workflow Engine

## APIs

Base: `/api/v1/projects/{project_id}/`

### Management decisions

`GET|POST /decisions/`  
`GET|PATCH|DELETE /decisions/{id}/`

Permission: `view_documents` (GET), `edit_project` (mutate) — see research.

#### Create body

```json
{
  "subject": "Approve temporary diversion",
  "options": "A) Divert north\nB) Divert south",
  "criteria": "Cost + safety",
  "proposer": "<user-uuid>",
  "approver_ids": ["<user-uuid>"],
  "final_decision": "",
  "execution_owner": "<user-uuid>",
  "due_date": "2026-10-30",
  "rationale": "North route avoids live traffic",
  "impact_schedule": true,
  "impact_cost": false,
  "impact_contract": false,
  "impact_risk": true,
  "execution_status": "pending",
  "related_risk": null,
  "related_activity": null,
  "related_contract": null
}
```

#### Rules

- Missing/blank `rationale` → **400** `{ "code": "rationale_required" }`.
- Missing `execution_owner` on create → **400**.
- Optional links MUST be same-project.
- Soft-delete via destroy.

---

### Workflow definitions

`GET|POST /workflows/definitions/`  
`GET|PATCH /workflows/definitions/{id}/`  
`POST /workflows/definitions/{id}/activate/`  
`POST /workflows/definitions/{id}/retire/`

Permission: `edit_project` to create/activate; `view_documents` or `view_project` to list.

#### Definition + stages body

```json
{
  "name": "Budget change approval",
  "workflow_type": "budget_change",
  "description": "Sample FR-COL flow",
  "stages": [
    {
      "order": 1,
      "name": "PM review",
      "approver_user": "<user-uuid>",
      "approver_role": null,
      "approval_mode": "any",
      "on_reject": "stop",
      "deadline_days": 3
    },
    {
      "order": 2,
      "name": "Finance approve",
      "approver_user": null,
      "approver_role": "finance_manager",
      "approval_mode": "all",
      "on_reject": "return_previous",
      "deadline_days": 5
    }
  ]
}
```

#### Activate

`POST .../activate/` → **400** `{ "code": "incomplete_stages" }` if any stage lacks both approver_user and approver_role; else status `active`.

---

### Workflow instances

`GET|POST /workflows/instances/`  
`GET /workflows/instances/{id}/`  
`POST /workflows/instances/{id}/approve/`  
`POST /workflows/instances/{id}/reject/`  
`POST /workflows/instances/{id}/cancel/`

#### Start

```json
{
  "definition": "<definition-uuid>",
  "subject_type": "budget_change",
  "subject_id": "<change-request-or-decision-uuid>",
  "comment": "Please review"
}
```

Definition MUST be `active`.

#### Approve / reject

```json
{ "comment": "Need more detail" }
```

- Reject applies stage `on_reject` (stop → instance `rejected`; return_previous → `returned` and stage moves back).
- Every call appends an action log entry with actor, time, from/to status, stage_order.

#### Query

| Param | Meaning |
|-------|---------|
| status | instance status |
| overdue | `true` → current_due_at &lt; now and not terminal |
| workflow_type | via definition |
| subject_type / subject_id | bind lookup |

### Action log

`GET /workflows/instances/{id}/log/`

```json
{
  "results": [
    {
      "actor": "<uuid>",
      "acted_at": "2026-10-09T12:00:00Z",
      "action": "reject",
      "from_status": "in_progress",
      "to_status": "returned",
      "stage_order": 2,
      "comment": "Need more detail"
    }
  ]
}
```

No PATCH/DELETE for clients.

---

## Consumer attachment (other domains)

Domains (budget/IPC/payment/schedule/inspection) start an instance with:

| Field | Value |
|-------|-------|
| subject_type | stable string agreed in their plan |
| subject_id | their entity UUID |
| definition | project definition with matching `workflow_type` |

This feature delivers the engine + **budget_change** sample path; other subject types are documented for later wiring only.

## Sample E2E (SC-003)

1. Create `budget_change` definition with ≥2 stages → activate.  
2. Start instance on a subject → reject at stage 2 → log shows return/stop.  
3. Re-submit/approve through final stage → instance `approved`; log complete.
