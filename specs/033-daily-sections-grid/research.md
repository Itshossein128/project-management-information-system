# Phase 0 Research: Specialty Unit Daily Sections and Structured Aggregation

**Feature**: 033-daily-sections-grid | **Date**: 2026-10-23
**Inputs**: [spec.md](./spec.md), `reports_gaps/02/GAP-SPEC-02-DAILY-SECTIONS-GRID.md`, `reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md`, current contracts in `sub_reports`, `field_reports`, `inventory`, `project_templates`, `risk`, `resources`.

Every unknown below is resolved with a decision, rationale, and rejected alternatives. No `NEEDS CLARIFICATION` markers remain.

## R1. Where does the labor-title catalog live, and how do the conflicting counts (34/32, 33/32, 32/36) resolve?

**Decision**: A versioned, per-project labor-title catalog owned by the project-template configuration family (draft-editable on the template; immutable per-title snapshot rows inside the effective-dated `ProjectReportingConfiguration` activation, exactly like required units in 032). Each catalog version holds: title (stable code + translatable label), category (indirect/direct), display order, project-specific aliases, active/retired status, and a migration provenance note. The existing legacy lists in `field_reports/migrations/0010_shiraz_labor_titles.py` (33 indirect / 32 direct) and `0002_seed_labor_titles.py` seed the first default version per project; SPEC-02's 34/32 and the sample workbook's 32/36 are recorded as historical evidence rows in version notes, never as hard-coded constants.

**Rationale**: The spec (FR-010/FR-011) explicitly forbids hard-coding any of the three counts and requires legacy-title migration, per-project titles, display order, and history preservation. The 032 activation-pattern is proven, immutable, effective-dated, and already drives completeness; extending it avoids inventing a second configuration mechanism.

**Alternatives considered**:
- Hard-code one count set as universal truth — forbidden by FR-010 and brittle across projects.
- A single global catalog without project versions — loses project-specific titles and per-project ordering.
- Storage inside field_reports as ad-hoc JSON — loses constraint checking, effective dating, and shared use by templates/aggregation/UI.

## R2. Which man-hours rule is "the project-approved rule"?

**Decision**: The rule is a code + parameter set stored on the reporting configuration (e.g. `man_hours_rule_code` defaulting to `standard_shift_plus_overtime`: `present_count × project standard_shift_hours + overtime_person_hours` per title-row). A small registry of allowed rule codes is fixed in code (each with a pure, capped-hours-aware function); projects pick one via their template. The default formula is locked in by contract tests during implementation against the legacy evidence (present Nokia-headcount shift hours plus per-overtime person-hours); the rule stays reproducible and identical for identical inputs.

**Rationale**: "MUST be reproducible using the project-approved rule" (FR-008) requires the rule to be explicit, versioned, and per-project — not implicit in aggregation code. The 032 configuration snapshot already provides versioned effective-dating at no extra cost.

**Alternatives considered**: Hard-code one formula — violates the project-configurable requirement and the spec's anti-universal-truth stance for project-specific standards. Free-form stored expressions — unsafe (injectable logic) and untestable.

## R3. Executed-activity contract: crew vs contractor, headcount, cross-project checks, and shift

**Decision**: Extend `DisciplineSubReportActivity` in place:
- `contractor_ref` FK to the project's `projects.Stakeholder` (contractor-role stakeholder) is required and project-verified; `crew_name` stays a separate free field and is never exported into a contractor column.
- Crew composition keeps `foreman_count`/`worker_count` and exposes an aggregated `headcount` computed as the sum; the derived activity row carries headcount explicitly.
- Add `parcel`; keep `block`, `floor`, `zone`(location), `quantity`, `unit`, `activity_description`, `activity_ref` (WBS).
- `activity_ref` MUST reference an approved/active WBS activity belonging to the same project; contractor_ref MUST belong to the same project; otherwise the row is rejected (permission/validation error).
- When provided, `quantity > 0` (zero and negative rejected); absent quantity stays absent (never zero-filled).
- `shift` accepts only the project's recognized shift vocabulary at save time; unrecognized values are rejected (never silently remapped). The legacy aggregation-side `_normalize_shift` silent fallback becomes explicit: only listed synonyms map; anything else is rejected upstream.

