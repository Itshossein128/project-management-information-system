# Implementation Plan: Physical Progress & Periodic Reports Gap Closure

**Branch**: `009-progress-periodic-reports` | **Date**: 2026-10-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/009-progress-periodic-reports/spec.md`

**Note**: Spec Kit plan/tasks only — **do not implement** until explicitly requested.

## Summary

Close FR-PRG gaps on the existing Sprint 6 progress stack (`schedule.ActivityProgress`, progress dashboard, S-curve, daily-report recalc): add versioned **measurement methods** with approval gates; enforce **reject >100%** (no silent clamp) unless linked approved quantity/basis change; expose **period / cumulative / planned / approved** as four distinct values; treat photos as evidence only (not technical approval); generate **project weekly and monthly reports** with per-figure provenance and audited overrides. Extend `apps/api/core/schedule/` (+ light `field_reports` / activity field hooks) and the progress UI; do not replace the dashboard or invent full EVM (13).

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2.11), TypeScript 5.x (React Router 7 + Vite)

**Primary Dependencies**: Django REST Framework, existing `schedule` progress services/views, `field_reports` approve→recalc path, `projects.Activity` / WBS, React + TanStack Query, i18next, Jalali helpers

**Storage**: PostgreSQL — additive fields on Activity / ActivityProgress; new measurement-definition + version tables; new weekly/monthly project report (+ figure provenance / override audit) tables in `schedule` (or thin `progress_reports` module under schedule)

**Testing**: pytest + pytest-django (TDD at implement time); frontend typecheck for touched types; optional Playwright smoke on progress + report generation

**Target Platform**: Web SPA + Django API under `/api/v1/projects/{uuid}/progress/` and `/…/progress-reports/`

**Project Type**: Monorepo web application

**Performance Goals**: Progress snapshot / four-way activity list within normal request latency for projects with hundreds of activities; weekly/monthly generate from approved sources in one request (or short async job with poll) for typical month data volumes

**Constraints**: Django 4.2 pin; project tenancy + `view_dashboard` / `edit_activities` / `approve_reports` (reuse; add report-specific codes only if needed); soft-delete / audit; bilingual labels; no Spec Kit implement in this pass; no full EVM (13); no portfolio dashboard (16); do not conflate with inventory department weekly PDF

**Scale/Scope**: Gap-close on physical progress semantics + two period-report generators; compose optional monthly sections from cost/commitment/IPC/risk when present (“not recorded” otherwise)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Server-enforced authorization | PASS | Method approve, progress write, report generate/override behind membership + permissions |
| II. Data integrity end-to-end | PASS | Method version, four-way progress, >100 reject, provenance through model→API→UI→tests |
| III. Bilingual / locale-correct | PASS | Method labels, four-way progress labels, report section “not recorded”, validation codes localized |
| IV. Explicit safe mutations | PASS | Method change versioned; report figure overrides blocked or audited; no silent clamp as success |
| V. Minimal coherent changes | PASS | Extend `schedule` + progress UI; reuse daily-report approval for quantity feed; no parallel progress domain |
| VI. Evidence-based verification | PASS | pytest per story (method, four-way, reject>100, weekly/monthly provenance, method version) |
| VII. Accessible practical UX | PASS | Clear four labels; incomplete-method warnings; report source links |

**Gate result (pre-research)**: PASS  
**Gate result (post-Phase 1 design)**: PASS — contracts additive; Complexity Tracking N/A

## Project Structure

### Documentation (this feature)

```text
specs/009-progress-periodic-reports/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── measurement-methods.md
│   ├── progress-four-way.md
│   ├── weekly-monthly-reports.md
│   └── progress-validation.md
├── checklists/
│   └── requirements.md
└── tasks.md                 # /speckit-tasks
```

### Source Code (repository root)

```text
apps/api/core/
├── schedule/
│   ├── models.py                    # ActivityProgress extensions; MeasurementDefinition/Version; PeriodReport*
│   ├── services/
│   │   ├── progress_service.py      # four-way snapshot; >100 reject; method binding
│   │   ├── measurement_service.py   # approve basis; method change lifecycle
│   │   └── period_report_service.py # weekly/monthly compose + provenance
│   ├── progress_views.py / urls.py / serializers
│   ├── ENDPOINTS.md
│   └── tests/                       # TDD modules for FR-PRG gaps
├── field_reports/
│   └── tasks.py                     # recalc respects method + reject>100 (no clamp-as-success)
├── projects/models.py               # optional Activity measurement FK / basis-approved flags
└── permissions/constants.py         # reuse view_dashboard / edit_activities / approve_reports

apps/web/src/
├── app/routes/project-progress.tsx  # four-way columns; method status; report actions
├── components/progress/             # tables, manual drawer validation, report panels
├── app/lib/api/progress.ts          # + measurement + period-report clients
└── app/locales/{fa,en}.json
```

**Structure Decision**: Extend existing `schedule` progress domain and progress React page; add period-report resources under the same project API prefix. Do not build a second dashboard or reuse inventory department weekly PDF.

## Complexity Tracking

> No unjustified violations.
