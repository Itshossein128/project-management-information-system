# Contract: Payment Duplicate Document Guard

## API

### Create payment

`POST /api/v1/projects/{project_id}/payments/`

```json
{
  "commitment": "<uuid>",
  "actual_cost": "<uuid|null>",
  "amount": "100000",
  "paid_at": "2026-10-05",
  "document_ref": "PAY-DOC-1",
  "currency": "IRR"
}
```

### Duplicate behavior

Given a **posted**, non-deleted payment in the same project with the same non-empty `document_ref`:

- Without exception → **400** `{ "code": "duplicate_payment_document", ... }`
- With exception:

```json
{
  "commitment": "<uuid>",
  "amount": "50000",
  "paid_at": "2026-10-06",
  "document_ref": "PAY-DOC-1",
  "acknowledge_duplicate_exception": true,
  "exception_reason": "Split bank transfer correction authorized by CFO"
}
```

→ **201**; stores `duplicate_exception_reason` and `duplicate_exception_by`.

Empty `document_ref` does not trigger the duplicate guard (still subject to commitment cap).

### Caps

Existing: posted payments on a commitment cannot exceed commitment amount.

## UI

- Payments panel on project costs: create payment; show duplicate error; exception reason dialog when user confirms override (permission: `edit_costs`).

## TDD anchor

1. Two payments same `document_ref` → second fails.
2. Second with ack + reason → succeeds; fields persisted.
3. Partial payments different refs → both succeed; commitment remaining decreases; source amount unchanged.
