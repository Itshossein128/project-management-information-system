# Implementation Plan: Specialty Unit Reporting Source of Truth

**Branch**: `032-unit-report-source-truth` (Spec Kit logical branch; actual Git checkout remains `develop`) | **Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/032-unit-report-source-truth/spec.md`  
**Feature Directory**: `specs/032-unit-report-source-truth`  
**Status**: Phase 0 research and Phase 1 design complete. This invocation changes design artifacts only; it does not create `tasks.md`, migrations, application code, or test results.

## Summary

Move the complete lifecycle of specialty-unit daily reports onto the six existing Specialty Units pages and remove the standalone `/sub-reports` product path. Evolve the existing `DisciplineSubReport` storage in place into a canonical, versioned unit-report container so UUIDs, child rows, and project-summary links survive. Bind mutable unit-page activity rows to that container, enforce project/unit permissions and segregation of duties, derive completeness from immutable effective-dated template activations, and rebuild the existing materialized DailyReport from only current submitted/approved versions. Replace last-source provenance with normalized source-row sets and execute migration as expand → backfill/trace/quarantine → validate → constrain, with rollback rehearsal before cleanup.

## Technical Context

**Language/Version**: Python 3.12 runtime with pinned Django 4.2.11 backend; TypeScript 5.9, React 19, React Router 7.12, Vite 7 frontend

**Primary Dependencies**: Django REST Framework 3.17, PostgreSQL via psycopg 3, Redis cache, drf-spectacular, TanStack Query 5, i18next/react-i18next, existing `sub_reports`, `inventory`, `project_templates`, `field_reports`, `permissions`, and `master_data` apps

**Storage**: PostgreSQL. Retain existing specialty-report, activity-record, and DailyReport tables; add canonical/version/history/configuration/provenance/migration-trace relations and staged constraints. Redis remains required for normal API behavior but is not a source of record.

**Testing**: pytest/pytest-django against PostgreSQL; `MigrationExecutor` forward/reverse tests; PostgreSQL `TransactionTestCase` concurrency tests; frontend typecheck; Playwright real-stack bilingual acceptance. Record the existing unrelated TypeScript baseline separately.

**Target Platform**: Linux-hosted Django API and bilingual responsive web application for desktop/tablet/mobile operational use

**Project Type**: pnpm monorepo with `apps/api` and `apps/web`; API/UI coupling only through documented contracts

**Performance Goals**: Current report open and one project-day synchronous rebuild target under 2 seconds for a typical day (six units and hundreds of source rows); date/unit queries and provenance lookups use indexed project/date/unit/current keys; unchanged rebuilds avoid unnecessary writes

**Constraints**: No Django upgrade; PostgreSQL and Redis required; server-side project isolation; no parallel authoring path; no hard-coded three-unit fallback; preserve all valid legacy IDs/history/links; source rows retain identity; summary overrides survive rebuild; deterministic lock order; Persian/English parity; detailed specialty-section contracts and final printable summary remain out of scope

**Scale/Scope**: Six canonical units; at most one current version per project/date/unit plus unbounded historical versions; one current full-shift project summary per project/date; many project-template activations over time; complete provenance for every derived row and multi-source total

## Constitution Check

*GATE: evaluated before research and re-evaluated after Phase 1 design.*

Pre-research: **PASS**. Post-design: **PASS**. No unresolved clarification or unjustified constitutional violation remains.

| Principle / gate | Result | Design evidence |
|---|---|---|
| **I — Authorization and isolation** | PASS | Every lookup is nested in project/unit scope; existing project report permissions are enforced server-side; provenance navigation rechecks source access; SoD runs in the locked service, not the UI. |
| **II — Data integrity and consistency** | PASS | Existing UUIDs/tables evolve in place; migration traces every record, normalizes collisions before constraints, preserves links, and rehearses rollback; API/UI/template/aggregation/provenance surfaces share canonical units. |
| **III — Bilingual/locale-correct UX** | PASS | Stable identifiers stay language-independent; all unit/status/audit/error/completeness labels require fa/en coverage and Jalali-aware date interaction is browser-tested in RTL/LTR. |
| **IV — Safe business mutations** | PASS | Explicit state machine, immutable approved history, required rejection reason, server capabilities plus enforcement, lock order, backdated-template preview/confirmation, quarantine, backup/restore rollback boundary. |
| **V — Minimal coherent change** | PASS | Reuse existing unit pages, specialty-report storage, project template system, report permissions, and materialized DailyReport; do not create a parallel report or summary model. |
| **VI — Evidence-based verification** | PASS | Plan separates migration, backend, concurrency, frontend, browser, dataset rehearsal, and usability evidence; TDD begins with failing behavioral tests and reruns on the final tree. |
| **VII — Accessible practical UX** | PASS | Shared panel, semantic audit/history, keyboard-operable actions/dialogs, text-plus-color status, localized actionable errors, and read-only historical/derived content. |

Architecture constraints also pass: Django stays pinned; cross-app behavior is contract-driven; PostgreSQL/Redis and unavailable optional services are named; changed models, migrations, APIs, UI, imports, exports, tests, and documentation are included in scope.

## Project Structure

### Documentation (this feature)

```text
specs/032-unit-report-source-truth/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── unit-report-api.md
│   ├── report-template-api.md
│   ├── daily-summary-api.md
│   └── unit-report-ui.md
├── spec.md
└── checklists/
    └── requirements.md
