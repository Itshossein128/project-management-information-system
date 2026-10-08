# Implementation Plan: WBS Structure

**Branch**: `004-wbs-structure` | **Date**: 2026-10-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-wbs-structure/spec.md`

**Note**: Spec Kit plan/tasks only — **do not implement** until explicitly requested.

## Summary

Close FR-WBS gaps on the existing treebeard WBS: node fields for responsible, acceptance criteria, and status; stronger delete protection (cost / progress / document in addition to children & activities); explicit cycle rejection on move; prove template apply is copy-on-write so later template edits never silently rewrite live project trees. Extend `apps/api/core/wbs/` + `projects.WBS` and light UI on the existing WBS page; reuse soft-delete/audit from 002 and project templates from `project_templates`.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2.11), TypeScript 5.x (React Router 7 + Vite)

**Primary Dependencies**: Django REST Framework, django-treebeard (`MP_Node`), existing `wbs` ViewSet/services, `project_templates` apply/save, React + TanStack Query, i18next

**Storage**: PostgreSQL — additive columns on `wbs`; no new CBS-like tree; templates remain in `project_template_wbs`

**Testing**: pytest + pytest-django (TDD at implement time); frontend typecheck for touched types

**Target Platform**: Web SPA + Django API under `/api/v1/projects/{uuid}/wbs/`

**Project Type**: Monorepo web application

**Performance Goals**: Tree load for hundreds of nodes interactive; move/recode safe under uniqueness constraints (existing two-phase propagate)

**Constraints**: Django 4.2 pin; project tenancy + `edit_wbs`/`view_wbs` (or equivalent) permissions; soft-delete only; bilingual labels; CBS ≠ WBS; no Spec 05 schedule redesign; no implement in this Spec Kit pass

**Scale/Scope**: Gap-close on mature WBS module + template immutability proofs + minimal UI field exposure

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Server-enforced authorization | PASS | Keep WBS mutations behind project membership + permission |
| II. Data integrity end-to-end | PASS | New fields + delete guards through model→API→UI→tests; staged code renumber already exists |
| III. Bilingual / locale-correct | PASS | Status/labels and delete reasons in fa/en |
| IV. Explicit safe mutations | PASS | Expand delete conflict reasons; template force-replace must stay explicit and dependency-aware |
| V. Minimal coherent changes | PASS | Extend `WBS` + `wbs.services` + existing template service; no parallel tree |
| VI. Evidence-based verification | PASS | pytest per story; template immutability regression |
| VII. Accessible practical UX | PASS | Tree + node drawer/form fields for responsible/acceptance/status |

**Gate result (pre-research)**: PASS  
**Gate result (post-Phase 1 design)**: PASS — contracts additive; Complexity Tracking N/A

## Project Structure

### Documentation (this feature)

```text
specs/004-wbs-structure/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── wbs-tree-nodes.md
│   ├── wbs-delete-guards.md
│   └── wbs-templates.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/api/core/
├── projects/models.py              # WBS additive fields
├── wbs/
│   ├── services.py                 # create/update/move/delete + cycle + dependency guards
│   ├── serializers.py / views.py
│   └── tests/                      # TDD modules for FR-WBS
├── project_templates/
│   ├── models.py                   # ProjectTemplateWBS (existing)
│   └── services.py                 # apply copy-on-write; no silent live rewrite
└── documents/ / cost_control/ / schedule/  # FK sources for delete guards

apps/web/src/
├── app/routes/project-wbs.tsx      # expose new node fields
├── components/wbs/                 # form/drawer updates
└── app/locales/{fa,en}.json
```

## Complexity Tracking

> No unjustified violations. Optional note: `force=true` template replace currently hard-deletes; plan tasks will align with soft-delete/dependency policy rather than inventing a second template engine.
