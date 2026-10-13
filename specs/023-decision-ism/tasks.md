# Tasks: Independent ISM Criterion Layering

**Input**: Design artifacts in `specs/023-decision-ism/`: [spec](spec.md), [plan](plan.md), [research](research.md), [data model](data-model.md), [API](contracts/ism-inputs-api.md), [result](contracts/ism-result.md), [UI](contracts/ism-ui.md), [validation guide](quickstart.md).

**Feature**: `023-decision-ism` | **Git branch at generation**: `develop` | **Created**: 2026-10-12.

**Tests**: TDD requested. “Use TD” is interpreted as TDD consistently with the preceding requests and plan. All tasks start unchecked; this document creates no application implementation or acceptance evidence.

**Organization**: Setup → shared foundation → US1 (P1) → US2 (P1) → US3 (P2) → US4 (P2) → final evidence. Existing entities serve all stories; no models, migrations, routes, permissions, dependencies or DEMATEL engine are added.

## Format and execution rules

- Tasks use `- [ ] TNNN [P?] [USn?] description with exact repository-relative paths`.
- `[P]` identifies independent files within a stated ready test batch. Finish prerequisite phases first; do not edit the same file concurrently across batches/stories.
- For missing behavior: run a meaningful failing assertion → minimal fix → focused green. Retain commands, assertion/exit and final green evidence in `specs/023-decision-ism/validation.md`. An import/scaffolding failure alone is not behavioral red. Already-correct behavior receives regression evidence; never break it to manufacture red.
- Every implementation task depends on its named test tasks. Rerun those tests immediately after its slice, even when a later checkpoint also names a broader suite.
- Read contracts for exact wire fields and error codes. The server calculates closure/layers/groups; frontend helpers handle entry/remap/structural guarding only. Do not derive expected outputs using production computation.
- Preserve dirty AHP work and all other feature artifacts. DEMATEL is unimplemented and is not a prerequisite; reuse compatible host support if it exists by implementation time, otherwise supply the minimal ISM support here.

## Phase 1: Setup

**Purpose**: Establish a reproducible worktree/environment and independent reference inputs without changing application behavior.

- [X] T001 Record Git branch/status, hashes or scoped baseline of existing dirty AHP work, active feature pointer and available design artifacts in `specs/023-decision-ism/validation.md`; inspect `apps/api/core/decision_support/models.py` and `apps/web/src/app/routes/project-decision-support.tsx` for drift, preserving existing fields and the title constraint “Existing required/max-200 policy”.
- [X] T002 Verify the existing PostgreSQL/Redis/API/browser environment using `specs/023-decision-ism/quickstart.md` and `apps/web/e2e/playwright.config.ts`; record versions/config/project name in `specs/023-decision-ism/validation.md`, retaining Django 4.2, actual root `.env` sourcing and no database reset/dependency upgrade.
- [X] T003 Transcribe the literal small-network and n=10 chain/cycle expectations from `specs/023-decision-ism/contracts/ism-result.md` into the fixture design section of `specs/023-decision-ism/validation.md`; identify a test-only traversal oracle distinct from production Warshall and retain direct diagonal 0/1 examples.

## Phase 2: Foundational — Shared Input and Host Boundaries

**Purpose**: Block all story delivery until strict execution, recoverable finite storage, permission presentation and same-case mutation coordination are available. No general framework or existing method algorithm rewrite.

### Validator and draft slices

- [X] T004 Write and run failing strict ISM validator tests in `apps/api/core/decision_support/tests/test_ism_service.py` for the data-model constraints “Execution 1–10 trimmed, nonempty unique strings” and “execution exact n×n numeric 0/1”; cover malformed root/rows, null/empty/text/bool/fractions/negative/>1/nonfinite/overflow, accepted 0.0/1.0 and both diagonal values with contract issue paths before unsafe indexing.
- [X] T005 Implement method-specific ISM executable validation in `apps/api/core/decision_support/services/validators.py` after T004; use existing trim/exact uniqueness and coded issue envelope, reject bool/text without coercion, accept all-zero input/direct diagonal 0/1, and rerun T004 green.
- [X] T006 Write and run failing ISM finite draft-storage and matrix-only PATCH isolation tests in `apps/api/core/decision_support/tests/test_ism_api.py`; null/finite invalid judgments stay drafts, actual nonfinite/overflow is rejected before JSON, unrelated ranking data is not revalidated by ISM-only correction, and genuine shared criterion changes still enforce existing ranking dimensions.
- [X] T007 Extend draft numeric guards and ISM-only matrix PATCH handling in `apps/api/core/decision_support/services/validators.py` and `apps/api/core/decision_support/services/case_service.py` after T006; keep AHP-only `ism_matrix:[[9]]` preservation and other method behavior, then rerun focused draft tests and `apps/api/core/decision_support/tests/test_ahp_api.py` green.

### Shared operation and permission slices

- [X] T008 Write and run missing-behavior browser assertions in `apps/web/e2e/tests/decision-ism.spec.ts` using existing AHP/SAW/TOPSIS/global saves for a synchronous same-case busy gate, frozen submitted variables, duplicate/conflicting acquisition rejection, failed-PATCH prevention of POST and `finally` release; retain real red before adding the coordinator.
- [X] T009 Implement the small route-owned mutation coordinator in `apps/web/src/app/routes/project-decision-support.tsx` and minimal adapters in `apps/web/src/components/decision-support/AhpMethodPanel.tsx`, `apps/web/src/components/decision-support/SawMethodPanel.tsx` and `apps/web/src/components/decision-support/TopsisMethodPanel.tsx` after T008; serialize each same-case PATCH→POST with global save, preserve algorithms/input semantics and rerun the shared-operation tests green.
- [X] T010 Write and run failing view-only mixed-workspace browser assertions in `apps/web/e2e/tests/decision-ism.spec.ts` for unavailable case creation, selected-method/criterion/ranking/relation editing and all save/run controls while cases/history remain readable; use actual project permission fixtures rather than treating UI as server authorization.
- [X] T011 Gate writable controls through existing `usePermission(projectId)` and the shared pending boundary in `apps/web/src/app/routes/project-decision-support.tsx` and `apps/web/src/components/decision-support/AhpMethodPanel.tsx`, `apps/web/src/components/decision-support/SawMethodPanel.tsx`, `apps/web/src/components/decision-support/TopsisMethodPanel.tsx` after T010; preserve existing permission IDs/server policy, rerun T010 and existing AHP browser regression green.

