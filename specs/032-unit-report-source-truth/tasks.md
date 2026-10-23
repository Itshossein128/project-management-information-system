---

description: "Task list for Specialty Unit Reporting Source of Truth"
---

# Tasks: Specialty Unit Reporting Source of Truth

**Input**: Design documents from `specs/032-unit-report-source-truth/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ (all present), quickstart.md

**Tests**: **REQUIRED — TDD requested.** Every user story has a test-first section: write the behavioral tests, run them to confirm they FAIL for the right reason (missing canonical fields/constraints/behavior, not import/setup errors), then implement the smallest change that makes them pass. RED evidence commands are documented in `quickstart.md` §2–§6.

**Organization**: Tasks are grouped by user story (US1–US6) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- Backend: `apps/api/core/` (Django apps `sub_reports`, `project_templates`, `inventory`, `field_reports`, `common`)
- Frontend: `apps/web/src/` (routes under `app/`, shared hooks under `app/hooks/`, API clients under `app/lib/api/`)
- E2E: `apps/web/e2e/`
- Backend tests run from `apps/api/core` with `../.venv/bin/python -m pytest <path>` against Postgres + Redis (see `AGENTS.md`)

## Domain → Story Map (traceability)

| Domain element | Story | Source |
|---|---|---|
| `SpecialtyUnit` vocabulary (`common/reporting_units.py`) | Foundational | FR-001, data-model §1, research D1 |
| Evolved `DisciplineSubReport` (unit/lineage/version/current/rejection fields) | Foundational expand; US1 behavior | data-model §4, research D2 |
| `UnitReportStatusEvent` | US1 | data-model §5, research D4 |
| `DepartmentActivityRecord.unit_report` ownership | US1 | data-model §6, research D3 |
| Permissions + SoD | US2 | FR-014/015/016, research D5 |
| `ProjectTemplateRequiredUnit`, `ProjectReportingConfiguration(Unit)` | US3 | FR-003, data-model §2–3, research D6 |
| `DailyReport.reporting_configuration`, `aggregation_fingerprint` | US3 | data-model §7 |
| `DailyReportDerivedSource` | US3 | FR-021/022, data-model §8, research D7 |
| Correction versioning, deterministic rebuild | US4 | FR-023/024/025, research D8 |
| `/sub-reports` retirement | US5 | FR-029–032, research D10 |
| `UnitReportMigrationTrace`, `UnitReportMigrationQuarantine`, backfill/constraints/rollback | US6 | FR-033–038, data-model §9–10, research D9 |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the neutral canonical vocabulary and client-side registry that every later phase depends on.

- [X] T001 Create neutral six-value `SpecialtyUnit` vocabulary module in `apps/api/core/common/reporting_units.py` with exactly `buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, `security` (FR-001; values language-independent and never user-editable)
- [X] T002 [P] Create canonical unit registry `BUSINESS_DEPARTMENTS` aligned to the API vocabulary in `apps/web/src/config/business-departments.config.ts` with fa/en labels including «ابنیه», «برق», «مکانیک», «ماشین‌آلات», «انبار», «حراست و HSE» (FR-002)
- [X] T003 [P] Add canonical unit, status, workflow-action, completeness-state, and error-code translation keys to both `apps/web/src/locales/fa.json` and `apps/web/src/locales/en.json` (FR-002; no raw backend English labels rendered)

---

## Phase 2: Foundational (Blocking Prerequisites — expand schema only)

