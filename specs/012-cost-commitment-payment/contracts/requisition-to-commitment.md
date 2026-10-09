# Contract: Requisition → Commitment Handoff

## API

### Create commitment from approved requisition

`POST /api/v1/projects/{project_id}/procurement/requisitions/{id}/create-commitment/`

(Exact path may follow existing procurement URL nesting; must be project-scoped.)

Body:

```json
{
  "commitment_number": "CM-FROM-REQ-1",
  "amount": "2500000",
  "currency": "IRR",
  "commitment_date": "2026-10-09",
  "cbs": "<uuid>",
  "wbs": "<uuid|null>",
  "payment_terms": "Per PO",
  "contract": "<uuid|null>",
  "counterparty": "Vendor"
}
```

### Rules

- Requisition `status` MUST be `approved`; otherwise **400** `requisition_not_approved` (covers “financial review incomplete”).
- Requisition project MUST match path project.
- Created Commitment has `requisition` set; optional `contract` if provided.
- Does not auto-approve commitment unless body includes approve flow separately (default: create as `draft`, caller may call approve).

### Optional link-only

`POST .../commitments/` with `"requisition": "<uuid>"` allowed only when requisition is approved (same gate).

## UI

- Requisition detail (approved): “Create commitment” action → costs commitment form prefilled with origin.
- Show link back to requisition on commitment detail.

## TDD anchor

1. Non-approved requisition → create-commitment 400.
2. Approved → 201 with `requisition` FK set; can approve with CBS/WBS.
3. Remaining reflects approved commitment after approve.
