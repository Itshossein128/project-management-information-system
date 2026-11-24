# Phase A.1 Package B02 End-User QA Verification Evidence Report

- **Date / Timestamp**: 2026-11-19T23:33:00+03:30
- **Scope Evaluated**: Phase A.1 / Package B02 (`specs/058-a1-b02-version-integrity`, Work Package A.1.03)
- **Evaluation Stage**: Stage 5 (Post-Implementation End-User QA Verification)
- **Feature Branch / Artifact Directory**: `specs/058-a1-b02-version-integrity`
- **Live System Endpoints**:
  - Web UI: http://localhost:5173 (React Router 7 + Vite, HTTP 200 `/login` and authenticated `/projects/:id/daily-reports/:id` active)
  - API: http://localhost:8000 (Django 4.2.11 + DRF, `/api/v1/...` active)
  - Database: PostgreSQL 16 (port 5433, 40/40 blueprint tables + 25 extension tables verified)
  - Cache: Redis 7 (port 6379, rate-limiting & session cache verified)

---

## 1. Executive Summary & QA Verdict

- **QA Status**: `qa_passed` (for Package B02 scope)
- **Summary**: Package B02 (Revision Integrity, Derived-Row Lock & Lineage Preservation) is completely implemented and passes end-to-end verification across all personas and required operational scenarios. All 6 historical Stage 1.2 QA defects (`DEF-B02-01` through `DEF-B02-06`) were verified as resolved in the live codebase and runtime API:
  1. `DEF-B02-01`: Draft revision created via `open_correction()` strictly preserves `is_auto_summary=True`, `lineage_id`, B01 contract metadata, and presentation profile.
  2. `DEF-B02-02`: Derived operational rows (activities, labor, machinery, materials, concrete logs, general activities, incidents) are protected against direct `POST`, `PATCH`, `DELETE`, bulk/batch upsert, legacy nested patch, and offline `sync-batch` mutations across both backend service guards and HTTP API endpoints (`derived_collection_read_only`, `derived_readonly`).
  3. `DEF-B02-03`: Provenance records in `DailyReportDerivedSource` are losslessly cloned and remapped across all child row UUIDs (`derived_row_id` pointing to the target revision's row ID), preserving multi-source drill-down (2-of-2 sources preserved).
  4. `DEF-B02-04`: Management opinion, authorized weather overrides, site-status overrides, and reporting configuration are preserved across revision opening, authorized rebuilds, approvals, and cancellations.
  5. `DEF-B02-05`: Official activity master log (`/activity-log/` and `/activity-log/excel/`) filters strictly by `report__is_current=True` and `report__status=approved`, returning exactly 1 row (quantity 5, headcount 4) instead of double-counting across superseded approved revisions. Unapproved draft revisions are excluded and immediate cache invalidation is verified.
  6. `DEF-B02-06`: Explicit rebuild action `POST .../daily-reports/{id}/rebuild/` rejects historical superseded versions (`historical_rebuild_rejected`), locked/approved versions (`report_locked`), and cancelled/deleted reports (`rebuild_target_deleted`) with localized bilingual (FA/EN) error messages, leaving snapshots and provenance completely untouched. Implicit approved snapshots remain immutable when contributing unit sub-reports update.
- **Test Suite Results**:
  - B02 dedicated version-integrity suite: `26 passed, 0 failed, 0 xfailed` in 103s.
  - Daily report lifecycle and regression suites: `103 passed, 0 failed, 0 xfailed` in 97s.
  - B01 data contract regression suite: `11 passed, 0 failed, 0 xfailed` in 151s.
  - Total automated test cases: `140 passed, 0 failed, 0 xfailed`.
  - Frontend typecheck (`pnpm typecheck`): `0 errors, exit code 0`.
- **Governance Note**: This establishes **technical readiness** for Package B02 (`A.1.03`) and unblocks downstream packages B03/B04. **Employer final acceptance** remains gated on independent review in Package `B06`. Zero defects remain within Package B02.

---

## 2. Personas & RBAC Live Verification Matrix

| Persona / Role | Authentication & Authorization | Endpoint / Action Tested | Expected Result | Actual Live HTTP Status & Behavior | Verification Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Anonymous User** | Unauthenticated | `POST .../daily-reports/:id/correction-requests/` | 401 Unauthorized | `401 Unauthorized` | Pass |
| **Anonymous User** | Unauthenticated | `POST .../daily-reports/:id/rebuild/` | 401 Unauthorized | `401 Unauthorized` | Pass |
| **Project Member (Viewer)** | Authenticated (`qa_viewer`), active member with `view_reports` | `GET .../daily-reports/by-date/?date=1406/03/01` | 200 OK (Read-only date inspection) | `200 OK` (returns report without creating parallel report) | Pass |
| **Project Member (Viewer)** | Authenticated (`qa_viewer`), active member with `view_reports` | `POST .../daily-reports/by-date/?date=1406/03/01` | 403 Forbidden | `403 Forbidden` | Pass |
| **Project Member (Viewer)** | Authenticated (`qa_viewer`), active member with `view_reports` | `POST .../daily-reports/:id/correction-requests/` | 403 Forbidden | `403 Forbidden` | Pass |
| **Project Member (Viewer)** | Authenticated (`qa_viewer`), active member with `view_reports` | `POST .../daily-reports/:id/rebuild/` | 403 Forbidden | `403 Forbidden` | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | `POST .../correction-requests/` (reason < 10 chars) | 400 Bad Request (`reason_required`) | `400 Bad Request` ("دلیل اصلاح باید حداقل ۱۰ کاراکتر باشد") | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | `POST .../correction-requests/` (reason ≥ 10 chars) | 201 Created (Draft revision opened) | `201 Created` (`is_auto_summary=True`, `status=draft`) | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | Concurrent duplicate `POST .../correction-requests/` | 400 Bad Request (`correction_already_open`) | `400 Bad Request` ("درخواست اصلاح باز برای این گزارش وجود دارد") | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | Direct `POST` / `PATCH` on derived activity row | 400 Bad Request (`derived_collection_read_only`) | `400 Bad Request` ("Derived rows are read-only.") | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | Legacy nested `PATCH` on report activities | 400 Bad Request (`derived_readonly`) | `400 Bad Request` ("Derived rows are read-only.") | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | Authorized `PATCH` on management opinion & weather override | 200 OK | `200 OK` (metadata updated, derived rows preserved) | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | `POST .../rebuild/` on approved report | 400 Bad Request (`report_locked`) | `400 Bad Request` (EN: "Report is locked." / FA: "گزارش قفل شده است") | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | `POST .../rebuild/` on superseded historical report | 400 Bad Request (`historical_rebuild_rejected`) | `400 Bad Request` (EN: "Historical report versions cannot be rebuilt." / FA: "بازسازی نسخه تاریخی مجاز نیست") | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | `POST .../rebuild/` on deleted report | 400 Bad Request (`rebuild_target_deleted`) | `400 Bad Request` (EN: "Deleted reports cannot be rebuilt." / FA: "گزارش حذف شده قابل بازسازی نیست") | Pass |
| **Project Approver** | Authenticated approver, active member with `approve_reports` | `POST .../daily-reports/:id/approve/` | 200 OK | `200 OK` (marks report approved, sets `is_current=True`) | Pass |
| **Preparer (Self-Approval)** | Authenticated preparer who created the report | `POST .../daily-reports/:id/approve/` | 403 Forbidden / Error (Separation of duties) | `403 Forbidden` (`test_submitter_cannot_approve_own_report` PASS) | Pass |
| **Cross-Project User** | Authenticated in Project B, accesses Project A | `POST .../daily-reports/:id/correction-requests/` | 403 Forbidden | `403 Forbidden` | Pass |

---

## 3. Requirement Verification & Acceptance Analysis

### User Story 1 (P1): Preserve Derived-Summary Identity and Lock Derived Rows
- **Requirements Covered**: `FR-001`, `FR-002`, `FR-003`, `FR-004`, `SC-001`, `SC-002`, `DEF-B02-01`, `DEF-B02-02`.
- **Observed Live Runtime Behavior**:
  - `open_correction()` produces revision with `is_auto_summary=True`, `lineage_id` linked to source, and status `draft`.
  - Direct child mutation via `POST /api/v1/projects/:id/daily-reports/:id/activities/` is rejected with `400 derived_collection_read_only`.
  - Nested legacy PATCH is rejected with `400 derived_readonly`.
  - Batch upsert and offline `sync-batch` enforce `derived_readonly` at the row level while permitting non-derived synchronization.
  - Authorized project management metadata (`management_opinion`, `weather_override`, `site_status_override`) remains editable via `PATCH /api/v1/projects/:id/daily-reports/:id/` (`200 OK`).
- **Status**: **VERIFIED / PASS**

### User Story 2 (P1): Preserve Complete Multi-Source Provenance and Lineage
- **Requirements Covered**: `FR-005`, `FR-006`, `FR-007`, `FR-008`, `SC-003`, `DEF-B02-03`.
- **Observed Live Runtime Behavior**:
  - When opening a correction on an approved report containing multi-source derived rows (e.g. 2 sources: `buildings` contributing 4.0 and `electrical` contributing 6.0), `open_correction()` clones both `DailyReportDerivedSource` records and remaps `derived_row_id` to the target revision's new child row UUID.
  - `GET /api/v1/projects/:id/daily-reports/:id/provenance/activity/:row_id/` returns HTTP 200 with all 2 sources preserved, displaying `source_unit`, `can_view_source=True`, and `contribution_value`.
  - Version history endpoint `GET .../versions/` preserves independent provenance for both superseded and approved versions.
  - When cancelling a correction (`POST .../correction-requests/:id/cancel/`), the original approved version is restored as `is_current=True` with all original provenance records intact.
- **Status**: **VERIFIED / PASS**

### User Story 3 (P1): Preserve Overrides, Metadata, and Protect Snapshots on Rebuild
- **Requirements Covered**: `FR-009`, `FR-010`, `FR-011`, `FR-012`, `SC-005`, `SC-006`, `DEF-B02-04`, `DEF-B02-06`.
- **Observed Live Runtime Behavior**:
  - Draft revisions preserve `management_opinion`, `weather_override`, `site_status_override`, and `reporting_configuration`.
  - Rebuilding an editable revision refreshes derived rows from contributing units without overwriting saved management opinions or overrides.
  - Explicit rebuild action `POST .../rebuild/` validates target eligibility and rejects:
    - Current approved reports: `400 report_locked` ("گزارش قفل شده است" / "Report is locked.")
    - Historical superseded reports: `400 historical_rebuild_rejected` ("بازسازی نسخه تاریخی مجاز نیست" / "Historical report versions cannot be rebuilt.")
    - Cancelled / deleted reports: `400 rebuild_target_deleted` ("گزارش حذف شده قابل بازسازی نیست" / "Deleted reports cannot be rebuilt.")
  - In all rejection cases, 0 rows and 0 snapshots are altered.
  - Modifying a source unit sub-report after daily summary approval leaves the approved summary snapshot completely immutable, and drift comparison accurately reports the delta.
- **Status**: **VERIFIED / PASS**

### User Story 4 (P1): Current-Approved Version Policy in Activity Master Log
- **Requirements Covered**: `FR-013`, `FR-014`, `FR-015`, `SC-004`, `DEF-B02-05`.
- **Observed Live Runtime Behavior**:
  - For a project with two approved revisions for the same date (v1 superseded with quantity 5 and headcount 4, v2 current with quantity 5 and headcount 4), `GET /api/v1/projects/:id/activity-log/` returns exactly 1 row (quantity 5, headcount 4), completely preventing double-counting (10 quantity / 8 headcount).
  - Excel export `GET /api/v1/projects/:id/activity-log/excel/` returns HTTP 200 with the single current approved record.
  - Opening a correction on an approved report immediately excludes unapproved draft data from the official activity log (0 rows returned while draft is open).
  - Cancelling the correction immediately restores the approved record in the activity log cache.
  - Version history endpoint `GET .../versions/` provides dedicated inspection of historical versions without polluting operational aggregates.
- **Status**: **VERIFIED / PASS**

### User Story 5 (P2): Logical Uniqueness, Six-Unit Effective Config, and Workflow RBAC
- **Requirements Covered**: `FR-016`, `FR-017`, `FR-018`, `FR-019`, `FR-020`, `SC-007`.
- **Observed Live Runtime Behavior**:
  - Opening a date via `GET /api/v1/projects/:id/daily-reports/by-date/` idempotently retrieves the existing report without creating parallel duplicate reports.
  - Read-only viewers with `view_reports` can access `by-date` without needing `edit_reports`.
  - Required units are resolved against the date-effective `ProjectReportingConfiguration` across all six valid units (`buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, `security`).
  - Unit reports in `draft`, `rejected`, `soft-deleted`, superseded, other-date, or other-project states contribute 0 operational rows and 0 completeness credit.
  - Workflow role enforcement verifies separation of duties (submitter cannot approve own report), minimum 10-character reason for corrections, and project membership boundaries.
- **Status**: **VERIFIED / PASS**

---

## 4. Defect Log & Resolutions

| Defect ID | Severity | Requirement | Description & Observed Behavior | Fix Verification & Evidence | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DEF-B02-01` | High | FR-001, SC-001 | Revision lost `is_auto_summary` flag, treating corrected report as manual | `open_correction()` retains `is_auto_summary=True`, `lineage_id`, B01 contract metadata | Resolved / Verified |
| `DEF-B02-02` | High | FR-003, SC-002 | Derived operational rows permitted direct mutation via API/batch | `derived_lock.py` enforces ownership guards across single, batch, legacy, and offline mutations | Resolved / Verified |
| `DEF-B02-03` | Critical | FR-005, SC-003 | Opening correction dropped all provenance rows (2-of-2 sources became 0) | `_clone_children()` remaps `DailyReportDerivedSource` across all child row UUIDs | Resolved / Verified |
| `DEF-B02-04` | Medium | FR-009, SC-005 | Management opinion and overrides erased upon revision creation | `open_correction()` and `rebuild` losslessly preserve management opinion and weather/site overrides | Resolved / Verified |
| `DEF-B02-05` | High | FR-013, SC-004 | Activity master log included superseded approved reports, double-counting totals | `activity_log_queryset()` filters `report__is_current=True, report__status=approved` | Resolved / Verified |
| `DEF-B02-06` | Medium | FR-011, SC-006 | Automatic / explicit rebuild did not reject historical or deleted targets | `rebuild_daily_report_summary()` validates status, returning bilingual 400 errors | Resolved / Verified |

---

## 5. Bilingual (FA / EN) Verification

- **Persian (fa)**:
  - Error messages returned with `Accept-Language: fa`:
    - Locked report rebuild: `"گزارش قفل شده است"`
    - Historical report rebuild: `"بازسازی نسخه تاریخی مجاز نیست"`
    - Deleted report rebuild: `"گزارش حذف شده قابل بازسازی نیست"`
    - Duplicate correction: `"درخواست اصلاح باز برای این گزارش وجود دارد"`
    - Short correction reason: `"دلیل اصلاح باید حداقل ۱۰ کاراکتر باشد"`
- **English (en)**:
  - Error messages returned with `Accept-Language: en`:
    - Locked report rebuild: `"Report is locked."`
    - Historical report rebuild: `"Historical report versions cannot be rebuilt."`
    - Deleted report rebuild: `"Deleted reports cannot be rebuilt."`
    - Duplicate correction: `"A correction request is already open for this report."`
    - Short correction reason: `"Correction reason must be at least 10 characters."`
- **UI Walkthrough**:
  - Authenticated Chromium sessions verified RTL reading direction for Persian and LTR for English, metadata editor fields, and provenance disclosures.
