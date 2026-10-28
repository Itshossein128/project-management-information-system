# Tasks: Shiraz Excel Forms Parity & Official PDF Standardization

**Input**: Design documents from `specs/044-shiraz-excel-parity-pdf/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`).

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/.

**Organization**: Tasks are grouped by user story and execution phase.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. US1, US2, US3, US4, US5)

---

## Phase 1: Setup & Foundational Prerequisites

**Purpose**: Shared infrastructure and setup verification.

- [x] T001 Verify backend environment (PostgreSQL 5433, Redis 6379, openpyxl, reportlab).
- [x] T002 Add frontend API helper functions `fetchReportExcel`, `fetchActivityLogExcel` in `apps/web/src/app/lib/api/daily-reports.ts` and `fetchSubReportExcel` in `apps/web/src/app/lib/api/unit-reports.ts`.

---

## Phase 2: User Story 1 - Shiraz FILE 4 Daily Report Excel Export (Priority: P1)

**Goal**: Deliver master daily report spreadsheet generator strictly matching Shiraz FILE 4 (RTL, header, 34 indirect staff roles with `=SUM()`, 32 direct worker roles with `=SUM()`, grand total manpower formula, materials, concrete pouring, machinery, and daily activities).

**Independent Test**: Download Excel from `GET /api/v1/projects/{project_pk}/daily-reports/{id}/excel/` and open in spreadsheet viewer; check RTL orientation, 34 staff rows, 32 worker rows, formulas, and child tables.

### Implementation Tasks for User Story 1
- [x] T003 [P] [US1] Create Shiraz FILE 4 Excel generator service in `apps/api/core/field_reports/shiraz_file4_excel.py`.
- [x] T004 [US1] Expose `excel` action on `DailyReportViewSet` in `apps/api/core/field_reports/daily_report_views.py` returning attachment `daily-report-{report_date}-{shift}.xlsx` with `view_reports` permission.
- [x] T005 [P] [US1] Add "خروجی اکسل (FILE 4)" download button in `apps/web/src/app/routes/daily-report-view.tsx`.
- [x] T006 [US1] Write automated pytest suite in `apps/api/core/field_reports/tests/test_shiraz_file4_excel.py` verifying RTL, header, 34 indirect roles, 32 direct roles, and `=SUM(...)` formulas.

---

## Phase 3: User Story 2 - Discipline Sub-Report Excel Exports for Civil (FILE 5) and Electrical (FILE 6) (Priority: P1)

**Goal**: Deliver trade-specific spreadsheet exports for Civil (`SpecialtyUnit.BUILDINGS` / FILE 5 with `قطعه` and `درصد اجرا` formatted `0.0%`) and Electrical (`SpecialtyUnit.ELECTRICAL` / FILE 6 omitting parcel and percentage).

**Independent Test**: Request `GET /api/v1/projects/{project_pk}/units/{unit}/daily-reports/{id}/excel/` for both `buildings` and `electrical` units and verify structural column parity.

### Implementation Tasks for User Story 2
- [x] T007 [P] [US2] Create trade-specific sub-report Excel generator service in `apps/api/core/sub_reports/shiraz_subreport_excel.py`.
- [x] T008 [US2] Expose `excel` action on `UnitReportViewSet` in `apps/api/core/sub_reports/unit_report_views.py` returning trade-specific `.xlsx` with `view_reports` permission.
- [x] T009 [P] [US2] Add sub-report Excel export button in `apps/web/src/components/department/unit-daily-report-panel.tsx`.
- [x] T010 [US2] Write automated pytest suite in `apps/api/core/sub_reports/tests/test_shiraz_subreport_excel.py` testing FILE 5 and FILE 6 generation.

---

## Phase 4: User Story 3 - Official Standardized PDF Export with Digital Signatures, Audit Hash & Draft Watermark (Priority: P1)

**Goal**: Standardize daily report PDF with 3-tier signature blocks (Preparer, Reviewer, Approver), 16-character SHA-256 Audit Security Hash, diagonal semi-transparent draft watermark on unapproved reports, and filename `daily-report-{report_date}-{shift}.pdf`.

**Independent Test**: Export PDF for a draft report (verify diagonal draft watermark), approve the report and re-export (verify watermark absent, 3 signature boxes populated, audit hash present, filename standardized).

### Implementation Tasks for User Story 3
- [x] T011 [US3] Implement SHA-256 audit fingerprint generator `generate_report_audit_hash(report)` in `apps/api/core/field_reports/pdf.py`.
- [x] T012 [US3] Implement canvas draft watermark callback `make_draft_watermark` and three-tier signature table in `apps/api/core/field_reports/pdf.py`, standardizing filename to `daily-report-{report_date}-{shift}.pdf`.
- [x] T013 [P] [US3] Update PDF download filename handling in `apps/web/src/app/routes/daily-report-view.tsx`.
- [x] T014 [US3] Write automated pytest suite in `apps/api/core/field_reports/tests/test_pdf_signatures_watermark.py` verifying watermark on draft, signature boxes on approved, audit hash, and standardized filename.

