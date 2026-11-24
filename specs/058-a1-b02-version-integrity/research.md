# Phase 0 Research & Design Decisions: Phase A.1 / B02 Version Integrity, Derived-Row Lock & Lineage Preservation

**Feature**: `058-a1-b02-version-integrity`  
**Date**: 2026-11-19  
**Spec**: [spec.md](./spec.md)

## Decision 1: Preserving Derived-Summary Identity, Summary Metadata & B01 Contract Fields in `open_correction` (`DEF-B02-01`, `DEF-B02-04`)

- **Decision**: Extend `open_correction()` in `apps/api/core/field_reports/services/correction_service.py` to copy all summary-owner and contract-level fields from `source_report` to the new draft revision `result`, while keeping approval/workflow fields (`submitted_by`, `submitted_at`, `reviewed_by`, `reviewed_at`, `approved_by`, `approved_at`, `rejection_reason`) clean/unset for the new draft version. Specifically preserve:
  - Derived identity: `is_auto_summary`
  - Authorized management/override metadata: `management_opinion`, `weather_override`, `site_status_override`
  - Aggregation/configuration metadata: `reporting_configuration`, `aggregation_fingerprint`, `aggregated_at`
  - B01 contract header metadata: `is_synthetic_reference`, `contract_version`, `presentation_profile_code`, plus cloning `DailyReportWorkedShift` rows (`worked_shifts`) so `C03` worked-shift durations survive revision.
- **Rationale**: Direct inspection of `correction_service.py:136-162` confirmed that `open_correction` omitted all of these fields, causing `is_auto_summary` to revert to `False` (`DEF-B02-01`) and silently wiping `management_opinion`, `weather_override`, `site_status_override`, `reporting_configuration`, `aggregation_fingerprint`, `aggregated_at`, and B01 contract metadata (`DEF-B02-04`). Keeping workflow/approval timestamps unset ensures approval snapshots and fingerprints remain strictly bound to each version (`W05`, `W06`).
- **Alternatives considered**:
  - *Re-running aggregation immediately inside `open_correction` instead of cloning*: Rejected because source unit sub-reports might already have drifted after version 1 approval; a correction revision must initially capture the exact approved version's state and provenance (`W02`, `W04`), then refresh only upon an authorized unit edit/rebuild (`FR-009`).

## Decision 2: Complete Multi-Source `DailyReportDerivedSource` Remapping (`DEF-B02-03`)

- **Decision**: Update `_clone_children(source, target)` in `correction_service.py` to record an `id_map: dict[str, str]` mapping `str(old_row.id) -> str(new_row.id)` across all 10 cloned child models in `CHILD_CLONE_SPECS` (plus `str(source.id) -> str(target.id)` for any report-scoped provenance). Immediately after cloning child rows, clone every `DailyReportDerivedSource` row belonging to `source` to `target` with `derived_row_id = id_map[old_derived_row_id]` (preserving `derived_kind`, `source_report`, `source_report_id_snapshot`, `source_report_version`, `source_unit`, `source_row_kind`, `source_row_id`, `contribution_value`, and `ordinal`).
- **Rationale**: All child models inherit `UUIDModel`, so child row UUIDs are globally unique across tables. A single `old_id -> new_id` map handles every `derived_kind` (`activity`, `labor`, `machinery`, `material`, `concrete`, `general_activity`, `visit`, `incident`/`barrier`/`issue`/`hse_incident`) deterministically without dropping multi-source rows or collapsing N sources into a single `source_sub_report_id` FK.
- **Alternatives considered**:
  - *Reconstructing `DailyReportDerivedSource` from child `source_sub_report_id`*: Rejected because `source_sub_report_id` holds at most one FK and loses all additional contributing sources in multi-source aggregations (e.g., 2 sources collapsing to 1 or 0).

## Decision 3: Defense-in-Depth Derived-Row Ownership Lock Across All Edit Paths (`DEF-B02-02`, `X01`)

- **Decision**: Introduce a shared ownership guard helper (e.g., `assert_report_and_row_editable` / `is_derived_row` in `apps/api/core/field_reports/services/derived_lock.py` or `correction_service.py`) enforced across all mutation surfaces:
  1. **`DailyReportChildViewSet` (`create`, `_batch_upsert`, `perform_update`, `destroy`)**:
     - Reject mutations when `not report.is_current` or `report.is_deleted` (`report_not_current` / `report_locked`).
     - Reject mutations when `report.is_auto_summary` (`derived_collection_read_only`).
     - Defense-in-depth row-level check on `perform_update`, `destroy`, and `_batch_upsert` (existing row): reject if `getattr(row, 'is_derived', False)` is `True`, or `getattr(row, 'source_sub_report_id', None)` / `getattr(row, 'source_report_id', None)` is set, or any `DailyReportDerivedSource` exists for `(daily_report=report, derived_row_id=str(row.id))`.
  2. **`DailyReportViewSet.partial_update` (legacy nested `activities` / derived section payload)**:
     - Reject mutations when `not instance.is_current` or `instance.is_deleted`.
     - Reject derived section payloads when `instance.is_auto_summary` OR when the report has any derived rows/provenance (`derived_readonly`), while keeping authorized project-level summary metadata (`management_opinion`, `weather_override`, `site_status_override`, `weather_condition`, `temp_min`, `temp_max`, `site_status`, `inactivity_reason`, `weather_impact_notes`, `general_notes`, `work_front`, `location_notes`) editable on editable revisions.
  3. **`services.sync_batch` (offline sync boundary — `X01` coordination)**:
     - Preserve `B01`/`A.8` ownership of offline sync architecture; tighten the existing derived-section check in `sync_batch` so payloads containing derived sections are rejected both when `existing.is_auto_summary` AND when `existing` owns derived rows/provenance, and never mutate non-current or approved versions.
