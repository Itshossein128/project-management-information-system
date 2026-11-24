# Phase 0 Research: Phase A.1 Daily Report Data Contract & Reference-Day Fixture (B01)

**Feature**: `057-a1-b01-data-contract` | **Date**: 2026-11-19 | **Spec**: [spec.md](./spec.md)

## Research Objectives

Resolve all technical design choices needed to implement the versioned Phase A.1 Daily Report Data Contract, core contract services/schema alignment, and the clearly labeled synthetic reference-day fixture (`SIM-A1-001`, Solar Hijri `1406-03-01`, project day 12) while respecting Building Management Constitution v1.1.0 and strict B01 vs. B02–B06 package boundaries.

---

## R-01: Versioned Data Contract Storage & Runtime Accessibility

- **Decision**: Publish the authoritative versioned contract as a structured, machine-readable JSON artifact inside `apps/api/core/field_reports/contracts/daily_report_contract_v1.json` (mirrored as the design specification in `specs/057-a1-b01-data-contract/contracts/daily-report-data-contract.v1.json`), loaded via a pure-Python contract loader/validator service (`apps/api/core/field_reports/services/data_contract.py`) and exposed through a read-only DRF endpoint (`GET /api/v1/projects/<project_id>/daily-reports/contract/`) guarded by server-enforced project membership and read permission (Constitution Principle I).
- **Rationale**: Storing the contract as a versioned, git-tracked JSON artifact inside `field_reports/contracts/` guarantees deterministic revision history, zero-cost schema validation in pytest, direct consumption by downstream B02–B05 services (aggregators, exporters, reconciliation checks), and non-technical stakeholder reviewability without introducing an unnecessary database CRUD subsystem for static governance rules (Constitution Principle V).
- **Alternatives Considered**:
  - *Database-stored contract rows*: Rejected for B01 because governance decisions (`C01`–`C10`, `GOV-01`) and reference-form mappings are code-reviewed specification artifacts; putting them in mutable DB tables risks drift from git history and complicates deterministic B05 reconciliation.
  - *Markdown-only contract in `docs/`*: Rejected because `DEF-B01-01-GAP-02` explicitly requires an executable, reviewable versioned contract artifact that automated tests and runtime services can validate against.

---

## R-02: Canonical Shift Model, Logical Report Uniqueness & Migration Strategy (`C03`, `FR-011`, `FR-012`)

- **Decision**:
  1. Introduce a dedicated, additive `DailyReportWorkedShift` table (`daily_report_worked_shifts`, keyed by `(report, shift_id)` where `shift_id ∈ {1, 2, 3}` enforced by `CheckConstraint` and `UniqueConstraint`) and a canonical shift validator (`normalize_canonical_shift_id`) accepting only canonical identifiers `1`, `2`, `3` (rejecting invalid codes without silent remapping).
  2. Reconcile the `C03` invariant ("one logical daily report per `(project, local report_date)`") with the existing `unique_current_daily_report_per_date_shift` constraint via a **two-layer non-destructive PostgreSQL partial-uniqueness migration (`0026_daily_report_b01_contract.py`)**:
     - **Retain** `DailyReport.shift` (`day`/`night`/`full`) and `unique_current_daily_report_per_date_shift` (`fields=['project', 'report_date', 'shift']`, `condition=Q(is_deleted=False, is_current=True)`) for untouched legacy pre-B01 rows (`contract_version=''`), because existing tests (`test_models.py`, `test_shiraz_file1_excel.py`) and historical databases may hold separate legacy `day` and `night` rows on the same `(project, report_date)`.
     - **Add** the final B01 partial uniqueness constraint `unique_current_contract_daily_report_per_date` on `fields=['project', 'report_date']` with `condition=Q(is_deleted=False, is_current=True) & ~Q(contract_version='')`. Any current, non-deleted contract-bound report (`contract_version != ''`, including `SIM-A1-001` and all Phase A.1 derived summaries) is strictly unique per `(project, report_date)` at the PostgreSQL level regardless of legacy `shift`.
     - **Legacy row behavior**: Pre-B01 rows remain readable and are NEVER silently merged, dropped, or auto-promoted to `contract_version='1.0.0'` during migration. Contract-bound paths always write `contract_version='1.0.0'` + `shift=ReportShift.FULL` (legacy compatibility shim) and store worked shifts exclusively in `DailyReportWorkedShift`. Full retirement of `unique_current_daily_report_per_date_shift` is deferred until legacy historical migration (`X08` in `A.8`/`A.12`).
     - **Rollback awareness**: `0026_daily_report_b01_contract.py` is purely schema-additive and fully reversible (`migrate field_reports 0025` drops only the new constraint, table, and defaulted columns without mutating pre-existing rows).
  3. Add an actual-duration person-hours calculator (`compute_actual_person_hours`) in `apps/api/core/field_reports/services/man_hours.py` alongside the existing rule registry: when `actual_duration_hours` is `None` (missing), it returns `None` (`unknown`) and NEVER falls back to `standard_shift_hours` (`8.0`).
