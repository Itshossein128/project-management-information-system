# Tasks: Daily Report Validation Codes and Unset Semantics

**Input**: Design artifacts in `specs/036-validation-codes-unset-semantics/`.
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [workflow API contract](contracts/workflow-api.md), [quantity UI contract](contracts/quantity-ui.md), [quickstart.md](quickstart.md), and `.specify/memory/constitution.md`.
**Feature identifier**: `036-validation-codes-unset-semantics`; planning checkout was `develop`. Verify the current checkout rather than assuming a feature branch exists.
**Tests**: Required by FR-015 and constitution quality gates. Add uncovered regression assertions before production changes, capture real red failures, implement minimally, then rerun green. Retain already-green coverage without manufacturing failures or weakening assertions. These unchecked tasks describe future implementation; this file is not test evidence.
**Organization**: Two P1 stories, then one P2 story, each independently testable. No new dependency, schema, permission, workflow engine, or report-authoring route.

## Format and Path Conventions

Every task uses `- [ ] Tnnn [P?] [USn?] Description with file path`. `[P]` means a task can be assigned alongside another ready task that edits different files; its prerequisites must already be complete. Story labels occur only in story phases. Paths are repository-relative; resolve them from `/home/hossein/Desktop/projects/building-management` for filesystem operations. `verification.md` below is a new feature evidence log, not a completed validation claim.

## Phase 1: Setup

**Purpose**: Confirm the active feature and establish a safe, reproducible validation environment without installing or upgrading unrelated dependencies.

- [X] T001 Confirm `.specify/feature.json` resolves to this feature, inspect branch and dirty work, read the linked artifacts and root AGENTS.md, and create `specs/036-validation-codes-unset-semantics/verification.md` with baseline commit/checkout, preserved pre-existing changes, acceptance evidence categories and pending status.
- [X] T002 Verify PostgreSQL/Redis reachability, API venv, pinned Django 4.2.11, pnpm and Chromium prerequisites using `specs/036-validation-codes-unset-semantics/quickstart.md`; record available services and sanitized commands in `specs/036-validation-codes-unset-semantics/verification.md`, use a unique TEST_DATABASE_NAME with one pytest process, and set synchronous audit/eager tasks only in the validation environment without logging secrets or resetting the development database.

## Phase 2: Foundational Prerequisites

**Purpose**: Establish shared fixtures and preservation boundaries. Complete this phase before starting story tasks.

- [X] T003 Inspect and, only where necessary, adapt the existing report setup used by `apps/web/e2e/tests/daily-report.spec.ts` to obtain disposable reports through canonical specialty-unit/by-date flows compatible with automatic summaries; keep reusable setup local or in `apps/web/e2e/helpers/daily-report.ts` if a helper is needed, retain production direct-create restrictions, and verify the fixture reaches both existing summary and read-only grid surfaces without changing application authorization.
- [X] T004 Record the preservation contract in `specs/036-validation-codes-unset-semantics/verification.md` by tracing `apps/api/core/field_reports/models.py`, `apps/api/core/field_reports/serializers.py`, `apps/api/core/field_reports/daily_report_views.py` and `apps/web/src/app/lib/api/daily-reports.ts`: retain “quantity (nullable decimal, max_digits=18, decimal_places=4)”, “quantity_measured (boolean, default true)”, “Status values: draft, submitted, under_review, approved, rejected”, and GeneralActivityRow “quantity (decimal string or null)” with “No quantity_measured field exists here”; confirm existing authenticated project resolution, edit_reports/approve_reports/view_reports boundaries and no migration requirement.

**Checkpoint**: Safe service/test configuration, usable canonical browser fixture and explicit data/permission preservation boundaries are ready. No new schema or global infrastructure is required.

## Phase 3: User Story 1 — Submit Only Complete Measured Quantities (P1, MVP)

**Goal**: Refuse any live measured-but-unset activity while accepting and retaining explicit zero.

**Independent Test**: Submit otherwise-valid draft and rejected reports with measured null, zero forms and positive quantities. Only the null completeness case fails with quantity_unset_invalid; a later invalid row also blocks the report, and refusal leaves lifecycle fields and stored quantities unchanged.

