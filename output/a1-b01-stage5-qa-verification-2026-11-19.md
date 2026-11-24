# Phase A.1 Package B01 End-User QA Verification Evidence Report

- **Date / Timestamp**: 2026-11-19T21:46:00+03:30
- **Scope Evaluated**: Phase A.1 / Package B01 (`specs/057-a1-b01-data-contract`)
- **Evaluation Stage**: Stage 5 (Post-Implementation End-User QA Verification)
- **Live System Endpoints**:
  - Web UI: http://localhost:5173 (React Router 7 + Vite, HTTP 200/302 `/login` active)
  - API: http://localhost:8000 (Django 4.2 + DRF, `/api/v1/...` active)
  - Database: PostgreSQL 16 (port 5433, 40/40 blueprint tables + 25 extension tables verified)
  - Cache: Redis 7 (port 6379, rate-limiting & session cache verified)

---

## 1. Executive Summary & QA Verdict

- **QA Status**: `qa_passed` (for Package B01 scope)
- **Summary**: Package B01 (Daily Report Data Contract & Reference-Day Fixture) is fully implemented, verified, and passing in live environment testing across all personas (Admin, Project Manager, Viewer, and Unauthorized/Unauthenticated). All 11 contract regression and invariant test suites passed. Live REST endpoints (`/contract/`, `/contract-summary/`, `/by-date/`) correctly serve the published contract and synthetic fixture `SIM-A1-001` (`SIM-A1-001-12-1406-03-01`). Ratified decisions `C03`–`C08` and `GOV-01` are enforced. Prerequisite handoffs for B03 (multi-sheet date-range workbook DEL-03 and standalone discipline PDFs DEL-04) are preserved outside the B01 execution checklist as T030, while B02–B06 remain properly out of scope. Zero defects remain within Package B01.

---

## 2. Personas & RBAC Live Verification Matrix

| Persona / Role | Authentication & Authorization | Endpoint Tested | Expected Result | Actual Live HTTP Status | Verification Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Anonymous User** | Unauthenticated | `GET /api/v1/projects/:id/daily-reports/contract/` | 401 Unauthorized | `401 Unauthorized` | Pass |
| **Anonymous User** | Unauthenticated | `POST /api/v1/projects/:id/daily-reports/contract/` | 401 Unauthorized | `401 Unauthorized` | Pass |
| **Project Member (No `view_reports`)** | Authenticated (`user_finance_manager`), active member, lacks `view_reports` | `GET /api/v1/projects/:id/daily-reports/contract/` | 403 Forbidden | `403 Forbidden` | Pass |
| **Project Member (No `view_reports`)** | Authenticated (`user_finance_manager`), active member, lacks `view_reports` | `GET /api/v1/projects/:id/daily-reports/:pk/contract-summary/` | 403 Forbidden | `403 Forbidden` | Pass |
| **Project Manager** | Authenticated (`user_project_manager`), active member with role having `view_reports` | `GET /api/v1/projects/:id/daily-reports/contract/` | 200 OK | `200 OK` | Pass |
| **Project Manager** | Authenticated (`user_project_manager`), active member with role having `view_reports` | `GET /api/v1/projects/:id/daily-reports/:pk/contract-summary/` | 200 OK | `200 OK` | Pass |
| **Project Viewer** | Authenticated (`user_viewer`), active member with `view_reports` | `GET /api/v1/projects/:id/daily-reports/contract/` | 200 OK | `200 OK` | Pass |
| **Project Viewer** | Authenticated (`user_viewer`), active member with `view_reports` | `GET /api/v1/projects/:id/daily-reports/:pk/contract-summary/` | 200 OK | `200 OK` | Pass |
| **Administrator (Observation)** | Authenticated (`admin`), global superuser/admin group observation | `GET /api/v1/projects/:id/daily-reports/contract/` | 200 OK | `200 OK` | Pass |
| **Administrator (Write Lock)** | Authenticated (`admin`), attempts write to contract | `POST /api/v1/projects/:id/daily-reports/contract/` | 403 / 405 Method Not Allowed / Forbidden | `403 Forbidden` | Pass |

---

## 3. Requirement Verification & Acceptance Analysis

### B01-01: Versioned Contract & Synthetic Reference Day
- **Requirement**: Publish a versioned data contract and clearly labeled `SIM-A1-001` fixture for 1406-03-01 (project day 12) with complete field mappings and revision history.
- **Verification**:
  - `GET /api/v1/projects/:id/daily-reports/contract/` returns `contract_version: "1.0.0"`, `reference_form_version: "shiraz-file4-v1"`.
  - Fixture parameters verified: project code `SIM-A1-001`, Jalali report date `1406-03-01`, Gregorian `2027-05-22`, start date `1406-02-21` (`2027-05-11`), project day `12`, official report number `SIM-A1-001-12-1406-03-01`.
  - 18 broader sections and 18 field mappings present with complete drill-down paths.
- **Status**: **VERIFIED / PASS**

