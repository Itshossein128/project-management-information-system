# Interface & Service Contracts: Phase A.1 / B02 Version Integrity, Derived-Row Lock & Lineage Preservation

**Feature**: `058-a1-b02-version-integrity`  
**Date**: 2026-11-19  
**Base API Prefix**: `/api/v1/projects/{project_pk}/`

---

## 1. Correction Lifecycle Endpoints

### 1.1 Open Correction
- **Endpoint**: `POST /api/v1/projects/{project_pk}/daily-reports/{pk}/correction-requests/`
- **Permissions**: Authenticated + active project member + `edit_reports` (read-only system-admin observers without active membership & `edit_reports` are denied with `403`).
- **Request Body**: `{ "reason": "<string, trimmed length >= 10>" }`
- **Success (`201 Created`)**: Returns `DailyReportCorrectionRequestSerializer` linking `source_report` (`v_n`, now `is_current=False`) and `result_report` (`v_{n+1}`, `status="draft"`, `is_current=True`) via `source_report_id` and `result_report_id`. The activity-log cache is invalidated after commit.
  - `result_report` MUST have:
    - `is_auto_summary == source_report.is_auto_summary`
    - `management_opinion == source_report.management_opinion`
    - `weather_override == source_report.weather_override`
    - `site_status_override == source_report.site_status_override`
    - `reporting_configuration_id == source_report.reporting_configuration_id`
    - `aggregation_fingerprint == source_report.aggregation_fingerprint`
    - `aggregated_at == source_report.aggregated_at`
    - `contract_version`, `presentation_profile_code`, `is_synthetic_reference`, and `worked_shifts` preserved
    - Complete `DailyReportDerivedSource` set remapped to `result_report` child row IDs.
- **Error Responses (`400 Bad Request`)**:
  - `reason_required` (reason missing or `< 10` chars after trim)
  - `correction_already_open` (concurrent or duplicate open correction on same `lineage_id`)
  - `report_not_locked` (`source_report` is not `approved` or not `is_current`)

### 1.2 Cancel Correction
- **Endpoint**: `POST /api/v1/projects/{project_pk}/correction-requests/{correction_pk}/cancel/`
- **Permissions**: Authenticated + active project member + `edit_reports`.
- **Success (`200 OK`)**: Soft-deletes `result_report` (`is_current=False, is_deleted=True`), restores `source_report.is_current=True` with untouched derived identity/provenance/opinion/overrides/snapshot, marks correction `cancelled`, and invalidates activity-log cache.
- **Error Responses (`400 Bad Request`)**: `correction_not_open`, `result_not_cancellable`, `source_not_restorable`.

---

## 2. Derived-Row Ownership Lock Contract (`DEF-B02-02`, `X01`)

### 2.1 Child Row Endpoints (Single-Row & Batch)
- **Endpoints**:
  - `POST/PATCH/PUT/DELETE /api/v1/projects/{project_pk}/daily-reports/{report_pk}/{activities|labor|equipment|materials|concrete-logs|labor-camp|incidents}/...`
  - Including `DailyReportLaborViewSet` batch list `POST` (`_batch_upsert`).
- **Rejection Rules (`400 Bad Request`)**:
  - `report.is_deleted` or `not report.is_current` → `code: "report_not_current"` (localized FA/EN).
  - `report.is_auto_summary` → `code: "derived_collection_read_only"`.
  - Row-level ownership check (defense-in-depth on `update`/`partial_update`/`destroy`/`_batch_upsert`): if target row has `is_derived=True`, `source_sub_report_id` / `source_report_id` set, or an associated `DailyReportDerivedSource` record → `code: "derived_collection_read_only"`.
  - `report.status == "approved"` → `code: "report_locked"`.

### 2.2 Header Partial Update & Legacy Nested Payload
- **Endpoint**: `PATCH /api/v1/projects/{project_pk}/daily-reports/{pk}/`
- **Permissions**: Active project member + `edit_reports`.
- **Rejection Rules (`400 Bad Request`)**:
  - `not instance.is_current` or `instance.is_deleted` → `code: "report_not_current"`.
  - Payload contains any derived section (`activities`, `labor`, `materials`, `concrete_logs`, `machinery_rows`, `general_activities`, `visits`, etc.) on an `is_auto_summary` report OR any report owning derived rows/provenance → `code: "derived_readonly"`.
  - `instance.status == "approved"` → `code: "report_locked"`.
- **Permitted Metadata Edits (`200 OK`)**: On an editable current report (`draft`/`rejected`, or authorized summary metadata fields on non-approved auto-summary), updating `management_opinion`, `weather_override`, `site_status_override`, `weather_condition`, `temp_min`, `temp_max`, `site_status`, `inactivity_reason`, `weather_impact_notes`, `general_notes`, `work_front`, `location_notes` succeeds without touching derived rows.