- **Rationale**: Reconciles `C03` DB-level uniqueness with Constitution Principle II (zero silent data loss on legacy multi-shift rows, explicit migration/rollback strategy) and Principle V (minimal coherent additive change without breaking existing non-B01 test suites).
- **Alternatives Considered**:
  - *Dropping `unique_current_daily_report_per_date_shift` and adding unconditional `(project, report_date)` uniqueness immediately*: Rejected because existing databases and test suites (`test_models.py`, `test_shiraz_file1_excel.py`) contain same-date `day` + `night` legacy rows; an unconditional constraint would either fail migration apply or force destructive data merging without stakeholder approval (`FR-008`).
  - *Enforcing one-report-per-date only in Python without a DB constraint*: Rejected because race conditions or direct ORM writes could create duplicate current A.1 reports; the PostgreSQL partial `UniqueConstraint` guarantees the invariant atomically.
  - *Using `standard_shift_hours` (8h) as a fallback when actual duration is missing*: Explicitly prohibited by ratified `C03` and `FR-008`/`FR-012`.

---

## R-03: Bilingual Labor Metric Taxonomy & Anti-Mislabeling Guard (`D07`, `FR-013`)

- **Decision**: Define four canonical, language-independent metric keys in the data contract and shared backend/frontend contract definitions:
  - `headcount` → EN: `Headcount (Persons)` / FA: `تعداد نفرات` (requires unique-person context when aggregated)
  - `person_shifts` → EN: `Person-Shifts` / FA: `نفر-شیفت` (sum of labor rows across shifts/activities without unique-worker deduplication)
  - `person_days` → EN: `Person-Days` / FA: `نفر-روز` (VALID ONLY when backed by unique-worker attendance deduplication proof; forbidden for raw activity row sums)
  - `person_hours` → EN: `Person-Hours` / FA: `نفر-ساعت` (computed exclusively from recorded actual shift durations; `null`/`unknown` when duration is missing)
- **Rationale**: Directly resolves `DEF-B01-03` and `DEF-B01-04-GAP-05`. Full frontend UI table/filter refactors (`project-activity-log.tsx`, `project-labor-productivity.tsx`) remain owned by `B04` (`coverage.json`), while B01 publishes the authoritative bilingual taxonomy, validation guard (`assert_valid_labor_metric_label`), and API contract consumed by B03/B04.
- **Alternatives Considered**:
  - *Hardcoding Persian-only strings in exporters*: Rejected (violates Constitution Principle III and `FR-013`).

---

## R-04: Configurable Project Catalog vs. Selectable Shiraz 34/32 Profile & Appendix (`C04`, `FR-014`, `FR-015`)

