# Data Model & State Transitions: Phase A.1 / B02 Version Integrity, Derived-Row Lock & Lineage Preservation

**Feature**: `058-a1-b02-version-integrity`  
**Date**: 2026-11-19  
**Spec**: [spec.md](./spec.md)  
**Migration Impact**: None (reuses existing verified PostgreSQL schema; 0 new migrations).

---

## 1. Entities & Ownership Boundaries

### 1.1 `DailyReport` (Versioned Project Daily Summary)
- **Lineage & Version Fields**: `id` (UUID), `lineage_id` (UUID, shared across versions), `version_number` (`>= 1`), `supersedes` (FK to prior `DailyReport`), `is_current` (bool), `is_deleted` (bool).
- **Derived Identity & Configuration Fields** *(MUST be preserved on correction)*:
  - `is_auto_summary` (bool) — identifies derived project summary (`DEF-B02-01`).
  - `reporting_configuration` (FK to `ProjectReportingConfiguration`) — date-effective six-unit configuration binding (`D02`).
  - `aggregation_fingerprint` (char 64) & `aggregated_at` (datetime) — version-bound aggregation state.
  - B01 contract metadata: `is_synthetic_reference`, `contract_version`, `presentation_profile_code`.
- **Authorized Project-Level Summary Metadata** *(MUST be preserved on correction & rebuild; editable on editable revisions)*:
  - `management_opinion` (text)
  - `weather_override` (bool), `site_status_override` (bool)
  - `weather_condition`, `temp_min`, `temp_max`, `site_status`, `inactivity_reason`, `weather_impact_notes`, `general_notes`, `work_front`, `location_notes`.
- **Version-Bound Workflow & Approval Metadata** *(MUST NOT be copied to new draft revision; remains locked on approved snapshot)*:
  - `status` (`draft` on new revision), `prepared_by` (correction requester), `submitted_by`, `submitted_at`, `reviewed_by`, `reviewed_at`, `approved_by`, `approved_at`, `rejection_reason`.
- **Uniqueness Constraints (Existing)**:
  - `unique_current_daily_report_per_date_shift`: unique `(project, report_date, shift)` where `is_deleted=False AND is_current=True`.
  - `unique_current_contract_daily_report_per_date`: unique `(project, report_date)` where `is_deleted=False AND is_current=True AND contract_version != ''` (ratified `C03`).

### 1.2 `DailyReportWorkedShift` (B01 Contract Worked Shifts)
- **Fields**: `report` (FK), `shift_id` (`1`, `2`, `3`), `actual_duration_hours` (Decimal or `NULL`).
- **Revision Rule**: Cloned from `source_report.worked_shifts` to `result_report` during `open_correction()` so `C03` worked-shift durations remain intact across revisions.

### 1.3 Child Operational Rows (`CHILD_CLONE_SPECS`)
- **Models**: `DailyReportActivity`, `DailyReportLabor`, `DailyReportEquipment`, `DailyReportMaterial`, `DailyReportConcreteLog`, `DailyReportLaborCamp`, `DailyReportIncident`, `DailyReportMachineryRow`, `DailyReportGeneralActivity`, `DailyReportVisit`.
- **Ownership Markers**: `is_derived` (bool, where present), `source_sub_report_id` / `source_report_id` (where present), and/or presence of any `DailyReportDerivedSource` row matching `(daily_report=report, derived_row_id=str(row.id))`.
- **Lock Invariant (`DEF-B02-02`)**: Direct `POST`/`PATCH`/`PUT`/`DELETE` (single-row, bulk/batch, legacy nested, or offline sync) is rejected whenever the report is non-current/deleted/approved, `report.is_auto_summary=True`, or the target row carries any derived ownership marker.

### 1.4 `DailyReportDerivedSource` (Multi-Source Provenance)
- **Fields**: `daily_report` (FK), `derived_kind` (str), `derived_row_id` (str UUID of child row), `source_report` (nullable FK to `DisciplineSubReport`), `source_report_id_snapshot` (UUID), `source_report_version` (int), `source_unit` (str), `source_row_kind` (str), `source_row_id` (str), `contribution_value` (Decimal or `NULL`), `ordinal` (int).
- **Uniqueness Constraint (Existing)**: `unique_derived_source_key` on `(derived_kind, derived_row_id, source_report_id_snapshot, source_row_kind, source_row_id)`.
- **Remapping Invariant (`DEF-B02-03`)**: During `open_correction()`, every `DailyReportDerivedSource` on `source_report` is cloned to `result_report` with `derived_row_id` remapped via `id_map[old_row_id] -> new_row_id`. If a derived row had `N >= 2` sources in `v1`, the cloned row in `v2` has all `N` sources pointing to the same `N` unit sources with `derived_row_id = str(v2_row.id)`.

