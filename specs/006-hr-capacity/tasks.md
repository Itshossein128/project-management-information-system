---
description: "Task list for HR & Capacity Gap Closure (FR-HR)"
---

# Tasks: HR & Capacity Gap Closure

**Input**: Design documents from `/specs/006-hr-capacity/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md  
**Depends on**: existing `hr` leave/OT; `authentication.User`; `master_data.ProjectMember` / `OrganizationUnit`; soft-delete/audit (002); WBS/activities (004/005)

**Tests**: Include failing-then-passing pytest per story at **implement** time (TDD; same bar as 002–005). Implemented via `/speckit-implement` (TDD).

**Organization**: By user story for independent delivery.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: US1–US4 maps to spec user stories
- Exact file paths required

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm HR baseline and scaffold test/i18n stubs

- [X] T001 Verify existing leave/OT ViewSets, `AuditSoftDeleteModel` usage, and project URL include of `hr.urls` in `apps/api/core/hr/` and `apps/api/core/projects/urls.py` (smoke read of `hr/ENDPOINTS.md` + models)
- [X] T002 [P] Create placeholder test modules `apps/api/core/hr/tests/test_person_dossier.py`, `test_resource_allocations.py`, `test_capacity_exceptions.py`, `test_wage_acl_and_cost_estimate.py`
- [X] T003 [P] Add i18n stub keys for dossier fields, resource allocation, capacity conflict, capacity exception statuses, missing approved rate, and wage-hidden labels under `apps/web/src/app/locales/fa.json` and `en.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared permissions, dossier schema stubs, allocation/exception models, and route mounts all stories need

**⚠️ CRITICAL**: Complete before story implementation

### Tests

- [X] T004 [P] Write failing expectations for User fields `skills` (JSON list default `[]`), `qualifications` (JSON list default `[]`), `org_unit` FK null → OrganizationUnit, `supervisor` FK User null SET_NULL, `default_capacity_percent` Decimal default `100` in `apps/api/core/hr/tests/test_person_dossier.py`
- [X] T005 [P] Write failing expectations for `ResourceAllocation` fields per `data-model.md` (person, project, wbs null, activity null, start_date/end_date with end≥start, role Char, capacity_percent Decimal ≥0, capacity_hours Decimal null, work_location blank, supervisor null, status in `planned|active|completed|cancelled`, has_capacity_exception Bool default False, capacity_exception FK null, AuditSoftDeleteModel) in `apps/api/core/hr/tests/test_resource_allocations.py`
- [X] T006 [P] Write failing expectations that permission codes `view_hr`, `edit_hr`, `approve_hr`, `view_wage`, `edit_wage` exist in `apps/api/core/permissions/constants.py` catalog (assert importable) in `apps/api/core/hr/tests/test_wage_acl_and_cost_estimate.py` (or shared permissions assert helper)

### Implementation

- [X] T007 Add `view_hr`, `edit_hr`, `approve_hr`, `view_wage`, `edit_wage` to `apps/api/core/permissions/constants.py` and seed via permissions/data migration (follow existing Sprint permission migration pattern under `apps/api/core/`)
- [X] T008 Add User dossier fields on `authentication.User` in `apps/api/core/authentication/models.py`: `skills` JSONField default list, `qualifications` JSONField default list, `org_unit` FK to `master_data.OrganizationUnit` null, `supervisor` FK to User null SET_NULL, `default_capacity_percent` DecimalField default 100 + migration
- [X] T009 Add `ResourceAllocation` and stub `CapacityException` models per `data-model.md` (CapacityException status `draft|submitted|approved|rejected`; reason Text; requested_capacity_percent Decimal; decided_* audit; AuditSoftDeleteModel) in `apps/api/core/hr/models.py` + migration; wire `ResourceAllocation.capacity_exception` FK SET_NULL
- [X] T010 [P] Optionally add `'hr'` to project `CAPABILITY_CATALOG` in `apps/api/core/projects/models.py` (default enabled for existing projects) if feature toggle desired per research D5
- [X] T011 Register URL stubs under `apps/api/core/hr/urls.py` (included from `projects/urls.py`) for `resource-allocations/`, `capacity-exceptions/`, `approved-labor-rates/`, `labor-cost-estimate/`, and dossier routes per contracts (can 501 until story wires views)
- [X] T012 Re-run T004–T006 until PASS for schema/permission smoke (views may still be incomplete)

**Checkpoint**: Shared schema + permissions + route mounts ready

---