- **Rationale**: Relying solely on `report.is_auto_summary` allowed `DEF-B02-02` to bypass row protection whenever the flag was false or stale. Ownership-based defense-in-depth guarantees derived rows cannot be directly mutated via UI, single-row child API, batch upsert, legacy nested PATCH, or offline sync, while leaving authorized project-level metadata editable.
- **Alternatives considered**:
  - *Fixing only `is_auto_summary` in `open_correction`*: Rejected because `DEF-B02-02` explicitly requires ownership-based defensive enforcement across child, batch, offline, and legacy paths independent of a single report flag or UI assumption.

## Decision 4: Explicit Rejection Semantics for Historical, Non-Current, Approved, Archived, and Deleted Rebuild Targets (`DEF-B02-06`, `FR-011`, `SC-006`)

- **Decision**: Make `rebuild_daily_report_summary(project_id, report_date, user=None, report=None, shift=None)` enforce explicit, unambiguous rejection semantics whenever an explicit `report` target is supplied (and expose an authorized explicit rebuild action `POST /api/v1/projects/{project_pk}/daily-reports/{pk}/rebuild/` requiring `edit_reports` + active project membership):
  - **Deleted / Archived-deleted target (`report.is_deleted is True`)**: Raise `ValidationError` with localized bilingual message and stable code `rebuild_target_deleted`.
  - **Historical / Non-current / Superseded / Archived target (`report.is_current is False`)**: Raise `ValidationError` with localized bilingual message and stable code `historical_rebuild_rejected`.
  - **Approved target (`report.status == ReportStatus.APPROVED`)**:
    - When `report` is explicitly targeted (service call with `report=<instance>` or `POST .../rebuild/`): Raise `ValidationError` with localized bilingual message and stable code `report_locked`.
    - When triggered implicitly as a side-effect of unit sub-report submission (`report=None`, e.g., `sub_reports/services/__init__.py:_trigger_rebuild`): Lookup finds only `is_deleted=False, is_current=True`; if that current report is `APPROVED`, return it untouched with zero mutations to rows, provenance, fingerprint, or snapshot (preserving `FR-012` / `W06` drift-detection behavior without breaking unit sub-report submission).
  - **Editable current draft/rejected target (`is_deleted=False, is_current=True, status in {DRAFT, REJECTED}`)**: Execute rebuild cleanly (`FR-009`), refreshing derived operational rows and `DailyReportDerivedSource` while preserving `management_opinion`, `weather_override`, `site_status_override`, and `is_auto_summary`.
  - **Ensure-shell helper (`ensure_daily_report_summary`)**: If an existing current report for `(project_id, report_date, shift)` is already `APPROVED`, return it directly without invoking `rebuild_daily_report_summary(..., report=report)`.
- **Rationale**: Satisfies both `FR-011`/`SC-006` (explicit rejection of any rebuild targeting approved, historical, non-current, archived, or deleted versions with zero mutation) and `FR-009`/`FR-012` (unit-triggered rebuild updates an open current draft revision while leaving an already-approved current snapshot immutable and surfacing source drift).
- **Alternatives considered**:
  - *Silently returning no-op on non-current/deleted targets*: Rejected because `FR-011`, `SC-006`, and Supervisor review explicitly require rejection semantics (not silent no-op) for historical, non-current, archived, and deleted rebuild targets.

## Decision 5: Current-Approved-Only Operational Activity Master Log (`DEF-B02-05`, `E15`)

- **Decision**: Update `activity_log_queryset(project_id, params)` in `apps/api/core/field_reports/services/activity_log.py` so the default official operational filter (`approved_only != 'false'`) filters:
  `report__status=ReportStatus.APPROVED, report__is_current=True, report__is_deleted=False`.
  Also add a reusable helper or explicit parameter policy so `approved_only='false'` (if used for non-official preview) still excludes `report__is_deleted=False` and defaults to `report__is_current=True` unless historical inspection is explicitly requested via the dedicated `/versions/` endpoint.
- **Rationale**: Direct inspection of `activity_log.py:15-17` confirmed `report__is_current=True` was missing, causing superseded approved versions to double-count (2 rows, quantity 10, headcount 8 instead of 1 row, 5, 4). Adding `report__is_current=True` in `activity_log_queryset` automatically fixes both the activity-log API and `FILE1` Excel export and provides the exact shared queryset policy that downstream Package `B04` will build upon for full-queryset aggregates and filters.
- **Alternatives considered**:
  - *Filtering `is_current=True` only in the view or frontend*: Rejected because `FILE1` Excel export and downstream `B04` aggregates call `activity_log_queryset` directly; enforcing the policy at the service queryset layer guarantees single-source consistency.

## Decision 6: Database Schema & Migration Impact

- **Decision**: **Zero new database migrations are required for B02.**
- **Rationale**: All required columns and constraints already exist on `DailyReport`, `DailyReportWorkedShift`, `DailyReportCorrectionRequest`, `DailyReportDerivedSource`, and child models (`is_auto_summary`, `management_opinion`, `weather_override`, `site_status_override`, `reporting_configuration`, `aggregation_fingerprint`, `aggregated_at`, `is_current`, `is_deleted`, `unique_current_daily_report_per_date_shift`, `unique_current_contract_daily_report_per_date`, `unique_derived_source_key`). Avoiding unnecessary schema churn honors Constitution Principle V (Minimal Coherent Changes) and preserves the verified 40/40 blueprint + 25 extension table baseline from B01.
- **Alternatives considered**:
  - *Adding a new `archived_at` column*: Unnecessary because historical/archived versions are already canonically represented by `is_current=False` (superseded) and `is_deleted=True` (soft-deleted/cancelled).
