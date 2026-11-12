# Implementation Plan: Import Fidelity for WBS, Activities, and Schedule

**Branch**: `develop` (feature directory `specs/053-a7-p3-import-fidelity`; Git branch is not renamed) | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/053-a7-p3-import-fidelity/spec.md`

## Summary

Make preview and confirm use one resolved import plan. The parent is the parent identifier in the file. Summary rows become work packages. Leaves and milestones become activities. Supported duration, milestone, planned dates, percent, critical, and slack land on the activity, with the same critical and slack values copied onto the unapproved working-copy rows the Gantt already reads. Link delay converts only when it is an exact number of eight-hour days. Blocking structure errors write nothing, and they are judged before replacement. Import safety, file rejection, and the access checks stay as they are.

## Technical Context

**Language/Version**: Python 3.12 with Django 4.2.11 and Django REST Framework; TypeScript on React Router 7.

**Primary Dependencies**: Existing MSP XML, MPP conversion, and P6 XER parsers; `import_safety` for replacement, attribution, and the unapproved working copy; the import wizard. No new library and no second importer.

**Storage**: PostgreSQL. One nullable-column migration on `activities` for planned percent, critical, and slack. Existing rows stay null. `working_calendar` stays null on imported activities. Pytest uses its own test database. Project code `A7P3-IMPORT-FIDELITY` only.

**Testing**: pytest for parent, duration, lag, blocking, warning, date separation, and stored MPP/XML equality. One browser pass of the imported milestone and the calendar warning in Persian and English. A synchronous import-task call is not a separately running worker. The employer file `real-data/plan.mpp` is not modified.

**Target Platform**: Local Linux development against PostgreSQL and Redis.

**Project Type**: Web application (API plus SPA).

**Performance Goals**: Resolve one file in memory, then write once. No live Primavera connection and no extra report calculation.

**Constraints**: Django stays on 4.2. No spreadsheet importer, preview rewrite, earned-value change, or weakening of import safety. Historical 83-versus-79 counts are not pass targets. Calendars are reported as not applied.

**Scale/Scope**: The existing `.xml`, `.mpp`, and `.xer` preview and confirm paths, the activity fields the schedule screens read, and the milestone line on the Gantt and status report.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
| --- | --- |
| I. Server-enforced authorization | Pass. Preview, start, and apply keep the current project scope, membership, and `edit_wbs` checks. This feature adds no actor and no archive exception. |
| II. Data integrity | Pass. New activity columns are nullable and are not backfilled. Blocking errors and replacement refusal run before writes. The employer file bytes stay unchanged. Actual, forecast, planned, and approved dates stay on their own fields. |
| III. Bilingual experience | Pass. New warning and blocking codes have Persian and English text. The codes themselves stay language-independent. Browser check covers the milestone and the calendar warning in both languages. |
| IV. Explicit safe mutations | Pass. A blocking file writes nothing. Tests that import or replace data use the pytest database and the `A7P3-IMPORT-FIDELITY` project code. |
| V. Minimal coherent changes | Pass. One shared resolver feeds the current preview and both executors. Parsers stay in place. No second import wizard. |
| VI. Evidence-based verification | Pass. Completion needs pytest against stored rows, including a paired MPP/XML comparison when the converter runs, plus the browser check. Preview-only equality and an eager task call are not full proof. |
| VII. Practical UX | Pass. Preview and the saved result show the same parents, counts, and warnings. The Gantt and milestone report show a stored milestone. A calendar that was not applied is visible. |

Post-design re-check: the same gates hold. The migration adds nullable columns only. The contract adds no new permission and does not assign a default calendar. No constitution violation requires a justification.

## Project Structure

### Documentation (this feature)

```text
specs/053-a7-p3-import-fidelity/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── import-fidelity.md
├── spec.md
└── checklists/requirements.md
```

`tasks.md`, traceability, and verification evidence are later commands. This command does not create them.

### Source Code (repository root)

```text
apps/api/core/schedule/services/import_fidelity.py
apps/api/core/schedule/services/msp_import.py
apps/api/core/schedule/services/p6_import.py
apps/api/core/schedule/services/shared_import.py
apps/api/core/schedule/services/import_safety.py
apps/api/core/schedule/services/gantt_service.py
apps/api/core/projects/models.py
apps/api/core/projects/migrations/
apps/api/core/schedule/tests/test_a7_p3_import_fidelity.py
apps/api/core/locale/fa/LC_MESSAGES/django.po
apps/web/src/components/wbs/msp-import-wizard.tsx
apps/web/src/app/routes/project-schedule-gantt.tsx
apps/web/src/app/locales/en.json
apps/web/src/app/locales/fa.json
```

**Structure Decision**: Keep the monolithic API under `apps/api/core/schedule/` and the existing wizard. One new resolver module is the only parent, warning, and unit-conversion path, so MSP, MPP, and P6 cannot drift between preview and confirm. `import_safety` remains the replacement and working-copy gate and is called only after the resolver finds no blocking error.

## Complexity Tracking

No constitution violations.
