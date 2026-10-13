# Tasks: Independent DEMATEL Criterion Influence Analysis

**Input**: Design documents from `specs/022-decision-dematel/`
**Date**: 2026-10-11 | **Feature**: `022-decision-dematel` | **Git branch**: `develop`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [API/input contract](contracts/dematel-inputs-api.md), [calculation/result contract](contracts/dematel-result.md), [UI contract](contracts/dematel-ui.md), [quickstart.md](quickstart.md), and the project constitution.
**Tests**: Required. User explicitly requested **Use TDD**.
**Organization**: Story phases match the specification priorities: US1/US2 P1, US3/US4 P2. All tasks start unchecked; this file does not assert implementation or acceptance evidence.

## Format and Path Conventions

Task format is `- [ ] TNNN [P?] [USn?] Description with exact file paths`. Paths are relative to the monorepo root. New files are created by their tasks; existing files retain unrelated changes. No new model, migration, permission, endpoint or dependency is planned.

`[P]` identifies independent files within a ready task batch, not permission to ignore prerequisites. Backend database jobs sharing one test database must run serially unless isolated databases are explicitly configured. Story implementations share route, validators and browser files, so story-wide parallel execution is not proposed.

## TDD Execution Rule

For each behavior slice: write the regression first, run the focused command against the existing behavior, retain its real failure and exit, implement the smallest fix, then rerun that same regression green. Tests in a story's test subsection precede its implementation tasks; explicit task dependencies below refine that order. Refactor only with the focused suite green. Retain meaningful numerical, API and real-browser evidence, not checkbox or source assertions alone.

An added test can reveal already-correct behavior. Record that initial green as existing coverage and avoid needless code changes; never weaken a passing behavior to manufacture red. Setup, documentation and final verification tasks do not require artificial failing application tests. Capture missing-feature failures without hiding unrelated environment/fixture failures. Expected numerical results must come from independent rational/Decimal reasoning, never the production NumPy calculation.

Test commands, environment prerequisites and proof boundaries are in quickstart.md. New test modules become runnable once their RED tasks create them. Temporary logs/traces may live outside Git; record their paths and commands in the eventual validation.md. No baseline tests or feature implementation run as part of generating this task list.

## Phase 1: Setup (Shared Infrastructure)

**Purpose/Goal**: Confirm the active DEMATEL feature and preserve the current AHP work before implementation.

- [ ] T001 Inspect `.specify/feature.json`, `specs/022-decision-dematel/plan.md`, `specs/022-decision-dematel/checklists/requirements.md` and existing dirty changes; record current file hashes, actual branch/runtime versions, PostgreSQL/Redis availability and baseline limitations in `specs/022-decision-dematel/validation.md` without changing reviewer checklists, source requirements or AHP artifacts.

- [ ] T002 Initialize red/green/final evidence sections in `specs/022-decision-dematel/validation.md` and run the existing focused backend/helper/AHP-browser baselines named in `specs/022-decision-dematel/quickstart.md`; record commands, exits and log paths. Reuse environments and dependencies; do not reset databases, disable throttling or install full API dev requirements.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose/Goal**: Establish strict executable inputs and recoverable finite draft storage shared by every story.

**Independent Test**: Direct validation rejects invalid shape/numbers with exact issue paths; incomplete drafts persist without rewriting unrelated method data.

- [ ] T003 RED: add strict DEMATEL validator regressions in `apps/api/core/decision_support/tests/test_dematel_service.py` for the data-model constraint “Execution requires exact n×n numeric matrix, 1≤n≤10, values 0–4, zero diagonal. Native JSON numbers only; booleans are invalid.” Cover empty/duplicate names, n=0/11, scalar/ragged rows, blanks, strings, bools, nonfinite/overflow values, out-of-range and nonzero diagonal; capture failing exits.

- [ ] T004 GREEN after T003: implement `validate_dematel_inputs` in `apps/api/core/decision_support/services/validators.py` using existing trimmed-name rules, exact shape prechecks with root/row issues, strict native numeric cells, inclusive decimals 0–4 and exact zero diagonal; keep opposite-direction values independent and rerun the validator tests.

- [ ] T005 RED: add draft/storage/isolation regressions in `apps/api/core/decision_support/tests/test_dematel_api.py` for “Draft cells may be null or finite values requiring later correction. Numeric nonfinite/overflow values must never reach PostgreSQL JSON.” Cover create, matrix-only PATCH, partial/null drafts, finite invalid drafts, malformed persisted containers, and unchanged persisted unrelated ranking/AHP/ISM inputs.

