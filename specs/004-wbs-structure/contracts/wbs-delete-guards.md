# Contract: WBS delete dependency guards

**Endpoint**: `DELETE /api/v1/projects/{project_id}/wbs/{wbs_id}/`

## Behavior

Soft-delete only when safe. On conflict return **409** (preferred) or **400** with structured body:

```json
{
  "code": "wbs_has_children | wbs_has_activities | wbs_has_cost | wbs_has_progress | wbs_has_documents",
  "message": "Human-readable localized-capable reason"
}
```

## Dependency checks (any match → reject)

| Code | Condition |
|------|-----------|
| `wbs_has_children` | Non-deleted child nodes exist |
| `wbs_has_activities` | Non-deleted Activity with `wbs_id` |
| `wbs_has_cost` | Non-deleted Budget or ActualCost with `wbs_id` |
| `wbs_has_progress` | ActivityProgress exists for activities of this WBS (if not already blocked by activities policy) |
| `wbs_has_documents` | Non-deleted Document with `related_wbs_id` |

## Success

**204** — node soft-deleted; sibling/project codes renormalized.

## Tests (implement time)

- Node with Budget → delete rejected (`wbs_has_cost`)  
- Node with Document.related_wbs → rejected  
- Node with ActivityProgress (via activity) → rejected  
- Clean leaf → 204  
