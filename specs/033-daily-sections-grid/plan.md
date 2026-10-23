# Implementation Plan: Specialty Unit Daily Sections and Structured Aggregation

**Branch**: `033-daily-sections-grid` (Spec Kit logical branch; actual Git checkout remains `develop`) | **Date**: 2026-10-23 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/033-daily-sections-grid/spec.md`
**Feature Directory**: `specs/033-daily-sections-grid`
**Status**: Phase 0 research and Phase 1 design complete. This invocation changes design artifacts only; it does not create `tasks.md`, migrations, application code, or test results.

## Summary

Give the six canonical Specialty Units the complete section contracts for their daily reports and make the project daily report a faithful, read-only aggregation of them — without fabrication, premature flattening, or provenance loss. Unit reports (the 032 `DisciplineSubReport` container) gain full executed-activity rows (project WBS activity, shift, contractor, headcount, parcel/block/floor, positive quantity), project-configurable labor catalogs with versioned titles and rule-based man-hours, a machinery status section deriving the five daily statuses without double counting, warehouse material receipts versus consumption with receipt-only main-table display and document-anchored reconciliation, concrete pours linked to the existing quality-control store when sampling is declared, structured general activities/issues/barriers/visits/HSE incidents (with owner, due date, severity, immediate action, and required notifications), and validated activity images. The 032 aggregation engine extends from five rebuilt sections to all section families while staying atomic, idempotent, provenance-complete, override-preserving, and correctable only at the source unit. Final page design, report numbering, headers, signatures, and printable/PDF-Excel output remain the third feature's scope.

## Technical Context

**Language/Version**: Python 3.12 runtime with pinned Django 4.2.11 backend; TypeScript 5.9, React 19, React Router 7.12, Vite 7 frontend

**Primary Dependencies**: Django REST Framework 3.17, PostgreSQL via psycopg 3, Redis cache, drf-spectacular, TanStack Query 5, i18next/react-i18next, existing `sub_reports`, `inventory`, `project_templates`, `field_reports`, `risk` (Inspection/NCR quality store), `resources` (material master + balances), `notifications`, `permissions`, and `projects` (WBS activities, Stakeholder contractors) apps

**Storage**: PostgreSQL. Extend the 032 unit-report child-row tables in place (activities, labor, materials, concrete, general activities, notes) and add child rows for machinery, structured issues/visits/HSE incidents, and attachments; add versioned labor-title catalog, man-hours rule, and stoppage vocabulary to the project-template/reporting-configuration configuration family; add derived child rows + extend `DailyReportDerivedSource` provenance for every new derived section. Redis remains required for normal API behavior but is not a source of record.

**Testing**: pytest/pytest-django against PostgreSQL (test-first RED→GREEN per acceptance scenario), PostgreSQL concurrency tests for rebuild atomicity, frontend typecheck (documented unrelated baseline retained), Playwright real-stack bilingual E2E for the unit→summary path. File-upload flows depend on MinIO (Docker-only locally) and their verification boundaries are stated explicitly.

**Target Platform**: Linux-hosted Django API and bilingual responsive web application for desktop/tablet/mobile operational use

**Project Type**: pnpm monorepo with `apps/api` and `apps/web`; API/UI coupling only through documented contracts

**Performance Goals**: One synchronous rebuild of a full project day (six units, all sections, hundreds of source rows) stays within the 032 budget (≈2 s target); catalog and vocabulary lookups are cached per effective configuration; drill-down provenance queries use the existing `(daily_report, derived_kind)` index; unchanged rebuilds short-circuit on fingerprint equality

**Constraints**: No Django upgrade; PostgreSQL and Redis required; Duck-typed optional services (RabbitMQ, MinIO) named in verification; server-side project isolation for every new identifier (WBS activity, contractor, equipment, concrete reference, warehouse document, attachment); no re-introduction of `/sub-reports`; derive-only summary editing; empty/zero/unknown remain distinct; catalog counts never hard-coded (34/32, 33/32, 32/36 are seed evidence only); stoppage reasons from a controlled translatable vocabulary; persistent overrides survive rebuild; Persian/English parity; structured narrative sections never stored as formatted text

**Scale/Scope**: Six canonical units; one current unit-report version per project/date/unit with unbounded versions; one current full-shift project summary per project/date; per-project versioned labor catalogs; per-project day's sections across seven families (activities, labor, machinery, materials, concrete, narrative/structured, attachments) with complete row-level and multi-source provenance

## Constitution Check

*GATE: evaluated before research and re-evaluated after Phase 1 design.*

Pre-research: **PASS**. Post-design: **PASS**. No unresolved clarification or unjustified constitutional violation remains.

| Principle / gate | Result | Design evidence |
|---|---|---|
| **I — Authorization and isolation** | PASS | All new section CRUD, catalog administration, reconciliation, attachments, and provenance drill-down resolve through authorized project scope; cross-project WBS/contractor/equipment/document/image references are refused server-side; image and document access re-check project membership rather than trusting URLs. |
| **II — Data integrity and consistency** | PASS | Child tables of the 032 unit-report container evolve in place via additive migrations with backfill-safe nullability; every new derived section writes rows + `DailyReportDerivedSource` entries inside the existing atomic rebuild; the shared fingerprint covers new sections so idempotency tests stay truthful; migration of legacy titles preserves history per versioned catalog. |
| **III — Bilingual/locale-correct UX** | PASS | Stable identifiers (section keys, transaction types, stoppage reasons, sampling states) stay language-independent; all new labels, validation errors, reconciliation statuses, and structured section text are localized fa/en and browser-checked in RTL/LTR. |
| **IV — Explicit, safe business mutations** | PASS | Section edits are mutation-safe only on editable report states; submission blocks (with localized reasons) when a section violates its contract rather than silently dropping rows; HSE incident notification generation is explicit and auditable; reconciliation is advisory and never mutates records; destructive operations stay out of scope. |
| **V — Minimal coherent changes** | PASS | Reuse the 032 unit-report container, child-row pattern, provenance table, fingerprint, and rebuild pipeline; only one new derived narrative table family and one derived machinery table are added where no existing table fits semantics; no parallel report/summary system and no second authoring surface. |
| **VI — Evidence-based verification** | PASS | Plan separates backend pytest, migration checks, concurrency, catalog/reconciliation behavior, typecheck baseline, browser E2E, and explicitly bounds what MinIO-dependent upload tests prove locally. |
| **VII — Accessible practical UX** | PASS | Section editors give immediate localized validation, searchable selects place Add inside the open menu, derived rows are read-only with one-attempt provenance navigation to the source unit row, and totals/statuses use text-plus-color presentation. |

Architecture constraints also pass: Django stays pinned; cross-app behavior goes through documented contracts (risk inspections, resources materials/balances, notifications, projects WBS/stakeholders); PostgreSQL/Redis and unavailable optional services are named; all dependent surfaces (models, migrations, serializers, APIs, UI, tests, documentation) are included in scope.

## Project Structure

### Documentation (this feature)

```text
specs/033-daily-sections-grid/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── unit-report-sections-api.md
│   ├── reporting-configuration-catalog-api.md
│   ├── daily-summary-sections-api.md
│   └── unit-report-and-summary-ui.md
├── spec.md
└── checklists/
    └── requirements.md