**Rationale**: Directly implements FR-001..FR-005 and closes the gap-report finding that crew names were archived as subcontractor names and unknown shifts silently became shift 1.

**Alternatives considered**: Inserting one generic "headcount" integer replacing foreman/worker detail — loses composition evidence needed by the sample-style columns. Keeping silent normalization — forbidden by FR-005.

## R4. Machinery: section model, five-status derivation, identity dedupe, vocabulary, 24-hour rule

**Decision**:
- New unit-report child row `DisciplineSubReportMachinery`: `equipment_type` (required) or optional stable `equipment_ref` (registered equipment identity), the five daily counts (`total`, `active`, `ready`, `inactive`, `under_repair`), optional `operating_hours`, `stoppage_hours`, `repair_hours`, and `stoppage_reason_code`.
  Rows carry either type-level status counts or per-item data; per-item rows sum consistently into their type when both styles are mixed (validated at submission).
- Stable identity = explicit `equipment_ref` (project-scoped registered equipment); dedupe applies only where identity is declared — per identity across the day at aggregation, and per-row when only a type is given.
- Time rule: `operating + stoppage + repair ≤ 24` per equipment item per day; stoppage > 0 requires `stoppage_reason_code`; codes come from the configuration's controlled, translatable vocabulary (`breakdown`, `lack_of_fuel`, `weather`, `no_operator`, `site_obstruction` as seed defaults, project-extensible); invalid/outside-vocabulary values are rejected.
- Derived projection: new `DailyReportMachineryRow` child rows (per equipment item or type) with the five-status columns preserved and summed to per-type table rows; provenance via `DailyReportDerivedSource` (`derived_kind='machinery'`).

**Rationale**: closes the finding that one of the four main daily tables was never produced; the dedicated derived table avoids overloading the legacy per-item operational `DailyReportEquipment` (whose status field is a single value and whose semantics are a raw-entry log, not a status grid). Stoppage vocabulary rides the same configuration snapshot as required units and the labor catalog.

**Alternatives considered**: Reusing `DailyReportEquipment` as the five-status grid — its fields/semantics do not fit (single status, ownership/rate/cost fields, no five-column assumption), and overloading it would be a high-integrity risk. Storing statuses as JSON — loses row-level provenance and constrainable validity.

## R5. Materials: receipt vs consumption semantics, receipt-only main table, document-anchored reconciliation

**Decision**: Extend `DisciplineSubReportMaterial` in place:
- Add `transaction_type` (`receipt` / `consumption`), keep `quantity`, add `material_ref` (project `resources.Material`), `consumption_location`, `supplier`, and `warehouse_document_reference` (project-scoped identifier of a specific warehouse receipt/issue document).
- A row is a **real receipt** iff `transaction_type = receipt` AND its `warehouse_document_reference` resolves to an actual warehouse document record of the same project; generic/unclassified rows are never displayed as receipts (FR-021).
- Aggregation: receipt rows appear as received-items rows in the summary main table; consumption rows are excluded from the main table but remain derived, listed in the visible details/drill-down endpoint (FR-020/FR-022).
- Reconciliation rework of `field_reports/services/material_reconciliation.py`: comparison happens against the **specific referenced warehouse document** (its recorded quantity for that material), not against `compute_material_balance` total balance. Resolution policy: resolvable document + equal quantities → `match`; resolvable + differing → `mismatch` (with both quantities reported); missing reference, unresolvable document, or document without usable quantities → `insufficient_data`. Reference and resolution evidence are persisted so the result stays traceable (FR-023/FR-024). The existing global-balance advisory remains only as an explicitly labeled cross-check, never as the reconciliation basis.