**Purpose**: Expand migrations that add nullable canonical/version/configuration/provenance/trace structures. **No destructive constraint, no backfill, no behavior change yet** (research D9 step 1; plan ordering step 2).

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Evolve `DisciplineSubReport` in `apps/api/core/sub_reports/models.py`: add nullable canonical `unit`, `legacy_discipline`, `lineage_id`, `version_number`, `is_current`, `supersedes`, `rejected_by`, `rejected_at`, `rejection_reason`, `updated_by`, `updated_at`, `linked_daily_report`, `is_deleted`, `deleted_at` (nullable only during migration/quarantine — data-model §4)
- [X] T005 [P] Add append-only `UnitReportStatusEvent` model in `apps/api/core/sub_reports/models.py` with `event_type` in `created/submitted/approved/rejected/corrected/deleted/superseded` and reason required for rejection semantics (data-model §5)
- [X] T006 [P] Add `UnitReportMigrationTrace` (unique `(source_system, source_model, source_id)`, disposition `migrated/historical/duplicate_alias/quarantined`, `source_checksum`, `snapshot`) and `UnitReportMigrationQuarantine` models in `apps/api/core/sub_reports/models.py` (data-model §9–10)
- [X] T007 [P] Add nullable `unit_report` FK to `DepartmentActivityRecord` in `apps/api/core/inventory/models.py` (data-model §6)
- [X] T008 [P] Add `ProjectTemplateRequiredUnit` (unique `(template, unit)`), immutable `ProjectReportingConfiguration` (unique `(project, effective_from)`, `supersedes`, audit snapshot fields), and `ProjectReportingConfigurationUnit` snapshot rows in `apps/api/core/project_templates/models.py` (data-model §2–3)
- [X] T009 [P] Add nullable `reporting_configuration` FK and `aggregation_fingerprint` to `DailyReport` in `apps/api/core/field_reports/models.py` (data-model §7)
- [X] T010 [P] Add `DailyReportDerivedSource` normalized provenance model in `apps/api/core/field_reports/models.py` with unique `(derived_kind, derived_row_id, source_report_id_snapshot, source_row_kind, source_row_id)` and `source_row_id` as string supporting UUID and integer IDs (data-model §8)
- [X] T011 Generate expand migrations in `apps/api/core/sub_reports/migrations/`, `apps/api/core/inventory/migrations/`, `apps/api/core/project_templates/migrations/`, and `apps/api/core/field_reports/migrations/`; verify `../.venv/bin/python manage.py makemigrations --check --dry-run` reports no drift and `migrate` applies cleanly

**Checkpoint**: Expand schema exists, app still behaves identically; user story implementation can now begin.

---

## Phase 3: User Story 1 — Author a unit report on its unit page (Priority: P1) 🎯 MVP

**Goal**: An authorized unit user opens their Specialty Units page, selects a date, opens/creates the single current report for project/date/unit, edits a draft, submits it, and sees state/audit without leaving the page.

**Independent Test**: On the Buildings page, create a report for date D, edit and submit it; verify the page shows submitted state, last-change time, preparer, submitter, and that a second active report for the same project/date/unit cannot be created.

### Tests for User Story 1 (TDD — write FIRST, confirm they FAIL) ⚠️

- [X] T012 [P] [US1] Model constraint tests in `apps/api/core/sub_reports/tests/test_unit_report_models.py`: unique current report on `(project, report_date, unit)` where `is_current=true`; unique `(lineage_id, version_number)`; `supersedes` shares project/date/unit/lineage with lower version number (data-model §4)
- [X] T013 [P] [US1] Workflow behavior tests in `apps/api/core/sub_reports/tests/test_unit_report_workflow.py`: two concurrent opens resolve to one current draft; draft/rejected editable; submitted/approved content immutable; rejection records rejector/time; duplicate create returns existing current report (spec US1 scenarios 1–5; quickstart §4 cases 1–2)

### Implementation for User Story 1

- [X] T014 [US1] Implement locked open/create/edit/submit service with deterministic current-version resolution in `apps/api/core/sub_reports/services.py` (reload and lock current version before validating state — data-model State Transitions)
- [X] T015 [P] [US1] Implement version/event creation and status-event recording in `apps/api/core/sub_reports/services.py` (created/submitted events; migration baseline rule documented in data-model §5)
- [X] T016 [P] [US1] Unit-report serializers in `apps/api/core/sub_reports/serializers.py` matching the detail response shape: `id`, `lineage_id`, `version_number`, `is_current`, `unit`, `report_date`, `status`, `audit`, `capabilities`, `content` (contracts/unit-report-api.md detail response)
- [X] T017 [US1] Unit-report views and URLs in `apps/api/core/sub_reports/views.py` and `apps/api/core/sub_reports/urls.py` under `/api/v1/projects/{project_id}/units/{unit}/daily-reports/`: `GET current/?date=`, `POST open/` (idempotent, 201 created / 200 existing), `GET/PATCH/DELETE {report_id}/`, `GET {report_id}/history/`, `POST {report_id}/submit/` (contracts/unit-report-api.md; URL unit is never an editable field)
- [X] T018 [US1] Add the same constraint test in `apps/api/core/sub_reports/tests/test_unit_report_models.py` must stay green: enforce canonical `unit` values from `apps/api/core/common/reporting_units.py` in model/serializer validation with error code `invalid_specialty_unit`
- [X] T019 [P] [US1] Typed canonical API client (not hr-forms legacy helpers) in `apps/web/src/app/lib/api/unit-reports.ts`
- [X] T020 [US1] Build shared `UnitDailyReportPanel` in `apps/web/src/components/department/unit-daily-report-panel.tsx`: Jalali-aware date picker persisted in URL query state, localized status badge, semantic audit `<dl>` (preparer, last change, submitter), server-capability-driven controls, rejection reason with `dir="auto"`
- [X] T021 [US1] Host the panel inside the existing unit page in `apps/web/src/components/department/department-page.tsx` with route-derived unit identity (never selectable in the form; contracts/unit-report-ui.md)
- [X] T022 [US1] Bind report-owned activity queries/mutations to the current report in `apps/web/src/app/hooks/queries.ts`; row mutation disabled unless current report is draft/rejected
- [X] T023 [US1] Attach `DepartmentActivityRecord` create/update/delete to the current draft/rejected parent in `apps/api/core/inventory/serializers.py` and `apps/api/core/inventory/views.py`: parent project/date/unit server-derived, mismatched body values rejected with `source_relation_project_mismatch`, unchanged row IDs survive edits (ID-aware updates; blanket soft-delete/recreate prohibited)