### 1.5 `DailyReportCorrectionRequest`
- **Fields**: `project`, `source_report` (`v_n`), `result_report` (`v_{n+1}`), `reason` (`len(reason.strip()) >= 10`), `status` (`draft`, `submitted`, `approved`, `cancelled`, `rejected`), `requested_by`, `requested_at`, `decided_by`, `decided_at`.
- **Concurrency Invariant**: `open_correction()` locks `source_report` (`select_for_update()`) inside `@transaction.atomic` and checks `OPEN_CORRECTION_STATUSES` on `lineage_id` so concurrent requests cannot create duplicate revisions.

---

## 2. State Transitions & Rebuild Eligibility Matrix

### 2.1 Revision Lifecycle Transitions
1. **Open Correction (`v1 [approved, current]` → `v1 [approved, non-current]` + `v2 [draft, current]`)**:
   - Preconditions: `v1.status == APPROVED`, `v1.is_current == True`, `v1.is_deleted == False`, no open correction for `lineage_id`, `len(reason.strip()) >= 10`.
   - Effects: `v1.is_current = False`; `v2` created with `version_number = v1.version_number + 1`, `supersedes = v1`, `is_current = True`, `status = DRAFT`, preserving `is_auto_summary`, `management_opinion`, `weather_override`, `site_status_override`, `reporting_configuration`, `aggregation_fingerprint`, `aggregated_at`, B01 contract metadata, `worked_shifts`, all child rows, and all remapped `DailyReportDerivedSource` rows.
2. **Authorized Rebuild on Open Draft Revision (`v2 [draft, current]`)**:
   - Triggered by source unit sub-report submit/approve/reject (`_trigger_rebuild`) or explicit `POST .../rebuild/`.
   - Effects: Re-aggregates eligible current same-project/same-date `submitted`/`approved` unit sub-reports; refreshes derived child rows and `DailyReportDerivedSource`; preserves `is_auto_summary`, `management_opinion`, `weather_override`, and `site_status_override`.
3. **Approve Revision (`v2 [submitted/under_review, current]` → `v2 [approved, current]`)**:
   - Preconditions: Valid role permission (`approve_reports`), active project membership, separation of duties (approver != submitter where enforced), valid site-status inactivity reason.
   - Effects: `v2.status = APPROVED`, `v2.approved_by/at` set, `v2.is_current = True`; `DailyReportCorrectionRequest.status = APPROVED`; activity-log cache invalidated; official activity master log now counts ONLY `v2` (excluding `v1` because `v1.is_current == False`).
4. **Cancel Correction (`v2 [draft, current]` → `v2 [soft-deleted, non-current]` + `v1 [approved, current]`)**:
   - Preconditions: Correction request is open, `v2` is still `DRAFT` and `is_current=True`, `v1` is `APPROVED` and `is_current=False`.
   - Effects: `v2.is_current = False`, `v2.soft_delete()`; `v1.is_current = True` restored with its untouched snapshot, derived-summary identity, child rows, provenance, opinion, and overrides; correction request marked `CANCELLED`; activity-log cache invalidated.

### 2.2 Rebuild Target Rejection Matrix (`FR-011`, `SC-006`, `DEF-B02-06`)

| Target Report State | Explicit Target (`report=<obj>` or `POST .../rebuild/`) | Implicit Unit-Trigger (`report=None`) | Resulting Mutation |
| :--- | :--- | :--- | :--- |
| `is_deleted=True` (deleted/cancelled) | **REJECT** (`ValidationError`, `code='rebuild_target_deleted'`) | Excluded by query (`is_deleted=False`) | **0 mutations** |
| `is_current=False` (historical / superseded / archived) | **REJECT** (`ValidationError`, `code='historical_rebuild_rejected'`) | Excluded by query (`is_current=True`) | **0 mutations** |
| `status=APPROVED, is_current=True` | **REJECT** (`ValidationError`, `code='report_locked'`) | **NO-OP return** (snapshot stays immutable; drift surfaced via `FR-012`) | **0 mutations** |
| `status in {SUBMITTED, UNDER_REVIEW}, is_current=True` | **REJECT** (`ValidationError`, `code='report_not_editable'`) | **NO-OP return** (or only rebuilds editable states) | **0 mutations** |
| `status in {DRAFT, REJECTED}, is_current=True, is_deleted=False` | **ALLOW** (`FR-009` authorized rebuild) | **ALLOW** (`FR-009` automatic rebuild) | Derived rows & provenance refreshed; opinion & overrides preserved |

### 2.3 Official Activity Master Log Query Policy (`FR-013`–`FR-015`, `DEF-B02-05`)
- **Official Operational Query (`approved_only != 'false'`)**: `DailyReportActivity` where `is_deleted=False`, `report__is_deleted=False`, `report__status=ReportStatus.APPROVED`, `report__is_current=True`.
- **Historical Version Inspection**: Dedicated `GET /api/v1/projects/{project_pk}/daily-reports/{pk}/versions/` endpoint (lists all versions in `lineage_id` with version number, status, `is_current`, timestamps, and correction history), never mixed into official activity-log totals.
