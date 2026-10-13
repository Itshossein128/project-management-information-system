# Contract: DEMATEL Inputs and Existing Project API

**Requirements**: FR-001–FR-007, FR-011–FR-017 | **Result**: [dematel-result.md](dematel-result.md)

## Existing routes and access

Base: `/api/v1/projects/{project_id}/decision-cases/`.

| Operation | Route suffix | Required permission | Behavior |
| --- | --- | --- | --- |
| Create case | POST base | `edit_decision_support` | Existing 201 case response |
| Read/edit case | GET/PATCH `{case_id}/` | view/edit respectively | Existing case response including `dematel_matrix` |
| Execute | POST `{case_id}/runs/` | `edit_decision_support` | Body `{"method":"dematel"}`; 201 immutable run only on success |
| List history | GET `{case_id}/runs/?method=dematel` | `view_decision_support` | Existing scoped paginated list, filter before pagination |
| Read execution | GET `{case_id}/runs/{run_id}/` | `view_decision_support` | Frozen input/result/actor/time |

Preserve authentication, active membership, existing administrator policy, and authoritative project/case/run scoping. No new permission or endpoint. Existing run PUT/PATCH/DELETE remain rejected as `run_immutable`; unauthorized access remains 403 or scoped 404 according to existing behavior.

## Draft saving

The case already exposes `dematel_matrix`. A matrix-only PATCH must not revalidate or normalize unrelated ranking drafts. A criteria edit must save the new ordered names and remapped matrix together. Partial matrices and null cells are recoverable drafts; finite incorrect values may be saved for later correction. Actual numeric NaN/infinity/overflow must be rejected before JSON storage. Malformed persisted containers must not cause an unhandled normalization exception when correcting a case.

Example complete draft:

```json
{
  "selected_methods": ["dematel"],
  "criteria": ["A", "B", "C"],
  "dematel_matrix": [[0,4,0],[0,0,2],[0,0,0]]
}
```

Alternatives, weights, criterion types and performance data are not DEMATEL prerequisites. Existing draft fields may still be present; DEMATEL does not rewrite them.

## Execution validation

- DEMATEL must be selected on the saved case. Recheck selection on authoritative locked state, not a stale instance.
- 1–10 nonempty trimmed unique string names; exact n×n list of list rows.
- Cells are int/float JSON numbers excluding booleans; values finite and inclusively 0–4. Decimal values are supported. Numeric strings are not executable cells; UI converts user input through the existing numeric entry boundary.
- Every diagonal is exactly zero; no reciprocal or symmetry constraint.
- Matrix root and row issues must be emitted for shape mismatches before indexing.
- Full validation and numerical reliability checks precede record creation.

## Error envelope and paths

Retain the current coded validation envelope: top-level error code `decision_input_invalid` with `error.details.issues` rows containing stable `code`, `path`, and localized `message`.

| Code | Path | Meaning |
| --- | --- | --- |
| Existing name/type/count codes | `criteria` or `criteria.j` | Invalid criterion identity/count |
| `dimension_invalid` | `dematel_matrix` and useful row paths | Matrix/row shape mismatches |
| `cell_empty` | `dematel_matrix.j.k` | Missing judgment, never substituted with zero |
| `non_numeric` | `dematel_matrix.j.k` | Nonnumeric/string/boolean cell |
| `non_finite` | cell or matrix | Numeric nonfinite/overflow value |
| `dematel_influence_out_of_range` | `dematel_matrix.j.k` | Finite influence outside 0–4 |
| `dematel_diagonal_invalid` | `dematel_matrix.j.j` | Nonzero direct self-influence |
| `dematel_all_zero` | `dematel_matrix` | Exact normalization factor zero |
| `dematel_singular` | `dematel_matrix` | Total relations undefined |
| `dematel_unreliable` | `dematel_matrix` | Reliability guard failed |
| Existing `method_not_selected` | `method` | DEMATEL not selected |

Translate DEMATEL messages in Django EN/FA and frontend error presentation. Reuse existing parsing for precise issues and generic permission, not-found, throttle, malformed-response and network feedback. A failed request appends no successful execution.

## Consistency boundary

Run executes the persisted state under an atomic case-row lock/reload, deriving calculation and frozen snapshot from that same state. PATCH then POST are separate requests; another editor may save between them. Returned `input_snapshot` is authoritative. The UI must render results against that snapshot and serialize its own same-case saves/runs. No guarantee of cross-client optimistic revision matching is introduced.
