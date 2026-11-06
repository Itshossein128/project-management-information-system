# Implementation Plan: گردش حساب و تیم پروژه (A6-P3)

**Branch**: `develop` (feature directory `047-a6-p3-team-lifecycle`; no feature branch was created) | **Date**: 2026-11-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/047-a6-p3-team-lifecycle/spec.md`

## Summary

Extend the existing user, membership, reset, and base-history behavior. A team manager selects an existing person. An account administrator creates a person through the current HR/admin endpoint. An invitation is the same membership until it is accepted, connected, or cancelled. Duplicate adds collapse to one membership. Account status controls sign-in, and leaving one project does not close the account. Real delivery uses the existing email or SMS settings and reports `sent` only after an operational send to the agreed test recipient. Last sign-in is recorded on successful login. Logout, password change, and account switch keep the current one-hour access rule and the actor-scoped offline queue.

## Technical Context

**Language/Version**: Python 3, Django 4.2, Django REST Framework; React Router 7 and TypeScript in `apps/web`

**Primary Dependencies**: Existing member view, HR user endpoint, password reset service, notification delivery settings, base access-history writer, and gettext catalogs

**Storage**: PostgreSQL. A schema migration adds invitation fields, pending-invitation uniqueness, and protects membership from user deletion. A data migration aligns account status without re-enabling a blocked person. Existing users and memberships stay.

**Testing**: pytest on the test database, plus a browser check of the team screen and of the account switch. The offline queue stays the existing actor-scoped queue.

**Target Platform**: Velora web application and API

**Project Type**: Web service with the existing team and account screens

**Performance Goals**: No new throughput target. User lookup stays limited to 20 rows. The team screen filters the existing member list.

**Constraints**: Constitution 1.1.0. Project member management does not administer organizational accounts. Observation does not grant member management. Django remains 4.2. The development database is not reset. No new messaging provider. The offline engine is not redesigned. The finished history screen is not built.

**Scale/Scope**: Person selection and creation, invitation connect and accept, membership conflict handling, account and membership status, team list labels, session boundary, and base history for those actions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Result | Reason |
|------|--------|--------|
| I. Server-enforced authorization | PASS | Member writes require active `manage_members`. Account creation and account status stay on `IsHrOrAdmin`. A viewer, inactive member, and explicit deny do not pass. |
| II. Data integrity | PASS | One person can belong to many projects. One membership per person and project is enforced by the existing constraint and a transactional conflict response. Old accounts are aligned without being re-enabled. |
| III. Bilingual experience | PASS | Refusal messages and the five membership statuses use the existing gettext and locale catalogs. |
| IV. Safe mutations | PASS | Leaving a project or suspending an account does not delete the person or the membership. Admin deletion is refused when history exists. |
| V. Minimal change | PASS | The current user, membership, reset, delivery settings, and history writer are extended. No second account or invitation system is added. |
| VI. Evidence | PASS | Quickstart names pytest modules, the offline actor check, and the team-screen browser check. |
| VII. Practical forms | PASS | The team screen can select, create within authority, connect, or cancel. An invitation without a person is no longer an edit dead end. |

Post-design: the same gates pass. No complexity exception is required.

## Project Structure

### Documentation (this feature)

```text
specs/047-a6-p3-team-lifecycle/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/team-lifecycle.md
└── spec.md
```

### Source Code (repository root)

```text
apps/api/core/authentication/models.py
apps/api/core/authentication/admin.py
apps/api/core/authentication/backends.py
apps/api/core/authentication/services.py
apps/api/core/authentication/views.py
apps/api/core/authentication/urls.py
apps/api/core/authentication/migrations/
apps/api/core/config/settings.py
apps/api/core/master_data/models.py
apps/api/core/master_data/migrations/
apps/api/core/projects/member_views.py
apps/api/core/projects/member_serializers.py
apps/api/core/projects/services/__init__.py
apps/api/core/projects/urls.py
apps/api/core/projects/tests/test_team_lifecycle.py
apps/api/core/authentication/tests/test_account_lifecycle.py
apps/web/src/app/routes/project-members.tsx
apps/web/src/app/routes/hr/users.tsx
apps/web/src/components/projects/add-member-drawer.tsx
apps/web/src/app/lib/api/members.ts
apps/web/src/app/contexts/auth-context.tsx
apps/web/src/app/locales/fa.json
apps/web/src/app/locales/en.json
apps/api/core/locale/fa/LC_MESSAGES/django.po
```

**Structure Decision**: Keep people in the current user model and team membership in `ProjectMember`. Reuse the HR user endpoint, the member view, the reset service, and `record_access_change`.

## Complexity Tracking

No constitution violation requires a justification.
