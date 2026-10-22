# API Contract: Daily Report Header and Weather Controls

## 1. Scope and conventions

Base project path:

```text
/api/v1/projects/{project_id}
```

All identifiers are language-independent. Display labels are localized by the API/client. Existing authentication, project membership, soft-delete filtering, and error-envelope conventions remain in force.

## 2. Shared values

### Weather condition

```json
["clear", "cloudy", "rainy", "snowy", "stormy"]
```

`sunny`, `partly_cloudy`, and `foggy` are migration-only inputs. They are invalid in new API requests after deployment.

### Site status

```json
["active", "inactive"]
```

### Inactivity reason

```json
[
  "weather",
  "holiday",
  "strike_or_dispute",
  "client_stop_order",
  "safety_incident"
]
```

## 3. Daily report date lookup and ensure

### Read an existing full-day summary

```http
GET /api/v1/projects/{project_id}/daily-reports/by-date/?date=2026-10-22
```

- Required project permission: `view_reports`.
- Returns only the current, non-deleted `shift=full` report for the requested project/date.
- Must not create, rebuild, version, or otherwise mutate a report.
- Returns `404` when no summary exists.
- A user with only `view_reports` can read an existing report but cannot create a missing one.

### Ensure or rebuild a full-day summary

```http
POST /api/v1/projects/{project_id}/daily-reports/by-date/
Content-Type: application/json

{"date":"2026-10-22"}
```

- Required project permission: `edit_reports`.
- Ensures the one current `shift=full` report and rebuilds derived content from eligible specialty reports.
- Repeated calls are logically idempotent: they return the same current summary rather than creating additional shells.
- The transaction locks the authoritative project row before the existence check/create/rebuild sequence; the database uniqueness rule remains the second defense.
- A viewer-only request fails authorization before any write occurs.

### Raw collection creation remains blocked

```http
POST /api/v1/projects/{project_id}/daily-reports/
```

Response:

```json
{
  "error": {
    "code": "auto_summary_only",
    "message": "Daily reports are created from specialty reports.",
    "details": {}
  }
}
```

HTTP status is `400`. This endpoint never becomes the replacement for `by-date`.

## 4. Header representation

The detail/header response exposes at least:

```json
{
  "id": "uuid",
  "project": "uuid",
  "report_date": "2026-10-22",
  "shift": "full",
  "weather_condition": "cloudy",
  "weather_condition_label": "ابری",
  "temp_min": 12.5,
  "temp_max": 21.0,
  "weather_impact_notes": "بارندگی صبحگاهی باعث کندی خاکبرداری شد.",
  "site_status": "inactive",
  "site_status_label": "تعطیل",
  "inactivity_reason": "weather",
  "inactivity_reason_label": "نامساعد بودن شرایط جوی",
  "weather_override": true,
  "site_status_override": true
}
```

Blank optional text is serialized consistently with existing API conventions. The machine value, not the localized label, is accepted in write payloads.

## 5. Header update

Existing detail/header update routes accept a partial payload such as:

```http
PATCH /api/v1/projects/{project_id}/daily-reports/{report_id}/
Content-Type: application/json

{
  "weather_condition": "stormy",
  "temp_min": -2.0,
  "temp_max": 4.5,
  "weather_impact_notes": "گرد و غبار دید ماشین‌آلات را محدود کرد.",
  "site_status": "inactive",
  "inactivity_reason": "safety_incident"
}
```

The allowlist used for auto-summary metadata updates includes `weather_impact_notes` and `inactivity_reason`. Derived row payloads and `shift` remain non-editable through header updates.

Validation uses the effective object after combining the stored instance with partial input:

- Each temperature is nullable or within the inclusive range `-40..60`.
- When both are non-null, `temp_max >= temp_min`.
- An inactive report requires one allowed `inactivity_reason`.
- Saving an active report clears a stale `inactivity_reason` server-side.

### Reversed temperature range

```json
{
  "error": {
    "code": "temp_max_must_be_gte_temp_min",
    "message": "Maximum temperature must be greater than or equal to minimum temperature.",
    "details": {
      "temp_max": ["Maximum temperature must be greater than or equal to minimum temperature."]
    }
  }
}
```

HTTP status is `400`; the error is attached to `temp_max`.

### Missing inactivity reason

```json
{
  "error": {
    "code": "inactivity_reason_required",
    "message": "An inactivity reason is required when the site is inactive.",
    "details": {
      "inactivity_reason": ["An inactivity reason is required when the site is inactive."]
    }
  }
}
```

HTTP status is `400`; the error is attached to `inactivity_reason`. Locale negotiation may translate messages but never changes codes or field keys.

## 6. Derived summary rules

- Weather is the highest-severity nonblank specialty value: `stormy > snowy > rainy > cloudy > clear`.
- `weather_override=true` preserves the project-level weather during rebuild.
- Any eligible inactive specialty report derives an inactive project summary unless `site_status_override=true`.
- Rebuild never invents an inactivity reason. It preserves an existing valid reason while the effective status remains inactive and clears it when the effective status becomes active.
- `weather_impact_notes` is never derived or overwritten by rebuild.
- An incomplete derived inactive draft may be returned for classification, but submit/review/approve and explicit header save enforce `inactivity_reason_required`.

## 7. Other weather-bearing APIs

### Standalone weather log

Weather-log create/update/read uses exactly the same five weather values and temperature rules. `weather_condition` remains required. A cross-field failure is attached to `temp_max` with `temp_max_must_be_gte_temp_min`.

### Specialty reports

`DisciplineSubReport.weather_condition` accepts the same five values and remains optional. This feature does not add `weather_impact_notes` or `inactivity_reason` to specialty reports.

## 8. Sync, correction, and lifecycle

- Sync-batch header comparison and conflict details include `weather_impact_notes` and `inactivity_reason`.
- Offline clients upgraded from old versions normalize retired weather values before sync. The API rejects retired values sent by non-upgraded clients.
- A correction/version copy carries weather, temperatures, weather-impact notes, site status, inactivity reason, override flags, and existing summary-owned management metadata.
- Submit, review, and approve transitions reject an inactive summary without a valid reason using `inactivity_reason_required`.

## 9. PDF output

The official daily-report PDF header/specification table includes:

- localized weather label;
- minimum and maximum temperatures;
- site status;
- localized inactivity reason when inactive;
- weather-impact notes when nonblank.

The PDF must not expose raw enum identifiers to end users. Automated verification asserts extracted content in addition to the existing PDF-signature smoke check.
