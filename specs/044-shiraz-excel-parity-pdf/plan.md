# Implementation Plan: Shiraz Excel Forms Parity & Official PDF Standardization

**Branch**: `044-shiraz-excel-parity-pdf` | **Date**: 2026-10-28 | **Spec**: [Feature Specification](file:///home/hossein/Desktop/projects/building-management/specs/044-shiraz-excel-parity-pdf/spec.md)

**Input**: Feature specification from `specs/044-shiraz-excel-parity-pdf/spec.md`, `SPEC-11-SHIRAZ-EXCEL-PARITY-PDF.md`, `GAP-SPEC-11-SHIRAZ-EXCEL-PARITY-PDF.md`, and Shiraz blueprint documentation.

## Summary

This feature achieves 100% parity with the Shiraz National Housing 2,000-unit project field reporting standards:
1. Generates master daily report Excel spreadsheets adhering strictly to Shiraz FILE 4 layout with RTL orientation, Persian typography, 34 staff labor rows, 32 direct worker rows, materials, concrete pouring, machinery, and daily activities with native spreadsheet sum formulas.
2. Generates discipline-specific sub-report spreadsheets matching Shiraz FILE 5 (Civil, featuring `قطعه` and `درصد اجرا` with `0.0%` percentage styling) and Shiraz FILE 6 (Electrical, omitting parcel and percentage).
3. Standardizes official PDF generation with ReportLab: 3-tier signature boxes (Site Supervisor, Technical Office, Project Manager), deterministic SHA-256 cryptographic audit fingerprint, diagonal draft watermarks for unapproved reports, and standard `daily-report-{report_date}-{shift}.pdf` naming.
4. Synchronizes multi-dimensional filters with browser URL search parameters (`useSearchParams`) across Daily Reports and the Project Activity Log, provides real-time summary aggregation (man-days and unit quantities), and enables flat database Excel export (Shiraz FILE 1).
5. Updates the repository Decision Tree in `docs/decision-tree/`.

## Technical Context

**Language/Version**: Python 3.12 (pinned Django 4.2.11 + DRF), TypeScript 5.6 (React 19, React Router 7, Vite, Tailwind CSS).

**Primary Dependencies**:
- Backend: `openpyxl`, `reportlab`, `arabic-reshaper`, `python-bidi`, `django`, `djangorestframework`, `drf-spectacular`.
- Frontend: `react`, `react-router`, `@tanstack/react-query`, `lucide-react`, `i18next`.

**Storage**: PostgreSQL (UUID primary keys, soft-delete audit records) & Redis (caching and rate-limiting).

**Testing**: `pytest` (backend) with `--reuse-db` against PostgreSQL/Redis; `tsc` and Vite build (frontend).

**Target Platform**: Linux / Containerized modern web browsers.

**Project Type**: Monorepo (`apps/api` and `apps/web`).

**Performance Goals**:
- Master Excel (FILE 4) and PDF generation: < 3.0 seconds for complex daily reports.
- Filtered activity log query with URL param hydration: < 2.0 seconds.

**Constraints**:
- Spreadsheet orientation MUST be Right-to-Left (`ws.sheet_view.rightToLeft = True`).
- Calculations MUST use native spreadsheet formulas (`=SUM(...)`).
- Unapproved PDF reports MUST render a diagonal draft watermark.
- Filter state MUST sync bi-directionally with browser URL search params without page reloads.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Server-Enforced Authorization)**: All Excel and PDF download endpoints verify `view_reports` permission and `IsProjectMember` server-side. **PASS**
- **Principle II (Data Integrity)**: Uses existing models `DailyReport`, `DailyReportActivity`, `DailyLabor`, `DailyEquipment`, `DailyMaterial`, `DailyConcrete`, `DisciplineSubReport`, `DisciplineSubReportActivity` without breaking schema or altering migration history. **PASS**
- **Principle III (Bilingual & Locale-Correct)**: Persian headings, Jalali date formatting, weekday names, and RTL spreadsheet/PDF rendering. **PASS**
- **Principle IV (Explicit, Safe Business Mutations)**: Exports are read-only idempotent queries; approval state and audit hashes are deterministic and tamper-evident. **PASS**
- **Principle V (Minimal Coherent Changes)**: Extends existing `DailyReportViewSet`, `UnitReportViewSet`, `ActivityLogView` and views in place without parallel models. **PASS**
- **Principle VI (Evidence-Based Verification)**: Automated pytest tests verify openpyxl workbooks, formula expressions, PDF byte signatures, watermark presence, and frontend build passes cleanly. **PASS**
- **Principle VII (Accessible UX)**: URL-synced search params, intuitive download buttons, and clear responsive summary cards. **PASS**

## Project Structure

### Documentation (this feature)

```text
specs/044-shiraz-excel-parity-pdf/
├── plan.md              # This file
├── research.md          # Technical research & architecture patterns
├── data-model.md        # Entities, services, and endpoints specification
├── quickstart.md        # Developer testing and verification guide
├── contracts/           # OpenAPI contracts for exports
│   ├── openapi-daily-report-excel.yaml
│   └── openapi-sub-report-excel.yaml
└── tasks.md             # Execution task list
```

### Source Code (repository root)

```text
apps/api/core/
├── field_reports/
│   ├── shiraz_file4_excel.py        # Shiraz FILE 4 Excel generator
│   ├── shiraz_file1_excel.py        # Shiraz FILE 1 Activity log Excel generator
│   ├── pdf.py                       # Enhanced PDF generator with signatures, hash, watermark
│   ├── daily_report_views.py        # Added 'excel' action to DailyReportViewSet
│   ├── report_views.py              # Added ActivityLogExcelView
│   ├── urls.py                      # Activity log excel route
│   └── tests/
│       ├── test_shiraz_file4_excel.py
│       └── test_pdf_signatures_watermark.py
├── sub_reports/
│   ├── shiraz_subreport_excel.py    # FILE 5 (Civil) and FILE 6 (Electrical) Excel generator
│   ├── unit_report_views.py         # Added 'excel' action to UnitReportViewSet
│   └── tests/
│       └── test_shiraz_subreport_excel.py

apps/web/src/
├── app/
│   ├── lib/api/
│   │   ├── daily-reports.ts         # Added fetchReportExcel, fetchActivityLogExcel
│   │   └── unit-reports.ts          # Added fetchSubReportExcel
│   └── routes/
│       ├── daily-reports-list.tsx   # useSearchParams synchronization
│       ├── daily-report-view.tsx    # FILE 4 Excel download button, updated PDF action
│       └── project-activity-log.tsx # useSearchParams sync, summary bar, FILE 1 export
└── components/
    └── department/
        └── unit-daily-report-panel.tsx # Sub-report Excel export button

docs/decision-tree/
└── login/submit-valid-credentials/select-project/[navigate-daily-reports]/
    ├── [view-report]/
    │   ├── [export-report-excel]/README.md
    │   └── [export-report-pdf]/README.md
    ├── [export-sub-report-excel]/README.md
    └── filter-and-change-view/README.md
```

## Complexity Tracking

No constitution violations detected. Standard Django DRF and React Router 7 patterns used.