- **Decision**:
  1. Preserve `project_templates.LaborTitleCatalog` and immutable activation snapshots (`ProjectReportingConfigurationLaborTitle`) as the authoritative, versioned project job-title catalog.
  2. Introduce a contract-driven **Form Presentation Profile** abstraction (`FormPresentationProfile`, starting with `shiraz-34-32-v1`) in `apps/api/core/field_reports/services/form_profiles.py` backed by the versioned JSON contract.
  3. Implement a deterministic mapper `resolve_labor_rows_for_profile(labor_rows, profile_code)` that:
     - Maps matching project catalog titles into the fixed 34 indirect / 32 direct slots of `shiraz-34-32-v1` without mutating the project catalog or historical records.
     - Routes ALL additional, custom, or historical titles outside the fixed 34/32 slots into dedicated `appendix_indirect` and `appendix_direct` collections (never concatenated onto the fixed 34/32 arrays, never dropped, never relabeled).
- **Rationale**: Directly resolves `DEF-B01-04` and `DEF-B01-05-GAP-03` while honoring `C04` and Constitution Principle V (extending existing `LaborTitleCatalog` rather than replacing it). Downstream cell-by-cell Excel/PDF rendering of the profile and appendix is cleanly handed off to `B03`.
- **Alternatives Considered**:
  - *Storing 34/32 slots as mandatory rows in every project's `LaborTitleCatalog`*: Rejected because it violates `C04` (conflating form layout with project catalog truth).

---

## R-05: Official Report Numbering, Project Day & Solar Hijri Formatting (`H05`, `C08`, `FR-017`)

- **Decision**:
  1. Reuse `apps/api/core/common/jalali.py` (`jdatetime`) to format the project-local Solar Hijri date with hyphen-separated zero-padded two-digit month and day (`%Y-%m-%d`, e.g., `1406-03-01`).
  2. Compute `project_day = (report_date - actual_start_date).days + 1` where `actual_start_date` comes from `Project.start_date` (or explicit `actual_start_date` if set).
  3. Format official report number strictly as `<project_code>-<project_day>-<YYYY>-<MM>-<DD>` (e.g., `SIM-A1-001-12-1406-03-01`), independent of database UUIDs.
  4. If `actual_start_date` is `None` or `report_date < actual_start_date`, return `project_day=None`, `official_report_number=None`, and explicit status `"unknown"` with a bilingual reason—NEVER fabricating day `0`, negative days, or synthetic IDs.
- **Rationale**: Verified via `jdatetime`: Solar Hijri `1406-03-01` = Gregorian `2027-05-22` (Saturday / `شنبه`); `1406-02-21` = Gregorian `2027-05-11`; `(2027-05-22 - 2027-05-11).days + 1 = 12`. Satisfies `C08` and `FR-017(a)` deterministically.
- **Alternatives Considered**:
  - *Sequential auto-increment integer per report*: Rejected by `C08` (report number must be deterministic from `<projectID>-<projectDay>-<SolarHijriDate>`).

---

## R-06: Observed Weather Logs & MET Norway Locationforecast 2.0 Contract (`X07`, `C08`, `FR-017`)

- **Decision**:
  1. Source observed weather condition, temperature min/max, `wind_speed`, and `soil_condition` (ground condition) from existing `field_reports.WeatherLog` for `(project, report_date)`, returning `"unknown"` (`None`) for any missing field.
  2. Add nullable `latitude` and `longitude` (`DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)`) on `Project` (additive migration) so project geographic coordinates can be stored cleanly without breaking existing projects.
  3. Implement a contract-compliant MET Norway Locationforecast 2.0 adapter (`apps/api/core/field_reports/services/weather_forecast.py`) targeting `https://api.met.no/weatherapi/locationforecast/2.0/compact` with a compliant `User-Agent` header, short timeout, and Redis cache. When coordinates are missing, offline, timed out, or HTTP error occurs, return structured `status: "unknown"` for all 3 forecast days—NEVER fabricating weather data.
