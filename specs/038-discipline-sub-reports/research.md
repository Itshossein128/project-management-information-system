# Research: Discipline Sub-Reports Lifecycle and Validation

## Context & Objectives

Feature 038 establishes rigorous lifecycle controls, domain validation, and discipline-specific extensions for specialized unit daily sub-reports (Civil/Structural, Finishing, Electrical, Mechanical, Plumbing, HVAC) in alignment with engineering reporting blueprints (Shiraz FILE 5 / FILE 6) and canonical architecture.

Gaps addressed from atomic specifications:
- **G01 & G02**: Lack of execution percentage (`execution_percentage`) and missing range validation `[0.00, 100.00]`.
- **G03**: Submitting empty sub-reports without active work rows, corrupting rollup summaries.
- **G04**: Civil/concrete clutter in electrical reports; need for discipline-specific UI layouts and unit pickers.
- **G05**: Warehouse-only restriction for materials, preventing mechanical/plumbing trades from documenting consumables.
- **G06**: Disconnected hydrostatic pressure test records without linkage to Quality Inspection (`risk.Inspection`).
- **G07**: Missing contractor person-hours computation and ledger rollup from activity crew allocations.
- **G08**: Architectural taxonomy bridge for sub-disciplines (`PLUMBING`, `HVAC`, `CIVIL`, `FINISHING`) under canonical units.

---

## Technical Decisions & Alternatives Considered

### Decision 1: Activity Row Execution Percentage Representation & Validation

- **Decision**: Add `execution_percentage` (`models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)`) to `DisciplineSubReportActivity` and serializers. Enforce range `0.00 <= execution_percentage <= 100.00` in both serializer validation and model validation. Reject violations with stable machine-readable code `percent_must_be_between_0_and_100` and localized Persian/English error messages ("درصد پیشرفت باید بین ۰ تا ۱۰۰ باشد" / "Execution percentage must be between 0.00 and 100.00").
- **Rationale**: Progress velocity must be explicitly bounded to the closed interval [0, 100]. Null represents unmeasured/not-applicable progress and must not be coerced to 0.00.
- **Alternatives Considered**:
  - *Integer percentage (0-100)*: Rejected because Shiraz FILE 5 / FILE 6 engineering standards track fractional progress (e.g. 15.50%).
  - *Coercing null to 0.00%*: Rejected because unset progress differs conceptually from zero progress achieved on an ongoing task.

### Decision 2: Prevention of Empty Sub-Report Submissions

- **Decision**: In `submit_unit_report` (and `submit_sub_report`), before updating status to `SUBMITTED`, compute the total active (non-deleted) row count across operational sections:
  `activities`, `labor_entries`, `material_entries`, `concrete_entries`, `machinery_rows`, and `general_activities`.
  If the sum of active rows is zero, reject submission immediately with `UnitReportError` carrying code `cannot_submit_empty_sub_report` and HTTP status 400.
- **Rationale**: Hollow submissions corrupt project rollup statistics, create meaningless audit events, and violate data integrity principles.
- **Alternatives Considered**:
  - *Allow submitting empty reports with warning*: Rejected; strict site compliance requires at least one operational row (activity, labor headcount, or materials) before a daily report can be certified.
  - *Checking only activity rows*: Rejected because a discipline might report labor attendance or material arrivals on weather-impacted days without physical activity output.

### Decision 3: Electrical Sub-Report Customization & Civil Field Separation

- **Decision**: In the frontend (`unit-daily-report-panel.tsx` and section components), ensure civil widgets (concrete pour sampling, slump test, mix design, batching plant) are strictly hidden when `unit === 'electrical'`. Introduce standard electrical units of measurement in quick selectors:
  - Linear meters (`متر طول` / `m`)
  - Outlets / points (`شعله / نقطه` / `point`)
  - Panels / enclosures (`دستگاه تابلو` / `panel`)
  - Branch / lengths (`شاخه` / `branch`)
- **Rationale**: Conforms to Shiraz FILE 6 electrical reporting standards and eliminates visual noise and erroneous civil data entry.
- **Alternatives Considered**:
  - *Hardcoding distinct pages for every discipline*: Rejected; keeping the canonical `UnitDailyReportPanel` with conditional section visibility maintains the unified architecture (Constitution Principle V).

