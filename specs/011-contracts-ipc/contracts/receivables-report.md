# Contract: Receivables Report

## Endpoint

`GET /api/v1/projects/{project_id}/contracts/ipcs/receivables-report/`

### Query

| Param | Default | Meaning |
|-------|---------|---------|
| near_due_days | 7 | Inclusive window for near-due (today … today+N) |
| contract_id | — | Optional filter |

### Response

```json
{
  "as_of": "2026-10-09",
  "near_due_days": 7,
  "summary": {
    "overdue_count": 2,
    "overdue_remaining": "1500000.00",
    "near_due_count": 1,
    "near_due_remaining": "400000.00"
  },
  "items": [
    {
      "ipc_id": "...",
      "contract_id": "...",
      "contract_number": "C-01",
      "ipc_number": "IPC-03",
      "status": "approved",
      "submitted_amount": "1000000.00",
      "approved_amount": "950000.00",
      "net_amount": "900000.00",
      "collected_total": "100000.00",
      "remaining_receivable": "800000.00",
      "planned_payment_date": "2026-09-01",
      "band": "overdue",
      "days_overdue": 38,
      "days_until_due": null
    }
  ]
}
```

### Inclusion rules

- IPC status = `approved` (open receivable; not draft/submitted/rejected)
- `remaining_receivable` &gt; 0
- `planned_payment_date` is set
- `band=overdue` if planned_payment_date &lt; as_of
- `band=near_due` if as_of ≤ planned_payment_date ≤ as_of + near_due_days

Permission: `view_contracts` (or equivalent existing contract view perm).