**Checkpoint**: Shared foundation green; strict execution does not block unfinished draft saving. Existing method algorithms and DEMATEL placeholder behavior remain unchanged.

## Phase 3: US1 — Extract Layers from My Criterion Relationships (P1, MVP)

**Goal**: A valid ISM-only case produces complete reachability and ordered structural layers independently of alternatives, weights and other methods.

**Independent test**: Enter A→B→C with `[[0,1,0],[0,0,1],[0,0,0]]`; expect `[[1,1,1],[0,1,1],[0,0,1]]` and levels 1:C, 2:B, 3:A. Also verify diamond, all-zero and one-criterion examples and unchanged unrelated mixed-method fields.

### Tests first (parallel ready batch after foundation)

- [X] T012 [P] [US1] Add and run pure calculation references in `apps/api/core/decision_support/tests/test_ism_service.py`: chain, diamond, disconnected, single diagonal 0/1, all-zero and ten-chain/ten-cycle; verify binary identity, full closure, active-set round restriction, simultaneous `Reach==Reach∩Antecedent`, “every criterion appears exactly once”, original order and levels≤n using literals/traversal oracle, then retain behavioral red.
- [X] T013 [P] [US1] Add and run API contract/independence tests in `apps/api/core/decision_support/tests/test_ism_api.py` for ISM-only 201 runs, exact `engine/status/result/policy`, immutable distinct append, unchanged other inputs/results, authoritative stale/deselected/deleted case handling and synchronized PostgreSQL save/run consistency; capture new behavioral failures and regression passes separately.
- [X] T014 [P] [US1] Add and run failing entry-helper tests in `apps/web/src/components/decision-support/ism-input-rules.test.ts` for explicit diagonal-zero/off-diagonal-null defaults, independent directed edits, exact empty/0/1 option mapping and guarded raw hydration without truthiness/blank conversion.
- [X] T015 [P] [US1] Add and run failing completed-result structural guard tests in `apps/web/src/app/lib/api/decision-support.test.ts` for `status:ok`, `engine:ism`, supported policy, n×n integer binary rows and frozen membership/order, rejecting malformed/unavailable stubs without calculating closure/layers/groups.
- [X] T016 [P] [US1] Add and run failing real API/browser ISM-only entry/run/render scenarios in `apps/web/e2e/tests/decision-ism.spec.ts` for chain, diamond, all-zero and single diagonal 0/1, save-before-run and mixed-method field/result preservation; verify the displayed matrix axes come from returned input.

### Implementation and focused green

- [X] T017 [US1] Implement pure `compute_ism` in `apps/api/core/decision_support/services/ism_service.py` after T012: copy direct input, Boolean identity/Warshall, active-set reachable/intersection extraction and maximal non-singleton classes per `specs/023-decision-ism/contracts/ism-result.md`; satisfy “n×n integer zero/one” and “consecutive levels from one”, stable member/group order and defensive no-progress/assignment guards with no weights/client/DEMATEL math, then run service tests green.
- [X] T018 [US1] Add early ISM-only dispatch and atomic project/case-scoped active `select_for_update` reload in `apps/api/core/decision_support/services/execution_service.py` after T013/T017; recheck method selection, compute/deep-snapshot/append from the same row, retain `method:ism` and server actor/time (“Actor foreign key is protected.”), zero partial records and unchanged other engines, then run API/concurrency tests green.
- [X] T019 [US1] Run T004/T006/T012/T013 and existing immutable/AHP mixed-history tests under PostgreSQL using `apps/api/core/decision_support/tests/test_ism_service.py`, `apps/api/core/decision_support/tests/test_ism_api.py`, `apps/api/core/decision_support/tests/test_runs_immutability.py` and `apps/api/core/decision_support/tests/test_ahp_api.py`; record focused green commands/exits in `specs/023-decision-ism/validation.md` before integrating the browser run.
- [X] T020 [US1] Implement guarded draft/default/direct-edit/local-validation helpers in `apps/web/src/components/decision-support/ism-input-rules.ts` after T014; preserve raw invalid containers/values for recovery, distinguish empty legacy matrix initialization from existing invalid data, and rerun helper tests green.
- [X] T021 [US1] Add ISM draft/completed-result/layer/group/policy types and structural guard in `apps/web/src/app/lib/api/decision-support.ts` after T015; keep wire input guarded unknown and valid editable matrix `(number|null)[][]`, exact contract fields, frozen name membership and legacy-stub fallback without client derivation, then rerun guard tests green.
- [X] T022 [US1] Build `apps/web/src/components/decision-support/BinaryRelationEditor.tsx` after T014/T016/T020 using semantic labeled row-influences-column native selects for unanswered/null, No/0 and Yes/1; all direct diagonals editable, reverse cells independent, existing styles and no AHP square-editor rule change; run entry/browser assertions green as integration becomes available.
- [X] T023 [US1] Build initial `apps/web/src/components/decision-support/IsmLayerList.tsx` after T015/T016/T021 to render server numbered layers and read-only reachability beside direct input with frozen axis names; keep membership/policy data server-supplied and run chain/diamond/all-zero presentation assertions.
- [X] T024 [US1] Build `apps/web/src/components/decision-support/IsmMethodPanel.tsx` after T008/T010/T016/T018/T022/T023 with explicit save-before-POST run, shared coordinator, permission/pending props, frozen operation variables and current result bound to returned snapshot; failed saves send no run, POST is not automatically retried, and current result clears on relevant edits/new attempts/failure.
- [X] T025 [US1] Integrate keyed ISM hydration/reset/live draft/global save/current-run state in `apps/web/src/app/routes/project-decision-support.tsx` after T020–T024; include selected ISM without ranking prerequisites, preserve all unrelated fields, guard case identity/unmount callbacks and render against authoritative returned input rather than live case names.
- [X] T026 [US1] Add EN/FA method/relation/axis/layer/basic execution labels and pending feedback in `apps/web/src/app/locales/en.json` and `apps/web/src/app/locales/fa.json` after T022–T025; use stable `ism` identifiers, accessible labels and existing active-language number/date conventions without storing translated result data.
- [X] T027 [US1] Run helper/guard and real persisted US1 browser scenarios in `apps/web/src/components/decision-support/ism-input-rules.test.ts`, `apps/web/src/app/lib/api/decision-support.test.ts` and `apps/web/e2e/tests/decision-ism.spec.ts`; record green chain/diamond/all-zero/single/mixed-method outcomes and exact frozen matrices in `specs/023-decision-ism/validation.md`.
- [X] T028 [US1] Verify the full independent US1 acceptance examples from `specs/023-decision-ism/spec.md` against the implementation and evidence in `specs/023-decision-ism/validation.md`; confirm no alternatives/weights/DEM engine, no case mutation by execution, no rank/weight output and no more levels than criteria before declaring this checkpoint complete.

