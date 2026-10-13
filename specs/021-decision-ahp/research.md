# Research & Decisions: AHP Criteria Weighting

**Feature**: `021-decision-ahp` | **Date**: 2026-10-11 | **Inspected tree**: `develop`, `c5328c4`

Backend/frontend research used the existing Graphify graph for navigation and current source for verification. The truncated graph query located models, engine, validators, views and panels; it is not completeness evidence. All planning unknowns below are resolved. O05/O06 remain interim product policies.

## 1. Reuse implemented behavior

**Decision**: correct the existing AHP engine, endpoint, fields and components.

**Rationale**: `apps/api/core/decision_support/services/ahp_service.py` already implements geometric means/RI/CI/CR; `execution_service.py` executes AHP; `models.py` has matrix/snapshot/result fields. `apps/web/src/components/decision-support/{AhpMethodPanel,SquareMatrixEditor,CriteriaWeightTable}.tsx` already exist. The spec gap table/old plan describe an earlier tree.

**Alternatives considered**: another engine/workspace duplicates behavior and violates Constitution V. Spec/tasks are left intact during planning; regenerate tasks separately.

## 2. Numerical semantics and safety

**Decision**: retain row geometric means and the spec's mean `(A*w)[j]/w[j]` lambda approximation, fixed interim RI table and warning threshold. Use log-domain geometric means where necessary to avoid product overflow/underflow; guard unrepresentable results with coded validation rather than non-finite JSON/HTTP 500. All engine formulas remain in `ahp_service.py`.

**Rationale**: `docs/decision-support/05-ahp.md` selects geometric means; the feature spec supplies CI/CR details. The approximation need not equal the exact principal eigenvalue for arbitrary inconsistent matrices. Existing direct multiplication can overflow with extreme finite values. Service/validator imports use existing Django error machinery, but numerical execution performs no DB/HTTP work.

**Alternatives considered**: eigenvector/NumPy/SciPy substitutions change the selected method and add dependencies. Avoid unsupported universal rank-reversal or exact-eigenvalue claims.

