# API Contract: Site Inactivity, Conflict Guard, and Access Hardening

**Feature**: `specs/031-site-inactivity-security` | **Date**: 2026-10-22

## 1. Scope and conventions

Base path: `/api/v1/projects/{project_id}/daily-reports/`. Existing authentication, project membership, lifecycle, and automatic-summary behavior remain unchanged. Requests send `Accept-Language: fa|en`. Reason values, field names, and error codes never change with locale; human messages may be localized.

**Compatibility contract (all already implemented; changes are copy-level only):**

- Stable field names: `site_status`, `inactivity_reason`.
- Stable reason values: `weather`, `holiday`, `strike_or_dispute`, `client_stop_order`, `safety_incident`.
- Stable error code: `inactivity_reason_required`, attached to `inactivity_reason`.

## 2. Read daily-report detail

```http
GET /api/v1/projects/{project_id}/daily-reports/{report_id}/
```

Relevant response fields (existing):

```json
{
  "site_status": "inactive",
  "site_status_label": "غیرفعال",
  "inactivity_reason": "weather",
  "inactivity_reason_label": "نامساعد بودن شرایط جوی"
}
```

- `inactivity_reason` is one approved value or `""` (active reports always carry `""`; the field is never `undefined`).
- `inactivity_reason_label` is `null` when the reason is empty; bilingual clients localize from the stable value and MUST NOT depend on the label as their only translation source.

## 3. Update daily-report header

```http
PATCH /api/v1/projects/{project_id}/daily-reports/{report_id}/
```

Partial payload example:

```json
{
  "site_status": "inactive",
  "inactivity_reason": "client_stop_order"
}
```

Rules:

- Any subset may be sent; validation uses the candidate object produced by merging supplied values with stored values.
- Candidate inactive without a candidate reason → HTTP 400:

```json
{
  "error": {
    "code": "inactivity_reason_required",
    "message": "در صورت تعطیلی کارگاه، انتخاب علت الزامی است.",
    "details": {
      "inactivity_reason": ["در صورت تعطیلی کارگاه، انتخاب علت الزامی است."]
    }
  }
}
```

- The exact message is not a stable contract; top-level `error.code` and the `details` field key are.
- Candidate active → saved record asynchronously carries `inactivity_reason = ""` (server clears it); sending a reason with an active status is accepted and ignored, or rejected by the client surface beforehand.
- Unknown/retired reason strings → standard invalid-choice 400 when inactive; ignored (cleared) when active.

## 4. Lifecycle paths

Submit, review, and approve re-check the same invariant (an inactive report cannot advance without its reason). No new endpoints.

## 5. Permissions (already implemented)

| Operation | Required effective permission | Denial outcome |
|---|---|---|
| `GET /daily-reports/by-date/` (existing date) | `view_reports` | unchanged |
| `GET /daily-reports/by-date/` for a date with no report | `view_reports` | HTTP 404; creates nothing |
| `POST /daily-reports/by-date/` (ensure/rebuild shell) | `edit_reports` | HTTP 403 for view-only members; no record created |
| List/retrieve/child reads/PDF | `view_reports` + IsProjectMember | unchanged |
| Writes (create/update/delete child rows, sync-batch, submit) | `edit_reports` | unchanged |

No member lacking `edit_reports` may cause creation of a daily-report shell; a viewer must not observe newly created rows after their denied attempt.

## 6. Derived summary weather/status reconciliation

Unchanged from the existing implementation: rebuild preserves a validly chosen `inactivity_reason` and clears it when the reconciled status is active; an approved project-level `site_status_override` retains authority. Specialty per-discipline statuses contribute only through the existing derivation; they never carry reasons.

## 7. Corrections, sync, and offline replay

- Correction/version copy carries `inactivity_reason` (existing).
- Header sync comparison includes `inactivity_reason` in conflict fields (existing, tested).
- Offline-queued header mutations are validated on replay by the same rules; an inactive-without-reason queued mutation is rejected with `inactivity_reason_required`.
- The inactive-day activity guard is a client-side confirmation; confirmed rows persist through the normal activity create/update endpoints (no new contract).

## 8. Official PDF

`GET /api/v1/projects/{project_id}/daily-reports/{report_id}/pdf/`

- Inactive + reason present: header table, alongside the inactive status, shows the localized reason label (`get_inactivity_reason_display`).
- Active, or inactive with empty reason: no reason text is rendered (and the empty-reason state cannot be persisted via API paths anyway).
