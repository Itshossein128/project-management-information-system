# Data Model: Phase A.1 Daily Report Data Contract & Reference-Day Fixture (B01)

**Feature**: `057-a1-b01-data-contract` | **Date**: 2026-11-19 | **Spec**: [spec.md](./spec.md)

This document defines the domain entities, additive Django model extensions, contract structures, validation rules, and state invariants owned by **B01**. Existing working models (`DailyReport`, `DailyReportActivity`, `DailyReportLabor`, `WeatherLog`, `Project`, `LaborTitleCatalog`, `ProjectReportingConfiguration`) are extended minimally and non-destructively (Constitution Principles II & V).

---

## 1. Versioned Contract & Governance Entities (Immutable Artifact Schema)

Stored in `apps/api/core/field_reports/contracts/daily_report_contract_v1.json` (mirrored in `specs/057-a1-b01-data-contract/contracts/daily-report-data-contract.v1.json`) and loaded by `field_reports.services.data_contract`.

### 1.1 `DailyReportDataContract`
| Field | Type | Constraints / Rules |
| :--- | :--- | :--- |
| `contract_version` | `string` (semver) | Required; `"1.0.0"` for B01 baseline |
| `reference_form_version` | `string` | Required; `"shiraz-file4-v1"` |
| `reference_day_fixture` | `ReferenceDayMetadata` | Project `SIM-A1-001`, Solar Hijri `1406-03-01` (Gregorian `2027-05-22`), project day `12`, official report `SIM-A1-001-12-1406-03-01`, `is_synthetic: true` |
| `governance` | `GovernanceMetadata` | Internal decision & verification owner (`AI workflow agent`, `2026-11-19`); employer final acceptance handoff placeholders (`employer_acceptance_representative: null`, `employer_acceptance_date: null`, `acceptance_owner_package: "B06"`) |
| `revision_history` | `list[RevisionEntry]` | Chronological list of `{version, date, author, summary}` |
| `scope_decisions` | `list[ScopeDecisionEntry]` | Complete register for `C01`–`C10` + `GOV-01` |
| `broader_sections` | `list[SectionDisposition]` | Exact 18 entries covering `broader-daily-sections.md` |
| `field_mappings` | `list[FieldMappingEntry]` | Independent mapping for every required reference-form and A.1 contract field |
| `labor_metrics` | `list[LaborMetricDefinition]` | Canonical bilingual definitions for `headcount`, `person_shifts`, `person_days`, `person_hours` |
| `form_profiles` | `dict[str, FormPresentationProfile]` | Includes selectable `shiraz-34-32-v1` (34 indirect + 32 direct slots + appendix rules) |
| `deliverables_scope` | `list[DeliverableDefinition]` | 4 mandatory A.1 deliverables (`C05`, `C07`) + `C06` attribution/fingerprint boundary |
| `cross_phase_boundaries` | `list[CrossPhaseBoundary]` | Explicit dispositions for `X01`–`X06`, `X08`–`X10` (`FR-019`) |

### 1.2 `FieldMappingEntry`
| Field | Type | Required | Description |
| :--- | :--- | :---: | :--- |
| `field_id` | `string` | Yes | Stable dot-notation identifier (e.g., `header.official_report_number`) |
| `section_number` | `integer` (`1..18`) | Yes | Links to `broader_sections` |
| `label_en` / `label_fa` | `string` | Yes | Bilingual stakeholder labels |
| `source_document` | `string` | Yes | Authoritative source model/document (e.g., `field_reports.WeatherLog`) |
| `source_field_or_cell` | `string` | Yes | Model field or reference-form cell (e.g., `soil_condition`, `G4`) |
| `unit` | `string \| null` | Yes | Measurement unit (`hours`, `°C`, `persons`, `m3`, or `null` for text/IDs) |
| `conversion_rule` | `string` | Yes | Exact derivation or conversion formula (e.g., `(report_date - actual_start_date).days + 1`) |
| `zero_unset_rule` | `enum` | Yes | `measured_zero_valid_null_unknown` \| `positive_only_domain_rule` \| `unknown_when_missing` \| `text_optional` |
| `print_location` | `string \| null` | Yes | Target cell/block in Shiraz reference form, or `null` if omitted |
| `omission_reason` | `string \| null` | Conditional | Required whenever `print_location` is `null` |
| `drill_down_path` | `string` | Yes | Authoritative detail view/endpoint or owner phase (`A.8`, `A.3.C`, etc.) |

