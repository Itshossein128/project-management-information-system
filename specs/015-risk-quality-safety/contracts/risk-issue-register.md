# Contract: Risk & Issue Register

## APIs

Base: `/api/v1/projects/{project_id}/`

### List / create risk events

`GET|POST /risk-events/`

**Compatibility**: Existing endpoint; request/response **extended** with FR fields. Clients that ignore new fields keep working for barrier/delay/claim.

Permission: `view_reports` (GET), `edit_reports` (POST/PATCH/DELETE).

#### Query (GET)

| Param | Meaning |
|-------|---------|
| event_type | `risk` \| `issue` \| `barrier` \| `delay` \| … |
| status | FR status code |
| severity | legacy enum |
| impact | one of `schedule`,`cost`,`quality`,`safety`,`contract`,`liquidity` |
| search | description/cause/owner text |
| date_from / date_to | on event_date or due_date (document chosen field in ENDPOINTS.md) |

#### Create/update body (risk/issue extras)

```json
{
  "event_type": "risk",
  "description": "Late steel delivery",
  "cause": "Supplier capacity",
  "consequence": "Slab pour slip",
  "response": "Dual-source fabricator",
  "probability_level": 3,
  "impact_severity_level": 4,
  "status": "open",
  "owner": "<user-uuid>",
  "due_date": "2026-11-01",
  "action_text": "Confirm alternate mill",
  "impact_on_schedule": true,
  "impact_on_cost": true,
  "impact_on_quality": false,
  "impact_on_safety": false,
  "impact_on_contract": false,
  "impact_on_liquidity": false,
  "activity": "<uuid|null>",
  "cost_item": "<uuid|null>",
  "contract": "<uuid|null>",
  "related_decision_ref": null,
  "related_decision_note": "",
  "acknowledge_open_actions": false
}
```

#### Response extras

```json
{
  "id": "<uuid>",
  "event_type": "risk",
  "probability_level": 3,
  "impact_severity_level": 4,
  "composite_score": 12,
  "status": "open",
  "impact_on_quality": false,
  "impact_on_safety": false,
  "impact_on_contract": false,
  "impact_on_liquidity": false,
  "open_actions_count": 1
}
```

### Rules

- `event_type=issue` MUST NOT be returned in default “risk-only” UI queries; clients pass `event_type` explicitly.
- If either level is null → `composite_score` MUST be `null` (not 0).
- PATCH to `status=closed` with `open_actions_count > 0` and without `acknowledge_open_actions=true` → **400** `{ "code": "open_actions_warning", ... }`.
- Linked `activity` / `cost_item` / `contract` MUST belong to the same project or validation fails.
- Soft-delete via existing destroy behavior.

### Matrix

`GET /risk-events/matrix/`

- Include only `event_type=risk` with non-closed FR statuses.
- Prefer axes from `probability_level` × `impact_severity_level` when present; else legacy buckets.

### Barriers

`/barriers/` unchanged in path semantics; status values stored as FR set with barrier-facing labels in UI.
