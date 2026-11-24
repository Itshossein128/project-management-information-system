# Phase A.1 Package B03 End-User QA Verification Evidence Report

- **Date / Timestamp**: 2026-11-21T19:04:00+03:30
- **Scope Evaluated**: Phase A.1 / Package B03 (`specs/059-a1-b03-reference-parity`, Work Package A.1.04)
- **Evaluation Stage**: Stage 5 (Post-Implementation End-User QA Verification)
- **Feature Directory**: `specs/059-a1-b03-reference-parity`
- **Live System Endpoints**:
  - Web UI: http://localhost:5173 (React Router 7 + Vite, authenticated daily view, range modal, and unit panel active)
  - API: http://localhost:8000 (Django 4.2.11 + DRF, `/api/v1/projects/:id/daily-reports/...` active)
  - Database: PostgreSQL 16 (port 5433, migration series through field reports 0028, sub-reports 0016, projects 0022 verified)
  - Cache: Redis 7 (port 6379, PONG verified)

---

## 1. Executive Summary & QA Verdict

- **QA Status**: `qa_passed` (for Package B03 technical readiness scope)
- **Summary**: Package B03 (Reference Form Parity for Excel and PDF Exports across Deliverables DEL-01 through DEL-04) is completely implemented and passes end-to-end verification across all required end-user personas, deliverable families, and operational edge-case scenarios. All 8 historical Stage 1.2 QA defects (`DEF-B03-01` through `DEF-B03-08`) have been conclusively resolved, tested, and validated:
  1. `DEF-B03-01`: Worked shift hours (start, end, effective duration) are populated from database models rather than static hardcoded text. Overnight shifts and independent durations are supported.
  2. `DEF-B03-02`: Shiraz form profile renders direct and indirect manpower tables side-by-side (starting on the same row) matching the physical employer reference form, preserving 34 and 32 standard positions while accommodating custom catalog entries in the appendix.
  3. `DEF-B03-03`: Excel exports across daily reports and discipline sub-reports strictly configure A4 landscape print settings (`fitToWidth=1`, `paperSize=9`), dynamic row wrapping, print titles, and repeated headers.
  4. `DEF-B03-04`: PDF signatures render authentic actor names, verified organizational roles, local timestamps (Tehran timezone), direct approval clauses, and full-page diagonal watermarks (`پیش‌نویس — غیرقابل استناد رسمی` / `Draft — Not Legally Binding`) across all pages of non-approved reports.
  5. `DEF-B03-05`: Legacy and unmeasured equipment hours strictly distinguish between measured zero (`0`) and unknown/unrecorded hours (empty cell in Excel, dash in PDF), resolving the historical strict XFAIL.
  6. `DEF-B03-06`: Concrete pour operational logs preserve delivery notes, truck mixer identifiers, batching plant info, canonical sample codes, and independent lab sheet tracking with clear drill-down links.
  7. `DEF-B03-07`: Bilingual FA/EN HSE incident severity and incident types are fully localized (`شدید` for Major, `ایمنی` for Safety).
  8. `DEF-B03-08`: Profile catalog abstraction supports customizable manpower positions without fixed placeholder pollution or loss of historical contractor lines.
- **Test Suite & Verification Results**:
  - Pytest focused regression suites (Excel parity, PDF generation, watermark/signatures, workbook range, unit report Excel/PDF, concrete QC links, summary parity): `78 passed, 0 failed, 4 warnings` across 2 active test batches.
  - Full B01/B02/B03 suite: 184 focused tests passing in isolated PostgreSQL dev environment.
  - Frontend typecheck (`pnpm typecheck`): `0 errors, exit code 0`.
  - Artifact & Openpyxl inspection: 31-sheet range workbook validated with chronological dates, landscape A4 setup (`paperSize=9`, `fitToWidth=1`), live formula `=SUM(G49,P47,G54)` evaluated to 24 person-shifts.
  - Poppler PDF inspection: Watermark validated on 9/9 pages of long daily draft PDF, 8/8 pages of long unit draft PDF, and 0/4 pages on approved reference report.
- **Governance Note**: This verification establishes **technical readiness** for Package B03. Independent reconciliation remains reserved for Package `B05` and employer final acceptance remains gated on Package `B06`. Zero defects remain open within Package B03 scope.

---

## 2. Personas & RBAC End-User Verification Matrix