```

`tasks.md` is intentionally not created by this command; generate it with `/speckit-tasks` after reviewing these decisions.

### Source Code (repository root; planned touchpoints)

```text
apps/api/core/
├── common/
│   └── reporting_units.py                 # neutral six-value SpecialtyUnit vocabulary
├── project_templates/
│   ├── models.py                          # required units + immutable project activations/snapshots
│   ├── serializers.py / services.py / views.py / urls.py
│   ├── migrations/
│   └── tests/test_required_report_units.py
├── sub_reports/
│   ├── models.py                          # in-place canonical unit, versions, events, trace/quarantine
│   ├── services.py                        # locked workflow, correction, ID-aware updates, SoD
│   ├── serializers.py / views.py / urls.py
│   ├── migrations/
│   └── tests/
│       ├── test_unit_report_migrations.py
│       ├── test_unit_report_models.py
│       ├── test_unit_report_workflow.py
│       ├── test_unit_report_permissions.py
│       └── test_unit_report_concurrency.py
├── inventory/
│   ├── models.py                          # canonical enum compatibility + unit_report parent
│   ├── serializers.py / views.py
│   ├── department_activity_io.py          # import bound to editable report
│   ├── migrations/
│   └── tests/                             # no workflow bypass through CRUD/import
└── field_reports/
    ├── models.py                          # reporting config binding, deterministic keys, provenance
    ├── serializers.py
    ├── services/daily_report_aggregation.py
    ├── migrations/
    └── tests/
        ├── test_unit_report_aggregation_eligibility.py
        ├── test_unit_report_provenance.py
        ├── test_unit_report_completeness.py
        └── test_unit_report_rebuild_idempotency.py

apps/web/src/
├── app/
│   ├── lib/api/unit-reports.ts             # typed canonical client; not hr-forms legacy helpers
│   ├── lib/api/daily-reports.ts            # completeness/provenance contract
│   ├── lib/api/templates.ts                # required units/config activations
│   ├── hooks/queries.ts                    # report-bound activity queries/mutations
│   ├── routeVars.ts                        # remove PROJECT_SUB_REPORTS
│   ├── routes/business-setup.routes.ts     # unregister legacy route
│   ├── routes/daily-reports-list.tsx       # no legacy CTA; optional six-unit chooser
│   └── locales/fa.json / en.json
├── components/
│   ├── department/
│   │   ├── department-page.tsx             # host shared UnitDailyReportPanel
│   │   └── unit-daily-report-panel.tsx
│   └── daily_reports/summary/
│       ├── IncompletenessBanner.tsx
│       └── DailyReportSummaryView.tsx       # canonical provenance projection
├── config/
│   ├── business-departments.config.ts      # frontend registry/labels
│   └── project-navigation.config.ts        # remove legacy nav item
└── app/routes/project-sub-reports.tsx       # delete after replacement

apps/web/e2e/
├── tests/unit-report-source-truth.spec.ts
├── tests/daily-report.spec.ts               # author via real unit page
├── tests/decision-tree-*.spec.ts            # legacy route now not-found
└── helpers/