**External reference**: [Saaty, Decision making with the analytic hierarchy process (2008)](https://www.inderscience.com/info/inarticle.php?artid=17590) establishes the pairwise-judgment/inconsistency context. The repository spec, rather than the article abstract, defines this phase's formulas/RI constants.

## 3. Types, diagonal and tolerance

**Decision**: follow FR-005: actual finite positive numbers excluding booleans/strings; exact diagonal equality to 1; `abs(a[j][k]*a[k][j]-1) < 1e-4`. Require actual string criterion names, trimmed exact uniqueness and 1..10 size. Paths are zero-based.

**Rationale**: `services/validators.py` currently parses numeric strings and tolerates diagonal error. Read-only probes accepted `[["1"]]` and `[[1.00005]]`. Interim spec prose uses inverse-difference tolerance; FR-005 is the explicit acceptance rule. Product residual is symmetric in pair direction. Null/blank string remain `cell_empty`; nonblank strings/bools are `non_numeric`.

**Alternatives considered**: retain coercion/diagonal epsilon or combine two tolerance rules, causing contradictory acceptance. Tighten AHP validation only; add asymmetric product-boundary and near-diagonal tests.

## 4. Scale interpretation

**Decision**: provide Saaty presets 1..9 and reciprocals 1/2..1/9 plus custom finite positive numbers. Values outside [1/9,9] show localized advisory feedback for the pair, not a new hard server cap. Numerical representability is a separate guard.

**Rationale**: FR-005 specifies positivity/finiteness without a hard maximum; assumptions/edge cases disagree on `(0,10)` versus `(0,10]` and leave reject/warn unspecified. Warning preserves permitted flexibility. A one-sided cap would reject the reciprocal of an otherwise allowed small decimal.

**Alternatives considered**: exact presets only, cap at 9/10 or cap one triangle. These remove decimal flexibility or break symmetry. Permanent scale governance can be specified separately.

## 5. Output order and ordinal ranks

**Decision**: new result rows follow frozen criteria order. Compute rank separately by descending weight, stable input-index tie-break; ranks are an ordinal permutation 1..n even with ties. No automatic transfer.

**Rationale**: source doc05 requires input order; current service sorts result rows. A reversed-importance probe confirms drift. Historical stored rows retain original order and identify their criteria by name.

**Alternatives considered**: keep sorted output or introduce shared competition ranks; both diverge from source/ordinal semantics without need.

## 6. Persistence, permissions and saves

**Decision**: reuse existing URLs and membership checks; `view_decision_support` for reads, `edit_decision_support` for saves/runs. Retain full deep-copied snapshot superset. Add optional method filter before run-list pagination. Resolve runs through both authorized case and project. Retain HTTP 400 `run_immutable` for API mutation attempts.

**Rationale**: actual permission codes live in `apps/api/core/permissions/constants.py`/`decision_support/views.py`; spec assumption names are absent. Calculation and snapshot use one loaded case instance before one final insert. No additional revision-order requirement exists. Models/DB do not enforce immutability against arbitrary ORM writes.

**Alternatives considered**: new permission codes/AHP-only endpoint, removing snapshot fields or claiming DB-level immutability. These change interfaces or overstate evidence. Separate save/run HTTP requests are not a single atomic draft execution; a run records persisted inputs at its own read.

**Save decision**: send only changed AHP fields. Matrix-only updates preserve unrelated fields and bypass unrelated ranking revalidation; real shared criteria changes retain established cross-method consistency checks. Use targeted writes from freshly scoped case state rather than replacing unrelated stale fields. Test matrix-only save alongside raw ranking inputs and incomplete ranking drafts.

## 7. Matrix and case-result lifecycle

**Decision**: parent owns actual matrix; diagonal 1, unjudged off-diagonal null. Reconcile criteria by trimmed exact name and order, preserve surviving comparisons, leave new/renamed pairs blank. Never silently overwrite saved malformed values as equality. Reset results/errors/history selection on case changes and guard late responses.

**Rationale**: `SquareMatrixEditor.tsx` renders all-ones defaults without updating parent state; n=1 cannot run fresh and the first off-diagonal edit invents other judgments. Route criteria edits do not reconcile AHP matrix. Panel result effect depends only on `latestResult`, so null-to-null case switching can retain the previous case's local result.

**Alternatives considered**: all-ones defaults, resetting every comparison or independent parent/component matrices. These hide missing input, discard judgments or repeat the state mismatch.

## 8. History, accessibility and math boundary

**Decision**: method-selected paginated history; historical input/result read-only and distinct from editable draft. Reuse tables/viewers, add fraction presets, associated cell errors and keyboard access. Localize all AHP copy and verify English/Persian RTL. Consistency display consumes server boolean; client validation/reciprocal synchronization/formatting remain allowed.

**Rationale**: current history is unfiltered; selecting past results can show old weights beside current matrix. Existing helper tests do not verify rendered warnings/state/RTL. Filtering only a mixed-method first page can hide older AHP runs.

**Alternatives considered**: duplicate history components, first-page client filtering or reconstructing CR client-side. Extend existing interfaces instead.

## 9. Verification and current evidence

**Decision**: extend existing pytest/Node suites and add `apps/web/e2e/tests/decision-ahp.spec.ts`. Use app-level Playwright config, which starts API/web; root config does not.

**Rationale**: baseline checks on 2026-10-11 passed 8 engine tests and 12 frontend helper/key/source tests. They do not cover strict types, all size boundaries, output identity, filtered history, case switching or rendered accessibility. Existing source math test skips absent files and uses limited regexes; strengthen missing-target and service-boundary checks. Commands/evidence limits are in [quickstart.md](quickstart.md).

**Alternatives considered**: treating tasks checkboxes, source inspection/typecheck or helper tests as acceptance. Constitution VI requires actual API/browser evidence. No API/DB, browser, migration, production or performance acceptance ran during planning.

## Specification reconciliation

FR-005 governs type/diagonal/tolerance; scale outside standard presets warns; actual permission catalog is retained; source doc05 governs input order. `weights_normalized` is ranking-run snapshot-derived, not a case field; raw `[1,2]` normalizes to `[1/3,2/3]`. Preservation tests compare actual before/after baselines. These are explicit design interpretations; spec/tasks and permanent governance remain unchanged.
