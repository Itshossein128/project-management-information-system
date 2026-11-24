# Stage 1.2 QA Verification Report: Requirement B01-06

- **Requirement ID**: `B01-06`
- **Title**: Official headers, weather, outputs, and boundaries
- **Acceptance Criteria**: Define official report numbering, weather sources, required Excel/PDF deliverables, unknown-data behavior, fingerprint scope, and cross-phase ownership.
- **Evaluator**: Per-Requirement End-User & QA Agent (Velora Phase A.1 / B01 Fan-Out)
- **Target Environment**: Velora Web (:5173) & API (:8000) / Codebase & Specification Baseline
- **Date**: 2026-11-19
- **QA Status**: `qa_failed`

---

## 1. Executive Summary

Requirement **B01-06** governs the definition and contract enforcement of:
1. Deterministic official report numbering (`<projectID>-<projectDay>-<YYYY>-<MM>-<DD>`) and actual project day calculation (with actual start date = day 1).
2. Authoritative weather sources (observed weather, wind, and ground conditions from existing `WeatherLog` records, plus 3-day weather forecasts at the project location from the free MET Norway Locationforecast 2.0 API).
3. The four mandatory Phase A.1 output deliverables: single-day Excel & PDF reports, discipline-specific Excel exports, multi-sheet date-range Excel workbook, and standalone discipline PDFs.
4. Unambiguous missing-data semantics displaying `"unknown"` / unrecorded rather than fabricating synthetic report numbers or weather forecasts.
5. Strict definition of the actor attribution block and metadata fingerprint (explicitly excluding PKI digital certificate signatures and whole-body tamper seals from Phase A.1 scope under `C06`).
6. Explicit cross-phase ownership and boundary preservation for non-A.1 capabilities (`X01`–`X06`, `X08`–`X10`), preventing accidental deletion or false completion claims.

