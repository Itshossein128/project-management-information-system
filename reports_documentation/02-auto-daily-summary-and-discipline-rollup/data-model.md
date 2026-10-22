# Data Model: Automated Project Daily Report Summary

**Feature**: `028-auto-daily-report-summary`  
**Date**: 2026-10-18

## Entities

### Project daily report summary (existing `DailyReport`)

| Field / concern | Notes |
|-----------------|--------|
| `project`, `report_date`, `shift` | One **current** summary per project+date with `shift=full` (existing unique constraint) |
| `weather_condition`, `site_status` | Derived or overridden (see rebuild rules) |
| `general_notes` | Summary-owned narrative (issues/remarks may map here or to incidents) |
| Approval fields | Existing `status`, `submitted_*`, `reviewed_*`, `approved_*`, `rejection_reason` |
| `management_opinion` | **Add** TextField (blank default) for Excel «نظر مدیریت» if not already present |
| `weather_override` / `site_status_override` | **Add** optional booleans (or null-sentinel) so rebuild does not clobber explicit overrides |
| `is_auto_summary` | **Add** boolean default True for new ensured rows; marks aggregation-managed shell |
| `aggregated_at` | **Add** nullable DateTime of last successful rebuild |

Relationships: one-to-many child rows (activities, labor, materials, concrete, equipment, labor camp, incidents); one-to-many `discipline_sub_reports` via `linked_daily_report`.

### Specialty-unit daily report (existing `DisciplineSubReport`)

| Field | Notes |
|-------|--------|
| `project`, `report_date`, `discipline` | Unique active per project+date+discipline |
| `weather_condition`, `status` | draft / submitted / approved / rejected |
| `linked_daily_report` | Set to the ensured DailyReport for that date after rebuild |

Children today: `DisciplineSubReportActivity`.

### Specialty contribution extensions (additive)

To feed Excel sections not yet on sub-reports, add child tables (names illustrative):

- **`DisciplineSubReportLabor`**: `labor_category` (indirect/direct), `job_title`, `present_count`, `leave_count` (or shift counts + absence)
- **`DisciplineSubReportMaterial`**: description, quantity, unit, notes (receipt-oriented)
- **`DisciplineSubReportConcrete`**: description/grade, `volume_m3`, location optional
- **`DisciplineSubReportGeneralActivity`**: description, location, quantity, unit, notes
- **`DisciplineSubReportNote`**: `note_type` (issue|visit|other), `text`, `row_number`

All soft-deletable, scoped to `sub_report`, project-isolated via parent.

### Derived DailyReport child rows (existing tables + provenance)

Add nullable provenance on aggregation-owned children (at minimum activities and labor; same pattern for materials/concrete):

| Field | Notes |
|-------|--------|
| `source_sub_report` | FK → `DisciplineSubReport`, SET_NULL |
| `source_discipline` | CharField snapshot of discipline code |
| `is_derived` | Boolean default False; True for rebuild-written rows |

Rebuild deletes/soft-deletes prior `is_derived=True` rows for that report, then inserts fresh derived rows. Non-derived legacy rows (historical manual) remain until migrated or left read-only.

## Validation rules

1. Ensure summary: `shift` must be `full` for auto-summary shells.
2. Rebuild input: only sub-reports with `status ∈ {submitted, approved}` and `is_deleted=False` for that `project`+`report_date`.
3. Labor aggregation key: `(labor_category, normalized job_title)`; sums present/leave (or shift/absence fields mapped to Excel present/leave).
4. Activity/material/concrete: one derived child row per specialty contribution row (union); preserve contractor/location/qty.
5. Child write APIs: if `report.is_auto_summary` and target row would conflict with derivation ownership, reject with localized error.
6. `linked_daily_report` updated for each contributing sub-report to the ensured shell.
7. Overrides: when `weather_override` is true, do not change `weather_condition` during rebuild (same for site).

## State transitions

### DisciplineSubReport

```text
draft → submitted → approved
                 ↘ rejected
```

- Entering `submitted` or `approved`, or leaving the include set (`rejected`, delete): trigger rebuild for that date.
- Draft edits do **not** affect summary until submit (MVP).

### DailyReport (summary shell)

```text
ensure(date) → draft|existing shell
rebuild → refreshes derived children; status unchanged unless product rule says otherwise
user approvals / management_opinion / overrides → persist; survive rebuild
```

Existing submit → review → approve → reject workflow remains available on the shell for project-level closure (FR-009). Approving the summary does **not** require all disciplines present, but UI shows partial banner (FR-012).

## Incompleteness projection (API-computed, not necessarily stored)

- `expected_disciplines`: configured or default set  
- `contributing_disciplines`: distinct disciplines in include set for the date  
- `missing_disciplines`: expected − contributing  
- `is_partial`: `len(missing_disciplines) > 0` OR zero contributors  

## Identity & tenancy

All reads/writes resolve through project scope. Provenance FKs must point at sub-reports of the same project and date as the DailyReport.