**Checkpoint**: US1 is an independently demonstrable MVP, with safe shared host boundaries. US2–US4 acceptance remains outstanding; this is not complete-feature acceptance.

## Phase 4: US2 — Enter and Correct Explicit Binary Judgments (P1)

**Goal**: Unanswered/invalid drafts remain recoverable, directed pair identity survives criterion operations, and errors identify/focus the actual pair.

**Independent test**: Save/reopen a blank A→C judgment, fail execution with a locatable pair error, correct to zero and succeed. Rename/reorder/add/remove preserves surviving directed pairs, and denial/interruption retains the draft without stale success.

### Tests first (parallel ready batch after US1)

- [X] T029 [P] [US2] Extend and run draft/API rejection/recovery tests in `apps/api/core/decision_support/tests/test_ism_api.py` for incomplete save/reopen, finite invalid binary drafts, malformed persisted scalar/non-row containers, strict field/pair errors, every invalid count/name/shape/type and zero successful runs; cover scoped correction without crashing `_case_dict`, retaining any actual new red failures.
- [X] T030 [P] [US2] Extend and run failing rename/move/add/remove pair-remap tests in `apps/web/src/components/decision-support/ism-input-rules.test.ts`; rename keeps all pairs, move permutes both axes, insertion yields zero new diagonal/null new cross-pairs, removal retains survivors and opposite judgments remain independent.
- [X] T031 [P] [US2] Add and run failing keyboard/draft/failure browser cases in `apps/web/e2e/tests/decision-ism.spec.ts` for multi-character typing/caret, save/reload blanks, malformed/invalid visible correction, named error focus and 403/404/429/non-JSON/network feedback; failed PATCH must not POST and old success must not masquerade as a new result.
- [X] T032 [P] [US2] Add and run optional operation-metadata regressions in `apps/web/src/components/decision-support/NamedListEditor.test.ts` for rename index, move source/destination, add index and removal index; retain existing callback/typing/AHP behavior and capture missing-metadata behavioral failure before changing the editor.

### Implementation and focused green

- [X] T033 [US2] Make persisted malformed ISM input recoverable in `apps/api/core/decision_support/services/case_service.py` after T029, retaining raw finite invalid values without scalar `list()` exceptions or implicit empty/zero replacement; keep matrix-only isolation and genuine shared ranking validation, then run draft/API/AHP preservation tests green.
- [X] T034 [US2] Add optional operation/index metadata to `apps/web/src/components/decision-support/NamedListEditor.tsx` after T032/T031 while preserving ordinary typing focus/caret and existing callback consumers; AHP's name-based rename clearing must not change, then run named-list and browser typing tests green.
- [X] T035 [US2] Implement operation-driven two-axis ISM reconciliation in `apps/web/src/components/decision-support/ism-input-rules.ts` after T030/T034; never infer rename identity by matching newly typed names or mirror reverse cells, then run all remap helpers green.
- [X] T036 [US2] Apply optional operations to ISM state and save aligned criteria/matrix together in `apps/web/src/app/routes/project-decision-support.tsx` after T035; preserve surviving pair identities through rename/move/add/remove, retain existing AHP/ranking reconciliation and surface shared-field save failures without losing the local draft.
- [X] T037 [US2] Finish explicit invalid/raw recovery presentation and stable directed cell focus targets in `apps/web/src/components/decision-support/BinaryRelationEditor.tsx` after T029/T031; text/bool/finite invalid cells or wrong containers are visible until deliberate correction/reset, never silently coerced/blanked, then rerun persisted-invalid/correction browser cases.
- [X] T038 [US2] Extend ISM pair-path parsing/localized location and clickable focus in `apps/web/src/components/decision-support/validation-issues.ts` and `apps/web/src/components/decision-support/ValidationIssueList.tsx` after T031; support `ism_matrix.i.j` alongside existing AHP paths and existing generic request fallbacks, then run the relevant assertions and `apps/web/src/components/decision-support/ValidationIssueList.test.ts` regressions.
- [X] T039 [US2] Add `ism_relation_invalid`, `ism_derivation_failed` and missing/type/shape/pair feedback in `apps/api/core/locale/fa/LC_MESSAGES/django.po`, `apps/api/core/locale/fa/LC_MESSAGES/django.mo`, `apps/web/src/app/locales/en.json` and `apps/web/src/app/locales/fa.json` after T029/T031/T038; compile Persian messages using the pinned runtime and retain stable error codes with localized messages.
- [X] T040 [US2] Complete recoverable failed-save/run behavior in `apps/web/src/components/decision-support/IsmMethodPanel.tsx` after T031/T038/T039; keep draft values, clear current output on attempts/failure/relevant edits, leave prior history inspectable and refetch history for ambiguous lost responses before an explicit retry, then rerun failure scenarios green.
- [X] T041 [US2] Run ISM and existing named-list/square-matrix/validation helper regressions in `apps/web/src/components/decision-support/ism-input-rules.test.ts`, `apps/web/src/components/decision-support/NamedListEditor.test.ts`, `apps/web/src/components/decision-support/SquareMatrixEditor.test.ts` and `apps/web/src/components/decision-support/ValidationIssueList.test.ts`; record exact green/remap evidence in `specs/023-decision-ism/validation.md`.
- [X] T042 [US2] Run all strict/draft/recovery API tests and AHP invalid-ISM preservation regression from `apps/api/core/decision_support/tests/test_ism_service.py`, `apps/api/core/decision_support/tests/test_ism_api.py` and `apps/api/core/decision_support/tests/test_ahp_api.py`; record rejection paths, accepted explicit zeros and zero appended failures in `specs/023-decision-ism/validation.md`.
- [X] T043 [US2] Run EN/FA draft/correction/rename/move/add/remove/failure browser cases in `apps/web/e2e/tests/decision-ism.spec.ts` against real persistence; retain traces and directed pair/focus observations in `specs/023-decision-ism/validation.md` before completing US2.