**Checkpoint**: US1 fully functional and testable independently (backend + unit page authoring).

---

## Phase 4: User Story 2 — Review unit reports with project-safe permissions (Priority: P1)

**Goal**: View/create/edit/submit/approve/reject each enforce the corresponding project permission, active membership, project/unit scope, and the project's segregation-of-duties policy; unauthorized and cross-project attempts are denied without disclosure.

**Independent Test**: Exercise every action with each required permission, a SoD-prohibited actor, a user without permission, and a member of another project; only authorized in-project actions succeed.

### Tests for User Story 2 (TDD — write FIRST, confirm they FAIL) ⚠️

- [X] T024 [P] [US2] Permission matrix tests in `apps/api/core/sub_reports/tests/test_unit_report_permissions.py`: `view_reports` for reads, `edit_reports` for open/create/edit/delete/correct/submit, `approve_reports` for approve/reject; non-member, wrong-project ID, wrong-unit ID, and nested foreign-key injection disclose no report content (contracts/unit-report-api.md permission matrix; spec US2 scenarios 1–2)
- [X] T025 [P] [US2] SoD tests in `apps/api/core/sub_reports/tests/test_unit_report_permissions.py`: preparer or submitter cannot approve the same report, returns stable `sod_self_approve`, state remains submitted; existing superuser break-glass verified separately (FR-016; quickstart §4 case 8)
- [X] T026 [P] [US2] Reject-validation tests in `apps/api/core/sub_reports/tests/test_unit_report_workflow.py`: blank reason refused with stable code `rejection_reason_required`; supplied reason records reviewer, reason, and decision time (spec US2 scenarios 5–6)

### Implementation for User Story 2

- [X] T027 [US2] Enforce permission matrix + active membership + URL/object unit consistency at the trusted authorization boundary in `apps/api/core/sub_reports/services.py` and `apps/api/core/sub_reports/views.py`; cross-project/wrong-unit returns non-disclosing not-found (FR-014/FR-015)
- [X] T028 [US2] Enforce SoD in the locked approval service path (not the UI) in `apps/api/core/sub_reports/services.py`, preserving the existing superuser break-glass rule (FR-016)
- [X] T029 [US2] Rejection path with required non-empty `rejection_reason`, localized messages, and stable error codes `invalid_unit_report_transition`, `unit_report_not_editable`, `unit_report_not_current`, `unit_report_conflict` in `apps/api/core/sub_reports/serializers.py` (contracts/unit-report-api.md stable errors)
- [X] T030 [US2] Compute `capabilities` (`can_edit`, `can_submit`, `can_approve`, `can_reject`, `can_correct`, `can_delete`, `can_view_history`) as convenience projections only in `apps/api/core/sub_reports/serializers.py`
- [X] T031 [US2] Frontend: localized inline server-error display with `role="alert"`, controls derived from server capabilities, and no reliance on hidden controls as authorization proof in `apps/web/src/components/department/unit-daily-report-panel.tsx` (contracts/unit-report-ui.md workflow behavior)

**Checkpoint**: US1 + US2 both work independently; authorization is server-enforced.

---

## Phase 5: User Story 3 — Build the project summary from eligible unit reports (Priority: P1)

**Goal**: The read-only project daily summary is derived only from current submitted/approved unit reports for the same project/date, with complete multi-source provenance and truthful completeness from the effective immutable template configuration.

