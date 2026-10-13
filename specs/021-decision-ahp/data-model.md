# Data Model: AHP Criteria Weighting

**Feature**: `021-decision-ahp` | **Date**: 2026-10-11

## DecisionCase — existing mutable dossier

Source: `apps/api/core/decision_support/models.py`, `AuditSoftDeleteModel`.

| Field | Stored type / relationship | AHP responsibility |
|---|---|---|
| id | UUID | Case identity |
| project | FK to Project | Authorized URL project boundary |
| title | String, max 200 | Existing decision goal |
| selected_methods | JSON list of stable IDs | Contains `ahp` for run |
| criteria | Ordered JSON list | Actual trimmed exact-unique strings; 1..10 at execution |
| ahp_matrix | JSON rows | Mutable draft; strict n×n validation on run |
| alternatives, weights, types, performance_matrix | Ranking JSON inputs | Not required by AHP execution; never written by it |
| dematel_matrix, ism_matrix | Existing method inputs | No AHP mutation |
| created_at, updated_at, created_by, updated_by | Inherited audit fields | Existing save behavior |

Drafts may have no criteria, an empty matrix or null comparisons. Saving does not certify runnable input. A matrix-only patch preserves ranking fields; a real criteria change honors cross-method consistency. No case `weights_normalized` field exists.

## DecisionRun — existing execution record

Source: `apps/api/core/decision_support/models.py`, `UUIDModel`/`TimeStampedModel`.

| Field | Type / relationship | Invariant |
|---|---|---|
| id | UUID | New for each successful execution |
| case | FK to DecisionCase, CASCADE | Resolved within URL project |
| project | FK to Project, CASCADE | Equals case.project; scope queries through both |
| method | String, max 32 | `ahp` |
| input_snapshot | JSON object | Independent deep copy of loaded case |
| result | JSON object | Stored output, never recomputed during inspection |
| extracted_at | DateTime | Execution timestamp |
| extracted_by | User FK, PROTECT | Authenticated initiating identity |
| created_at, updated_at | Inherited timestamps | Existing persistence metadata |

Run PUT/PATCH/DELETE endpoints reject changes with `run_immutable`. Arbitrary ORM/admin/DB writes are outside that API guarantee; no trigger is proposed. Existing cascade deletion policy remains. Historical JSON is preserved.

## Validated input and output

- Criteria: n actual nonempty strings after trim, exact uniqueness, 1≤n≤10.
- Matrix: n rows of n actual finite positive numbers; exclude bool/string/null; exact diagonal 1; product residual <1e-4. No rounding before validation.
- Service validates independently of UI and must not mutate input arrays or case.
- Snapshot retains `title`, `selected_methods`, `criteria`, `alternatives`, `weights`, `types`, `performance_matrix`, `ahp_matrix`, `dematel_matrix`, `ism_matrix`. AHP uses only criteria/matrix and never adds derived AHP values to ranking inputs.
- Result: `status:'ok'`, `engine:'ahp'`, n `{criterion,weight,rank}` rows, `lambda_max`, `ci`, `cr`, `is_consistent`. New rows follow snapshot criterion order; rank is computed independently. All values finite, weights positive and sum to 1±1e-6. n≤2: CR=0 and true; otherwise CR≤0.10 defines true.

See [input contract](contracts/ahp-pairwise-matrix.md) and [result contract](contracts/ahp-run-result.md) for issues, formulas and fixtures.

## Transient state transitions

| State | Contents / transition |
|---|---|
| No case | Panel absent; no retained previous-case result |
| Draft | Parent-owned criteria/matrix; diagonal 1, unjudged pairs null |
| Edited | Full-precision inverse sync; blank clears both directions |
| Criteria changed | Preserve exact-name submatrix; new/renamed pairs blank |
| Saving/executing | Save changed AHP inputs, then run persisted case; prevent repeated clicks |
| Invalid | Show issues; no successful run appended |
| Successful | New immutable API record; refresh history/display result |
| Inconsistent | Successful run plus advisory warning |
| Historical | Frozen inputs/result read-only, distinct from draft |
| Case switched | Clear local state; ignore previous-case late responses |

No AHP-to-ranking transfer transition. PATCH/POST are separate requests; each execution snapshots the persisted case it reads.

## Migration and compatibility

No model/table/constraint migration. Existing data remains untouched; previously permissive drafts may require repair before a new execution. Historical weights keep their stored row order and named identity. Readers tolerate old non-AHP/stub runs while identifying completed AHP results through method/engine.
