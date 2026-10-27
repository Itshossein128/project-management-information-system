---
description: "TDD implementation tasks for reliable specialty-unit offline sync"
---

# Tasks: ثبت آفلاین و همگام‌سازی مطمئن گزارش واحد

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [sync contract](contracts/sync-v2.md), [UI contract](contracts/ui-recovery.md), [quickstart.md](quickstart.md).
**Scope**: implementation work only after this task-generation step. Paths are repository-relative. All stories are P1; [US1]–[US8] map directly to the specification.

## TDD execution rules

For every behavior, write the named canonical test first and run it against the unchanged relevant implementation. Record the exact command and observed assertion failure (RED); an import/setup error, existing probe PASS or skipped test is not behavioral RED. If behavior already passes, document the existing proof and investigate coverage instead of forcing a failure. Make the minimum coherent product change, run the same assertions GREEN, then run relevant regression tests. Do not remove/weaken assertions, skip, stub or mass-replace tests to obtain green. Where an old assertion explicitly requires a now-prohibited destructive behavior, replace it with stronger contract assertions and document why. Use a unique PostgreSQL test DB per process and record separate backend, API, real two-connection race, browser, migration, typecheck and live evidence. A task checkbox denotes completed work with evidence, not a planned change.

`[P]` marks only tasks in the same stage with independent files and no dependency on incomplete tasks; RED tasks may be authored in parallel but execute against isolated databases. Do not concurrently edit the same shared file. New test filenames below are intended canonical paths, not claims they exist today. No production deployment is authorized by this task list.

## Phase 1: Setup

**Purpose**: establish accurate baseline, executable test tooling and safe test data without changing the product.

- [X] T001 Inspect `specs/037-daily-offline-sync/spec.md`, `specs/037-daily-offline-sync/plan.md`, `.specify/feature.json` and Git status; record current commit, active feature, existing dirty files and a G01–G13 evidence inventory in `specs/037-daily-offline-sync/verification/baseline.md`, without claiming a gap fixed from file existence or old tests.
- [X] T002 Inventory each effective section, its unit page, mutation, backend writer, validation and permissions in `specs/037-daily-offline-sync/verification/section-writer-inventory.md` using `apps/web/src/components/department/`, `apps/api/core/sub_reports/unit_report_views.py`, `apps/api/core/sub_reports/unit_report_services.py` and legacy `apps/api/core/field_reports/`; include all six canonical units and sections, not just activities/labor/materials.
- [X] T003 Establish a documented executable canonical TypeScript test command for `apps/web/src/app/lib/__tests__/offlineDB.test.ts` and new offline tests using the installed project tooling; add minimal runner configuration only if required in `apps/web/package.json` and record the exact command in `specs/037-daily-offline-sync/quickstart.md` without upgrading the stack.
- [X] T004 Set up isolated PostgreSQL/Redis, browser profile and fixture instructions in `specs/037-daily-offline-sync/verification/environment.md` using `specs/037-daily-offline-sync/quickstart.md`; run existing targeted baseline only on a unique test DB, preserve logs and note unavailable services, without treating prior 17 tests or probes as acceptance.

## Phase 2: Foundational safety and shared contracts

**Purpose**: block unsafe mutation paths and establish durable identity, revision and authorization before enabling a new sync client. **Gate**: complete T005–T017 before story implementation; story tests can use controlled fixtures but must not bypass this gate.

### Tests first

- [X] T005 [P] Add and run RED API tests in `apps/api/core/field_reports/tests/test_offline_legacy_protection.py` for derived row create, child PATCH/DELETE, summary PATCH including `activities: []`, existing-summary batch and legacy create/batch; assert `derived_readonly`, unchanged rows/provenance and no shell after invalid header.
- [X] T006 [P] Add and run RED tests in `apps/api/core/sub_reports/tests/test_offline_sync_foundation.py` for actor/project scoping, active membership and permission including existing admin policy, cross-project target/reference refusal, immutable operation ID/fingerprint, and exact same-ID replay outcome.
- [X] T007 [P] Add and run RED migration tests in `apps/api/core/sub_reports/tests/test_offline_sync_migrations.py` for historical reports, rows, lineage, references, revisions and receipt constraints through apply/backfill and supported rollback/restore; use disposable data.
- [X] T008 [P] Add and run RED local persistence/upgrade tests in `apps/web/src/app/lib/__tests__/offlineMigration.test.ts` for legacy schema data, unknown actor/unit quarantine, atomic upgrade abort/storage failure and retained raw records; never clear stores.

