# Research: Specialty Unit Reporting Source of Truth

**Feature**: `032-unit-report-source-truth`  
**Date**: 2026-10-22

This research treats `specs/028-auto-daily-report-summary/` as historical context. Its materialized project-day summary, submitted/approved eligibility, read-only derived rows, and override preservation remain useful. Its standalone `/sub-reports` authoring surface, legacy discipline taxonomy, hard-coded three-discipline completeness, and single-source provenance are superseded.

## Decision 1 — One neutral canonical unit registry

**Decision**: Define a neutral shared `SpecialtyUnit` vocabulary with exactly `buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, and `security`. Backend models, validation, project templates, aggregation, and API metadata use it. Existing `inventory.Department` becomes a compatibility import/alias, and the frontend `BUSINESS_DEPARTMENTS` registry is contract-tested against the API vocabulary.

**Rationale**: The same six identifiers already drive the real unit pages, but the backend enum currently lives in the inventory domain while legacy reports use a conflicting six-value `Discipline` enum. A neutral vocabulary avoids importing an inventory model into reporting and prevents a third taxonomy.

**Alternatives considered**:

- Keep `Discipline` — rejected because it cannot represent Machinery, Warehouse, or Security/HSE and introduces Plumbing/HVAC/Finishing as parallel units.
- Use mutable organization units — rejected because organizational structure and the fixed reporting taxonomy have different identity and lifecycle rules.
- Maintain separate frontend/backend registries without a contract test — rejected because the present drift originated that way.

## Decision 2 — Evolve the existing specialty report in place

**Decision**: Evolve the existing `DisciplineSubReport` record and table into the internal, versioned unit-report container. Add canonical `unit`, lineage/version/current markers, rejection actor/time, and history relations while preserving the existing UUID, children, and project-summary link. Expose it through new unit-report naming and contracts; retain the legacy `discipline` field only for migration evidence and rollback during a compatibility window.

**Rationale**: The current record already owns workflow state, audit fields, nested source rows, and links to project daily summaries. Creating a parallel `UnitDailyReport` table would require copying every relationship and would place stable identifiers at risk.

**Alternatives considered**:

- Create a second unit-report table — rejected as duplicate storage and an avoidable high-risk migration.
- Rename and rewrite every table immediately — rejected because the product contract needs canonical naming now, while physical cleanup can wait until compatibility evidence is complete.
- Keep the current record unchanged and translate only in the UI — rejected because uniqueness, completeness, provenance, and migrations require canonical unit identity at the trusted data boundary.

**Retirement milestone**: remove the legacy `discipline` field, old `/sub-reports` server routes, compatibility serializers, and compatibility query paths no later than completion of the third feature in this series, after migration accounting, rollback rehearsal, and all consumers use canonical unit contracts.

## Decision 3 — Unit pages own the report and all mutable day rows

**Decision**: Add a shared `UnitDailyReportPanel` to the existing `DepartmentPage`. The route-derived unit and selected date open or create the current unit-report container. Existing `DepartmentActivityRecord` rows become report-owned through a parent report reference; create, update, delete, and import operations are permitted only when that parent is the current draft or rejected version and project/unit permissions pass. Legacy nested contribution rows remain attached to the evolved report and readable during migration. The standalone specialty form/page is removed.

**Rationale**: The six existing unit routes are the correct product surface. Leaving the activity log independently mutable would preserve a parallel daily-data workflow; aggregating it without a report parent would bypass workflow state and version history. Parent ownership makes the unit report—not either child table—the source-of-truth boundary.

**Alternatives considered**:

- Silently aggregate all existing activity-log rows — rejected because those rows have no submit/approve state or report version.
- Keep the activity log independently writable beside a unit report — rejected because it creates two entry paths for the same operational day data.
- Build six separate report pages — rejected because it duplicates routing, labels, and workflow code.

**Scope boundary**: this feature establishes ownership, lifecycle, and provenance for existing rows. It does not define the final field contracts or calculations for labor, equipment, warehouse materials, concrete, issues, visits, or other specialty sections; those belong to the next feature.

## Decision 4 — Explicit versions and immutable workflow events

**Decision**: A report lineage contains numbered versions. Exactly one version is current for each project/date/unit. Draft and rejected current versions are editable. Submitted and approved versions are immutable. Correcting an approved report clones its report-owned content into a new current draft and preserves the approved version. Every transition creates an append-only status event containing previous/new state, actor, time, and reason where applicable.

**Rationale**: Current status columns do not preserve resubmission history, and nested updates presently delete/recreate all rows, changing source identities. Explicit versions and ID-aware child updates preserve contractual evidence and stable provenance.

**Alternatives considered**:

- Soft-delete superseded versions — rejected because supersession is valid history, not deletion.
- Rely only on generic request audit logs — rejected because they do not guarantee domain transition semantics.
- Overwrite the approved record during correction — rejected because it destroys the evidence previously approved.

## Decision 5 — Reuse project report permissions and enforce SoD

**Decision**: Reuse the existing project codenames: `view_reports` for current/history/source reads, `edit_reports` for open/create/edit/correct/delete/submit, and `approve_reports` for approve/reject. Every action also requires active membership and project/unit-scoped object resolution. Approval applies the existing stable SoD error contract and, except for the existing superuser break-glass rule, refuses an actor who prepared or submitted the current version.

**Rationale**: The controlling specification requires corresponding project permissions but does not introduce a new per-unit assignment model. Adding new codenames or assignment administration would unnecessarily expand product scope. Current project permissions are adequate, but the current specialty service does not enforce self-approval separation and the activity-log endpoint uses unrelated global/HR rules.

**Alternatives considered**:

- Add separate submit/reject codenames — rejected for this feature because the approved scope does not require a new role taxonomy.
- Trust an editable unit in request data — rejected because it permits scope confusion; the canonical unit is bound by the URL and verified against the report.
- Hide forbidden controls only in the UI — rejected because the server is the authorization boundary.

## Decision 6 — Effective-dated, immutable reporting configuration from project templates

**Decision**: Project templates declare required canonical units using normalized child rows. Activating a template for a project creates an immutable, effective-dated project reporting configuration and snapshots those required units. Date resolution selects exactly one configuration effective on the report date and returns its identity with completeness metadata. With no effective configuration, the state is `configuration_incomplete`; the system never falls back to a hard-coded unit list.

**Rationale**: Current templates contain WBS and role definitions only, are mutable, and leave no project/template assignment after application. Reading a live mutable template would retroactively change historical completeness. A dated immutable snapshot preserves what was required on that date.

**Alternatives considered**:

- Store a JSON list only on the reusable template — rejected for weak validation and historical drift.
- Put one current template FK on Project — rejected because it cannot answer historical dates.
- Backfill every existing project with three or six required units — rejected because required units cannot be inferred truthfully. Existing projects remain configuration-incomplete until explicitly activated.

## Decision 7 — Normalized, many-source provenance

**Decision**: Add a normalized derived-source relation that identifies the project summary, derived section/row, source report/version, canonical unit snapshot, source row kind, and source row identifier. Union rows have one source reference; grouped totals have one reference per contributing row in deterministic order. Serialized summary rows expose the complete provenance list and whether the current viewer may open each source.

**Rationale**: Current derived rows store only one report and legacy discipline. Labor totals overwrite that reference as each source is processed, producing last-source-wins provenance. Normalized rows support uniqueness, reverse lookup, authorization, and multi-source totals.

**Alternatives considered**:

- Keep a single source FK — rejected because totals are many-to-many by definition.
- Store the canonical source list only as JSON — rejected as the authoritative store because it lacks referential and duplicate guarantees; JSON may be used only as the response projection.
- Duplicate a total once per source — rejected because each duplicate would no longer represent the actual combined value.

## Decision 8 — One serialized, deterministic rebuild transaction

**Decision**: Unit transitions and summary rebuilds use a consistent lock order: Project, current unit-report version(s), then current full-shift DailyReport. Rebuild inputs are only current, non-deleted, submitted/approved reports for the exact project/date. Inputs and source rows are stably ordered. Derived items use deterministic derivation keys and are upserted; obsolete keys and provenance are removed. Rebuild updates only derived and aggregation-owned fields, preserving summary-owned overrides and management opinion.

**Rationale**: The existing ensure path locks Project, but direct rebuild does not lock the summary and deletes/recreates rows. Concurrent calls can interleave. Deterministic keys also allow three unchanged rebuilds to produce identical logical rows and provenance rather than merely the same summary shell.

**Alternatives considered**:

- Keep delete/recreate under `transaction.atomic` only — rejected because an atomic block without row locks does not prevent concurrent stale reads or interleaving rebuilds.
- Rebuild asynchronously only — rejected because submit/open must immediately reflect current eligible data.
- Last-writer-wins — rejected because it can lose provenance and summary-owned updates.

## Decision 9 — Expand, backfill, validate, then contract

**Decision**: Use staged migrations:

1. Add nullable canonical/version/configuration/provenance fields plus permanent trace and quarantine structures.
2. Rehearse and inventory all legacy report rows, child identifiers, links, states, and activity-log groups.
3. Map `civil`/`finishing` to Buildings; `mechanical`/`plumbing`/`hvac` to Mechanical; `electrical` to Electrical. Do not infer Machinery, Warehouse, or Security from legacy discipline values.
4. Preserve every legacy report as a version. For collisions, order by business change time then stable UUID and mark only the deterministic winner current. Preserve collision losers as non-current history.
5. Attach canonical unit-page activity records to the applicable version or create a traced draft lineage when no report exists. Exact cross-source duplicates are represented by aliases in the migration trace and contribute only once; non-identical records remain distinct.
6. Quarantine malformed/unknown values while retaining authorized read access.
7. Validate 100% accounting and link integrity; only then replace legacy uniqueness with canonical current/version constraints.
8. Keep original fields and permanent trace through the rollback window; perform destructive cleanup only at the retirement milestone.

**Rationale**: Many legacy disciplines map to one canonical unit, so an enum rewrite would violate uniqueness or silently discard records. Existing stable UUIDs make in-place versioning feasible.

**Alternatives considered**:

- Add constraints before normalization — rejected because existing collisions would fail or be lost.
- Delete exact duplicates — rejected because original identifiers must remain traceable.
- Reverse-map new Machinery/Warehouse/Security reports during rollback — rejected because the legacy taxonomy has no truthful values for them.

**Rollback boundary**: before canonical-only reports are accepted, rollback can reconstruct legacy categories and links from the trace. After new categories exist, rollback requires a verified backup restore plus controlled replay/export; a reverse data migration alone cannot be truthful.

## Decision 10 — New canonical API; legacy route unavailable to clients

**Decision**: Introduce project-scoped `unit-reports` endpoints for current-by-unit/date, history, detail/update/delete, submit, approve, reject, and correction. Unit identity is route/query context, not editable payload. Responses include audit metadata and server-authoritative capabilities. Remove frontend route registration, navigation, CTAs, translations, helpers, and product tests for `/sub-reports`; direct browser navigation uses the standard not-found boundary. Legacy server internals are not registered as a second client API after cutover.

**Rationale**: Extending the current untyped HR helper and legacy URL would keep obsolete product language and make accidental reuse likely. Capability fields improve UX without weakening server authorization.

**Alternatives considered**:

- Redirect `/sub-reports` to a unit — rejected because no arbitrary unit is correct and the specification requires a not-found result.
- Keep both APIs during an open-ended deprecation — rejected because it preserves parallel workflow risk.

## Decision 11 — TDD and verification order

**Decision**: Implement through failing tests in this order: migration accounting/rollback; schema constraints; effective template resolution; workflow/versioning; permissions/SoD; aggregation eligibility/provenance/completeness; PostgreSQL concurrency; typed frontend behavior; real-stack bilingual browser acceptance. Existing summary isolation and metadata-preservation tests remain regression anchors.

**Rationale**: Migration and invariants are the highest-risk foundations. Browser tests cannot prove trusted authorization, and focused tests alone cannot prove the complete workflow.

**Alternatives considered**:

- Start with UI relocation — rejected because it would sit on the wrong taxonomy and unsafe workflow.
- Treat typecheck as delivery proof — rejected by the constitution and by the repository’s unrelated baseline TypeScript errors.
- Rely only on fixture migrations — rejected because only a sanitized dataset rehearsal can establish real accounting and rollback confidence.

## Resolved Unknowns

- **Canonical identifiers**: the six unit-page slugs listed in Decision 1.
- **Existing model reuse**: evolve `DisciplineSubReport` in place; do not add a parallel report store.
- **Completeness source**: immutable, effective-dated project reporting configuration snapshotted from a project template.
- **Missing template behavior**: explicit `configuration_incomplete`; never report complete.
- **Permission mapping**: existing view/edit/approve report permissions plus active project membership, URL/object unit consistency, and SoD.
- **Provenance representation**: normalized many-source rows serialized as ordered lists.
- **Concurrency strategy**: consistent row-lock order and deterministic upsert.
- **Legacy URL behavior**: standard not-found, no redirect and no data request.
- **Detailed specialty section contracts**: deferred to feature two, as required by the specification.