**Rationale**: closes the finding that aggregation blindly converted every generic material row into a receipt and that reconciliation compared against total historical balance, both of which misrepresent procurement reality.

**Alternatives considered**: Displaying consumption alongside receipts in the main table — contradicts the controlling prompt/sample output. Keeping the balance-based service as primary — explicitly forbidden by FR-023. Inventing a new "warehouse document" store — unnecessary; project-scoped document references resolve to the existing procurement/warehouse document records (requisition-driven stock documents and similar) selected/identified during implementation; if a concrete document record type is still missing for a reference, the correct outcome is `insufficient_data`, which the spec endorses.

## R6. Concrete: fields, sampling rule, QC linkage

**Decision**: Extend `DisciplineSubReportConcrete` in place with `structural_element`/`location`, `parcel`, `batching_plant` (name or registered plant ref), `truck_delivery_note_number`, `lab_sample_code`, `sampling_state` (`not_sampled`/`sampling_declared`), `test_sheet_count`, and a `qc_inspection` link to `risk.Inspection` (the existing quality-control store already wired to WBS/activity, date, responsible user, and NCR chain). Rules: `volume` > 0 (negative rejected); cross-project references rejected; `sampling_state = sampling_declared` requires `lab_sample_code` + `test_sheet_count` present at submission and creates/links the traceable `risk.Inspection` record at the same transaction; `not_sampled` rows stay fully functional. Derived concrete rows (already exists as a section in the 032 rebuild) extend to the full column set.

**Rationale**: closes the gap-report's missing concrete granularity and the SPEC-02 QC requirement without inventing a parallel QC store; `risk.Inspection` is project-scoped with proven required validation and an existing NCR/corrective-action chain, satisfying Principle V.

**Alternatives considered**: A new QC work table — parallel system, violates minimal-change. Free-text "linked QC" note — violates traceability intention of FR-026.

## R7. General activities, issues/barriers, visits, HSE incidents, and plain notes

**Decision**:
- General activities persist as structured rows end-to-end; replace their current text-encoding transfer with a structured derived child table `DailyReportGeneralActivity` mirroring the unit-row columns.
- Notes keep their existing enum types; a `note_type='other'` record is never auto-promoted to an issue — promotion requires the explicit structured record.
- New structured unit-report child rows: `DisciplineSubReportIssue` (issue or barrier; text, display order, owner user, due date; barrier/issue.kind distinction) and `DisciplineSubReportHseIncident` (severity `minor`/`moderate`/`major`, immediate action text), sourced per unit (security/HSE).
- Visits: `DisciplineSubReportVisit` (text, display order, source unit).
- Derived projection: reuse and extend the existing `DailyReportIncident` legacy child table for issues/barriers/HSE incidents (it already carries `incident_type`, `corrective_action`, `follow_up_owner_user`, `due_date` — mapping cleanly onto barrier owner/due structure; add a nullable `severity` and source provenance); new `DailyReportVisit` derived child; new `DailyReportGeneralActivity` derived child. All derived narrative rows copy structured values; HTML/markup embedded in free text is stripped/washed at the boundary and never treated as structure (FR-041).
- HSE incident creation additionally creates the required `notifications.Notification` (and a follow-up task where the notification system supports one) referencing the incident record (FR-031).

**Rationale**: converts the top two structural-loss findings (preformatted general activities and narrative text blobs) into structured, ordered, provenance-scoped records while reusing the closest existing derived table for the incident family.

**Alternatives considered**: Persisting general activities as preformatted text (status quo) — explicitly forbidden. Mapping all `other` notes to issues (status quo) — explicitly forbidden. A fully separate HSE incident module — parallel system, unnecessary.

## R8. Attachments (activity images)