### Tests First

- [X] T005 [P] [US1] Extend `apps/api/core/field_reports/tests/test_approval_workflow.py` with API contract cases for draft/rejected source states, measured null among several zero/positive rows, multiple null rows, deleted invalid-row exclusion, and explicit Decimal zero forms 0/0.0/0.00; assert HTTP status, stable quantity_unset_invalid, exact FA/EN messages from `specs/036-validation-codes-unset-semantics/contracts/workflow-api.md`, database-refreshed zero/null/flags and unchanged lifecycle fields on failure.
- [X] T006 [P] [US1] Add a real API-backed submit acceptance scenario in `apps/web/e2e/tests/daily-report.spec.ts` using the Phase 2 fixture: demonstrate measured-null refusal and numeric-zero success through an authorized workflow, inspect returned code and persisted state after reload, and preserve any separate mocked rendering fixtures as explicitly labeled UI-only evidence.

### Implementation and Verification

- [X] T007 [US1] Run T005/T006 against the existing implementation and record actual missing-behavior failures versus retained passing cases in `specs/036-validation-codes-unset-semantics/verification.md`; do not require already-implemented correct behavior to fail or count infrastructure errors as RED behavior evidence.
- [X] T008 [US1] Reconcile only demonstrated quantity-validation gaps in `apps/api/core/field_reports/daily_report_views.py` and, if required, `apps/api/core/field_reports/serializers.py`: preserve “Submission reads non-deleted rows only”, measured=true plus null refusal, explicit numeric zero acceptance, nullable decimal precision, blank-input normalization and existing false-plus-numeric submission policy; use `is None` rather than truthiness and leave already-correct code unchanged.
- [X] T009 [US1] Add or tighten submit permission and foreign-project no-mutation regressions in `apps/api/core/field_reports/tests/test_approval_workflow.py`; prove a caller lacking edit_reports cannot submit and existing project scoping prevents access/mutation, preserving current denial statuses without weakening permission fixtures or exposing workflow details first.
- [X] T010 [US1] Run the focused pytest and US1 browser/API scenarios from `specs/036-validation-codes-unset-semantics/quickstart.md` on the final US1 tree and append command results, test database name and state-persistence evidence to `specs/036-validation-codes-unset-semantics/verification.md`; treat service failures or missing real API proof as incomplete validation.

**Checkpoint**: US1 is independently demonstrable without the later client error mapper or badge styling. The existing server-localized quantity message remains usable for the MVP.

## Phase 4: User Story 2 — Receive Stable Workflow Validation Feedback (P1)

**Goal**: Return exact localized invalid-state and rejection messages with stable codes, and show all four known codes consistently in daily-report form/view feedback.

**Independent Test**: Attempt submit from submitted/under_review/approved; reject from submitted and under_review using missing/null/empty/whitespace, short trimmed and valid trimmed reasons. Verify exact message/code and unchanged state on refusal; exactly 10 characters succeeds. Both client surfaces translate known codes after locale changes and retain unknown-code fallback.

### Tests First

- [X] T011 [P] [US2] Extend `apps/api/core/field_reports/tests/test_approval_workflow.py` for every non-submittable status, both valid reject source states, missing/null/empty/spaces/tabs/newlines, 1–9 trimmed characters and exactly 10/longer reasons; quote and enforce “Apply leading/trailing whitespace trim before length: 1–9 characters → rejection_reason_min_length_10; at least 10 characters → eligible under existing workflow” and “Internal whitespace counts normally, matching existing Python string length semantics”; assert exact FA/EN error.message, unchanged error.code, retained details.reason leaf, trimmed persistence and no mutation on invalid/unauthorized/foreign-project reject.
- [X] T012 [P] [US2] Add browser feedback contract cases in `apps/web/e2e/tests/daily-report.spec.ts` for report_not_in_submittable_state, rejection_reason_required, rejection_reason_min_length_10 and quantity_unset_invalid through both DailyReportForm and daily-report-view callbacks; assert exact FA/EN text, locale switching and existing fallback for an unknown API code and a non-API error, and capture pre-change failures separately from real API tests.

