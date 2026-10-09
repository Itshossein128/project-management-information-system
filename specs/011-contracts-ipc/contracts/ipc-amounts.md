# Contract: IPC Submitted vs Approved Amounts

## Fields on IPC

| Field | When set | Mutable after |
|-------|----------|---------------|
| gross_amount | draft edit | locked after submit |
| submitted_amount | on submit (= gross) | never (immutable) |
| approved_amount | on approve | never via collection; only via re-approve flows if any |
| approval_variance_note | on approve if approved &lt; submitted | with approve |

## Actions

### Submit

`POST .../ipcs/{id}/submit/`

- Requires gross_amount &gt; 0
- Sets `submitted_amount = gross_amount`
- Status → submitted

### Approve

`POST .../ipcs/{id}/approve/`

Body (optional):

```json
{
  "approved_amount": "950000.00",
  "approval_variance_note": "Quantity variance on BOQ item 12",
  "planned_payment_date": "2026-11-01"
}
```

Rules:

- Default `approved_amount` = `submitted_amount` if omitted
- `approved_amount` MUST be ≤ `submitted_amount` and ≥ 0
- If `approved_amount` &lt; `submitted_amount`, `approval_variance_note` required (non-blank)
- Status → approved
- Recalculate net from approved_amount − deductions (existing deduction rules)

### Collection

MUST NOT change: status, submitted_amount, approved_amount, gross_amount.

Error codes (CodedValidationError):

- `approved_exceeds_submitted`
- `approval_variance_note_required`
- `ipc_not_submittable` / existing codes as today
