# Data Model: Stakeholders, Documents, Decisions & Workflow

## Existing (extended): `projects.Stakeholder`

| Field | Type | Rules |
|-------|------|-------|
| relationship_owner | FK User \| null | Recommended; FR-001 |
| email, phone | string | **Redacted** in API unless caller has `view_sensitive_contacts` or `edit_project` |
| influence, interest | 1–5 \| null | Existing validation retained |
| (other) | | name, organization_name, role, communication_need, status — unchanged |

---

## New: `projects.CommunicationPlan`

| Field | Type | Rules |
|-------|------|-------|
| project | FK Project | required |
| audience | text | required (stakeholder group or named audience) |
| message | text | required |
| channel_type | enum/text | e.g. meeting, email, report, site_visit |
| frequency | text | required (e.g. weekly, on_milestone) |
| owner | FK User \| null | plan owner |
| stakeholder | FK Stakeholder \| null | optional link |
| status | active \| inactive | default active |

Soft-delete via audit base.

---

## Existing (extended): `documents.ProjectDocument`

| Field | Type | Rules |
|-------|------|-------|
| status | enum | `draft`, `in_review`, `approved`, `superseded`, `obsolete` (default draft) |
| approver | FK User \| null | FR-005 |
| doc_code | string | unique per project when non-empty |
| current revision pointer | revision label + date + file fields | Updated on revise; prior content lives in `DocumentRevision` |

### `documents.DocumentRevision` (existing, rules clarified)

| Rule | Behavior |
|------|----------|
| Append-only | New revision never deletes previous revision rows |
| File retention | Previous `file_url` remains readable to authorized users |
| Current doc | Parent document fields reflect latest revision; older revisions queryable via `/revisions/` |

---

## Existing (extended): `documents.Correspondence`

| Field | Type | Rules |
|-------|------|-------|
| related_contract | FK Contract \| null | Same project; FR-004 |
| (other) | | number, dates, parties, subject, attachment, status, project — retained |

---

## Existing (extended): `documents.MeetingMinutes`

| Field | Type | Rules |
|-------|------|-------|
| topic / title | CharField | Add if missing; else derive from type+date in UI |
| decisions | text | Retained (resolutions narrative) |
| action_items | text | Retained for compat; **not** source for open-actions report |

### New: `documents.MeetingAction`

| Field | Type | Rules |
|-------|------|-------|
| meeting | FK MeetingMinutes | CASCADE |
| project | FK Project | denormalized for report queries |
| description | text | required |
| owner | FK User \| null | required for “open” tracking in practice; allow null draft then validate before open report inclusion policy: include if status=open |
| due_date | date \| null | |
| status | open \| done | default open |
| completed_at | datetime \| null | set when done |

**Open-actions report**: `status=open` for project (optional `overdue=true` when due_date < today).

---

## New: `workflow.ManagementDecision`

| Field | Type | Rules |
|-------|------|-------|
| project | FK Project | **required** |
| subject | text | required |
| options | text/JSON | required narrative or list |
| criteria | text | required |
| proposer | FK User | required |
| approvers | M2M User or JSON uuids | at least conceptually present |
| final_decision | text | blank until decided |
| execution_owner | FK User \| null | required on save per SC-002 (with rationale) |
| due_date | date \| null | |
| rationale | text | **required** non-blank |
| attachment_refs | JSON/text | optional |
| impact_schedule / cost / contract / risk | bool | default false |
| execution_status | pending \| in_progress \| done \| cancelled | default pending |
| related_risk | FK RiskEvent \| null | same project |
| related_activity | FK Activity \| null | same project |
| related_contract | FK Contract \| null | same project |
| workflow_instance | FK WorkflowInstance \| null | optional link when routed through engine |

**Validation**: blank/whitespace `rationale` → 400 (SC-002).

---

## New: `workflow.WorkflowDefinition`

| Field | Type | Rules |
|-------|------|-------|
| project | FK Project | required (project-scoped) |
| name | text | required |
| workflow_type | enum | `purchase_request`, `ipc_approval`, `payment_approval`, `budget_change`, `schedule_change`, `inspection_approval`, `custom` |
| status | draft \| active \| retired | default draft |
| description | text | optional |

### New: `workflow.WorkflowStage`

| Field | Type | Rules |
|-------|------|-------|
| definition | FK WorkflowDefinition | CASCADE |
| order | positive int | unique per definition |
| name | text | required |
| approver_user | FK User \| null | |
| approver_role | string \| null | project role codename |
| approval_mode | all \| any | default any |
| on_reject | stop \| return_previous \| return_to | default stop |
| return_to_order | int \| null | when on_reject=return_to |
| deadline_days | positive int \| null | from stage enter |
| notify_on_enter | bool | default true |

**Activate gate**: every stage MUST have `approver_user` or non-empty `approver_role`; else reject activation (SC-006).

---

## New: `workflow.WorkflowInstance`

| Field | Type | Rules |
|-------|------|-------|
| definition | FK WorkflowDefinition | PROTECT; must be active at start |
| project | FK Project | required |
| subject_type | string | e.g. `budget_change`, `management_decision` |
| subject_id | UUID | required |
| status | pending \| in_progress \| approved \| rejected \| returned \| cancelled | |
| current_stage_order | int \| null | |
| current_due_at | datetime \| null | |
| started_by | FK User | |
| started_at / completed_at | datetime | |

### Stage assignment (optional child)

`WorkflowStageAssignment`: instance, stage_order, assignee user, status pending/approved/rejected — supports concurrent `all` mode.

---

## New: `workflow.WorkflowActionLog`

| Field | Type | Rules |
|-------|------|-------|
| instance | FK WorkflowInstance | CASCADE |
| actor | FK User | required |
| acted_at | datetime | auto |
| action | string | start, approve, reject, return, cancel, comment |
| from_status | string | |
| to_status | string | |
| stage_order | int \| null | |
| comment | text | optional |

**Immutable**: no update/delete API for logs (admin soft-delete only if audit base requires).

---

## State transitions

### Document status (typical)

`draft` → `in_review` → `approved` → `superseded` (on new approved revision) or `obsolete`.

### Meeting action

`open` → `done` (sets `completed_at`).

### Workflow definition

`draft` → `active` (activate gate) → `retired`.

### Workflow instance

`pending` → `in_progress` → (`returned` ↔ `in_progress`) → `approved` \| `rejected` \| `cancelled`.

Every transition appends `WorkflowActionLog`.

---

## Relationships (summary)

```text
Project
├── Stakeholder ──?── CommunicationPlan
├── MeetingMinutes ──< MeetingAction
├── ProjectDocument ──< DocumentRevision
├── Correspondence ──?── Contract
├── ManagementDecision ──?── Risk / Activity / Contract / WorkflowInstance
└── WorkflowDefinition ──< WorkflowStage
         └── WorkflowInstance ──< WorkflowActionLog
                              ──< StageAssignment
```