## Phase 3: User Story 1 - Extend person dossier (Priority: P1) 🎯 MVP

**Goal**: Persist skills, qualifications, org unit, supervisor, status/contact; gate new allocations for inactive persons

**Independent Test**: PATCH dossier with skills/quals/supervisor/org_unit; inactive person rejected on new allocation attempt; unauthorized edit denied

### Tests for User Story 1

- [X] T013 [P] [US1] Failing API tests for GET/PATCH dossier per `contracts/person-dossier.md` (`view_hr`/`edit_hr`; skills/qualifications lists; org_unit_id; supervisor_id) in `apps/api/core/hr/tests/test_person_dossier.py`
- [X] T014 [P] [US1] Failing tests: person with inactive/suspended status rejected for new ResourceAllocation with `person_inactive`; historical allocations remain listable in same module (or allocation test module)

### Implementation for User Story 1

- [X] T015 [US1] Implement dossier service (update skills/qualifications/org_unit/supervisor/default_capacity_percent; reject unauthorized) in `apps/api/core/hr/services/dossier_service.py`
- [X] T016 [US1] Serializers + views for dossier endpoints per `contracts/person-dossier.md` in `apps/api/core/hr/serializers.py` / `views.py` (or `dossier_views.py`); permissions `view_hr`/`edit_hr`; wire URLs
- [X] T017 [P] [US1] UI: person dossier edit (skills, qualifications, org unit, supervisor) in `apps/web/src/components/hr/` + API client `apps/web/src/app/lib/api/hr.ts`; surface from project people or settings route
- [X] T018 [US1] Re-run T013–T014 until PASS (allocation reject may wait until ResourceAllocation create exists — assert service helper if US2 not yet done)

**Checkpoint**: US1 independently verifiable (dossier + inactive guard helper)

---

## Phase 4: User Story 2 - Allocate person to project / WBS / activity (Priority: P1)

**Goal**: ResourceAllocation distinct from ProjectMember; date range, role, capacity %/hours, location, supervisor; list by project

**Independent Test**: Create valid allocation; appear on project list; end&lt;start rejected; membership can exist without allocation

### Tests for User Story 2

- [X] T019 [P] [US2] Failing API tests for list/create/GET/PATCH/soft-DELETE allocations per `contracts/resource-allocations.md` in `apps/api/core/hr/tests/test_resource_allocations.py`
- [X] T020 [P] [US2] Failing tests: derive `capacity_percent` from `capacity_hours` when % omitted using STANDARD_DAY_HOURS=8 (`hours/8*100`); reject end_date &lt; start_date; reject WBS/activity outside project (`scope_mismatch`) in same module

### Implementation for User Story 2

- [X] T021 [US2] Implement allocation CRUD service (scope checks; hours→% conversion; soft-delete; does not create ProjectMember) in `apps/api/core/hr/services/allocation_service.py`
- [X] T022 [US2] Serializers + views + URLs for resource-allocations (incl. query filters person/wbs/activity/status/from/to) per contract; permissions `view_hr`/`edit_hr`
- [X] T023 [P] [US2] UI: project allocations list + create/edit form in `apps/web/src/components/hr/` + route under project nav; API client methods in `apps/web/src/app/lib/api/hr.ts`
- [X] T024 [US2] Re-run T019–T020 until PASS (capacity_conflict path may still 501 until US3)

**Checkpoint**: US2 independently verifiable for in-capacity allocations

---

## Phase 5: User Story 3 - Capacity conflict warning and approved exception (Priority: P1)

**Goal**: Overlap sum vs available capacity; 409 capacity_conflict; exception draft→submit→approve/reject; over-capacity save only with approved exception

**Independent Test**: Existing 80% + new 50% overlapping → 409; approve exception with reason → allocation saved with `has_capacity_exception=True`; draft/rejected exception does not authorize

### Tests for User Story 3

- [X] T025 [P] [US3] Failing tests: capacity preview and create over available returns 409 `capacity_conflict` with available/committed/requested/overlapping_allocation_ids; available defaults to person `default_capacity_percent` (100) in `apps/api/core/hr/tests/test_capacity_exceptions.py` and/or `test_resource_allocations.py`
- [X] T026 [P] [US3] Failing tests: exception submit requires reason; approve/reject transitions; only `approved` allows allocation with `capacity_exception_id`; `exception_not_approved` otherwise; soft SoD note (approver==requester allowed for admin in v1) in `apps/api/core/hr/tests/test_capacity_exceptions.py`

### Implementation for User Story 3