**Independent Test**: Approve a Buildings report for D, reopen/rebuild D's summary, verify eligible rows appear read-only with report/unit/source-row provenance while an ineligible required unit remains missing.

### Tests for User Story 3 (TDD — write FIRST, confirm they FAIL) ⚠️

- [X] T032 [P] [US3] Template contract tests in `apps/api/core/project_templates/tests/test_required_report_units.py`: unique canonical units, order preserved for display only, at least one unit on reporting-capable templates, editing a reusable template never changes an activated configuration, no hard-coded fallback list (FR-003; contracts/report-template-api.md)
- [X] T033 [P] [US3] Aggregation eligibility tests in `apps/api/core/field_reports/tests/test_unit_report_aggregation_eligibility.py`: only current, non-deleted, non-quarantined, submitted/approved, matching project/date reports contribute; draft/rejected/deleted/superseded/cross-project/cross-date contribute nothing (FR-018/019; spec US3 scenarios 2–3)
- [X] T034 [P] [US3] Completeness tests in `apps/api/core/field_reports/tests/test_unit_report_completeness.py`: expected/contributing/missing sets from the bound configuration; `complete` only when every required unit has an eligible report; eligible non-required units appear in contributing but never missing; no configuration yields `configuration_incomplete` and never claims completeness; empty eligible report still counts as contributing (FR-026/027/028; spec US3 scenarios 4–5, edge cases)
- [X] T035 [P] [US3] Provenance tests in `apps/api/core/field_reports/tests/test_unit_report_provenance.py`: every derived row retains source report UUID, version number, canonical unit, source-row kind and ID; multi-source totals retain every contributing row in deterministic order — no last-source-wins (FR-021/022; spec US3 scenario 6)

### Implementation for User Story 3

- [X] T036 [US3] `ProjectTemplateRequiredUnit` read/write with validation (`invalid_required_units` for empty/duplicate/non-canonical lists) in `apps/api/core/project_templates/serializers.py` and `apps/api/core/project_templates/services.py`
- [X] T037 [US3] Immutable effective-dated configuration activation endpoints in `apps/api/core/project_templates/views.py` and `apps/api/core/project_templates/urls.py` under `/api/v1/projects/{project_id}/reporting-configurations/`: `GET ?date=`, `GET ` list newest first, `POST ` (append-only, later than latest), `POST preview/`; errors `reporting_configuration_date_conflict`, `daily_report_template_required` (contracts/report-template-api.md). Enforce target-project membership + `edit_project` on the existing globally authenticated template-apply endpoint
- [X] T038 [US3] Resolve latest configuration where `effective_from <= report_date`, bind its identifier to the summary, and use the bound configuration on rebuilds in `apps/api/core/field_reports/services/daily_report_aggregation.py` (data-model §3)
- [X] T039 [US3] Eligibility selection with lock order Project → current unit report(s) → current full-shift DailyReport, stable ordering by `(unit, version_number, id)` and source rows by domain order then stable ID, plus project/date/unit scope validation of every source relation in `apps/api/core/field_reports/services/daily_report_aggregation.py` (deterministic rebuild rules 1–3)
- [X] T040 [US3] Deterministic `derivation_key` assignment and `DailyReportDerivedSource` upsert (replace provenance set per derived row; remove obsolete derived keys only) in `apps/api/core/field_reports/services/daily_report_aggregation.py` (deterministic rebuild rules 4–6)
- [X] T041 [US3] Completeness computation (`configuration_incomplete`/`partial`/`complete`, expected/contributing/missing sets, `configuration_id`, `source_template`) serialized into DailyReport detail and by-date responses under `aggregation` in `apps/api/core/field_reports/serializers.py` (contracts/daily-summary-api.md)
- [X] T042 [US3] Trigger rebuild from submit/approve/reject/delete/relevant report-owned source changes in `apps/api/core/sub_reports/services.py`; `by-date` ensure path invokes the same serialized rebuild orchestration in `apps/api/core/field_reports/services/daily_report_aggregation.py`
- [X] T043 [P] [US3] Completeness UI: separate localized states with expected/contributing/missing chips from the shared registry, missing-unit links to the unit page preserving date, in `apps/web/src/components/daily_reports/summary/IncompletenessBanner.tsx` and `apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx`
- [X] T044 [US3] Provenance disclosure UI: accessible "View sources (N)" per derived row; source linked only when `can_view_source=true`, else non-clickable attribution; source navigation re-enters the unit-report API with full re-authorization in `apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx` and `apps/web/src/app/lib/api/daily-reports.ts`

