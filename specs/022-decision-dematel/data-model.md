# Data Model: DEMATEL

**Spec**: [spec.md](spec.md) | **Contracts**: [inputs/API](contracts/dematel-inputs-api.md), [result](contracts/dematel-result.md)

## Existing DecisionCase

No new entity or column. Retain project ownership, title, selected methods, ordered criteria and all existing method inputs. `dematel_matrix` is existing editable JSON containing row-major directed judgments in criteria order.

- Empty/uninitialized draft: `[]`; rendered initialization supplies zero diagonal and null off-diagonal values.
- Draft cells may be null or finite values requiring later correction. Numeric nonfinite/overflow values must never reach PostgreSQL JSON.
- Execution requires exact n×n numeric matrix, 1≤n≤10, values 0–4, zero diagonal. Native JSON numbers only; booleans are invalid. The frontend numeric parser owns localized input conversion.
- Names use existing trimmed-string uniqueness rules. No global name-normalization change.
- DEMATEL-only updates write only requested fields and audit fields; unrelated ranking/AHP/ISM inputs retain original values.

## Existing DecisionRun

No new entity or migration. Retain foreign keys `case`, `project`, `extracted_by`, method `dematel`, immutable `input_snapshot`, immutable `result`, and `extracted_at`.

Snapshot uses the existing deep-copy helper, preserving title, ordered criteria, selected methods, direct influences and existing method inputs. Calculation and snapshot must come from one locked authoritative case state. The result records normalized/total matrices, normalization factor, ordered criterion results and the versioned numerical policy described in the result contract.

A result row has `criterion`, `d`, `r`, `prominence`, `relation`, and server-assigned `role`. Rows stay in snapshot criterion order; no ranks or generated ranking weights. All numeric outputs are finite native JSON numbers.

## Live criterion identity mapping

The current storage identifies criteria by ordered strings, not persistent IDs. UI operation metadata preserves each surviving DEMATEL pair across rename and reordering without changing storage:

- Rename: retain all pairs by index, update both axis labels.
- Move: apply the same index permutation to rows and columns.
- Add: keep surviving pairs, new diagonal zero, new off-diagonal pairs null.
- Remove: drop that row and column, retain surviving pairs.

Save the updated criteria and aligned DEMATEL matrix together. Existing AHP name-based remapping remains independent. Historical names and matrices are never remapped.

## State transitions

`Uninitialized draft → partial draft → complete draft → execution requested → validated/calculated → immutable successful run`.

Validation/numerical/permission/request failure leaves no new successful run and retains recoverable user draft. All-zero and singular matrices can remain drafts for correction; they cannot become successful numerical results. Case edits invalidate the UI's current-result association, but historical runs remain accessible.

Existing DEMATEL `status: stub` records are preserved and shown as unavailable output, not upgraded or interpreted as successful computations. ISM remains a stub. Run update/delete prohibition and project scoping remain unchanged.

## Migration decision

Expected: no migration. Implementation must run `makemigrations --check --dry-run` and report its actual outcome; discovering a genuine schema need requires revisiting this design rather than inventing a parallel record model.
