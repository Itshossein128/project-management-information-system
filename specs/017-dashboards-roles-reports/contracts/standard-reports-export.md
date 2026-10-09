# Contract: Standard Reports & Export Metadata

## Catalog

`GET /api/v1/projects/{project_id}/reports/catalog/`  
(Portfolio-level: `GET /api/v1/portfolio/reports/catalog/`)

Permission: `view_dashboard` or `view_reports`.

```json
{
  "results": [
    {
      "report_type": "weekly_progress",
      "title": "Weekly summary",
      "supported_filters": ["date_from", "date_to", "wbs", "status"],
      "approved_only_default": true
    }
  ]
}
```

Minimum catalog keys (implement iteratively; wrapper same for all):

`daily_site`, `weekly_progress`, `monthly_project`, `portfolio_summary`, `lookahead_plan`, `stakeholder_status`, `changes`, `risk_issue`, `procurement_contract`, `cash_flow`, `budget_variance`

## Run report (JSON)

`GET /api/v1/projects/{project_id}/reports/{report_type}/?date_from=&date_to=&unit=&contract=&wbs=&cbs=&owner=&status=&approved_only=true`

Permission: membership + report-appropriate view permission.

Rules:

- Default `approved_only=true` for daily/weekly/monthly/portfolio types (FR-016).
- If `approved_only=false`, every included unapproved figure/row MUST set `label_unapproved=true` (or equivalent).
- Confidential fields redacted without `view_wage` / `view_sensitive_contacts` as applicable.
- Unsupported filter keys ignored (not 400).

## Export

`POST /api/v1/projects/{project_id}/reports/{report_type}/export/`

```json
{
  "filters": {
    "date_from": "2026-10-01",
    "date_to": "2026-10-07",
    "approved_only": true
  },
  "format": "json"
}
```

Response **201**:

```json
{
  "id": "<export-uuid>",
  "report_type": "weekly_progress",
  "filters": { "date_from": "2026-10-01", "date_to": "2026-10-07", "approved_only": true },
  "extracted_at": "2026-10-10T08:15:00Z",
  "extracted_by": "<user-uuid>",
  "download_url": "/api/v1/projects/{id}/reports/exports/{export-uuid}/download/"
}
```

`GET .../reports/exports/{id}/` returns metadata; download returns file/JSON **including** the same `extracted_at` and `filters` in a header section or envelope (SC-004).

## Rules

- Export versions are immutable.
- 100% of exports must persist and return extraction date + filters.
- Portfolio exports use portfolio base path and `project=null` on the version row.
