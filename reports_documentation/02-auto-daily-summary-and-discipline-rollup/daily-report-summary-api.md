# Contract: Daily Report Summary API

**Feature**: `028-auto-daily-report-summary`  
**Base**: `/api/v1/projects/{project_id}/`

## 1. Ensure / open summary by date

**Intent**: Replace blank `POST /daily-reports/` create for project summaries.

| Method | Path | Behavior |
|--------|------|----------|
| `GET` or `POST` | `daily-reports/by-date/?date=YYYY-MM-DD` | Ensure shell for `shift=full`, rebuild if needed, return **detail** payload (same shape as retrieve, plus summary meta) |

**Auth**: Project member with existing daily-report **view** permission (same as list/retrieve today).

**Responses**:
- `200` with DailyReport detail + `aggregation` block (below)
- `400` invalid/missing date
- `403` / `404` per existing tenancy rules

**Idempotent**: Multiple ensures for the same date return the same current report id.

## 2. List (unchanged path, semantic shift)

`GET daily-reports/` — list current summaries by date filters. Does not require prior manual create; rows appear after specialty activity and/or ensure-by-date.

## 3. Disable blank create

`POST daily-reports/` for client-authored blank headers:
- **Reject** with `403` or `400` and message that project daily reports are auto-generated (or internally route only to ensure with required `report_date` and no free-form empty create).

`sync-batch` / offline: must not create blank project dailies as a substitute for the removed button (see research Decision 11).

## 4. Retrieve / patch summary metadata

| Method | Path | Allowed |
|--------|------|---------|
| `GET` | `daily-reports/{id}/` | Full detail + aggregation meta; derived children included |
| `PATCH` | `daily-reports/{id}/` | Summary-owned fields only: overrides, notes, `management_opinion`, weather/site when override semantics apply — **not** bulk replacement of derived tables |
| Submit / review / approve / reject | existing action paths | Unchanged ACL |

## 5. Derived child collections — read-only

For aggregation-owned resources under `daily-reports/{id}/activities|labor|materials|concrete-logs|...`:

| Method | Behavior |
|--------|----------|
| `GET` | Allowed |
| `POST` / `PATCH` / `DELETE` | `400` with clear Persian/English message: edit via specialty (رشته) reports |

Exception: if a product flag later allows non-derived manual rows, only `is_derived=false` rows may be mutated—MVP can reject all child writes on `is_auto_summary` reports.

## 6. Aggregation metadata (detail + by-date)

```json
{
  "aggregation": {
    "is_auto_summary": true,
    "aggregated_at": "2026-10-18T12:00:00Z",
    "is_partial": true,
    "expected_disciplines": ["civil", "electrical", "mechanical"],
    "contributing_disciplines": ["civil"],
    "missing_disciplines": ["electrical", "mechanical"],
    "weather_source": "derived|override",
    "site_status_source": "derived|override"
  }
}
```

Child rows include provenance when derived:

```json
{
  "id": "...",
  "is_derived": true,
  "source_discipline": "civil",
  "source_sub_report": "uuid-or-null"
}
```

## 7. Specialty hooks (sub_reports)

Existing:
- `POST sub-reports/`, detail PATCH/DELETE
- `POST sub-reports/{id}/submit|approve|reject/`

**Contract addition**: After successful submit/approve/reject/delete (and after contribution child writes), server **rebuilds** the project daily summary for that `report_date` and sets `linked_daily_report`.

Specialty create remains allowed. Contribution child APIs (labor/materials/…) follow same project tenancy as parent sub-report.

## 8. Permissions

| Action | Permission (existing or equivalent) |
|--------|-------------------------------------|
| View summary / by-date / list | view reports (e.g. existing list ACL) |
| Patch summary metadata / approve flow | edit/approve reports as today |
| Specialty create/submit | specialty/sub-report edit permissions |
| View summary without specialty edit | **Allowed** (FR-010) |

## 9. Isolation

All IDs resolved inside `{project_id}`. Cross-project `source_sub_report` rejected. Rebuild never reads other projects’ sub-reports.
