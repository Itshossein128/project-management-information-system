# Implementation Plan: تثبیت سیاست دسترسی و رفع نقص‌های فوری (A6-P1)

**Branch**: `develop` (feature directory `045-a6-p1-access-policy`; no feature branch was created) | **Date**: 2026-11-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/045-a6-p1-access-policy/spec.md`

## Summary

Record and enforce the customer observation exception on the paths selected for
this phase, and close the three reproduced access defects. A system
administrator or superuser may read general project information without active
membership. They may not write, delete, or approve on those selected paths
without an active membership and the matching permission. Staff and human
resources do not receive the exception. Unknown role ids fail atomically.
Organization visitors cannot write the legacy item catalog. Full module
coverage stays in P4, and the independent final acceptance stays in P6.

## Technical Context

**Language/Version**: Python 3, Django 4.2, Django REST Framework; React Router 7 and TypeScript in `apps/web`

**Primary Dependencies**: Existing permission helpers, gettext catalogs, and the member form. No new service or authorization framework.

**Storage**: PostgreSQL. One data migration inserts `delete_activities` rows. No schema change. The development database is not reset.

**Testing**: pytest on the API test database, plus a browser check of the member form error.

**Target Platform**: Velora web application and API.

**Project Type**: Web service with an existing member form.

**Performance Goals**: No new throughput target. Role validation is one existence query before any write.

**Constraints**: Constitution 1.1.0. Observation is read-only, stays inside the single installed authorization realm, and does not reveal sensitive fields or bypass approval separation. Django remains 4.2.

**Scale/Scope**: Selected paths only: member roles, project positions and direct callers of the membership helper, legacy items, and one activity edit/delete/approve example.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Result | Reason |
|------|--------|--------|
| I. Server-enforced authorization | PASS | Selected paths check active membership or the named read exception on the server. Writes on those paths ignore the old full bypass. |
| II. Data integrity | PASS | Role replacement is transactional. The permission backfill preserves existing delete ability. No history rows are removed. |
| III. Bilingual experience | PASS | The role error is a gettext message, shown by the existing member form. |
| IV. Safe mutations | PASS | Invalid role lists do not create or clear memberships. |
| V. Minimal change | PASS | Existing helpers and the item read-only gate are extended. `_is_global_admin` is left in place for unselected modules. |
| VI. Evidence | PASS | Quickstart names pytest modules and the member-form check, and states what they do not prove. |
| VII. Practical forms | PASS | The member form surfaces the server refusal and does not close as a successful save. |

Post-design: the same gates pass. The single-realm limit is documented in research and is not a second organization grant. No complexity exception is required.

## Project Structure

### Documentation (this feature)

```text
specs/045-a6-p1-access-policy/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/selected-access.md
├── spec.md
└── checklists/requirements.md
```

### Source Code (repository root)

```text
apps/api/core/
├── permissions/project.py
├── permissions/constants.py
├── business_meta/permissions.py
├── business_meta/views.py
├── projects/member_views.py
├── projects/member_serializers.py
├── projects/services/__init__.py
├── inventory/views.py
├── schedule/activity_views.py
└── locale/fa/LC_MESSAGES/django.po

apps/web/src/components/projects/add-member-drawer.tsx
```

**Structure Decision**: Keep the work inside the current API permission and
view modules and the existing member drawer. Do not add a parallel access
service.

## Design notes

Research decisions, entities, contracts, and the validation commands are in
the sibling files. Implementation follows those files rather than restating
them here.

Selected-path enforcement:

- Strict project permission checks do not call `_is_global_admin`.
- Organizational observation is superuser or group `admin`, and only for reads
  of general operational data on the position helper.
- `CanViewProjectMembers` requires an active membership unless that observation
  applies.
- Position writes and member role changes require active membership plus
  `manage_members`.
- `ItemViewSet` gains the existing visitor read-only gate.
- Activity delete requires the new `delete_activities` codename after the
  backfill migration. Measurement approval already requires `approve_reports`.

Out of scope for code in this phase: project-local roles, multiple job titles
on one membership, invitation flow, history screens, wage and contact
redaction, emergency approval accounts, and every remaining caller of
`_is_global_admin`.

## Complexity Tracking

No constitution violation requires a justification.