```

`tasks.md` is intentionally not created by this command; generate it with `/speckit-tasks` after reviewing these decisions.

### Source Code (repository root; planned touchpoints)

```text
apps/api/core/
├── common/
│   └── reporting_units.py                  # (unchanged canonical units)
├── project_templates/
│   ├── models.py                           # labor-title catalog, man-hours rule, stoppage vocabulary (+ snapshots)
│   ├── serializers.py / services.py / views.py / urls.py
│   ├── migrations/
│   └── tests/test_required_report_units.py # catalog contract tests alongside
├── sub_reports/
│   ├── models.py                           # extended child rows + new machinery/issue/visit/HSE/attachment child rows
│   ├── serializers.py / local services     # section-level validation contracts
│   ├── unit_report_views.py / serializers.py
│   ├── migrations/
│   └── tests/
│       ├── test_section_contracts.py       # new: per-section field+validation contracts
│       ├── test_labor_catalog.py           # new: versions, migration titles, display order
│       ├── test_machinery_contract.py      # new: statuses, hours, vocabulary, 24h rule
│       ├── test_materials_receipt_contract.py  # new: receipt semantics, doc references
│       ├── test_concrete_qc_link.py        # new: sampling→Inspection linkage
│       └── test_structured_narrative.py    # new: issues/visits/HSE structure + notes stays note
├── inventory/
│   └── (activity-record modal fields stay bound to the editable report; no workflow bypass)
└── field_reports/
    ├── models.py                            # derived child rows: machinery daily status, general activity, visit, concrete/HSE severity extensions
    ├── serializers.py / daily_report_views.py ( drill-down, materials reconciliation )
    ├── services/
    │   ├── daily_report_aggregation.py      # extended section rebuild + fingerprint + wash of silent shift fallback
    │   ├── material_reconciliation.py       # specific-warehouse-document comparison
    │   └── (hse notification handler)
    ├── migrations/
    └── tests/
        ├── test_unit_report_aggregation_*.py  # 032 suites extended to new sections
        ├── test_machinery_derivation.py       # new: five statuses, dedupe by identity
        ├── test_receipts_only_summary.py      # new: main table receipts, consumption drill-down
        └── test_structured_transfer.py        # new: narrative sections stay structured + ordered

