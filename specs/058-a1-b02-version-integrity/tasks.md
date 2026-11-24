# Tasks: Phase A.1 Daily Report Version Integrity, Derived-Row Lock & Lineage Preservation (B02)

**Input**: Design documents from `/specs/058-a1-b02-version-integrity/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/version-integrity-api.md`, `quickstart.md`  
**Formal Deliverable**: `A.1.03` (Technical readiness unlocks `B03`/`B04`; employer final acceptance remains gated on independent review in `B06`.)  
**Evidence**: [Stage 4.2 implementation evidence](implementation-evidence.md)  
**Database Migrations**: `0` new migrations required (reuses verified 40/40 blueprint + 25 extension tables from B01).  
**Tests**: Explicitly required by `spec.md` (`SC-001`–`SC-007`) and Stage 1.2 QA (`DEF-B02-01`–`DEF-B02-06`, 0 `XFAIL` markers).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: User story label (`[US1]`–`[US5]`) for user story phases only
- Every task includes exact repository file path(s)

---

## Phase 1: Setup (Shared Verification & Test Scaffolding)

**Purpose**: Verify B01 baseline integrity and prepare shared multi-unit test fixtures for B02.

- [X] T001 Verify B01 handoff baseline (`specs/057-a1-b01-data-contract`) and PostgreSQL blueprint schema (`40/40` blueprint + `25` extension tables, `0` pending migrations) using `apps/api/core/manage.py verify_blueprint_schema`
- [X] T002 Create B02 test suite scaffolding and shared multi-unit, two-source approved summary fixtures (including preparer, approver, read-only viewer, unauthorized member, cross-project user, and system-admin observer personas) in `apps/api/core/field_reports/tests/test_a1_b02_version_integrity.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared bilingual error definitions and the dedicated ownership-based derived-lock helper module required by all user stories.

**⚠️ CRITICAL**: Complete Phase 2 before starting User Story phases.

- [X] T003 [P] Add bilingual (`fa` and `en`) stable lifecycle/lock/rebuild error codes (`report_not_current`, `historical_rebuild_rejected`, `rebuild_target_deleted`, `report_not_editable`, `report_locked`, `derived_collection_read_only`, `derived_readonly`, `sod_self_approval_forbidden`) in `apps/api/core/field_reports/services/lifecycle_errors.py`
- [X] T004 [P] Create dedicated derived-ownership lock helper module `apps/api/core/field_reports/services/derived_lock.py` implementing `is_derived_row(row, report=None)` (checks `is_derived`, `source_sub_report_id`, `source_report_id`, and `DailyReportDerivedSource` existence), `report_has_derived_rows(report)`, `assert_report_editable(report, request=None)` (rejects `is_deleted`, `not is_current`, `status == APPROVED`, non-editable status), and `assert_child_row_mutable(report, row=None, request=None)`

**Checkpoint**: Foundation ready — bilingual error codes and shared ownership lock helpers are in place.

---

## Phase 3: User Story 1 - Preserve Derived-Summary Identity & Lock Derived Rows Across Revisions (Priority: P1) 🎯 MVP

**Goal**: Preserve `is_auto_summary` (and B01 contract header metadata) on correction revisions and block direct creation, update, or deletion of derived rows across UI, child single-row, batch upsert, legacy nested `partial_update`, and offline `sync_batch` paths while keeping authorized project-level metadata editable (`D01`, `W02`, `W03`, `X01`, `DEF-B02-01`, `DEF-B02-02`).

**Independent Test**: Open a correction on an approved two-unit derived summary (`reason` >= 10 chars), verify `v2.is_auto_summary == True`, verify `POST`/`PATCH`/`DELETE` on derived rows via single-row child endpoints, labor batch upsert, legacy nested `activities` PATCH, and `sync-batch` are all rejected (`400` / error `derived_collection_read_only` or `derived_readonly`) with 0 stored mutations, and verify editing authorized project-level metadata (`management_opinion`) succeeds (`200`).

- [X] T005 [US1] Preserve `is_auto_summary`, `is_synthetic_reference`, `contract_version`, and `presentation_profile_code` from `source_report` to `result` inside `open_correction()` in `apps/api/core/field_reports/services/correction_service.py`
- [X] T006 [US1] Enforce `assert_child_row_mutable` (checking `is_deleted`, `is_current`, `is_auto_summary`, status lock, and row-level `is_derived_row` ownership) across `_assert_editable`, `create`, `_batch_upsert`, `perform_update`, and `destroy` in `DailyReportChildViewSet` in `apps/api/core/field_reports/daily_report_views.py`
- [X] T007 [US1] Enforce non-current/deleted guard and `report_has_derived_rows` derived-section rejection (blocking legacy nested `activities`/derived payloads while keeping authorized project-level summary metadata editable) in `DailyReportViewSet.partial_update` in `apps/api/core/field_reports/daily_report_views.py`
- [X] T008 [P] [US1] Harden `sync_batch()` in `apps/api/core/field_reports/services/__init__.py` to reject derived-section payloads whenever target is new, `is_auto_summary=True`, or `report_has_derived_rows(existing)` is true while retaining `B01`/`A.8` ownership of `X01` offline sync
- [X] T009 [US1] Implement US1 automated tests (`DEF-B02-01`, `DEF-B02-02`, `X01`) verifying derived-summary identity retention on correction, rejection of single-row/batch/legacy/offline derived-row mutations (including defense-in-depth when `is_auto_summary=False` on a row with `is_derived=True` or provenance), and permitted management metadata edits in `apps/api/core/field_reports/tests/test_a1_b02_version_integrity.py`

**Checkpoint**: User Story 1 (MVP) is complete and independently testable.

---

## Phase 4: User Story 2 - Preserve Complete Multi-Source Provenance & Lineage Across Revisions (Priority: P1)

**Goal**: Clone and remap the complete multi-source `DailyReportDerivedSource` set to the exact new child row UUIDs in `v_{n+1}`, clone B01 `DailyReportWorkedShift` rows, and guarantee lossless restoration on correction cancellation (`W02`, `W04`, `DEF-B02-03`).

**Independent Test**: Start with an approved summary having a derived row aggregated from 2 distinct unit sources (`2` `DailyReportDerivedSource` rows), open a correction, verify `v2` has `2` remapped provenance rows pointing to `v2`'s child row UUID via `GET .../provenance/{kind}/{row}/`, approve `v2` and verify both `v1` and `v2` retain independent 2-source provenance, and in a separate branch cancel a correction and verify the restored approved version still exposes all `2` sources.

- [X] T010 [US2] Update `_clone_children(source, target)` in `apps/api/core/field_reports/services/correction_service.py` to build an `old_row_id -> new_row_id` UUID map across all 10 `CHILD_CLONE_SPECS` models (plus `str(source.id) -> str(target.id)`), bulk-create cloned `DailyReportDerivedSource` rows on `target` with remapped `derived_row_id` preserving all source metadata and `ordinal` (respecting `unique_derived_source_key`), and clone `DailyReportWorkedShift` rows (`worked_shifts`, preserving `shift_id` in `{1, 2, 3}` and `actual_duration_hours`)
- [X] T011 [US2] Update `cancel_correction()` in `apps/api/core/field_reports/services/correction_service.py` to call `invalidate_activity_log_cache(source.project_id)` upon restoring `source.is_current = True` and verify atomic restoration preserves `source`'s `is_auto_summary`, child rows, and complete `DailyReportDerivedSource` set
- [X] T012 [US2] Implement US2 automated tests (`DEF-B02-03`, `W02`, `W04`) verifying 2-source provenance cloning, remapped UUID drill-down via `GET .../provenance/{derived_kind}/{derived_row}/`, `worked_shifts` preservation, independent post-approval provenance on `v1` and `v2`, and lossless cancellation restoration in `apps/api/core/field_reports/tests/test_a1_b02_version_integrity.py`

**Checkpoint**: User Stories 1 and 2 both pass independently with complete multi-source lineage.

---

## Phase 5: User Story 3 - Preserve Management Opinion, Overrides, Version-Bound Metadata & Explicit Rebuild Rejection (Priority: P1)

**Goal**: Preserve `management_opinion`, `weather_override`, `site_status_override`, `reporting_configuration`, `aggregation_fingerprint`, and `aggregated_at` across correction creation and editable-draft rebuilds while enforcing explicit `FR-011`/`SC-006` rejection semantics for approved, historical/non-current, archived, and deleted rebuild targets (`W05`, `W06`, `DEF-B02-04`, `DEF-B02-06`).

**Independent Test**: Save `management_opinion` and `weather_override=True` on an approved summary, open a correction (`v2`) and verify both plus `reporting_configuration`/`aggregation_fingerprint`/`aggregated_at` are preserved (with approval timestamps unset), update a source unit and rebuild `v2` (`FR-009`) verifying derived rows refresh while opinion/overrides stay intact, invoke explicit rebuild (service & `POST .../rebuild/`) against approved `v2`, historical/non-current `v1`, and deleted/cancelled `v3` verifying bilingual rejection with 0 mutations (`FR-011`/`SC-006`), and verify implicit unit-trigger (`report=None`) leaves an approved current snapshot immutable while surfacing drift (`FR-012`).

- [X] T013 [US3] Preserve `management_opinion`, `weather_override`, `site_status_override`, `reporting_configuration`, `aggregation_fingerprint`, and `aggregated_at` in `open_correction()` in `apps/api/core/field_reports/services/correction_service.py` while keeping version-bound workflow/approval fields (`submitted_by`, `submitted_at`, `reviewed_by`, `reviewed_at`, `approved_by`, `approved_at`, `rejection_reason`) clean on the new draft revision
- [X] T014 [US3] Implement explicit `FR-011`/`SC-006` rejection semantics in `rebuild_daily_report_summary()` and update `ensure_daily_report_summary()` in `apps/api/core/field_reports/services/daily_report_aggregation.py`: when `report` is explicitly targeted, raise bilingual `ValidationError` (`rebuild_target_deleted` if `is_deleted`, `historical_rebuild_rejected` if `not is_current`, `report_locked` if `status == APPROVED`, `report_not_editable` if `status in {SUBMITTED, UNDER_REVIEW}`); when called implicitly (`report=None`), leave approved/non-editable current snapshots untouched (`FR-012`) while rebuilding current `DRAFT`/`REJECTED` reports (`FR-009`) preserving `management_opinion`, `weather_override`, and `site_status_override`
- [X] T015 [US3] Add explicit `POST /api/v1/projects/{project_pk}/daily-reports/{pk}/rebuild/` action on `DailyReportViewSet` in `apps/api/core/field_reports/daily_report_views.py` requiring active project membership + `edit_reports` and delegating to `rebuild_daily_report_summary(..., report=instance)` (passing `request` for bilingual `fa`/`en` error messages)
- [X] T016 [US3] Implement US3 automated tests (`DEF-B02-04`, `DEF-B02-06`, `FR-009`, `FR-011`, `FR-012`) covering opinion/override/config preservation on correction & rebuild, explicit rebuild rejection (service & `POST .../rebuild/`) for approved, historical/non-current, archived, submitted, and deleted targets with 0 mutations, implicit unit-trigger approved-snapshot immutability + drift comparison, and bilingual FA/EN error messages in `apps/api/core/field_reports/tests/test_a1_b02_version_integrity.py`

**Checkpoint**: User Stories 1, 2, and 3 all pass independently.

---

## Phase 6: User Story 4 - Count Only the Current Approved Version in the Official Activity Master Log (Priority: P1)

**Goal**: Restrict `activity_log_queryset()` to `report__status=APPROVED` AND `report__is_current=True` AND `report__is_deleted=False` so official totals never double-count superseded versions while keeping version history separate and handing off the exact queryset policy to Package `B04` (`E15`, `DEF-B02-05`).

**Independent Test**: Approve `v1` (quantity `5`, headcount `4`), open and approve correction `v2` (quantity `5`, headcount `4`), query `GET .../activity-log/` and `GET .../activity-log/excel/` and verify exactly `1` row with quantity `5` and headcount `4` (never `2` rows / `10` / `8`), verify unapproved drafts are excluded, verify cancelled corrections restore `v1` cleanly, and verify `GET .../daily-reports/{v2_id}/versions/` still lists both `v1` and `v2`.

- [X] T017 [US4] Add `report__is_current=True` to the official approved filter (and `report__is_deleted=False` guard) in `activity_log_queryset()` in `apps/api/core/field_reports/services/activity_log.py`
- [X] T018 [US4] Implement US4 automated tests (`DEF-B02-05`, `E15`) verifying single-version counting (`1` row, `quantity=5`, `headcount=4` across two approved versions) in `GET .../activity-log/` and `GET .../activity-log/excel/`, exclusion of open draft revisions, clean restoration after cancel, and separate version-history visibility via `GET .../versions/` in `apps/api/core/field_reports/tests/test_a1_b02_version_integrity.py`

**Checkpoint**: All four P1 defect-closing user stories (US1–US4) pass independently.

---

## Phase 7: User Story 5 - Logical Uniqueness, Six-Unit Effective Config, Eligible Sources, Concurrency & Role-Safe Workflow (Priority: P2)

**Goal**: Prove and harden preserved B02 invariants (`H06`, `D02`, `D03`, `W01`, `C03`, `C09`), including concurrent correction locking, read-only viewer `by-date` access, two-version date-effective six-unit templates, negative source eligibility, active-membership RBAC, cross-project isolation, and separation of duties (SoD).

**Independent Test**: Run concurrent correction requests (1 succeeds, 2nd returns `correction_already_open`), open `by-date` repeatedly as editor and read-only viewer (no duplicates, viewer succeeds without `edit_reports`), test two `ProjectReportingConfiguration` versions with different effective dates across the 6 valid units, inject ineligible sources (draft/rejected/deleted/superseded/other-date/other-project → 0 rows & 0 completeness), verify `C09` summary approval independence, and verify SoD/RBAC/cross-project/admin-observer denials and `<10`-char rejection/correction reason errors.

- [X] T019 [US5] Verify and enforce server-side separation of duties (rejecting self-approval with `sod_self_approval_forbidden` when `instance.submitted_by_id == request.user.id` and `instance.submitted_by_id` is set, unless explicitly exempted by project policy) and active project-membership mutation checks across `DailyReportViewSet._approve`, `_reject`, `correction_requests`, `rebuild`, and `DailyReportCorrectionCancelView` in `apps/api/core/field_reports/daily_report_views.py`
- [X] T020 [US5] Implement US5 automated tests (`H06`, `D02`, `D03`, `W01`, `C03`, `C09`) covering concurrent correction requests, repeated `by-date` & read-only viewer access, two date-effective six-unit `ProjectReportingConfiguration` versions, all ineligible source types (draft/rejected/deleted/superseded/other-date/other-project), `C09` summary-vs-source approval independence, `<10`-char correction/rejection reasons, cross-project & unauthorized role & system-admin-observer mutation denials (`403`), and SoD enforcement in `apps/api/core/field_reports/tests/test_a1_b02_version_integrity.py`

**Checkpoint**: All 5 user stories (US1–US5) pass with full traceability.

---

## Phase 8: Polish, Documentation & Full Verification

**Purpose**: Update API documentation, run full B02 + regression test suites (0 `XFAIL`), verify live UI/API bilingual behavior, refresh graphify index, and record technical-readiness boundary.

- [X] T021 [P] Document `POST /api/v1/projects/{project_pk}/daily-reports/{pk}/rebuild/`, derived-row ownership lock error codes, and current-approved activity-log policy in `apps/api/core/field_reports/ENDPOINTS.md`
- [X] T022 Run full B02 test suite (`test_a1_b02_version_integrity.py`) and all 11 daily-report regression suites listed in `specs/058-a1-b02-version-integrity/quickstart.md` via `apps/api/.venv/bin/python -m pytest` (assert 100% pass, 0 failures, 0 `XFAIL` markers for B02)
- [X] T023 Verify `verify_blueprint_schema` (`40/40` blueprint + `25` extension tables) and run live API/UI bilingual (`fa`/`en`) walkthrough of existing frontend consumers (`apps/web/src/app/routes/daily-report-view.tsx`, `apps/web/src/app/routes/project-activity-log.tsx`) per `specs/058-a1-b02-version-integrity/quickstart.md`
- [X] T024 Run `graphify update .` after code changes and confirm B02 technical readiness (`A.1.03`) is reported separately from employer final acceptance (gated in Package `B06`)

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Starts immediately (`T001` → `T002`).
- **Phase 2 (Foundational)**: Depends on Phase 1; `T003` and `T004` run in parallel and BLOCK Phases 3–7.
- **Phase 3 (US1, P1)** → **Phase 4 (US2, P1)** → **Phase 5 (US3, P1)**: All touch `correction_service.py` / `daily_report_views.py` and build cleanly in order; `T008` (`services/__init__.py`) can run in parallel within US1.
- **Phase 6 (US4, P1)**: Touches only `activity_log.py` and `test_a1_b02_version_integrity.py` — can execute in parallel with US1–US3 after Phase 2.
- **Phase 7 (US5, P2)**: Depends on Phases 3–5 (tests full lifecycle + SoD/RBAC/concurrency/templates).
- **Phase 8 (Polish)**: Depends on all user stories (`T021` can run in parallel with late test writing; `T022`–`T024` run sequentially on the final tree).

### Parallel Opportunities
- **Phase 2**: `T003` (`lifecycle_errors.py`) and `T004` (`derived_lock.py`) touch distinct files and run in parallel.
- **Phase 3**: `T008` (`services/__init__.py`) runs in parallel with `T005`–`T007`.
- **Phase 6**: `T017` (`activity_log.py`) runs in parallel with US1/US2/US3 backend edits.
- **Phase 8**: `T021` (`ENDPOINTS.md`) runs in parallel with final test preparation before `T022`–`T024`.

## Implementation Strategy

1. **MVP First (Phases 1–3 / US1)**: Establish bilingual error codes, `derived_lock.py`, `is_auto_summary` retention, and ownership-based mutation guards across all 4 write boundaries (single-row, batch, legacy nested, offline sync).
2. **Complete P1 Defect Closure (Phases 4–6 / US2–US4)**: Add complete `DailyReportDerivedSource` UUID remapping + `worked_shifts`, preserve management opinion/overrides/config metadata, enforce explicit `FR-011`/`SC-006` rebuild rejection vs. implicit `FR-012` no-op, and lock `activity_log_queryset` to `is_current=True`.
3. **Full Workflow & Governance Proof (Phases 7–8 / US5 + Polish)**: Harden and prove SoD/RBAC/concurrency/six-unit templates/source eligibility, update `ENDPOINTS.md`, pass all pytest + regression suites with 0 `XFAIL`, and verify live bilingual behavior while keeping employer final acceptance explicitly in `B06`.
