# Contract: Fiscal Period Lock

**Feature**: `002-core-domain-principles`  
**Base path**: `/api/v1/projects/{project_id}/fiscal-period-locks/`

## Endpoints

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `.../fiscal-period-locks/` | `view_project` or finance read | List locks |
| POST | `.../fiscal-period-locks/` | finance/edit elevated | Close a period |
| POST | `.../fiscal-period-locks/{id}/deactivate/` | finance/edit elevated | Soft-unlock with reason |

## Create body

```json
{
  "period_start": "2026-03-21",
  "period_end": "2026-06-21",
  "reason": "Q1 close"
}
```

## Mutation gate (in-scope financial writes)

When creating/updating/deleting in-scope financial records (actual costs, cash transactions, IPC payment side-effects, budget line edits) whose document/effective date falls inside an active lock:

- Without corrective flags → `409` `code: fiscal_period_locked`
- With corrective path:

```json
{
  "corrective": true,
  "correction_reason": "Fix duplicate posting"
}
```

→ allowed; audit must record actor, time, reason.

## Duplicate document warning (related FR-013)

On create of in-scope transactions with `document_ref` / contract number matching an existing active row in the same project:

```json
{
  "warnings": [
    {
      "code": "duplicate_document_ref",
      "message": "..."
    }
  ]
}
```

Finalize requires `acknowledge_warnings: true` when warnings are present; otherwise `400` `warnings_unacknowledged`.

## Errors

| Code | HTTP | When |
|------|------|------|
| `fiscal_period_locked` | 409 | Ordinary mutate in closed period |
| `overlapping_fiscal_lock` | 400 | Overlaps active lock |
| `warnings_unacknowledged` | 400 | Duplicate warning not acknowledged |
