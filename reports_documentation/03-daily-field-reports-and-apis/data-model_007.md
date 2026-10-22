# Data Model: Daily Site Report Gap Closure

**Feature**: `007-daily-report-gaps`  
**Date**: 2026-10-08

## Entities

### DailyReport (existing — extend)

| Field | Type | Notes |
|-------|------|-------|
| id, project, report_date, shift, weather_*, temps, site_status, notes | existing | |
| prepared_by / submitted_* / reviewed_* / approved_* | existing | |
| status | existing enum | `draft` \| `submitted` \| `under_review` \| `approved` \| `rejected` — **approved = locked** |
| **work_front** | Char(120), blank | **NEW** — header work front / site location |
| **location_notes** | Char(200), blank | **NEW** optional |
| **lineage_id** | UUID | **NEW** — shared across versions; default = id on first create |
| **version_number** | PositiveInt, default 1 | **NEW** |
| **supersedes** | FK → DailyReport, null | **NEW** — prior version |
| **is_current** | Bool, default True | **NEW** — operational current version |
| soft-delete / audit | Yes | `AuditSoftDeleteModel` |

**Invariants**:

- At most one non-deleted row with `is_current=True` per `(project, report_date, shift)`.
- `approved` reports are immutable except via correction that creates a new version.
- Historical versions (`is_current=False`) remain readable; not hard-deleted when superseded.
- Soft-deleted drafts do not block a new current report for the same date/shift.

**Status semantics (presentation)**:

| status | Business meaning |
|--------|------------------|
| draft | Editable draft |
| submitted / under_review | Supervisor confirmation in progress |
| approved | **Locked** |
| rejected | Unlocked editable (like draft for writes) |

### DailyReportActivity (existing — extend)

| Field | Type | Notes |
|-------|------|-------|
| activity_ref, description, qty, unit, zone/block/floor, photo, quantity_measured | existing | |
| **responsible_user** | FK → User, null, SET_NULL | **NEW** |
| **responsible_name** | Char(120), blank | **NEW** — free-text when no user |

**Invariants**:

- If `quantity_measured=True`, `quantity` must be non-null on submit (0 allowed).
- If `quantity_measured=False`, `quantity` MUST be null (not coerced to 0).

### DailyReportLabor (existing — extend)

| Field | Type | Notes |
|-------|------|-------|
| headcount / work_hours / overtime | existing | |
| **absence_count** | PositiveInteger, **null** | **NEW** — null = not recorded; 0 = zero absences |

### DailyReportMaterial (existing — extend)

| Field | Type | Notes |
|-------|------|-------|
| material_ref, description, quantity, unit, transaction_type, activity_ref | existing | |
| transaction_type | enum | existing + **`return`** |
| **consumption_location** | Char(120), blank | **NEW** |

**Invariants**:

- `quantity` required when row exists; never null→0 coercion.
- Return exceeding same-report receipt: warn (advisory).

### DailyReportIncident / Site event (existing — extend)

| Field | Type | Notes |
|-------|------|-------|
| incident_type, description, corrective_action | existing | |
| incident_type | enum | + **`site_instruction`**, **`barrier`** (keep stoppage etc.) |
| **follow_up_owner_user** | FK → User, null | **NEW** |
| **follow_up_owner_name** | Char(120), blank | **NEW** |
| **due_date** | Date, null | **NEW** |

### DailyReportCorrectionRequest (new)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| project | FK → Project | |
| source_report | FK → DailyReport | locked version being corrected |
| result_report | FK → DailyReport, null | new draft/version once created |
| reason | Text | required, min length 10 |
| status | Char | `draft` \| `submitted` \| `approved` \| `cancelled` \| `rejected` |
| requested_by / requested_at | | |
| decided_by / decided_at / decision_notes | | optional |
| soft-delete / audit | Yes | |

**State transitions**:

```text
draft → submitted → approved  (creates/confirms result_report draft; source stays approved, is_current=False; result becomes is_current draft)
                 ↘ rejected / cancelled

result_report then follows normal: draft → submit → … → approved (new locked current)
```

**Invariants**:

- At most one open (`draft` or `submitted`) correction per lineage at a time.
- `source_report.status` must be `approved` and `is_current=True` when opening.
- Creating correction clones children into `result_report` with `version_number = source.version_number + 1`, same `lineage_id`, `supersedes=source`.

### MaterialReconciliationHint (read model — not stored)

Per linked material consumption row: `material_id`, `consumed_qty`, `available_balance` (nullable), `status` ∈ `match` \| `mismatch` \| `insufficient_data`.

## Relationships

```text
DailyReport (lineage) ──< versions (version_number)
       │
       ├── activities / labor / equipment / materials / incidents …
       │
       └── DailyReportCorrectionRequest
                 ├── source_report (approved)
                 └── result_report (new draft version)
```

## Validation rules (submit)

1. Header: `work_front` recommended; if empty → warning (soft) unless project later requires it.
2. Activity measured qty rules as above.
3. Material quantities present and typed including `return`.
4. Equipment start/end pairs (existing).
5. Labor-camp counts (existing if camp rows present).
6. At least one activity OR explicit empty-activity acknowledgement per existing/stricter rules (see spec edge cases).