- [ ] T006 GREEN after T005: extend finite draft guarding in `apps/api/core/decision_support/services/validators.py` and DEMATEL-only requested-field updates/recovery in `apps/api/core/decision_support/services/case_service.py`; implement “DEMATEL-only updates write only requested fields and audit fields; unrelated ranking/AHP/ISM inputs retain original values.” Preserve recoverable blanks/invalid finite values and rerun PostgreSQL regressions.

**Checkpoint**: Foundation blocks all story implementation until strict execution validation and finite draft/isolation regressions are green.

---

## Phase 3: User Story 1 - Run an Independent Influence Analysis (Priority: P1) — MVP

**Purpose/Goal**: Deliver a safe independent DEMATEL execution and directed matrix entry on the existing case workspace.

**Independent Test**: A criteria-only A/B/C case with [[0,4,0],[0,0,2],[0,0,0]] yields D=[1.5,0.5,0], R=[0,1,1], prominence=[1.5,1.5,1], relation=[1.5,-0.5,-1]; no alternatives or other method execution is required.

### Tests first — capture RED or existing coverage

- [ ] T007 [P] [US1] RED: extend `apps/api/core/decision_support/tests/test_dematel_service.py` with independently derived rational/Decimal expectations for the chain, decimals, isolated criterion, uniformly tiny nonzero scale, n=10, symmetric nonregular balanced network and near-condition boundary; include all-zero/singular/unreliable/nonfinite guards, signed neutral-boundary roles, accuracy within 1e-6×max(1,|expected|), and no input mutation.

- [ ] T008 [P] [US1] RED: extend `apps/api/core/decision_support/tests/test_dematel_api.py` with DEMATEL-only POST201, selected-method enforcement, frozen criteria/matrix/results/policy/actor/time and unchanged ranking inputs; assert the exact `status: ok`, `engine: dematel`, `normalization_factor`, matrices, `criteria_results` and `numerical_policy` contract instead of the current stub.

- [ ] T009 [P] [US1] RED: add directed default/edit/remap tests in `apps/web/src/components/decision-support/dematel-input-rules.test.ts`: “Rename: retain all pairs by index, update both axis labels.” “Move: apply the same index permutation to rows and columns.” “Add: keep surviving pairs, new diagonal zero, new off-diagonal pairs null.” “Remove: drop that row and column, retain surviving pairs.” Include asymmetric values, explicit zero, decimals, nulls and no mutation.

- [ ] T010 [P] [US1] RED: create real EN/FA primary-flow scenarios in `apps/web/e2e/tests/decision-dematel.spec.ts` for DEMATEL-only entry/execution and the exact chain result, independent A→B/B→A values, fixed zero diagonal, criteria-only save/reload and unchanged existing ranking data; capture actual missing-feature failures using the running API rather than mocked successful calculation.

### Implementation and GREEN verification

- [ ] T011 [US1] GREEN after T007: add `apps/api/core/decision_support/services/dematel_service.py` with accurate maximum-row sum, exact s=0 rejection, float64 right solve `solve((I-N).T,N.T).T`, cond2≤1e8, normalized residual≤1e-10, finite-output and negative-T roundoff guards; derive D/R/prominence/signed relation and server roles with absolute 1e-9 neutrality exactly per `specs/022-decision-dematel/contracts/dematel-result.md`, then rerun numerical tests.

- [ ] T012 [US1] GREEN after T008 and T011: add DEMATEL-only early dispatch in `apps/api/core/decision_support/services/execution_service.py` before stale selection checks; atomically reload/row-lock the project-scoped active case, recheck selection, compute and deep-snapshot one authoritative state, append the complete finite result only after all guards. Preserve other engines and ISM stub behavior; rerun run-contract tests.

- [ ] T013 [US1] After T012, reproduce the expected old-stub fixture failure in `apps/api/core/decision_support/tests/test_ahp_api.py`; give its mixed-history DEMATEL entry valid judgments or use remaining ISM stub, retaining existing count/filter/pagination/project-scoping assertions, and record the minimal fixture change and green rerun.

- [ ] T014 [US1] GREEN after T009: add `apps/web/src/components/decision-support/dematel-input-rules.ts` defaults/directed edit/index-remap helpers and optional operation/index metadata in `apps/web/src/components/decision-support/NamedListEditor.tsx`; retain numeric zero, null unjudged pairs and surviving directed identities without changing AHP name-based rename-clearing behavior; rerun new helpers and existing AHP matrix tests.