**Checkpoint**: Summary derives solely from eligible unit reports with complete provenance and truthful completeness.

---

## Phase 6: User Story 4 — Correct and rebuild without duplicates or stale data (Priority: P1)

**Goal**: Corrections create a new current version preserving history; rebuilds deterministically replace obsolete contributions, are idempotent, and preserve summary-owned overrides.

**Independent Test**: With a contributing report, reject/supersede it, change one source row, resubmit, and rebuild repeatedly; exactly one current contribution remains, the obsolete row is absent, history identifies prior versions.

### Tests for User Story 4 (TDD — write FIRST, confirm they FAIL) ⚠️

- [X] T045 [P] [US4] Rebuild idempotency tests in `apps/api/core/field_reports/tests/test_unit_report_rebuild_idempotency.py`: three consecutive rebuilds with unchanged inputs yield identical logical content, row counts, derivation keys, ordered provenance, completeness, and summary-owned override values (excluding volatile timestamps); rejection/deletion/correction/resubmission replace stale contributions exactly once (FR-023/024; spec US4 scenarios 1–3; SC-004/SC-005)
- [X] T046 [P] [US4] Override-preservation tests in `apps/api/core/field_reports/tests/test_unit_report_rebuild_idempotency.py`: management opinion, explicit weather override, and site-status override survive rebuild unchanged (FR-025; spec US3 scenario 7)
- [X] T047 [P] [US4] Correction-version tests in `apps/api/core/sub_reports/tests/test_unit_report_workflow.py`: approved correction creates version n+1 current draft leaving approved version n read-only and traceable; rejected correction resubmits while preserving all state-transition events (spec US1 scenario 4, US4 scenario 4; quickstart §4 case 5)

### Implementation for User Story 4

- [X] T048 [US4] Explicit correction action in `apps/api/core/sub_reports/services.py`: clone report-owned content into new current draft version (monotonic `version_number`, shared `lineage_id`, `supersedes` link), append `corrected` status event; approved version never mutated (data-model State Transitions)
- [X] T049 [US4] Add `POST {report_id}/correct/` endpoint in `apps/api/core/sub_reports/views.py` and `apps/api/core/sub_reports/urls.py` with `edit_reports` + membership + scope checks (contracts/unit-report-api.md)
- [X] T050 [US4] Aggregation fingerprint of current eligible source versions/rows/configuration and skip-writes on unchanged fingerprint while returning current metadata; explicit `update_fields` on summary save — never blanket-save stale summary-owned values in `apps/api/core/field_reports/services/daily_report_aggregation.py` (deterministic rebuild rule 7–8; data-model §7)
- [X] T051 [US4] History endpoint `GET {report_id}/history/` returning ordered lineage versions with `superseded_by` and immutable status events in `apps/api/core/sub_reports/views.py` (contracts/unit-report-api.md history response)
- [X] T052 [US4] Accessible version-history table/timeline and correction/resubmit path in `apps/web/src/components/department/unit-daily-report-panel.tsx` (contracts/unit-report-ui.md)

**Checkpoint**: Corrections and rebuilds are duplicate-free, idempotent, and history-preserving.

---

## Phase 7: User Story 5 — Retire the parallel standalone workflow (Priority: P1)

**Goal**: Specialty authoring is reachable only from the six Specialty Units pages; `/projects/{projectId}/sub-reports` shows the standard not-found state and the project daily-report area has no "New Report" action.

**Independent Test**: Scan all navigation/CTAs/empty states in both languages and open the legacy route directly; no link or form exposes the old workflow.

### Tests for User Story 5 (TDD — write FIRST, confirm they FAIL) ⚠️

- [X] T053 [P] [US5] Browser tests in `apps/web/e2e/tests/unit-report-source-truth.spec.ts`: direct navigation to `/projects/{projectId}/sub-reports` renders the standard localized not-found state, issues no report-data request, and renders no form (FR-030; spec US5 scenario 2)
- [X] T054 [P] [US5] Navigation-scan tests in `apps/web/e2e/tests/unit-report-source-truth.spec.ts`: in fa and en, menus, CTAs, and empty states contain zero `/sub-reports` links; project daily-report area exposes no "New Report" action (FR-029/031; SC-007; spec US5 scenarios 1 and 3)

### Implementation for User Story 5