### Implementation and GREEN

- [X] T009 Close the derived/atomicity bypasses in `apps/api/core/field_reports/daily_report_views.py` and `apps/api/core/field_reports/services/__init__.py`: protect every auto-summary path with `derived_readonly`, validate/rollback before shell effects, and preserve safe legacy `results/summary` and `conflict` semantics; run T005 GREEN.
- [X] T010 Add receipt and revision models/expand migrations in `apps/api/core/sub_reports/models.py` and `apps/api/core/sub_reports/migrations/`: "Unique `(project, actor, operation_id)`", immutable canonical fingerprint, terminal result and target mapping; preserve receipt retention for supported retries and backfill tokens without changing business data; run T007 GREEN including rollback/restore.
- [X] T011 Implement receipt fingerprint, authorization and commit-with-mutation primitives in `apps/api/core/sub_reports/services/offline_sync.py`; identical `(project, actor, operation_id)` plus fingerprint returns prior result, changed payload returns `operation_id_reused`, retryable failure is not recorded as success, and receipt reads require current authorized scope; run `apps/api/core/sub_reports/tests/test_offline_receipt_service.py` GREEN; T006 is API-level and remains RED until the v2 endpoint and dispatch exist at T035.
- [X] T012 Implement parent-before-child/receipt lock protocol and target revision primitives in `apps/api/core/sub_reports/unit_report_services.py` and `apps/api/core/sub_reports/services/offline_sync.py`; "Each mutable row and editable header has a monotonically changing revision or equivalent opaque token" and "deletes leave a detectable tombstone/version"; apply in all writers before v2 is enabled.
- [X] T013 Extend existing writer and workflow entry points in `apps/api/core/sub_reports/unit_report_views.py`, `apps/api/core/sub_reports/services/`, `apps/api/core/field_reports/daily_report_views.py` and `apps/api/core/field_reports/services/` using T002 inventory so online, legacy, correction, delete and workflow transitions participate in the same locking/revision protocol; preserve eligible aggregation and existing authorization policy.
- [X] T014 Extend `apps/web/src/app/lib/offlineDB.ts` with additive local schema and atomic upgrade: "preserve IndexedDB name", keep original raw records and conversion provenance, only map proven actor/project/unit/date/target, quarantine unknown ownership without disclosure, abort failed upgrade without clearing; run T008 GREEN.
- [X] T015 Add scope-aware local snapshot and immutable operation primitives in `apps/web/src/app/lib/offlineDB.ts` and `apps/web/src/app/lib/offlineWrite.ts`: independent report/row/operation identifiers, UUIDv4 row identity, actor/project/unit ownership, immutable payload and dependency history; snapshot plus operation commit atomically before success.
- [X] T016 Implement versioned request/result types and scoped endpoint registration in `apps/api/core/sub_reports/urls.py`, `apps/api/core/sub_reports/unit_report_views.py` and `apps/web/src/app/lib/api/unit-reports.ts` per `specs/037-daily-offline-sync/contracts/sync-v2.md`; keep v2 disabled until T009–T015 and legacy-compatible reader/writer deployment are verified.
- [X] T017 Run T005, T007, T008 and `apps/api/core/sub_reports/tests/test_offline_receipt_service.py`, plus relevant `apps/api/core/field_reports/tests/test_sync_batch.py` and `apps/api/core/sub_reports/tests/test_unit_report_permissions.py`, on final foundation; record T006 as pending endpoint/dispatch and capture RED/GREEN, migration evidence and justified changed legacy expectations in `specs/037-daily-offline-sync/verification/foundation.md`.

## Phase 3: User Story 1 — ادامه ثبت در فرم فعلی واحد (P1)

**Goal**: persist allowed local edits in the current unit pages with stable identities. **Independent test**: authenticate/cache, disconnect before and during save, create/edit/delete in an enabled unit section, then inspect durable local content and current server report without duplicates.

### Tests first

