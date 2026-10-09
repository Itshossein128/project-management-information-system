# Contract: Weekly & monthly project period reports

**Base**: `/api/v1/projects/{project_id}/progress-reports/`

Distinct from inventory/department weekly PDF routes.

## Permissions

- List/retrieve: `view_dashboard`
- Generate: `view_dashboard` (or `edit_activities` — prefer membership + view_dashboard; document)
- Override figure: `edit_activities` + required reason

## POST generate

```json
{
  "kind": "weekly",
  "period_start": "2026-10-05",
  "period_end": "2026-10-11"
}
```

```json
{
  "kind": "monthly",
  "period_start": "2026-10-01",
  "period_end": "2026-10-31"
}
```

**Response**: Full report with figures array. Prior report for same period → `status=superseded`.

## GET list / detail

List by kind; detail includes figures with provenance.

### Figure object

```json
{
  "id": "<uuid>",
  "section": "critical_activities",
  "label_key": "progressReports.sections.critical",
  "value": { "...": "structured or scalar" },
  "value_status": "recorded",
  "source_type": "schedule_status",
  "source_id": "<uuid|null>",
  "source_path": "/projects/{id}/schedule-status",
  "source_approved": true,
  "last_updated_at": "2026-10-11T12:00:00Z"
}
```

Missing domain data:

```json
{
  "section": "cost",
  "value": null,
  "value_status": "not_recorded",
  "source_type": "cost",
  "source_approved": false,
  "last_updated_at": null
}
```

## Weekly minimum sections

`critical_activities`, `next_week_plan`, `barriers`, `decisions_required` (plus progress summary if available).

## Monthly minimum sections

`progress_summary`, `baseline_variance`, `cost`, `commitments`, `ipc`, `risks`, `next_month_forecast`.

## POST `…/figures/{figure_id}/overrides/`

```json
{ "new_value": 12.5, "reason": "Corrected transcription from approved IPC" }
```

Creates override audit row; updates displayed value. Direct PATCH of figure without override → `403/400 figure_immutable`.

## SC-004

Client MUST be able to navigate via `source_path` (or equivalent) in one step to the source and show approval status from `source_approved` / source detail.
