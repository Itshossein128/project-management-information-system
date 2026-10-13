# Contract: ISM Inputs and Existing Project API

**Requirements**: FR-001–FR-004, FR-012–FR-018 | **Output**: [ism-result.md](ism-result.md)

## Routes and authorization

Base: `/api/v1/projects/{project_id}/decision-cases/`.

| Operation | Route suffix | Required permission | Contract |
| --- | --- | --- | --- |
| Create | POST base | `edit_decision_support` | Existing 201 case response |
| Read/edit | GET/PATCH `{case_id}/` | view/edit respectively | Existing case including `ism_matrix` |
| Execute | POST `{case_id}/runs/` | `edit_decision_support` | `{"method":"ism"}`; 201 immutable run on success |
| History | GET `{case_id}/runs/?method=ism` | `view_decision_support` | Scoped pagination, filter before pagination |
| Read run | GET `{case_id}/runs/{run_id}/` | `view_decision_support` | Frozen input/result/actor/time |

Preserve authentication, active membership, administrator policy and project/case/run scoping. Cross-project resources are never resolved globally. Existing denial behavior remains 403 or scoped 404. Run PUT/PATCH/DELETE remains rejected with `run_immutable`. No new route or permission is introduced.

## Drafts

```json
{
  "selected_methods": ["ism"],
  "criteria": ["A", "B", "C"],
  "ism_matrix": [[0,1,0],[0,0,1],[0,0,0]]
}
```

ISM-only cases need no alternatives, weights, types or performance matrix. Row i influences column j; reverse judgments are independent. New matrices have explicit diagonal zero and null off-diagonals. Every cell is editable, including direct diagonal zero/one; unanswered diagonal is a permissible unfinished draft but cannot execute.

Saving may retain null, incomplete shape and finite invalid cells for correction; it does not perform executable analysis or fill missing cells. Reject actual nonfinite/overflow numbers before JSON storage with locatable errors. ISM-only matrix PATCH must not revalidate/normalize unrelated ranking or method fields. Criteria changes save ordered names and the remapped matrix together and retain existing shared-dimension/ranking validation. Renaming/moving/removing preserves surviving ISM pairs; adding creates zero on the new diagonal and unanswered cross-pairs. Other-method reconciliation retains its established behavior.

Malformed persisted ISM containers remain recoverable: do not crash on scalar normalization or silently coerce text/bool/invalid cells to zero. Other-method operations preserve unrelated finite invalid ISM drafts.

## Execution validation

1. ISM is selected on the authoritative saved case.
2. Criteria are 1–10 nonempty trimmed unique strings using existing exact uniqueness rules.
3. Matrix is exactly n list rows of exactly n cells; validate root/rows before indexing.
4. Every cell is a native finite int/float exactly zero or one; 0.0/1.0 accepted, strings/bools rejected. Null/empty judgments are missing. No rounding/coercion, reciprocity or all-zero rejection.
5. Both direct diagonal values are valid; derived identity is separate. All validation/derivation completes before any run is appended.

## Errors

Use existing `error.code: decision_input_invalid` and `error.details.issues` rows with stable `code`, `path`, localized `message`. `method_not_selected` retains its existing top-level code.

| Issue code | Path | Meaning |
| --- | --- | --- |
| `invalid_type`, `name_empty`, `name_duplicate`, `dimension_invalid` | `criteria` or `criteria.i` | Invalid identity/count |
| `dimension_invalid` | `ism_matrix` or `ism_matrix.i` | Invalid container/row dimensions |
| `cell_empty` | `ism_matrix.i.j` | Missing judgment |
| `non_numeric` | `ism_matrix.i.j` | Text, bool or other nonnumeric value |
| `non_finite` | affected draft/execution path | Actual numeric nonfinite/overflow |
| `ism_relation_invalid` | `ism_matrix.i.j` | Finite numeric value other than zero/one |
| `ism_derivation_failed` | `ism_matrix` | Internal nonprogress/invariant failure, never normal cycle rejection |
| `method_not_selected` | `method` | ISM not selected |

All failed runs append zero records. Finite invalid draft correction remains available. Preserve localized generic permission/not-found/throttle/non-JSON/network feedback and do not present an older result as a new success.

## Consistency boundary

An ISM-only atomic path reloads/locks the active case by project and case ID, rechecks selection, computes, snapshots and appends from that same authoritative state. Deleted/deselected/stale cases cannot execute from the caller's old instance. Existing concurrent updates wait on that row. PATCH and POST remain separate requests: another client can save between them, so returned `input_snapshot` is authoritative. No optimistic revision or exactly-once network retry protocol is added.
