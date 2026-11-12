# Implementation Plan: Schedule Import Experience

**Branch**: `develop` (feature directory `specs/054-a7-p4-import-experience`; Git branch is not renamed) | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/054-a7-p4-import-experience/spec.md`

## Summary

Complete the existing schedule import journey so the planner sees the file, the recognized kind, the mode, the structure, and figures that match what is stored. Warnings stay distinct from blocking failures and are translated from stable codes in the active language. A second click or drop cannot change the attempt, a late result stays bound to the file, project, and account that started it, and a lost connection is resumed from that same attempt. No second importer, no new export, and no migration.

## Technical Context

**Language/Version**: Python 3.12 with Django 4.2.11 and Django REST Framework; TypeScript on React Router 7.

**Primary Dependencies**: The existing MSP/MPP and P6 preview and confirm paths, `import_fidelity` counts and warning codes, `import_safety` replacement and in-flight replay, and `MspImportWizard`. No new library.

**Storage**: PostgreSQL. No schema migration. Preview and the import-job result JSON gain display fields only. The browser remembers the open attempt in `sessionStorage` by user and project, with no file bytes. Pytest uses its own database and project code `A7P4-IMPORT-EXPERIENCE`.

**Testing**: pytest for the shared figures, replacement projection, and unchanged safety and fidelity tests. One browser pass of success, warning, recoverable rejection, refused replacement, interrupted status, and a prevented second file, in Persian and English, on a desktop width and a phone width, including keyboard only. A synchronous task call is not a separately running worker.

**Target Platform**: Local Linux development against PostgreSQL and Redis. The web app is the existing SPA.

**Project Type**: Web application (API plus SPA).

**Performance Goals**: One parse per preview. The replacement projection is a read of the same protection checks the confirm path already runs. No second parse and no new report.

**Constraints**: Django stays on 4.2. Code changes wait until `specs/052-a7-p2-import-safety` and `specs/053-a7-p3-import-fidelity` each have a handoff. This plan does not start those handoffs and does not treat their task checkmarks as one. The 2026-11-10 audit counts are not pass targets. No spreadsheet import, preview rewrite, live Primavera connection, earned-value change, date picker, or weaker access rule.

**Scale/Scope**: The one import wizard and the two preview, start, and status paths already used for `.mpp`, `.xml`, and `.xer`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
| --- | --- |
| I. Server-enforced authorization | Pass. Preview, start, and status keep membership and `edit_wbs`. The screen translates a refusal; it does not grant import. The remembered attempt is keyed by the signed-in user and project and is not a credential. |
| II. Data integrity | Pass. No migration. Display figures are derived from the resolved plan and from rows actually inserted. Preview and a refused replacement write nothing. |
| III. Bilingual experience | Pass. New and missing messages are Persian and English. Codes stay language-independent. The browser pass covers both languages. This journey does not change a date picker. |
| IV. Explicit safe mutations | Pass. Confirm still uses the safety gate and the in-flight replay. Tests that write use the pytest database and `A7P4-IMPORT-EXPERIENCE`. Closing the screen does not cancel or invent success. |
| V. Minimal coherent changes | Pass. The current wizard, preview payload, and job result are extended. No second journey and no download. |
| VI. Evidence-based verification | Pass. Completion needs pytest against stored rows plus the browser journeys. A green typecheck or a mocked status call is not that proof. |
| VII. Practical UX | Pass. The result shows every control figure and the full warning text. File choice, mode, and confirm stay keyboard reachable. A phone-width panel keeps the file name and warnings readable. |

Post-design re-check: the same gates hold. The contract adds no permission, no table, and no sensitive field. The client record stores the attempt id, file name, kind, and mode only. No constitution violation requires a justification.

## Project Structure

### Documentation (this feature)

```text
specs/054-a7-p4-import-experience/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── import-experience.md
├── spec.md
└── checklists/requirements.md
```

`tasks.md`, traceability, and verification evidence are later commands. This command does not create them.

### Source Code (repository root)

```text
apps/api/core/schedule/services/import_fidelity.py
apps/api/core/schedule/services/import_safety.py
apps/api/core/schedule/services/msp_import.py
apps/api/core/schedule/services/p6_import.py
apps/api/core/schedule/services/shared_import.py
apps/api/core/schedule/views.py
apps/api/core/schedule/tests/test_a7_p4_import_experience.py
apps/web/src/components/wbs/msp-import-wizard.tsx
apps/web/src/app/lib/api/msp.ts
apps/web/src/app/locales/en.json
apps/web/src/app/locales/fa.json
```

**Structure Decision**: Keep the wizard and both import families. `import_fidelity` remains the source of preview figures. `import_safety` remains the replacement gate and supplies the read-only removal projection. The wizard renders those figures, translates codes, and binds one attempt to one file, project, and account.

## Complexity Tracking

No constitution violations.

## Implementation correction authorized on 2026-11-12

The real-file browser pass exposed a pre-existing WBS tree-path collision. The user requested root-cause investigation and solution selection and confirmed that preserving development data was not a priority. The reproduced cause was ordering the physical tree by mutable `wbs_code` while soft deletion and renumbering mutate that field. The correction extends scope to `projects/models.py`, `wbs/services.py`, and focused WBS regression tests: structural position determines order, display codes do not. No schema migration, data reset or tree rebuild was required. Integrated tests and the previously failing populated-database MPP journey pass; evidence is recorded under `evidence/wbs-path-root-cause.md`.
