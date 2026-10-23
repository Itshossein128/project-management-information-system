# Contract: Required Unit Templates and Project Activation

**Feature**: `032-unit-report-source-truth`

## Template contract

Existing project-template list/detail/create/update payloads add:

```json
{
  "required_daily_report_units": [
    "buildings",
    "electrical",
    "mechanical",
    "machinery",
    "warehouse",
    "security"
  ]
}
```

Rules:

- Values must be unique canonical units.
- Order is preserved for display but has no effect on completeness.
- New reporting-capable templates require at least one unit.
- Changing a reusable template affects only future activations; existing project configurations are immutable snapshots.
- System-template immutability remains unchanged.

## Project reporting configuration endpoints

Base: `/api/v1/projects/{project_id}/reporting-configurations/`

| Method | Path | Behavior |
|---|---|---|
| `GET` | `?date={date}` | Return the configuration bound/resolved for date, or configuration-incomplete result |
| `GET` | `` | List immutable activation history newest first |
| `POST` | `` | Activate a template snapshot from `effective_from` |
| `POST` | `preview/` | Preview affected date range and required units before activation/backdated correction |

Activation request:

```json
{
  "template_id": "template-uuid",
  "effective_from": "2026-10-23"
}
```

Activation response:

```json
{
  "id": "configuration-uuid",
  "project_id": "project-uuid",
  "source_template": {
    "id": "template-uuid",
    "name": "Residential project"
  },
  "effective_from": "2026-10-23",
  "required_units": ["buildings", "electrical", "mechanical"],
  "supersedes": "prior-configuration-uuid",
  "activated_by": {"id": "...", "display_name": "..."},
  "activated_at": "..."
}
```

## Authorization and safety

- Read: active project member with `view_reports`.
- Preview/activate: active member with `edit_project`.
- Template identity is resolved before the snapshot, but the activated unit list is copied and immutable.
- Normal activation must be later than the latest existing effective date.
- A backdated correction is a separate privileged, explicitly confirmed path. It previews affected summaries, records a reason, and schedules/rebuilds only after confirmation; it is not a silent PATCH.
- The existing globally authenticated template-apply endpoint must not create project reporting configuration unless it also enforces target-project membership and `edit_project`.

## No-configuration response

```json
{
  "state": "configuration_incomplete",
  "configuration": null,
  "required_units": [],
  "message_code": "daily_report_template_required"
}
```

No fallback to legacy `civil/electrical/mechanical` or all six units is permitted.

## Errors

| Code | Meaning |
|---|---|
| `invalid_required_units` | Empty, duplicate, or non-canonical unit list |
| `daily_report_template_required` | No configuration resolves for date |
| `reporting_configuration_date_conflict` | Another activation already owns the effective date |
| `backdated_activation_requires_confirmation` | Normal path attempted a historical insertion |
| `template_activation_forbidden` | Missing target-project authority |