## Phase 5: US3 — Understand Cycles and Review Frozen Layers (P2)

**Goal**: Explicit maximal mutual groups and accurate interpretation accompany immutable frozen historical analyses.

**Independent test**: A↔B with B→C yields layer 1:C and layer 2:A/B with one A/B group. Edit/reorder/rerun and reopen the original frozen direct/derived/layers/groups/actor/time. Full three-cycle is one group/layer; disconnected same-layer criteria are not grouped.

### Tests first (parallel ready batch after US2)

- [X] T044 [P] [US3] Extend exact group/invariant references in `apps/api/core/decision_support/tests/test_ism_service.py` for two-way/outgoing cycles, longer cycles with no direct reciprocal pair, multiple connected/disconnected maximal groups, original group ordering and singleton/self/same-level exclusions; test unsuccessful defensive derivation separately from valid-cycle success, retaining real regressions without manufacturing red for already-correct T017 behavior.
- [X] T045 [P] [US3] Add and run frozen ISM record tests in `apps/api/core/decision_support/tests/test_runs_immutability.py` for new run IDs after edits/reruns and unchanged ordered input/direct/closure/layers/groups/actor/time/other-method runs, plus denied run mutation and method-filtered history; record existing passes and any missing-behavior red separately.
- [X] T046 [P] [US3] Add and run failing cycle/explanation/frozen-history browser cases in `apps/web/e2e/tests/decision-ism.spec.ts` including language switches and legacy ISM stubs; assert server-provided groups, no false same-layer groups and historical labels independent of live names/order.
- [X] T047 [P] [US3] Extend and run structural group/member/order/policy guard tests in `apps/web/src/app/lib/api/decision-support.test.ts` for unknown names, duplicate memberships, wrong group-level references and unavailable legacy stubs; guard structure only, never determine actual mutual reachability on the client.

### Implementation and focused green

- [X] T048 [US3] Complete frozen membership/group-level/policy structural guarding in `apps/web/src/app/lib/api/decision-support.ts` after T047, preserving valid named contract results and treating malformed/stub computations as unavailable; rerun guard tests green without client analysis.
- [X] T049 [US3] Extend `apps/web/src/components/decision-support/IsmLayerList.tsx` after T046/T048 to render explicit server mutual groups at their shared levels in deterministic order, distinguish same-level from mutual reachability and explain result-oriented/top versus more foundational/lower without causal proof/weight/rank/deletion advice; run cycle/presentation checks green.
- [X] T050 [US3] Add frozen ISM direct/derived matrices, layer/group review and legacy unavailable fallback in `apps/web/src/components/decision-support/InputSnapshotViewer.tsx` after T045/T046/T048/T049; derive every axis/member label from the selected run's snapshot, not the live case, then rerun edit/rerun historical browser assertions.
- [X] T051 [US3] Integrate frozen historical selection/method filtering and current-versus-history separation in `apps/web/src/app/routes/project-decision-support.tsx` and `apps/web/src/components/decision-support/ExecutionHistoryList.tsx` after T045/T046/T050; reuse existing locale dates/actor display and ensure edit/language changes do not rewrite selected frozen data.
- [X] T052 [US3] Add complete EN/FA cycle-group, no-group, historical-unavailable and interpretation text in `apps/web/src/app/locales/en.json` and `apps/web/src/app/locales/fa.json` after T049–T051; layer/group/actor/time data remains language-independent and interpretation never recommends automatic criterion removal.
- [X] T053 [US3] Run expanded service/maximal-group/defensive failure and immutable-run/API suites in `apps/api/core/decision_support/tests/test_ism_service.py`, `apps/api/core/decision_support/tests/test_runs_immutability.py` and `apps/api/core/decision_support/tests/test_ism_api.py`; fix only demonstrated derivation/snapshot defects in the ISM service/path if needed and record green frozen comparisons in `specs/023-decision-ism/validation.md`.
- [X] T054 [US3] Run result guards and EN/FA cycle/frozen history/legacy-stub scenarios in `apps/web/src/app/lib/api/decision-support.test.ts` and `apps/web/e2e/tests/decision-ism.spec.ts`; record exact group/level/old-record equality and explanatory copy evidence in `specs/023-decision-ism/validation.md`.

