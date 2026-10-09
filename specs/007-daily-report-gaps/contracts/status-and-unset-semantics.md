# Contract: Status presentation and unset-vs-zero semantics

## Status presentation

API may keep enum values `draft|submitted|under_review|approved|rejected`.

Responses SHOULD include:

```json
{
  "status": "approved",
  "is_locked": true,
  "status_label_key": "dailyReport.status.locked"
}
```

UI (fa/en) MUST present `approved` as locked / «قفل‌شده» for end users. Submit/review labels may map to supervisor confirmation language.

Timestamps MUST remain distinct in responses:

- `report_date` — calendar day of the shift
- `created_at` — registration time
- `submitted_at` / `reviewed_at` / `approved_at` — workflow times

## Unset vs zero

| Field | Unset | Zero |
|-------|-------|------|
| Activity `quantity` | `null` with `quantity_measured=false` | `0` with `quantity_measured=true` |
| Material `quantity` | row absent or reject blank — never store null as 0 | `0` explicit |
| Labor `absence_count` | `null` | `0` |

Submit validation error shape:

```json
{
  "code": "quantity_unset_invalid",
  "fields": {
    "activities": [{ "id": "uuid", "error": "measured_quantity_required" }]
  }
}
```

Clients MUST NOT send `quantity: 0` to mean “not measured.”

## Write guards

| Report state | Header/child writes |
|--------------|---------------------|
| draft, rejected | allowed (`edit_reports`) |
| submitted, under_review | denied |
| approved (`is_locked`) | denied — use correction request |
| non-current historical | denied |

Offline `sync-batch` MUST return `conflict` (not merge) when server current report is locked/approved.
