# API Contract: Daily Report Correction Lineage and Lossless Cloning

**Feature**: `035-correction-lineage-cloning`  
**Base Path**: `/api/v1/projects/{project_pk}/`  

---

## 1. Request Correction for Approved Report

Initiates a correction draft from an approved current report, cloning all active child rows losslessly.

- **Method**: `POST`
- **Path**: `/api/v1/projects/{project_pk}/daily-reports/{report_pk}/correction-requests/`
- **Permission**: `edit_reports` (Project Member)

### Request Payload
```json
{
  "reason": "اصلاح مقادیر کارکرد آرماتوربندی بر اساس صورت‌جلسه جدید کارگاهی"
}
```

### Validation Constraints
- `reason`: String, required, minimum length 10 characters after trimming.
- Target report must have `status == "approved"` and `is_current == true`.

### Response: 201 Created
```json
{
  "id": "c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c",
  "project": "283ee667-3849-4a0d-905b-561abc24aa41",
  "source_report_id": "8a7b6c5d-4e3f-2a1b-0c9d-8e7f6a5b4c3d",
  "result_report_id": "ef929847-9935-4580-922a-7395b860e63b",
  "reason": "اصلاح مقادیر کارکرد آرماتوربندی بر اساس صورت‌جلسه جدید کارگاهی",
  "status": "submitted",
  "requested_by_name": "علی محمدی",
  "requested_at": "2026-10-27T08:30:00Z"
}
```

### Errors
- **400 Bad Request** (`correction_already_open`):
  ```json
  {
    "detail": "درخواست اصلاح باز برای این گزارش وجود دارد",
    "code": "correction_already_open"
  }
  ```
- **400 Bad Request** (`reason_required`):
  ```json
  {
    "reason": "دلیل اصلاح باید حداقل ۱۰ کاراکتر باشد",
    "code": "reason_required"
  }
  ```
- **400 Bad Request** (`report_not_locked`):
  ```json
  {
    "detail": "فقط گزارش قفل‌شده جاری قابل اصلاح است",
    "code": "report_not_locked"
  }
  ```

---

## 2. Cancel Open Correction

Cancels an in-progress correction draft, soft-deletes the draft version, and reinstates the source report as the current approved record.

- **Method**: `POST`
- **Canonical Path**: `/api/v1/projects/{project_pk}/correction-requests/{correction_id}/cancel/`
- **Alias Path**: `/api/v1/projects/{project_pk}/daily-reports/correction-requests/{correction_id}/cancel/`
- **Permission**: `edit_reports` (Project Member)

### Request Payload
Empty body `{}`.

### Response: 200 OK
```json
{
  "id": "c1a2b3c4-d5e6-7f8a-9b0c-1d2e3f4a5b6c",
  "status": "cancelled",
  "source_report_id": "8a7b6c5d-4e3f-2a1b-0c9d-8e7f6a5b4c3d",
  "result_report_id": "ef929847-9935-4580-922a-7395b860e63b",
  "decided_by_name": "علی محمدی",
  "decided_at": "2026-10-27T08:45:00Z"
}
```

### Errors
- **400 Bad Request**:
  - `فقط درخواست اصلاح باز قابل لغو است` (if already approved or cancelled)
  - `گزارش نتیجه دیگر پیش‌نویس نیست و قابل لغو نیست` (if draft was submitted or is version 1)
- **403 Forbidden**: Viewer role or non-project member.
- **404 Not Found**: Correction request does not exist in the project scope.

---

## 3. Version History Retrieval

Returns all iterations belonging to a report lineage, enriched with modifier attribution, justification reason, and approval timestamps.

- **Method**: `GET`
- **Path**: `/api/v1/projects/{project_pk}/daily-reports/{report_pk}/versions/`
- **Permission**: `view_reports` (Project Member)

### Response: 200 OK
```json
[
  {
    "id": "8a7b6c5d-4e3f-2a1b-0c9d-8e7f6a5b4c3d",
    "version_number": 1,
    "status": "approved",
    "is_current": false,
    "modifier_name": "سارا حسینی",
    "correction_reason": null,
    "approved_at": "2026-10-25T14:15:00Z",
    "created_at": "2026-10-25T08:00:00Z"
  },
  {
    "id": "ef929847-9935-4580-922a-7395b860e63b",
    "version_number": 2,
    "status": "approved",
    "is_current": true,
    "modifier_name": "علی محمدی",
    "correction_reason": "اصلاح مقادیر کارکرد آرماتوربندی بر اساس صورت‌جلسه جدید کارگاهی",
    "approved_at": "2026-10-27T09:30:00Z",
    "created_at": "2026-10-27T08:30:00Z"
  }
]
```
