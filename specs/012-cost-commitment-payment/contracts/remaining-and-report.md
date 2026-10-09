# Contract: Remaining Math & Ledger Report

## Remaining allocatable

`GET /api/v1/projects/{project_id}/budgets/remaining/`

Response headings include:

```json
{
  "approved": 1000,
  "committed": 600,
  "consumed": 400,
  "remaining": 0,
  "overrun": false
}
```

Semantics (updated):

- `consumed` = sum of **approved** actuals on the heading.
- `committed` = **open** commitment = per approved commitment `max(0, amount − linked approved actuals)`, summed on heading.
- `remaining` = `max(0, approved − consumed − committed)`; `overrun` if raw &lt; 0.

### Example (no double-count)

| Step | Commitment | Actual (linked) | committed | consumed | remaining (approved=1000) |
|------|------------|-----------------|-----------|----------|---------------------------|
| A | 600 approved | — | 600 | 0 | 400 |
| B | 600 | 400 approved | 200 | 400 | 400 |
| C | 600 | 600 approved | 0 | 600 | 400 |

## Contract remaining

`GET /api/v1/projects/{project_id}/contracts/{contract_id}/cost-remaining/`  
(or nested under costs: `GET .../costs/contract-remaining/?contract_id=`)

```json
{
  "contract_id": "<uuid>",
  "approved_amount": 5000000,
  "paid_total": 1200000,
  "remaining": 3800000
}
```

`paid_total` = posted payments on commitments with that `contract` FK (not IPC collections).

## Ledger report

`GET /api/v1/projects/{project_id}/costs/ledger-report/`

Optional filters: `date_from`, `date_to`, `commitment_id`, `document_ref`.

```json
{
  "rows": [
    {
      "row_type": "commitment",
      "id": "<uuid>",
      "amount": 600,
      "document_ref": "PO-1",
      "status": "approved",
      "commitment_id": "<uuid>",
      "contract_id": null,
      "requisition_id": null
    },
    {
      "row_type": "actual",
      "id": "<uuid>",
      "amount": 400,
      "document_ref": "INV-1",
      "status": "approved",
      "commitment_id": "<uuid>"
    },
    {
      "row_type": "payment",
      "id": "<uuid>",
      "amount": 200,
      "document_ref": "PAY-1",
      "status": "posted",
      "commitment_id": "<uuid>",
      "actual_cost_id": "<uuid>"
    }
  ]
}
```

## UI

- Costs page: show remaining with committed/consumed tooltips explaining open commitment.
- Ledger report panel: three row types, document column, filter by document.

## TDD anchor

- `test_remaining_no_double_count`: steps A→C above.
- `test_contract_order_remaining`: payments reduce contract remaining only via linked commitments.
- `test_ledger_report`: all three types present and document-traceable.
