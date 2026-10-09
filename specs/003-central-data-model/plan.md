# Implementation Plan: Central Data Model

**Branch**: `003-central-data-model` | **Date**: 2026-10-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-central-data-model/spec.md`

**Note**: Spec Kit plan/tasks only — **do not implement** until explicitly requested.

## Summary

Close FR-DATA gaps: explicit navigation/aggregation along project←WBS←activity←daily report/progress; partial IPC/collection (and payment) rows that never overwrite originals; CBS hierarchy + Commitment entity completing budget←commitment←cost←payment; managed references for contract type/cost codes; OrganizationUnit (OBS) and Stakeholder foundations. Extend existing Django apps (`projects`, `contracts`, `cost_control`, `master_data`, `cash_flow`) rather than a parallel schema. Reuse 002 currency, soft-delete, and audit helpers.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2.11), TypeScript 5.x (React Router 7 + Vite)

**Primary Dependencies**: Django REST Framework, drf-spectacular, treebeard (WBS pattern reuse for CBS), existing contracts/cost_control/cash_flow services, React + TanStack Query, i18next

**Storage**: PostgreSQL — new tables for CBS, Commitment, Payment/Collection rows, OrganizationUnit, Stakeholder; additive FKs on Project/Contract/Budget/ActualCost

**Testing**: pytest + pytest-django (recommended TDD at implement time); frontend typecheck for new API types

**Target Platform**: Web SPA + Django API under `/api/v1/projects/{uuid}/` (org-wide refs under `/api/v1/` where appropriate)

**Project Type**: Monorepo web application

**Performance Goals**: Portfolio aggregate for tens of projects in interactive time; tree list for CBS comparable to WBS

**Constraints**: Django 4.2 pin; no SQLite; server tenancy/permissions; bilingual labels; minimal coherent change; no ERP; no implement in this Spec Kit pass

**Scale/Scope**: Data-model foundation across ~6 apps + light UI for CBS/stakeholders/collections; not full rewrite of modules 03–16

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Server-enforced authorization | PASS | Project-scoped entities under existing permissions; org-wide refs staff/admin or `view_project` read |
| II. Data integrity end-to-end | PASS | Trace new FKs through model→migration→serializer→API→UI→i18n→tests |
| III. Bilingual / locale-correct | PASS | New entity labels in fa/en |
| IV. Explicit safe mutations | PASS | Soft-delete/block on CBS with links; collections append-only vs original amount |
| V. Minimal coherent changes | PASS | Extend contracts/cost_control/master_data; mirror WBS tree pattern for CBS |
| VI. Evidence-based verification | PASS | pytest per story at implement; quickstart validation |
| VII. Accessible practical UX | PASS | Catalog selects over free-text for critical refs |

**Gate result (pre-research)**: PASS  
**Gate result (post-Phase 1 design)**: PASS — contracts project-scoped; additive schema; Complexity Tracking N/A

## Project Structure

### Documentation (this feature)

```text
specs/003-central-data-model/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── navigation-portfolio.md
│   ├── ipc-collections.md
│   ├── cbs-commitment-payment.md
│   └── org-stakeholder-refs.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/api/core/
├── master_data/
│   ├── models.py              # Unit (existing); ContractType; CostCode; OrganizationUnit
│   └── views/serializers      # org-wide reference CRUD
├── projects/
│   ├── models.py              # Project.owning_unit FK; optional budget_ceiling alias
│   └── portfolio_views.py     # NEW portfolio aggregate
├── wbs/ or projects/          # existing WBS/Activity chains
├── cost_control/
│   ├── models.py              # CBS nodes; Commitment; Payment; Budget±cbs FK; ActualCost±cbs/commitment
│   └── services/
├── contracts/
│   ├── models.py              # IPCCollection (partial receipts); contract_type FK
│   └── ipc_service.py         # append-only collections
└── field_reports/             # ensure activity→wbs→project exposed in serializers

apps/web/src/
├── app/lib/api/               # cbs, commitments, collections, org, stakeholders, portfolio
├── app/routes/                # cbs tree, stakeholders, ipc collection UI hooks
└── app/locales/fa.json|en.json
```

**Structure Decision**: Keep domain ownership — CBS/Commitment/Payment in `cost_control`; IPC collections in `contracts`; OrganizationUnit/ContractType/CostCode in `master_data`; Stakeholder in `projects` or `documents` (prefer `projects` for project FK simplicity).

## Complexity Tracking

> Not applicable — Constitution Check passed without violations.
