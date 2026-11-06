---
description: "Task list for A6-P4 uniform module access and confidentiality"
---

# Tasks: پوشش یکسان دسترسی و محرمانگی در ماژول‌های موجود (A6-P4)

**Input**: Design documents from `/specs/048-a6-p4-module-access/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required by the spec acceptance scenarios, quickstart, constitution, and A6-P4 prompt. Assert the desired behavior. Write the new test first and make it fail before the implementation. Do not leave a test as an expected failure. Preserve existing wage, stakeholder-contact, and attachment-signing tests; re-run them when those areas change. Do not treat mocks of file signing as real file-service evidence.

**Organization**: Tasks are grouped by user story. Three internal packages (US9) are sequential: close package N evidence before starting package N+1 consumer rollout.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: Which user story this task belongs to (US1–US9)
- Setup, foundational, and polish tasks have no story label

## Path Conventions

- API: `apps/api/core/`
- Web: `apps/web/src/`
- Feature docs: `specs/048-a6-p4-module-access/`
- Tests use the repository `.env` and the test database. Do not drop or recreate the development database. Django stays on 4.2.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Working artifacts for the 29-area matrix and package gates

- [X] T001 Create the empty operation-matrix workbook template at `specs/048-a6-p4-module-access/matrix/README.md` defining columns: module area, operation, methods/paths, roles, projects A/B, expected allow/deny, result, evidence, defect class (`policy` | `project-scope` | `sensitive-field` | `action/SoD` | `file` | `UI` | `queue/session`), N/A reason. Do not mark any row green.
- [X] T002 [P] Create package trackers `specs/048-a6-p4-module-access/matrix/package-1.md`, `package-2.md`, and `package-3.md` listing M01–M10+M14, M13+M15–M21+M26, and M11–M12+M22–M25+M27–M29 respectively with status `not_started`.
- [X] T003 [P] Add a draft A6-R → FR/Story → Task → Test mapping stub at `specs/048-a6-p4-module-access/traceability.md` with columns Requirement, Result (`حفظ شد` | `اصلاح شد` | `اضافه شد` | `جزئی باقی است`), What changed, Evidence. Leave rows empty until package evidence exists.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared permission, observation, SoD, redaction, and project-scope helpers every story uses

**⚠️ CRITICAL**: No user story work starts until this phase is complete

- [X] T004 [P] Add catalog codename `view_person_contacts` (label: view person/employee contact fields) in `apps/api/core/permissions/constants.py`, distinct from `view_sensitive_contacts`. Do not grant it via observation, staff, or bare `hr`. Document default role grants only where an existing product role already needs person-contact visibility; otherwise leave unassigned until role matrix review.
- [X] T005 [P] Extend `record_access_change` usage contract in `apps/api/core/permissions/role_services.py` so break-glass actions can store `action='sod_break_glass'`, reason inside `after`, exception flag, and before/after snapshots using existing `RoleAccessChange` JSON fields in `apps/api/core/master_data/models.py`. Do not build the P5 history screen.
- [X] T006 Rewrite `assert_not_self_final_approve` in `apps/api/core/permissions/sod.py` per Clarifications Q2/Q3: null `created_by` must not pass; superuser must not auto-bypass; optional explicit break-glass path requires non-empty reason and returns a structured result the caller must audit before approving. Update `apps/api/core/permissions/tests/test_sod.py` expectations in the same change only after the failing rewrite tests in US8 exist—during foundation, keep the helper signature documented in `specs/048-a6-p4-module-access/contracts/module-access.md`.
- [X] T007 [P] Add a shared nested redaction helper in `apps/api/core/permissions/redaction.py` (new) that walks dict/list payloads and strips wage/rate and contact keys unless the supplied permission set allows them. Reuse from report export later; do not change call sites yet.
- [X] T008 [P] Add `assert_same_project` (or equivalent) in `apps/api/core/permissions/project.py` that rejects related object ids whose `project_id` differs from the request project, raising a coded validation error without partial save. Do not expand observation.
- [X] T009 Document the observation vs write rule in a short comment block on `has_organizational_observation` and replace remaining unjustified write bypass notes for `_is_global_admin` consumers inventory in `specs/048-a6-p4-module-access/research.md` appendix list of files still calling `_is_global_admin` for writes. Implementation of each consumer stays in story/package tasks.

**Checkpoint**: Catalog, SoD contract, redaction helper, and project-scope helper exist. User stories can proceed.

---

## Phase 3: User Story 1 - Project isolation and foreign ids (Priority: P1) 🎯 MVP

**Goal**: A member of project A cannot read or mutate project B data via id swap; observation stays read-only general data.

**Independent Test**: Two projects; A-only member uses B ids on read/write/action; B data never appears; same operation on A succeeds; inactive/non-member denied; observation reads general data and cannot write.

### Tests for User Story 1

- [X] T010 [US1] Write failing tests in `apps/api/core/projects/tests/test_module_access_project_scope.py` covering project list/detail isolation, a representative related-id bind rejection using `assert_same_project`, inactive member deny, and observation read-without-write on a selected project path.

### Implementation for User Story 1

- [X] T011 [US1] Enforce active-membership or observation-only reads on remaining project queryset filters in `apps/api/core/projects/views.py` and ensure writes still require active membership plus codename via `active_member_has_codename` where P1 left `_is_global_admin` write bypass.
- [X] T012 [US1] Wire `assert_same_project` into `apps/api/core/common/viewsets.py` `ProjectScopedViewSet` create/update paths and into `apps/api/core/documents/serializers.py` for related project objects.
- [X] T013 [P] [US1] Add Persian/English messages for project-scope mismatch in `apps/api/core/locale/fa/LC_MESSAGES/django.po`, `apps/web/src/app/locales/fa.json`, and `apps/web/src/app/locales/en.json`.

**Checkpoint**: US1 is independently testable on core project and scoped viewset paths.

---

## Phase 4: User Story 2 - Direct, legacy, and import/export paths (Priority: P1)

**Goal**: Alternate/legacy/import/export/download paths do not grant more than the canonical policy.

**Independent Test**: For each inventoried alternate path in the active package, denied role fails the same way as the canonical path; shared org catalogs are not treated as project-private.

### Tests for User Story 2

- [X] T014 [US2] Write failing probe tests in `apps/api/core/permissions/tests/test_alternate_path_parity.py` for at least: legacy inventory item writes (visitor), one project-scoped canonical vs alias pair, and one import or export path, asserting equal or stricter denial on the alternate route.

### Implementation for User Story 2

- [X] T015 [US2] Inventory live URLs/actions for package-1 areas into `specs/048-a6-p4-module-access/matrix/package-1.md` from `apps/api/core/config/urls.py` and each module `urls.py` listed in the prompt. Mark missing operations N/A with reason.
- [X] T016 [US2] Align legacy/global inventory write guards in `apps/api/core/inventory/views.py` and `apps/api/core/business_meta/permissions.py` so alternate paths cannot exceed canonical policy; keep shared org catalog semantics.
- [X] T017 [P] [US2] Fix any package-1 alias route that skips `ProjectScopedViewSet` or active-membership checks discovered in T015.

**Checkpoint**: Alternate-path probes fail closed; package-1 inventory exists.

---

## Phase 5: User Story 3 - Revocation during queue and retry (Priority: P1)

**Goal**: After membership/permission revoke or account switch, retry and offline queue use the current actor and permission.

**Independent Test**: Queue an allowed action, revoke permission or switch account, reconnect/retry; forbidden submit fails; prior actor payload is not sent as the new user.

### Tests for User Story 3

- [X] T018 [US3] Write failing tests covering revoke-then-retry authorization in `apps/api/core/sub_reports/tests/test_unit_report_permissions.py` (or a new `apps/api/core/permissions/tests/test_revocation_retry.py`) and document the client queue actor expectation for `apps/web/src/app/contexts/auth-context.tsx`.

### Implementation for User Story 3

- [X] T019 [US3] Ensure server endpoints re-evaluate effective permission on each request (no cached allow across revoke) for unit-report and field-report sync entry points in `apps/api/core/sub_reports/unit_report_views.py` and `apps/api/core/field_reports/` sync views.
- [X] T020 [US3] In `apps/web/src/app/contexts/auth-context.tsx` and offline queue usage, keep queue items actor-scoped; on account switch, do not submit the previous actor’s payloads; surface a recoverable localized message when permission is gone.

**Checkpoint**: Revocation and account-switch queue behavior are testable.

---

## Phase 6: User Story 4 - Menu/button vs server enforcement (Priority: P1)

**Goal**: UI reflects effective permission; hidden controls stay denied on direct API; observation accounts are not falsely blocked from allowed reads.

**Independent Test**: Denied role sees no forbidden control and direct call fails; observation account can open allowed read UI without effective write controls.

### Tests for User Story 4

- [X] T021 [P] [US4] Add failing API+permission fixture tests in `apps/api/core/permissions/tests/test_ui_server_parity_fixtures.py` that document expected allow/deny pairs for observer, denied member, and observation admin on one representative write codename.
- [X] T022 [P] [US4] Add a failing frontend permission-guard test or story checklist in `apps/web/src/app/contexts/project-context.tsx` consumers noting any screen still using global group instead of project effective permission.

### Implementation for User Story 4

- [X] T023 [US4] Align `apps/web/src/app/contexts/project-context.tsx` and permission hooks so menus/buttons use effective project permissions, including observation read without write affordances.
- [X] T024 [US4] Fix representative screens that gate only on global `admin`/`hr` groups when project permission should decide, starting with member/settings entry points under `apps/web/src/app/routes/`.

**Checkpoint**: UI assistive checks match server policy on the representative surfaces.

---

## Phase 7: User Story 5 - Sensitive fields and nested outputs (Priority: P1)

**Goal**: Wage/rate and nested report/dashboard/export payloads redact without the right permission; allowed data for other roles is not corrupted.

**Independent Test**: Two roles read the same nested payload; denied role never sees wage/rate; allowed role still sees permitted values.

### Tests for User Story 5

- [X] T025 [US5] Extend or add failing nested redaction tests in `apps/api/core/hr/tests/test_wage_acl_and_cost_estimate.py` and a new `apps/api/core/projects/tests/test_nested_export_redaction.py` proving nested wage keys are stripped without `view_wage`.
- [X] T026 [P] [US5] Keep existing stakeholder contact ACL tests green in `apps/api/core/projects/tests/test_stakeholder_contacts_acl.py` while adding a case that observation without `view_sensitive_contacts` sees no contacts.

### Implementation for User Story 5

- [X] T027 [US5] Deepen `_redact_wage_fields` in `apps/api/core/projects/services/report_export_service.py` to use the shared nested helper from T007.
- [X] T028 [US5] Apply the same redaction on dashboard/report views in `apps/api/core/projects/report_views.py` and HR capacity/estimate responses in `apps/api/core/hr/capacity_views.py` / related serializers.
- [X] T029 [P] [US5] Ensure `edit_wage` remains required for mutations; `view_wage` alone cannot change amounts.

**Checkpoint**: Nested sensitive redaction works on reports and HR surfaces.

---

## Phase 8: User Story 6 - Person directory and lookup (Priority: P1)

**Goal**: Four separate person-data accesses from Clarification Q1; server omits unauthorized fields.

**Independent Test**: Active member roster without person-contact omits mobile/email; org directory denied without account-admin; `manage_members` lookup returns id+name only; `view_sensitive_contacts` alone does not open person contacts.

### Tests for User Story 6

- [X] T030 [US6] Write failing tests in `apps/api/core/projects/tests/test_person_directory_acl.py` for roster field omission, `GET /api/v1/users/lookup/` requiring `manage_members`, lookup without `view_person_contacts` omitting mobile/email, account-admin-only full directory, and independence from `view_sensitive_contacts`.

### Implementation for User Story 6

- [X] T031 [US6] Change `UserLookupView` in `apps/api/core/projects/member_views.py` to require active `manage_members` (project context via query param or existing team flow), return `user_id` and `full_name` by default, include mobile/email only with `view_person_contacts`, optionally one non-sensitive org disambiguator for duplicate names, and keep the 20-row cap.
- [X] T032 [US6] Redact mobile/email in `apps/api/core/projects/member_serializers.py` unless `view_person_contacts` is effective for that project.
- [X] T033 [US6] Confirm organization user directory endpoints in `apps/api/core/authentication/views.py` remain behind account-admin (`IsHrOrAdmin` / explicit account gate from P3); refuse bare staff, project manager, or hr-without-gate.
- [X] T034 [P] [US6] Update `apps/web/src/components/projects/add-member-drawer.tsx` and `apps/web/src/app/lib/api/members.ts` to consume minimal lookup fields and not assume email/mobile always exist.

**Checkpoint**: Person directory policy matches Q1 on API and team UI.

---

## Phase 9: User Story 7 - Files, attachments, and download links (Priority: P1)

**Goal**: File issue/download follow source and project permission; revoke invalidates later use; real file evidence preferred.

**Independent Test**: Non-member and member without source permission cannot download; after revoke, prior link fails or expires; document honest gaps if MinIO unavailable.

### Tests for User Story 7

- [X] T035 [US7] Extend failing/positive cases in `apps/api/core/documents/tests/test_attachment_signing_security.py` and `apps/api/core/storage/` tests for source permission, project membership, and post-revoke behavior. If real storage is unavailable, assert the permission branch and record incomplete file-service evidence in the matrix—do not claim full coverage from mocks alone.

### Implementation for User Story 7

- [X] T036 [US7] Tighten `apps/api/core/storage/permissions.py` and `apps/api/core/storage/views.py` so download/sign require source resource permission plus current project authority, not generic membership alone.
- [X] T037 [US7] Re-check documents attachment signing paths in `apps/api/core/documents/` against the same rules after membership revoke.

**Checkpoint**: File ACL matches contract; evidence honesty recorded.

---

## Phase 10: User Story 8 - Submitter vs approver and workflows (Priority: P1)

**Goal**: Ordinary submitter cannot final-approve own material transaction; second approver can; superuser break-glass is explicit, audited, and still requires membership and approve permission; null creator blocked on normal path.

**Independent Test**: Creator self-approve fails; second approver succeeds; superuser without reason fails; with reason+audit succeeds only for self-approve bypass; admin/staff/HR without superuser cannot break-glass; null creator normal path fails.

### Tests for User Story 8

- [X] T038 [US8] Rewrite failing unit tests in `apps/api/core/permissions/tests/test_sod.py` for null creator refusal, no automatic superuser bypass, and break-glass requiring reason.
- [X] T039 [P] [US8] Write failing integration tests for `approve_commitment` in `apps/api/core/cost_control/tests/test_commitment_sod.py` (new) covering creator deny, second approver allow, and break-glass audit requirement.
- [X] T040 [P] [US8] Write failing workflow SoD/stage tests touching `apps/api/core/workflow/services/instance_service.py` for out-of-stage and out-of-project actors.

### Implementation for User Story 8

- [X] T041 [US8] Implement the SoD helper behavior from T006 fully in `apps/api/core/permissions/sod.py` and update all existing callers (`actual_cost_service`, `budget_change_service`, `budget_version_service`, `ipc_service`, `exception_service`, `instance_service`, change requests) to pass actor and optional break-glass reason.
- [X] T042 [US8] Update `approve_commitment` in `apps/api/core/cost_control/cbs_services.py` and `apps/api/core/cost_control/cbs_views.py` to accept actor, enforce SoD, require break-glass reason when used, and refuse when audit write fails.
- [X] T043 [US8] On successful break-glass, call `record_access_change` with actor, project, record id, reason, exception flag, before/after. If audit cannot be written, do not approve.
- [X] T044 [US8] Ensure new SoD-covered creates (including import/background entry points touched in package work) set a real `created_by`/system actor; never assign creator to the approver to bypass. Add attribution-repair path that audits creator correction for legacy null rows without auto-approving.
- [X] T045 [P] [US8] Add Persian/English strings for `sod_self_approve`, break-glass reason required, and unknown-creator refusal in locale files under `apps/api/core/locale/` and `apps/web/src/app/locales/`.

**Checkpoint**: SoD and break-glass match Q2/Q3 on commitment and shared helper callers.

---

## Phase 11: User Story 9 - Three sequential packages and 29-area matrix (Priority: P2)

**Goal**: Deliver package 1, then 2, then 3 with positive/negative evidence on two projects; no unmarked green rows.

**Independent Test**: Each package tracker shows every area green or N/A with reason; package N+1 consumer work starts only after package N gate task is checked.

### Package 1 — account, project, site (M01–M10, M14)

- [X] T046 [US9] Apply US1–US8 fixes to remaining package-1 consumers listed in `specs/048-a6-p4-module-access/matrix/package-1.md` (auth, members/roles, projects, templates, master_data, business_meta, wbs, schedule, field_reports, concrete_operations, sub_reports). Prefer extending helpers over parallel ACL.
- [X] T047 [US9] Run positive and negative pytest evidence for package-1 rows; attach commands and results into `package-1.md`. Include two-project isolation samples.
- [X] T048 [US9] **GATE**: Mark package-1 `closed` only when every row is pass or N/A with reason. Do not start package-2 consumer rollout before this gate.

### Package 2 — finance, contracts, resources (M13, M15–M21, M26)

- [X] T049 [US9] Inventory package-2 URLs/actions into `specs/048-a6-p4-module-access/matrix/package-2.md`.
- [X] T050 [US9] Apply access, redaction, and SoD fixes across `apps/api/core/hr/`, `cost_control/`, `cash_flow/`, `contracts/`, `subcontractors/`, `procurement/`, `inventory/`, `resources/`, `economic/` consumers still open after earlier stories.
- [X] T051 [US9] Run package-2 positive/negative evidence including wage and SoD rows; update `package-2.md`.
- [X] T052 [US9] **GATE**: Mark package-2 `closed` only when complete. Do not start package-3 rollout before this gate.

### Package 3 — documents, collaboration, management outputs (M11–M12, M22–M25, M27–M29)

- [X] T053 [US9] Inventory package-3 URLs/actions into `specs/048-a6-p4-module-access/matrix/package-3.md`.
- [X] T054 [US9] Apply remaining fixes across `risk/`, `decision_support/`, `documents/`, `workflow/`, stakeholders, reports/dashboard, `notifications/`, `storage/`, and audit event hooks for sensitive actions (history UI stays P5).
- [X] T055 [US9] Run package-3 evidence including nested export, file ACL honesty, and workflow stage checks; update `package-3.md`.
- [X] T056 [US9] **GATE**: Mark package-3 `closed` when complete.

**Checkpoint**: All three packages closed with matrix evidence.

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Traceability, quickstart validation, and handoff to P5/P6

- [X] T057 [P] Fill `specs/048-a6-p4-module-access/traceability.md` for A6-R30, R33–R35, R38–R46 and retested R10/R31/R32/R36/R37 with نتیجه and evidence paths.
- [X] T058 [P] Execute `specs/048-a6-p4-module-access/quickstart.md` checks that are runnable in this environment; record skipped file-service items explicitly.
- [X] T059 Run a Persian UI spot check for lookup minimal fields, hidden forbidden control, and observation read-without-write; note project id and outcome in `traceability.md`.
- [X] T060 Confirm P5 handoff: break-glass and sensitive events are in `RoleAccessChange`; no claim of finished history UI. Confirm P6 handoff: customer acceptance scenarios remain unexecuted.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **US1–US8 (Phases 3–10)**: Depend on Foundational; prefer priority order; US2 inventory (T015) should precede deep package-1 alternate fixes
- **US9 (Phase 11)**: Depends on US1–US8 helper/story work for its package consumers; **package gates T048 → T052 → T056 are strictly sequential**
- **Polish (Phase 12)**: Depends on US9 package-3 gate

### User Story Dependencies

- **US1**: After Foundational — MVP isolation
- **US2**: After Foundational; benefits from US1 helpers
- **US3**: After Foundational; can parallel US4 once server re-check exists
- **US4**: After Foundational; UI only after server pairs exist for the representative codename
- **US5**: Needs T007 redaction helper
- **US6**: Needs T004 `view_person_contacts`
- **US7**: Can follow US1 project-scope rules
- **US8**: Needs T005/T006 SoD + audit contract; blocks honest package-2 finance close
- **US9**: Rolls helpers across 29 areas with sequential package gates

### Parallel Opportunities

- T001–T003 setup in parallel
- T004, T005, T007, T008 foundational in parallel after T001
- Within a story, tests marked [P] can start together
- US5 redaction tests and US6 directory tests can proceed in parallel after foundation
- US8 commitment and workflow test files marked [P] can proceed in parallel
- Do **not** parallelize package-2/3 consumer rollout across package gates

---

## Parallel Example: User Story 8

```bash
# After foundation SoD contract exists:
Task: "Rewrite failing unit tests in apps/api/core/permissions/tests/test_sod.py"
Task: "Write failing integration tests for approve_commitment in apps/api/core/cost_control/tests/test_commitment_sod.py"
Task: "Write failing workflow SoD/stage tests touching apps/api/core/workflow/services/instance_service.py"
```

## Parallel Example: Package trackers (Setup)

```bash
Task: "Create matrix/README.md template"
Task: "Create package-1.md, package-2.md, package-3.md trackers"
Task: "Add traceability.md stub"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup + Foundational
2. Complete US1 project isolation tests and fixes
3. **STOP and VALIDATE** with `test_module_access_project_scope.py`
4. Then continue US2–US8 before claiming module-wide coverage