- [ ] T018 [P] [US1] Write and run RED real-browser tests in `apps/web/e2e/tests/unit-offline-entry.spec.ts` for offline and interrupted request on current unit page, enabled/disabled section behavior, stable UUIDv4 client ID and independent operation IDs, durable-success-only feedback, storage failure retaining input and missing reference explanation.
- [X] T019 [P] [US1] Write and run RED API tests in `apps/api/core/sub_reports/tests/test_offline_unit_draft.py` for local draft matching authorized project/unit/date current report, no duplicate current, no overwrite of divergent draft and rejection of raw project creation.

### Implementation

- [X] T020 [US1] Cache actor-scoped effective project/unit configuration and required reference data in `apps/web/src/app/lib/offlineCache.ts`; surface uncached prerequisites without clearing previously saved edits.
- [X] T021 [US1] Connect unit draft creation/lookup in `apps/web/src/components/department/unit-daily-report-panel.tsx` and `apps/web/src/app/hooks/queries.ts` to T015 local persistence and authoritative unit matching, without creating project summary or independent `/sub-reports` flow.
- [X] T022 [US1] Route create/edit/delete of activities, labor and materials through scoped online/offline operations in `apps/web/src/components/department/section-activities.tsx`, `apps/web/src/components/department/section-labor.tsx`, `apps/web/src/components/department/section-materials.tsx` and `apps/web/src/app/lib/offlineWrite.ts`; persist before feedback and preserve input on failure.
- [X] T023 [US1] Apply the same behavior to all other currently effective editable sections identified by T002 in `apps/web/src/components/department/section-machinery.tsx`, `section-concrete.tsx`, `section-general.tsx`, `section-structured.tsx`, `section-issues.tsx`, `section-visits.tsx` and `section-hse.tsx`; do not invent a new section or offline binary upload.
- [ ] T024 [US1] Implement scoped unit report create-or-match in `apps/api/core/sub_reports/services/offline_sync.py` using existing `apps/api/core/sub_reports/unit_report_services.py`, validating header atomically, respecting current report and returning conflict on divergence; run T018–T019 GREEN and capture G01/G07 evidence.

## Phase 4: User Story 2 — مشاهده و بازیابی کامل داده محلی (P1)

**Goal**: full local content is visible and recoverable without silent replacement. **Independent test**: seed a local report with header, create/edit/delete/error, refresh and reopen the same browser profile while offline, then inspect and edit all content.

### Tests first

- [ ] T025 [P] [US2] Write and run RED browser tests in `apps/web/e2e/tests/unit-offline-recovery.spec.ts` for refresh and actual close/reopen of a persistent profile offline, restoring header/rows/tombstones/IDs/status/errors and opening draft from the same unit list.
- [X] T026 [P] [US2] Write and run RED local tests in `apps/web/src/app/lib/__tests__/offlineHydration.test.ts` for server refetch/row reconstruction preserving local overlay and pending deletes, including unchanged unrelated server rows.
- [ ] T027 [P] [US2] Write and run RED accessible bilingual status tests in `apps/web/e2e/tests/unit-offline-status.spec.ts` for yellow cloud and named pending text plus distinct sending/synced/failed/conflict, keyboard interaction and no color-only state.

### Implementation

- [X] T028 [US2] Implement local report hydration, base/overlay and tombstone reconciliation in `apps/web/src/app/lib/offlineDB.ts` and `apps/web/src/app/hooks/queries.ts`; keep stored local modifications on refresh and server revalidation.
- [X] T029 [US2] Expose full draft navigation and editing in `apps/web/src/components/department/unit-daily-report-panel.tsx` and `apps/web/src/components/department/department-page.tsx` with actor/project/unit scope.
- [ ] T030 [US2] Render accessible per-row status and localize labels in `apps/web/src/components/department/section-activities.tsx`, `section-labor.tsx`, `section-materials.tsx`, remaining T002 sections, `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`; run T025–T027 GREEN and record SC-02/G08.

## Phase 5: User Story 3 — ارسال دقیق عملیات و تأیید قابل اعتماد (P1)

**Goal**: independent operations sync automatically with truthful per-operation receipts and atomic effects. **Independent test**: prepare ten independent offline operations in three sections, reconnect and verify exact server rows and ten matched operation acknowledgments.

### Tests first

