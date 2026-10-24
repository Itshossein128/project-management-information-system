# Tasks: Specialty Unit Daily Sections and Structured Aggregation

**Input**: Design documents from `/specs/033-daily-sections-grid/` (plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md)

**Prerequisites**: Feature 032 (`specs/032-unit-report-source-truth/`) delivered: canonical units, unit-page authoring, states/eligibility, current versions, rebuild fingerprint, `DailyReportDerivedSource` provenance. Postgres + Redis must run before all pytest work.

**Tests**: Explicitly requested by the spec (SC-010: RED-then-GREEN per acceptance scenario). Write each story's tests FIRST, verify they FAIL, then implement.

**Organization**: Tasks grouped by user story (spec US1–US8). US8 (aggregation engine) deliberately runs last of the stories because it transfers all section families; per-story aggregation slices ship inside each section story so the engine is extended, not hoarded.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: US1–US8 mapped to `specs/033-daily-sections-grid/spec.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Test scaffolding and baseline evidence for RED-run comparisons.

- [X] T001 Create empty RED test modules per plan structure: `apps/api/core/sub_reports/tests/test_section_contracts.py`, `test_labor_catalog.py`, `test_machinery_contract.py`, `test_materials_receipt_contract.py`, `test_concrete_qc_link.py`, `test_structured_narrative.py`, `apps/api/core/field_reports/tests/test_machinery_derivation.py`, `test_receipts_only_summary.py`, `test_structured_transfer.py` — each a runnable empty pytest module (documented skips) so suites can be invoked from day one.
- [X] T002 Record baseline evidence in `specs/033-daily-sections-grid/baseline.md`: run `pnpm typecheck` (record the known unrelated `DailyReportForm.tsx` failure), `cd apps/api/core && set -a && source /workspace/.env && set +a && ../.venv/bin/python -m pytest sub_reports/tests field_reports/tests --quick` scope summary, and note the 032 green state to compare against later.

**Checkpoint**: Scaffolding + baseline documented.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Configuration family and schema expansions that US1–US4+ build on. MUST complete before user stories.

**⚠️ CRITICAL**: No user story work below until this phase is complete.

- [X] T003 [P] Implement labor-title catalog + rule/vocabulary configuration models in `apps/api/core/project_templates/models.py` per data-model §1: `LaborTitleCatalog` (project/template owner, `version_name`, `notes`), `LaborTitleCatalogTitle` (`title_code` stable language-independent + `(catalog, title_code)` unique, `title_label`/`title_label_fa` translatable, `category` indirect/direct, `display_order` non-negative + `(catalog, category, display_order)` unique, `active`, `legacy_alias`, `project_specific`), immutable activation children `ProjectReportingConfigurationLaborTitle` and `ProjectReportingConfigurationStoppageReason` (`reason_code` + labels), plus on `ProjectReportingConfiguration`: `man_hours_rule_code` (fixed registry choice, default `standard_shift_plus_overtime`) and `standard_shift_hours` (positive decimal, default 8).
- [X] T004 Create additive migration `apps/api/core/project_templates/migrations/0004_labor_catalog_and_rules.py` (models existing → nothing removed; verify `makemigrations --check --dry-run` clean afterwards).
- [X] T005 [P] Implement catalog draft CRUD + effective-snapshot serializers/services in `apps/api/core/project_templates/serializers.py` + `services.py` per `contracts/reporting-configuration-catalog-api.md` §1–§2: draft-only catalog/title CRUD (template-management permission), title resolution order legacy alias → exact label → project-specific alias, `unknown_job_title` on unresolved, extend `activate`/`preview` to snapshot labor titles, man-hours rule, and stoppage vocabulary immutably.
- [X] T006 Wire catalog endpoints + permissions in `apps/api/core/project_templates/views.py` + `urls.py`: `/project-templates/{pk}/labor-catalogs/` CRUD (draft-only), reporting-configuration current/by-date reads exposing the new snapshot fields; every lookup project-scoped (Constitution I).
- [X] T007 [P] Register the default man-hours rule implementation in `apps/api/core/field_reports/services/man_hours.py`: pure function for `standard_shift_plus_overtime` = `present_count × standard_shift_hours + overtime_person_hours`; identical inputs → identical outputs (FR-008); no hard-coded project constants.
- [X] T008 Add unit-report child-row schema per data-model §2 in `apps/api/core/sub_reports/models.py`: new `DisciplineSubReportMachinery` (`equipment_type` required; optional `equipment_ref` stable identity; five non-negative status counts `status_total/active/ready/inactive/under_repair`; `operating_hours`, `stoppage_hours`, `repair_hours` ≥ 0 decimals; `stoppage_reason_code` blank only when `stoppage_hours == 0`), `DisciplineSubReportIssue` (`kind` issue/barrier, `text` plain text, `display_order`/`row_number`, `owner_user`, `due_date`), `DisciplineSubReportVisit` (`row_number`, `text`), `DisciplineSubReportHseIncident` (`severity` minor/moderate/major, `immediate_action`, `row_number`), `UnitReportAttachment` (`row_kind`+`row_id` nullable, storage key, declared content type, measured `size_bytes` ≤ 10 MB, `capture_date`, `work_front`, `checksum`), and in-place extensions: `DisciplineSubReportActivity` + `parcel`, `contractor_ref`; `DisciplineSubReportLabor` + `overtime_hours` (≥ 0 decimal, default 0), `contractor_ref`; `DisciplineSubReportMaterial` + `transaction_type` (receipt/consumption, required), `material_ref`, `consumption_location`, `supplier`, `warehouse_document_reference`; `DisciplineSubReportConcrete` + `structural_element`, `parcel`, `batching_plant`, `truck_delivery_note_number`, `lab_sample_code`, `sampling_state` (not_sampled/sampling_declared), `test_sheet_count` (non-negative int), `qc_inspection` (nullable FK to `risk.Inspection`); `DisciplineSubReportGeneralActivity` unchanged columns confirmed.
- [X] T009 Create additive migration `apps/api/core/sub_reports/migrations/0008_section_contracts_and_more.py` for T008 (backfill-compatible nullability; no destructive constraint in this feature).
- [X] T010 [P] Implement derived projection schema per data-model §3 in `apps/api/core/field_reports/models.py`: new `DailyReportMachineryRow` (`equipment_type`, nullable `equipment_ref`, five status counts, hours, `stoppage_reason_code`, `is_derived=True`), `DailyReportGeneralActivity` (structured: description, location/building, quantity/volume, unit, notes), `DailyReportVisit` (`row_number`, `text`, structured `is_derived=True`), and extensions: `DailyReportLabor` + explicit `source_set_complete` marker + null-preserving fields (retain legacy `source_sub_report`/`source_discipline` as compat aliases only), `DailyReportMaterial` + `transaction_type`, `material_ref`, `consumption_location`, `supplier`, `warehouse_document_reference`, `receipt_resolved` marker, `reconciliation_status` (match/mismatch/insufficient_data nullable), `reconciliation_document_id`, `reconciliation_checked_at`; `DailyReportConcreteLog` + full §2.5 column set; `DailyReportActivity` + explicit `contractor` and `crew_name` separate columns + `parcel`; `DailyReportIncident` + nullable `severity` + `notification_id` + structured source-row provenance. Every new derived row type participates in `DailyReportDerivedSource` via `derived_kind` values `machinery`, `general_activity`, `visit`, `hse_incident`.
- [X] T011 Create additive migration `apps/api/core/field_reports/migrations/0021_section_projection_and_more.py` for T010.

**Checkpoint**: Configuration family + section schema + derived projection tables exist; RED suites still fail on missing VALIDATION/behavior, not on import errors.

---

## Phase 3: User Story 1 — Executed-activity rows with the full site contract (Priority: P1) 🎯 MVP

**Goal**: Buildings/Electrical/Mechanical users save executed-activity rows carrying the full FR-001 contract; invalid values (non-positive quantity, foreign WBS/contractor, unknown shift) are rejected with explicit localized errors, and the aggregate reproduces every column with crew and contractor separated.

**Independent Test**: Save a complete valid row on the Buildings panel; attempt zero quantity, foreign-project WBS, foreign contractor, unknown shift — each refused with a fielded error; submit/approve the report and confirm the derived summary row carries all columns + source link.

### Tests for User Story 1 (write FIRST — verify RED)

- [X] T012 [P] [US1] Write activity-contract RED tests in `apps/api/core/sub_reports/tests/test_section_contracts.py` (class-level grouping per `contracts/unit-report-sections-api.md` §1): `quantity_must_be_positive` on provided quantity 0 and −12.5; `invalid_shift` for unrecognized shift values (never silently remapped to shift 1); `activity_not_in_project_scope` for WBS activity of another project and for inactive/unapproved activity; `contractor_not_in_project_scope`; `contractor_required` missing; crew_name + contractor survive as separate columns in the serializer output.
- [X] T013 [P] [US1] Extend `apps/api/core/field_reports/tests/test_unit_report_provenance.py` with RED assertions: derived activity row exposes parcel/block/floor/location/headcount and `crew_name` distinct from `contractor`; scenario "approved unit activity appears with all required columns and a source link" (spec US1 mandatory scenario 1); cross-project source contributes nothing.

### Implementation for User Story 1

- [X] T014 [US1] Enforce activity validation in `apps/api/core/sub_reports/serializers.py` (activity serializer) + `services`: contractor_ref required + project/contractor-role check; activity_ref active+approved+same-project check; provided `quantity > 0`; `shift` restricted to the recognized vocabulary with a full synonym list and NO silent fallback; `headcount` maintained as `foreman_count + worker_count` in `save()` of `DisciplineSubReportActivity` (T008 dependency).
- [X] T015 [US1] Extend activity aggregation + fingerprint in `apps/api/core/field_reports/services/daily_report_aggregation.py`: map every §1 column into `DailyReportActivity` derived rows; REMOVE the silent `_normalize_shift` coercive fallback and the `crew_name → subcontractor_name` coercion (crew saved as crew column, contractor as contractor column); extend `compute_aggregation_fingerprint` payload with the new activity fields (parcel, contractor_ref id, headcount components).
- [X] T016 [US1] Extend `apps/api/core/field_reports/serializers.py` `DailyReportActivitySerializer` per `contracts/daily-summary-sections-api.md` §1.1: all columns + null-preserving unknown/empty/zero distinction + per-row provenance via `DailyReportDerivedSource` (`derived_kind='activity'`).
- [X] T017 [P] [US1] Add activity-section editing UI in `apps/web/src/components/department/unit-daily-report-panel.tsx` + new `section-activities.tsx` (Buildings/Electrical/Mechanical tabs): inline validation chips mapping every T012 error code to localized messages; searchable creatable selects (WBS activity, contractor) with Add action INSIDE the open menu; keyboard-operable.
- [X] T018 [P] [US1] Localize all US1 strings in `apps/web/src/app/locales/fa.json` + `en.json` (labels, `quantity_must_be_positive`, `invalid_shift`, `activity_not_in_project_scope`, `contractor_not_in_project_scope`, `contractor_required`, crew/contractor columns).

**Checkpoint**: Buildings/Electrical/Mechanical rows validate, aggregate, and render complete; RED suite T012/T013 GREEN.

---

## Phase 4: User Story 2 — Labor with a project-configurable catalog (Priority: P1)

**Goal**: Labor rows resolve via the effective versioned catalog, reject negative counts/unknown titles, compute man-hours reproducibly from the configured rule, aggregate per (category, resolved title) with totals, and keep every contributing source in the drill-down.

**Independent Test**: Record the same job title from two units for one date; rebuild; verify the aggregated total equals the sum of both and the drill-down lists every source; attempt a negative count and unknown title → refused.

### Tests for User Story 2 (write FIRST — verify RED)

- [X] T019 [P] [US2] Write catalog RED tests in `apps/api/core/sub_reports/tests/test_labor_catalog.py`: draft-only CRUD permission matrix; activation snapshots titles + display_order immutably; resolution order legacy alias → exact label → project-specific; historical rows keep former evidence after a catalog revision; two projects get different catalogs (frustrate cross-project reads).
- [X] T020 [P] [US2] Write labor-contract + aggregation RED tests in `apps/api/core/sub_reports/tests/test_section_contracts.py` + `apps/api/core/field_reports/tests/test_machinery_derivation.py`-independent file `apps/api/core/field_reports/tests/test_labor_totals.py`: `headcount_must_be_non_negative` for present −1 / leave −1; `unknown_job_title` outside effective catalog; multi-source title aggregation retains BOTH sources and `source_set_complete` (spec scenario 3); man-hours computed via T007 rule (present × `standard_shift_hours` + overtime) and deterministic; indirect/direct/overall totals calculable (spec FR-009).

### Implementation for User Story 2

- [X] T021 [US2] Enforce labor validation in `apps/api/core/sub_reports/serializers.py` + `apps/api/core/project_templates/services.py` resolution helper: effective-catalog snapshot resolution per report date; category must match catalog title's category (`invalid_labor_category`); counts non-negative ints; optional `contractor_ref` project-scoped; `overtime_hours` ≥ 0.
- [X] T022 [US2] Extend labor aggregation + totals in `apps/api/core/field_reports/services/daily_report_aggregation.py`: derive per-(category, resolved title) rows using `man_hours` service (T007); never attribute multi-source totals to the last unit — normalized `DailyReportDerivedSource` set (`derived_kind='labor'`, ordinal-deterministic); produce category/overall totals; extend fingerprint with labor overtime/contractor fields.
- [X] T023 [US2] Extend `apps/api/core/field_reports/serializers.py` `DailyReportLaborSerializer` per `contracts/daily-summary-sections-api.md` §1.2 (summary payloads + per-unit breakdown + `source_count` markers).
- [X] T024 [P] [US2] Add labor-section UI editor in `apps/web/src/components/department/section-labor.tsx` (title select constrained by effective catalog + localized display order, counts/overtime/contractor fields, reduction-safe add/remove) registered in `unit-daily-report-panel.tsx` for applicable units.
- [X] T025 [P] [US2] Localize US2 strings in `apps/web/src/app/locales/fa.json` + `en.json` (catalog-driven titles are data; only labels/errors live here) incl. `headcount_must_be_non_negative`, `unknown_job_title`, `invalid_labor_category`.

**Checkpoint**: Catalog-driven labor entry + totals + multi-source drill-down work end to end.

---

## Phase 5: User Story 3 — Machinery status grid (Priority: P1)

**Goal**: Machinery unit records per-type/per-item daily statuses and hours with controlled stoppage reasons; the summary derives the five-status table without double counting stable-identity items.

**Independent Test**: Record one item's status + hours with a valid reason (aggregates once with a type-sum view); refuse a reason-less positive stoppage, >24h item, out-of-vocabulary reason, and a duplicated stable identity (spec scenario 4 + 9 machinery parts).

### Tests for User Story 3 (write FIRST — verify RED)

- [X] T026 [P] [US3] Write machinery-contract RED tests in `apps/api/core/sub_reports/tests/test_machinery_contract.py`: `stoppage_reason_required_when_stoppage_gt_zero`; `hours_exceed_day_limit` when operating+stoppage+repair > 24 for a declared item identity or for the row without identity; `stoppage_reason_not_in_vocabulary` for free-text/non-snapshot codes; `status_count_must_be_non_negative`; `machinery_status_sums_inconsistent` for mixed type/item rows disagreeing; vocabulary returned with localized labels.
- [X] T027 [P] [US3] Write derivation RED tests in `apps/api/core/field_reports/tests/test_machinery_derivation.py`: five correct statuses derived from the Machinery unit report (spec scenario 4 first half); a stable `equipment_ref` appearing in multiple rows/aggregated exactly once; type-only rows never deduped cross-row; per-type sums correct when item+type styles mix; provenance rows written with `derived_kind='machinery'`; fingerprint includes machinery payload.

### Implementation for User Story 3

- [X] T028 [US3] Enforce machinery validation in `apps/api/core/sub_reports/serializers.py` (child CRUD) + `views` per `contracts/unit-report-sections-api.md` §3, using the effective snapshot's `stoppage_reasons` from T003/T005.
- [X] T029 [US3] Implement machinery derivation in `apps/api/core/field_reports/services/daily_report_aggregation.py`: build `DailyReportMachineryRow` rows (item-level when identity declared; type-level otherwise), identity dedupe, type-sum consistency washout on rebuild, fingerprint extension; provenance via `DailyReportDerivedSource`.
- [X] T030 [US3] Extend `apps/api/core/field_reports/serializers.py` + `daily_report_views.py` per `contracts/daily-summary-sections-api.md` §1.3 (machinery table payload with `equipment_type`, `equipment_ref`, five counts, hours, reason code+label, `vocabulary_revision_marker`).
- [X] T031 [P] [US3] Add machinery-section UI in `apps/web/src/components/department/section-machinery.tsx`: five numeric status columns per row, controlled reason select (localized labels from snapshot), inline day-limit + reason-required errors; registered on the Machinery panel in `unit-daily-report-panel.tsx`.
- [X] T032 [P] [US3] Localize US3 strings in `apps/web/src/app/locales/fa.json` + `en.json` (five status headers, hours labels, error codes).

**Checkpoint**: Machinery table renders in the summary and is identity-dedupe-safe.

---

## Phase 6: User Story 4 — Receipts-only materials + document-anchored reconciliation (Priority: P1)

**Goal**: Receipt/consumption recorded independently; the main summary table shows only real receipts; consumption stays traceable in details; reconciliation compares against the specific referenced warehouse document with traceable `match`/`mismatch`/`insufficient_data`.

**Independent Test**: Record one receipt (with warehouse document reference) and one consumption row; main table shows only the receipt; details show the consumption; reconciliation of the receipt equals/mismatch/insufficient per scenario; a global-balance-only comparison never fabricates a match.

### Tests for User Story 4 (write FIRST — verify RED)

- [X] T033 [P] [US4] Write receipt-contract RED tests in `apps/api/core/sub_reports/tests/test_materials_receipt_contract.py`: `transaction_type_required`; `receipt_requires_document_reference`; `consumption_location_required_for_consumption`; `quantity_must_be_positive`; supplier/warehouse-document reference preserved verbatim + independently; cross-project material_ref refused (`reference_not_in_project_scope`).
- [X] T034 [P] [US4] Write summary + reconciliation RED tests in `apps/api/core/field_reports/tests/test_receipts_only_summary.py` + `apps/api/core/field_reports/tests/test_material_reconciliation_documents.py`: main-table payload contains ONLY resolved receipts (spec scenario 5 first half); generic/unresolved rows never appear as receipts; consumption rows always present in details payload (FR-022); reconciliation statuses vs the SPECIFIC referenced document (`match` equal, `mismatch` differing with both quantities, `insufficient_data` for missing/unresolvable/lacking documents — never a fabricated match); global balance appears only under a labeled `cross_check` key; evidence persists `resolved_document_id`.

### Implementation for User Story 4

- [X] T035 [US4] Enforce material validation in `apps/api/core/sub_reports/serializers.py` per `contracts/unit-report-sections-api.md` §4.
- [X] T036 [US4] Extend materials aggregation in `apps/api/core/field_reports/services/daily_report_aggregation.py`: derive receipt/consumption rows with the §4 fields; WRITE receipt-resolution into the rebuild (resolved vs unresolved_reference per R5); extend fingerprint; provenance `derived_kind='material'`.
- [X] T037 [US4] Rework `apps/api/core/field_reports/services/material_reconciliation.py` to document-anchored comparison (R5/FR-023/FR-024): resolve the specific project-scoped warehouse document record from `warehouse_document_reference`, compare recorded vs document quantity, write reconciliation fields on `DailyReportMaterial`; keep the `match`/`mismatch`/`insufficient_data` response shape with `evidence.basis='specific_document'`; retain global-balance output ONLY as labeled `cross_check`.
- [X] T038 [P] [US4] Add materials-section UI in `apps/web/src/components/department/section-materials.tsx` (transaction-typed rows; receipt requires document reference; consumption location field appears for consumption) registered on the Warehouse panel; summary materials + reconciliation UI in `apps/web/src/components/daily_reports/summary/` (receipts-only main table + visible details toggle listing consumption + status pills, per `contracts/unit-report-and-summary-ui.md` §2).
- [X] T039 [P] [US4] Localize US4 strings in `apps/web/src/app/locales/fa.json` + `en.json` (receipt/consumption, reconciliation statuses, `insufficient_data` wording, error codes).

**Checkpoint**: Receipts-only summary + document-anchored reconciliation behave per contract.

---

## Phase 7: User Story 5 — Concrete pours with QC traceability (Priority: P2)

**Goal**: Concrete rows carry the full FR-025 column set; sampling declaration requires test information and links the existing `risk.Inspection` store; negative volumes and foreign references are rejected.

**Independent Test**: Save a full valid pour with declared sampling (QC link created, traceable); refuse negative volume, declared-sampling-without-test-info, and foreign batching-plant reference.

### Tests for User Story 5 (write FIRST — verify RED)

- [X] T040 [P] [US5] Write concrete RED tests in `apps/api/core/sub_reports/tests/test_concrete_qc_link.py`: `volume_must_be_positive`; `sampling_requires_test_information` (declared state without `lab_sample_code` or `test_sheet_count` blocks submit); `reference_not_in_project_scope` for foreign batching plant/document; submit-time linkage creates/sets `qc_inspection` to a project `risk.Inspection` (traceable, idempotent on resubmit); `not_sampled` rows usable without link; derived concrete rows expose the full column set + QC link (spec US5 acceptance scenario 1/4).

### Implementation for User Story 5

- [X] T041 [US5] Enforce concrete validation in `apps/api/core/sub_reports/serializers.py` + implement the QC-linkage service in `apps/api/core/sub_reports/services.py` (create/link same-project `risk.Inspection` at submit/correction; never fabricate parallel QC storage).
- [X] T042 [US5] Extend concrete aggregation columns in `apps/api/core/field_reports/services/daily_report_aggregation.py` (+ serializer `DailyReportConcreteLogSerializer`) per `contracts/daily-summary-sections-api.md` §1.5; extend fingerprint.
- [X] T043 [P] [US5] Add concrete-section UI in `apps/web/src/components/department/section-concrete.tsx` (Buildings/Mechanical panels) incl. sampling toggle revealing required test fields; summary §1.5 display with QC link; localize in `apps/web/src/app/locales/fa.json` + `en.json`.

**Checkpoint**: Concrete contract + QC traceability complete on unit + summary surfaces.

---

## Phase 8: User Story 6 — Structured general activities, issues/barriers, visits, HSE (Priority: P2)

**Goal**: Narrative content persists and aggregates as structured, ordered, source-attributed records; barriers carry owner + due date; HSE incidents carry severity + immediate action and generate the required notification/task; general notes are never auto-classified as issues.

**Independent Test**: Record general activity, barrier (owner+due), visit, HSE incident; rebuild twice; structure and order preserved; incident notification exists; an untyped note never appears as an issue (spec scenario 6).

### Tests for User Story 6 (write FIRST — verify RED)

- [X] T044 [P] [US6] Write structured-narrative RED tests in `apps/api/core/sub_reports/tests/test_structured_narrative.py`: `barrier_owner_and_due_date_required`; `hse_immediate_action_required` + severity enum enforcement; submit-time notification creation (`notifications.Notification` referencing the incident row, id confirmed in the response); general note with issue-like text stays type `other` and is never promoted (FR-032); general activities persist structured columns (never formatted text).
- [X] T045 [P] [US6] Write transfer RED tests in `apps/api/core/field_reports/tests/test_structured_transfer.py`: rebuild twice → issues/visits/HSE/general-activity rows retain fieldwise structure, source attribution, and DISPLAY ORDER exactly (FR-045); HTML/markup in free text is washed at the boundary and never drives structure (FR-041); derived kinds `general_activity`/`visit`/`hse_incident` carry normalized provenance.

### Implementation for User Story 6

- [X] T046 [US6] Enforce narrative validation in `apps/api/core/sub_reports/serializers.py` + `views` (new child CRUD endpoints per `contracts/unit-report-sections-api.md` §6) + implement the HSE notification handler service in `apps/api/core/field_reports/services/hse_incident_notifications.py` (notification + task where supported, linked `notification_id` on derived incident).
- [X] T047 [US6] Replace the text-encoding transfer of general activities/notes in the aggregation path (`apps/api/core/field_reports/services/daily_report_aggregation.py`) with structured `DailyReportGeneralActivity`/`DailyReportVisit`/`DailyReportIncident` rows (issues/barriers use `incident_type='barrier'` + owner + due; HSE rows add severity + immediate action) with order preservation.
- [X] T048 [P] [US6] Add narrative-section UI in `apps/web/src/components/department/` (`section-general.tsx`, `section-issues.tsx`, `section-visits.tsx`, `section-hse.tsx`) assigned per unit table in `contracts/unit-report-and-summary-ui.md` §1; summary structured sections with overdue due-date marks + severity pills; localize in `apps/web/src/app/locales/fa.json` + `en.json`.

**Checkpoint**: Narrative families are structured, ordered, and notification-complete.

---

## Phase 9: User Story 7 — Activity image attachments (Priority: P2)

**Goal**: JPEG/PNG ≤ 10 MB images attach to related activity rows with full provenance; disguised/oversized/cross-project uploads rejected; summary exposes accessible counts + links only.

**Independent Test**: Attach a valid image → retrievable count+link; refuse ZIP/EXE/renamed-invalid/oversized and a foreign-project target without storing partial data.

### Tests for User Story 7 (write FIRST — verify RED)

- [X] T049 [P] [US7] Write attachment RED tests in `apps/api/core/sub_reports/tests/test_section_contracts.py` (attachment group per `contracts/unit-report-sections-api.md` §7): `unsupported_file_format` for ZIP/EXE/content-misdeclared files (content-validated: renamed executable refuses); `file_too_large` above 10 MB; `attachment_row_not_in_version` for targets outside the version; `reference_not_in_project_scope` for cross-project targets — no partial storage on refusal; attachments mutable only on draft/rejected; provenance metadata (capture date, work front, source activity/unit/project) preserved.
- [X] T050 [P] [US7] Write summary-count RED assertions in `apps/api/core/field_reports/tests/test_receipts_only_summary.py`-adjacent file `apps/api/core/field_reports/tests/test_summary_attachment_counts.py`: per-section accessible counts + link payloads derive from contributing units (FR-036); URLs never returned to users lacking project/unit view permission.

### Implementation for User Story 7

- [X] T051 [US7] Implement attachment upload/validation service + endpoints in `apps/api/core/sub_reports/` (serializers, attachment service with content-signature validation, viewset wiring per contract §7; storage via the environment-dependent file-storage holder with MinIO-unavailable behavior documented).
- [X] T052 [P] [US7] Add upload control to activity editors (inline limit/type feedback) and summary attachment counts/links component `apps/web/src/components/daily_reports/summary/AttachmentCountLink.tsx`; localize `apps/web/src/app/locales/fa.json` + `en.json`.

**Checkpoint**: Attachments validated, isolated, and summarized as counts+links.

---

## Phase 10: User Story 8 — Aggregation integrity and correction (Priority: P1, runs after US1–US7)

**Goal**: One engine contracts all section families: atomic + idempotent rebuilds, complete multi-source provenance, distinct empty/zero/unknown, preserved overrides, one-unit-precise corrections, read-only derived rows with one-attempt provenance navigation.

**Independent Test**: Build from ≥3 units across all families; rebuild three times → byte-identical payload; mid-failure test leaves prior summary intact; reject one unit → only its rows vanish; fix data only via the source unit report.

### Tests for User Story 8 (write FIRST — verify RED)

- [ ] T053 [P] [US8] Extend `apps/api/core/field_reports/tests/test_unit_report_rebuild_idempotency.py` RED cases: all-section payload equality across three consecutive rebuilds; fingerprint equality short-circuit; mid-rebuild failure (poisoned section write) leaves the previously valid summary intact (atomicity per FR-038); `authorized reviewer's rejection of one current unit removes only that unit's machinery/material/narrative/attachment contributions (FR-044) while other units' rows are byte-identical.
- [ ] T054 [P] [US8] Extend `apps/api/core/field_reports/tests/test_unit_report_aggregation_eligibility.py` RED cases: zero/empty/unknown distinctness across every section family (null preserved, no fabricated zeros — FR-040); overrides + management opinion untouched by every rebuild (FR-042); concurrent rebuilds converge (extend existing concurrency test file) with no duplicated or orphaned derived rows.