e2e/
├── helpers/registered-routes.ts
└── tests/navigation-routes.spec.ts
```

**Structure Decision**: Preserve the monorepo and extend established domains. `sub_reports` remains the physical compatibility owner during the migration window, but the public contract and frontend use canonical unit-report language. Unit pages host authoring; `field_reports.DailyReport` remains the single project-day summary. A neutral common enum prevents inventory or legacy discipline code from owning the taxonomy.

## Phase 0 — Research Outcome

[research.md](./research.md) resolves every technical unknown:

- canonical unit ownership and legacy mapping;
- in-place model evolution versus a parallel table;
- unit-page/activity-row ownership and elimination of workflow bypasses;
- versions, immutable transition history, project permissions, and SoD;
- effective-dated template snapshots and no-template behavior;
- normalized many-source provenance;
- deterministic locking/rebuild strategy;
- staged migration, permanent trace/quarantine, retirement, and rollback boundary;
- canonical API/UI route retirement and TDD sequence.

No unresolved clarification markers remain.

## Phase 1 — Design Outcome

- [data-model.md](./data-model.md) — canonical entities, constraints, lifecycle, completeness, rebuild, migration, and rollback invariants.
- [contracts/unit-report-api.md](./contracts/unit-report-api.md) — current/open/history/workflow/correction API, capabilities, errors, permissions, and legacy retirement.
- [contracts/report-template-api.md](./contracts/report-template-api.md) — required-unit declarations and immutable project activation.
- [contracts/daily-summary-api.md](./contracts/daily-summary-api.md) — eligible inputs, canonical completeness, multi-source provenance, and rebuild guarantees.
- [contracts/unit-report-ui.md](./contracts/unit-report-ui.md) — unit-page panel, state UX, activity-log transition, route removal, localization, and accessibility.
- [quickstart.md](./quickstart.md) — runnable RED/GREEN, migration, backend, concurrency, frontend, browser, and rehearsal evidence guide.

Post-design constitution re-check remains **PASS** because contracts close the current IDOR/SoD, template-history, last-source provenance, concurrent rebuild, bilingual, and parallel-workflow gaps without introducing a second report system.

## Implementation Strategy and Ordering

1. **RED — migration/invariants first**: add failing MigrationExecutor tests for every legacy mapping, collisions, unknowns, children, links, rollback, and forward reapply; add model constraint tests.
2. **Expand schema**: neutral enum, nullable canonical/version fields, transition history, template required-unit/configuration snapshots, provenance, migration trace/quarantine, and report ownership on activity rows. No destructive constraint yet.
3. **Backfill and validate**: deterministic, resumable mapping; attach activity groups; record aliases/quarantine; assert 100% ID/link accounting. Add canonical/current constraints only after validation.
4. **Domain services/API**: implement locked open/edit/submit/approve/reject/correct/delete services, ID-aware row updates, unit/project permission matrix, SoD, new typed endpoints, and remove legacy endpoint registration.
5. **Aggregation**: current-version eligibility, configuration binding, deterministic derivation keys, normalized provenance, lock order, and override-safe updates.
6. **Frontend cutover**: add shared panel to six unit pages, bind activity mutations to current report, localize/a11y audit/history, remove legacy route/navigation/CTA/helpers, and update completeness/provenance UI.
7. **GREEN and regression**: focused pytest, migration forward/reverse/forward, real PostgreSQL concurrency, relevant existing field-report/inventory/template suites, typecheck baseline comparison, and real-stack bilingual Playwright.
8. **Dataset rehearsal before release**: sanitized snapshot accounting, backup/restore drill, rollback decision point, and proof that no valid report/source/link is unaccounted for. Do not perform destructive cleanup in this feature.

## Verification Boundaries

- Focused pytest proves local model/service/API behavior against PostgreSQL, not browser behavior or production scale.
- Threaded transaction tests prove local PostgreSQL serialization and invariants, not throughput.
- Typecheck is compilation evidence and may retain documented unrelated baseline failures.
- Real-stack Playwright proves seeded local browser/API workflows and locale behavior, not production authorization configuration or migration safety.
- Fixture migration tests prove enumerated cases; only sanitized staging-snapshot rehearsal proves real dataset accounting and operational rollback.
- The 90% first-attempt usability criterion requires representative-user observation and cannot be claimed from automation.
- RabbitMQ, MinIO, file-upload flows, final specialty-section contracts, Excel parity, and printable PDF are outside this feature’s verification claim.

## Complexity Tracking

> None. The new relations are required to preserve immutable versions, effective historical configuration, and many-source provenance; they replace unsafe/hard-coded behavior rather than introducing parallel product systems.