- [X] T031 [P] [US3] Write and run RED transformation/ack tests in `apps/web/src/app/lib/__tests__/syncOperations.test.ts` for POST collection with trailing slash, operation ID matching independent of order, missing/duplicate/unknown/malformed results, inconsistent `synced_ids`, exact client/server mapping and no unconfirmed queue removal.
- [X] T032 [P] [US3] Write and run RED integration tests in `apps/api/core/sub_reports/tests/test_sync_operations_api.py` for v2 outcomes, safe legacy response compatibility, ten independent changes, authorized scope and invalid header/create leaving no shell or receipt, with other report operations succeeding.
- [X] T033 [P] [US3] Write and run RED dependency/idempotency tests in `apps/api/core/sub_reports/tests/test_sync_operation_idempotency.py` for create→multiple edits→delete, blocked/missing/cyclic prerequisites, same-ID replay after lost response, altered payload rejection, server IDs and provenance without duplicate effects.
- [ ] T034 [P] [US3] Write and run RED real-browser test in `apps/web/e2e/tests/unit-offline-ten-operations.spec.ts` for ten operations across activity/labor/material, automatic reconnect without refresh/manual action, exact values and identities, no unrelated delete or duplicate.

### Implementation

- [X] T035 [US3] Implement v2 operation dispatch in `apps/api/core/sub_reports/services/offline_sync.py` and endpoint in `apps/api/core/sub_reports/unit_report_views.py`: separate transaction per operation, validate dependency graph and target scope, commit receipt with effect, report four distinct outcomes, permit independent operations to succeed, and run the T006 API contract GREEN with v2 enabled only for the isolated test.
- [X] T036 [US3] Integrate target-specific validation and mutations for all T002 section types in `apps/api/core/sub_reports/services/offline_sync.py` and `apps/api/core/sub_reports/services/section_validation.py`; preserve existing section validation, row IDs and attachments, never translate an omitted/empty snapshot into replacement.
- [X] T037 [US3] Implement target-operation serialization and safe ID-based response reconciliation in `apps/web/src/app/lib/syncService.ts` and `apps/web/src/app/lib/api/unit-reports.ts`; `synced_ids` consists only of operation IDs and successful create includes distinct client/server row mapping.
- [ ] T038 [US3] Start automatic sync on restored connection and valid session in `apps/web/src/app/hooks/useAutoSync.ts`, with predecessor receipt/revision ordering and no acknowledgment based on response position; run T031–T034 GREEN and record SC-01/G02/G09/G12.

## Phase 6: User Story 4 — حفظ داده دیگران و منبع تجمیع (P1)

**Goal**: protect other writers and read-only derived content. **Independent test**: update/delete one source row without a full cache, add/change a row as another user, and rebuild summary while asserting all unrelated data and provenance.

### Tests first

- [X] T039 [P] [US4] Write and run RED integration tests in `apps/api/core/sub_reports/tests/test_offline_target_isolation.py` for incomplete/empty snapshot, explicit PATCH/DELETE, unrelated concurrent addition, stale same-row conflict, unchanged IDs and project isolation.
- [X] T040 [P] [US4] Extend and run RED tests in `apps/api/core/field_reports/tests/test_daily_report_derived_readonly.py` for authored rows/empty arrays in create, PATCH, child and legacy/v2 batch; assert `derived_readonly`, unchanged provenance and history.
- [X] T041 [P] [US4] Extend and run RED aggregation tests in `apps/api/core/field_reports/tests/test_unit_report_aggregation_eligibility.py` and `apps/api/core/field_reports/tests/test_summary_attachment_counts.py` for current same-project/date eligible sources only, repeated rebuild, overrides, zero/empty/unknown, attachment references and no duplicated contribution.

### Implementation

- [X] T042 [US4] Implement targeted row update/delete with base revision and tombstones in `apps/api/core/sub_reports/services/offline_sync.py` and `apps/api/core/sub_reports/services/section_validation.py`; retain unrelated rows, detect same-target stale updates and preserve section invariants.
- [X] T043 [US4] Complete any missing legacy/summary derived guards and aggregation preservation discovered by T040–T041 in `apps/api/core/field_reports/daily_report_views.py` and `apps/api/core/field_reports/services/daily_report_aggregation.py`; do not change the eligibility lifecycle rules.
- [X] T044 [US4] Run T039–T041 GREEN and existing relevant summary/aggregation tests in `apps/api/core/field_reports/tests/`; document changed legacy destructive expectations and evidence for G03/G04 in `specs/037-daily-offline-sync/verification/aggregation.md`.