### Incremental Delivery

1. Foundation helpers
2. US1–US8 capabilities with failing-then-passing tests
3. US9 package-1 gate → package-2 gate → package-3 gate
4. Traceability and quickstart honesty

### Package Rule (mandatory)

Never start the next package’s consumer rollout task before the previous package gate task is checked. Existing green wage/contact/signing tests must remain green unless intentionally superseded with stronger replacements.

---

## Notes

- [P] = different files, no dependency on incomplete work
- Observation policy is not expanded
- `view_person_contacts` ≠ `view_sensitive_contacts`
- Break-glass is superuser-only, explicit reason, audited, membership + approve permission still required
- Null creator does not skip SoD; do not reassign `created_by` to the approver
- Customer acceptance and release are out of scope (P6)
- Full history UI is out of scope (P5)

## Phase 13: Convergence

- [X] T061 CRITICAL: Replace legacy global and inactive-member guards (`CanViewBusinessAssignments`, `CanViewProjectMembers._legacy_write_allowed`, `IsHrOrAdminOrReadOnly`) on project-scoped inventory and department-activity views in `apps/api/core/inventory/views.py`, `apps/api/core/inventory/department_activity_data_views.py`, and `apps/api/core/business_meta/permissions.py` with `IsProjectMember` + `HasProjectPermission` active-membership checks per Constitution I, FR-001, FR-005, FR-012, US2/AC1, T016 (contradicts)
- [X] T062 CRITICAL: Enforce `HasProjectPermission` write codenames on `DynamicRowsView`, `DynamicRowsImportView`, and `DynamicRowDetailView` in `apps/api/core/business_meta/data_views.py` so `viewer` members remain read-only, and require active project membership plus project write permission instead of global `IsBusinessSetup` on project-scoped `TableDefinitionViewSet` and `FieldDefinitionViewSet` mutations in `apps/api/core/business_meta/views.py` per Constitution I, FR-001, FR-012, US1/AC2, T046 (contradicts)
- [X] T063 CRITICAL: Redact `email` and `mobile` in `PersonDossierSerializer` and `PersonDossierView` in `apps/api/core/hr/serializers.py` and `apps/api/core/hr/capacity_views.py` unless the caller holds effective active-member `view_person_contacts` on that project (never via observation or `view_sensitive_contacts`) per Constitution I, FR-008, SC-006, US6/AC1, US6/AC4 (contradicts)
- [X] T064 CRITICAL: Remove bare `hr` group and `is_staff` bypasses from `IsOrganizationalAccountAdmin` in `apps/api/core/authentication/permissions.py`, `UserListView` and `UserAssignmentsListView` in `apps/api/core/authentication/views.py`, org-wide `UserLookupView` in `apps/api/core/projects/member_views.py`, and `RoleViewSet` in `apps/api/core/projects/role_views.py` so full organization directory, cross-user assignment reads, and global role mutations require explicit account/role administration authority per Constitution I, FR-008, SC-006, US6/AC2, T033 (contradicts)
- [X] T065 CRITICAL: Require an edit permission instead of `view_dashboard` on `SimulateView.post`, avoid writing `EconomicSnapshot` rows during observer `GET` requests on `EconomicSnapshotView`, bind `SimulateStatusView` task polling to `project_pk` in `apps/api/core/economic/views.py`, and replace bare `is_staff` (`IsAdminUser` / `_is_global_admin`) write gates in `apps/api/core/economic/views.py`, `apps/api/core/sub_reports/quarantine_views.py`, `apps/api/core/projects/lifecycle_service.py`, and `apps/api/core/projects/status_undo_service.py` with explicit org/project authorization per Constitution I, FR-001, FR-012, US1/AC2, US1/AC3, T009, T050 (contradicts)
- [X] T066 CRITICAL: Enforce source-resource permission (`view_documents` / `view_reports`) and `AccessLevel.RESTRICTED` checks in `CanAccessStoredFile` and `StoredFileDownloadView` in `apps/api/core/storage/permissions.py` and `apps/api/core/storage/views.py`, and block presigned download URL issuance for non-member organizational observers and unauthorized members in `apps/api/core/documents/views.py` and `apps/api/core/documents/serializers.py` per Constitution I, FR-009, SC-007, US7/AC1, US7/AC2, T036, T037 (contradicts)
- [X] T067 CRITICAL: Catch `403` permission-revocation errors per project in `syncPendingUnitOperations` in `apps/web/src/app/lib/syncService.ts`, filter `getFailedQueue` and `getQueueStats` by `actor_id` in `apps/web/src/app/lib/offlineDB.ts`, replace hardcoded Persian sync/toast messages in `syncService.ts` and `apps/web/src/app/hooks/useAutoSync.ts` with i18n lookups, and add missing bilingual error keys (`project_scope_mismatch`, `sod_missing_creator`, `sod_actor_required`, break-glass reason required) under `errors` in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json` per Constitution III, Constitution IV, FR-004, FR-015, US3/AC1, T013, T020, T045 (partial)
- [X] T068 CRITICAL: Replace single-row summary and source-inspection claims (including the false `0 project-nested inventory urls` note) in `specs/048-a6-p4-module-access/matrix/package-1.md`, `package-2.md`, and `package-3.md` with live URL/action inventories from `apps/api/core/config/urls.py` and module `urls.py` files, execute two-project positive/negative pytest suites sequentially across package 1 -> 2 -> 3 gates, run the live Persian browser UI spot check, and update `specs/048-a6-p4-module-access/traceability.md` honestly per Constitution VI, FR-005, FR-013, SC-002, SC-010, SC-011, US9/AC1-3, T015, T047-T059 (contradicts)
- [X] T069 Wire `assert_same_project` into `ProjectScopedViewSet` `perform_create` and `perform_update` in `apps/api/core/common/viewsets.py` (failing closed when `project_id` is `None` in `apps/api/core/permissions/project.py`), enforce cross-project foreign-ID rejection in `CommunicationPlanSerializer` (`apps/api/core/projects/stakeholder_views.py`), `bulk_upsert_budgets` (`apps/api/core/cost_control/services/budget_service.py`), `bulk_upsert_contract_items` (`apps/api/core/contracts/services/contract_service.py`), `CostPoolAllocateView` (`apps/api/core/cost_control/views.py`), and `WorkflowInstanceViewSet.create` (`apps/api/core/workflow/views.py`), and add two-project API bind tests in `apps/api/core/projects/tests/test_module_access_project_scope.py` per FR-002, SC-001, US1/AC1, T010, T012, T046, T050, T054 (partial)
- [X] T070 Require dedicated `approve_*` permissions instead of `edit_*` on `CommitmentViewSet.approve` (`apps/api/core/cost_control/cbs_views.py`), `ActualCostViewSet.approve`/`void` (`apps/api/core/cost_control/views.py`), and `ChangeOrderApproveView` (`apps/api/core/contracts/views.py`), enforce SoD in `approve_change_order` (`apps/api/core/contracts/services/contract_service.py`), add status validation and `@transaction.atomic` break-glass `RoleAccessChange` auditing across `approve_commitment` (`apps/api/core/cost_control/cbs_services.py`) and all seven `T041` SoD service callers and API views, and add HTTP-level tests in `apps/api/core/cost_control/tests/test_commitment_sod.py` per FR-010, FR-011, FR-012, SC-008, SC-009, US8/AC1, US8/AC3, T039, T041-T043 (partial)
- [X] T071 Verify active `ProjectMember` status in `user_can_act_on_stage` in `apps/api/core/workflow/services/instance_service.py`, include `IsProjectMember` on all `WorkflowReadMixin` actions and remove the out-of-stage `edit_project` bypass on `WorkflowInstanceActionView` (`approve`/`reject`) in `apps/api/core/workflow/views.py`, and add real `instance_service`/API tests for out-of-stage, deactivated-approver, and out-of-project actors in `apps/api/core/workflow/tests/test_sod_final_approve.py` per FR-010, SC-008, US8/AC2, T040 (partial)
- [X] T072 Reject `creator == actor` self-assignment in `repair_missing_creator` and tighten `unknown_creator` reason matching in `apps/api/core/permissions/sod.py`, wire audited legacy creator-attribution repair to an authorized service/endpoint without auto-approving, verify `created_by` attribution on import and background SoD-covered creates, and replace mock-only tests in `apps/api/core/permissions/tests/test_creator_repair.py` with real domain-model tests per FR-011, SC-009, US8/AC4, T044 (partial)
- [X] T073 Re-apply caller-specific `redact_sensitive_payload` (including stakeholder contacts) on `ProjectReportExportDownloadView` and `ProjectReportRunView` in `apps/api/core/projects/report_views.py` as well as `ProjectDashboardPackView` (`apps/api/core/projects/dashboard_views.py`) and `ProjectKpiDrillView` (`apps/api/core/projects/kpi_views.py`, gating `finance.*`/`cash.*` drills on `view_costs`/`view_cashflow`), require `edit_wage` on `ApprovedLaborRateViewSet.destroy` in `apps/api/core/hr/capacity_views.py`, restrict `_user_may_view_sensitive_contacts` strictly to `view_sensitive_contacts` in `apps/api/core/projects/stakeholder_views.py`, and create `apps/api/core/projects/tests/test_nested_export_redaction.py` per FR-006, FR-007, SC-005, US5/AC1-3, T025, T028, T029 (partial)
- [X] T074 Remove automatic `view_person_contacts` from `DEFAULT_ROLE_PERMISSIONS['project_manager']` in `apps/api/core/permissions/constants.py`, redact `invited_email`/`invited_mobile` and contact `full_name` fallbacks while exposing member position titles in `ProjectMemberListSerializer` in `apps/api/core/projects/member_serializers.py`, disable `email`/`mobile` query matching without `view_person_contacts` in `UserLookupView` (`apps/api/core/projects/member_views.py`), and fix lookup label formatting and `createPerson` button gating in `apps/web/src/components/projects/add-member-drawer.tsx` with updated tests in `apps/api/core/projects/tests/test_person_directory_acl.py` per FR-008, SC-006, US6/AC1, US6/AC3, T004, T030-T034 (partial)
- [X] T075 Return empty effective permissions for non-active `ProjectMember` rows in `get_effective_permissions` in `apps/api/core/permissions/services.py`, prevent stale inactive-member write controls and non-member observer `404` permission fetches in `apps/web/src/app/contexts/project-context.tsx`, replace remaining global-group project UI gates (including `apps/web/src/app/routes/business-table.tsx`) with `usePermission`, and add the frontend permission-guard test/checklist required by `T022` per FR-003, SC-004, US4/AC1-3, T022-T024 (partial)
- [X] T076 Connect SoD refusals, emergency break-glass approvals across all callers, sensitive file link issuance and refusals, sensitive access denials, and post-revocation offline sync rejections to `record_access_change` (`RoleAccessChange`) in `apps/api/core/permissions/role_services.py` and consumer paths with unit/API tests per FR-014, T054, T060 (missing)
- [X] T077 Require explicit organizational catalog write authority for unsafe methods and `import_items` on `ItemViewSet` in `apps/api/core/inventory/views.py` while keeping read access shared across the organization, and add alternate-path import/export parity tests in `apps/api/core/permissions/tests/test_alternate_path_parity.py` per FR-005, FR-012, SC-002, US2/AC3, T014, T016 (partial)
- [X] T078 Extend `apps/api/core/documents/tests/test_attachment_signing_security.py` and `apps/api/core/storage/tests/test_stored_file_access.py` with active-member-without-source-permission, `AccessLevel.RESTRICTED`, cross-project, and post-revocation download/presign refusal tests, documenting live MinIO vs policy-branch coverage honestly per FR-009, SC-007, US7/AC1-3, T035 (partial)
