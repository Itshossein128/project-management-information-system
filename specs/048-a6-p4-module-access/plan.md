# Implementation Plan: پوشش یکسان دسترسی و محرمانگی در ماژول‌های موجود (A6-P4)

**Branch**: `develop` (feature directory `048-a6-p4-module-access`; no feature branch was created) | **Date**: 2026-11-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/048-a6-p4-module-access/spec.md`

## Summary

Apply the recorded A6-P1/P2/P3 access policy across all active operations in the 29 existing module areas, in three sequential internal packages. Extend the current project-permission helpers, SoD helper, wage/contact redaction, file signing checks, and UI permission guards. Do not invent a parallel ACL. Close IDOR and alternate-path gaps, align menus with effective permissions while keeping server enforcement independent, redact sensitive fields in nested payloads, require an explicit audited superuser self-approve exception, and enforce creator attribution for SoD-covered records. PM-16 and PM-17 are resolved by the 2026-11-06 clarifications and are not reopened.

## Technical Context

**Language/Version**: Python 3, Django 4.2, Django REST Framework; React Router 7 and TypeScript in `apps/web`

**Primary Dependencies**: Existing `permissions.project`, `permissions.sod`, `permissions.constants`, `RoleAccessChange` / `record_access_change`, project-scoped viewsets, stakeholder/wage redaction paths, storage signing, auth/offline actor context, and frontend `usePermission` / project context

**Storage**: PostgreSQL. Likely additive permission catalog entry for person-contact (separate from `view_sensitive_contacts`). Possible small schema or payload fields for explicit SoD break-glass reason and audit rows. No reset of the development database.

**Testing**: pytest on the independent test database for positive/negative matrix rows per package; preserve existing wage/contact/signing tests; targeted browser checks for menu/button alignment; real file service evidence where available, otherwise mark file coverage incomplete

**Target Platform**: Velora web application and API

**Project Type**: Web service covering existing module surfaces, not new business modules

**Performance Goals**: No new throughput target. User lookup stays capped (current 20-row limit). Redaction must not leak nested sensitive keys.

**Constraints**: Constitution 1.1.0. Organizational observation stays read-only and does not expand. Django remains 4.2. Three internal packages must close sequentially. No new financial engines, report builders, or workflow product features. Full history UI is P5. Customer acceptance is P6.

**Scale/Scope**: 29 module areas in three packages; requirements A6-R30, R33–R35, R38–R46 plus retest of R10/R31/R32/R36/R37 and P2/P3 contracts on consumers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Result | Reason |
|------|--------|--------|
| I. Server-enforced authorization | PASS | Plan keeps server checks as the boundary; UI hide is assistive only. Observation remains read-only and does not open wages, contacts, or SoD. |
| II. Data integrity | PASS | Cross-project relation rejection and creator attribution preserve consistent project scope and auditability. |
| III. Bilingual experience | PASS | Refusal and break-glass validation messages use gettext / locale catalogs. |
| IV. Safe mutations | PASS | Final approve and break-glass require explicit reason and durable audit; missing audit blocks the approve. |
| V. Minimal change | PASS | Extend current helpers and consumers; no parallel ACL or rewrite of unrelated modules. |
| VI. Evidence | PASS | Quickstart requires per-package pytest matrix, UI spot checks, and honest file-service evidence. |
| VII. Practical forms | PASS | Menus/buttons follow effective permission; allowed observers are not falsely blocked from allowed reads. |

Post-design: the same gates pass. No complexity exception is required.

## Project Structure

### Documentation (this feature)

```text
specs/048-a6-p4-module-access/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/module-access.md
├── checklists/requirements.md
└── spec.md
```

### Source Code (repository root)

```text
apps/api/core/permissions/
├── project.py
├── sod.py
├── constants.py
├── role_services.py
└── tests/
apps/api/core/projects/
├── member_views.py
├── member_serializers.py
├── stakeholder_views.py
├── services/report_export_service.py
└── tests/
apps/api/core/common/viewsets.py
apps/api/core/storage/
apps/api/core/cost_control/
apps/api/core/contracts/
apps/api/core/workflow/
apps/api/core/hr/
apps/api/core/inventory/
apps/api/core/field_reports/
apps/api/core/sub_reports/
apps/web/src/app/contexts/project-context.tsx
apps/web/src/app/contexts/auth-context.tsx
apps/web/src/app/hooks/
apps/web/src/components/
```

**Structure Decision**: Keep authorization in the existing permission helpers and project-scoped viewsets. Add person-contact as a catalog permission distinct from stakeholder contacts. Tighten `assert_not_self_final_approve` and wire `approve_commitment` and remaining final-approve paths through it. Deliver module coverage package-by-package against the operation matrix rather than rewriting modules.

## Complexity Tracking

No constitution violation requires a justification.