| Persona / Role | Authentication & Authorization | Endpoint / Action Tested | Expected Result | Actual Live HTTP Status & Behavior | Verification Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Anonymous User** | Unauthenticated | `GET .../daily-reports/:id/shiraz-excel/` | 401 Unauthorized | `401 Unauthorized` | Pass |
| **Anonymous User** | Unauthenticated | `GET .../daily-reports/:id/pdf/` | 401 Unauthorized | `401 Unauthorized` | Pass |
| **Non-Member User** | Authenticated, no project membership | `GET .../daily-reports/:id/shiraz-excel/` | 403 Forbidden | `403 Forbidden` | Pass |
| **Project Viewer** | Active project member with `view_reports` | `GET .../daily-reports/:id/shiraz-excel/` | 200 OK (Downloads FILE 4) | `200 OK` (binary XLSX, Content-Disposition valid) | Pass |
| **Project Viewer** | Active project member with `view_reports` | `GET .../daily-reports/:id/pdf/` | 200 OK (Downloads daily PDF) | `200 OK` (binary PDF, 4 pages, Content-Disposition valid) | Pass |
| **Project Viewer** | Active project member with `view_reports` | `GET .../daily-reports/workbook/?from_date=...&to_date=...` (31 days) | 200 OK (Multi-sheet workbook) | `200 OK` (31 sheets, chronological, current-approved) | Pass |
| **Project Viewer** | Active project member with `view_reports` | `GET .../daily-reports/workbook/?from_date=...&to_date=...` (32 days) | 400 Bad Request (`range_limit_exceeded`) | `400 Bad Request` (Bilingual error message returned) | Pass |
| **Discipline Lead** | Project member with unit report permissions | `GET .../sub-reports/buildings/:id/shiraz-excel/` | 200 OK (Downloads FILE 5) | `200 OK` (Numeric progress 0..100, empty for null) | Pass |
| **Discipline Lead** | Project member with unit report permissions | `GET .../sub-reports/electrical/:id/shiraz-excel/` | 200 OK (Downloads FILE 6) | `200 OK` (Electrical-only columns, no civil columns) | Pass |
| **Site Engineer** | Active project member with `edit_reports` | UI Date-range export modal (Persian UI) | Localized validation & download | `200 OK` (Jalali dates validated, Enter triggers download) | Pass |
| **Auditor / Observer** | Scoped organizational observer | `GET .../daily-reports/:id/pdf/` | 200 OK if org unit matches; 403 if mismatch | `200 OK` (Scoped unit match) / `403 Forbidden` (Mismatch) | Pass |

---

## 3. Detailed Deliverables & Requirement Parity Analysis

### Deliverable DEL-01: FILE 4 Shiraz Parity Daily Excel Export
- **Covered Requirements**: `FR-001` through `FR-008`, `SC-001`, `SC-002`, `DEF-B03-01`, `DEF-B03-02`, `DEF-B03-03`, `DEF-B03-05`.
- **Observed Behavior**:
  - Worked shifts: Populated dynamically with actual start/end timestamps and hours (e.g. Shift 1: 07:00–15:30 = 8.5h, Shift 3: 23:00–05:00 = 6.0h).
  - Side-by-side manpower tables: Direct (left) and indirect (right) tables start on the same row, matching the Shiraz reference form. Custom job titles exceed standard slots cleanly in the appendix.
  - Page setup: A4 landscape (`paperSize=9`), `fitToWidth=1`, repeating title rows enabled.
  - Formula safety: Cells starting with `=, +, -, @` literalized with leading apostrophes, preventing injection. Legitimate total formulas (`=SUM(...)`) preserved.
  - Status: **VERIFIED / PASS**

### Deliverable DEL-02: Bilingual Daily Summary PDF
- **Covered Requirements**: `FR-009` through `FR-014`, `SC-004`, `SC-005`, `DEF-B03-04`.
- **Observed Behavior**:
  - Signature attribution: Final page renders valid signers, true organizational positions, local action timestamps, and direct-approval annotations.
  - Watermark coverage: Diagonal draft watermark rendered across all 9 pages of long draft reports; cleanly omitted on approved reports (4 pages).
  - Bilingual text formatting: Persian RTL reshaped properly; mixed FA/EN strings wrap cleanly without clipping.
  - Status: **VERIFIED / PASS**

### Deliverable DEL-03: Discipline Sub-Reports (FILE 5, FILE 6, and Unit PDFs)
- **Covered Requirements**: `FR-015` through `FR-021`, `SC-003`, `SC-006`, `DEF-B03-06`, `DEF-B03-07`.
- **Observed Behavior**:
  - FILE 5 (Civil / Buildings): Progress values output as formatted decimals (0, 0.455, 1) and empty strings for unrecorded progress.
  - FILE 6 (Electrical): Exclusively renders electrical columns without civil/structural artifacts.
  - Unit PDFs: Standalone PDF generation supported for all 6 unit disciplines (Buildings, Electrical, Mechanical, Machinery, Warehouse, Security).
  - Concrete QC details: Delivery notes, truck mixer codes, slump, and canonical sampling IDs preserved with separate inspection links.
  - Localized HSE severity: Terms such as `شدید` and `ایمنی` rendered consistently in Persian exports.
  - Status: **VERIFIED / PASS**

### Deliverable DEL-04: Date-Range Multi-Sheet Workbook
- **Covered Requirements**: `FR-022` through `FR-027`, `SC-007`, `SC-008`.
- **Observed Behavior**:
  - Generates 1 sheet per date containing a current-approved daily report.
  - Enforces the 31-day inclusive limit by default (400 rejection on 32 days).
  - Preserves exact-version integrity and chronological sheet ordering.
  - Status: **VERIFIED / PASS**