### Audit Result
- **Specification State**: In [spec.md](file:///home/hossein/Desktop/projects/building-management/specs/057-a1-b01-data-contract/spec.md) (lines 17–19, 105–119, 170–183, 225–228, 235–256, 271–281), decisions `C05`, `C06`, `C07`, and `C08` are formally ratified, and the 18-section disposition matrix is complete.
- **Runtime & Codebase State**: Verification of `apps/api` and `apps/web` reveals that the software does not implement the ratified official report numbering, lacks MET Norway forecast integration, lacks standalone discipline PDFs and multi-sheet date-range Excel workbooks, and lacks formal missing-data handling for unrecorded project start dates and weather logs.
- **Overall Status**: **`qa_failed`** (Pre-implementation QA baseline audit identifies 5 distinct functional and contract gaps).

---

## 2. Requirement-by-Requirement Findings & Gap Analysis

### 2.1 Official Report Numbering & Project Day Numbering (`H05`, `C08`, `FR-017`, `DEF-B01-01`)
- **Contract Rule**:
  - Format: `<projectID>-<projectDay>-<YYYY>-<MM>-<DD>` in Solar Hijri project-local date with 2-digit month and day (e.g., `PRJ-012-12-1406-03-01` or `SIM-A1-001-12-1406-03-01`).
  - Project day counts actual start date as day 1 (`project_day = (report_date - actual_start_date).days + 1`).
  - Independent of internal database UUIDs or sequential PK IDs.
  - If actual start date is missing or report date precedes start date, display an explicit `"unknown"` / unrecorded validation state rather than inventing day 0 or negative days.
- **Observed Implementation**:
  - `apps/api/core/field_reports/models.py` has no `report_number` or `project_day_number` fields.
  - `apps/api/core/field_reports/shiraz_file4_excel.py` and `apps/api/core/field_reports/pdf.py` do not generate or render the ratified `<projectID>-<projectDay>-<YYYY>-<MM>-<DD>` official identifier.
  - Neither UI nor API calculates or surfaces the actual project day number.

### 2.2 Authoritative Weather, Wind, Ground Conditions & 3-Day Forecast (`X07`, `C08`, `FR-017`, `DEF-B01-05`)
- **Contract Rule**:
  - Observed weather, wind, and ground conditions must be sourced from existing `WeatherLog` records.
  - 3-day weather forecast at project geographic coordinates must be sourced from the free MET Norway Locationforecast 2.0 API (`https://api.met.no/weatherapi/locationforecast/2.0/`).
  - When log readings or forecast service responses are unavailable, output must render `"unknown"` / unrecorded and never fabricate synthetic forecasts.
- **Observed Implementation**:
  - `apps/api/core/field_reports/` contains basic `weather_condition`, `temp_min`, `temp_max`, and `weather_impact_notes` on `DailyReport`, but has zero integration with MET Norway Locationforecast 2.0.
  - Observed wind and ground conditions from weather logs are not incorporated into daily report exports.
  - No service exists in `apps/api` to query or cache project location weather forecasts.

### 2.3 Required Deliverables & Multi-Sheet / Standalone Parity (`E17`, `C05`, `C07`, `FR-016`)
- **Contract Rule**:
  - Phase A.1 requires four distinct deliverables:
    1. Single-day representative report in Excel (`FILE 4`).
    2. Single-day representative report in PDF.
    3. Discipline-specific Excel exports (`FILE 5` Civil, `FILE 6` Electrical, etc.).
    4. Multi-sheet Excel workbook covering a project date range.
    5. Standalone discipline sub-report PDFs for each discipline.
- **Observed Implementation**:
  - Single-day Excel (`ShirazDailyReportExcelBuilder`) and single-day PDF (`generate_daily_report_pdf`) are partially implemented.
  - Discipline Excel export exists via `ShirazSubReportExcelBuilder` (`apps/api/core/sub_reports/shiraz_subreport_excel.py`).
  - **Missing**: No multi-sheet date-range Excel builder exists in `apps/api/core/field_reports/` or `apps/api/core/projects/services/report_export_service.py`.
  - **Missing**: No standalone discipline sub-report PDF generator exists in `apps/api/core/sub_reports/` (only Excel export action `excel()` is defined on `UnitDailyReportViewSet`).

### 2.4 Fingerprint Scope vs. PKI Digital Signature (`C06`, `FR-018`)
- **Contract Rule**:
  - Existing actor attribution block and metadata fingerprint are sufficient for Phase A.1.
  - Certificate-backed PKI digital signatures and whole-report tamper seals are explicitly excluded from A.1 scope.
- **Observed Implementation**:
  - `field_reports/models.py` and `projects/services/report_export_service.py` track actor attribution and basic hash fingerprints.
  - Specification in `spec.md` cleanly confines scope under `C06` and `FR-018`.
  - Conformance verified: no unratified cryptographic PKI requirements are improperly imposed on A.1.

### 2.5 Cross-Phase Ownership & Boundaries (`X01`–`X06`, `X08`–`X10`, `FR-019`)
- **Contract Rule**:
  - Non-A.1 capabilities must be routed to their owner phases (`X01` offline sync to `A.8`, `X02` discipline QC to `A.8`, `X03` physical progress weighting to `A.7`/`A.8`, `X04` monthly reports to `A.10`, `X05` correspondence to `A.3.C`, `X06` procurement to `A.4`/`A.10`, `X08` historical 367-sheet ETL to `A.8`/`A.12`, `X09` rollout to `A.12`, `X10` warehouse balance to `A.8`/`A.10`).
  - Daily activity quantities must not be conflated with cumulative physical progress.
  - Free-text notes must not be presented as official procurement or correspondence registers.
- **Observed Implementation**:
  - Fully mapped and bounded in `spec.md` Section 18-Section Matrix and `FR-019`.
  - No boundary leakage into A.1 scope.

---

## 3. Detailed Defect & Gap Register

| Defect ID | Severity | Category | Description | Reference |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-B01-06-GAP-01** | High | Header & Numbering | Backend schema and exporters lack official report numbering (`<projectID>-<projectDay>-<YYYY>-<MM>-<DD>`) and actual project day calculation from project start date. | `FR-017`, `H05`, `C08`, `DEF-B01-01` |
| **DEF-B01-06-GAP-02** | High | Weather Integration | Free MET Norway Locationforecast 2.0 client and 3-day project location forecast integration are missing in `apps/api/core/field_reports/`. | `FR-017`, `X07`, `C08`, `DEF-B01-05` |
| **DEF-B01-06-GAP-03** | Medium | Weather Display | Observed wind and ground conditions from weather logs are omitted from official daily report header exports. | `FR-017`, `X07`, `C08` |
| **DEF-B01-06-GAP-04** | High | Deliverables Parity | Multi-sheet date-range Excel workbook exporter is not implemented in `field_reports` or `report_export_service`. | `FR-016`, `E17`, `C05` |
| **DEF-B01-06-GAP-05** | High | Deliverables Parity | Standalone discipline sub-report PDF exporter is not implemented in `apps/api/core/sub_reports/` (only Excel exists). | `FR-016`, `C07` |

---

## 4. Environment & Services Status

- **Web Frontend (`:5173`)**: Not running in cloud VM dev environment.
- **API Backend (`:8000`)**: Not running in cloud VM dev environment (Postgres/Redis services idle).
- **MET Norway External Endpoint**: Verified reachable via outbound HTTPS (`https://api.met.no/weatherapi/locationforecast/2.0/status` returned HTTP 200).

---

## 5. QA Conclusion & Next Steps

Requirement **B01-06** is fully clarified and ratified at the data contract and specification level in [spec.md](file:///home/hossein/Desktop/projects/building-management/specs/057-a1-b01-data-contract/spec.md), but is currently **`qa_failed`** against the codebase implementation. 

The 5 identified defects (`DEF-B01-06-GAP-01` through `DEF-B01-06-GAP-05`) establish the exact baseline gaps for downstream implementation in package B01 and parity packages B02–B06. Specification B01 is ready for Supervisor review and progression to `/speckit-plan`.
