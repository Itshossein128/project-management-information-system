# Contract: Working calendars

**Base**: `/api/v1/projects/{project_id}/working-calendars/`

## Permissions

- Read: project member + `view_activities`
- Write: project member + `edit_activities`

## List / create

`GET .../working-calendars/` — non-deleted calendars for the project.

`POST .../working-calendars/`

```json
{
  "name": "Project standard",
  "is_default": true,
  "work_monday": true,
  "work_tuesday": true,
  "work_wednesday": true,
  "work_thursday": true,
  "work_friday": true,
  "work_saturday": false,
  "work_sunday": false
}
```

**201** created. Setting `is_default=true` clears default on other calendars in the same project.

## Detail / update / soft-delete

`GET|PATCH|DELETE .../working-calendars/{calendar_id}/`

## Exceptions

`GET|POST .../working-calendars/{calendar_id}/exceptions/`

```json
{
  "exception_date": "2026-03-21",
  "is_working": false,
  "name": "Nowruz"
}
```

`PATCH|DELETE .../working-calendars/{calendar_id}/exceptions/{exception_id}/`

**409** `calendar_exception_duplicate` on same date.

## Errors

| Code | When |
|------|------|
| `calendar_in_use` | Soft-delete blocked if activities still reference calendar (or reassign first) |
| `validation_error` | Invalid weekday payload |
