# Contract: Quality & HSE Records

## APIs

Base: `/api/v1/projects/{project_id}/`

Permission: `view_reports` (GET), `edit_reports` (mutations).

### Inspections

`GET|POST /inspections/`  
`GET|PATCH|DELETE /inspections/{id}/`

```json
{
  "wbs": "<uuid>",
  "responsible_user": "<uuid>",
  "inspection_date": "2026-10-09",
  "stage": "result",
  "result": "fail",
  "description": "Rebar spacing check"
}
```

**Rules**: `wbs`, `responsible_user`, `inspection_date` required; missing any → 400. WBS and user must be valid for project.

### Nonconformities

`GET|POST /nonconformities/`  
`GET|PATCH|DELETE /nonconformities/{id}/`

```json
{
  "inspection": "<uuid>",
  "description": "Spacing exceeds tolerance",
  "raised_date": "2026-10-09",
  "status": "open"
}
```

### Corrective actions

`GET|POST /corrective-actions/`  
`GET|PATCH|DELETE /corrective-actions/{id}/`

```json
{
  "nonconformity": "<uuid>",
  "description": "Re-tie and re-inspect",
  "responsible_user": "<uuid>",
  "due_date": "2026-10-12",
  "status": "open"
}
```

### HSE events (incident / near miss)

`GET|POST /hse-events/`  
`GET|PATCH|DELETE /hse-events/{id}/`

```json
{
  "kind": "near_miss",
  "event_date": "2026-10-08",
  "description": "Unsecured scaffold plank",
  "wbs": null,
  "status": "open"
}
```

**Rules**: `project` from URL; `kind` and `event_date` required; `wbs` optional.

### Work permits

`GET|POST /work-permits/`  
`GET|PATCH|DELETE /work-permits/{id}/`

### Safety trainings

`GET|POST /safety-trainings/`  
`GET|PATCH|DELETE /safety-trainings/{id}/`

All list endpoints support `date_from` / `date_to` on their primary date field for report building.
