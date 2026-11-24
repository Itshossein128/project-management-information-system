# Phase A.1 Requirement B03 End-User & QA Verification Evidence Report

- **Document Identifier**: `a1-requirements-2026-11-22-stage1-b03-qa-findings.md`
- **Requirement ID**: `B03`
- **Title**: Reference-form parity (Excel and PDF values, fields, labels, roles, unknown semantics, long text, pagination, printing, timezone, and watermark match the agreed reference form)
- **Phase**: A.1 (Daily Reports and Export Parity)
- **Evaluation Stage**: Stage 1.2 (Per-Requirement Fan-Out Verification)
- **Evaluation Date / Timestamp**: 2026-11-22T20:13:30+03:30
- **Target Systems Tested**:
  - Web UI: http://localhost:5173 (React Router 7 + Vite — HTTP 302 redirect to /login verified live, typecheck passed 0 errors)
  - API: http://localhost:8000 (Django 4.2.11 + DRF — HTTP 200 /api/docs/ active)
  - Database: PostgreSQL 16 (Port 5433, `ipcas` blueprint schema)
  - Cache: Redis (Port 6379, active)
- **Associated Spec & Implementation**: `specs/059-a1-b03-reference-parity`, `specs/044-shiraz-excel-parity-pdf`, `apps/api/core/field_reports/shiraz_file4_excel.py`, `apps/api/core/field_reports/pdf.py`, `apps/api/core/sub_reports/shiraz_subreport_excel.py`, `apps/api/core/sub_reports/pdf.py`

---

## 1. Executive Summary & QA Verdict

- **Requirement Evaluation Status**: **VERIFIED / TECHNICAL READINESS PASSED (`qa_passed`)**
- **QA Summary**:
  Requirement B03 specifies reference-form parity across Excel and PDF outputs:
  - **DEL-01**: FILE 4 Shiraz parity daily Excel export (`/api/v1/projects/:id/daily-reports/:id/shiraz-excel/`).
  - **DEL-02**: Bilingual daily summary PDF export (`/api/v1/projects/:id/daily-reports/:id/pdf/`).
  - **DEL-03**: Discipline sub-reports FILE 5 (Civil), FILE 6 (Electrical), and discipline unit PDFs (`/sub-reports/unit-reports/:id/pdf/`).
  - **DEL-04**: Date-range multi-sheet workbook export (`/daily-reports/workbook/`).

  All 8 historical Stage 1.2 QA defect areas (`DEF-B03-01` through `DEF-B03-08`) remain fully resolved and covered by regression test suites and physical fixture artifacts:
  1. **DEF-B03-01 (Dynamic Shift Hours)**: Worked shift start/end times and actual durations are dynamically populated from `DailyReportWorkedShift` (e.g. 8.50h, 7.25h, 6.00h), completely replacing static text.
  2. **DEF-B03-02 (Side-by-Side Manpower Layout)**: Shiraz 34/32 reference profile renders direct (34) and indirect (32) labor tables side-by-side on row 6, precisely matching the Shiraz reference form geometry.
  3. **DEF-B03-03 (Excel Print Properties & RTL)**: All generated workbooks enforce A4 landscape (`paperSize=9`), `fitToWidth=1`, RTL worksheet layout, dynamic row auto-wrapping for long notes, and repeating header rows (`print_title_rows`). User input strings are strictly literalized to prevent formula injection.
  4. **DEF-B03-04 (PDF Signatures & Watermarks)**: Signature blocks render frozen legal roles, organizational positions, and Tehran local timestamps (`Asia/Tehran`). Diagonal draft watermarks (`پیش‌نویس — غیرقابل استناد رسمی`) cover all pages of draft, submitted, under-review, and rejected reports, and are cleanly omitted on approved reports.
  5. **DEF-B03-05 (Equipment Unmeasured vs Zero Semantics)**: Unrecorded equipment hours remain blank in Excel and display as dashes in PDF, preventing silent coercion to 0.0. Explicitly measured 0.0 hours are faithfully preserved.
  6. **DEF-B03-06 (Concrete & QC Inspection Drill-Down)**: Concrete pour rows capture batching plant, transit mixer IDs, slump tests, and canonical lab sample IDs with direct drill-down links.
  7. **DEF-B03-07 (Bilingual Persian Localization)**: HSE incident severity and categories render authentic Persian terminology (`شدید`, `ایمنی`, `مرخصی / غیبت`).
  8. **DEF-B03-08 (Profile Catalog Flexibility)**: Project occupations beyond the standard 34/32 profile appear in the appendix table without polluting fixed slots; unprofiled projects render standard catalog without forcing 34/32 constraints.

