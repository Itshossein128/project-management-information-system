# Implementation Plan: Reference Project and Base Data

**Branch**: `develop` (feature directory `specs/051-a7-p1-project-reference`; Git branch is not renamed) | **Date**: 2026-11-10 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/051-a7-p1-project-reference/spec.md`

## Summary

Keep the existing project registration, life cycle, archive, undo, and work-breakdown behavior. Correct two proven gaps: the staff-only organization-unit test and permission text disagree with the approved access policy, and a project can still store a contract type that is not in the catalog. Add the missing steward create path for measurement units on the existing organization-references screen. Publish a versioned schedule-file contract with hand-counted fixtures and historical mismatch identifiers, without changing the importer.

## Technical Context

**Language/Version**: Python 3.12 with Django 4.2.11 and Django REST Framework; TypeScript on React Router 7.

**Primary Dependencies**: Existing `master_data` reference views, `projects` serializers, organization-references page. No new library.

**Storage**: PostgreSQL. No migration. Pytest uses its own test database.

**Testing**: pytest for the API and the fixture-count check. Browser check of the measurement-unit form on `/settings/org-refs`.

**Target Platform**: Local Linux development. The employer file stays in `real-data/`.

**Project Type**: Web application (API plus SPA).

**Performance Goals**: Catalog create and project save stay ordinary single-row requests. No batch import in this phase.

**Constraints**: Django stays on 4.2. Staff status alone must not gain write access. `real-data/plan.mpp` is not modified. Importer code is not modified. Destructive checks stay on the pytest database and project code `A7P1-REF`.

**Scale/Scope**: One reference scenario, three catalog writes, and nine small schedule examples. Existing life-cycle and work-breakdown tests are the regression net.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate |
| --- | --- |
| I. Server-enforced authorization | Pass. Write rules stay on the server. Staff is not granted a new exception. |
| II. Data integrity | Pass. No migration. Legacy contract-type values can be saved unchanged. New values must match the catalog. |
| III. Bilingual experience | Pass. New validation messages are added in English and Persian. The references screen uses existing translation calls with Persian defaults. |
| IV. Explicit safe mutations | Pass. Rejected creates do not leave rows. The employer file is not rewritten. |
| V. Minimal coherent changes | Pass. Extends the current reference views, project serializer, and references screen. No parallel archive or import path. |
| VI. Evidence-based verification | Pass. Completion requires pytest on the final tree plus a browser pass for the new form. Historical importer counts are not reported as new proof. |
| VII. Practical UX | Pass. The steward adds a measurement unit on the same screen as the other catalogs. |

Post-design re-check: the same gates hold. No constitution violation requires a justification.

## Project Structure

### Documentation (this feature)

```text
specs/051-a7-p1-project-reference/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── reference-catalog.md
│   └── schedule-reference.md
├── evidence/
│   ├── fixtures/
│   ├── control-figures.json
│   └── test_control_figures.py
├── tasks.md
├── traceability.md
├── evidence/verification.md
└── handoff.md
```

### Source Code (repository root)

```text
apps/api/core/master_data/permissions.py
apps/api/core/master_data/ref_serializers.py
apps/api/core/master_data/ref_views.py
apps/api/core/master_data/urls.py
apps/api/core/master_data/tests/test_org_refs.py
apps/api/core/master_data/tests/test_units.py
apps/api/core/projects/serializers.py
apps/api/core/projects/tests/test_a7_p1_reference_project.py
apps/api/core/locale/fa/LC_MESSAGES/django.po
apps/web/src/app/lib/api/central-data.ts
apps/web/src/app/routes/settings-org-refs.tsx
apps/web/src/app/routes/project-create-wizard.tsx
```

## Complexity Tracking

No constitution violations.