- [ ] T015 [US1] GREEN after T014 and T010: extend `apps/web/src/components/decision-support/SquareMatrixEditor.tsx` with explicit DEMATEL mode, fixed zero diagonal, independent 0–4 decimal cells, localized directed-axis labels, `dematel_matrix.j.k` issue targets and no AHP scale/advisory/reciprocal presets; preserve pairwise mode and existing tests.

- [ ] T016 [US1] GREEN after T012 and T010: extend `apps/web/src/app/lib/api/decision-support.ts` with result types and a structural finite-result guard; add `apps/web/src/components/decision-support/DematelResultTable.tsx` rendering snapshot-order rows and server roles (“All numeric outputs are finite native JSON numbers.”). Display D/R/prominence/relation and the judgment-based causation caveat without client calculation, ranks or weights.

- [ ] T017 [US1] GREEN after T015 and T016: add `apps/web/src/components/decision-support/DematelMethodPanel.tsx` and wire DEMATEL draft hydration/reset/save plus operation remapping in `apps/web/src/app/routes/project-decision-support.tsx`; save ordered criteria with their aligned matrix, run only after save succeeds, render returned frozen labels, retain per-case state and no ranking prerequisites. Establish typed coordinator/disabled callback boundaries for the later shared adapters.

- [ ] T018 [US1] Run the focused service/API/helper tests and EN/FA primary-flow cases after T017; record red→green commands/exits/results in `specs/022-decision-dematel/validation.md` and verify the exact independent-test fixture. Do not mark this story complete from source or helper checks alone; full failure/history/access acceptance remains assigned to later stories.

**Checkpoint**: Story complete only when its independent test and scoped evidence pass.

---

## Phase 4: User Story 2 - Correct Inputs Without Misleading Results (Priority: P1)

**Purpose/Goal**: Expose actionable validation, numerical and request failures while preserving correctable drafts and producing no false successful runs.

**Independent Test**: Submit missing/out-of-range/malformed/all-zero/singular matrices, observe named-cell or matrix-level feedback and zero new successful records, then correct and execute successfully.

### Tests first — capture RED or existing coverage

- [ ] T019 [P] [US2] RED: extend `apps/api/core/decision_support/tests/test_dematel_api.py` for EN/FA coded issue envelopes and root/row/cell paths on invalid inputs, all-zero n=1/n=3, singular loop, rejected reliability boundary and arithmetic failure; every invalid attempt must append zero records while valid sparse/zero-row references still succeed.

- [ ] T020 [P] [US2] RED: extend `apps/web/src/components/decision-support/ValidationIssueList.test.ts` to cover the existing request/error helpers without changing production code for DEMATEL path parsing, criterion-name cell labels and generic 403/404/429/non-JSON/network fallbacks; test meaningful expected outputs before editing production error presentation.

- [ ] T021 [US2] RED: extend `apps/web/e2e/tests/decision-dematel.spec.ts` with missing-cell focus, scale/diagonal/shape feedback, all-zero/singular rejection, failed save preventing POST, run/save403/404/429/non-JSON/network failures, preserved edits, no stale current result, recovery retry and partial/malformed draft reopen behavior. Keep the existing US1 browser scenarios intact.

### Implementation and GREEN verification

- [ ] T022 [US2] GREEN after T019: correct only missing localized code/path/arithmetic behavior in `apps/api/core/decision_support/services/validators.py`, `apps/api/core/decision_support/services/dematel_service.py` and `apps/api/core/decision_support/services/execution_service.py`; add DEMATEL gettext entries to `apps/api/core/locale/fa/LC_MESSAGES/django.po`, compile `django.mo` and rerun the EN/FA API guard tests without weakening numerical policy.

- [ ] T023 [US2] GREEN after T020 and T021: extend `apps/web/src/components/decision-support/ValidationIssueList.tsx` and `apps/web/src/components/decision-support/validation-issues.ts` to use DEMATEL cell paths, name both influencing/receiving criteria and focus the correct editable cell; reuse precise server issues and generic request fallback instead of exposing raw exception strings.