### Decision 4: Mechanical & Plumbing Consumables Enablement

- **Decision**: Update `MATERIALS_ENABLED_UNITS` in `apps/web/src/app/lib/api/unit-reports.ts` to include `"mechanical"`. The backend already supports `UnitReportMaterialSectionViewSet` for any canonical unit. Provide a quick-pick palette in `SectionMaterials` when `unit === 'mechanical'` for top high-frequency items:
  1. لوله ۵ لایه (5-layer composite pipe)
  2. لوله پلیکا / فاضلابی (PVC pipe)
  3. اتصالات جوشی (Welding fittings)
  4. عایق الاستومری حرارتی و برودتی (Elastomeric insulation)
  5. لوله گالوانیزه (Galvanized pipe)
- **Rationale**: Mechanical installations install and consume large volumes of piping and fittings daily that must be tracked at the unit report level without forcing supervisors into the central warehouse inventory module.
- **Alternatives Considered**:
  - *Requiring warehouse staff to log all plumbing materials*: Rejected; field velocity requires immediate reporting by the installation supervisor on-site.

### Decision 5: Hydrostatic & Pressure Testing Integration with Quality Control

- **Decision**: Add hydrostatic testing fields to `DisciplineSubReportActivity`:
  - `is_hydrostatic_tested` (BooleanField, default=False)
  - `test_pressure_bar` (DecimalField, max_digits=6, decimal_places=2, null=True, blank=True)
  - `test_duration_minutes` (PositiveIntegerField, null=True, blank=True)
  - `test_outcome` (CharField, max_length=10, choices=[('PASSED', 'Passed'), ('FAILED', 'Failed')], null=True, blank=True)
  - `tested_segment` (CharField, max_length=120, blank=True, default='')
  - `qc_inspection` (ForeignKey to `risk.Inspection`, on_delete=SET_NULL, null=True, blank=True, related_name='tested_activities')
  Validation: If `is_hydrostatic_tested=True`, `test_pressure_bar` must be provided and > 0; otherwise raise `invalid_test_pressure_value`.
  On submission (`submit_unit_report`), invoke a linkage service `link_hydrostatic_tests(report, user)` that automatically creates or links a `risk.Inspection` record with stage `RESULT`, test metadata, and report date for all `PASSED` hydrostatic tests.
- **Rationale**: Adheres to plumbing codes where pressurized lines require auditable inspection records before walls/shafts are closed. Reuses the existing `risk.Inspection` entity without duplicating QC schema.
- **Alternatives Considered**:
  - *Creating a standalone PressureTest model*: Rejected; plumbing tests are performed as part of piping activity execution, and inspections belong in `risk.Inspection`.

### Decision 6: Subcontractor Crew Labor Hours Rollup & Ledger

- **Decision**: Compute contractor person-hours as `(foreman_count + worker_count) * shift_duration_hours` (defaulting shift hours to 8 when unspecified). Introduce `SubcontractorLaborLedgerEntry` in `apps/api/core/sub_reports/models.py`. Upon sub-report approval (`approve_unit_report`), generate or update ledger entries for each activity with an associated `contractor_ref`.
- **Rationale**: Provides tamper-evident labor records tied directly to approved daily reports for subcontractor invoice verification (Interim Payment Certificates).
- **Alternatives Considered**:
  - *Dynamic on-the-fly aggregation without a persisted ledger*: Rejected; historical billing records require an immutable snapshot of approved contractor hours that cannot shift if activity rows are later corrected in new versions.

### Decision 7: Taxonomy Bridge: Sub-Discipline Tags within Canonical Units

- **Decision**: Add `sub_discipline` field to `DisciplineSubReport`:
  - Under `mechanical`: `MECHANICAL`, `PLUMBING`, `HVAC`
  - Under `buildings`: `CIVIL`, `FINISHING`
  Provide a sub-discipline dropdown in the report header/metadata. Ensure both navigation routes (Project Overview Daily Reports & Specialty Units sidebar) route to the canonical unit workspace.
- **Rationale**: Resolves the tension between the 6 canonical architectural units and granular trade disciplines without creating separate database tables or orphaned routes.
- **Alternatives Considered**:
  - *Creating separate canonical units for plumbing and HVAC*: Rejected; violates Constitution Principle V and the 6 canonical unit boundary established in Feature 032.