---

## Phase 5: User Story 4 - Multi-Dimensional Activity Log Filtering with Full URL State Persistence & Master Activity Export (FILE 1) (Priority: P2)

**Goal**: Synchronize all filter controls with browser URL search parameters (`useSearchParams`) in Daily Reports list and Project Activity Log, provide real-time aggregate summary bar (man-days and unit quantities), and deliver flat cumulative Excel export (FILE 1).

**Independent Test**: Apply multi-parameter filters in `project-activity-log.tsx`, copy URL into another browser tab, verify exact filter and pagination restoration, check summary bar aggregates, and download FILE 1 Excel.

### Implementation Tasks for User Story 4
- [x] T015 [P] [US4] Create Shiraz FILE 1 Activity Log Excel generator in `apps/api/core/field_reports/shiraz_file1_excel.py`.
- [x] T016 [US4] Expose `ActivityLogExcelView` endpoint `GET /api/v1/projects/{project_pk}/activity-log/excel/` in `apps/api/core/field_reports/report_views.py` and `apps/api/core/field_reports/urls.py`.
- [x] T017 [P] [US4] Synchronize filter state with `useSearchParams` in `apps/web/src/app/routes/daily-reports-list.tsx`.
- [x] T018 [P] [US4] Synchronize filters with `useSearchParams`, add summary metric bar, and add FILE 1 Excel download button in `apps/web/src/app/routes/project-activity-log.tsx`.
- [x] T019 [US4] Write automated pytest in `apps/api/core/field_reports/tests/test_shiraz_file1_excel.py` verifying FILE 1 export filtering and formatting.

---

## Phase 6: User Story 5 - Decision Tree State Machine Synchronization (Priority: P2)

**Goal**: Synchronize application decision tree documentation in `docs/decision-tree/` to document the new export routes, permission gates, and URL parameter persistence.

**Independent Test**: Verify markdown nodes exist and reference links resolve cleanly.

### Implementation Tasks for User Story 5
- [x] T020 [P] [US5] Add `[export-report-excel]/README.md` and update `[export-report-pdf]/README.md` under `docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-daily-reports]/[view-report]/`.
- [x] T021 [P] [US5] Add `[export-sub-report-excel]/README.md` under `docs/decision-tree/login/submit-valid-credentials/select-project/[navigate-daily-reports]/` and reference sub-reports.
- [x] T022 [P] [US5] Update `filter-and-change-view/README.md` in `docs/decision-tree/` documenting URL query parameter persistence (`useSearchParams`).

---

## Phase 7: Polish, Quality Gates & Verification

**Purpose**: End-to-end regression validation and build verification.

- [x] T023 Run full backend pytest test suite: `cd apps/api/core && ../.venv/bin/python -m pytest field_reports/tests/ sub_reports/tests/ --reuse-db`.
- [x] T024 Run frontend build validation: `pnpm --filter web build`.
- [x] T025 Update `tasks.md` with all completed tasks and create comprehensive implementation summary.

---

## Phase 10: Convergence

**Purpose**: Close edge-case, documentation, and verification gaps found by comparing the completed implementation with SPEC-11 and the decision-tree governance rules.

- [x] T026 [US1] Add an explicit empty-report FILE 4 regression path that preserves every required section/header row and emits valid zero-valued/native `=SUM(...)` formulas for empty child sections, with pytest coverage in `apps/api/core/field_reports/tests/test_shiraz_file4_excel.py` (FR-001, Edge Cases: empty/inactive report) (partial)
- [x] T027 [US3] Add multi-page PDF watermark coverage and direct-approval signature coverage, normalize the reviewer fallback text to `بدون نیاز به بررسی دفتر فنی`, and verify the watermark appears on first and later pages without obscuring the report content (FR-011, FR-012, Edge Cases: multi-page PDF and direct approval) (partial)
- [x] T028 [US2] Render null and zero civil execution percentages as numeric zero cells with native `0.0%` formatting, and add pytest coverage for both values in `apps/api/core/sub_reports/tests/test_shiraz_subreport_excel.py` (FR-006, Edge Cases: null/zero execution percentage) (partial)
- [x] T029 [US5] Reconcile the four Shiraz decision-tree READMEs and `inventory.json` verification metadata with the implemented routes and exact audit-hash contract, then run the scoped decision-tree checks (FR-020, US5/AC1–AC4) (partial)
