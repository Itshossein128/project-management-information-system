# Data Model: Contracts & IPC Gap Closure

## Contract (extend)

| Field | Type | Notes |
|-------|------|-------|
| payment_terms | TextField, blank=True, default="" | Free-text payment terms / شرایط پرداخت |

Unchanged: number, title, amount, type, dates, retention/advance %, project FK, change orders.

## IPC (extend)

| Field | Type | Notes |
|-------|------|-------|
| submitted_amount | DecimalField(18,2), null=True | Frozen on submit from gross_amount |
| approved_amount | DecimalField(18,2), null=True | Set on approve; ≤ submitted |
| approval_variance_note | TextField, blank=True | Required when approved &lt; submitted |

Semantics:

- **Draft**: `gross_amount` editable; submitted/approved null.
- **Submitted**: `submitted_amount` set; gross may be read-only thereafter.
- **Approved**: `approved_amount` set; deductions apply against approved; `net_amount` / remaining based on approved net.
- **Collections**: never mutate submitted_amount, approved_amount, or status.

Backfill migration: for existing rows, set submitted_amount and approved_amount from gross_amount where status is submitted/approved/paid as appropriate; leave draft null.

## Receivables report (derived, not stored)

Row shape:

- ipc_id, contract_id, contract_number, ipc_number, status
- submitted_amount, approved_amount, net_amount
- collected_total, remaining_receivable
- planned_payment_date
- band: `overdue` | `near_due`
- days_overdue or days_until_due

Filter: status = approved (and optionally paid with remaining&gt;0 if that exists — normally remaining 0 when paid), remaining_receivable &gt; 0, planned_payment_date not null.

## Relationships (unchanged)

```
Project 1──* Contract 1──* ChangeOrder
Contract 1──* IPC 1──* IPCDeduction
IPC 1──* IPCCollection
```
