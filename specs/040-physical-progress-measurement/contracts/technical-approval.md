# API Contract: Technical Approval Workflow

## Endpoint: `POST /api/v1/projects/{project_pk}/progress/{activity_id}/technical-approve/`

### Permissions Required
- `IsAuthenticated`
- `IsProjectMember`
- User must possess project permission `approve_reports` (Resident Engineer, Project Manager, or Admin).

### Request Headers
- `Authorization: Bearer <jwt_token>`
- `Content-Type: application/json`

### Request Body
```json
{
  "report_date": "1404-01-15",
  "approved_progress_pct": 75.0,
  "basis": "survey_log",
  "evidence_refs": {
    "test_sheet_no": "QC-2024-089",
    "surveyor_signature": "Eng. Moradi",
    "notes": "Verified against physical topographic survey"
  }
}
```

### Response 200 OK
```json
{
  "id": "7f8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
  "activity_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "report_date": "2025-04-04",
  "cumulative_progress_pct": 75.0,
  "approved_progress_pct": 75.0,
  "technical_approved_at": "2026-10-28T09:30:00Z",
  "measurement_version_id": "4b5c6d7e-8f9a-0b1c-2d3e-4f5a6b7c8d9e"
}
```

### Error Responses

#### 400 Bad Request: Photo Only Claim (`photo_not_technical_approval`)
Triggered when `"basis": "photo"` or `"approved_by_photo": true`.
```json
{
  "error": {
    "code": "photo_not_technical_approval",
    "message": "بارگذاری عکس به‌تنهایی معادل تأیید فنی نیست؛ تأیید صریح ناظر الزامی است"
  }
}
```

#### 400 Bad Request: Measurement Not Approved (`measurement_not_approved`)
Triggered when activity has no active approved `ActivityMeasurementVersion`.
```json
{
  "error": {
    "code": "measurement_not_approved",
    "message": "روش اندازه‌گیری این فعالیت هنوز تأیید نشده است."
  }
}
```

#### 403 Forbidden: Insufficient Permission
Triggered when user lacks `approve_reports`.
```json
{
  "detail": "You do not have permission to perform this action."
}
```
