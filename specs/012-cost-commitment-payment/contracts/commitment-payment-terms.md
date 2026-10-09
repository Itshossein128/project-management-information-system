# Contract: Commitment Payment Terms & Origins

## API

### Create / Update Commitment

`POST|PATCH /api/v1/projects/{project_id}/commitments/`

Body (additive):

```json
{
  "commitment_number": "CM-100",
  "amount": "1000000",
  "currency": "IRR",
  "commitment_date": "2026-10-01",
  "counterparty": "Vendor Co",
  "cbs": "<uuid>",
  "payment_terms": "Net 30 after invoice approval",
  "contract": "<uuid|null>",
  "requisition": "<uuid|null>"
}
```

### Response

Includes `payment_terms`, `contract`, `requisition`, and existing `remaining` (amount − posted payments).

### Approve

`POST .../commitments/{id}/approve/` — unchanged rule: WBS or CBS required.

## UI

- Commitment create/edit on costs page: payment-terms textarea (i18n).
- Optional contract selector when contracts exist for the project.
- Show origin requisition/contract on detail when set.

## TDD anchor

Failing test: create commitment with `payment_terms` → GET returns same string; approve still requires classification.
