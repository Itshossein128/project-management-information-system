# Research: Independent ISM Criterion Layering

**Date**: 2026-10-12 | **Feature**: [spec.md](spec.md)

Research inspected the current worktree, including existing uncommitted AHP changes. Two read-only research agents reviewed backend and frontend integration. DEMATEL and ISM remain placeholders; the DEMATEL design is not an implementation dependency. No application tests or implementation acceptance are claimed by this artifact.

## 1. Exact reachability and layer extraction

**Decision**: Use a pure Python service with Boolean Floyd–Warshall closure. Validate first, copy the accepted direct matrix, set derived self-relations to one, then complete paths with intermediate index outermost. Emit integer zero/one cells. Extract each layer simultaneously using `Reach_active(i) == Reach_active(i) ∩ Antecedent_active(i)`; restrict both sets to the same remaining indices every round. Preserve original order and number layers from one.

**Rationale**: Matches [the requested method](../../docs/decision-support/07-ism.md) and the reachable/intersection level-partitioning condition checked in [Chen's primary publication](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254694). A chain yields C, B, A; using reachable/antecedent equality instead would fail this rule. Binary self-inclusion avoids creating diagonal twos. At n≤10, O(n³) work and O(n²) memory need no numerical dependency or tolerance policy.

**Alternatives considered**: Repeated Boolean powers are correct but introduce an unnecessary stopping rule; numeric matrix addition/multiplication risks nonbinary output; client-side analysis duplicates the authoritative service. No DEMATEL threshold conversion, inversion or weight calculation is used.

## 2. Cycles and interpretation policy

**Decision**: Derive maximal mutually reachable equivalence classes from the full closure: two indices share a class exactly when each reaches the other. Omit singleton classes; attach every remaining group to its common layer. Group order is layer then first original member index; member order is original criterion order. Render numbered layers with explicit group labels, not a diagram.

**Rationale**: These classes are strongly connected components; a finite component condensation has a sink each extraction round, including cyclic input. Cycles are valid. Same-layer disconnected criteria and identity alone do not imply a group. This implements the spec's explicit O10 working policy without claiming the source settled presentation.

**Alternatives considered**: Rejecting cycles or splitting their members would change the entered network. A separate Tarjan implementation or graph library duplicates information in the closure. Existing graph dependencies do not justify diagram/layout scope.

**Defensive boundary**: No-progress, more than n rounds, missing/duplicate assignment or a group spanning levels indicates an internal derivation failure, not an invalid-cycle rule. Fail without appending a partial run.

## 3. Independent storage and strict execution

**Decision**: Reuse `DecisionCase.ism_matrix` and `DecisionRun.input_snapshot/result` in `apps/api/core/decision_support/models.py`; add `services/ism_service.py` and method-specific validators. No model, migration, endpoint, permission or dependency addition is planned. Execute only finite native numeric 0/1, excluding bool/text; accept 0.0/1.0. Direct diagonal 0 or 1 is editable and valid; all-zero networks are valid.

**Rationale**: Generic serializers already expose ISM storage. `services/execution_service.py` currently dispatches ISM to a criteria-only stub. Existing shared name normalization is trim plus exact uniqueness; preserve it, while strict execution checks string identities and full shape/type/value before indexing.

**Alternatives considered**: A separate run model or external graph service would duplicate the domain. AHP reciprocal/diagonal rules and DEMATEL scale/all-zero rules are incompatible with ISM.

## 4. Recoverable drafts and method isolation

**Decision**: Extend `services/case_service.py` and `validators.py` with ISM finite-storage protection and ISM-only matrix PATCH isolation. Incomplete, malformed-shape and finite invalid judgments may remain drafts; strict executable validation belongs to run creation. Reject actual nonfinite/overflow numbers before JSON persistence. Recover malformed persisted ISM containers without calling `list()` on scalars or silently replacing them with an empty/zero matrix. Preserve raw invalid values until a deliberate correction.

**Rationale**: The current finite draft guard and matrix-only bypass cover AHP only. `_case_dict` currently converts ISM to a list and can crash on a scalar. `test_ahp_api.py` deliberately preserves unrelated `ism_matrix: [[9]]`; AHP-only saves/runs must still do so. A genuine shared criterion dimension change must retain existing ranking validation boundaries; do not broaden matrix-only isolation into a bypass for other fields.

**Alternatives considered**: Enforcing completeness on every save prevents unfinished drafts; coercing missing/text/bool to zero changes relationships; validating every method during any PATCH breaks independent correction.

## 5. Authoritative immutable execution and access

**Decision**: Normalize/check method ID, then dispatch ISM before checking method selection on a potentially stale case object. Inside an ISM-only atomic helper, reload an active case through `select_for_update`, scoped by both project and case ID; recheck selection, validate/compute, deep-copy input and append the run in that transaction. Preserve existing other-method paths.

**Rationale**: Current `create_run` can calculate from stale state. Existing case updates/soft deletion contend on the same PostgreSQL row. Calculation and snapshot must reflect one authoritative state. Existing `view_decision_support` / `edit_decision_support`, membership, administrator policy and nested scoped routes remain the security boundary; no separate run permission exists.

**Alternatives considered**: Copying the caller instance can freeze stale input; an unlocked reload leaves a race; locking all methods would expand scope. PATCH and POST remain separate requests and offer no cross-client revision guarantee. Returned frozen input is authoritative, including an intervening valid save.

## 6. Binary editor and criterion identity

**Decision**: Add `BinaryRelationEditor.tsx` with native selects for unanswered/null, absent/0 and present/1. Initialize new diagonals to zero and off-diagonals to null. Add optional operation/index metadata to `NamedListEditor`; ISM helpers remap both axes by rename/move/add/remove operations, without persistent criterion IDs.

**Rationale**: No binary or DEMATEL editor exists. `SquareMatrixEditor` contains AHP labels/paths and reciprocal/diagonal behavior. Named-list callbacks currently provide only names; name matching cannot preserve ISM relationships while a name is typed. Existing AHP intentionally clears renamed pairs and must keep that behavior.

**Alternatives considered**: A general square-editor ISM mode is possible but adds AHP branches; stable database criterion IDs are unnecessary for a ten-item ordered input. Never use truthiness or `Number('')` to map select values. Invalid persisted text/bool/shape needs an explicit recoverable invalid state, not a blind `(number|null)[][]` cast.

## 7. Shared permission and pending operations

**Decision**: Introduce a small route-owned operation coordinator and minimal permission/pending adapters in `AhpMethodPanel`, `SawMethodPanel` and `TopsisMethodPanel`. Global save and every same-case method save/run acquire the same synchronous busy gate, freeze submitted variables and release in `finally`. Key panels by project/case, invalidate late callbacks after selection/unmount, and disable writable controls while busy or view-only. History remains inspectable.

**Rationale**: The route currently omits ISM hydration/save and permission gating; all three panels independently perform PATCH→POST. A wrapper cannot observe an already-started panel mutation. SAW/TOPSIS also lack AHP's keyed/unmount safeguards. ISM must build the minimum host support itself; if DEMATEL later supplies compatible support, reuse it instead of duplicating coordinators.

**Alternatives considered**: An ISM-only pending flag cannot satisfy mixed-method isolation. A broad global state rewrite is unnecessary. No algorithm or existing other-method input semantics change is planned.

## 8. Result/history and localization

**Decision**: Use the exact [result contract](contracts/ism-result.md): server reachability, named ordered layers and explicit named groups, plus versioned derivation policy. Add a structural result guard and render frozen snapshot labels in `IsmLayerList` and `InputSnapshotViewer`. Reuse generic history/filter/date behavior. Add EN/FA relation, error, layer/group and interpretation text and directed cell focus.

**Rationale**: Unique frozen names are sufficient membership identifiers; no duplicate parallel index/name arrays are needed. Display guards check structure/member references without recomputing analysis. Legacy ISM stubs stay unavailable computations. Relevant draft edits/new attempts/failures clear current-result presentation, while previous successful history remains available.

**Alternatives considered**: Grouping adjacent rendered rows confuses shared levels with mutual reachability; live case labels corrupt frozen provenance. Client-side derivation or upgrading old stubs invents historical results.

## 9. TDD and acceptance evidence

**Decision**: Deliver meaningful failing tests before each new validator, calculation, API/persistence, editor and browser slice, then minimal fixes and focused green checks. Use literal small-network expectations plus a test-only traversal oracle independent of production Warshall. Add PostgreSQL concurrency/scoping tests, helper tests, real EN/FA browser flows and request-to-visible-result timing.

**Rationale**: Source audits and helper tests cannot prove structural correctness, authorization, keyboard interaction or the two-second outcome. Existing suites must preserve AHP's unrelated invalid-ISM draft fixture and DEMATEL-stub mixed history. No current test was found that relies on executing an ISM stub.

**Alternatives considered**: Generating expected results with production computation is circular. Synthetic service timing alone excludes API/UI latency. All commands and evidence categories are specified in [quickstart.md](quickstart.md).

## Planning verification

An isolated standard-library reference exercise checked 732 graphs: exhaustive binary matrices for n=1,2,3, 100 deterministic random networks each for n=4 and n=10, and ten-criterion chains with each diagonal policy. Boolean Warshall closure matched independent traversal reachability; reachable/intersection layers matched independently peeled sink components. This supports the chosen design rule only: it did not import or test an application ISM service and establishes no API, browser or performance acceptance.

All design unknowns are resolved within the approved specification assumptions. No implementation acceptance or performance pass is claimed.
