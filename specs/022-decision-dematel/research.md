# Research: Independent DEMATEL

**Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

Research is based on the current dirty worktree, including completed AHP convergence edits. Two read-only research agents inspected backend and frontend integration. No application tests or implementation changes were made during planning. All design questions below are resolved.

## 1. Extend the existing case/run domain

**Decision**: Use existing `DecisionCase.dematel_matrix`, `METHOD_IDS`, generic serializers, project-scoped case/run routes, and frozen `DecisionRun` JSON. Add `services/dematel_service.py` and an explicit DEMATEL execution branch before the criteria-method placeholder branch.

**Rationale**: `models.py`, `serializers.py`, and `_snapshot_from_case` already include DEMATEL. Only its calculation and UI are missing; `execution_service.py` currently returns `status: stub` for DEMATEL. Existing read/edit permissions are `view_decision_support` and `edit_decision_support`; execution uses edit permission, not a new run codename.

**Alternatives considered**: New models/endpoints/permissions would duplicate working tenancy and history. Schema migration and rewriting old stubs are unnecessary. Preserve historical stubs as unavailable calculation results.

## 2. Separate recoverable drafts from executable judgments

**Decision**: Draft saves retain blanks and recoverable finite invalid values, following AHP draft behavior. Reject numeric NaN/infinity/overflow before JSON storage. Execution strictly requires 1–10 trimmed unique names, native numeric cells excluding booleans, exact n×n list shape, inclusive 0–4 values, and exact zero diagonal. Numeric text and localized digits are parsed in the existing frontend input boundary, not accepted as executable numeric strings by the service.

**Rationale**: Incomplete inputs must be saveable without recording false success. `case_service.py` only guards AHP draft numbers and only isolates AHP-only PATCH from unrelated ranking validation. Extend that behavior for DEMATEL; write requested fields only. A DEMATEL-matrix-only patch must not normalize or validate unrelated ranking drafts.

**Alternatives considered**: Full execution validation on every save would prevent iterative correction. Coercing empty strings to zero or booleans to numbers would corrupt judgment meaning. Global changes to ranking validation are out of scope. Guard malformed legacy draft containers during normalization/recovery rather than crashing on `list(scalar)`.

## 3. Evaluate the required model with existing NumPy

**Decision**: Use installed NumPy float64, already declared as `numpy>=1.26.0`; research runtime is NumPy 1.26.4 / Python 3.12.3. Calculate s as the maximum accurately summed direct-influence row. Reject exactly s=0, not a small-value epsilon. Set N=X/s and A=I−N. Evaluate the source T=N×A⁻¹ through `numpy.linalg.solve(A.T, N.T).T`, solving T×A=N without constructing an inverse.

