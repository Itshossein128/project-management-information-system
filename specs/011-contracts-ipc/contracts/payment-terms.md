# Contract: Payment Terms

## API

### Create / Update Contract

`POST|PATCH /api/v1/projects/{project_id}/contracts/`

Body (additive):

```json
{
  "payment_terms": "Net 30 after approval; retention released at final certificate"
}
```

### Response

Includes `payment_terms` string (may be empty).

## UI

- Contract create/edit form: multiline textarea labeled payment terms (i18n).
- Contract detail: display payment terms when non-empty.