### 1.3 `ScopeDecisionEntry` (`C01`–`C10` + `GOV-01`)
| Field | Type | Validation Rules |
| :--- | :--- | :--- |
| `id` | `string` | `C01`..`C10`, `GOV-01` |
| `topic` | `string` | Concise decision title |
| `status` | `enum` | `baseline_recorded` \| `ratified` \| `baseline_preserved` \| `boundary_preserved` \| `ratified_internal_scope` \| `open` |
| `observed_behavior` | `string` | Explicitly separated from ratified target rule (`FR-005`) |
| `decision_text` | `string` | Verbatim ratified rule or preserved baseline |
| `actor_or_source` | `string` | Actor ID (`385da9f5-52d9-4f26-bb09-fc125283cf94`) or prior spec reference |
| `ratified_date` | `string \| null` | ISO date (`"2026-11-19"` for `C03`–`C08` & `GOV-01`) |
| `linked_requirements` | `list[string]` | Mapped `FR-*` identifiers |

---

## 2. Additive Relational Model Extensions (Django 4.2 / PostgreSQL)

### 2.1 `projects.Project` (Additive Fields)
Extends existing `apps/api/core/projects/models.py` (`projects` table):
| Field | Django Type | Constraints | Purpose |
| :--- | :--- | :--- | :--- |
| `latitude` | `DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)` | `-90 <= lat <= 90` | Project geographic latitude for MET Norway Locationforecast 2.0 (`C08`, `FR-017(c)`) |
| `longitude` | `DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)` | `-180 <= lon <= 180` | Project geographic longitude for MET Norway Locationforecast 2.0 (`C08`, `FR-017(c)`) |

- **Existing fields reused**:
  - `Project.project_code`: Stable project ID used in `<projectID>-<projectDay>-<YYYY>-<MM>-<DD>` (e.g., `SIM-A1-001`).
  - `Project.start_date`: Actual start date (`start_date = day 1`); when `None`, project day and official report number evaluate to `unknown`.

### 2.2 `field_reports.DailyReportWorkedShift` (New Child Table)
Added to `apps/api/core/field_reports/models.py` (`daily_report_worked_shifts` table):
| Field | Django Type | Constraints | Purpose |
| :--- | :--- | :--- | :--- |
| `id` | `UUIDField` (via `UUIDModel`) | PK | Standard Velora UUID primary key |
| `report` | `ForeignKey(DailyReport, on_delete=CASCADE, related_name='worked_shifts')` | Indexed | Parent logical daily report |
| `shift_id` | `PositiveSmallIntegerField(choices=[(1,'1'),(2,'2'),(3,'3')])` | `CheckConstraint(shift_id__in=[1,2,3])` | Canonical shift ID (`1`, `2`, `3`) per `C03`, `FR-011` |
| `actual_duration_hours` | `DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)` | `null=True`; if present, `> 0` and `<= 24` | Recorded actual working duration; `null` = unknown (NEVER defaulted to `8`) |
| `created_at` / `updated_at` | `TimeStampedModel` | Auto | Audit timestamps |

- **Constraints**:
  - `UniqueConstraint(fields=['report', 'shift_id'], name='unique_worked_shift_per_report')`
  - `CheckConstraint(actual_duration_hours IS NULL OR (actual_duration_hours > 0 AND actual_duration_hours <= 24))`
  - Presence of a row means that shift **actually worked** on `(project, report_date)`. Unworked shifts MUST NOT have a row in `worked_shifts` (`C03`).

### 2.3 `field_reports.DailyReport` (Additive Contract Metadata)
Extends existing `apps/api/core/field_reports/models.py` (`daily_reports` table) non-destructively:
| Field | Django Type | Constraints | Purpose |
| :--- | :--- | :--- | :--- |
| `is_synthetic_reference` | `BooleanField(default=False)` | Default `False` | Unmistakably labels `SIM-A1-001` reference fixture records (`GOV-01`, `FR-002`) |
| `contract_version` | `CharField(max_length=20, blank=True, default='')` | Optional | Records data contract version bound to report (e.g., `"1.0.0"`) |
| `presentation_profile_code` | `CharField(max_length=40, blank=True, default='')` | Optional | Optional selectable form profile (e.g., `"shiraz-34-32-v1"`); never overwrites project catalog (`C04`) |