- [X] T027 [US3] Implement capacity calculator (overlap date ranges; exclude soft-deleted and `cancelled`; sum capacity_percent) in `apps/api/core/hr/services/capacity_service.py`
- [X] T028 [US3] Implement CapacityException lifecycle (create/submit/approve/reject) in `apps/api/core/hr/services/exception_service.py`; integrate allocation create/update to require approved exception when conflict
- [X] T029 [US3] Wire capacity-exceptions serializers/views/URLs + `capacity-preview` GET per contracts; `approve_hr` for approve/reject; `edit_hr` for create/submit
- [X] T030 [P] [US3] UI: capacity conflict banner with committed/available; exception reason + manager approve/reject actions in `apps/web/src/components/hr/`
- [X] T031 [US3] Re-run T025–T026 until PASS

**Checkpoint**: US3 independently verifiable (SC-001/SC-002)

---

## Phase 6: User Story 4 - Sensitive rates and approved-rate cost estimate (Priority: P2)

**Goal**: Field-level wage ACL; ApprovedLaborRate; estimate = approved rate × approved hours or `missing_approved_rate`; progress isolation regression

**Independent Test**: Without `view_wage`, wage omitted from membership responses; estimate with rate returns amount; without rate returns warning null amount; labor headcount alone does not change activity progress

### Tests for User Story 4

- [X] T032 [P] [US4] Failing tests: membership/wage serializers omit `wage`/`wage_type` without `view_wage`; with permission include values in `apps/api/core/hr/tests/test_wage_acl_and_cost_estimate.py` (and/or master_data serializer tests)
- [X] T033 [P] [US4] Failing tests: `POST .../labor-cost-estimate/` uses ApprovedLaborRate×hours; missing rate → `warning: missing_approved_rate`, `amount: null` — never invent from ProjectMember.wage; `rate_amount` only with `view_wage` per `contracts/wage-acl-and-cost-estimate.md`
- [X] T034 [P] [US4] Failing/regression: create ResourceAllocation and/or labor-only daily report does not change ActivityProgress in `apps/api/core/hr/tests/test_wage_acl_and_cost_estimate.py` or extend existing field_reports progress isolation test

### Implementation for User Story 4

- [X] T035 [US4] Add `ApprovedLaborRate` model (project, person null, amount, currency, effective_from/to, AuditSoftDeleteModel) in `apps/api/core/hr/models.py` + migration if not already in T009
- [X] T036 [US4] Gate wage fields on ProjectMember read/write serializers in `apps/api/core/business_meta/serializers.py` and any other wage-exposing serializers; require `view_wage` / `edit_wage`
- [X] T037 [US4] Implement approved-rate CRUD + labor cost estimate service (no invented rates; no progress recalculation call) in `apps/api/core/hr/services/cost_estimate_service.py`; wire views/URLs
- [X] T038 [P] [US4] UI: redact wage without permission; optional approved-rate admin + estimate display in project HR/cost surfaces; API client updates
- [X] T039 [US4] Re-run T032–T034 until PASS

**Checkpoint**: All stories independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T040 [P] Update `apps/api/core/hr/ENDPOINTS.md` with dossier, allocations, exceptions, approved rates, labor-cost-estimate, permission codes
- [X] T041 [P] drf-spectacular summaries/tags on new HR endpoints
- [X] T042 [P] Verification checklist `specs/006-hr-capacity/checklists/verification.md` mapping SC-001–SC-005 to tests
- [X] T043 Run quickstart smoke commands from `specs/006-hr-capacity/quickstart.md` and record evidence categories (pytest vs typecheck vs UI)
- [X] T044 [P] Confirm leave/OT and manpower UIs unchanged; document allocation ≠ membership ≠ attendance ≠ progress in ENDPOINTS.md
- [X] T045 [P] Assign default role bundles including new HR/wage perms where appropriate in `apps/api/core/permissions/constants.py` ROLE maps

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup** → no deps
- **Phase 2 Foundational** → after Setup; **blocks** all stories
- **US1 (Phase 3)** → after Foundational (MVP)
- **US2 (Phase 4)** → after Foundational; uses ResourceAllocation model; inactive guard from US1 preferred
- **US3 (Phase 5)** → after Foundational; **practically after US2** (conflict on create/update)
- **US4 (Phase 6)** → after Foundational; independent of capacity math; can parallel US2/US3 if staffed
- **Polish** → after desired stories

### User Story Dependencies