### 2.3 Offline Sync Batch Boundary (`X01` Coordination)
- **Endpoint**: `POST /api/v1/projects/{project_pk}/daily-reports/sync-batch/`
- **Contract**: Retains `B01`/`A.8` ownership of offline sync; rejects derived-section payloads with item `status: "error"` and `code: "derived_readonly"` whenever the target is new, `is_auto_summary=True`, or owns derived rows/provenance, and returns `status: "conflict"` for non-current or approved targets without mutating them.

---

## 3. Provenance Drill-Down Contract (`DEF-B02-03`)

- **Endpoint**: `GET /api/v1/projects/{project_pk}/daily-reports/{pk}/provenance/{derived_kind}/{derived_row}/`
- **Permissions**: Authenticated + project view access (`view_reports` or authorized admin observation for read-only metadata; source links masked with `can_view_source: false` when caller lacks `view_reports`).
- **Response (`200 OK`)**:
  ```json
  {
    "derived_kind": "activity",
    "derived_row": "<uuid of row in requested report version>",
    "rows": [
      {
        "source_report": "<uuid>",
        "source_report_version": 1,
        "source_unit": "buildings",
        "source_row_kind": "activity",
        "source_row_id": "<id>",
        "contribution_value": "5.0000",
        "can_view_source": true,
        "href": "/api/v1/projects/<project_id>/units/buildings/daily-reports/<source_report>/"
      }
    ]
  }
  ```
- **Invariant**: Every derived row cloned from `v1` to `v2` returns the exact same count `N` of contributing sources (`N >= 2` for multi-source rows) when queried on `v2` using `v2`'s child row UUID.

---

## 4. Explicit Summary Rebuild Contract (`DEF-B02-06`, `FR-011`, `SC-006`)

- **Endpoint**: `POST /api/v1/projects/{project_pk}/daily-reports/{pk}/rebuild/`
- **Permissions**: Authenticated + active project member + `edit_reports`.
- **Service Entry Point**: `rebuild_daily_report_summary(project_id, report_date, user=user, report=target_report)`
- **Explicit Target Rejection Responses (`400 Bad Request` / `ValidationError`)**:
  - Deleted/cancelled target (`is_deleted=True`): `code: "rebuild_target_deleted"` (bilingual FA/EN)
  - Historical / non-current / superseded / archived target (`is_current=False`): `code: "historical_rebuild_rejected"` (bilingual FA/EN)
  - Approved target (`status="approved"`): `code: "report_locked"` (bilingual FA/EN)
  - Submitted / under-review target (`status in {"submitted", "under_review"}`): `code: "report_not_editable"` (bilingual FA/EN)
- **Success (`200 OK`)**: On a current editable (`draft`/`rejected`, `is_current=True`, `is_deleted=False`) report, refreshes derived rows and `DailyReportDerivedSource` from eligible current unit sub-reports while preserving `is_auto_summary`, `management_opinion`, `weather_override`, and `site_status_override`.

---

## 5. Official Activity Master Log Contract (`DEF-B02-05`, `E15`, B04 Handoff)

- **Endpoint**: `GET /api/v1/projects/{project_pk}/activity-log/` and `GET /api/v1/projects/{project_pk}/activity-log/excel/`
- **Service Entry Point**: `activity_log_queryset(project_id, params)`
- **Invariant**: Default official query (`approved_only != "false"`) filters `report__status=ReportStatus.APPROVED`, `report__is_current=True`, `report__is_deleted=False`, `is_deleted=False`.
- **Preview**: `approved_only=false` includes current non-approved reports and still excludes historical and deleted reports.
- **Downstream B04 Guarantee**: Package B04's filter extensions, full-queryset aggregates, and `FILE1` export consume this exact `activity_log_queryset` current-approved policy without double-counting superseded versions.
- **History Separation**: Superseded versions remain accessible exclusively via `GET /api/v1/projects/{project_pk}/daily-reports/{pk}/versions/` and individual version retrieval (`GET .../daily-reports/{old_pk}/`).

---

## 6. Bilingual Error Codes (`lifecycle_errors.py`, Constitution Principle III)

All new/updated B02 error codes MUST provide both Persian (`fa`) and English (`en`) messages via `lifecycle_error_detail(code, request=request)`:
- `report_not_current`
- `historical_rebuild_rejected`
- `rebuild_target_deleted`
- `report_not_editable`
- `report_locked`
- `derived_collection_read_only` / `derived_readonly`
- `sod_self_approval_forbidden` (if separation-of-duties rejection is triggered)