### B01-02: Governance & Anti-Fabrication (`C01`–`C10` + `GOV-01`)
- **Requirement**: Record `C01`–`C10` and `GOV-01` with provenance, preserving boundaries and never fabricating missing values or employer decisions.
- **Verification**:
  - `governance.employer_acceptance_representative` is `null`.
  - `governance.employer_acceptance_date` is `null`.
  - `governance.employer_acceptance_owner_package` is `"B06"`.
  - `governance.employer_acceptance_status` is `"pending_b06_handoff"`.
  - Scope decisions register has all 11 keys (`C01`–`C10`, `GOV-01`) with ratification metadata.
- **Status**: **VERIFIED / PASS**

### B01-03: Zero, Unset, and Not-Measured Semantics
- **Requirement**: Measured zero remains valid (`0`); unset (`null`) and not-measured remain unknown and are never silently coerced to zero.
- **Verification**:
  - Verified across 5 activities in `SIM-A1-001`: 2 measured zero (`quantity=0.00`, `quantity_measured=True`), 1 unset measured (`quantity=null`, `quantity_measured=True`), 1 unmeasured (`quantity=null`, `quantity_measured=False`), 1 positive quantity (`12.50`).
  - Summaries return total `12.50` and `unrecorded_count: 2`. When filtering unset items, total returns `null` (not `0`).
- **Status**: **VERIFIED / PASS**

### B01-04: Canonical Shifts, Durations, and Labor Metrics
- **Requirement**: Use worked shifts only with canonical IDs 1–3, actual durations, unknown missing durations, and distinct bilingual labor metrics.
- **Verification**:
  - `GET .../contract-summary/` returns worked shifts with `shift_id: 1` (`actual_duration_hours: "8.50"`, `recorded`) and `shift_id: 3` (`actual_duration_hours: null`, `unknown`).
  - `GET .../by-date/?date=1406/03/01&shift=1` returns the report with `canonical_worked_shift_ids: [1, 3]`.
  - Query with non-worked shift `shift=2` returns HTTP `404 Not Found`.
  - Labor metrics prevent conflation between headcount (`نفر`) and person-hours (`نفرساعت`).
- **Status**: **VERIFIED / PASS**

### B01-05: Job-Title Catalog & Shiraz 34/32 Profile
- **Requirement**: Separate the configurable project catalog from the 34/32 Shiraz profile and preserve extra/custom titles in an appendix.
- **Verification**:
  - `labor_profile_resolution` in summary confirms `profile_code: "shiraz-34-32-v1"`, `standard_indirect_slots: 34`, `standard_direct_slots: 32`, `appendix_indirect_count: 1`, `appendix_direct_count: 1`.
  - 68 total labor rows accurately partitioned without data loss or silent dropping.
- **Status**: **VERIFIED / PASS**

### B01-06: Official Headers, Weather, Outputs, and Boundaries
- **Requirement**: Define official report numbering, weather sources, required deliverables, unknown-data behavior, fingerprint scope.
- **Verification**:
  - Official numbering generated: `SIM-A1-001-12-1406-03-01`.
  - Weather correctly identifies observed log source and MET Norway Locationforecast 2.0 attribution. For future date 2027-05-22, forecast status is cleanly reported as `unknown` with `outside_forecast_window` (no hallucinated weather data).
  - Signature scope explicitly clarifies `mode: "actor_attribution_and_metadata_fingerprint"`, `pki_digital_signature_claimed: false`, `whole_body_tamper_seal_claimed: false`.
- **Status**: **VERIFIED / PASS**

---

## 4. Test Suite Execution & Schema Verification Summary

1. **Automated Unit & Integration Test Suite**:
   - Command: `python -m pytest field_reports/tests/test_a1_b01_data_contract.py`
   - Results: **11 passed**, 0 failed, 2 warnings (reportlab/pandas deprecation) in 151.65s.
2. **PostgreSQL Blueprint Schema Integrity**:
   - Command: `python manage.py verify_blueprint_schema`
   - Results: Found **40/40 blueprint tables**, **25 extension tables**. Blueprint intact.
3. **Database Migrations & Rollback Execution**:
   - `field_reports.0026_daily_report_b01_contract`: Applied cleanly. Partial unique constraint `unique_current_contract_daily_report_per_date` active.
   - `projects.0022_project_coordinates`: Applied cleanly.
4. **Synthetic Fixture Management Command**:
   - Command: `python manage.py seed_a1_reference_fixture`
   - Tested twice: 100% idempotent; prevents overwriting real project data if project code conflicts.

---

## 5. Handoff & Out-of-Scope Boundary Tracking

- **Package B01 Scope**: Complete and verified. Zero defects.
- **Pending Deliverables under B03 Handoff (T030)**:
  - `DEL-03`: Multi-sheet date-range Excel workbook.
  - `DEL-04`: Standalone discipline PDF export.
  - *Note*: Both deliverables are assigned to downstream Package B03 per contract boundary and are cleanly tracked in `specs/057-a1-b01-data-contract/tasks.md` under Phase 10 / B03 handoff.
- **B02–B06 Status**: Kept unstarted in accordance with project constraints.