- **System Health & Build Verification**:
  - `pnpm typecheck`: Clean compilation with 0 errors across frontend.
  - Live API connectivity: `http://localhost:8000/api/docs/` HTTP 200 OK.
  - Web frontend: `http://localhost:5173/` HTTP 302 `/login` active.
  - Test evidence: 40+ unit/integration test cases in `test_shiraz_file4_excel.py`, `test_pdf_signatures_watermark.py`, `test_b03_workbook_range.py`, and `test_b03_unit_report_pdf.py` validate all parity requirements.

---

## 2. End-User Persona Evaluation Matrix

| Persona | Role / Perspective | Feature / Action Evaluated | Observed Behavior | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Site Engineer / Technical Office** | Field reporting & progress capture | Downloads FILE 4 Excel export (`/api/v1/projects/:id/daily-reports/:id/shiraz-excel/`) | Dynamic shift hours displayed; side-by-side direct/indirect manpower tables; `=SUM(...)` formulas intact; formula injection prevention active. | **Pass** |
| **Consultant / Resident Inspector** | Quality oversight & regulatory sign-off | Reviews Daily PDF export (`/api/v1/projects/:id/daily-reports/:id/pdf/`) | Legal roles and timestamps visible on signature page; draft watermark present across all non-approved pages; RTL Persian text wrapping clean. | **Pass** |
| **Discipline Lead** | Civil / Electrical / Mechanical sub-reports | Downloads discipline exports (FILE 5, FILE 6, and Unit PDFs) | Civil progress formatted as decimals/percentages; electrical sheet isolates electrical columns; unit PDFs watermarked on drafts. | **Pass** |
| **Project Manager / Client Auditor** | Historical audit & contract verification | Generates 30-day range workbook (`/daily-reports/workbook/`) | Multi-sheet chronological workbook generated; A4 landscape fit settings active; 31-day threshold strictly enforced (400 returned on >31 days). | **Pass** |

---

## 3. Defects Resolution Audit Register

| Defect ID | Description | Component | Verification Evidence | Status |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-B03-01** | Static shift hours string in row 4 | `shiraz_file4_excel.py` | Populates dynamic shift times from DB; tests pass | **Resolved** |
| **DEF-B03-02** | Stacked direct/indirect manpower layout | `shiraz_file4_excel.py` | Side-by-side columns (direct & indirect) implemented | **Resolved** |
| **DEF-B03-03** | Missing Excel A4 print & fit settings | `shiraz_file4_excel.py` | `fitToWidth=1`, `paperSize=9`, repeating titles configured | **Resolved** |
| **DEF-B03-04** | Missing legal roles in PDF signatures | `pdf.py` | Signer roles and local Tehran timestamps rendered | **Resolved** |
| **DEF-B03-05** | Artificial zero for unrecorded equipment | `shiraz_file4_excel.py` | `None` operating hours left blank instead of `0` | **Resolved** |
| **DEF-B03-06** | Missing concrete delivery & QC fields | `shiraz_file4_excel.py`, `pdf.py` | Delivery truck, plant, slump, lab links preserved | **Resolved** |
| **DEF-B03-07** | Untranslated English HSE severity labels | `shiraz_file4_excel.py` | Persian translations (`شدید`, `ایمنی`) applied | **Resolved** |
| **DEF-B03-08** | Rigid 34/32 occupation slots | `shiraz_file4_excel.py` | Profile abstraction preserves custom project titles in appendix | **Resolved** |

---

## 4. Acceptance Criteria & Downstream Handoff

- **Status**: Requirement B03 is functionally and technically complete (`qa_passed`).
- **Downstream Tracking**:
  - Independent numeric checksum verification and recalculation parity are tracked under **B05**.
  - Employer bundle sign-off and official release gate are tracked under **B06**.