- [ ] T024 [US2] GREEN after T021: update `apps/web/src/components/decision-support/DematelMethodPanel.tsx` and `apps/web/src/app/routes/project-decision-support.tsx` failure states to preserve recoverable entries, clear current-result association on input edits/start/error, prevent run after failed save and show visible localized feedback. Historical successful runs remain available as history rather than the failed request outcome.

- [ ] T025 [US2] GREEN after T021: complete safe legacy/incomplete draft hydration in `apps/web/src/app/routes/project-decision-support.tsx` and `apps/web/src/components/decision-support/dematel-input-rules.ts`, plus any remaining recovery in `apps/api/core/decision_support/services/case_service.py`; do not crash on scalar/ragged drafts, silently zero missing judgments, or overwrite surviving pairs while allowing correction and save/reload.

- [ ] T026 [US2] GREEN after T022 and T023: add DEMATEL validation/numerical/request explanations in `apps/web/src/app/locales/en.json` and `apps/web/src/app/locales/fa.json`; preserve stable codes and explicitly explain why all-zero/singular inputs have no result; rerun targeted failure-feedback browser cases.

- [ ] T027 [US2] Run the US2 API/helper/EN/FA failure-and-retry cases and the US1 numerical/primary-flow regression; record actual evidence and zero-record assertions in `specs/022-decision-dematel/validation.md`. Include exact one-criterion [[0]] rejection and successful isolated-criterion results in a larger valid matrix.

**Checkpoint**: Story complete only when its independent test and scoped evidence pass.

---

## Phase 5: User Story 3 - Review a Frozen Analysis Later (Priority: P2)

**Purpose/Goal**: Make every historical DEMATEL result attributable, immutable and independent of later case edits.

**Independent Test**: Run, rename/reorder/change influences, run again and reopen both records: IDs differ and the prior input/result/actor/time stay fixed; old stubs display unavailable.

### Tests first — capture RED or existing coverage

- [ ] T028 [P] [US3] RED-first: extend `apps/api/core/decision_support/tests/test_runs_immutability.py` with DEMATEL before/after persisted snapshot/result/actor/time comparisons following rename/reorder/edit/rerun; cover result policy and ordered names, distinct IDs, forbidden update/delete and unchanged unrelated method results. Record already-green existing immutability behavior honestly.

- [ ] T029 [P] [US3] RED-first: extend `apps/api/core/decision_support/tests/test_dematel_api.py` with stale-instance/latest-input, authoritative deselection, soft-deleted case and controlled PostgreSQL concurrent edit tests; use separate connections/barriers to prove computation and snapshot cannot mix case versions, without sleep-based timing assumptions or creating successful failed runs.

- [ ] T030 [P] [US3] RED: extend `apps/web/e2e/tests/decision-dematel.spec.ts` for frozen DEMATEL matrix/indicators/policy/actor/time after live rename/reorder/edit and a second run, method filtering/pagination, unavailable legacy stub/invalid result payloads, and separate selected historical output versus current result.

### Implementation and GREEN verification

- [ ] T031 [US3] GREEN after T028 and T029: fix only demonstrated gaps in `apps/api/core/decision_support/services/execution_service.py` deep-copy/authoritative lock/snapshot/append behavior; preserve “Existing DEMATEL `status: stub` records are preserved and shown as unavailable output, not upgraded or interpreted as successful computations.” Rerun controlled concurrency and immutability checks; skip edits when regressions already pass.

- [ ] T032 [US3] GREEN after T030: extend `apps/web/src/components/decision-support/InputSnapshotViewer.tsx` to render frozen ordered criteria, directed matrix, normalization/total-relations/policy and `apps/web/src/components/decision-support/DematelResultTable.tsx`; historical labels must come exclusively from `run.input_snapshot`, with safe unavailable display for old stubs or malformed/nonfinite results.

- [ ] T033 [US3] GREEN after T030: finish snapshot-aware current/history selection and type-guard behavior in `apps/web/src/app/routes/project-decision-support.tsx` and `apps/web/src/app/lib/api/decision-support.ts`; reuse `apps/web/src/components/decision-support/ExecutionHistoryList.tsx` filtering and localized dates, retain immutable extracted time and avoid relabeling frozen results from live criteria.

- [ ] T034 [US3] Run DEMATEL immutability/concurrency/history cases and existing mixed-method history regressions; record concrete old/new run IDs, persisted comparisons, scoped pagination and browser evidence in `specs/022-decision-dematel/validation.md`, not screenshots alone.

**Checkpoint**: Story complete only when its independent test and scoped evidence pass.

