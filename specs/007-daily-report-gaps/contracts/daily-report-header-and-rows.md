# Contract: Daily report header and extended child rows

**Base**: `/api/v1/projects/{project_id}/daily-reports/`

## Permissions

- Read: project member + `view_reports`
- Write (draft/rejected current only): `edit_reports`
- Approve/reject: `approve_reports`

## Create / update header

`POST .../daily-reports/`  
`PATCH .../daily-reports/{report_id}/`

New/updated fields:

```json
{
  "report_date": "2026-04-01",
  "shift": "day",
  "work_front": "North block / Axis A",
  "location_notes": "optional",
  "weather_condition": "sunny",
  "temp_max": "28.0",
  "temp_min": "14.0",
  "site_status": "active",
  "general_notes": ""
}
```

Response includes: `lineage_id`, `version_number`, `is_current`, `supersedes_id`, status, timestamps (`created_at`, `submitted_at`, `approved_at`), and presentation hint `is_locked: true` when status=`approved`.

**409** on duplicate **current** report for same `(report_date, shift)`.

## Activity rows

`POST|PATCH .../daily-reports/{report_id}/activities/`

```json
{
  "activity_ref_id": "uuid|null",
  "activity_description": "Formwork east wall",
  "quantity": "12.5",
  "quantity_measured": true,
  "unit": "m2",
  "zone": "A",
  "block": "B1",
  "floor": "2",
  "responsible_user_id": "uuid|null",
  "responsible_name": "Site lead Reza",
  "photo_file_id": "uuid|null"
}
```

Rules:

- `quantity_measured=false` ⇒ `quantity` must be null
- `quantity_measured=true` ⇒ `quantity` required (0 allowed)
- Never coerce null quantity to 0

## Labor rows

```json
{
  "labor_category": "direct",
  "job_title": "بازوی کارگر",
  "shift_1_count": 4,
  "work_hours": "8.00",
  "absence_count": 1
}
```

`absence_count`: integer ≥ 0, or `null` if not recorded.

## Material rows

```json
{
  "material_ref_id": "uuid|null",
  "material_description": "Cement",
  "quantity": "10",
  "unit": "bag",
  "transaction_type": "return",
  "consumption_location": "Warehouse A",
  "activity_ref_id": "uuid|null"
}
```

`transaction_type`: `receipt` \| `issue` \| `waste` \| **`return`**.

## Site event / incident rows

```json
{
  "incident_type": "barrier",
  "description": "Access road blocked",
  "corrective_action": "Reroute trucks",
  "follow_up_owner_user_id": "uuid|null",
  "follow_up_owner_name": "HSE lead",
  "due_date": "2026-04-02"
}
```

`incident_type` includes at least: existing types + `site_instruction` + `barrier`.

## List filters (additive)

`GET .../daily-reports/` may accept `is_current=true|false` (default true for list UX) and `lineage_id`.

## Errors

| Code | When |
|------|------|
| `duplicate_current_report` | Current report already exists for date/shift |
| `report_locked` | Write against approved/non-editable status |
| `quantity_unset_invalid` | measured=true with null qty, or measured=false with non-null qty |
| `invalid_transaction_type` | Unknown material type |
