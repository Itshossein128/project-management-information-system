# Contract: KPI Drill-Through

## APIs

### Enriched project KPIs

`GET /api/v1/projects/{project_id}/kpis/?as_of=`

Permission: `view_dashboard` (+ project membership).

Response figures (additive to existing KPI payload) include provenance blocks:

```json
{
  "figures": [
    {
      "figure_key": "evm.spi",
      "value": 0.92,
      "status": "ok",
      "source_approved": true,
      "last_updated_at": "2026-10-09T12:00:00Z",
      "label_unapproved": false,
      "drill": { "href": "/api/v1/projects/{id}/kpis/drill/?figure_key=evm.spi&as_of=2026-10-09" }
    },
    {
      "figure_key": "module.disabled_example",
      "value": null,
      "status": "inactive",
      "source_approved": false,
      "last_updated_at": null,
      "drill": null
    }
  ]
}
```

Existing top-level KPI fields may remain for compatibility; UI prefers `figures[]`.

### Drill list

`GET /api/v1/projects/{project_id}/kpis/drill/?figure_key=&as_of=&approved_only=true`

Permission: `view_dashboard`.

```json
{
  "figure_key": "finance.commitment_total",
  "results": [
    {
      "id": "<uuid>",
      "display": "Commitment PO-12",
      "amount": 1000,
      "approval_status": "approved",
      "approved": true,
      "last_updated_at": "2026-10-01T08:00:00Z",
      "source_path": "/projects/.../costs/..."
    }
  ]
}
```

## Rules

- Unknown `figure_key` → **404** `{ "code": "unknown_figure_key" }`.
- `approved_only=true` (default for standard report consumers): exclude unapproved constituents; if a dashboard figure must show unapproved, set `label_unapproved=true` and only when explicitly requested.
- Disabled capability → `status=inactive`, `value=null`, no fabricated `0`.
- Drill never mutates domain data.