---

## Phase 6: User Story 4 - Understand and Use the Analysis in Either Language (Priority: P2)

**Purpose/Goal**: Complete Persian/English keyboard usability, shared permission controls and safe same-case request coordination.

**Independent Test**: In EN and FA perform entry/correction/run/history review with stable focus and pair identities, then verify view-only mixed-method controls, denied mutation/execution and delayed other-method/global-save isolation.

### Tests first — capture RED or existing coverage

- [ ] T035 [P] [US4] RED-first: extend `apps/api/core/decision_support/tests/test_dematel_api.py` for authentication/membership/view/edit permissions, view-only reads and mutation/run denial, foreign project/case/run IDs and zero unauthorized records; preserve existing global-admin policy and `view_decision_support`/`edit_decision_support` codenames rather than inventing run permission.

- [ ] T036 [P] [US4] RED: extend `apps/web/src/components/decision-support/i18n.keys.test.ts` with DEMATEL components, scale/direction/zero-diagonal explanation, D/R/prominence/relation, dynamic role/error keys and causation caveat in both dictionaries; detect missing strings rather than accepting untranslated key fallbacks.

- [ ] T037 [US4] RED-first: extend `apps/web/e2e/tests/decision-dematel.spec.ts` with real multi-character typing/caret, cell navigation and rename/move/add/remove directed-pair preservation in EN/FA; include supported localized numeric input, explicit zero/null distinction, and surviving AHP reciprocal/rename semantics on a mixed case.

- [ ] T038 [US4] RED: extend `apps/web/e2e/tests/decision-dematel.spec.ts` with delayed other-method PATCH→POST followed by attempted DEMATEL/global save, double clicks, edits during pending, case switch/unmount and late response isolation; test no writable controls for view-only mixed-method cases and no stale current DEMATEL result after a changed or failed draft.

- [ ] T039 [US4] RED-first: extend `apps/web/e2e/tests/decision-dematel.spec.ts` for active-language labels/roles/errors and history dates while browser locale differs from app locale, then switch EN↔FA and assert frozen actor/time/numeric values and directed row/column associations remain unchanged.

### Implementation and GREEN verification

- [ ] T040 [US4] GREEN after T038: use existing `usePermission(projectId)` in `apps/web/src/app/routes/project-decision-support.tsx` and pass view-only/edit/pending gates into `apps/web/src/components/decision-support/DematelMethodPanel.tsx`, `apps/web/src/components/decision-support/SquareMatrixEditor.tsx` and `apps/web/src/components/decision-support/NamedListEditor.tsx`; gate create/method/criterion/matrix/save/run controls while preserving read/history access and server authority.

- [ ] T041 [US4] GREEN after T038: implement one same-case save/run coordinator in `apps/web/src/app/routes/project-decision-support.tsx` and minimal callback/disabled/pending adapters in `apps/web/src/components/decision-support/AhpMethodPanel.tsx`, `apps/web/src/components/decision-support/SawMethodPanel.tsx`, `apps/web/src/components/decision-support/TopsisMethodPanel.tsx` and `apps/web/src/components/decision-support/DematelMethodPanel.tsx`; deep-copy submissions, serialize whole PATCH→POST operations, guard selection/unmount and preserve existing algorithms and input semantics.

- [ ] T042 [P] [US4] GREEN after T036: complete DEMATEL labels/roles/caveat and dynamic errors in `apps/web/src/app/locales/en.json`, `apps/web/src/app/locales/fa.json` and any missing backend messages in `apps/api/core/locale/fa/LC_MESSAGES/django.po`; compile `django.mo` when changed and rerun key coverage. Role identifiers remain `influencing`, `receiving`, `balanced`.

- [ ] T043 [US4] GREEN after T037: correct only observed focus/caret/RTL/pair-alignment gaps in `apps/web/src/components/decision-support/NamedListEditor.tsx`, `apps/web/src/components/decision-support/SquareMatrixEditor.tsx`, `apps/web/src/components/decision-support/dematel-input-rules.ts` and `apps/web/src/app/routes/project-decision-support.tsx`; keep index-based DEMATEL rename retention and separate AHP name-based remapping, using exact earlier data-model constraints.

- [ ] T044 [US4] GREEN after T039 and T042: complete active-language display formatting in `apps/web/src/components/decision-support/DematelResultTable.tsx`, `apps/web/src/components/decision-support/InputSnapshotViewer.tsx` and only if needed `apps/web/src/components/decision-support/ExecutionHistoryList.tsx`; never round stored values or classify roles on the client, and retain historical execution time across language switches.