- **Derived / Computed Properties (Never Fabricated)**:
  - `project_day_number -> int | None`: `(report_date - project.start_date).days + 1` if `project.start_date` exists and `report_date >= project.start_date`, else `None` (`unknown`).
  - `official_report_number -> str | None`: `f"{project.project_code}-{project_day}-{jalali_yyyy_mm_dd}"` if `project.project_code` and `project_day is not None`, else `None` (`unknown`).
  - `canonical_worked_shift_ids -> list[int]`: Sorted list of `worked_shifts.shift_id` (`[1]`, `[1, 3]`, etc.).

### 2.4 Uniqueness Constraints, Legacy Compatibility & Migration Strategy (`C03`, Principle II)

| Constraint Name | Table | Fields | Partial Condition | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `unique_current_daily_report_per_date_shift` *(existing)* | `daily_reports` | `['project', 'report_date', 'shift']` | `Q(is_deleted=False, is_current=True)` | Retained for all current, non-deleted rows to preserve legacy pre-B01 data and legacy test suites (`test_models.py`, `test_shiraz_file1_excel.py`). |
| `unique_current_contract_daily_report_per_date` *(new in `0026`)* | `daily_reports` | `['project', 'report_date']` | `Q(is_deleted=False, is_current=True) & ~Q(contract_version='')` | Enforces the ratified `C03` / `FR-011` invariant at PostgreSQL level: **at most one current, non-deleted contract-bound daily report per `(project, report_date)`**, regardless of legacy `shift`. Superseded (`is_current=False`) and soft-deleted (`is_deleted=True`) revisions remain permitted for `B02`. |
| `unique_worked_shift_per_report` *(new in `0026`)* | `daily_report_worked_shifts` | `['report', 'shift_id']` | *(unconditional)* | Prevents duplicate worked-shift entries on the same report. |
| `daily_report_worked_shift_id_valid` *(new in `0026`)* | `daily_report_worked_shifts` | `shift_id` | `CheckConstraint(shift_id__in=[1, 2, 3])` | Enforces canonical shift IDs `1`, `2`, `3` at database level. |

- **Legacy Report Behavior**:
  - Existing pre-B01 rows retain `contract_version=''` and are NOT destructively merged, deleted, or silently promoted during migration `0026`.
  - If a legacy `(project, report_date)` has multiple current rows (e.g., `day` and `night`), contract-audit helpers report an explicit legacy-conflict warning rather than fabricating a merged record (`FR-008`).
  - All B01 contract-bound writes (`seed_a1_reference_fixture` and future A.1 builders) set `contract_version='1.0.0'` and `shift=ReportShift.FULL` (legacy compatibility shim) while persisting worked shifts and actual durations in `DailyReportWorkedShift`.
  - Full retirement of `unique_current_daily_report_per_date_shift` occurs only after legacy historical migration/archival (`X08`, Phases `A.8`/`A.12`).
- **Rollback Strategy**:
  - `projects/migrations/0022_project_coordinates.py` (depends on `0021_project_measurement_unit`) and `field_reports/migrations/0026_daily_report_b01_contract.py` (depends on `0025_material_unknown_type`) are strictly additive and reversible via standard Django reverse migrations (`migrate projects 0021` and `migrate field_reports 0025`, then re-apply to `0022` and `0026`), dropping only newly added constraints, tables, and columns with zero impact on pre-existing rows.

---

## 3. Domain Rules & Invariants

### 3.1 Measured Zero vs. Unset vs. Not-Measured (`C02`, `FR-009`, `FR-010`)
- `quantity = Decimal('0')` or `Decimal('0.00')` with `quantity_measured = True` → **Valid measured zero**; preserved as `0` / `0.00` in API, UI, aggregations, and exports.
- `quantity = None` OR `quantity_measured = False` → **Unknown / unrecorded**; excluded from numeric sums (tracked via `unrecorded_count`) and NEVER coerced to `0`.
- Positive-only domain rules (e.g., concrete strength / pressure tests) remain strictly `> 0`.