## Phase 6: US4 — Use ISM Safely in Persian or English (P2)

**Goal**: Complete localized keyboard flows with permission and late-operation isolation across the mixed-method workspace.

**Independent test**: In EN and FA, enter/correct/run/review ISM by keyboard, switch language, attempt view-only/foreign-project access, delay each method/global save and switch cases before a response. Pair identity and frozen provenance remain stable; denied attempts disclose/mutate nothing.

### Tests first

- [X] T055 [P] [US4] Extend real authenticated access tests in `apps/api/core/decision_support/tests/test_ism_api.py` for no membership, absent view/edit permission, view-only create/PATCH/run, foreign project/case/nested run and existing administrator policy; assert denied requests append zero runs and disclose no foreign data, recording existing correct enforcement as regression.
- [X] T056 [US4] Add and run failing full EN/FA keyboard/caret/RTL/date/number/language-switch assertions in `apps/web/e2e/tests/decision-ism.spec.ts`, including all editor operations, directed error focus and historical direct/derived/group review; separate actual missing behavior from previously green story scenarios.
- [X] T057 [P] [US4] Add locale-key/dynamic-error coverage and server-only analysis audits in `apps/web/src/components/decision-support/i18n.keys.test.ts`, `apps/web/src/components/decision-support/no-client-ism-math.test.ts` and `apps/api/core/decision_support/tests/test_no_math_in_views.py`; cover all new components/guards, reject frontend closure/layer/group calculation and retain architectural regression passes honestly.
- [X] T058 [US4] Extend and run delayed-response/pending browser assertions in `apps/web/e2e/tests/decision-ism.spec.ts` for each AHP/SAW/TOPSIS/global→ISM and ISM→other/global conflict, duplicate clicks, pending edits, permission feedback, case-switch/unmount late responses and old-operation release not clearing a newer case's gate; include both locales and frozen returned input.

### Implementation and focused green

- [X] T059 [US4] Verify or minimally repair only demonstrated ISM authorization/scoping regressions in `apps/api/core/decision_support/views.py` and `apps/api/core/decision_support/services/execution_service.py` after T055; preserve existing `view_decision_support`/`edit_decision_support`, scoped active row loading, administrator and denial policy, then run access tests green without adding a new permission.
- [X] T060 [US4] Fix demonstrated EN/FA typing/caret/keyboard/directed focus defects in `apps/web/src/components/decision-support/NamedListEditor.tsx`, `apps/web/src/components/decision-support/BinaryRelationEditor.tsx` and `apps/web/src/components/decision-support/ValidationIssueList.tsx` after T056; preserve physical/logical axis mapping, operation metadata and AHP semantics, then rerun keyboard scenarios green.
- [X] T061 [US4] Finish project/case-keyed operation identity, late-response invalidation and busy-gate release isolation in `apps/web/src/app/routes/project-decision-support.tsx`, `apps/web/src/components/decision-support/IsmMethodPanel.tsx`, `apps/web/src/components/decision-support/AhpMethodPanel.tsx`, `apps/web/src/components/decision-support/SawMethodPanel.tsx` and `apps/web/src/components/decision-support/TopsisMethodPanel.tsx` after T058; keep history readable and no client revision/exactly-once guarantee, then run delay/conflict cases green.
- [X] T062 [US4] Complete permission/pending presentation for every remaining workspace editor/action in `apps/web/src/app/routes/project-decision-support.tsx` and `apps/web/src/components/decision-support/IsmMethodPanel.tsx` after T055/T056/T058; view-only sees inputs/results/history with no writable relation/criterion/method/ranking/save/run controls, then rerun mixed-workspace access browser cases.
- [X] T063 [US4] Finish localized text/error/date/number/direction presentation in `apps/web/src/app/locales/en.json`, `apps/web/src/app/locales/fa.json`, `apps/web/src/components/decision-support/IsmLayerList.tsx`, `apps/web/src/components/decision-support/InputSnapshotViewer.tsx` and `apps/web/src/components/decision-support/ExecutionHistoryList.tsx` after T056/T057; use existing locale conventions and keep stored identifiers/names/membership/actor/time unchanged.
- [X] T064 [US4] Run all new/extended locale and no-client/no-view-math audits in `apps/web/src/components/decision-support/i18n.keys.test.ts`, `apps/web/src/components/decision-support/no-client-ism-math.test.ts` and `apps/api/core/decision_support/tests/test_no_math_in_views.py`; fix only demonstrated missing keys/boundary violations and record this evidence separately from actual browser/math proof in `specs/023-decision-ism/validation.md`.
- [X] T065 [US4] Run actual API access denials and view-only/mixed-method browser controls from `apps/api/core/decision_support/tests/test_ism_api.py` and `apps/web/e2e/tests/decision-ism.spec.ts`; record zero-disclosure/zero-run outcomes and administrator/read access in `specs/023-decision-ism/validation.md`.
- [X] T066 [US4] Run the complete EN/FA keyboard/RTL/caret/correction/language-switch/history flow from `apps/web/e2e/tests/decision-ism.spec.ts`; retain traces and paired row/column plus unchanged frozen-data assertions in `specs/023-decision-ism/validation.md`.
- [X] T067 [US4] Run all delayed global/other-method/ISM saves, failure and case-switch scenarios from `apps/web/e2e/tests/decision-ism.spec.ts`; record conflict rejection, preserved drafts, operation identity and authoritative returned snapshot evidence in `specs/023-decision-ism/validation.md` before completing US4.

## Phase 7: Polish and Cross-Cutting Verification

**Purpose**: Validate the final changed tree across all evidence categories and every success criterion; no source-only completion claims.

