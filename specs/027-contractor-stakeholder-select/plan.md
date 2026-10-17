# Implementation Plan: Contractor Stakeholder Select

**Branch**: `develop` (actual Git branch; unchanged) | **Date**: 2026-10-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/027-contractor-stakeholder-select/spec.md`  
**Feature Directory**: `specs/027-contractor-stakeholder-select`  
**Spec Kit logical feature key**: `027-contractor-stakeholder-select` (setup JSON `BRANCH`; no Git branch created/switched)

**Status**: Phase 0 research and Phase 1 design complete. Design artifacts only; no `tasks.md`, source edits, or migrations in this invocation.

## Summary

Replace free-text پیمانکار pickers with a non-creatable selection of **active project stakeholders whose role is the canonical contractor code**, maintained on ذینفعان. Persist a Stakeholder FK plus denormalized name snapshot on department activity (P1), then daily-report/labor and project party fields (P2). Reuse the existing stakeholders list API with `role` + `status` filters; do not merge the پیمانکار فرعی / contracts registers.

## Technical Context

**Language/Version**: Python 3.x / Django 4.2.11 (API); TypeScript + React 19 + React Router 7 + Vite (`apps/web`)

**Primary Dependencies**: DRF, PostgreSQL, TanStack Query, i18next, existing form `Select` / combobox patterns (not CreatableSelect for this field)

**Storage**: PostgreSQL — additive nullable FKs to `projects.Stakeholder`; existing CharField name columns retained as snapshots

**Testing**: pytest (stakeholder filter, FK validation, import resolve, project isolation); `pnpm typecheck`; browser check of department modal + ذینفعان role (fa/en)

**Target Platform**: Bilingual web SPA + Django API (Linux-hosted)

**Project Type**: pnpm monorepo (`apps/api` + `apps/web`)

**Performance Goals**: Contractor option lists are project-scoped and small; no new SLA beyond normal form responsiveness

**Constraints**: Project tenancy / IDOR-safe FK checks; no inline create in picker; no Django upgrade; preserve warehouse path that clears contractor; leave `subcontractors` app and Contract FK schema in place

**Scale/Scope**: One classification rule on Stakeholder; FKs on department activity + daily/labor + Project; shared UI helper; P1 then P2 surfaces per spec

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-research and post-design: **PASS** (design gates only; not runtime proof).

| Principle | Gate |
|-----------|------|
| **I — Authorization / isolation** | PASS — Project-scoped stakeholder queries and FK project equality checks; list uses existing `view_project`; edits use existing `edit_project` |
| **II — Data / domain integrity** | PASS — Additive FKs + name snapshots; import resolution; legacy free-text readable until edit; Contract FK retained unused by picker |
| **III — Bilingual** | PASS — Stable `contractor` code; fa/en labels for role, empty state, validation |
| **IV — Safe mutations** | PASS — No destructive drop of Contract FK; inactive removes from options only |
| **V — Minimal coherent change** | PASS — Extend Stakeholder `role` + existing list endpoint; shared select; no parallel contractor registry |
| **VI — Evidence** | PASS — Plan requires pytest + typecheck + browser/locale checks on final tree |
| **VII — Accessible UX** | PASS — Non-creatable accessible select; empty-state guidance to ذینفعان |

No unjustified violations → Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/027-contractor-stakeholder-select/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── contractor-select-api.md
│   └── contractor-select-ui.md
├── spec.md
└── checklists/requirements.md
```

`tasks.md` is **not** created here — use `/speckit-tasks` next.

### Source Code (repository root; proposed touchpoints, not edits)

```text
apps/api/core/
├── projects/
│   ├── models.py                 # Project.contractor_ref; role normalize helper
│   ├── stakeholder_views.py      # role/status query filters; role write normalize
│   ├── serializers.py            # project contractor_ref if settings exposed here
│   └── migrations/               # additive FKs
├── inventory/
│   ├── models.py                 # DepartmentActivityRecord.contractor_ref
│   ├── serializers.py            # require/validate contractor_ref; snapshot name
│   ├── department_activity_*.py  # filter + import resolve
│   └── tests.py / new focused tests
├── field_reports/
│   ├── models.py                 # DailyReportActivity + labor contractor_ref
│   ├── serializers.py
│   └── tests/
└── locale/fa/LC_MESSAGES/        # validation messages as needed

apps/web/src/
├── components/form/              # shared ContractorSelect (non-creatable)
├── components/department/
│   └── department-activity-record-modal.tsx
├── components/department/department-page.tsx   # filter
├── app/routes/project-stakeholders.tsx         # role (+ status) on create/edit
├── components/daily_reports/                   # ActivityTab / LaborCamp options source
├── app/routes/project-settings.tsx
├── app/routes/project-create-wizard.tsx
├── app/lib/api/central-data.ts                 # fetchProjectContractors helper
└── locales/fa.json / en.json
```

**Structure Decision**: Keep ذینفعان as the register; add FKs on consumers; one shared frontend fetch + select. Do not introduce a second contractor table.

## Phase 0 — Research outcome

[research.md](./research.md) resolves: stakeholder source, `role=contractor` classification, FK + name snapshot, department P1, daily/labor/project P2 without dropping Contract FK, list filter API, non-creatable UI, out-of-scope registers, verification categories.

## Phase 1 — Design outcome

- [data-model.md](./data-model.md) — classification predicate, FKs, validation, legacy/inactive behavior  
- [contracts/contractor-select-api.md](./contracts/contractor-select-api.md) — list filter, writes, import, isolation  
- [contracts/contractor-select-ui.md](./contracts/contractor-select-ui.md) — shared select, ذینفعان role, surfaces  
- [quickstart.md](./quickstart.md) — end-to-end validation scenarios  

## Complexity Tracking

> None — no constitution violations requiring justification.