```text
Foundational
├── US1 (person dossier)  ← MVP
├── US2 (resource allocation)
│     └── US3 (capacity conflict + exception)
└── US4 (wage ACL + approved-rate estimate)  ← can parallel US2/US3
```

### Parallel Opportunities

- T002/T003; T004/T005/T006; T013/T014; T019/T020; T025/T026; T032/T033/T034
- After Foundational: US1 and US4 can proceed in parallel
- US2 after model ready; US3 after US2 create path
- UI tasks marked [P] when different files from backend serializers

### Parallel Example: User Story 2

```bash
# Tests in parallel:
Task: T019 allocation API tests
Task: T020 hours→% and scope validation tests

# After service:
Task: T022 serializers/views
Task: T023 UI allocations panel  # [P] different files
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 + 2  
2. Phase 3 US1  
3. **STOP** — validate dossier PATCH + inactive allocation guard  
4. Demo person dossier fields

### Incremental Delivery

1. US1 → dossier  
2. US2 → allocations (in-capacity)  
3. US3 → capacity conflict + exception (SC-001/SC-002)  
4. US4 → wage ACL + estimate (SC-003/SC-004)  
5. Polish + quickstart evidence (SC-005)

### Suggested MVP scope

**US1 only** (T001–T018): delivers FR-HR-001 dossier gap without waiting on capacity engine.

---

## Notes

- Do **not** implement until `/speckit-implement` (or explicit user request)
- STANDARD_DAY_HOURS = 8 for hours→percent conversion
- Allocation never grants project membership or login
- Allocation/attendance never feed ActivityProgress
- Leave/OT/manpower rebuild is out of scope
- All tasks use checklist format with IDs and file paths

---

## Phase 8: Convergence

Remaining gaps found by `/speckit-converge` against spec/plan/tasks/constitution after implement. Do not renumber prior tasks.

- [X] T046 CRITICAL: Gate `ProjectMemberCreateSerializer` wage/`wage_type`/totals on `edit_wage` (same as write serializer) and add ACL create test in `apps/api/core/business_meta/serializers.py` / `hr/tests/test_wage_acl_and_cost_estimate.py` per FR-002 / Constitution I (contradicts)
- [X] T047 Redact daily-report `daily_rate` without `view_wage` in `apps/api/core/field_reports/serializers.py` and cover in wage ACL tests per FR-002 / `contracts/wage-acl-and-cost-estimate.md` (partial)
- [X] T048 Split capacity-exception UX: `edit_hr` can submit written reason; `approve_hr` approves/rejects separately (no auto-approve with canned reason) in `apps/web/src/app/routes/project-resource-allocations.tsx` / `components/hr/` per FR-005 / US3 (partial)
- [X] T049 [P] Add optional WBS, activity, capacity_hours, and supervisor fields to `AllocationFormPanel` and show navigable scope on the allocations list in `apps/web/src/components/hr/` per FR-003 / US2 (partial)
- [X] T050 [P] Allow editing org_unit and supervisor on person dossier UI wired to dossier PATCH in `PersonDossierPanel.tsx` per FR-001 / US1 (partial)
- [X] T051 [P] Add approved-labor-rate and labor-cost-estimate UI (or membership wage redact messaging) using `hr-capacity.ts` / membership surfaces per FR-008 / US4 / T038 (partial)
- [X] T052 Add automated regression: labor/manpower headcount alone does not change `ActivityProgress` in `hr/tests/` or field_reports tests per SC-004 / US4/AC4 / FR-007 (partial)
- [X] T053 [P] Add preferred `/api/v1/users/{user_id}/dossier/` route (or document project-scoped alt as chosen in ENDPOINTS.md) per `contracts/person-dossier.md` (missing)
- [X] T054 Allow authenticated self-read of non-sensitive dossier fields without `view_hr` in `PersonDossierView` per `contracts/person-dossier.md` (missing)
- [X] T055 [P] Soft SoD: when capacity-exception approver equals requester, include a warn flag in approve response (still allow admin) in `exception_service.py` per data-model validation / `contracts/capacity-exceptions.md` (missing)

---

## Phase 9: Convergence

Remaining gaps found by `/speckit-converge` against spec/plan/tasks/constitution after Phase 8 implement. Do not renumber prior tasks.

- [X] T056 Wire `fetchOrganizationUnits` from `apps/web/src/app/lib/api/central-data.ts` into `project-resource-allocations.tsx` and pass `orgUnits` to `PersonDossierPanel` so org unit can be selected/changed per FR-001 / US1 / T050 (partial)
