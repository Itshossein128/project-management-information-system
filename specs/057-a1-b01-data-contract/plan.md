# Implementation Plan: Phase A.1 Daily Report Data Contract & Reference-Day Fixture (B01)

**Branch**: `057-a1-b01-data-contract` | **Date**: 2026-11-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/057-a1-b01-data-contract/spec.md`

## Summary

Publish the versioned Phase A.1 Daily Report Data Contract (`v1.0.0`), implement its core backend contract services and additive schema extensions (canonical worked shifts `1`–`3` with actual working durations and unknown-when-missing person-hours, bilingual labor metric taxonomy with anti-mislabeling guard, selectable `shiraz-34-32-v1` form presentation profile with dedicated Appendix partitioning, deterministic Solar Hijri official report & project-day numbering, observed `WeatherLog` wind/ground and MET Norway Locationforecast 2.0 graceful-degradation adapter), expose read-only contract endpoints under server-enforced authorization, and deliver the clearly labeled, idempotently importable synthetic reference-day fixture `SIM-A1-001` (`1406-03-01` Solar Hijri / `2027-05-22` Gregorian, project day `12`, official report `SIM-A1-001-12-1406-03-01`) with a comprehensive pytest verification suite. Downstream packages `B02`–`B06` (versioning, full Excel/PDF parity, frontend filter/totals UI, independent reconciliation proof, and employer acceptance sign-off) remain cleanly outside B01 scope.

## Technical Context

**Language/Version**: Python 3.11+ (backend, Django 4.2.11 pinned in `apps/api/.venv`); TypeScript 5 / React Router 7 (frontend contract types only if needed; primary B01 runtime is backend + shared contract JSON)

**Primary Dependencies**: Django 4.2.11, Django REST Framework, `jdatetime` (Solar Hijri conversion in `common/jalali.py`), PostgreSQL 16 (port 5433), Redis (port 6379), standard-library `urllib` / `requests` for MET Norway Locationforecast 2.0

**Storage**: PostgreSQL 16 (`projects`, `daily_reports`, `daily_report_worked_shifts`, `weather_logs`, `project_reporting_configurations`) + git-tracked JSON contract & fixture artifacts under `apps/api/core/field_reports/`

**Testing**: `pytest` + `pytest-django` via `apps/api/.venv/bin/python -m pytest` (never `manage.py test`; preserve pinned `Django==4.2.11`)

**Target Platform**: Linux server (Velora monorepo `apps/api` + `apps/web`)

**Project Type**: Web application (pnpm monorepo: Django DRF backend + React Router 7 frontend)

**Performance Goals**: Contract JSON load & validation `< 20ms` in-memory; official numbering & profile resolution `< 10ms` per report; MET Norway forecast cached in Redis with short timeout (`<= 3s`) and immediate `"unknown"` degradation when offline/unavailable

**Constraints**:
- Strict anti-fabrication (`FR-008`, `C02`, `C03`, `C08`): never default missing shift duration to `8` hours, never coerce `null`/`not-measured` to `0`, never fabricate report numbers or weather forecasts.
- Strict B01 scope boundary: do NOT start `B02`–`B06`; employer acceptance representative and date remain `null` / pending `B06` handoff (`GOV-01`).
- Non-destructive additive migrations only (Constitution Principle II).
- Pinned `Django==4.2.11` boundary (do NOT install `django-debug-toolbar`).

**Scale/Scope**: Single Phase A.1 foundation package (`B01`), 6 requirements (`B01-01`..`B01-06`), 19 FRs (`FR-001`..`FR-019`), 6 SCs (`SC-001`..`SC-006`), 18 broader daily report sections, 1 synthetic reference fixture (`SIM-A1-001`).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Phase 0 Gate | Post-Phase 1 Design Verification |
| :--- | :--- | :--- |
| **I. Server-Enforced Authorization & Tenant/Project Isolation** | PASS — Read-only contract endpoints must require authenticated active project membership + `view_reports` (or bounded org-admin read-only exception). | PASS — Specified in `contracts/api-contract.md` §1 and verified by 401/403 tests in `quickstart.md` §3. |
| **II. Data Integrity & End-to-End Domain Consistency** | PASS — Additive schema changes (`Project.latitude/longitude`, `DailyReportWorkedShift`, `DailyReport` contract flags) preserve all existing data and migrations. | PASS — `data-model.md` §2.4 defines the exact two-layer partial uniqueness migration (`unique_current_contract_daily_report_per_date` alongside legacy `unique_current_daily_report_per_date_shift`), zero-data-loss legacy behavior, reversible rollback, and migration apply/preservation/rollback verification tests. |
| **III. Bilingual & Locale-Correct Experience** | PASS — Persian & English labels required for labor metrics, appendix headings, unknown indicators; Solar Hijri formatting via `jdatetime`. | PASS — `daily-report-data-contract.v1.json` and `data-model.md` §3.3 enforce language-independent keys with bilingual EN/FA labels and verified Solar Hijri `1406-03-01` formatting. |
| **IV. Explicit, Safe Business Mutations** | PASS — Synthetic seeder must be idempotent and scoped strictly to `SIM-A1-001`; no destructive mutations on real projects. | PASS — `seed_a1_reference_fixture` safety invariants codified in `contracts/api-contract.md` §3 and `quickstart.md` §2. |
| **V. Minimal Coherent Changes** | PASS — Extend existing `field_reports`, `projects`, and `project_templates` models/services rather than creating parallel apps. | PASS — Reuses `WeatherLog`, `ProjectReportingConfigurationLaborTitle`, `common/jalali.py`, and `field_reports/services/man_hours.py`. |
| **VI. Evidence-Based Verification** | PASS — Separate B01 internal pytest/migration verification from B06 employer acceptance; state environment limits explicitly. | PASS — `quickstart.md` §4 and `GOV-01` distinguish internal verification from B06 employer sign-off. |
| **VII. Accessible, Practical Construction-Management UX** | PASS — Contract eliminates ambiguous `"نفر-روز"` mislabeling and static shift-hour placeholders for downstream UI/export consumers. | PASS — Bilingual metric guard and unknown-duration contract ready for B03/B04 consumption. |

## Project Structure

### Documentation (this feature)

```text
specs/057-a1-b01-data-contract/
├── spec.md                                           # Clarified & Supervisor-approved specification
├── checklists/
│   └── requirements.md                               # 16/16 passing quality checklist
├── plan.md                                           # This file (/speckit-plan output)
├── research.md                                       # Phase 0 research decisions (R-01..R-08)
├── data-model.md                                     # Phase 1 entities, additive schema & invariants
├── quickstart.md                                     # Phase 1 runnable validation guide
├── contracts/
│   ├── daily-report-data-contract.v1.json            # Versioned machine-readable A.1 data contract
│   └── api-contract.md                               # Read-only DRF API, Python service & CLI contracts
└── tasks.md                                          # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
apps/api/core/
├── projects/
│   ├── models.py                                     # Additive: Project.latitude, Project.longitude
│   └── migrations/
│       └── 0022_project_coordinates.py               # Additive migration (depends on 0021_project_measurement_unit)
└── field_reports/
    ├── contracts/
    │   └── daily_report_contract_v1.json             # Published runtime versioned data contract (v1.0.0)
    ├── fixtures/
    │   └── sim_a1_001_1406_03_01.json                # Clearly labeled synthetic SIM-A1-001 reference fixture
    ├── management/
    │   └── commands/
    │       └── seed_a1_reference_fixture.py          # Idempotent SIM-A1-001 seeder CLI
    ├── migrations/
    │   └── 0026_daily_report_b01_contract.py         # Additive: DailyReportWorkedShift + DailyReport flags (depends on 0025_material_unknown_type)
    ├── models.py                                     # Additive: DailyReportWorkedShift + contract metadata
    ├── services/
    │   ├── data_contract.py                          # Contract loader, official numbering, canonical shifts, metric guard
    │   ├── form_profiles.py                          # Selectable shiraz-34-32-v1 profile + dedicated Appendix mapper
    │   ├── man_hours.py                              # Additive: compute_actual_person_hours (None when duration missing)
    │   └── weather_forecast.py                       # MET Norway Locationforecast 2.0 adapter with unknown fallback
    ├── daily_report_views.py                         # Read-only contract & contract-summary actions (Principle I auth)
    ├── urls.py                                       # Wire read-only contract endpoints
    └── tests/
        └── test_a1_b01_data_contract.py              # Comprehensive B01 pytest suite (SC-001..SC-006 + B01-03 regression)