### Implementation for User Story 8

- [X] T055 [US8] Finalize fingerprint + atomicity wiring in `apps/api/core/field_reports/services/daily_report_aggregation.py`: complete fingerprint coverage of machinery/receipts/narrative/attachments/catalog-rule revision + vocabulary revision markers; ensure every derived write is inside the existing single-transaction lock order (Project → current unit reports → DailyReport) with all-section `_clear_derived`/rebuild pairs.
- [X] T056 [US8] Implement the provenance drill-down endpoints + serializers in `apps/api/core/field_reports/daily_report_views.py` + `serializers.py` per `contracts/daily-summary-sections-api.md` §4 (`GET …/daily-reports/{pk}/provenance/{derived_kind}/{derived_row}/`, multi-source-complete, navigate-with-permission-respecting links).
- [X] T057 [US8] Verify read-only derived surface: `apps/api/core/field_reports/daily_report_views.py` exposes NO create/update/delete on derived rows; correction affordances point to source unit report paths; unauthorized provenance navigation returns the standard denial without content disclosure (Constitution I).
- [X] T058 [P] [US8] Add summary drill-down component `apps/web/src/components/daily_reports/summary/SectionProvenanceDrillDown.tsx` wired to T056 endpoints (badge → source unit context in one step; permission notice instead of foreign data), localize in `apps/web/src/app/locales/fa.json` + `en.json`.