**Rationale**: The algebra preserves the domain formula; the existing dependency handles a small dense system with at most ten criteria. [NumPy solve documentation](https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html) specifies a full-rank square system and singular exceptions. [Chen's method description](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254694) supports the source's maximum-row-sum normalization and total relations.

**Alternatives considered**: A hand-written inverse duplicates numerical library behavior. A pseudoinverse, damping, alternative scaling, or a truncated series changes the required calculation and must not silently produce a substitute result.

## 4. Declare numerical reliability policy

**Decision**: Use the explicit policy in [calculation/result contract](contracts/dematel-result.md): singular solve failure; nonfinite condition or cond₂(A)>10⁸; normalized right-solve residual>10⁻¹⁰; nonfinite outputs; materially negative total relations all block success. Use absolute relation tolerance 10⁻⁹ for neutral roles, as specified. Preserve signed unrounded relation. Use accurate sums for D/R and all indicators.

**Rationale**: [NumPy inverse documentation](https://numpy.org/doc/stable/reference/generated/numpy.linalg.inv.html) warns that ill-conditioned computations can be inaccurate without raising. [Condition-number documentation](https://numpy.org/doc/stable/reference/generated/numpy.linalg.cond.html) supplies the SVD-based 2-norm estimate. Thresholds are conservative feature policy, not proof of component accuracy. Independent rational/high-precision fixtures must verify SC-002, including accepted near-boundary networks.

**Alternatives considered**: Catching singular exceptions alone accepts unreliable finite results. Rejecting every zero row/column would incorrectly reject valid sparse networks. A minimum influence epsilon would incorrectly reject uniformly tiny but valid judgments.

## 5. Freeze coherent authoritative input

**Decision**: For DEMATEL execution, atomically reload and row-lock the authorized project case before rechecking selected method, validating, computing, snapshotting, and appending. Derive both result and snapshot from that single authoritative case state. Do not modify other method calculations. Keep the existing POST method-only request; it runs the saved case state at lock acquisition.

**Rationale**: Passing a stale model instance to execution can mismatch the latest saved case. The snapshot must match the computation. A client save followed by run is not an atomic transaction across requests or across editors; its returned frozen snapshot remains the authoritative provenance.

**Alternatives considered**: Client-provided results undermine the trust boundary. New optimistic-revision schema/API is unnecessary for this feature. A transaction without a reload/lock does not establish the authoritative case snapshot. Avoid claiming that a separate PATCH and POST guarantees no intervening user edit.

## 6. Extend shared UI with explicit DEMATEL behavior

**Decision**: Add a `dematel` matrix mode, a `DematelMethodPanel`, a `DematelResultTable`, and pure directed-matrix helpers. General-mode matrix code still contains AHP text, paths and diagonal assumptions, so merely choosing existing general mode is insufficient. Defaults are zero diagonal and null off-diagonal; edits affect only the chosen directed cell. Reuse existing request-issue parser, run action bar, and locale-aware history list.

**Rationale**: Additive mode-specific behavior retains working AHP reciprocity, advisory text and tests. The client renders server D/R/prominence/relation/roles without inversion, indicator calculation, or weight conversion.

**Alternatives considered**: A separate table duplicates accessibility/validation markup. Client-side DEMATEL calculation and causal diagrams are unnecessary and outside scope.

## 7. Preserve DEMATEL pairs during rename and pending actions

**Decision**: Add optional operation/index metadata to `NamedListEditor` callbacks; use index mappings for DEMATEL rename/move/add/remove. Keep AHP's existing name-based reconciliation. Introduce one same-case mutation coordinator for global save and every method panel's save/run; deep-copy submitted drafts, disable relevant controls while pending, ignore results for unmounted/switched cases, and invalidate the current DEMATEL result after draft changes/start/failure. Add minimal permission/pending/coordinator adapters to `AhpMethodPanel`, `SawMethodPanel` and `TopsisMethodPanel` without changing their algorithms or input semantics.

**Rationale**: AHP intentionally clears renamed comparisons, while DEMATEL FR-005 requires retention. Matching solely by trimmed names cannot satisfy both. Existing AHP fields remain editable during pending; route guards selection changes but not every draft revision. AHP/SAW/TOPSIS independently perform PATCH→POST, so a DEMATEL-only coordinator would not observe an already pending other-method save. Shared adapters enforce view-only mixed-method controls and prevent overlapping same-case mutations. DEMATEL must explicitly avoid stale-current-result presentation.

**Alternatives considered**: Persistent criterion IDs need a schema redesign; changing AHP rename semantics would break its established contract. Merely disabling the run button leaves global-save and case-switch races open.

## 8. Evidence and compatibility

**Decision**: Require red→green TDD by slice, full Decision Support backend regression, helper/key/source tests, and actual EN/FA browser scenarios. Update the AHP mixed-history fixture that currently inserts a DEMATEL stub without judgments: use a valid DEMATEL input or the remaining ISM stub, retaining count/scoping assertions. Old successful stubs remain unchanged and display unavailable.

**Rationale**: Source-only checks cannot prove input focus, permissions, stale results, localization, history or numerical correctness. No application acceptance result is claimed by this planning step.

**Numerical research evidence**: An isolated NumPy calculation of the required chain reproduced T, D and R exactly, with cond₂(A)≈3.010643. A two-criterion normalized loop with reverse influence 1−10⁻⁶ has condition≈4.0×10⁶; 1−10⁻⁹ has condition≈4.0×10⁹. This checks design fixtures only, not an implemented DEMATEL service.
