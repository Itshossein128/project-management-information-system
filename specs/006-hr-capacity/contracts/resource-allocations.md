# Contract: Resource allocations

**Base**: `/api/v1/projects/{project_id}/resource-allocations/`

## Permissions

- Read: project member + `view_hr`
- Write: project member + `edit_hr`
- Feature toggle (optional): project capability `hr` enabled

## List

`GET .../resource-allocations/`

Query: `person_id`, `wbs_id`, `activity_id`, `status`, `from`, `to` (overlap filter).

Returns non-deleted allocations for the project.

## Create

`POST .../resource-allocations/`

```json
{
  "person_id": "uuid",
  "wbs_id": "uuid|null",
  "activity_id": "uuid|null",
  "start_date": "2026-04-01",
  "end_date": "2026-06-30",
  "role": "site engineer",
  "capacity_percent": "50.00",
  "capacity_hours": null,
  "work_location": "Site A",
  "supervisor_id": "uuid|null",
  "status": "planned",
  "capacity_exception_id": "uuid|null"
}
```

**201** created when within available capacity, or when `capacity_exception_id` references an **approved** exception covering this request.

**409** `capacity_conflict` when over capacity without approved exception:

```json
{
  "code": "capacity_conflict",
  "available": "100.00",
  "committed": "80.00",
  "requested": "50.00",
  "overlapping_allocation_ids": ["uuid"]
}
```

**400** if person inactive; **400** if end < start; **400** if WBS/activity not in project.

## Detail / update / soft-delete

`GET|PATCH|DELETE .../resource-allocations/{allocation_id}/`

PATCH that increases capacity into conflict follows the same 409 / exception rules.

## Person capacity preview

`GET .../resource-allocations/capacity-preview/?person_id=&from=&to=&capacity_percent=`

Returns committed sum, available, and whether conflict would occur (read-only helper for UI).

## Errors

| Code | When |
|------|------|
| `capacity_conflict` | Over capacity without approved exception |
| `person_inactive` | Target person not active |
| `scope_mismatch` | WBS/activity not in project |
| `exception_not_approved` | Provided exception not approved / wrong person |