**Decision**: New `UnitReportAttachment` child rows attached to the unit-report version (with nullable pointers to the related section row kind and id): JPEG/PNG only, ≤ 10 MB, validated at least partially by actual content declaration in addition to filename; mandatory metadata: capture date, work front, related activity row reference, source unit, and file project. Attachments are editable only on draft/rejected states; cross-project file attachment is refused; rendering/access flows resolve only through project-scoped endpoints. Aggregation exposes per-section accessible image counts plus link references; the printable form shows counts/links, not a gallery (per prompt). Storage rides the existing environment-dependent file-storage service (MinIO in full environments).

**Rationale**: satisfies FR-033..FR-036 with explicit rejection rules and project isolation while keeping the printable-form decision explicit.

**Alternatives considered**: Maintaining filenames as the sole type guard — unsafe against renamed executables; free-form image gallery in summary — contradicts the approved boundary.

## R9. Totals, empty/zero/unknown, provenance, and fingerprint extension

**Decision**: All new derived sections extend the existing aggregation pipeline:
- The rebuild fingerprint payload gains machinery, receipt/consumption, structured-narrative, catalog rule/version/vocabulary, and attachment-count inputs; unchanged rebuilds short-circuit on fingerprint equality (existing 032 behavior).
- Derived rows use the existing `DailyReportDerivedSource` (multi-source normalized provenance; no last-source-wins) plus row-level `source_*` fields already on labor/material/activity derived rows where they exist.
- Empty section, actual zero, and unknown value are held distinct by null-preserving fields; derived totals (labor indirect/direct/overall, machinery type sums) compute only from present values and expose which component is empty vs zero vs unknown; missing data never becomes a fabricated zero.
- Legacy `crew_name → subcontractor_name` coercion is removed; crew and contractor values stay in their own columns with separate provenance.
- Project-level overrides and management opinion keep the 032 preserved semantics; the fingerprint continues to exclude/leave them untouched during rebuilds.

**Rationale**: implements FR-037..FR-045 on proven machinery instead of parallel logic.

## R10. Shift vocabulary

**Decision**: The project's recognized shift set is the existing constants (`shift_1`, `shift_2`, `shift_3`); aggregation mapping keeps the small list of accepted synonyms (Persian and English spellings) and rejects everything else (marked unknown if entered; never remapped). Aggregation-derived shift display stays localized (fa/en), while identifiers stay stable.

**Rationale**: FR-005: no silent coercions; also closes the silent-remap finding.

## R11. Detail vs print surface

**Decision**: Detailed specialty sections live in the unit reports; the project summary gains a faithful but bounded presentation (machinery table, receipts-only material table, structured activities/issues/visits/HSE sections, totals, drill-down, attachment counts/links) while the printable/PDF-Excel layout, report numbering, page numbering, header composition, and signatures remain the third feature's scope. No commitment here introduces layout features that the next feature would have to undo.

**Rationale**: respects the feature boundary from the controlling prompt while still delivering every acceptance scenario's data contract.

## Summary of resolved questions

| Unknown | Resolution |
|---|---|
| Labor-count conflict | versioned per-project catalog; historical evidence recorded, no universal truth |
| man-hours rule | per-project rule registry default `standard_shift_plus_overtime` on configuration |
| activity contract gaps | extended child row + contractor/crew separation + strict shift/quantity/WBS/contractor validation |
| machinery section | new type/item child rows → derived derived-table projection; dedupe only on declared identity |
| materials semantics | explicit transaction_type + receipt evidence; documents-anchored reconciliation |
| concrete QC traceability | linkage to `risk.Inspection` existing store |
| narrative flattening | structured unit rows + structured derived tables; other-notes never auto-promoted |
| attachments | content-validated JPEG/PNG ≤10 MB, project-scoped, counts+links on summary |
| aggregate idempotence | existing fingerprint extended to new sections; provenance table reused |

No `NEEDS CLARIFICATION` markers remain; all decisions are grounded in the constitution, the controlling prompt, and the named gaps.
