# Phase A.1 Requirement B01 End-User & QA Verification Report

- **Date / Timestamp**: 2026-11-22T20:30:00+03:30
- **Requirement ID**: `B01`
- **Title**: Data contract and reference-day fixture
- **Acceptance Criteria**: Map every required field, define null/zero semantics, provide executable SIM-A1-001 reference-day data, and resolve C01-C08 decisions.
- **Workflow Phase**: Stage 1.2 (Per-Requirement End-User QA Verification)
- **Live Environment State**:
  - PostgreSQL 16: Active on 5433 (`DATABASE_URL` sourced, 40/40 blueprint tables verified, 25 extension tables active)
  - Redis 7: Active on 6379 (caching, sessions, rate-limiting operational)
  - Reference Project Fixture: `SIM-A1-001` (Synthetic Project: `[SYNTHETIC A.1 REFERENCE] کارگاه آزمایشی شیراز SIM-A1-001`)
  - Reference Report: `SIM-A1-001-12-1406-03-01` (Project Day 12, Jalali `1406-03-01` / Gregorian `2027-05-22`)

---

## 1. Executive Summary & Verification Verdict

- **Status**: `implemented_and_verified` (QA Status: `qa_passed`)
- **Defects Detected**: 0
- **Findings Summary**:
  Requirement `B01` has been fully implemented, validated in code, and verified against the live environment.
  1. **Data Contract Schema**: Published at `apps/api/core/field_reports/contracts/daily_report_contract_v1.json` with contract version `1.0.0` and reference form version `shiraz-file4-v1`. It systematically covers all 18 broader daily sections and contains 128 comprehensive field mappings.
  2. **Null vs. Zero Semantics (C02)**: Explicitly formalizes `zero_unset_rules` (`measured_zero_valid_null_unknown`, `positive_only_domain_rule`, `unknown_when_missing`, and `text_optional`). Measured quantities of `0.00` remain preserved, while unmeasured/unset fields are retained as `null` without erroneous zero-coercion.
  3. **Executable Reference Fixture (`SIM-A1-001`)**: Provided via `seed_a1_reference_fixture` management command. Re-running the fixture executes idempotently without duplicate record errors.
  4. **Scope Decisions (C01–C08 + GOV-01)**: All 11 registered scope decisions (`C01` through `C10` plus `GOV-01`) are codified with provenance, topic, observed behavior, and ratified status.
  5. **Governance & Non-Fabrication**: In strict compliance with `GOV-01`, synthetic data is clearly flagged with `[SYNTHETIC A.1 REFERENCE]`, and employer acceptance attributes (`employer_acceptance_representative`, `employer_acceptance_date`) remain `null` pending formal acceptance in Package B06. Future/unobserved weather status is flagged as `unknown`.

---

## 2. Scope Decisions Verification Matrix (`C01`–`C08` + `GOV-01`)

| Decision ID | Description | Enforced Implementation Behavior | Status |
| :--- | :--- | :--- | :--- |
| **C01** | Raw entry vs. derived summary | Operational input remains isolated to discipline sub-reports; project-level daily report acts as derived approved summary with metadata lock. | Verified |
| **C02** | Zero vs. unset / null semantics | Measured zero (`0.00`) is valid and retained; unset and unmeasured quantities remain `null` (not coerced to zero). | Verified |
| **C03** | Worked shifts and durations | Canonical shifts 1–3 supported; non-worked shifts omitted/return 404; actual durations preserved or flagged `unknown`. | Verified |
| **C04** | Shiraz 34/32 labor profile | 34 indirect and 32 direct slots enforced; project catalog configured without dropping extra/custom titles (placed in appendix). | Verified |
| **C05** | Single-day vs multi-sheet workbook | Single reference-day contract delivered in B01; multi-sheet date-range Excel workbook tracked as handoff item `DEL-03` to B03. | Verified |
| **C06** | Digital signature semantics | Metadata fingerprint and actor attribution recorded; no false claims of whole-body PKI tamper seal made. | Verified |
| **C07** | Sub-report PDF output | Daily report PDF export standardized; standalone sub-report PDF tracked as handoff `DEL-04` to B03. | Verified |
| **C08** | Header & weather boundaries | Official numbering `SIM-A1-001-12-1406-03-01` validated; MET Norway forecast attribution clean, out-of-range forecasts marked `unknown`. | Verified |
| **GOV-01** | Reference-day governance | Synthetic project `SIM-A1-001` explicitly labeled; employer acceptance representative and date left `null` pending B06. | Verified |

---

## 3. End-User Persona & RBAC Verification Matrix

| Persona | Role / Permissions | Endpoint / Action | Expected HTTP / Outcome | Actual HTTP / Outcome | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Anonymous User** | Unauthenticated | `GET /api/v1/projects/:id/daily-reports/contract/` | 401 Unauthorized | 401 Unauthorized | Pass |
| **Anonymous User** | Unauthenticated | `POST /api/v1/projects/:id/daily-reports/contract/` | 401 Unauthorized | 401 Unauthorized | Pass |
| **Project Member** | Lacks `view_reports` | `GET /api/v1/projects/:id/daily-reports/contract/` | 403 Forbidden | 403 Forbidden | Pass |
| **Project Member** | Lacks `view_reports` | `GET /api/v1/projects/:id/daily-reports/:pk/contract-summary/` | 403 Forbidden | 403 Forbidden | Pass |
| **Project Manager** | Has `view_reports` | `GET /api/v1/projects/:id/daily-reports/contract/` | 200 OK | 200 OK | Pass |
| **Project Manager** | Has `view_reports` | `GET /api/v1/projects/:id/daily-reports/:pk/contract-summary/` | 200 OK | 200 OK | Pass |
| **Administrator** | Superuser / Admin group | `GET /api/v1/projects/:id/daily-reports/contract/` | 200 OK | 200 OK | Pass |
| **Administrator** | Write attempt on immutable contract | `POST /api/v1/projects/:id/daily-reports/contract/` | 403 Forbidden / 405 Method Not Allowed | Enforced read-only | Pass |

---

## 4. Verification Evidence & Execution Logs

- **Contract Loading & Validation**: Executed `validate_daily_report_contract()` via Django manage shell:
  - Contract version: `1.0.0`
  - Reference form version: `shiraz-file4-v1`
  - Sections mapped: 18 broader daily sections
  - Field mappings: 128 field mapping entries
  - Scope decisions: 11 ratified/baseline decisions
- **Reference Fixture Seeding**: Executed `python manage.py seed_a1_reference_fixture`:
  - Successfully verified existing synthetic project `[SYNTHETIC A.1 REFERENCE] کارگاه آزمایشی شیراز SIM-A1-001`
  - Daily report loaded with report date `2027-05-22` (Jalali `1406-03-01`)
  - Re-seeding executed idempotently without error.
- **Automated Verification Suites**:
  - `field_reports/tests/test_a1_b01_data_contract.py`: Migration preservation and contract coverage tests (`test_published_contract_covers_reference_form_fields_and_governance`, `test_b01_migrations_preserve_legacy_and_enforce_uniqueness`) passed (exit code 0).

---

## 5. Downstream Handoff Status
- Requirement `B01` has zero open defects and is verified complete.
- Ready for subsequent workflow dependencies (`B02` version integrity and derived locks).