### Implementation and Verification

- [X] T013 [P] [US2] Fix the two reason-validation branches of `_reject` in `apps/api/core/field_reports/daily_report_views.py` to provide identical localized ErrorDetail values under both detail and reason, retaining “error.code (stable string), error.message (localized flattened string), error.details (original field/detail tree)”; reuse `apps/api/core/field_reports/services/lifecycle_errors.py`, preserve reason request key and trimmed length rules, and leave `apps/api/core/config/exceptions.py` unchanged so the targeted API messages lose the reason prefix while field errors survive.
- [X] T014 [P] [US2] Add `dailyReports.validationErrors.<code>` entries for all four scoped identifiers in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json` using the exact contract strings, leaving shared errors namespace entries unchanged so specialty-unit feedback is unaffected.
- [X] T015 [US2] Add the narrowly scoped four-code resolver `apps/web/src/components/daily_reports/workflow-error-message.ts` using ApiRequestError.code and the current translator; select `dailyReports.validationErrors.<code>` only for the four known identifiers and preserve existing server-message/generic fallback for unknown codes and non-API errors without altering the global API client or matching translated strings.
- [X] T016 [P] [US2] Wire submit/reject error handling in `apps/web/src/components/daily_reports/DailyReportForm.tsx` to the T015 resolver with the current translator, preserving existing successful transitions, callbacks, notifications and unrelated error handling.
- [X] T017 [P] [US2] Wire submit/reject error handling in `apps/web/src/app/routes/daily-report-view.tsx` to the T015 resolver and inspect `apps/web/src/components/daily_reports/ApprovalStatusBar.tsx` reason guards for consistency with the trimmed >=10 backend boundary, changing only demonstrated mismatches and preserving existing approve/correction actions.
- [X] T018 [US2] Run T011/T012 after integration, ensure valid reasons are stored trimmed and exactly-10 reasons succeed, and record RED-to-GREEN or retained-green results plus exact API message/envelope and permission persistence evidence in `specs/036-validation-codes-unset-semantics/verification.md`.
- [X] T019 [US2] Run combined US1/US2 backend and browser cases using `specs/036-validation-codes-unset-semantics/quickstart.md`; confirm locale changes alter text only, all four identifiers remain stable and unknown-code fallback still works, recording results in `specs/036-validation-codes-unset-semantics/verification.md` without equating mocked feedback tests to actual authorization evidence.

**Checkpoint**: Exact rejection error.message is corrected locally; all four daily-report codes have bilingual feedback on both client entry points. US1 quantity and permission guarantees remain intact.

## Phase 5: User Story 3 — Distinguish Unset from Zero at a Glance (P2)

**Goal**: Present unset quantity with exact localized text and a compact neutral badge with a visible caution outline in every scoped read-only activity quantity cell.

**Independent Test**: Inspect summary activity rows, general activities and the read-only grid in FA/EN with measured null, not-measured null, legacy not-measured numeric, measured zero and positive values. Unset rows show the exact label; zero/positive rows remain numeric without a badge. General activities use nullability only. Inspect both themes and keyboard editing regression.

### Tests First

- [X] T020 [US3] Extend the canonical quantity presentation case and add missing scoped cases in `apps/web/e2e/tests/daily-report.spec.ts`: exact FA ثبت‌نشده and EN Unset assertions instead of the broad Not recorded regex; measured/null, false/null, false/numeric legacy zero and positive, measured numeric/string zero and positive, general-activity null/zero, locale switch and unchanged keyboard input; target quantity cells specifically and record failures before changing UI, using read-response fixtures only for legacy states normalized by supported writes.

### Implementation and Verification

- [X] T021 [P] [US3] Change only `dailyReports.unsetQuantity` in `apps/web/src/app/locales/en.json` to exact `Unset` and retain exact `ثبت‌نشده` in `apps/web/src/app/locales/fa.json`, preserving the US2 validation translations and all unrelated labels.
- [X] T022 [P] [US3] Update `apps/web/src/components/daily_reports/UnsetQuantityBadge.tsx` with an explicit caution-colored border/ring using existing light/dark warning tokens over a muted neutral background and compact text; retain “null/undefined quantity OR quantityMeasured === false means unset”, including false-plus-numeric precedence and numeric zero output, the existing test hook and text meaning, without globally changing `apps/web/src/components/ui/badge.tsx`.
- [X] T023 [US3] Replace the general-activity quantity dash fallback in `apps/web/src/components/daily_reports/summary/DailyReportSummaryView.tsx` with the shared badge, retaining the existing report.activities badge path; enforce “quantity (decimal string or null)” and “No quantity_measured field exists here” for general activities by supplying undefined measured state, and preserve numeric zero, provenance, ordering and unrelated numeric columns.
- [X] T024 [US3] Verify the read-only activity quantity branch in `apps/web/src/components/daily_reports/EditableGrid.tsx` reached through `apps/web/src/components/daily_reports/ActivityTab.tsx` uses the shared predicate/badge for null and false, including legacy numeric rows; fix only demonstrated gaps and preserve existing editable numeric inputs, data-testid hooks and numeric zero without data coercion or stored-value writes.
- [X] T025 [US3] Run the expanded quantity browser cases in `apps/web/e2e/tests/daily-report.spec.ts` across FA/EN and light/dark, desktop/narrow views; assert computed visible caution outline and neutral background, readable exact labels, per-cell zero/positive output and keyboard editing, keeping any read-response fixture evidence separate from live workflow runs.
- [X] T026 [US3] Record screenshots and a first-inspection review of unset versus zero versus positive values on all scoped surfaces in `specs/036-validation-codes-unset-semantics/verification.md`, including theme/locale/viewport, actual observer/review method for SC-005, unchanged legacy values and any unverified usability boundary; do not infer human usability success from a predicate test alone.

**Checkpoint**: Both activity summary tables and read-only grid distinguish unset from explicit zero, with bilingual accessible caution treatment and no storage/calculation changes.

## Phase 6: Polish and Cross-Cutting Validation

**Purpose**: Validate the final combined implementation and document only collected evidence.

- [X] T027 Run focused `apps/api/core/field_reports/tests/test_approval_workflow.py` plus relevant existing activity serializer/read/permission regressions selected from `apps/api/core/field_reports/tests/` against one isolated test database, run `pnpm typecheck`, and record exact commands/results on the final tree in `specs/036-validation-codes-unset-semantics/verification.md`, distinguishing observed failures from historical AGENTS.md notes.
- [X] T028 Execute the full scoped acceptance flow from `specs/036-validation-codes-unset-semantics/quickstart.md` using `apps/web/e2e/playwright.config.ts` and `apps/web/e2e/tests/daily-report.spec.ts`, including real zero-submit/valid-reject persistence and permission-denial proof plus bilingual browser feedback/display checks; record mock/live boundaries, service limitations, traces and results in `specs/036-validation-codes-unset-semantics/verification.md`, rerunning only checks invalidated by subsequent fixes.
- [X] T029 Review the final diff against `specs/036-validation-codes-unset-semantics/data-model.md` and `specs/036-validation-codes-unset-semantics/contracts/quantity-ui.md`, tracing serialization, sync, aggregation, imports/exports and PDF dependencies to confirm no stored field/quantity/calculation/provenance or permission changes; record the no-migration conclusion and out-of-scope proof boundaries in `specs/036-validation-codes-unset-semantics/verification.md`, revisiting the plan if a schema change is actually necessary.
- [X] T030 Update `specs/036-validation-codes-unset-semantics/quickstart.md` only for verified command/setup corrections and finalize `specs/036-validation-codes-unset-semantics/verification.md` with FR-001–FR-016 and SC-001–SC-005 coverage, evidence links, unresolved limitations and acceptance decision; check off tasks in `specs/036-validation-codes-unset-semantics/tasks.md` only when their work and required evidence are complete, without claiming deployment or services not exercised.

## Dependencies and Execution Order

### Phase Dependency Graph

```text
Phase 1: T001 → T002
       ↓
