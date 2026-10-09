# Contract: IPC Partial Collections

**Feature**: `003-central-data-model`  
**Base**: `/api/v1/projects/{project_id}/ipcs/{ipc_id}/collections/`

## Endpoints

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `.../collections/` | `view_contracts` | List collection rows |
| POST | `.../collections/` | `edit_contracts` | Append partial collection |
| DELETE | `.../collections/{id}/` | `edit_contracts` | Soft-delete collection row |

## Create body

```json
{
  "amount": "1000000",
  "currency": "IRR",
  "fx_rate": null,
  "collected_at": "2026-10-01",
  "reference": "CHK-12",
  "notes": ""
}
```

## Invariants

- IPC `submitted` / approved / net amounts are **not** modified by POST/DELETE collections.
- Response detail for IPC includes `collections: [...]`, `collections_total`, `remaining_receivable` (= approved_net − collections_total).
- Over-collection (collections_total + amount > approved payable) → `400` `code: collection_exceeds_payable` (default).

## Errors

| Code | HTTP | When |
|------|------|------|
| `collection_exceeds_payable` | 400 | Sum would exceed payable |
| `ipc_not_approvable_state` | 409 | Optional: block collections before approve if product policy requires |
