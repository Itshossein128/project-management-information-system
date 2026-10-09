# Contract: Role Dashboard Packs

## APIs

### Resolve pack for current user (project)

`GET /api/v1/projects/{project_id}/dashboard/pack/`

Permission: `view_dashboard` + membership.

Optional query: `pack=` to request a specific pack id if the user is eligible; default = highest-priority pack from member roles.

```json
{
  "pack_id": "project_manager",
  "project_id": "<uuid>",
  "groups": [
    {
      "group_key": "schedule",
      "title": "Plan vs actual",
      "figures": [ { "figure_key": "progress.plan_vs_actual", "value": 0.12, "status": "ok", "drill": { "href": "..." } } ]
    }
  ]
}
```

### Executive / portfolio strip

`GET /api/v1/portfolio/dashboard/`

Permission: authenticated; **only projects where user is an active member**.

```json
{
  "pack_id": "executive",
  "projects": [
    { "project_id": "<uuid>", "project_name": "...", "figures": [ /* portfolio status, liquidity need, high risks, … */ ] }
  ]
}
```

Finance user on A+B must not receive project C.

## Rules

- Pack indicator set is role-filtered server-side (not client-trusted).
- Viewer may read packs but UI must not expose approve actions (API approve endpoints still SoD/permission gated).
- Inactive capability → figure `status=inactive` inside pack.
- Dashboards are read-only (GET only for pack endpoints).
