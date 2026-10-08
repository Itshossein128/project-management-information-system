# Contract: Material consumption reconciliation hint

**Base**: `/api/v1/projects/{project_id}/daily-reports/{report_id}/materials/reconciliation/`

## Permissions

- Read: project member + `view_reports`

## Get hints

`GET .../materials/reconciliation/`

Returns advisory comparison for **issue/consumption** rows that have `material_ref_id` set. Does **not** mutate inventory. Does **not** block submit.

```json
{
  "items": [
    {
      "material_entry_id": "uuid",
      "material_id": "uuid",
      "material_description": "Cement",
      "consumed_qty": "10.0000",
      "unit": "bag",
      "available_balance": "8.0000",
      "status": "mismatch"
    },
    {
      "material_entry_id": "uuid",
      "material_id": "uuid",
      "consumed_qty": "2.0000",
      "unit": "m3",
      "available_balance": null,
      "status": "insufficient_data"
    }
  ]
}
```

`status`:

| Value | Meaning |
|-------|---------|
| `match` | Balance available and consumed ≤ balance (or equal within project tolerance if defined; default exact ≤) |
| `mismatch` | Balance available and consumed &gt; balance |
| `insufficient_data` | No material_ref, no balance service data, or unit incomparable |

Receipt / return / waste rows may be omitted or included with `status=insufficient_data` unless product later extends rules.

## Errors

| Code | When |
|------|------|
| `not_found` | Report missing / wrong project |
| `403` | Missing `view_reports` |
