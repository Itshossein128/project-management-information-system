# Contract: Contractor Daily Labor Ledger API

## Endpoint

`GET /api/v1/projects/{project_id}/contractors/{contractor_id}/labor-ledger/`

## Response (200 OK)

```json
{
  "project_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "contractor_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
  "contractor_name": "شرکت تأسیساتی پیمان‌گستر",
  "total_person_hours": "64.00",
  "entries": [
    {
      "id": "1fa85f64-5717-4562-b3fc-2c963f66afa1",
      "report_date": "2026-10-28",
      "discipline": "mechanical",
      "activity_row_id": "2fa85f64-5717-4562-b3fc-2c963f66afa2",
      "foreman_count": 2,
      "worker_count": 6,
      "shift_hours": "8.00",
      "total_person_hours": "64.00",
      "status": "APPROVED"
    }
  ]
}
```