```

**Structure Decision**: Use Velora's established Django 4.2 backend (`apps/api/core/field_reports/` and `apps/api/core/projects/`) for all B01 contract artifacts, additive models, services, fixture seeding, and read-only endpoints. No new apps or parallel frontend refactors are introduced in B01; `B03` (Excel/PDF rendering parity) and `B04` (frontend filter/totals UI) consume these contracts in subsequent packages.

## Migration, Uniqueness & Legacy Compatibility Strategy

To enforce ratified `C03` / `FR-011` ("one logical daily report per `(project, local report_date)`") without breaking existing pre-B01 rows or legacy test suites (`test_models.py`, `test_shiraz_file1_excel.py`) that hold separate `day`/`night` rows on the same date:

1. **Additive Migrations (`field_reports/migrations/0026_daily_report_b01_contract.py` & `projects/migrations/0022_project_coordinates.py`)**:
   - `projects/migrations/0022_project_coordinates.py` (depends on `('projects', '0021_project_measurement_unit')`): adds nullable `Project.latitude` and `Project.longitude` (forward to `0022`, reversible to `0021`).
   - `field_reports/migrations/0026_daily_report_b01_contract.py` (depends on `('field_reports', '0025_material_unknown_type')`): adds `DailyReport.contract_version` (`default=''`), `DailyReport.is_synthetic_reference` (`default=False`), `DailyReport.presentation_profile_code` (`default=''`), and child table `DailyReportWorkedShift(report, shift_id ∈ {1,2,3}, actual_duration_hours nullable)` with `unique_worked_shift_per_report` and `daily_report_worked_shift_id_valid` (forward to `0026`, reversible to `0025`).
2. **Final Uniqueness Enforcement (`C03`)**:
   - Adds PostgreSQL partial `UniqueConstraint` `unique_current_contract_daily_report_per_date` on `fields=['project', 'report_date']` with `condition=Q(is_deleted=False, is_current=True) & ~Q(contract_version='')`.
   - Retains the existing `unique_current_daily_report_per_date_shift` on all current, non-deleted rows. The additional constraint applies to contract-bound rows and preserves legacy same-date day/night reports.
   - Guarantees at the database level that at most **one** current, non-deleted contract-bound daily report (`contract_version != ''`) can exist per `(project, report_date)` regardless of `shift`, while preserving `is_current=False` / `is_deleted=True` revision rows for `B02`.
3. **Legacy Report Behavior**:
   - Existing pre-B01 rows stay readable with `contract_version=''`; migration `0026` performs zero destructive merges, deletions, or silent promotions (`FR-008`).
   - All B01 contract-bound writes (`seed_a1_reference_fixture` and A.1 contract services) set `contract_version='1.0.0'`, `shift=ReportShift.FULL` (legacy compatibility shim), and record worked shifts exclusively in `DailyReportWorkedShift`.
   - Full retirement of `unique_current_daily_report_per_date_shift` is explicitly deferred until historical data migration (`X08`, Phases `A.8`/`A.12`).
4. **Migration Verification & Rollback Awareness (Constitution Quality Gate)**:
   - Automated tests in `test_a1_b01_data_contract.py` and `quickstart.md` verify: (a) clean forward migration apply (`projects 0022` and `field_reports 0026`), (b) preservation of pre-existing legacy same-date `day` + `night` rows (`contract_version=''`), (c) DB-level `IntegrityError` when inserting two current contract-bound reports (`contract_version='1.0.0'`) on the same `(project, report_date)` even with differing `shift` values, and (d) verified reversible rollback for both apps (`migrate projects 0021` → `migrate projects 0022` and `migrate field_reports 0025` → `migrate field_reports 0026`) with zero loss of legacy data.

## Complexity Tracking

No Constitution violations exist. All design choices extend existing Velora models and services minimally and non-destructively.