- [ ] T045 [US4] GREEN after T035 only if failures expose a gap: repair established project/case/run scoping in `apps/api/core/decision_support/views.py` or DEMATEL authoritative lookup in `apps/api/core/decision_support/services/execution_service.py`; retain current permission catalog and administrator behavior, rerun the denial tests, and record green existing behavior without unnecessary edits.

- [ ] T046 [US4] Run focused permission API/key/helper/EN/FA keyboard/pending/locale scenarios after the fixes; capture actual exits, focus/ordering assertions, role explanations, denied request results and late-response behavior in `specs/022-decision-dematel/validation.md`. Verify all specified influencing/receiving/balanced reference roles are rendered correctly.

- [ ] T047 [US4] Run existing `apps/web/e2e/tests/decision-ahp.spec.ts` browser scenarios plus AHP helper/API regressions and new SAW/TOPSIS mixed-method adapter smoke cases in `apps/web/e2e/tests/decision-dematel.spec.ts`; prove shared adapters did not change engine results, reciprocal edits or established rename behavior, recording evidence in `specs/022-decision-dematel/validation.md`.

**Checkpoint**: Story complete only when its independent test and scoped evidence pass.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose/Goal**: Collect final-tree acceptance evidence and update actual interface documentation without widening scope.

- [ ] T048 Extend `apps/api/core/decision_support/tests/test_no_math_in_views.py` and add `apps/web/src/components/decision-support/no-client-dematel-math.test.ts` for the server-service calculation boundary, new DEMATEL components and missing-source failures; run the guards and meaningful isolated negative-control samples. These audits complement numerical/API/browser evidence and cannot establish feature completion alone.

- [ ] T049 Update `apps/api/core/decision_support/ENDPOINTS.md` and schema descriptions in `apps/api/core/decision_support/views.py` to state DEMATEL now executes, document draft/strict-input/result/error/history policy and remaining ISM stub; synchronize actual runnable commands and observed limits in `specs/022-decision-dematel/quickstart.md` without rewriting accepted spec/plan policies.

- [ ] T050 Run final-tree full pytest `decision_support/tests` and `makemigrations --check --dry-run` using PostgreSQL/Redis as documented in `specs/022-decision-dematel/quickstart.md`; record command/output/exit/runtime in `specs/022-decision-dematel/validation.md`, confirm no planned schema change, and resolve only feature regressions before marking complete.

- [ ] T051 Run final-tree Node helper/key/math-boundary regressions, `pnpm typecheck`, and full `apps/web/e2e/tests/decision-dematel.spec.ts` plus existing AHP browser suite with traces per `specs/022-decision-dematel/quickstart.md`; record actual counts/exits/traces in `specs/022-decision-dematel/validation.md` and identify unrelated existing type errors without repairing them or claiming full typecheck success.

- [ ] T052 Measure SC-006 in `apps/web/e2e/tests/decision-dematel.spec.ts` or the documented browser validation flow: at least 20 valid real request-to-visible-result trials including n=10 under recorded normal conditions, active throttling, warm/cold state and locale context. Record every sample and ≥95% within 2s assessment in `specs/022-decision-dematel/validation.md`; no calculation-only benchmark or invented timing may satisfy this task.

- [ ] T053 Reconcile FR-001–FR-017 and SC-001–SC-007 against actual final evidence in `specs/022-decision-dematel/validation.md` and `specs/022-decision-dematel/tasks.md`; mark tasks only after their own requirements pass, retain any unverified acceptance item unchecked, verify protected source-requirement/AHP-spec/model/constitution hashes and compare shared-adapter diffs against the initial dirty worktree to preserve earlier AHP edits, and report remaining limits without generating commits or deployment actions.

---

## Dependencies & Execution Order

### Phase and story dependencies

```text
Setup → Foundation → US1 (safe independent execution / MVP)
                         ├→ US2 (actionable errors and correction)
                         ├→ US3 (frozen history and coherent snapshots)
                         └→ US4 (bilingual usability / permissions / shared coordination)
US1 + US2 + US3 + US4 → final evidence and acceptance
```

