# Implementation Plan: Project Registration & Kickoff Gap Closure

**Branch**: `008-project-registration` | **Date**: 2026-10-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-project-registration/spec.md`

**Note**: Spec Kit plan/tasks only — **do not implement** until explicitly requested.

## Summary

Close FR-PRJ gaps on the existing `projects` stack: full lifecycle statuses (draft → pending approval → active → suspended / completed / archived); create as draft with purpose, scope, deliverables, contract number, and budget-approval gate; project kickoff charter; project change requests for protected approved fields; block definitive locked schedule baselines (and binding commitments) while unapproved or suspended; archive read-only for non–system-admin. Extend `apps/api/core/projects/` + create wizard / settings / overview UI; reuse `edit_project` and add `approve_project`.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2.11), TypeScript 5.x (React Router 7 + Vite)

**Primary Dependencies**: Django REST Framework, existing `projects` ViewSet/services, schedule `baseline_service` gate hook, React + TanStack Query/Form, i18next

**Storage**: PostgreSQL — additive columns on `projects`; new `project_kickoff_charters` and `project_change_requests` tables; permission seed for `approve_project`

**Testing**: pytest + pytest-django (TDD at implement time); frontend typecheck for touched types; optional Playwright smoke for create→approve→change-request

**Target Platform**: Web SPA + Django API under `/api/v1/projects/`

**Project Type**: Monorepo web application

**Performance Goals**: Status transition and change-request approve within normal request latency; list/filter by status unchanged for portfolio scale (hundreds of projects)

**Constraints**: Django 4.2 pin; project tenancy + membership; bilingual status/validation copy; minimal coherent extension of `projects` (no generic workflow engine); do not rebuild WBS (04), schedule CR (05), line budgets (09), or full contracts (10); no Spec Kit implement in this pass

**Scale/Scope**: Gap-close on project identity lifecycle, charter, and project-field change control; thin enforcement hooks into schedule baseline lock and commitment creation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Server-enforced authorization | PASS | Lifecycle/charter/CR behind membership + `edit_project` / `approve_project`; archive mutates only system admin |
| II. Data integrity end-to-end | PASS | Status, identity fields, charter, CR through model→API→UI→tests; migration maps legacy statuses |
| III. Bilingual / locale-correct | PASS | New statuses, gate errors, CR labels in fa/en |
| IV. Explicit safe mutations | PASS | Activation gated; protected fields only via approved CR; baseline lock blocked when unapproved/suspended |
| V. Minimal coherent changes | PASS | Extend `projects`; reuse schedule baseline service for lock gate; no parallel project domain |
| VI. Evidence-based verification | PASS | pytest per story (lifecycle, charter, CR, gates); migration apply check |
| VII. Accessible practical UX | PASS | Clear missing-gate messages; create wizard + settings aligned with draft/active rules |

**Gate result (pre-research)**: PASS  
**Gate result (post-Phase 1 design)**: PASS — contracts additive; Complexity Tracking N/A

## Project Structure

### Documentation (this feature)

```text
specs/008-project-registration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── project-lifecycle.md
│   ├── kickoff-charter.md
│   ├── project-change-requests.md
│   └── commitment-and-baseline-gates.md
├── checklists/
│   └── requirements.md
└── tasks.md                 # this command
```

### Source Code (repository root)

```text
apps/api/core/
├── projects/
│   ├── models.py              # status enum expand; identity fields; Charter; ChangeRequest
│   ├── services.py / lifecycle_service.py / charter_service.py / change_request_service.py
│   ├── serializers.py / views.py / urls.py
│   ├── migrations/            # status + fields + tables + backfill
│   └── tests/                 # test_project_lifecycle_*, charter, change_request, gates
├── schedule/services/baseline_service.py   # call project gate before lock
├── contracts/ or cost_control/             # thin gate on binding commitment create (see research)
└── permissions/constants.py                # approve_project

apps/web/src/
├── app/routes/project-create-wizard.tsx
├── app/routes/project-settings.tsx
├── app/routes/project-overview.tsx / project-list.tsx
├── components/projects/                    # charter panel; change-request UI; status bar
├── app/lib/api/projects.ts
└── app/locales/{fa,en}.json
```

**Structure Decision**: Extend existing `projects` Django app and project create/settings/overview React surfaces; enforce FR-PRJ-004 via shared project readiness helper called from schedule (and commitment) services—do not create a second project registry.

## Complexity Tracking

> No unjustified violations.
