# Implementation Plan: Daily Site Report Gap Closure

**Branch**: `007-daily-report-gaps` | **Date**: 2026-10-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-daily-report-gaps/spec.md`

**Note**: Spec Kit plan/tasks only — **do not implement** until explicitly requested.

## Summary

Close FR-DR gaps on the existing `field_reports` daily-report stack: header work-front/location; activity responsible person; labor absence; material **return** type + optional consumption location; site-event owner/due date (and stoppage/instruction/barrier types); treat **approved = locked** in UX/copy; add **correction-request** lifecycle that retains prior locked versions; extend unset-vs-zero for measured quantities; light material–inventory reconciliation hint. Extend `apps/api/core/field_reports/` + daily-report UI; preserve offline sync, progress recalculation on approve, and existing submit/review/approve/reject path.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2.11), TypeScript 5.x (React Router 7 + Vite)

**Primary Dependencies**: Django REST Framework, existing `field_reports` services/views, `resources.Material` balance for reconciliation hint, React + TanStack Query, i18next, Jalali helpers

**Storage**: PostgreSQL — additive columns on DailyReport / child rows; new correction-request + version snapshot tables (or equivalent lineage fields) in `field_reports`

**Testing**: pytest + pytest-django (TDD at implement time); frontend typecheck for touched types; optional Playwright smoke after UI lands

**Target Platform**: Web SPA + Django API under `/api/v1/projects/{uuid}/daily-reports/`

**Project Type**: Monorepo web application

**Performance Goals**: Correction snapshot create + detail retrieve within normal request latency for reports with typical child-row counts (tens of rows per section)

**Constraints**: Django 4.2 pin; project tenancy + `view_reports` / `edit_reports` / `approve_reports`; soft-delete / audit; bilingual labels; approved reports remain immutable except via correction; offline sync must not overwrite locked content; no Spec Kit implement in this pass; do not rebuild weekly/monthly progress (08) or HR capacity (06)

**Scale/Scope**: Gap-close on `field_reports` daily report + form UI; light read-only reconciliation against `resources` balance

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Server-enforced authorization | PASS | Correction create/edit/approve behind membership + `edit_reports` / `approve_reports`; child writes remain status-gated |
| II. Data integrity end-to-end | PASS | Header location, responsible, absence, return, site-event owner/due, correction versions through model→API→UI→tests→PDF/sync where applicable |
| III. Bilingual / locale-correct | PASS | Locked/correction statuses, unset-vs-zero messages, material return labels in fa/en; Jalali report date unchanged |
| IV. Explicit safe mutations | PASS | Direct edit of locked denied; correction requires reason; prior locked version retained |
| V. Minimal coherent changes | PASS | Extend `field_reports`; reuse approve as lock; do not invent generic workflow engine (15) |
| VI. Evidence-based verification | PASS | pytest per story (header/responsible, correction, materials/labor/events, status copy + unset-vs-zero) |
| VII. Accessible practical UX | PASS | Correction reason required; clear lock messaging; mobile-width form fields |

**Gate result (pre-research)**: PASS  
**Gate result (post-Phase 1 design)**: PASS — contracts additive; Complexity Tracking N/A

## Project Structure

### Documentation (this feature)

```text
specs/007-daily-report-gaps/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── daily-report-header-and-rows.md
│   ├── correction-requests.md
│   ├── material-reconciliation.md
│   └── status-and-unset-semantics.md
├── checklists/
│   └── requirements.md
└── tasks.md                 # /speckit-tasks
```

### Source Code (repository root)

```text
apps/api/core/
├── field_reports/
│   ├── models.py                 # header work_front; responsible; absence; return; site events; correction/version
│   ├── services/                 # correction lifecycle; reconciliation hint; unset validation
│   ├── serializers.py / daily_report_views.py / urls.py
│   ├── ENDPOINTS.md
│   ├── pdf.py                    # include new fields where printed
│   └── tests/                    # TDD modules for FR-DR gaps
├── resources/                    # read-only balance for reconciliation hint
└── permissions/constants.py      # reuse view/edit/approve_reports (no new codes unless needed)

apps/web/src/
├── components/daily_reports/     # form tabs, correction UI, lock labels, unset qty UX
├── app/routes/                   # daily report list/form/view
├── app/lib/api/daily-reports.ts
└── app/locales/{fa,en}.json
```

**Structure Decision**: Extend existing `field_reports` Django app and daily-report React form; do not create a parallel reporting domain.

## Complexity Tracking

> No unjustified violations.