**Checkpoint**: Aggregation engine covers every section family with 032-level guarantees extended.

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Deterministic parity, docs, and end-to-end evidence.

- [X] T059 [P] Update API documentation: extend `apps/api/core/sub_reports/ENDPOINTS.md` + `apps/api/core/field_reports/ENDPOINTS.md` + `apps/api/core/project_templates/` docs with new endpoints, statuses, and error codes (documentation REQUIRED whenever behavior/permissions change per Constitution quality gates).
- [X] T060 [P] Run `pnpm typecheck` and fix any NEW frontend errors introduced by this feature (baseline unrelated failures stay documented in `specs/033-daily-sections-grid/baseline.md`; no blanket suppressions per Constitution VI).
- [ ] T061 Run full backend suite vs baseline: `cd apps/api/core && set -a && source /workspace/.env && set +a && ../.venv/bin/python -m pytest sub_reports field_reports project_templates inventory risk -x` and add targeted suites for changed surfaces; record evidence categories in a verification report under `specs/033-daily-sections-grid/`.
- [ ] T062 Create Playwright E2E `apps/web/e2e/tests/daily-sections-aggregation.spec.ts` + helpers per `specs/033-daily-sections-grid/quickstart.md` §5 covering the six mandatory view scenarios (activity+link, cross-project rejection, machinery dedupe, receipts-only, structured order, rebuild idempotence + correction) in BOTH locales; `pnpm e2e -- --grep "daily-sections"` GREEN.
- [X] T063 Audit constitutional gates: bilingual fa/en parity table for all new strings, keyboard operability of all new editors, text-plus-color statuses, documentation updates, evidence-category naming — record in the verification report of T061.
- [X] T064 State verification boundaries explicitly in the final report (local pytest vs browser scope; MinIO/RabbitMQ unavailability bounds attachment/upload claims; usability observation items) per Constitution VI and `quickstart.md` §6.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: none — immediate.
- **Foundational (Phase 2)**: after Setup; BLOCKS every user story (schema + catalogs + rule registry are shared prerequisites).
- **US1 (Phase 3) / US2 (Phase 4) / US3 (Phase 5) / US4 (Phase 6) / US5 (Phase 7) / US6 (Phase 8) / US7 (Phase 9)**: all can start after Phase 2; independent of each other (different files/tables).
- **US8 (Phase 10)**: depends on US1–US7 (engine transfers all families); per-story aggregation slices inside Phases 3–9 keep risk off a single big-bang.
- **Polish (Phase 11)**: after all stories (T062 E2E needs the whole column set).

