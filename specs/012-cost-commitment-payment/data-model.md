# Data Model: Cost Commitment & Payment Gap Closure

## Commitment (extend)

| Field | Type | Notes |
|-------|------|-------|
| payment_terms | TextField, blank=True, default="" | شرایط پرداخت |
| contract | FK → contracts.Contract, null=True, blank=True | Optional origin / remaining rollup |
| requisition | FK → procurement.RequisitionHeader, null=True, blank=True | Optional purchase-request origin |

Unchanged: project, commitment_number, counterparty, amount, currency, fx_rate, commitment_date, due_date, wbs, cbs, status (draft/approved/closed/cancelled), description, document_ref.

### State transitions

```
draft → approved  (requires wbs or cbs; existing)
approved → closed | cancelled
```

Approving reduces allocable remaining via open-commitment math (see Remaining).

### Validation

- Project required (FK).
- Approve: WBS or CBS required (`wbs_or_cbs_required`).
- Create-from-requisition: requisition must be `APPROVED` and same project.

## ActualCost (extend)

| Field | Type | Notes |
|-------|------|-------|
| cost_date | DateField (existing) | **Occurrence** date |
| registered_at | DateField | Registration date; default = create date |
| status | CharField | `draft` \| `approved` \| `void` (default `draft` for new; backfill existing → `approved`) |
| document_ref | CharField optional | Prefer alongside `invoice_number`; either may satisfy “document” policy |

Unchanged: project, activity, wbs, cbs, commitment (optional), amount, cost_category, description, invoice_number, supplier, approved_by, cost_type, etc.

### State transitions

```
draft → approved  (sets approved_by; requires project + wbs or cbs)
approved → void   (reverse/void path; does not hard-delete)
```

### Validation

- Finalize/approve: project + (wbs or cbs) required.
- If project policy `require_cost_document`: require non-empty `invoice_number` or `document_ref`.
- Actual without commitment allowed (default).

## Payment (extend)

| Field | Type | Notes |
|-------|------|-------|
| duplicate_exception_reason | TextField, blank=True | Required when ack exception used |
| duplicate_exception_by | FK User, null=True | Actor who authorized exception |

Unchanged: project, commitment, actual_cost, amount, currency, fx_rate, paid_at, document_ref, status (draft/posted/void).

### Validation

- Amount > 0; must link commitment and/or actual_cost (existing).
- Posted total on a commitment cannot exceed commitment.amount (existing).
- Duplicate guard: if `document_ref` non-empty and another **posted**, non-deleted payment exists in the **same project** with the same `document_ref` (case-sensitive trim), reject with `duplicate_payment_document` unless `acknowledge_duplicate_exception=true` and non-empty `exception_reason`.
- Partial installments: different `document_ref` or same source with distinct refs allowed; source amount unchanged.

## Project cost policy (minimal)

Prefer extending existing project capability / settings if present; otherwise a boolean on project cost settings:

| Field | Type | Notes |
|-------|------|-------|
| require_cost_document | bool, default False | When true, block actual approve without document |

## Remaining (derived)

Per budget heading (unchanged keys from 010):

- `approved` = sum of control-version line amounts on heading
- `consumed` = sum of **approved** (non-void) actual costs on heading
- `committed_open` = for each **approved** commitment on heading: `max(0, commitment.amount − sum(approved actuals linked to that commitment))`, then sum
- `remaining` = `max(0, approved − consumed − committed_open)` (flag `overrun` if raw &lt; 0)

## Contract remaining (derived)

For a contract in the project:

- `approved_amount` = contract amount after approved change orders (existing contract semantics)
- `paid_total` = sum of **posted** payments on commitments where `commitment.contract_id = contract.id`
- `remaining` = `approved_amount − paid_total`

## Ledger report (derived rows)

Each row:

- `row_type`: `commitment` | `actual` | `payment`
- ids, amounts, currency, dates, status
- `document_ref` / invoice
- links: commitment_id, actual_cost_id, contract_id, requisition_id as applicable

## Relationships

```
Project 1──* Commitment *──? Contract
              Commitment *──? RequisitionHeader
              Commitment 1──* ActualCost
              Commitment 1──* Payment
              ActualCost 1──* Payment
```

## Migration notes

- Backfill `ActualCost.status = approved` for existing rows; `registered_at = cost_date` when null.
- New Commitment FKs nullable; no data loss.
- TDD: write migration + behavior tests together (red on behavior, green after migrate + service).