- [X] T055 [US5] Remove `PROJECT_SUB_REPORTS` from `apps/web/src/app/routeVars.ts` and unregister the legacy route in `apps/web/src/app/routes/business-setup.routes.ts` and the nav item in `apps/web/src/config/project-navigation.config.ts` (no redirect to Buildings or any arbitrary unit)
- [X] T056 [US5] Delete `apps/web/src/app/routes/project-sub-reports.tsx` and the legacy untyped API helper; ensure the not-found boundary issues no report-data request
- [X] T057 [US5] Remove legacy CTA from `apps/web/src/app/routes/daily-reports-list.tsx`; optional registry-driven six-unit chooser popover preserving the selected date
- [X] T058 [US5] Unregister legacy client endpoints under `/api/v1/projects/{project_id}/sub-reports/` in `apps/api/core/sub_reports/urls.py` and mark the internal compatibility path with the retirement milestone (no later than the third feature in this series) per FR-032/research D2
- [X] T059 [P] [US5] Remove obsolete `/sub-reports` and hard-coded discipline-tab translation entries from `apps/web/src/locales/fa.json` and `apps/web/src/locales/en.json`
- [X] T060 [US5] Rename the department "daily report" PDF control as an activity-log export in `apps/web/src/components/department/department-page.tsx` and route independent add/edit/delete/import controls through the current report context per `apps/web/src/components/department/unit-daily-report-panel.tsx` (contracts/unit-report-ui.md existing activity log transition)

**Checkpoint**: All six stories deliver; legacy workflow is unreachable from the product surface.

---

## Phase 8: User Story 6 — Migrate legacy reports without losing history (Priority: P2)

**Goal**: Every valid legacy report, child ID, state, actor/time, rejection text, and summary link is preserved, traced, and accounted for; collisions resolve deterministically before canonical constraints; rollback is rehearsed.

**Independent Test**: Migrate a representative legacy dataset (each legacy discipline, duplicate candidates for one unit/date, historical states, existing summary links); all source records traceable, exactly one current version per canonical key, rollback restores pre-migration relationships.

### Tests for User Story 6 (TDD — write FIRST, confirm they FAIL) ⚠️

- [X] T061 [P] [US6] Migration accounting tests in `apps/api/core/sub_reports/tests/test_unit_report_migrations.py` via `MigrationExecutor` (forward → pre-feature target → forward again, leaf restored in `finally`): `civil`/`finishing` → `buildings`; `plumbing`/`hvac` → `mechanical`; `electrical` → `electrical`; legacy `mechanical` → `mechanical`; no inference for machinery/warehouse/security; every source report/row ID present in trace exactly once (FR-004; quickstart §3)
- [X] T062 [P] [US6] Collision/quarantine tests in `apps/api/core/sub_reports/tests/test_unit_report_migrations.py`: multiple non-identical legacy reports for one project/date/unit all preserved as versions, current selected by latest business change time then stable legacy UUID as tie-breaker, displaced current markers traced; exact duplicates become trace aliases contributing once; unknown/malformed categories quarantined with stable reason codes and never silently mapped (FR-035/036/037)
- [X] T063 [P] [US6] Link/rollback tests in `apps/api/core/sub_reports/tests/test_unit_report_migrations.py`: existing `linked_daily_report` relationships resolve after migration; rollback from the trace reconstructs original category values, current-version relationships, and summary links (FR-038; data-model Migration and Rollback Invariants)

### Implementation for User Story 6

- [X] T064 [US6] Deterministic, resumable backfill management command in `apps/api/core/sub_reports/management/commands/` with mapping rules, `source_checksum` snapshotting, and unique `(source_system, source_model, source_id)` upsert (idempotent/resumable per data-model §9)
- [X] T065 [US6] Attach unit-page `DepartmentActivityRecord` groups to the applicable version, or create a traced draft lineage when no report exists; retain unsafe attachments in quarantine/trace; row identifiers unchanged, implemented in `apps/api/core/sub_reports/management/commands/` backfill plus `apps/api/core/inventory/models.py` (data-model §6)
- [X] T066 [US6] Collision resolution implementing latest-business-change-time then stable-UUID selection with auditable trace of all displaced current markers; create baseline `UnitReportStatusEvent` describing only evidence present at migration time — no fabricated pre-feature transitions, implemented in `apps/api/core/sub_reports/services/migration.py` (new module) called by the backfill command (FR-035; data-model §5)
- [X] T067 [US6] `UnitReportMigrationQuarantine` resolution surface for authorized migration operators (readable, never current, never contributes) in `apps/api/core/sub_reports/views.py` and `apps/api/core/sub_reports/serializers.py`
- [X] T068 [US6] `verify_unit_report_migration` management command emitting JSON classification of every source report/activity row as migrated/historical/duplicate_alias/quarantined with 100% accounting in `apps/api/core/sub_reports/management/commands/`
- [X] T069 [US6] Constraint migration applied only after validation: unique current report on `(project, report_date, unit)` where `is_current=true`, product-visible rows require valid canonical unit, submitted/approved content immutability, in `apps/api/core/sub_reports/migrations/`
- [X] T070 [US6] Sanitized-dataset rehearsal + backup/restore rollback drill executed and evidenced per `specs/032-unit-report-source-truth/quickstart.md` §10; **no destructive cleanup in this feature** — legacy `discipline` field and tables remain through the rollback window (plan ordering step 8)

