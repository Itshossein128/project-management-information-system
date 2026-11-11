# Implementation Plan: Import Safety and History

**Branch**: `develop` (feature directory `specs/052-a7-p2-import-safety`; Git branch is not renamed) | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/052-a7-p2-import-safety/spec.md`

## Summary

Stop schedule replacement from physically deleting activities, work-breakdown nodes, and locked baseline rows. Refuse replacement before any write when progress, cost, documents, live activities, or a locked or approved baseline would be lost. When nothing is protected, remove the existing structure with the same soft delete already used by forced template replacement. An append or a repeated file must not create duplicate rows or a new current baseline when nothing new was added. Recheck membership, `edit_wbs`, archive state, and the acting user when the import is applied. Do not attribute rows to the oldest account.

## Technical Context

**Language/Version**: Python 3.12 with Django 4.2.11 and Django REST Framework; TypeScript on React Router 7.

**Primary Dependencies**: Existing MSP/MPP and P6 import services, import jobs, work-breakdown soft delete, and the import wizard. No new library.

**Storage**: PostgreSQL. No schema migration. Import jobs, baselines, activities, and work-breakdown nodes already store the actor and the outcome. Pytest uses its own test database.

**Testing**: pytest for service and API cases, including a project that already has history. One browser pass of the import wizard in Persian and English. A synchronous call of the import task is not reported as a separately running worker.

**Target Platform**: Local Linux development against PostgreSQL and Redis.

**Project Type**: Web application (API plus SPA).

**Performance Goals**: One project import at a time. The apply step locks that project row, then either refuses or writes once.

**Constraints**: Django stays on 4.2. No new schedule-versioning scheme. No parser or preview rewrite. No spreadsheet importer, live Primavera sync, or weakening of the A.6 access policy. Destructive checks use project code `A7P2-IMPORT-SAFETY` only inside the pytest database. The 2026-11-10 audit is history, not proof of the final tree.

**Scale/Scope**: The existing `.xml`, `.mpp`, and `.xer` confirm paths. Field mapping inside those files stays with the next stage.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
| --- | --- |
| I. Server-enforced authorization | Pass. Preview, start, status, and apply keep project scope. `edit_wbs` and active membership are checked again at apply time. Observation does not authorize import. Archive is an additional server gate. |
| II. Data integrity | Pass. No migration. Locked and approved baseline rows stay. Unprotected replacement soft-deletes, matching template replacement. A failed apply rolls back with the existing transaction. |
| III. Bilingual experience | Pass. New refusal and result text is available in Persian and English. Stable error codes stay language-independent. |
| IV. Explicit safe mutations | Pass. Protected replacement is refused before writes, with a reason. Tests that delete or replace data run only on the pytest database. |
| V. Minimal coherent changes | Pass. Extend the current MSP and P6 execute paths, their shared writer, the start/apply checks, and the existing wizard. No second importer. |
| VI. Evidence-based verification | Pass. Completion needs pytest on a project with history, plus a browser check of the refusal. An empty-project success and an eager task call are not reported as full proof. |
| VII. Practical UX | Pass. The planner sees the refusal in the import confirmation journey before project data changes. A no-change result is not labeled as a changed plan. |

Post-design re-check: the same gates hold. The contract adds no new table and no new administrator exception. No constitution violation requires a justification.

## Project Structure

### Documentation (this feature)

```text
specs/052-a7-p2-import-safety/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── import-safety.md
├── spec.md
└── checklists/requirements.md
```

`tasks.md`, traceability, and verification evidence are later commands. This command does not create them.

### Source Code (repository root)

```text
apps/api/core/schedule/services/import_safety.py
apps/api/core/schedule/services/msp_import.py
apps/api/core/schedule/services/p6_import.py
apps/api/core/schedule/services/shared_import.py
apps/api/core/schedule/views.py
apps/api/core/schedule/tasks.py
apps/api/core/schedule/tests/test_a7_p2_import_safety.py
apps/api/core/locale/fa/LC_MESSAGES/django.po
apps/web/src/components/wbs/msp-import-wizard.tsx
apps/web/src/app/locales/en.json
apps/web/src/app/locales/fa.json
```

**Structure Decision**: Keep the monolithic API under `apps/api/core/schedule/` and the existing wizard. One new service module holds the shared refusal and recheck so MSP and P6 cannot drift. Parsers, preview builders, and template application stay in place.

## Complexity Tracking

No constitution violations.