### Within Each Story

Tests first (RED), then models/serializers (already schema-expanded in Phase 2) → services/validation → aggregation slice → endpoints/UI → localized strings → GREEN verification.

### Parallel Opportunities

- Foundational T003, T005, T007, T010 run in parallel (different apps/files).
- Entire story phases US1↔US2↔US3↔US4↔US5↔US6↔US7 can run in parallel once Phase 2 completes (different tables; UI files distinct per section).
- Test tasks inside a story marked [P] run together.

---

## Implementation Strategy

### MVP First (US1 only)

1. Phase 1 + Phase 2 → foundation.
2. Phase 3 (US1) → activity contract appears in summary with provenance.
3. **STOP and validate** with T012/T013 GREEN + a manual Buildings→summary check.

### Incremental Delivery

US2 → labor totals + catalog; US3 → machinery table; US4 → receipts + reconciliation; US5/US6/US7 → remaining P2 families; US8 → engine guarantees across all; Phase 11 → parity/docs/E2E. Each increment leaves the summary more faithful without breaking prior ones (rebuild fingerprint safeguards existing sections).

---

## Notes

- Every test task: confirm RED before implementing (SC-010).
- Section contracts NEVER import from or depend on the retired `/sub-reports` route; all UI lives on Specialty Units panels.
- The sample workbook stays a read-only structural reference; no import tasks exist anywhere in this list.
- Commit after each task or logical group; stop at checkpoints to validate the story independently.

