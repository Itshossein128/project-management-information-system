# Contract: WBS tree & node fields

**Base**: `/api/v1/projects/{project_id}/wbs/`

## List tree

`GET .../wbs/` — nested tree of non-deleted nodes.

Each node includes at least:

| Field | Notes |
|-------|-------|
| wbs_id | UUID |
| wbs_code, wbs_name | |
| description | |
| depth | |
| weight_physical, weight_financial | optional |
| responsible | UUID or null |
| acceptance_criteria | string |
| status | enum string |
| children | nested |

## Create

`POST .../wbs/`

```json
{
  "parent_id": "<uuid|null>",
  "wbs_code": "1.2",
  "wbs_name": "Foundations",
  "description": "",
  "responsible": "<user-uuid|null>",
  "acceptance_criteria": "Concrete poured and cured",
  "status": "active",
  "weight_physical": null,
  "weight_financial": null
}
```

**201** with created node. **400** on duplicate code / invalid parent.

## Update

`PATCH .../wbs/{wbs_id}/` — name, description, weights, responsible, acceptance_criteria, status (not parent; use move).

## Move

`POST .../wbs/{wbs_id}/move/`

```json
{ "new_parent_id": "<uuid>", "position": "last-child" }
```

**400/409** with `code: wbs_cycle` if new parent is self or descendant.

## Permissions

- Read: project member + view WBS permission  
- Write: project member + edit WBS permission  

## Tests (implement time)

- Create 3-level tree; set responsible + acceptance on leaf; list embeds fields  
- Move under descendant → rejected  