### 3.2 Canonical Shifts & Actual Person-Hours (`C03`, `FR-011`, `FR-012`)
- Valid shift IDs: strictly `{1, 2, 3}` (integer or string `"1"`, `"2"`, `"3"`). Any other value (e.g., `"4"`, `"morning"`, `"invalid"`) raises a validation error—no silent remapping.
- Legacy `ActivityRowShift` (`shift_1`, `shift_2`, `shift_3`) maps 1:1 to canonical IDs `(1, 2, 3)` at the contract boundary while rejecting unknown strings.
- `actual_person_hours = count * actual_duration_hours` ONLY when `actual_duration_hours is not None` and `count is not None`; otherwise `None` (`unknown`).

### 3.3 Labor Metric Labeling Guard (`D07`, `FR-013`)
| Metric Key | English Label | Persian Label | Attendance Deduplication Proof Required? |
| :--- | :--- | :--- | :---: |
| `headcount` | Headcount (Persons) | تعداد نفرات | Yes (when summed across activities/shifts) |
| `person_shifts` | Person-Shifts | نفر-شیفت | No (valid for row sums across shifts/activities) |
| `person_days` | Person-Days | نفر-روز | **Yes (STRICT — forbidden for raw activity row sums)** |
| `person_hours` | Person-Hours | نفر-ساعت | No, but requires non-null `actual_duration_hours` |

### 3.4 Form Presentation Profile & Appendix Partitioning (`C04`, `FR-014`, `FR-015`)
- Input: Project labor rows (with `title_code`, `job_title`, `category ∈ {indirect, direct}`, shift counts) + selectable `profile_code` (e.g., `shiraz-34-32-v1`).
- Partition output:
  - `standard_indirect`: Fixed 34 positional slots matching `shiraz-34-32-v1`.
  - `standard_direct`: Fixed 32 positional slots matching `shiraz-34-32-v1`.
  - `appendix_indirect`: All additional, custom, or historical indirect titles outside the 34 fixed slots (preserved verbatim, never dropped or merged).
  - `appendix_direct`: All additional, custom, or historical direct titles outside the 32 fixed slots (preserved verbatim, never dropped or merged).

### 3.5 Weather & MET Norway 3-Day Forecast (`X07`, `C08`, `FR-017`)
- Observed block: `{weather_condition, temp_min, temp_max, wind_speed, soil_condition, source: "weather_logs", log_date}` — any absent reading serializes as `null` with `status: "unknown"`.
- Forecast block: `{provider: "MET Norway Locationforecast 2.0", coordinates: {lat, lon} | null, days: [day+1, day+2, day+3], status: "ok" | "unknown", unavailable_reason: str | null}`.

---

## 4. Reference-Day Fixture Structure (`SIM-A1-001`)

| Attribute | Value |
| :--- | :--- |
| Project Code (`project_code`) | `SIM-A1-001` |
| Synthetic Labeling | `is_synthetic_reference = True`; project name explicitly labeled `[SYNTHETIC A.1 REFERENCE] ...` |
| Actual Start Date | Gregorian `2027-05-11` / Solar Hijri `1406-02-21` (Day 1) |
| Reference Report Date | Gregorian `2027-05-22` / Solar Hijri `1406-03-01` (Saturday / `شنبه`, Day 12) |
| Official Report Number | `SIM-A1-001-12-1406-03-01` |
| Coordinates | `29.591800, 52.583700` (Shiraz synthetic reference coordinates) |
| Worked Shifts | Shift `1` (`actual_duration_hours = 8.50`), Shift `3` (`actual_duration_hours = None` → unknown person-hours); Shift `2` omitted (unworked) |
| Controlled Activity Cases | Measured `0`, `0.00`, positive `12.50`, unset (`null`), and `not-measured` (`quantity_measured = False`) |
| Controlled Labor Cases | Standard Shiraz 34/32 indirect & direct roles + 1 custom indirect role + 1 historical direct role (routed to Appendix) |
| Observed Weather Log | `WeatherLog` on `2027-05-22` with `clear`, `temp_min=16.0`, `temp_max=31.5`, `wind_speed="12 km/h NW"`, `soil_condition="خشک / Dry"` |
