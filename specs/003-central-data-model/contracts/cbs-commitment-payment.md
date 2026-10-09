# Contract: CBS, Commitment, Payment

**Feature**: `003-central-data-model`  
**Base**: `/api/v1/projects/{project_id}/`

## CBS

| Method | Path | Permission |
|--------|------|------------|
| GET/POST | `cbs/` | `view_costs` / `edit_costs` |
| PATCH/DELETE | `cbs/{id}/` | `edit_costs` |
| GET | `cbs/tree/` | `view_costs` |

### Node body

```json
{
  "parent_id": null,
  "cbs_code": "C.1",
  "cbs_name": "Direct labor",
  "cost_type": "labor",
  "description": ""
}
```

Soft-delete on DELETE; `409` if children or linked budget/commitment/cost.

## Commitment

| Method | Path | Permission |
|--------|------|------------|
| GET/POST | `commitments/` | `view_costs` / `edit_costs` |
| GET/PATCH | `commitments/{id}/` | same |
| POST | `commitments/{id}/approve/` | `edit_costs` |

### Body

```json
{
  "commitment_number": "CM-001",
  "counterparty": "Vendor Co",
  "amount": "50000000",
  "currency": "IRR",
  "commitment_date": "2026-09-01",
  "due_date": "2026-12-01",
  "wbs": "uuid",
  "cbs": "uuid",
  "description": "",
  "document_ref": "PO-9"
}
```

Approve requires wbs or cbs. Remaining = amount − sum(posted payments).

## Payment

| Method | Path | Permission |
|--------|------|------------|
| GET/POST | `payments/` | `view_costs` / `edit_costs` |
| DELETE | `payments/{id}/` | soft-delete / void |

### Body

```json
{
  "commitment": "uuid",
  "actual_cost": null,
  "amount": "1000000",
  "currency": "IRR",
  "paid_at": "2026-10-05",
  "document_ref": "PAY-1"
}
```

Does not mutate `commitment.amount`. `400 payment_exceeds_commitment` if sum would exceed.

## Budget / ActualCost extensions

Create/update payloads accept optional `cbs` (and ActualCost optional `commitment`).