## Phase 7: User Story 5 — خطای ردیف و retry پس از اصلاح (P1)

**Goal**: isolate errors and send only a corrected target version. **Independent test**: send nine valid operations and one invalid, refresh, correct that row and retry without replaying successes.

### Tests first

- [X] T045 [P] [US5] Write and run RED tests in `apps/web/src/app/lib/__tests__/offlineRowRetry.test.ts` for stable field error linked to actor/project/unit/report/section/client/operation, persistence after refresh, new operation linked to invalid predecessor, immutable old payload and retry of target only.
- [ ] T046 [P] [US5] Write and run RED API/browser tests in `apps/api/core/sub_reports/tests/test_sync_operation_validation.py` and `apps/web/e2e/tests/unit-offline-row-retry.spec.ts` for nine successes plus one invalid, blocked dependent, localized field error and zero-success toast refusal.

### Implementation

- [X] T047 [US5] Implement structured stable per-field validation outcomes in `apps/api/core/sub_reports/services/offline_sync.py` and `apps/api/core/sub_reports/unit_report_views.py` with localized message separate from stable code and target identity.
- [X] T048 [US5] Persist error and operation supersession and implement target-only retry in `apps/web/src/app/lib/offlineDB.ts`, `apps/web/src/app/lib/offlineWrite.ts` and `apps/web/src/app/lib/syncService.ts`; send corrected payload only under new `operation_id`.
- [ ] T049 [US5] Wire inline field errors, retry and truthful status messages in `apps/web/src/components/department/section-activities.tsx`, `section-labor.tsx`, `section-materials.tsx`, remaining T002 section components and `apps/web/src/app/locales/fa.json`, `apps/web/src/app/locales/en.json`; run T045–T046 GREEN and record SC-03/G06.

## Phase 8: User Story 6 — احترام به قفل و نسخه جاری در رقابت (P1)

**Goal**: server current state wins under genuine concurrent transitions. **Independent test**: race two independent PostgreSQL connections across approve/sync, current replacement/ensure and simultaneous first drafts, assert persisted state and audit history.

### Tests first

- [ ] T050 [P] [US6] Extend and run RED transactional race tests in `apps/api/core/sub_reports/tests/test_unit_report_concurrency.py` using two independent PostgreSQL connections and barriers for approve versus sync, current change between lookup/ensure and write, same-key concurrent draft, plus locked header/notes/rows and history assertions.
- [X] T051 [P] [US6] Write and run RED integration tests in `apps/api/core/sub_reports/tests/test_sync_lock_contract.py` for `conflict_report_approved` plus `sync_conflict`, non-current/stale targets, unchanged local payload, denied permissions and no implicit submit/review/approve/reject/correction decision.

### Implementation

- [X] T052 [US6] Complete common parent locking and final current/status/permission revalidation in `apps/api/core/sub_reports/unit_report_services.py`, `apps/api/core/sub_reports/unit_report_views.py` and `apps/api/core/sub_reports/services/offline_sync.py`; include all competing writers and consistent lock order, not only sync.
- [X] T053 [US6] Handle missing-parent creation race and existing constraint violation deterministically in `apps/api/core/sub_reports/services/offline_sync.py` and `apps/api/core/sub_reports/models.py`; return conflict on divergent draft, never auto-retarget a locked/non-current version.
- [ ] T054 [US6] Preserve approved/current state, lineage and stable conflict codes in `apps/api/core/field_reports/services/__init__.py` and `apps/web/src/app/lib/syncService.ts`; run T050–T051 GREEN with real PostgreSQL independent connections and record SC-04/G05.

## Phase 9: User Story 7 — رسیدگی به تعارض بدون از دست رفتن کار (P1)

**Goal**: explicit server choice or authorized correction retains local data until reconciliation. **Independent test**: create conflict with full header and activity/labor/material rows, separately test server choice and formal correction including failure/retry.

### Tests first

- [ ] T055 [P] [US7] Write and run RED browser tests in `apps/web/e2e/tests/unit-offline-conflict.spec.ts` for full local/server header and rows, scope confirmation, server reconciliation without later resend, unrelated data preservation, bilingual accessible destination preview and correction failure/retry.
- [X] T056 [P] [US7] Write and run RED API tests in `apps/api/core/sub_reports/tests/test_offline_correction_transfer.py` for authorized unit/project formal correction intent, reason/lineage, retry without duplicate correction/row, denied permission, partial destination results and no direct approved PATCH.
- [X] T057 [P] [US7] Write and run RED local reconciliation tests in `apps/web/src/app/lib/__tests__/offlineConflictResolution.test.ts` for selected-scope atomic cleanup, unsent unrelated operations, retained conflict until acknowledged destination, and no resurrection after reload.