- [X] T068 Update implemented-method/schema guidance in `apps/api/core/decision_support/ENDPOINTS.md` and `apps/api/core/decision_support/views.py`, and actual runnable commands in `specs/023-decision-ism/quickstart.md`; document binary draft/execute distinction, groups/frozen output, scope/access and unchanged DEMATEL placeholder without changing source requirements/spec/plan.
- [X] T069 Check compiled Persian backend messages and complete EN/FA frontend keys using `apps/api/core/locale/fa/LC_MESSAGES/django.po`, `apps/api/core/locale/fa/LC_MESSAGES/django.mo` and `apps/web/src/components/decision-support/i18n.keys.test.ts`; record final compilation/key exits in `specs/023-decision-ism/validation.md`.
- [X] T070 Run the full PostgreSQL Decision Support suite under `apps/api/core/decision_support/tests/` using `specs/023-decision-ism/quickstart.md`; retain final-tree test count/exit and existing AHP/SAW/TOPSIS/DEM-stub compatibility evidence in `specs/023-decision-ism/validation.md`.
- [X] T071 Run all relevant Decision Support helper/guard/source tests under `apps/web/src/components/decision-support/` plus `apps/web/src/app/lib/api/decision-support.test.ts` and root `pnpm typecheck`; record final exits and specific failure attribution in `specs/023-decision-ism/validation.md`, without treating known unrelated errors as a pass.
- [X] T072 Run final persisted EN/FA ISM and existing AHP Playwright suites using `apps/web/e2e/playwright.config.ts`, `apps/web/e2e/tests/decision-ism.spec.ts` and `apps/web/e2e/tests/decision-ahp.spec.ts`; include real SAW/TOPSIS mixed-method smokes in the ISM suite, retaining browser exits/reports/traces in `specs/023-decision-ism/validation.md`.
- [X] T073 Run `makemigrations --check --dry-run` through `apps/api/core/manage.py` and verify pinned runtime versions; record no expected schema migration and preservation limits in `specs/023-decision-ism/validation.md`, without resetting any database.
- [X] T074 Measure SC-008 through the real browser flow in `apps/web/e2e/tests/decision-ism.spec.ts` per `specs/023-decision-ism/quickstart.md`: at least 40 valid trials per documented locale/normal environment, execution POST dispatch→visible returned-run layers, include n=10 sparse/dense networks and failures, require ≥95%≤2000 ms; save raw durations/environment and median/p95 in `specs/023-decision-ism/validation-performance.json` and `specs/023-decision-ism/validation.md` (exclude preparatory PATCH/entry time).
- [X] T075 Reconcile all FR-001–FR-018 and SC-001–SC-008 against final numerical/API/helper/type/migration/browser/timing evidence in `specs/023-decision-ism/validation.md`; leave unproven checks/tasks explicitly open and distinguish reference design exercises from application acceptance.
- [X] T076 Review final scoped diff against the T001 baseline, run whitespace/link/format checks for `specs/023-decision-ism/tasks.md` and evidence artifacts, and record preserved unrelated AHP/DEM/spec/plan work in `specs/023-decision-ism/validation.md`; summarize any actual limitations without committing/pushing or claiming acceptance from task markers.

## Dependencies and Execution Order

### Phase graph

```text
Setup T001–T003
       ↓
Foundation T004→T005, T006→T007, T008→T009, T010→T011
       ↓
US1 T012–T028 (MVP)
       ↓
US2 T029–T043 (draft correction and pair identity)
       ↓
US3 T044–T054 (cycle explanation and frozen review)
       ↓
US4 T055–T067 (complete bilingual/access/pending proof)
       ↓
Final T068–T076
```

The execution order reflects shared source/test files and integration needs, not method chaining. Every story has its own independently verifiable scenario; US2 builds on the US1 engine/editor, US3 on persisted runs, and US4 verifies the integrated workspace. Do not declare these whole phases parallel merely because their assertions are separable.

### Important task dependencies

| Slice | Test/evidence prerequisite | Implementation/green |
| --- | --- | --- |
| Strict inputs | T004 | T005 |
| Finite storage/isolation | T006 | T007 |
| Shared mutation boundary | T008 | T009 |
| Shared permission presentation | T010 | T011 |
| Exact computation/API | T012,T013 | T017→T018→T019 |
| Input helpers/guard/editor | T014,T015,T016 | T020,T021→T022,T023→T024→T025→T026→T027,T028 |
| Draft recovery | T029 | T033,T037→T042,T043 |
| Operation metadata/remap | T030,T031,T032 | T034→T035→T036→T041,T043 |
| Pair errors/failures | T031 | T037,T038→T039→T040→T043 |
| Cycles/frozen history | T044,T045,T046,T047 | T048→T049,T050→T051→T052→T053,T054 |
| Authorization | T055 | T059,T062→T065 |
| Keyboard/locale | T056,T057 | T060,T063→T064,T066 |
| Late-operation isolation | T058 | T061,T062→T067 |
| Final acceptance | All story checkpoints | T068–T074→T075→T076 |

T055 and T057 may run together after US3. T056 and T058 both modify the browser suite and must run sequentially. All shared backend/frontend source edits are sequential; `[P]` labels apply only to the named independent test batches. Tests already green at introduction are recorded as regressions, while missing behavior still needs real red before its fix.

## Parallel Execution Examples

These are ready-file batches, not instructions to spawn agents or bypass prerequisite/red gates.

| Story | Ready batch (distinct files) | Follow-up |
| --- | --- | --- |
| US1 | T012 service tests; T013 API tests; T014 input helpers; T015 result guard tests; T016 browser scenarios | After red, implement the linked slices; T017 before T018, T020/T021 before integrated panel |
| US2 | T029 API recovery; T030 remap helpers; T031 browser flows; T032 named-list metadata tests | Metadata T034 precedes remap T035 and route T036; one owner edits the browser suite |
| US3 | T044 service cycle regressions; T045 immutable run tests; T046 frozen browser review; T047 result guards | Guard T048 before viewer/list; do not fabricate failures for correct engine/history behavior |
| US4 | T055 server access and T057 locale/architecture audits | Run T056 then T058 separately; T060/T061/T062 share components/route and are not parallel |

