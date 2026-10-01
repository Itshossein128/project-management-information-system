# Implementation Plan: Warehouse Report Fields

**Branch**: `001-warehouse-report-fields` | **Date**: 2026-10-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-warehouse-report-fields/spec.md`

## Summary

Warehouse department activity records switch from the generic activity-log field set to material-movement fields: date, material type, inbound quantity, unit, outbound quantity, consumption location, supplier, and notes. Non-warehouse departments keep the existing schema. Implementation extends the shared `DepartmentActivityRecord` model with warehouse-specific columns, department-aware validation/IO/UI, and TDD-first coverage across API, persistence, lists, Excel, and PDF reports.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2.11), TypeScript 5.x (React Router 7 + Vite)

**Primary Dependencies**: Django REST Framework, drf-spectacular, pandas/openpyxl/reportlab (existing IO), React + TanStack Query/Table, i18next (fa/en)

**Storage**: PostgreSQL (`DepartmentActivityRecord` in `inventory` app; new nullable/blank warehouse columns + relaxed blank on generic fields)

**Testing**: pytest + pytest-django (API/services/IO first, TDD); frontend typecheck; browser verification for warehouse form/list bilingual UX

**Target Platform**: Web SPA (`apps/web`) + Django API (`apps/api/core`) under project tenancy `/api/v1/projects/{uuid}/`

**Project Type**: Monorepo web application (frontend + backend)

**Performance Goals**: Unchanged list/export performance for typical department activity volumes (hundreds–thousands of rows per project/department)

**Constraints**: Django 4.2 pin; no SQLite; server-enforced project permissions; bilingual labels; minimal coherent change (no parallel warehouse microservice)

**Scale/Scope**: One department schema variant (`warehouse`) across create modal, table, filters/search/sort, Excel import/export, daily/weekly PDF reports, admin, and TypeScript contracts

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Server-enforced authorization / project isolation | PASS | Reuse existing project-scoped viewsets and permissions; no new unauthenticated paths |
| II. Data integrity end-to-end | PASS | Plan traces fields through model → migration → serializer → services → IO → UI → i18n → tests |
| III. Bilingual / locale-correct | PASS | New warehouse labels and validation copy in `fa.json` / `en.json`; Jalali date picker retained |
| IV. Explicit safe mutations | PASS | Import validation rejects bad rows; no irreversible destructive migration of non-warehouse data |
| V. Minimal coherent changes | PASS | Extend shared `DepartmentActivityRecord` + department-aware branches; no second activity model |
| VI. Evidence-based verification | PASS | TDD pytest for warehouse rules; migration verification; browser check for warehouse form |
| VII. Accessible practical UX | PASS | Required/optional clarity, sticky fields preserved where applicable, searchable unit select retained |

**Gate result (pre-research)**: PASS — no unjustified violations. Complexity Tracking not required.

**Gate result (post-Phase 1 design)**: PASS — `data-model.md` and `contracts/` keep authorization on existing project routes, bilingual presentation in quickstart, end-to-end field tracing, additive migration without silent legacy remap, and TDD verification path.

## Project Structure

### Documentation (this feature)

```text
specs/001-warehouse-report-fields/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/           # Phase 1
│   └── department-activity-records.md
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
apps/api/core/inventory/
├── models.py                          # DepartmentActivityRecord + helpers
├── serializers.py                     # department-aware validation
├── department_activity_services.py    # filters/search/ordering for warehouse fields
├── department_activity_io.py          # Excel/PDF warehouse headers & mapping
├── department_activity_data_views.py  # export/import/report OpenAPI params
├── views.py                           # list/create OpenAPI + queryset
├── admin.py                           # warehouse field display/search
├── migrations/                        # schema migration
└── tests.py                           # TDD pytest coverage (extend)

apps/web/src/
├── app/lib/api-types.ts               # warehouse-aware types/helpers
├── app/locales/fa.json                # warehouse field labels
├── app/locales/en.json
├── components/department/
│   ├── department-activity-record-modal.tsx  # warehouse vs generic form
│   └── department-page.tsx                   # warehouse columns/filters
└── app/hooks/queries.ts               # payload types if needed
```

**Structure Decision**: Extend the existing inventory department-activity stack in `apps/api/core/inventory` and the shared department UI in `apps/web/src/components/department`. No new top-level apps.

## Complexity Tracking

> Not applicable — Constitution Check passed without violations.