### Implementation

- [X] T058 [US7] Implement idempotent correction transfer intent using existing official unit/project flows in `apps/api/core/sub_reports/unit_report_services.py`, `apps/api/core/field_reports/services/correction_service.py` and `apps/api/core/sub_reports/services/offline_sync.py`; verify permission and current destination, preserve reason/lineage and avoid duplicate intent effects.
- [X] T059 [US7] Persist complete conflict snapshots and atomic scoped reconciliation/transfer progress in `apps/web/src/app/lib/offlineDB.ts` and `apps/web/src/app/lib/syncService.ts`; retain source until all relevant destination operations have matching receipts.
- [X] T060 [US7] Replace scalar-only/direct-PATCH conflict flow in `apps/web/src/components/sync/ConflictMergeEditor.tsx`, `apps/web/src/components/daily_reports/ConflictCard.tsx` and `apps/web/src/app/routes/sync-conflicts.tsx` with full section comparison, explicit confirmation, formal correction destination preview and localized keyboard-accessible actions.
- [ ] T061 [US7] Run T055–T057 GREEN and re-run correction/lineage suites in `apps/api/core/sub_reports/tests/test_unit_report_workflow.py` and `apps/api/core/field_reports/tests/`; capture SC-05/G10 without treating correction creation alone as successful transfer.

## Phase 10: User Story 8 — ادامه پس از اختلال و اجرای همپوشان (P1)

**Goal**: recover interrupted sends, concurrent tabs, account changes and legacy data safely. **Independent test**: interrupt before and after server commit, restart same profile, overlap two tabs, switch accounts and upgrade a real legacy store.

### Tests first

- [ ] T062 [P] [US8] Write and run RED browser tests in `apps/web/e2e/tests/unit-offline-interruption.spec.ts` for close during syncing before/after commit, reopen and automatic recovery, simultaneous manual/auto and two-tab sends, network loss, expired session and revoked permission.
- [X] T063 [P] [US8] Write and run RED local tests in `apps/web/src/app/lib/__tests__/offlineClaims.test.ts` for actor-scoped lease expiry, fencing stale worker, atomic claim/ack and unknown/other-account data invisibility or non-replay.
- [ ] T064 [P] [US8] Write and run RED browser migration tests in `apps/web/e2e/tests/unit-offline-legacy-upgrade.spec.ts` for prior IndexedDB schema with provable and ambiguous items, interrupted upgrade, account change and supported backup/restore; verify full data retained and no guessed target.
- [X] T065 [P] [US8] Write and run RED two-connection replay tests in `apps/api/core/sub_reports/tests/test_sync_concurrent_replay.py` asserting single receipt, one business effect and preserved IDs when identical operations arrive concurrently.

### Implementation

- [X] T066 [US8] Implement local claims with owner, expiry and fencing generation plus recovery of abandoned syncing in `apps/web/src/app/lib/offlineDB.ts` and `apps/web/src/app/lib/syncService.ts`; never rely on lease for server-side idempotency.
- [ ] T067 [US8] Enforce actor/project/unit scope through authentication transitions, queue access and cache display in `apps/web/src/app/lib/auth-storage.ts`, `apps/web/src/app/lib/offlineDB.ts` and `apps/web/src/app/hooks/useAutoSync.ts`; expired/revoked credentials retain but do not send payload.
- [X] T068 [US8] Implement legacy record inventory, provable mapping and quarantine/review in `apps/web/src/app/lib/offlineDB.ts` and `apps/web/src/app/routes/sync-conflicts.tsx`; preserve raw data and require verified ownership; local deletion must identify scope and require confirmation.
- [X] T069 [US8] Supply compatible IndexedDB reader/export/restore and server receipt retention rollback procedure in `apps/web/src/app/lib/offlineDB.ts` and `specs/037-daily-offline-sync/quickstart.md`; never assume version downgrade works or delete journal to roll back.
- [ ] T070 [US8] Run T062–T065 GREEN, including real concurrent connections and same-profile browser restart; record SC-06/G11 and legacy/account evidence in `specs/037-daily-offline-sync/verification/recovery.md`.