## Phase 12: Convergence

- [ ] T065 CRITICAL: Create and run `apps/web/e2e/tests/daily-sections-aggregation.spec.ts` with the six required bilingual unit-to-summary scenarios (including rejection/correction, provenance, machinery dedupe, receipts-only details, and structured order) per Constitution III and VI, SC-001, and T062 (missing)
- [X] T066 CRITICAL: Establish an isolated PostgreSQL test database, run the final-tree TypeScript, migration, and feature backend suites, then update `specs/033-daily-sections-grid/verification-report.md` with exact results and service/browser boundaries per Constitution VI and T060-T061 (partial)
- [X] T067 Replace the generic concrete editor and abbreviated summary table with full contract fields, sampling/test-information controls, and the read-only QC link; cover the complete unit-to-summary flow per FR-025, FR-026, FR-027, and US5/AC1 (partial)
- [X] T068 Replace the lossy generic narrative UI and legacy-note summary rendering with localized, full-contract structured editors and ordered read-only summary rows for general activities, issues/barriers, visits, and HSE incidents; include barrier owner/due date, HSE action/severity/notification state, source correction navigation, and regression coverage per FR-028 through FR-032, FR-041, FR-045, and US6 (partial)
- [X] T069 Wire activity-image upload feedback and the authorized per-section count/link payload through the daily-summary API and `AttachmentCountLink`, with no gallery and explicit MinIO boundary tests, per FR-033 through FR-036 and US7 (missing)
