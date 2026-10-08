# Implementation Plan: HR & Capacity Gap Closure

**Branch**: `006-hr-capacity` | **Date**: 2026-10-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-hr-capacity/spec.md`

**Note**: Spec Kit plan/tasks only — **do not implement** until explicitly requested.

## Summary

Close FR-HR gaps on the existing HR stack: extend person dossier (skills, qualifications, org unit, supervisor); introduce project-scoped **resource allocations** distinct from `ProjectMember` membership; capacity overlap calculation with conflict warning and approved exception workflow; field-level ACL for wage / approved labor rates; prefer approved rate × approved hours for cost estimates without inventing rates. Extend `apps/api/core/hr/` + light User dossier fields; redact wage on membership serializers; preserve leave/OT/manpower and progress≠labor isolation.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2.11), TypeScript 5.x (React Router 7 + Vite)

**Primary Dependencies**: Django REST Framework, existing `hr` leave/OT services, `authentication.User`, `master_data.ProjectMember` / `OrganizationUnit`, `permissions` catalog, React + TanStack Query, i18next

**Storage**: PostgreSQL — additive User dossier columns; new `hr` tables for resource allocations, capacity exceptions, approved labor rates (project- or person-scoped)

**Testing**: pytest + pytest-django (TDD at implement time); frontend typecheck for touched types; optional Playwright smoke after UI lands

**Target Platform**: Web SPA + Django API under `/api/v1/projects/{uuid}/` (allocations, exceptions) plus person-dossier endpoints (org- or project-scoped as designed)

**Project Type**: Monorepo web application

**Performance Goals**: Capacity check for a person with dozens of overlapping allocations within a normal request; allocation list for a project interactive for hundreds of rows

**Constraints**: Django 4.2 pin; project tenancy + new `view_hr` / `edit_hr` / `approve_hr` / `view_wage`; soft-delete / audit on allocations and exceptions; bilingual labels; allocation never grants membership; allocation/attendance never feed progress; no leave/OT/manpower rebuild; no Spec Kit implement in this pass

**Scale/Scope**: Gap-close on `hr` + User dossier + wage ACL on membership/cost estimate paths

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Server-enforced authorization | PASS | New routes behind membership + `view_hr` / `edit_hr` / `approve_hr`; wage fields gated by `view_wage` |
| II. Data integrity end-to-end | PASS | Dossier + allocation + exception + rate ACL through model→API→UI→tests; progress isolation regression |
| III. Bilingual / locale-correct | PASS | Conflict messages, exception reasons, dossier labels in fa/en |
| IV. Explicit safe mutations | PASS | Over-capacity requires explicit exception approval; soft-delete on allocations/exceptions |
| V. Minimal coherent changes | PASS | Extend `hr` + User; do not overload `ProjectMember` into allocation; leave `resources` (materials) alone |
| VI. Evidence-based verification | PASS | pytest per story (dossier, allocation, capacity conflict, exception, wage ACL, progress isolation) |
| VII. Accessible practical UX | PASS | Clear capacity conflict feedback; allocation forms with validation |

**Gate result (pre-research)**: PASS  
**Gate result (post-Phase 1 design)**: PASS — contracts additive; Complexity Tracking N/A

## Project Structure

### Documentation (this feature)

```text
specs/006-hr-capacity/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── person-dossier.md
│   ├── resource-allocations.md
│   ├── capacity-exceptions.md
│   └── wage-acl-and-cost-estimate.md
├── checklists/
│   └── requirements.md
└── tasks.md                 # /speckit-tasks (not this command)
```

### Source Code (repository root)

```text
apps/api/core/
├── authentication/models.py           # User dossier additive fields
├── hr/
│   ├── models.py                      # ResourceAllocation, CapacityException, ApprovedLaborRate
│   ├── services/                      # capacity calc, allocation CRUD, exception workflow, cost estimate
│   ├── serializers.py / views.py / urls.py
│   ├── ENDPOINTS.md
│   └── tests/                         # TDD modules for FR-HR gaps
├── master_data/                       # ProjectMember wage ACL on serializers only
├── permissions/constants.py           # view_hr, edit_hr, approve_hr, view_wage (+ seed migration)
├── projects/                          # optional hr capability key if toggled
└── field_reports/                     # regression only: progress ≠ labor

apps/web/src/
├── app/routes/                        # project allocations + person dossier surfaces
├── components/hr/                     # allocation form, capacity warning, exception approve
├── app/lib/api/hr*.ts
└── app/locales/{fa,en}.json
```

**Structure Decision**: Extend existing `hr` Django app and User dossier fields in the monorepo; do not place people capacity in `resources` (materials).

## Complexity Tracking

> No unjustified violations.