apps/web/src/
├── app/lib/api/
│   ├── unit-reports.ts                      # section CRUD + validation error shapes
│   ├── reporting-config.ts                   # catalog/vocabulary APIs
│   └── daily-reports.ts                      # sections, drill-down, reconciliation, attachment counts
├── components/
│   ├── department/                          # unit page section editors (activities/labor/machinery/warehouse/concrete/narrative/images)
│   │   ├── unit-daily-report-panel.tsx      # section tabs per canonical unit
│   │   ├── section-*.tsx                    # per-family editors
│   │   └── department-activity-record-modal.tsx  # extended, still report-bound
│   └── daily_reports/summary/
│       ├── DailyReportSummaryView.tsx        # machinery table, receipts-only materials, totals, structured narrative
│       ├── SectionProvenanceDrillDown.tsx    # one-attempt navigation to source unit row
│       └── AttachmentCountLink.tsx           # accessible counts + links
└── app/locales/fa.json / en.json

apps/web/e2e/
├── tests/daily-sections-aggregation.spec.ts  # unit→summary browser path per mandatory scenarios
└── helpers/                                  # section builders for six units
```

**Structure Decision**: Preserve the pnpm monorepo and the 032 architecture. Section contracts live on the existing unit-report container inside `sub_reports` + `inventory` (activity records), configuration catalogs live in `project_templates` (the effective-dated snapshot family), and only derived projection rows live in `field_reports`, extending the existing child-row + provenance + fingerprint pattern. No new product route, workflow, or authoring surface is introduced.

## Phase 0 — Research Outcome

[research.md](./research.md) resolves every technical unknown: labor-title catalog storage and legacy seed evidence; the project-configurable man-hours rule; executed-activity completion, cross-project validation, crew-vs-contractor, and shift handling; machinery section modeling, five-status derivation, equipment identity dedupe, and the stoppage vocabulary; receipt vs consumption semantics, receipt-only display, and specific-warehouse-document reconciliation; concrete fields and the sampling→`risk.Inspection` linkage; structured narrative storage (issues/barriers/visits/HSE + untouched general notes) and derived projection; attachment validation and cross-project isolation; totals, provenance, empty/zero/unknown treatment, and fingerprint extension. No unresolved clarification markers remain.

## Phase 1 — Design Outcome

- [data-model.md](./data-model.md) — extended/derived/child entities, validation rules, uniqueness, lifecycle, and aggregate invariants per section family.
- [contracts/unit-report-sections-api.md](./contracts/unit-report-sections-api.md) — section CRUD on unit-report versions, validation/error codes, permissions, attachment rules.
- [contracts/reporting-configuration-catalog-api.md](./contracts/reporting-configuration-catalog-api.md) — labor-title catalog versions, man-hours rule, stoppage vocabulary, template preview/activation.
- [contracts/daily-summary-sections-api.md](./contracts/daily-summary-sections-api.md) — derived section shapes, machinery five-status table, receipts-only materials, document-anchored reconciliation, totals + provenance drill-down, idempotency guarantees.
- [contracts/unit-report-and-summary-ui.md](./contracts/unit-report-and-summary-ui.md) — unit-page section editors, summary display + drill-down model, accessibility and bilingual requirements.
- [quickstart.md](./quickstart.md) — runnable RED/GREEN validation guide across section contracts, aggregation idempotency, reconciliation, browser E2E, and stated service-availability boundaries.

Post-design constitution re-check remains **PASS** (see table above): contracts close the flattening, provenance-loss, receipt ambiguity, uncontrolled vocabulary, missing machinery series, and attachment-isolation gaps while reusing 032 foundations and adding no parallel product systems.

## Implementation Strategy and Ordering

1. **RED — section contracts first**: failing pytest for every per-section field/validation rule (completed-quantity positivity, non-negative counts, 24-hour machinery limit, stoppage-reason vocabulary, positive concrete volume, sampling completeness, attachment type/size/cross-project rules, structural narrative typing, unknown-shift rejection) mapped to the spec's mandatory scenarios.
2. **Expand schema additively**: labor-title catalog + man-hours rule + stoppage vocabulary in `project_templates` (draft-editable, activated snapshots); new unit-report child rows (machinery, structured issues/visits/HSE, attachments) and in-place extension of activities/labor/materials/concrete/general-activity child rows; new derived child rows in `field_reports`; all backfill-compatible.
3. **Catalog migration**: seed versioned catalogs from the existing legacy title evidence (01x migration lists as one version, SPEC-02/sample counts recorded as historical evidence), alias-mapped, display-ordered, per project; verify title-history preservation queries.
4. **Section validation services + API**: section serializers/services enforcing contracts at the trusted boundary; submission-level integrity (a submitted report whose rows violate the effective catalog/vocabulary/date rules cannot silently disappear from aggregation).
5. **Aggregation extension**: rebuild all section families from current eligible versions; per-item identity dedupe for machinery; receipts-only main table; structured transfer of general activities/issues/visits/HSE; totals per the project-approved rule; extended fingerprint; wash the silent shift remap; atomicity/idempotency/concurrency tests extended.
6. **Reconciliation rework**: document-anchored comparison replacing global-balance hints; explicit match/mismatch/insufficient statuses with document references preserved.
7. **Frontend**: per-unit section editors on Specialty Units pages (no new route), summary sections + totals + machinery table + drill-down + attachment counts, bilingual/a11y coverage.
8. **GREEN + regression**: run the new suites, the extended 032 aggregation/eligibility/provenance/completeness/idempotency suites, relevant `risk`/`resources`/`inventory` suites, migration forward/reverse/forward, typecheck baseline, and real-stack bilingual Playwright for the end-to-end unit→summary path.

## Verification Boundaries

- Focused pytest proves model/service/serializer/API behavior against PostgreSQL, not browser rendering or production scale.
- Migration tests prove additive-schema forward/apply/reverse safety, not real dataset volume.
- The 24-hour rule, catalog versioning, and receipts semantics are proven by enumerated contract tests, not by the sample workbook (which remains a read-only reference only).
- File-upload and image-validation tests requiring MinIO are bounded by the AGENTS.md local-environment rule: they document what local runs prove; browser E2E exercises the non-MinIO paths locally and flags the upload boundary in the report.
- The `risk.Inspection` linkage proves traceability, not a new QC workflow; NCR/CA generation policies beyond the required link are out of scope.
- Usability criteria requiring representative-user observation cannot be claimed from automation.

## Complexity Tracking

> None. The only new relations (catalog/vocabulary/rule configuration, machinery + structured narrative + attachment child rows, derived projection rows) are required by the corrected section contracts; they extend the 032 foundations rather than introducing parallel product systems.
