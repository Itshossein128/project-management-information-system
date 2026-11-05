# Implementation Plan: نقش، سمت و مجوز مؤثر در محدوده پروژه (A6-P2)

**Branch**: `develop` (feature directory `046-a6-p2-project-roles`; no feature branch was created) | **Date**: 2026-11-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/046-a6-p2-project-roles/spec.md`

## Summary

Extend the existing role, job-title, and member-permission behavior. Local roles belong to one project. Custom roles with any current assignment cannot be deleted. Permission results expose inherit, grant, and deny. Several job titles can be selected without replacing access roles. Changes write a base history record. The finished history screen, invitations, and coverage of every business module stay later phases.

## Technical Context

**Language/Version**: Python 3, Django 4.2, Django REST Framework; React Router 7 and TypeScript in `apps/web`

**Primary Dependencies**: Existing role view, member form, permission summary, and gettext catalogs

**Storage**: PostgreSQL. Schema migration adds the project link, assignment protection, several titles, title defaults, and base history. Existing roles stay global and existing title links are copied.

**Testing**: pytest on the test database, plus a browser check of the member form

**Target Platform**: Velora web application and API

**Project Type**: Web service with existing role and member screens

**Performance Goals**: No new throughput target. Impact counts are one grouped query.

**Constraints**: Constitution 1.1.0. Project authority does not administer global roles. Observation does not grant role management. Django remains 4.2. The development database is not reset.

**Scale/Scope**: Role catalog, project member assignment, job-title selection, permission origin, and base history records

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Result | Reason |
|------|--------|--------|
| I. Server-enforced authorization | PASS | Local role changes require active member-management authority. Global role deletion stays with the existing organization role administrators. |
| II. Data integrity | PASS | Existing global roles and title links are preserved. Delete cannot cascade assignments. |
| III. Bilingual experience | PASS | Refusal messages are gettext strings shown by the existing forms. |
| IV. Safe mutations | PASS | Delete is refused while assignments exist and is rechecked inside a transaction. |
| V. Minimal change | PASS | The current Role, assignment, and member form are extended. |
| VI. Evidence | PASS | Quickstart names pytest modules and the member-form check. |
| VII. Practical forms | PASS | Origin is visible as inherit, grant, or deny, and delete explains remaining assignments. |

Post-design: the same gates pass. No complexity exception is required.

## Project Structure

### Documentation (this feature)

```text
specs/046-a6-p2-project-roles/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/project-roles.md
└── spec.md
```

### Source Code (repository root)

```text
apps/api/core/master_data/models.py
apps/api/core/master_data/migrations/
apps/api/core/permissions/services.py
apps/api/core/permissions/role_services.py
apps/api/core/projects/role_views.py
apps/api/core/projects/local_role_views.py
apps/api/core/projects/member_views.py
apps/api/core/projects/member_serializers.py
apps/api/core/projects/urls.py
apps/api/core/business_meta/views.py
apps/web/src/app/routes/settings-roles.tsx
apps/web/src/app/routes/project-members.tsx
apps/web/src/components/projects/add-member-drawer.tsx
apps/web/src/app/locales/fa.json
apps/web/src/app/locales/en.json
```

**Structure Decision**: Keep role storage in the current role model and member screen. Do not add a second authorization system.

## Complexity Tracking

No constitution violation requires a justification.