## Implementation Strategy

### MVP first

Complete Setup and Foundation, then US1. Demonstrate the independent chain/diamond/all-zero/single cases and mixed-method preservation with real API/browser output. This is a bounded MVP, not full ISM acceptance; public completion still requires US2–US4 and final evidence.

### Incremental delivery

Add US2's recoverable drafts/operation identity, US3's cycle/history explanation and US4's full bilingual/permission/pending proof. Keep prior focused and mixed-method regressions green after every shared change. Preserve explicit task evidence, then run final checks once the tree is stable; repeat only after new changes/failures.

### Contract and entity mapping

| Artifact/entity | Primary tasks/stories |
| --- | --- |
| Inputs/API contract; live case/direct relations | Foundation T004–T007; US1 T013,T018,T020–T025; US2 T029–T043; US4 T055,T059,T065 |
| Result contract; reachability/structural layers | US1 T012,T015,T017,T021,T023,T027; US3 T044,T047–T049,T053 |
| Immutable execution/provenance | US1 T013,T018,T019; US3 T045,T050,T051,T053,T054 |
| Mutual groups and interpretation | US1 T017; US3 T044,T046–T054 |
| UI contract; ephemeral identity/current result/coordinator | Foundation T008–T011; US1 T014–T016,T022–T026; US2 T030–T040; US4 T056–T067 |

### Requirement and outcome traceability

| Coverage | Task IDs |
| --- | --- |
| FR-001 / SC-001 independent execution | T012,T013,T017–T028 |
| FR-002 name/count/shape | T004,T005,T029,T042 |
| FR-003 / SC-003 binary validation and valid zeros | T004–T007,T012,T029,T037–T043 |
| FR-004 draft/pair preservation | T006,T007,T014,T020,T029–T043 |
| FR-005 identity without direct mutation | T012,T013,T017–T019,T027 |
| FR-006 full closure | T003,T012,T017,T027,T044,T053 |
| FR-007 active sets | T012,T017,T044,T053 |
| FR-008 / SC-002 exact extraction/assignment | T012,T017,T027,T044,T053 |
| FR-009 ordered structural meaning | T012,T017,T023,T046,T049,T052,T054 |
| FR-010 / SC-004 maximal groups/no false groups | T017,T044,T046–T049,T052–T054 |
| FR-011 direct/derived/layers/groups visible | T023,T046,T049,T050,T054 |
| FR-012 immutable distinct execution | T013,T018,T019,T045,T053 |
| FR-013 frozen edit/rerun/locale history | T045,T046,T050–T054,T056,T066 |
| FR-014 / SC-005 other-method/frozen preservation | T007,T013,T018,T027,T028,T041,T042,T045,T053,T054 |
| FR-015 locatable failure/no stale success | T004–T007,T024,T029,T031,T033,T037–T040,T043,T058,T067 |
| FR-016 / SC-007 access/isolation | T010,T011,T055,T059,T062,T065 |
| FR-017 EN/FA labels/dates/stable identity | T026,T039,T043,T052,T054,T056,T057,T063,T064,T066 |
| FR-018 / SC-006 keyboard/pending/late-case safety | T008–T011,T024,T025,T030–T038,T043,T056,T058,T060–T067 |
| SC-008 visible result latency | T074,T075 |

## Notes and completion limits

76 tasks: Setup 3, Foundation 8, US1 17, US2 15, US3 11, US4 13, Final 9. There are 15 `[P]` test tasks across four story batches. Checklist format, ID order, story labels, dependencies and FR/SC mapping are checked at generation; application tests have not run in this tasks phase. No automatic commit, push, deployment or human acceptance is implied.


## Phase 8: Convergence

Assessed current code against all 76 existing tasks, FR-001–FR-018, SC-001–SC-008, 23 user-story acceptance scenarios, 12 edge cases, 17 grouped plan obligations and the seven constitution principles. This assessment used source inspection, read-only replay of the actual coordinator/error callbacks and Django JSON-field preparation, plus existing numerical/API/browser/timing evidence; no new API mutations or full test reruns occurred. Existing 200 backend, 66 frontend and 54 browser passes do not cover the three gaps below. Existing unrelated typecheck failures remain outside this feature's remediation scope. No application/spec/plan/checklist changes are made by convergence.

- [X] T077 [US4] Close F1 (HIGH): add meaningful failing EN/FA browser cases in `apps/web/e2e/tests/decision-ism.spec.ts` that hold each AHP/SAW/TOPSIS/ISM PATCH→POST or global PATCH pending, reselect its current case and navigate A→B→A before completion; assert no second same-case save/run and no writable captured-case controls while allowing independent case B and history reads. Repair the per-project/case pending identity in `apps/web/src/app/routes/project-decision-support.tsx` and only necessary method adapters so `hydrateFromCase` cannot discard an outstanding case's guard, and its eventual release updates that case without clearing another gate or attaching stale callbacks. Keep captured variables and existing algorithms unchanged; retain red→minimal fix→green and focused mixed-method/AHP regression evidence in `specs/023-decision-ism/validation.md` per FR-018, US4/AC5, plan: same-case synchronous coordinator/captured-case pending isolation and T009/T061 (partial).

- [X] T078 [US2] Close F2 (HIGH): add failing PostgreSQL/API tests in `apps/api/core/decision_support/tests/test_ism_api.py` for explicit root `ism_matrix:null` on create, matrix-only PATCH and a general/shared-field PATCH, plus correction of a persisted JSON-null root and an execution attempt that appends zero runs. Repair `apps/api/core/decision_support/services/validators.py` and `apps/api/core/decision_support/services/case_service.py` so root null has deliberate, consistent recoverable handling under the existing JSON schema: no unhandled SQL-NULL/not-null failure, no silent replacement by an empty/default matrix, and locatable coded feedback if a save cannot retain the malformed value. Preserve null cells as valid unfinished drafts, missing-field/empty-legacy initialization, unrelated finite-invalid method inputs and shared ranking boundaries; no schema/dependency change. Verify correction/reset in EN/FA through `apps/web/e2e/tests/decision-ism.spec.ts`, rerun AHP draft regressions and record actual outcomes in `specs/023-decision-ism/validation.md` per FR-004, FR-015, US2/AC1/AC6, plan: raw malformed draft recovery and T029/T033/T037 (contradicts).

