# Contract: Budget versions

**Base**: `/api/v1/projects/{project_id}/budget-versions/`

## Permissions

| Action | Permission |
|--------|------------|
| List / retrieve / compare | `view_costs` |
| Create draft / patch draft lines / submit | `edit_costs` |
| Approve / reject | `approve_costs` |

## Create

`POST …/budget-versions/`

```json
{
  "kind": "initial",
  "name": "Initial FY budget",
  "currency": "IRR",
  "notes": ""
}
```

Kinds: `initial`, `revised`, `final_forecast` (creating `approved` directly is forbidden — use approve).  
**201** with `status=draft`, auto `version_number`.

## Lifecycle

| Method | Path | Effect |
|--------|------|--------|
| PATCH | `…/budget-versions/{id}/` | Update name/notes while draft |
| POST | `…/{id}/submit/` | draft → submitted (requires ≥1 line) |
| POST | `…/{id}/approve/` | → approved; for control-eligible kinds set `is_control` (clear previous); kind may normalize to `approved` or stay `revised`/`final_forecast` |
| POST | `…/{id}/reject/` | → rejected; body `{ "reason": "…" }` |

Approve body optional: `{ "promote_to_control": true }` required to make `final_forecast` the control baseline.

## Compare

`GET …/budget-versions/compare/?left={id}&right={id}&fx_rate=`

Returns per-heading amount diffs. If currencies differ and `fx_rate` missing → **400** `fx_rate_required`.

## List / detail

Includes kind, status, version_number, is_control, currency, line_count, totals.
