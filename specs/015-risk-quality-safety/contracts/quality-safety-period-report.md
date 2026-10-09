# Contract: Quality & Safety Period Report

## API

`GET /api/v1/projects/{project_id}/quality-safety/report/`

Query:

| Param | Required | Notes |
|-------|----------|-------|
| date_from | yes | Inclusive start (Jalali or Gregorian per project date convention) |
| date_to | yes | Inclusive end |

Permission: `view_reports`.

### Response

```json
{
  "project_id": "<uuid>",
  "date_from": "2026-10-01",
  "date_to": "2026-10-31",
  "inspections": [],
  "nonconformities": [],
  "corrective_actions": [],
  "incidents": [],
  "near_misses": [],
  "work_permits": [],
  "trainings": [],
  "counts": {
    "inspections": 0,
    "nonconformities": 0,
    "corrective_actions": 0,
    "incidents": 0,
    "near_misses": 0,
    "work_permits": 0,
    "trainings": 0
  }
}
```

### Rules

- Each section lists matching records (summary fields: id, date, description/title, status, wbs when present).
- Empty period → empty arrays and zero counts; UI MUST show empty state, not a fabricated safety score.
- Does **not** include daily-report incident child rows in v1.
- Does **not** include `RiskEvent` rows (risk register remains separate); optional “top risks” for monthly progress is out of scope here.
