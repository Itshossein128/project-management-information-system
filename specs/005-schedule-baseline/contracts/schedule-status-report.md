# Contract: Schedule status report

**Base**: `/api/v1/projects/{project_id}/schedule-status/`

## Permissions

- Read: project member + `view_activities`

## Get report

`GET .../schedule-status/?as_of=<date optional>`

### Response shape

```json
{
  "as_of": "2026-10-08",
  "forecast_project_finish": "2026-12-01",
  "date_sets": {
    "approved_baseline_id": "<uuid|null>",
    "has_planned": true,
    "has_actual": true,
    "has_forecast": true
  },
  "critical_path": {
    "valid": false,
    "reason_codes": ["incomplete_durations"],
    "message_key": "schedule.critical_path_not_valid",
    "critical_activity_ids": [],
    "near_critical_activity_ids": []
  },
  "milestones": [
    {
      "activity_id": "<uuid>",
      "activity_code": "M-1",
      "activity_name": "Foundation complete",
      "planned_finish": "2026-04-10",
      "forecast_finish": "2026-04-12",
      "actual_finish": null,
      "baseline_finish": "2026-04-10",
      "delay_days": 2
    }
  ],
  "delays": [
    {
      "activity_id": "<uuid>",
      "activity_code": "A-100",
      "is_critical": false,
      "is_near_critical": false,
      "planned_finish": "2026-04-10",
      "forecast_finish": "2026-04-15",
      "baseline_finish": "2026-04-08",
      "actual_finish": null,
      "delay_days": 5
    }
  ]
}
```

### Critical-path rules

- If `critical_path.valid` is `false`, `critical_activity_ids` and `near_critical_activity_ids` MUST be empty arrays; clients MUST show localized “not calculable / not valid” (not a fake path).
- If `valid` is `true`, IDs may be populated from baseline floats/flags per research D6; near-critical default float ≤ 5 days.

### Four-way date clarity

Each milestone/delay row SHOULD expose baseline (approved), planned (current), actual, and forecast finish when data exists (null otherwise). Clients must render four distinct columns/labels — not a single overwritten date.

## Gantt consumer note

`GET .../gantt/` SHOULD include the same `critical_path` validity object (or a compact flag) so the chart does not paint authoritative critical bars when invalid.
