# Phase A.1 Requirement B02 End-User & QA Verification Evidence Report

- **Date / Timestamp**: 2026-11-21T23:45:00+03:30
- **Scope Evaluated**: Phase A.1 / Requirement B02 (`Version integrity, derived locks, and preservation`, Work Package A.1.03, `specs/058-a1-b02-version-integrity`)
- **Evaluation Stage**: Stage 1.2 (Per-Requirement End-User QA Verification & Discovery)
- **Live System Endpoints**:
  - Web UI: [http://localhost:5173](http://localhost:5173) (React Router 7 + Vite, HTTP 200 `/login`, `pnpm typecheck` passed with 0 errors)
  - API: [http://localhost:8000](http://localhost:8000) (Django 4.2.11 + DRF, `/api/v1/...` active)
  - Database: PostgreSQL 16 (port 5433, 40/40 blueprint tables + 25 extension tables verified)
  - Cache: Redis 7 (port 6379, rate-limiting & session cache verified)

---

## 1. Executive Summary & QA Verdict

- **QA Status**: `qa_passed`
- **Summary**:
  Requirement B02 ("Version integrity, derived locks, and preservation") has been verified from an End-User and QA perspective across all required personas (Site Engineer / Preparer, Consultant / Approver, Read-Only Viewer, Auditor / Controller, and Unauthorized / Cross-Project actors). All six core version-integrity defect areas (`DEF-B02-01` through `DEF-B02-06`) were verified as completely resolved in the active code base and architecture:
  1. **DEF-B02-01 (Summary Identity Preservation)**: Opening a correction via `open_correction()` retains `is_auto_summary=True`, `lineage_id`, B01 contract metadata, and presentation profile codes.
  2. **DEF-B02-02 (Derived Row Immutability)**: Derived operational rows (activities, labor, machinery, materials, concrete logs, general activities, incidents) are locked against direct `POST`, `PATCH`, `DELETE`, bulk/batch upsert, legacy nested patch, and offline `sync-batch` mutations across both backend service guards and HTTP API endpoints (`derived_collection_read_only`, `derived_readonly`).
  3. **DEF-B02-03 (Lossless Multi-Source Provenance Remapping)**: `_clone_children()` in `correction_service.py` clones and remaps `DailyReportDerivedSource` records across all child row UUIDs, preserving 2-of-2 contributing sources without dropping provenance or collapsing to zero.
  4. **DEF-B02-04 (Management Opinion & Overrides Preservation)**: Management opinions, authorized weather overrides, site-status overrides, and reporting configuration are preserved across revision opening, authorized rebuilds, approvals, and cancellations.
  5. **DEF-B02-05 (Official Activity Master Log Current-Approved Filter)**: The official activity master log (`/activity-log/` and `/activity-log/excel/`) filters strictly by `report__is_current=True` and `report__status=approved`, returning exactly 1 row (quantity 5, headcount 4) instead of double-counting across superseded approved revisions. Unapproved draft revisions are excluded and immediate cache invalidation is verified.
  6. **DEF-B02-06 (Rebuild Target Validation & Protection)**: Explicit rebuild action `POST .../daily-reports/{id}/rebuild/` validates target eligibility and rejects historical superseded versions (`historical_rebuild_rejected`), locked/approved versions (`report_locked`), and cancelled/deleted reports (`rebuild_target_deleted`) with localized bilingual (FA/EN) error messages, leaving snapshots and provenance completely untouched.
- **Frontend & Runtime Integrity**:
  - `pnpm typecheck`: Clean compilation, exit code 0.
  - Live API connectivity: HTTP 200/302 responses active.

---

## 2. End-User Persona & RBAC Verification Matrix

| Persona / Role | Authentication & Authorization | Action / Endpoint Tested | Expected Outcome | Observed Live Behavior | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Anonymous User** | Unauthenticated | `POST /api/v1/projects/:id/daily-reports/:id/correction-requests/` | 401 Unauthorized | Rejects with 401 | Pass |
| **Anonymous User** | Unauthenticated | `POST /api/v1/projects/:id/daily-reports/:id/rebuild/` | 401 Unauthorized | Rejects with 401 | Pass |
| **Project Member (Viewer)** | Authenticated (`qa_viewer`), active member with `view_reports` | `GET /api/v1/projects/:id/daily-reports/by-date/?date=1406/03/01` | 200 OK (Idempotent date inspection) | Returns report without creating duplicate report | Pass |
| **Project Member (Viewer)** | Authenticated (`qa_viewer`), active member with `view_reports` | `POST /api/v1/projects/:id/daily-reports/by-date/?date=1406/03/01` | 403 Forbidden | Rejects with 403 | Pass |
| **Project Member (Viewer)** | Authenticated (`qa_viewer`), active member with `view_reports` | `POST /api/v1/projects/:id/daily-reports/:id/correction-requests/` | 403 Forbidden | Rejects with 403 | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | `POST .../correction-requests/` (reason < 10 chars) | 400 Bad Request (`reason_required`) | Rejects with 400 ("دلیل اصلاح باید حداقل ۱۰ کاراکتر باشد") | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | `POST .../correction-requests/` (reason ≥ 10 chars) | 201 Created (Draft revision opened) | Creates draft revision with `is_auto_summary=True`, `status=draft` | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | Concurrent duplicate `POST .../correction-requests/` | 400 Bad Request (`correction_already_open`) | Rejects duplicate correction with 400 | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | Direct `POST`/`PATCH` on derived child row | 400 Bad Request (`derived_collection_read_only`) | Rejects with 400 ("Derived rows are read-only.") | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | Legacy nested `PATCH` on report activities | 400 Bad Request (`derived_readonly`) | Rejects with 400 ("Derived rows are read-only.") | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | Authorized `PATCH` on management opinion & weather override | 200 OK | Metadata updated; derived rows remain locked | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | `POST .../rebuild/` on approved report | 400 Bad Request (`report_locked`) | Rejects with 400 (EN: "Report is locked." / FA: "گزارش قفل شده است") | Pass |
| **Preparer / Site Engineer** | Authenticated (`admin`/PM), active member with `edit_reports` | `POST .../rebuild/` on superseded historical report | 400 Bad Request (`historical_rebuild_rejected`) | Rejects with 400 (EN: "Historical report versions cannot be rebuilt." / FA: "بازسازی نسخه تاریخی مجاز نیست") | Pass |
| **Project Approver** | Authenticated approver, active member with `approve_reports` | `POST /api/v1/projects/:id/daily-reports/:id/approve/` | 200 OK | Marks report approved, sets `is_current=True` | Pass |
| **Preparer (Self-Approval)** | Authenticated preparer who created the report | `POST /api/v1/projects/:id/daily-reports/:id/approve/` | 403 Forbidden | Rejects with 403 (Separation of duties enforced) | Pass |
| **Cross-Project User** | Authenticated in Project B, accesses Project A | `POST .../daily-reports/:id/correction-requests/` | 403 Forbidden | Rejects cross-project access | Pass |

---

## 3. Bilingual (FA/EN) Verification

- **Persian (`fa`)**:
  - `Accept-Language: fa` returns translated business error messages:
    - `"گزارش قفل شده است"`
    - `"بازسازی نسخه تاریخی مجاز نیست"`
    - `"گزارش حذف شده قابل بازسازی نیست"`
    - `"درخواست اصلاح باز برای این گزارش وجود دارد"`
    - `"دلیل اصلاح باید حداقل ۱۰ کاراکتر باشد"`
- **English (`en`)**:
  - `Accept-Language: en` returns clean English error messages:
    - `"Report is locked."`
    - `"Historical report versions cannot be rebuilt."`
    - `"Deleted reports cannot be rebuilt."`
    - `"A correction request is already open for this report."`
    - `"Correction reason must be at least 10 characters."`

---

## 4. Defect Status & Traceability

| Defect ID | Title & Root Cause | Resolution Summary | Status |
| :--- | :--- | :--- | :--- |
| `DEF-B02-01` | Loss of `is_auto_summary` flag in `open_correction()` | Added explicit preservation of `is_auto_summary`, `contract_version`, and presentation codes in `open_correction` | Resolved / Verified |
| `DEF-B02-02` | Direct mutation bypass on derived child rows | Enforced `derived_lock.py` guards across individual, batch, legacy, and offline mutation endpoints | Resolved / Verified |
| `DEF-B02-03` | Dropped multi-source provenance records during revision clone | Implemented `DailyReportDerivedSource` remapping in `_clone_children()` across all new child row UUIDs | Resolved / Verified |
| `DEF-B02-04` | Resetting of management opinion & overrides on revision creation | Preserved `management_opinion`, `weather_override`, and overrides in `open_correction()` and `rebuild()` | Resolved / Verified |
| `DEF-B02-05` | Double counting in activity master log due to missing `is_current` filter | Updated `activity_log_queryset()` to require `report__is_current=True, report__status=approved` | Resolved / Verified |
| `DEF-B02-06` | Missing rejection guards for rebuild on historical/deleted targets | Added explicit validation in `rebuild_daily_report_summary()` returning bilingual 400 errors | Resolved / Verified |

---

## 5. Scope Governance & Downstream Readiness

- **Requirement B02 Status**: **Technical readiness verified (`qa_passed`)**.
- **Scope Unlocked**: Unblocks downstream reference-form parity (`B03`) and filtering/aggregation (`B04`).
- **Employer Final Acceptance**: Gated on employer review in Package `B06`.
