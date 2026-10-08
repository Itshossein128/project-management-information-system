# Contract: Navigation & Portfolio

**Feature**: `003-central-data-model`

## Drill-up from daily report

`GET /api/v1/projects/{project_id}/daily-reports/{report_id}/navigation/`

Permission: `view_reports`

### Response 200

```json
{
  "report": { "id": "uuid", "report_date": "...", "status": "..." },
  "activities": [
    {
      "id": "uuid",
      "activity_id": "uuid|null",
      "activity_code": "A1",
      "wbs_id": "uuid|null",
      "wbs_code": "1.2",
      "project_id": "uuid"
    }
  ],
  "project": { "id": "uuid", "project_code": "...", "project_name": "..." }
}
```

Logical steps to project: open report → (optional) pick activity line → project context already in payload (≤3 UI steps).

## Activity detail embeds

Activity retrieve/list items MUST include `project_id`, `wbs_id`, `wbs_code`.

## Portfolio summary

`GET /api/v1/portfolio/summary/`

Permission: authenticated; returns only projects where user has `view_project` or `view_dashboard`.

### Response 200

```json
{
  "projects": [
    {
      "project_id": "uuid",
      "project_code": "...",
      "currency": "IRR",
      "total_budget": 0,
      "total_commitment": 0,
      "total_actual": 0,
      "spi": null,
      "cpi": null
    }
  ],
  "totals": {
    "project_count": 2,
    "note": "Totals only sum rows sharing the same currency; mixed currencies omitted or separated by currency key"
  }
}
```

### Errors

| Code | HTTP | When |
|------|------|------|
| `currency_mix_forbidden` | 400 | Client requests single total across mixed currencies without conversion |
