# Contract: AHP Inputs, Execution and History

**Feature**: `021-decision-ahp` | **Date**: 2026-10-11

Base: `/api/v1/projects/{project_id}/decision-cases/`. UUIDs, authenticated membership and server permissions apply. Fraction labels submit numeric JSON values.

| Operation | Method / suffix under base | Permission | Success/error |
|---|---|---|---|
| Create dossier | POST `/` | `edit_decision_support` | 201 case |
| Save AHP draft | PATCH `/{case_id}/` | `edit_decision_support` | 200 case |
| Execute persisted inputs | POST `/{case_id}/runs/` | `edit_decision_support` | 201 run |
| List history | GET `/{case_id}/runs/?method=ahp&page=1` | `view_decision_support` | 200 paginated runs |
| Inspect run | GET `/{case_id}/runs/{run_id}/` | `view_decision_support` | 200 frozen run |
| Mutate run | PUT/PATCH/DELETE `/{case_id}/runs/{run_id}/` | Existing mutation permission | 400 `run_immutable` |

Optional planned `method` filter validates against existing method catalog; absent means all methods. Unknown/empty supplied values: 400 `decision_input_invalid`, issue `invalid_method` at `method`. Filter before pagination, keep newest-first ordering and `{count,next,previous,results}` envelope. Client follows pages rather than filtering only one mixed-method page.

Resolve active case by URL project; resolve run by authorized case and project. Cross-project case/run IDs yield scoped 404 for otherwise authorized users. Missing membership/permission yields 403; unauthenticated status follows configured authentication. Body IDs never override server assignment.

## Draft and run requests

Valid dossier create (ranking fields omitted):

```json
{
  "title": "Criteria weighting",
  "selected_methods": ["ahp"],
  "criteria": ["Quality", "Cost", "Schedule"],
  "ahp_matrix": [[1,2,6],[0.5,1,3],[0.16666666666666666,0.3333333333333333,1]]
}
```

Matrix-only patch sends only `ahp_matrix`; include criteria only when intentionally changing shared criteria. Incomplete drafts can be saved; execution validates fully. Matrix-only save preserves unrelated fields without unrelated ranking validation; real shared criteria changes retain existing consistency checks.

Execute stored input:

```json
{"method":"ahp"}
```

Requires AHP selected, criteria and matrix only; no alternatives, ranking weights/types/performance or other method execution. All valid executions including CR>0.10 return a new run ([result contract](ahp-run-result.md)); invalid execution creates no run.

## Strict execution validation

| Rule | Issue code | Path |
|---|---|---|
| Criteria list with actual strings | `invalid_type` | `criteria` or `criteria.i` |
| 1..10 trimmed exact-unique nonempty names | `dimension_invalid`, `name_empty`, `name_duplicate` | `criteria` or `criteria.i` |
| n×n row arrays | `dimension_invalid` | `ahp_matrix` or `ahp_matrix.j` |
| Null/blank string | `cell_empty` | `ahp_matrix.j.k` |
| Nonblank string/bool/other nonnumber | `non_numeric` | `ahp_matrix.j.k` |
| Non-finite cell | `non_finite` | `ahp_matrix.j.k` |
| Zero/negative | `cell_non_positive` | `ahp_matrix.j.k` |
| Diagonal not exactly numeric 1 | `ahp_diagonal_invalid` | `ahp_matrix.j.j` |
| abs(a[j][k]×a[k][j]−1)≥1e-4 | `ahp_reciprocal_mismatch` | `ahp_matrix.k.j`, j<k |
| Finite inputs yielding unrepresentable/non-finite calculation | `non_finite` | `ahp_matrix` |

Indices are zero-based. Validate types/shape before pair indexing. No rounding before validation/calculation. Standard JSON parser may reject nonstandard NaN/Infinity before domain validation; direct service tests still cover non-finite values. Parser failures need not invent cell paths.

Scale [1/9,9] is guidance via presets; custom finite positive values remain supported, with out-of-scale UI advice. No new hard cap. Product residual follows FR-005; do not combine it with interim inverse-difference prose.

## HTTP 400 envelope

```json
{
  "error": {
    "code": "decision_input_invalid",
    "message": "Localized validation feedback",
    "details": {
      "issues": [{"code":"ahp_diagonal_invalid","path":"ahp_matrix.0.0","message":"Localized cell feedback"}]
    }
  }
}
```

Follow `apps/api/core/config/exceptions.py` nesting (`error.details.issues`). Codes/paths are language independent, messages localized. `method_not_selected` is a separate top-level code with `method` issue; unknown execution method uses `decision_input_invalid`/`invalid_method`.
