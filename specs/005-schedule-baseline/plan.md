# Implementation Plan: Schedule & Baseline Gap Closure

**Branch**: `005-schedule-baseline` | **Date**: 2026-10-08 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-schedule-baseline/spec.md`

**Note**: Spec Kit plan/tasks only — **do not implement** until explicitly requested.

## Summary

Close FR-SCH gaps on the existing schedule stack: project working calendars; activity duration/milestone + forecast dates + calendar-aware validation; formal baseline lock (live edits never rewrite locked snapshots); schedule change-request workflow that publishes a new locked baseline version; milestone/delay report with four-way date clarity; critical-path validity gate when durations/relations are incomplete. Extend `apps/api/core/schedule/` + `projects.Activity` and light UI on activities / Gantt / a new status report route; reuse relation cycle detection, MSP/P6 import, and Gantt compare.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2.11), TypeScript 5.x (React Router 7 + Vite)

**Primary Dependencies**: Django REST Framework, existing `schedule` services/views, `projects.Activity` / `ActivityRelation`, Celery for import-only paths (unchanged), React + TanStack Query, i18next, Jalali date helpers

**Storage**: PostgreSQL — additive columns on `activities` / `baseline_schedules`; new tables for working calendars, calendar exceptions, schedule change requests (+ optional line items)

**Testing**: pytest + pytest-django (TDD at implement time); frontend typecheck for touched types; optional Playwright smoke after UI lands

**Target Platform**: Web SPA + Django API under `/api/v1/projects/{uuid}/` (activities, calendars, baselines, change-requests, schedule-status)

**Project Type**: Monorepo web application

**Performance Goals**: Status report for hundreds of activities interactive; validity check O(n+e) over active network; baseline snapshot create on approve within normal request budgets (or async only if needed later)

**Constraints**: Django 4.2 pin; project tenancy + `view_activities` / `edit_activities`; soft-delete / audit for new entities; bilingual labels; no full CPM rewrite; no auto forecast from progress in v1; no Spec 07/08 scope; no implement in this Spec Kit pass

**Scale/Scope**: Gap-close on mature schedule module (~activities + baselines + Gantt) + change-request workflow + status report UI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Server-enforced authorization | PASS | All new routes behind membership + `view_activities` / `edit_activities` |
| II. Data integrity end-to-end | PASS | Fields + lock + change-request through model→API→UI→tests; locked baseline immutable |
| III. Bilingual / locale-correct | PASS | Status/labels, “not calculable”, change-request reasons in fa/en; Jalali display |
| IV. Explicit safe mutations | PASS | Baseline lock; approve change request is explicit; reject direct locked snapshot edit |
| V. Minimal coherent changes | PASS | Extend Activity + BaselineSchedule + schedule services; no parallel schedule engine |
| VI. Evidence-based verification | PASS | pytest per story (lock, change request, validity gate, forecast separation) |
| VII. Accessible practical UX | PASS | Clear validation on impossible dates; report distinguishes four date sets |

**Gate result (pre-research)**: PASS  
**Gate result (post-Phase 1 design)**: PASS — contracts additive; Complexity Tracking N/A

## Project Structure

### Documentation (this feature)

```text
specs/005-schedule-baseline/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── working-calendars.md
│   ├── activities-extended.md
│   ├── baselines-and-change-requests.md
│   └── schedule-status-report.md
├── checklists/
│   └── requirements.md
└── tasks.md                 # /speckit-tasks (not this command)
```

### Source Code (repository root)

```text
apps/api/core/
├── projects/models.py                 # Activity additive fields (forecast, duration, milestone, calendar FK)
├── schedule/
│   ├── models.py                      # WorkingCalendar*, BaselineSchedule lock fields, ScheduleChangeRequest
│   ├── services/                      # validation, lock, change_request, critical_path_validity, status_report
│   ├── serializers.py / *_views.py / urls.py
│   ├── ENDPOINTS.md                   # document new routes
│   └── tests/                         # TDD modules for FR-SCH gaps
└── permissions/constants.py           # reuse view/edit_activities (no new perm unless tasks prove need)

apps/web/src/
├── app/routes/project-activities.tsx / project-schedule-gantt.tsx
├── app/routes/project-schedule-status.tsx   # milestone/delay report (new)
├── components/schedule/                    # calendar picker, change-request drawer, status tables
├── app/lib/api/activities.ts / schedule*.ts
└── app/locales/{fa,en}.json
```

**Structure Decision**: Extend existing schedule + projects Activity models in the monorepo API/web apps; no new top-level Django app.

## Complexity Tracking

> No unjustified violations.