**Checkpoint**: Legacy data fully accounted, traceable, and rehearsably reversible.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Concurrency proof, bilingual browser acceptance, regression anchoring, and final evidence capture.

- [X] T071 [P] PostgreSQL concurrency tests in `apps/api/core/sub_reports/tests/test_unit_report_concurrency.py` using independent connections and barriers: simultaneous open/create; simultaneous approved corrections; edit/delete racing submit; approve racing reject; two unit submissions rebuilding one day; rebuild racing an override update — assert database state, not just response codes (quickstart §6)
- [X] T072 [P] Full bilingual real-stack Playwright acceptance in `apps/web/e2e/tests/unit-report-source-truth.spec.ts` and `apps/web/e2e/tests/daily-report.spec.ts` covering quickstart §9 scenarios 1–10 in fa and en, including keyboard operability of date picker, dialogs, history, and provenance disclosure with correct RTL/LTR (SC-010 automation portion only)
- [X] T073 Update legacy-affected existing tests to canonical behavior in `apps/api/core/inventory/tests.py`, `apps/api/core/inventory/test_department_activity_contractor_import.py`, `apps/api/core/inventory/test_department_activity_contractor_ref.py`, and existing `apps/api/core/field_reports/tests/test_daily_report_*.py` — adjust obsolete assertions, never delete tests merely for exposing the old architecture (quickstart §7)
- [X] T074 [P] Run `pnpm typecheck` and record the pre-existing `DailyReportForm.tsx` baseline separately; confirm no new error originates from changed unit-report files (plan Verification Boundaries)
- [X] T075 [P] Run `rg -n "sub-reports|PROJECT_SUB_REPORTS|project-sub-reports" apps/web/src apps/web/e2e e2e` and confirm references remain only in explicit not-found/retirement assertions or migration documentation (quickstart §8)
- [X] T076 Run full quickstart validation sequence (RED/GREEN evidence, migration verifier, focused suites, concurrency, regression) per `specs/032-unit-report-source-truth/quickstart.md` §2–§7 and record results

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (`SpecialtyUnit` vocabulary) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational
- **US2 (Phase 4)**: Depends on US1 (workflow state machine exists before permission enforcement on actions)
- **US3 (Phase 5)**: Depends on US1 (eligible sources are current unit reports). US2 recommended first but not required for eligibility tests.
- **US4 (Phase 6)**: Depends on US1 (versioning/correction) + US3 (rebuild orchestration to make idempotent)
- **US5 (Phase 7)**: Depends on US1 (replacement authoring surface exists). Independent of US2–US4 for route removal; UI hints depend on the shared registry from Phase 1.
- **US6 (Phase 8)**: Depends on Foundational schema (Phase 2) for trace/quarantine tables; the **final constraint migration (T069) depends on US1–US5 being complete** so canonical-only reports coexist safely with backfill
- **Polish (Phase 9)**: Depends on all desired user stories

### User Story Dependencies

- **US1 (P1)**: After Foundational — no dependencies on other stories
- **US2 (P1)**: After Foundational + US1
- **US3 (P1)**: After Foundational + US1
- **US4 (P1)**: After US1 + US3
- **US5 (P1)**: After Foundational + US1 (parallel with US2/US3/US4 possible)
- **US6 (P2)**: After Foundational; constraints land last (T069 gates on US5 cutover)

### Within Each User Story

- Tests MUST be written and confirmed FAILING before implementation (TDD)
- Models before services; services before endpoints; endpoints before frontend integration
- Backend contract before typed frontend client
- Story complete before moving to next priority

### Parallel Opportunities

