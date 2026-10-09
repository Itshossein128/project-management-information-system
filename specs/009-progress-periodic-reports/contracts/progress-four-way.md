# Contract: Four-way progress display

**Base**: `/api/v1/projects/{project_id}/progress/` (extend existing)

## Permissions

- Read: `view_dashboard` (existing)
- Manual write: `edit_activities`
- Technical approve: `approve_reports` or `edit_activities` (document chosen code)

## GET progress snapshot / activities list (additive fields)

Each activity row MUST include:

```json
{
  "activity_id": "<uuid>",
  "wbs_id": "<uuid>",
  "wbs_code": "1.1.1",
  "period_progress_pct": 5.0,
  "cumulative_progress_pct": 42.0,
  "planned_progress_pct": 50.0,
  "approved_progress_pct": 40.0,
  "measurement_method": "quantity",
  "measurement_version_id": "<uuid|null>",
  "measurement_status": "approved",
  "period_start": "2026-10-01",
  "period_end": "2026-10-07"
}
```

Labels in UI/i18n MUST distinguish the four values (never conflate cumulative recorded with approved).

Query params (optional): `period_start`, `period_end` (default: current week for period column).

## POST `progress/manual/` (behavior change)

Existing endpoint; additional rules:

- Requires approved measurement definition → else `400 measurement_not_approved`
- Stores `measurement_version_id`
- May set period + cumulative recorded; does **not** auto-set `approved_progress` unless project policy auto-approves (default: no)
- Rejects over-100% per [progress-validation.md](./progress-validation.md)

## POST `progress/{activity_id}/technical-approve/` (new)

Marks latest recorded progress as technically approved → updates `approved_progress`. Requires auth permission. Photo attachment alone is insufficient (server ignores photo-as-approval).

## Regression

S-curve and KPI endpoints remain; may expose approved vs planned distinctly where useful without removing existing fields.
