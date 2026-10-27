# Contract: Daily Report Lifecycle API

Base report path: `/api/v1/projects/{project_pk}/daily-reports/`

All routes are project-scoped and require authenticated membership. Read routes use the established report-view permission; open/cancel and report mutation routes use the established report-edit permission; review/approval retains the existing approval permission.

## Open correction

`POST /{report_pk}/correction-requests/`

Request:

```json
{ "reason": "Correct the recorded workforce count" }
```

Success: `201 Created`, returning the correction request including `id`, `source_report_id`, `result_report_id`, `reason`, `status`, and timestamps.

Rules: source is approved/current; result is the next draft version/current member of the lineage; active child rows are copied per [data-model.md](../data-model.md). An existing open correction returns `400` / `correction_already_open` and creates no record.

## List correction requests

`GET /{report_pk}/correction-requests/`

Success: `200 OK`, newest first. Each item includes `id`, `source_report_id`, `result_report_id`, `reason`, `status`, and available request/decision metadata.

Client rule: bind cancellation only to an open request whose `result_report_id` equals the displayed current draft id.

## Cancel correction

`POST /api/v1/projects/{project_pk}/correction-requests/{correction_id}/cancel/`

Success: `200 OK`, returning the cancelled request. `source_report_id` is the navigation target.

Rules: server requires project-scoped report-edit permission and verifies that request is open, result exists/current/draft, and source is approved predecessor. It locks participating lifecycle records. On success result becomes non-current and soft-deleted, source becomes current, and request status is `cancelled`.

## Version history

`GET /{report_pk}/versions/`

Success: `200 OK`, ordered by ascending `version_number`.

```json
[
  {
    "report_id": "uuid",
    "report_date": "1405/08/03",
    "shift": "full",
    "version_number": 2,
    "is_current": true,
    "status": "approved",
    "is_locked": true,
    "modifier_name": "نام کامل کاربر",
    "correction_reason": "اصلاح مقدار ثبت‌شده",
    "approved_at": "2026-10-25T10:30:00Z",
    "created_at": "2026-10-25T09:00:00Z"
  }
]
```

`modifier_name`, `correction_reason`, and `approved_at` can be null. A correction reason is attached to its result version only.

## Workflow error contract

The existing application envelope remains authoritative:

```json
{ "error": { "code": "stable_machine_code", "message": "Localized message", "details": {} } }
```

| Action | Condition | Status | Code |
|---|---|---:|---|
| Open correction | An open correction exists | 400 | `correction_already_open` |
| Submit | State is not draft/rejected | 400 | `report_not_in_submittable_state` |
| Reject | Reason absent/whitespace | 400 | `rejection_reason_required` |
| Reject | Trimmed reason under 10 characters | 400 | `rejection_reason_min_length_10` |
| Submit | Measured activity quantity is null | 400 | `quantity_unset_invalid` |

For `quantity_unset_invalid`, the Persian message is exactly: `مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود`. Explicit numeric `0` is valid.
