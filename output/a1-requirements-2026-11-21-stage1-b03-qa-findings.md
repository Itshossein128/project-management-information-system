# Phase A.1 Package B03 End-User QA Verification & Requirement Parity Report

- **Document Identifier**: `a1-requirements-2026-11-21-stage1-b03-qa-findings.md`
- **Requirement ID**: `B03`
- **Title**: Reference-form parity (Excel/PDF values, fields, labels, roles, unknown semantics, long text, pagination, printing, timezone, and watermark match the agreed reference form)
- **Phase**: A.1 (Daily Reports and Export Parity)
- **Evaluation Stage**: Stage 1.2 (Per-Requirement Fan-Out Verification)
- **Evaluation Date / Timestamp**: 2026-11-21T23:42:00+03:30
- **Target Systems Tested**:
  - Web UI: http://localhost:5173 (React Router 7 + Vite — HTTP 302 redirect to /login verified live)
  - API: http://localhost:8000 (Django 4.2.11 + DRF — port 8000 active)
  - Database: PostgreSQL 16 (Port 5433)
  - Cache: Redis (Port 6379)
- **Associated Spec & Task Definitions**: `specs/059-a1-b03-reference-parity`, `specs/044-shiraz-excel-parity-pdf`

---

## 1. Executive Summary & QA Verdict

- **Requirement Evaluation Status**: **VERIFIED / TECHNICAL READINESS PASSED (`qa_passed`)**
- **QA Summary**:
  Package B03 specifies reference-form parity across Excel and PDF outputs (DEL-01: FILE 4 Shiraz parity daily Excel; DEL-02: Bilingual daily summary PDF; DEL-03: Discipline sub-reports FILE 5, FILE 6, and unit PDFs; DEL-04: Date-range multi-sheet workbook).
  All 8 historical Stage 1.2 QA defects (`DEF-B03-01` through `DEF-B03-08`) identified on 2026-11-19 have been implemented and verified in the codebase:
  1. `DEF-B03-01` (Shift hours): Actual worked shift hours and elapsed durations are dynamically bound from `DailyReportWorkedShift` rather than emitting static hardcoded text.
  2. `DEF-B03-02` (Side-by-side manpower): Direct (34) and indirect (32) labor tables are structured side-by-side starting on row 6, adhering strictly to the physical Shiraz FILE 4 reference layout.
  3. `DEF-B03-03` (Excel print settings): Workbooks enforce A4 landscape (`paperSize=9`), `fitToWidth=1`, dynamic row auto-wrapping, and repeating table headers (`print_title_rows`).
  4. `DEF-B03-04` (PDF signatures & watermarks): Signatures print real actor legal roles, organizational positions, and Tehran timestamps. Diagonal watermarks (`پیش‌نویس — غیرقابل استناد رسمی`) cover all pages of draft/under-review reports and are cleanly omitted on approved reports.
  5. `DEF-B03-05` (Equipment unmeasured hours): Unrecorded/legacy machinery operating hours render empty cells in Excel and dashes in PDF, cleanly distinguishing unmeasured states from measured zero hours.
  6. `DEF-B03-06` (Concrete & QC test data): Concrete pours capture batching plant, transit mixer IDs, slump tests, and canonical lab sample IDs with direct drill-down links.
  7. `DEF-B03-07` (Bilingual localization): HSE incident severity and types use authentic Persian terminology (`شدید`, `ایمنی`).
  8. `DEF-B03-08` (Profile catalog flexibility): Project occupations beyond the standard 34/32 profile are systematically accommodated in the appendix table without polluting fixed slots.

- **Current Verification Evidence**:
  - `apps/web`: `pnpm typecheck` passed with 0 errors (exit code 0).
  - Web service responds at `http://localhost:5173/` (HTTP 302 to `/login`).
  - Core test suites in `apps/api/core/field_reports/tests/` and `apps/api/core/sub_reports/tests/` demonstrate 47 passing tests across Excel parity, PDF formatting, unit discipline PDFs, and workbook range generation.
  - Zero open defects remain within the direct scope of B03.

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

## 4. Acceptance Criteria & Delivery Boundary Note

- **Status**: Requirement B03 is functionally and technically complete (`qa_passed`).
- **Phase A.1 Note**:
  - Independent numeric checksum verification and recalculation parity are tracked under **B05**.
  - Employer bundle sign-off and official release gate are tracked under **B06**.
