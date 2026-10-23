# Phase 1 Data Model: Specialty Unit Daily Sections and Structured Aggregation

**Feature**: 033-daily-sections-grid | **Date**: 2026-10-23
**Conventions**: All tables are UUID-keyed, timestamped, and live in PostgreSQL. Unit-report child rows belong to a `DisciplineSubReport` version (032 container) with `is_deleted`/`deleted_at` soft-delete; derived rows belong to the full-shift `DailyReport` summary (032) and use `is_derived=True`. All spoke FKs are project-scoped; storage IDs in this document match the codebase names used by tasks.

## 1. Configuration family (`project_templates`)

### 1.1 `LaborTitleCatalog` / `LaborTitleCatalogTitle`
Versioned per-project (and per-template) labor-title catalog. Editable only while its owning `ProjectTemplate` is in draft; activation snapshots titles into the immutable reporting-configuration activation (matching 032 Section 3's `ProjectReportingConfigurationUnit` pattern).

- `LaborTitleCatalog`: project/template owner, version name/number, notes, effective period on activations only (no direct effective dating).
- `LaborTitleCatalogTitle`: catalog FK, `title_code` (stable, language-independent), `title_label` + `title_label_fa` (translatable), `category` (indirect/direct), `display_order` (non-negative int), `active` boolean, `legacy_alias` (optional original legacy title string), `project_specific` boolean. Uniqueness: (catalog, title_code), (catalog, category, display_order).
- Activation children `ProjectReportingConfigurationLaborTitle` mirror the snapshot (configuration FK, title_code, category, display_order) and are immutable after activation (§ 032 config pattern).
- Migration seeding: create default versions per affected project from the legacy evidence lists (`0002_seed_labor_titles.py`, `0010_shiraz_labor_titles.py` → 34/32+33/32 shapes) with alias links so existing rows in `DailyLabor`/`DisciplineSubReportLabor.job_title` resolve by `legacy_alias` first, exact `title_label` second. SPEC-02's 34/32 and the workbook's 32/36 counts are recorded in version notes only.
- Resolution rule (aggregation + serializer validation): resolve a row's job title to the effective catalog title via alias → exact label → project-specific title; unresolved titles are rejected at save/submit with a localized error listing available Catalog titles.

### 1.2 Configuration: man-hours rule + vocabulary + section defaults
Add to `ProjectReportingConfiguration` (immutable per activation, like required units):

- `man_hours_rule_code` (choice from a fixed registry: `standard_shift_plus_overtime` default; future codes allowed at code level), `standard_shift_hours` (positive decimal, template-owned, used by the default rule).
- `stoppage_reasons`: snapshot child rows (`ProjectReportingConfigurationStoppageReason`: `reason_code` stable + translatable labels; seed defaults `breakdown`, `lack_of_fuel`, `weather`, `no_operator`, `site_obstruction`; project-extensible at template level). Validation at save/submit checks codes against the effective snapshot.
- Optional later feature hook: per-section ordering flags for the third feature's layout; not used here.

## 2. Unit-report child rows (`sub_reports`)

### 2.1 `DisciplineSubReportActivity` (extended in place)
Existing fields retained. Additions/clarifications:

- `contractor_ref` (FK `projects.Stakeholder`, required, project-scoped, contractor-role; validated at save and submit); `crew_name` remains a separate, never-substituted column.
- `parcel` (char, optional). `block`, `floor`, `zone` (location) retained.
- `activity_ref` (FK `projects.Activity`, required, active + approved WBS of the same project).
- `quantity`: positive decimal when provided (`> 0`, zero/negative rejected); `unit` required when quantity provided; optional when absent.
- `shift`: restricted to the recognized project shift vocabulary at save; unknown values rejected (never silently remapped).
- `headcount` = `foreman_count + worker_count` maintained in `save()`.
- Validation errors (localized codes): `quantity_must_be_positive`, `invalid_shift`, `activity_not_in_project_scope`, `contractor_not_in_project_scope`, `contractor_required`.

### 2.2 `DisciplineSubReportLabor` (extended in place)
Add `overtime_hours` (decimal ≥ 0, default 0) and `contractor_ref` (optional project stakeholder). `labor_category` (indirect/direct) and `job_title` retained but now validated against the effective catalog at save/submit (alias/exact/project-specific title resolution); unknown titles rejected with `unknown_job_title`. Counts remain non-negative integers (`headcount_must_be_non_negative`). Man-hours are computed at aggregation time from the configuration rule (not stored on the unit row), guaranteeing one reproducible value per project/day.

### 2.3 `DisciplineSubReportMachinery` (new)
- `sub_report` FK; `row_number`; `equipment_type` (required translatable-stable text); `equipment_ref` (optional stable project-scoped equipment identity — declared identity enables item-level dedupe); `status_total`, `status_active`, `status_ready`, `status_inactive`, `status_under_repair` (non-negative ints, defaults 0);
- `operating_hours`, `stoppage_hours`, `repair_hours` (decimals ≥ 0, optional);
- `stoppage_reason_code` (FK-by-code to effective vocabulary; blank only when `stoppage_hours ≤ 0`);
- validation rules (submission-time + save-time): `stoppage_reason_required_when_stoppage_gt_zero`, `hours_exceed_day_limit` (operating+stoppage+repair > 24 per declared item identity or per row when no identity), `stoppage_reason_not_in_vocabulary`, `status_count_must_be_non_negative`.
- Row-level vs item-level mix: rows that carry an `equipment_ref` are item rows; rows without are type rows; sum consistency type-level is validated at submit when both styles coexist (`machinery_status_sums_inconsistent`).

### 2.4 `DisciplineSubReportMaterial` (extended in place)
Add `transaction_type` (`receipt` / `consumption`, required), `material_ref` (FK `resources.Material`, optional at draft, required for receipt), `consumption_location` (text; required for consumption), `supplier` (text), `warehouse_document_reference` (project-scoped char identifier; required for receipt, stored verbatim). `quantity` stays required and positive. Receiptness decision rule: `transaction_type = receipt` AND the reference resolves to an actual project warehouse document record (resolution service R5) — an unresolvable reference keeps the row saved but **not** displayed as a receipt (it remains a non-receipt generic row; displayed under warnings).

### 2.5 `DisciplineSubReportConcrete` (extended in place)
Add `structural_element` (text/char), `parcel`, `batching_plant` (text or project-scoped plant ref), `truck_delivery_note_number` (char), `lab_sample_code` (char), `sampling_state` (`not_sampled` default / `sampling_declared`), `test_sheet_count` (non-negative int), `qc_inspection` (FK `risk.Inspection`, nullable until linkage created). Rules: `volume_m3 > 0` (`volume_must_be_positive`); cross-project references rejected (`reference_not_in_project_scope`); when `sampling_state = sampling_declared`, `lab_sample_code` AND `test_sheet_count` MUST be present by submit (`sampling_requires_test_information`), and the linkage service creates/sets `qc_inspection` (same project; one inspectrow per declared sample) at submission or correction — keeping the record editable until interpretive linkage is required.

### 2.6 Structured narrative child rows (new)
- `DisciplineSubReportIssue`: `sub_report` FK; `row_number`; `text` (plain text, markup washed); `kind` (`issue` / `barrier`); `owner_user` (FK, required for barriers; recommended for issues); `due_date` (required for barriers; optional for issues); validation: barrier requires owner + due date (`barrier_owner_and_due_date_required`).
- `DisciplineSubReportVisit`: `sub_report` FK; `row_number`; `text`; (source unit + date inherited from the parent report).
- `DisciplineSubReportHseIncident`: `sub_report` FK; `row_number`; `text`; `severity` (`minor` / `moderate` / `major`); `immediate_action` (text, required on incident creation); on creation of a submitted version containing an incident, the HSE notification handler emits the required `notifications.Notification` (and task where supported) referencing the incident row (id, unit, date, severity).
- `DisciplineSubReportNote` (-general): unchanged, plus explicit enforcement that only `note_type ∈ {issue, visit}` rows (unchanged semantics) or structured children above ever appear as structured narrative in aggregation; `other` notes are never promoted (FR-032).

### 2.7 `UnitReportAttachment` (new)
- `sub_report` FK; `row_kind` + `row_id` (nullable target section row), `storage_key`/`file` reference, declared `content_type`, measured size ≤ 10 MB, `capture_date` (date), `work_front` (char), source unit + project inherited from parent, checksum; validity reason (none / `unsupported_file_format` / `file_too_large` / `cross_project_refusal`). Files are editable only while the parent report is draft/rejected; content-based validation (JPEG/PNG signature) runs at upload in addition to declared type/extension; cross-project target rows are refused before storage.

## 3. Derived projection rows (`field_reports`)

All derived rows live under the full-shift `DailyReport` and are rebuilt only by the aggregation service; product users cannot create/edit them. Every derived row carries `is_derived=True` and row-level provenance fields (source_report_id/version/unit, source_row_kind, source_row_id), plus one `DailyReportDerivedSource` entry per contributing source (multi-source for combined values; `ordinal` deterministic).

### 3.1 `DailyReportActivity` (existing; extended)
Full executed-activity column set from 2.1 (WBS activity ref+label, activity_description, shift, contractor label + crew name separate columns, headcount, parcel, block, floor, location, completed quantity, unit, notes).

### 3.2 `DailyReportLabor` (existing; extended)
Per (category, resolved title) aggregate with `total_count = Σ present`, `absence_count = Σ leave`, `overtime_hours = Σ overtime`, `contractor` retained as a per-source snapshot column, computed `man_hours` from the rule, plus `source_sub_report`/`source_discipline` legacy columns kept **only as compat aliases** (they are no longer the source of truth; `DailyReportDerivedSource` is), and a new `source_set_complete` marker for tests. Multi-source rule: one derived row per (category, resolved title) when the same title appears in multiple units, with all sources in `DailyReportDerivedSource` (`derived_kind='labor'`); no last-source-wins.

### 3.3 `DailyReportMachineryRow` (new derived)
- `report` FK; `equipment_type`; `equipment_ref` (nullable; item row when set); five status counts, hours (operating/stoppage/repair, summed per declared identity when mixing item+type rows), `stoppage_reason_code` (item rows) / aggregated flag (type rows); normalization invariant: per-type sums equal the type-row values when both styles coexist.
- Provenance: `DailyReportDerivedSource` (`derived_kind='machinery'`, per contributing row); dedupe invariant: an `equipment_ref` appearing in multiple contributing rows yields exactly one derived item row per identity; type-only rows are never deduped cross-row.
- Fingerprint gains machinery payload (ids, counts, hours, reasons, vocabulary revision marker).

### 3.4 `DailyReportMaterial` (existing; extended)
Adds `transaction_type`, `material_ref`, `consumption_location`, `supplier`, `warehouse_document_reference`, receiptness marker (derived: resolved receipt vs non-receipt), `reconciliation_status` (nullable), `reconciliation_document_id`, `reconciliation_checked_at`. Main-table display rule (UI + serializer contract): only resolved receipt rows are exposed in the main materials section; consumption and unresolved generic rows are exposed by the details/drill-down endpoint only. Reconciliation (service rework per R5) compares each receipt/consumption row against the **specific referenced warehouse document** quantity, returning `match`/`mismatch`/`insufficient_data` with the document reference and evidence; global balance remains an advisory cross-check only.

### 3.5 `DailyReportConcreteLog` (existing; extended)
Extended with the 2.5 column set (including `batching_plant`, `truck_delivery_note_number`, `lab_sample_code`, `sampling_state`, `test_sheet_count`, `qc_inspection`) so the derived pour records are as rich as the source.

### 3.6 `DailyReportGeneralActivity` (new derived)
Structured row mirroring 2.1-family (description, location/building, quantity/volume, unit, notes) with row-level provenance + multi-source support. Replaces the previous behavior of persisting general activities as preformatted text blobs (FR-028, FR-041); the old text-encoding migration path is removed in the same rebuild.

### 3.7 `DailyReportIncident` (existing; extended) + `DailyReportVisit` (new derived)
- `DailyReportIncident` gains a nullable `severity`, keeps `corrective_action` as the immediate-action interpretation for HSE rows, and gains structured source-row provenance; it is used for derived issues/barriers/HSE incidents (barrier: `incident_type='barrier'` + `follow_up_owner_user` + `due_date`); HSE incident rows additionally keep a `notification_id` reference to the notification/task generated when the HSE incident was created.
- `DailyReportVisit` (new derived child): structured visit rows with `row_number`, `text`, source attribution.
- Generic-`other` notes: persist as structured general note rows, never as issues/visits — they populate a bounded "notes" narrative section only when explicitly typed (FR-032).
- All narrative rows (issues, visits, incidents, barriers) preserve display order (`row_number` / `ordinal` in `DailyReportDerivedSource`) across rebuilds (FR-045).

### 3.8 Attachment projection
Attachment data is not copied; the summary exposes counts + links computed from contributing unit reports' attachments grouped by related section (via provenance chain) — `attachment_count` per section with abstract storage URLs surfacing only to users with project membership (server-side access re-check at fetch time; no URLs leaked to unauthorized users).

### 3.9 Fingerprint + invariants recap
- Fingerprint payload gains: machinery rows, receipt/consumption semantics, structured narrative rows, catalog rule code + snapshot revision, vocabulary revision marker, attachment counts/checksums.
- Existing invariants extended: empty/zero/unknown distinctness (null-preserving fields everywhere; absent sums never materialized as zeros), atomic rebuild (single transaction, prior summary intact on mid-failure), idempotency (three consecutive rebuilds equal), override preservation (weather/site-status/management opinion), deterministic order via existing lock order Project → current unit reports → DailyReport.
