# Contract: Actual Cost Lifecycle

## API

### Create (draft)

`POST /api/v1/projects/{project_id}/costs/`

```json
{
  "amount": "500000",
  "cost_date": "2026-09-15",
  "registered_at": "2026-10-01",
  "wbs": "<uuid>",
  "commitment": "<uuid|null>",
  "invoice_number": "INV-1",
  "document_ref": "INV-1"
}
```

- `cost_date` = occurrence; `registered_at` defaults to today if omitted.
- New rows default `status: draft` (existing backfilled rows remain `approved`).

### Approve

`POST .../costs/{id}/approve/`

- Requires project + (wbs or cbs).
- If `require_cost_document` policy on: requires non-empty `invoice_number` or `document_ref` → else `cost_document_required`.
- Sets `status=approved`, `approved_by=request.user`.

### Void

`POST .../costs/{id}/void/` — `approved` → `void` (no hard delete of history).

## Errors

| Code | When |
|------|------|
| `wbs_or_cbs_required` | Approve without classification |
| `cost_document_required` | Policy on and no document |
| `invalid_status_transition` | Illegal transition |

## TDD anchor

1. Approve without WBS/CBS → 400.
2. Policy on + empty document → 400.
3. Linked actual + commitment appear as separate amounts in ledger; remaining does not double-count (see remaining contract).