Phase 2: T003 → T004
       ↓
US1 (P1): {T005 || T006} → T007 → T008 → T009 → T010
       ↓ delivery order / shared-file ownership
US2 (P1): {T011 || T012} → {T013 || T014} → T015
          → {T016 || T017} → T018 → T019
       ↓ delivery order / shared locale and browser suite ownership
US3 (P2): T020 → {T021 || T022} → T023 → T024 → T025 → T026
       ↓
Polish: T027 → T028 → T029 → T030
```

- All stories depend on Phase 2. No new US1 runtime module is required by US2 or US3; their acceptance tests can run independently using shared setup.
- Default execution is US1 → US2 → US3 because priorities and shared-file ownership make this the safest delivery order. This is a scheduling dependency, not a new product coupling.
- US1/US2 edit the same backend approval test module and workflow view; US1/US2/US3 edit the same browser suite; US2/US3 edit the same locale files. Serialize those edits. Do not launch whole story phases concurrently against this checkout.
- The conservative US2 graph waits for both backend fix and translations before helper integration; the helper itself consumes translations, while final verification also needs the backend fix.
- Database test execution is serial on one unique TEST_DATABASE_NAME. Parallel editing opportunities do not authorize concurrent processes sharing a test database.

### Parallel Examples Per Story

US1, after T004: author T005 API tests in `apps/api/core/field_reports/tests/test_approval_workflow.py` alongside T006 browser/API scenario in `apps/web/e2e/tests/daily-report.spec.ts`. Complete both before baseline evaluation or production changes.

US2, after the US1 edit handoff: author T011 backend cases alongside T012 browser feedback cases. Once failing contracts are captured, T013 local backend error fix can proceed alongside T014 locale entries. After T015, T016 form wiring and T017 route/guard wiring touch separate files and can proceed together.

US3, after T020 captures missing behavior: T021 locale-label corrections and T022 component styling use separate files. Wait for the badge contract before summary integration and final UI evidence.

These examples identify scheduling opportunities only; no subagents are dispatched by tasks generation. If implementation delegates work, retain the user's economic-model preference and explicit file ownership.

## Implementation Strategy

### MVP First

Complete Phases 1–3 (T001–T010), then independently demonstrate US1: measured null blocks, explicit zero passes and persists, invalid or unauthorized actions leave records untouched. This MVP does not claim completion of the remaining error-feedback or presentation stories.

### Incremental Delivery

1. Preserve existing correct code and collect baseline proof before extending it.
2. Deliver US1 quantity completeness with API/persistence/permission evidence.
3. Deliver US2 exact API messages and four-code client localization, keeping US1 regressions green.
4. Deliver US3 scoped quantity badges and exact bilingual/visual proof, keeping successful workflows unchanged.
5. Validate the final tree across stories and record limitations before declaring feature acceptance. No deployment is part of this task list.

### Coverage and Acceptance Trace

- US1 T005–T010: FR-006–008, FR-015–016; SC-002 and quantity portions of SC-004.
- US2 T011–T019: FR-001–005, FR-013–016 and quantity-code feedback integration; SC-001 and error portions of SC-004.
- US3 T020–T026: FR-008–013, FR-015; SC-003, display portion of SC-004 and SC-005 review evidence.
- Shared setup T001–T004 and final T027–T030 enforce constitution, isolation, final-tree checks and honest proof boundaries across all requirements.

## Task Summary and Notes

30 tasks: Setup 2; Foundational 2; US1 6; US2 9; US3 7; Polish 4. Ten tasks carry [P], arranged in five safe pairs; a [P] marker never overrides dependencies or same-file ownership.

Do not remove assertions, skip required cases, coerce nulls to zero, rewrite legacy history on read, broaden who can mutate reports, alter corrections/locking/calculations or restyle global neutral badges. Existing passing tests remain evidence, not a reason to invent duplicate infrastructure. Execution records belong in verification.md; unchecked tasks remain work to do.
