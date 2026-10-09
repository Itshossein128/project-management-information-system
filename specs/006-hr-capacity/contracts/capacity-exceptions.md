# Contract: Capacity exceptions

**Base**: `/api/v1/projects/{project_id}/capacity-exceptions/`

## Permissions

- Read: project member + `view_hr`
- Create/submit: project member + `edit_hr`
- Approve/reject: project member + `approve_hr`

## List / create

`GET .../capacity-exceptions/`

`POST .../capacity-exceptions/`

```json
{
  "person_id": "uuid",
  "reason": "Peak pour week — temporary double assignment",
  "requested_capacity_percent": "50.00",
  "start_date": "2026-04-01",
  "end_date": "2026-04-15",
  "allocation_id": null
}
```

Creates `draft` (or `submitted` if `submit: true`).

## Submit

`POST .../capacity-exceptions/{id}/submit/`

Status → `submitted`. Reason required.

## Approve / reject

`POST .../capacity-exceptions/{id}/approve/`

```json
{ "decision_notes": "Approved for two weeks" }
```

Status → `approved`; sets `decided_by`, `decided_at`. Soft SoD: warn if approver == requester (v1 may still allow for admin).

`POST .../capacity-exceptions/{id}/reject/`

```json
{ "decision_notes": "Reschedule instead" }
```

Status → `rejected`.

## Use with allocation

After approve, client `POST` allocation with `capacity_exception_id` (see [resource-allocations.md](./resource-allocations.md)). Server sets `has_capacity_exception=True` and links the exception.

## Errors

| Code | When |
|------|------|
| `invalid_status_transition` | e.g. approve from draft without submit |
| `permission_denied` | Missing `approve_hr` |
| `already_decided` | Approve/reject on terminal status |
