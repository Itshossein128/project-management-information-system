# Implementation Plan: تکمیل ممیزی و تاریخچه قابل استفاده (A6-P5)

**Branch**: `049-a6-p5-access-history` | **Date**: 2026-11-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/049-a6-p5-access-history/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Deliver a usable access-history screen and durable evidence for access changes by extending `RoleAccessChange` and `record_access_change`. Sensitive access updates commit only together with their trail. Readers are limited to the project team manager and the organizational administrator or superuser. Secrets are redacted before save and before display. Successful login, recovery, final approval, and sensitive export get explicit rows. Missing historical values stay labeled unknown.

## Technical Context

**Language/Version**: Python 3.12 with Django 4.2.11 and Django REST Framework; TypeScript on React Router 7 and Vite

**Primary Dependencies**: Existing `RoleAccessChange`, `record_access_change`, project access-change list, audit redaction walk, drf-spectacular, TanStack Query, i18next

**Storage**: PostgreSQL. No new database. Redis remains required for the API process and is not the history store.

**Testing**: pytest for the API, on the isolated test database. Browser check for the Persian and English screens. Typecheck is a separate frontend signal.

**Target Platform**: Linux server for the API and a desktop browser for the history screens

**Project Type**: Web application, `apps/api` and `apps/web`

**Performance Goals**: A filtered page of fifty rows returns in the same interactive range as the current member list. No new batch or export job.

**Constraints**: Django stays on 4.2. Do not install the full development requirements file. Do not reset the development database. Synchronous tests do not prove a later asynchronous worker. History rows are not editable. Secrets never appear in stored JSON or responses.

**Scale/Scope**: One project screen, one organization screen, filters, pagination, redaction, and the missing sensitive events. Not a SIEM, not a full business-entity history, and not a backfill of old events.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Before research | After design |
| --- | --- | --- |
| I. Server-enforced authorization | Pass. History reads will check `manage_members` or the named organization observation accounts. Client hiding is not the boundary. | Pass. Contracts return 403 or 404 and omit other projects. Observation does not reveal secrets. |
| II. Data integrity | Pass. Existing rows stay. Indexes are additive. | Pass. No backfill. Rollback of a sensitive change includes its missing trail. |
| III. Bilingual experience | Pass. Labels and errors are planned in Persian and English. Action codes stay stable. | Pass. Quickstart requires both locales. |
| IV. Safe mutations | Pass. History has no delete API. Failure of a sensitive trail does not announce success. | Pass. The transaction rule is limited to sensitive access changes. |
| V. Minimal coherent changes | Pass. Extend the current model, service, and project endpoint. | Pass. No second history table and no new permission codename. |
| VI. Evidence-based verification | Pass. Pytest, browser, and the sync-versus-delivery limit are separate. | Pass. Quickstart names the new test module and the limit. |
| VII. Practical UX | Pass. Filters and a paged table, not a raw event dump. | Pass. Unknown values have an explicit label. |

No gate violations. Complexity tracking is empty.

## Project Structure

### Documentation (this feature)

```text
specs/049-a6-p5-access-history/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/access-history.md
├── checklists/requirements.md
└── spec.md
```

`tasks.md` is created later by `/speckit-tasks`.

### Source Code (repository root)

```text
apps/api/core/
├── master_data/models.py
├── master_data/migrations/
├── permissions/role_services.py
├── permissions/tests/test_access_history.py
├── projects/local_role_views.py
├── projects/urls.py
├── authentication/views.py
└── audit/middleware.py

apps/web/src/
├── app/routes/project-members.tsx
├── app/routes/access-history.tsx
├── app/lib/api/members.ts
└── app/locales/fa.json
└── app/locales/en.json
```

**Structure Decision**: Keep the monorepo boundary. The API owns the trail and authorization. The web app only renders the contract. Request `AuditLog` stays the best-effort write log and is not the access-history screen.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations.