## Phase 11: Polish and cross-cutting verification

- [X] T071 Update legacy and v2 consumers, permissions, security refusal, `synced_ids`, stable codes and transition/rollout instructions in `reports_documentation/03-daily-field-reports-and-apis/field_reports_ENDPOINTS.md`, `apps/api/core/field_reports/ENDPOINTS.md` and `apps/api/core/sub_reports/ENDPOINTS.md`.
- [ ] T072 Verify all FA/EN labels, field errors, failure/recovery paths, keyboard focus and accessible names in `apps/web/src/app/locales/fa.json`, `apps/web/src/app/locales/en.json` and `apps/web/e2e/tests/unit-offline-status.spec.ts`; include all six canonical units and active sections in representative configured projects, without treating route/banner as proof.
- [ ] T073 Run migration apply/backfill, historical fixtures, rollback/restore, no-data-loss and `makemigrations --check --dry-run` against an isolated database, plus IndexedDB upgrade and recovery on a persistent browser profile; record exact commands/results in `specs/037-daily-offline-sync/verification/migration.md`.
- [ ] T074 Run final-tree API integration, backend and PostgreSQL race suites with unique test DBs, frontend canonical tests, `pnpm typecheck` and applicable browser suites in `specs/037-daily-offline-sync/quickstart.md`; write counts, commands and failures separately to `specs/037-daily-offline-sync/verification/final-checks.md`.
- [ ] T075 Map each G01–G13 and SC-01–SC-07 to actual RED/GREEN and final-tree browser/backend/race/migration evidence in `specs/037-daily-offline-sync/verification/traceability.md`; mark unexecuted tests/services/live checks explicitly and do not infer completion from old 17 tests, probes or checked tasks.
- [X] T076 Review deploy compatibility, v2 feature gating, server rollback with receipt retention, local export/restore and document non-executed live verification in `specs/037-daily-offline-sync/verification/rollout.md`; do not deploy as part of these tasks.

## Dependencies & Execution Order

Phase 1 → Phase 2. T005–T008 are RED prerequisites for their corresponding T009–T014 implementations; T012–T013 must cover **all** writers before enabling T016/v2. T017 gates the rest. T006 is intentionally deferred to T035 because it exercises the v2 HTTP dispatcher, which does not exist at the foundation checkpoint; keep v2 disabled outside isolated tests. Within each story, run its RED tests before its implementation and verify the same tests GREEN; a story is independently testable with seeded fixtures, not necessarily independently deployable.

- US1 requires Phase 2; US2 depends on US1 persistence and screen integration (T020–T023).
- US3 depends on Phase 2 and US1 identity/creation; browser SC-01 also depends on US2 display/hydration. US4 depends on US3 operation dispatch and foundation guard, and must complete before real rollout.
- US5 depends on US3 operation outcomes and US2 persisted state. US6 depends on foundation shared writers and US3 dispatch; T050–T054 must complete before enabling v2.
- US7 depends on US2 snapshots, US3 receipts and US6 lock/correction contracts. US8 depends on US3 idempotency, US2 persistence and US6 authorization; legacy migration foundation T014 is prerequisite.
- Phase 11 requires all US1–US8, not merely a subset of stories. TDD RED/GREEN evidence is recorded at every checkpoint; final verification follows all changes.

## Parallel execution examples

Only after prerequisites and with separate files/isolated DBs: US1 T018 and T019; US2 T025, T026 and T027; US3 T031–T034; US4 T039–T041; US5 T045 and T046; US6 T050 and T051; US7 T055–T057; US8 T062–T065. Shared-file implementation tasks are sequential; parallel test authoring is not permission to run multiple pytest processes against the same DB. The user must explicitly authorize agent delegation if actual agents are used.

## Implementation Strategy

**First demonstrable slice**: foundation plus US1–US3 for a controlled offline draft, recovery and targeted sync; it is not production-ready until derived protection, concurrency, error handling, conflict and crash/account recovery in US4–US8 also pass. No unsafe legacy or v2 path may be exposed during the slice. Deliver stories incrementally behind the compatibility gate, but complete all P1 stories and the final evidence matrix before claiming the feature complete.
