# Phase A.1 Requirement B01 End-User & QA Verification Report

- **Date / Timestamp**: 2026-11-21T23:45:00+03:30
- **Requirement ID**: `B01`
- **Title**: Data contract and reference-day fixture
- **Acceptance Criteria**: Independently map every required field and complete reference day; resolve C01-C08 decisions affecting official output.
- **Workflow Phase**: Stage 1.2 (Per-Requirement End-User QA Verification)
- **Live Environment State**:
  - PostgreSQL 16: Active on 5433 (all blueprint tables verified, migrations applied up to `field_reports.0028` and `sub_reports.0016`)
  - Redis 7: Active on 6379 (caching, sessions, rate-limiting operational)
  - Synthetic Fixture: `SIM-A1-001` (Representative day `1406-03-01`, Project day `12`, Official report code `SIM-A1-001-12-1406-03-01`)

---

## 1. Executive Summary & Verification Verdict

- **Status**: `implemented_and_verified` (QA Status: `qa_passed`)
- **Defects Detected**: 0
- **Findings Summary**:
  Requirement `B01` has been fully implemented and verified in the codebase and live database environment. The versioned data contract (`1.0.0`) maps every required field across all 18 broader daily sections. Decisions `C01` through `C08` and governance `GOV-01` are ratified and enforced in code and contract schemas. The synthetic reference-day fixture (`SIM-A1-001` for Jalali 1406-03-01 / Gregorian 2027-05-22) seeds idempotently, adheres to non-fabrication policies (employer acceptance fields remain `null` pending B06 handoff, future weather status reported as `unknown`), and distinguishes measured zeros (`0.00`) from unmeasured/unset fields (`null`). All 11 automated contract verification suites passed without error.

---

## 2. Scope Decisions Verification (`C01`–`C08` + `GOV-01`)

| Decision ID | Description | Enforced Implementation Behavior | Status |
| :--- | :--- | :--- | :--- |
| **C01** | Raw entry vs. derived summary | Operational input remains confined to discipline sub-reports; project-level daily report acts as derived approved summary with metadata lock. | Verified |
| **C02** | Zero vs. unset / null semantics | Measured zero (`0.00`) is valid and retained; unset and unmeasured quantities remain `null` (not coerced to zero). | Verified |
| **C03** | Worked shifts and durations | Canonical shifts 1–3 supported; non-worked shifts return 404; actual durations preserved or flagged `unknown`. | Verified |
| **C04** | Shiraz 34/32 labor profile | 34 indirect and 32 direct slots enforced; project catalog configured without dropping extra/custom titles (placed in appendix). | Verified |
| **C05** | Single-day vs multi-sheet workbook | Single reference-day contract delivered in B01; multi-sheet date-range Excel workbook tracked as handoff item `DEL-03` to B03. | Verified |
| **C06** | Digital signature semantics | Metadata fingerprint and actor attribution recorded; no false claims of whole-body PKI tamper seal made. | Verified |
| **C07** | Sub-report PDF output | Daily report PDF export standardized; standalone sub-report PDF tracked as handoff `DEL-04` to B03. | Verified |
| **C08** | Header & weather boundaries | Official numbering `SIM-A1-001-12-1406-03-01` validated; MET Norway forecast attribution clean, out-of-range forecasts marked `unknown`. | Verified |
| **GOV-01** | Reference-day governance | Synthetic project `SIM-A1-001` explicitly labeled; employer acceptance representative and date left `null` pending B06. | Verified |

---

## 3. End-User Persona & RBAC Verification Matrix

| Persona | Role / Permissions | Endpoint Tested | Expected HTTP | Actual HTTP | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Anonymous User** | Unauthenticated | `GET /api/v1/projects/:id/daily-reports/contract/` | 401 Unauthorized | 401 | Pass |
| **Anonymous User** | Unauthenticated | `POST /api/v1/projects/:id/daily-reports/contract/` | 401 Unauthorized | 401 | Pass |
| **Project Member** | Lacks `view_reports` | `GET /api/v1/projects/:id/daily-reports/contract/` | 403 Forbidden | 403 | Pass |
| **Project Member** | Lacks `view_reports` | `GET /api/v1/projects/:id/daily-reports/:pk/contract-summary/` | 403 Forbidden | 403 | Pass |
| **Project Manager** | Member with `view_reports` | `GET /api/v1/projects/:id/daily-reports/contract/` | 200 OK | 200 | Pass |
| **Project Manager** | Member with `view_reports` | `GET /api/v1/projects/:id/daily-reports/:pk/contract-summary/` | 200 OK | 200 | Pass |
| **Viewer** | Member with `view_reports` | `GET /api/v1/projects/:id/daily-reports/contract/` | 200 OK | 200 | Pass |
| **Administrator** | Superuser / Admin group | `GET /api/v1/projects/:id/daily-reports/contract/` | 200 OK | 200 | Pass |
| **Administrator** | Write attempt on contract | `POST /api/v1/projects/:id/daily-reports/contract/` | 403 Forbidden | 403 | Pass |

---

## 4. Test Suite Execution & Evidence

- **Command**: `python -m pytest field_reports/tests/test_a1_b01_data_contract.py`
- **Results**: 11 passed in 199.86s
- **Suites Verified**:
  1. `test_seed_is_idempotent_and_scoped`: Pass
  2. `test_seed_refuses_existing_non_fixture_project`: Pass
  3. `test_contract_permissions_and_query_params`: Pass
  4. `test_measured_zero_and_unknown_are_distinct`: Pass
  5. `test_canonical_shifts_and_actual_duration`: Pass
  6. `test_form_profile_has_fixed_slots_and_preserves_appendix`: Pass
  7. `test_numbering_observed_weather_and_summary`: Pass
  8. `test_legacy_summary_warns_without_merging_reports`: Pass
  9. `test_b01_migrations_preserve_legacy_and_enforce_uniqueness`: Pass
  10. Additional invariant & contract structure tests: Pass

---

## 5. Downstream Handoff Status
- Package B01 has zero open defects.
- Handoff deliverables `DEL-03` (multi-sheet workbook) and `DEL-04` (discipline sub-report PDF) are assigned to downstream Package B03 and do not block B01 completion.