US2 and US3 need a working US1 run to test correction and history; US4's full flow needs US1 and its history/feedback surfaces. These are honest integration dependencies, not independent reimplementations. Each story has its own isolated acceptance fixture and adds value without requiring another calculation method. Recommended execution is phase order because later tasks edit shared files; do not edit the same route/test files concurrently across stories.

Specific GREEN dependencies are written in task descriptions. Within US1, backend numerical/run work and frontend pure helper/editor work can proceed separately after their RED batches; panel integration waits for both. US2 backend error localization and frontend error-focus work can proceed separately after their respective failing tests. Within US3, backend snapshot/concurrency fixes and frontend historical viewer work are separate, followed by the story acceptance check. US4 shared-panel adapters and route state are one sequential integration unit; localization files can proceed in parallel after key tests.

### Parallel examples per story

- **US1**: T007 with T009 (distinct Python and TypeScript helper files); T008 and T010 can be authored separately, but serialize any shared runtime/database use. After red evidence, T011 and T014 are separate implementation branches; join at T017.
- **US2**: T019 with T020 (API and error-helper tests); T022 with T023 after their red prerequisites. Do not concurrently edit the shared browser suite.
- **US3**: T028, T029 and T030 use distinct test files; serialize PostgreSQL test invocations sharing the test database. T031 and T032 touch different layers after prerequisites.
- **US4**: T035 with T036 (API permission and locale-key tests); T042 can run alongside the sequential route/panel adapter work. T037, T038 and T039 share one browser file and must be serialized.

## Requirement and Entity Coverage

| Requirement/outcome | Owning tasks |
| --- | --- |
| FR-001 independent method; SC-001 | T008, T012, T010, T017, T018 |
| FR-002–FR-004 names/dimensions/scale/diagonal | T003, T004, T009, T015, T019 |
| FR-005 drafts/pair identity; DecisionCase judgments | T005, T006, T009, T014, T017, T025 |
| FR-006–FR-009 calculation/roles; SC-002–SC-003 | T007, T011, T016, T019, T022, T027 |
| FR-010 truthful interpretation | T016, T036, T042, T046 |
| FR-011–FR-012 immutable DecisionRun; SC-004 | T008, T012, T028, T029, T031, T032, T034 |
| FR-013 independent inputs/no weight feed | T005, T006, T008, T010, T047 |
| FR-014 locatable/request feedback | T020, T021, T023, T024, T026 |
| FR-015 permissions/isolation; SC-007 | T035, T040, T045, T046 |
| FR-016 bilingual text/dates; SC-005 | T036, T039, T042, T044, T046 |
| FR-017 keyboard/RTL/pair alignment; SC-005 | T009, T014, T037, T043, T046 |
| SC-006 user-visible performance | T052 |
| Calculation boundary/full regression/no migration | T048, T050, T051, T053 |

## Implementation Strategy

### MVP first

Complete Setup, Foundation and US1, then demonstrate the criteria-only directed-chain execution with exact server results. Foundation and US1 include strict validation, numerical rejection, server authorization inherited from scoped endpoints, frozen record creation and no automatic ranking-weight changes. This is the smallest technical MVP; full product acceptance still requires US2–US4 and the final evidence phase.

### Incremental delivery

Add US2 correction/error recovery, US3 frozen review and concurrency proof, then US4 bilingual keyboard/permission/coordination behavior. Recheck earlier story behavior after shared-file changes. Use the defined parallel batches only when prerequisites are met; no agent delegation is required by this task list. Finish documentation, full final-tree checks, performance samples and acceptance reconciliation. Deployment, commit and push are outside this task-generation workflow.

## Notes

- Numerical policy is the settled feature contract, including exact zero scale, condition limit 1e8/residual tolerance 1e-10, roundoff factor 1e-12 and role neutrality 1e-9. Do not silently switch normalization, use a pseudoinverse, or generate ranking weights.
- AHP rename-clearing and reciprocity remain established behavior; DEMATEL rename retention and directed edits use their own mapping. Shared panel changes are adapters only.
- Preserve old DEMATEL stubs and ISM placeholders. Do not rewrite historical runs or weaken old mixed-history assertions.
- Case save then run are separate requests. Compute and snapshot the authoritative locked saved state; no new optimistic client-revision promise is introduced.
- Final performance/browser acceptance tasks remain unchecked when their required evidence is unavailable. Checklist completion, a helper pass, or a source audit alone is insufficient.

**Task counts**: 53 total; Phase 1=2, Phase 2=4, US1=12, US2=9, US3=7, US4=13, Phase 7=6.