- **Rationale**: `WeatherLog` already stores `wind_speed` and `soil_condition` (`apps/api/core/field_reports/models.py:768-790`), and Stage 1 verified outbound reachability to MET Norway (`HTTP 200`). Adding nullable coordinates and an explicit graceful-degradation adapter satisfies `C08` and `FR-008` in both online and air-gapped/CI environments.
- **Alternatives Considered**:
  - *Geocoding free-text `Project.location` at export time*: Rejected because free-text geocoding is non-deterministic and risks wrong coordinates; explicit nullable lat/lon with `"unknown"` fallback is auditable and safe.

---

## R-07: Synthetic Reference-Day Fixture (`SIM-A1-001`) & Idempotent Seeder (`GOV-01`, `FR-001`, `FR-002`)

- **Decision**:
  1. Create a clearly labeled synthetic fixture file `apps/api/core/field_reports/fixtures/sim_a1_001_1406_03_01.json` containing:
     - Project `SIM-A1-001` (`is_synthetic_reference_fixture: true`, `actual_start_date: 2027-05-11` / `1406-02-21`, coordinates for Shiraz reference site `29.5918, 52.5837`).
     - Report date `2027-05-22` / Solar Hijri `1406-03-01`, project day `12`, official report number `SIM-A1-001-12-1406-03-01`.
     - Worked shifts `1` (actual duration `8.5` hours) and `3` (actual duration `null` → unknown person-hours); Shift `2` unworked and omitted from header (`C03`).
     - Activity rows covering measured `0`, `0.00`, positive `12.50`, unset (`null`), and `quantity_measured=False` (`not-measured`) (`C02`).
     - Labor rows covering standard Shiraz 34/32 titles PLUS custom/extra/historical titles that route to the Appendix (`C04`).
     - `WeatherLog` for `2027-05-22` with observed condition, temperatures, `wind_speed`, and `soil_condition` (`C08`).
  2. Provide an idempotent Django management command `seed_a1_reference_fixture` (`apps/api/core/field_reports/management/commands/seed_a1_reference_fixture.py`) that imports or updates `SIM-A1-001` deterministically without altering non-synthetic projects.
  3. Explicitly exclude unlabeled legacy synthetic audit samples (`GOV-01`, `FR-002`).
- **Rationale**: Satisfies `GOV-01`, `FR-001`, `FR-002`, and `SC-005`/`SC-006`, giving downstream packages B02–B06 one shared, deterministic, unmistakably labeled reference dataset.
- **Alternatives Considered**:
  - *Hardcoding fixture data inside test files only*: Rejected because `FR-002` and `DEF-B01-01-GAP-01` require an importable reference-day fixture for both internal verification and B06 employer review.

---

## R-08: Zero / Unset / Not-Measured Regression Preservation (`C02`, `FR-009`, `FR-010`)

- **Decision**: Preserve the Stage 1 QA-passed `coerce_optional_decimal` and `UnsetQuantityBadge` / `quantity_measured` semantics as explicit contract rules in `daily_report_contract_v1.json` and lock them with regression tests in B01's pytest suite, including mixed-aggregate verification (`0.00` + `12.50` + `null`/`not-measured` → sum `12.50` with unrecorded count `1`) and positive-only domain-invalid checks (e.g., pressure/concrete tests rejecting `<= 0`).
- **Rationale**: Carries forward the verified `B01-03` pass as automated regression evidence while formally superseding `033` `FR-002`/`SC-004` text in the versioned contract.

---

## Summary of Resolved Unknowns

All technical choices for B01 are resolved with zero remaining `NEEDS CLARIFICATION` items. Downstream deliverables (`B02` versioning, `B03` Excel/PDF rendering parity, `B04` UI filters/totals, `B05` independent reconciliation proof, `B06` employer final acceptance sign-off) remain cleanly scoped to their recorded owners.
