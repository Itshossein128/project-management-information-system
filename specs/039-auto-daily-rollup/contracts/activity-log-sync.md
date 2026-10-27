# Contract: Activity Master Log (Shiraz Excel Sheet 1 Sync)

## Endpoint: `GET /api/v1/projects/{project_pk}/activity-log/`

### Query Parameters
- `date_from` (string, optional): Filter by start date (Jalali or ISO).
- `date_to` (string, optional): Filter by end date (Jalali or ISO).
- `source_discipline` or `discipline` (string, optional): Single value or comma-separated list of disciplines (e.g., `CIVIL,ELECTRICAL`).
- `parcel` (string, optional): Single value or comma-separated list of parcels.
- `zone` (string, optional): Filter by zone.
- `block` (string, optional): Filter by block.
- `floor` (string, optional): Filter by floor.
- `subcontractor` (string, optional): Filter by subcontractor name (case-insensitive substring).
- `approved_only` (boolean, optional, default: `true`): Only include activities from approved reports.
- `page` (integer, default: 1): Page number.

### Success Response (HTTP 200 OK)
```json
{
  "count": 42,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "e4a2d810-0000-4000-8000-000000000001",
      "report_id": "c1f7b093-0100-4000-8000-000000000001",
      "report_date": "1405/08/06",
      "day_name": "Wednesday",
      "source_discipline": "CIVIL",
      "parcel": "قطعه ۱۰",
      "zone": "Zone A",
      "block": "Block 2",
      "floor": "Floor +3",
      "location": "Axis 4-7",
      "activity_description": "بتن‌ریزی سقف طبقه سوم",
      "shift": "shift_1",
      "subcontractor": "شرکت آرماتوربندان جنوب",
      "headcount": 8,
      "quantity": 45.5,
      "unit": "متر مکعب",
      "activity_code": "ACT-102",
      "activity_name": "بتن‌ریزی سازه",
      "report_status": "APPROVED"
    }
  ]
}
```

## Endpoint: `GET /api/v1/projects/{project_pk}/activity-log/filter-options/`

### Success Response (HTTP 200 OK)
```json
{
  "zones": ["Zone A", "Zone B"],
  "blocks": ["Block 1", "Block 2"],
  "subcontractors": ["شرکت آرماتوربندان جنوب", "پیمانکاری برق نوین"],
  "disciplines": ["CIVIL", "ELECTRICAL", "MECHANICAL"],
  "parcels": ["قطعه ۹", "قطعه ۱۰", "قطعه ۱۱"]
}
```

## Cache Invalidation Contract
- Upon calling `approve_report(report, user)` or `reject_report(report, user)`:
  - System MUST immediately purge all Redis keys matching `activity_log:{project_id}:*`.
  - System MUST increment the version key `activity_log_version:{project_id}`.