- [X] T079 [US2] Close F3 (HIGH): add failing EN/FA browser coverage in `apps/web/e2e/tests/decision-ism.spec.ts` that forwards an ISM POST to the real server, loses only its response after the run commits and delays/fails the subsequent history GET; assert preserved input, cleared current result, an authoritative history recovery attempt before an explicit retry, and no automatic POST retry. Complete bounded recovery/pending feedback in `apps/web/src/components/decision-support/IsmMethodPanel.tsx` and only necessary coordinator/localization touch-points so the current fire-and-forget `invalidateQueries` after `finally` release cannot expose an immediate run button before recovery settles; keep another case isolated and history readable, and report unresolved history lookup failures explicitly. Retain normal denial/network recovery and no idempotency/revision guarantee; rerun focused failure/pending scenarios, then relevant final backend/helper/type/migration/EN-FA ISM/AHP browser checks and visible-result timing if changed behavior affects that boundary. Reconcile these three findings against final evidence in `specs/023-decision-ism/validation.md` per FR-015, US2/AC6, plan: ambiguous lost-response recovery, UI contract: inspect/refetch history before explicit retry and T040/T067/T075 (partial).


## Phase 9: Convergence

Assessed the current implementation against all 79 existing tasks, FR-001–FR-018, SC-001–SC-008, 23 user-story acceptance scenarios, 12 edge cases, 17 grouped plan obligations and seven constitution principles. Current source inspection and read-only replay of the actual API helper, ISM mutation callbacks and React Query cache confirm the two remaining HIGH partial gaps below. Retained 205 backend, 66 frontend and 64 browser passes include the prior T077–T079 fixes but do not cover malformed successful HTTP responses or recovery with an active filtered/paginated history. No full suites or live API mutations were run in this assessment. Existing unrelated typecheck errors remain outside this remediation scope. Complete T080 before T081 because they share the panel and browser suite; preserve all earlier tasks and artifacts.

- [X] T080 [US2] Close F4 (HIGH): add meaningful failing EN/FA cases in `apps/web/e2e/tests/decision-ism.spec.ts` and focused response-boundary coverage in `apps/web/src/app/lib/api/decision-support.test.ts` for empty/non-JSON/truncated and structurally invalid successful responses to ISM PATCH 200 and POST 201, including a real committed POST whose response alone is replaced. Current `jsonOrThrow` in `apps/web/src/app/lib/api/decision-support.ts:110` accepts malformed successful JSON as `{}`; current `IsmMethodPanel.tsx:143–156` releases before checking the returned envelope and dereferences `value.input_snapshot.criteria` without an envelope guard. Repair only necessary parsing/envelope handling in `apps/web/src/app/lib/api/decision-support.ts` and `apps/web/src/components/decision-support/IsmMethodPanel.tsx`: an unconfirmed save must not update saved-case metadata or send POST; validate the returned run envelope/method/frozen input and existing structural result inside the acquired operation, before release; route an unconfirmed successful POST through the existing bounded authoritative history recovery before explicit retry. Preserve draft input, clear current output, show localized failure/recovery feedback, avoid callback TypeErrors and automatic POST retry, retain case-switch isolation and valid raw draft/legacy-history compatibility, and leave scientific computation server-only. Record actual red→minimal fix→green, failed-save zero-POST and committed-run no-duplicate evidence in `specs/023-decision-ism/validation.md`, including delayed/failed recovery and existing AHP/shared-helper regressions per FR-015, FR-018, US2/AC6, plan: recoverable save/run failure and structural guarding, UI contract: malformed-response handling/history before explicit retry, T021/T024/T031/T040/T048/T079 (partial).

- [X] T081 [US3] Close F5 (HIGH): add failing real EN/FA lost-response browser scenarios in `apps/web/e2e/tests/decision-ism.spec.ts` with the displayed history filtered to ISM and with a non-first history page. Forward the POST to commit once, lose only its response, and hold the recovery GET; assert that the committed run and accurate history count become inspectable in the visible recovery history before another explicit attempt, with the displayed filter/page matching that authoritative result. Current `IsmMethodPanel.tsx:62–93` invalidates without active refetch and fetches only `["decision-runs", projectId, caseId, "", 1]`, while `project-decision-support.tsx:116–119` displays the selected filter/page key: actual React Query replay leaves the active ISM-filtered count at 1 and its old row while the unfiltered recovered count is 2 and status is `refreshed`. Make the minimal panel/route coordination in `apps/web/src/components/decision-support/IsmMethodPanel.tsx` and `apps/web/src/app/routes/project-decision-support.tsx` so recovery either updates the displayed history or explicitly selects its authoritative first page, without claiming refreshed visible history while it remains stale. Keep recovery bounded, failed/timeout lookup feedback explicit, historical data frozen, other cases isolated, and POST retry strictly manual; add localization only if the chosen visible transition needs it. Retain red→minimal fix→green and filtered/paginated delayed/failure/isolation outcomes in `specs/023-decision-ism/validation.md`; after T080/T081, rerun relevant final backend/helper/type/migration and EN/FA ISM/AHP browser checks, refresh visible-result timing if its boundary changes, and reconcile both findings against final evidence per FR-012, FR-013, FR-015, US2/AC6, US3/AC4, plan: filtered frozen history and ambiguous lost-response recovery, UI contract: inspect/refetch history before explicit retry, T040/T051/T067/T075/T079 (partial).