- Phase 1: T002–T003 parallel with T001
- Phase 2: T005–T010 all parallel (different model files)
- US1: T012–T013 parallel; T015–T016 parallel; T019 parallel with backend work
- US2: T024–T026 parallel
- US3: T032–T035 parallel (four test files); T043 parallel with backend
- US4: T045–T047 parallel
- US5: T053–T054 parallel; T059 parallel
- US6: T061–T063 parallel
- Polish: T071–T072 parallel with T074–T075

---

## Parallel Example: User Story 3

```bash
# Launch all tests for User Story 3 together:
Task: "Template contract tests in apps/api/core/project_templates/tests/test_required_report_units.py"
Task: "Aggregation eligibility tests in apps/api/core/field_reports/tests/test_unit_report_aggregation_eligibility.py"
Task: "Completeness tests in apps/api/core/field_reports/tests/test_unit_report_completeness.py"
Task: "Provenance tests in apps/api/core/field_reports/tests/test_unit_report_provenance.py"

# Then implementation (template config before aggregation binding):
Task: "Template required-unit validation in apps/api/core/project_templates/serializers.py"
Task: "Eligibility + derivation keys in apps/api/core/field_reports/services/daily_report_aggregation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (canonical vocabulary)
2. Complete Phase 2: Foundational expand schema (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (tests RED → GREEN)
4. **STOP and VALIDATE**: Author a Buildings report end-to-end on the unit page against local Postgres/Redis
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → schema expanded, no behavior change
2. Add US1 → test independently → authoring works (MVP)
3. Add US2 → test independently → authorization/SoD enforced
4. Add US3 → test independently → summary derives solely from eligible reports
5. Add US4 → test independently → corrections/rebuilds idempotent
6. Add US5 → test independently → legacy workflow unreachable
7. Add US6 → migration rehearsal + rollback evidence → constraint migration lands

### TDD Discipline

- Capture RED failures showing missing canonical fields/constraints/behavior — import/setup errors are not valid RED
- `sub_reports/tests/test_unit_report_migrations.py` RED comes first overall (research D11: migration accounting is the highest-risk foundation)
- Existing summary isolation/metadata/permission tests (`test_daily_report_summary_*`) remain regression anchors and must stay green throughout
- Commit after each task or logical group; stop at any checkpoint to validate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Docker is unavailable in the cloud VM: start Postgres (`sudo pg_ctlcluster 16 main start`) and Redis (`sudo redis-server /etc/redis/redis.conf --daemonize yes`) before running backend tests; migration/concurrency tests run only against disposable local/test databases
- Do NOT `pip install -r requirements-dev.txt`; use the existing `apps/api/.venv` pytest tooling (AGENTS.md)
- Detailed specialty-section field contracts (labor/equipment/materials/concrete/etc.) are deferred to the next feature; every row still needs stable source-row identity for provenance
- No destructive cleanup in this feature; retirement milestone for legacy `discipline` field/tables is recorded during planning (FR-032, research D2)

---

## Phase 10: Convergence

- [X] T077 Implement PostgreSQL concurrency tests in `apps/api/core/sub_reports/tests/test_unit_report_concurrency.py` per T071, spec Edge Cases (concurrent rebuild), quickstart §6, and SC-004 (missing)
- [X] T078 Update legacy test helper `field_reports/tests/daily_report_summary_helpers.py` and affected suites in `apps/api/core/field_reports/tests/` to use canonical units and attributes per T073, FR-001, quickstart §7, and Constitution II (partial)
- [X] T079 Implement full bilingual real-stack Playwright acceptance scenarios in `apps/web/e2e/tests/unit-report-source-truth.spec.ts` covering quickstart §9 scenarios 1–10 in fa and en per T072, SC-010, and Constitution III (missing)
- [X] T080 Update `apps/web/e2e/tests/daily-report.spec.ts`, `apps/web/e2e/helpers/project.ts`, `decision-tree-interactive-workflows.spec.ts`, and `decision-tree-project-domains.spec.ts` to replace legacy `/sub-reports` seeding and URL assertions with canonical unit endpoints and 404 assertions per T072, T075, FR-029, and FR-030 (contradicts)
- [X] T081 Update decision tree state machine in `docs/decision-tree/` to retire `/projects/:projectId/sub-reports` (mark 404 not-found) and map canonical unit daily reporting workflows under Specialty Units per FR-029, Constitution Quality Gates, and repository decision-tree rules (contradicts)
- [X] T082 Execute full quickstart validation sequence (§2–§7) and record comprehensive verification evidence per T076, SC-001–SC-010, and Constitution VI (partial)

