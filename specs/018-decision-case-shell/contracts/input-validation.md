# Contract: Shared Decision Input Validation

**Source**: [docs/decision-support/02-decision-inputs.md](../../../docs/decision-support/02-decision-inputs.md)  
**Acceptance**: AC05–AC12, AC26 (AC11 = normalize helper; AC13 deferred to engines)

## Modes

| Mode | When | Required fields |
|------|------|-----------------|
| `names` | Any case update touching criteria/alternatives | Non-empty unique names; length ≤ 10 |
| `ranking` | SAW/TOPSIS run, or case update with ranking payload complete enough to check | `criteria`, `alternatives`, `weights`, `types`, `performance_matrix` |
| `criteria_only` | AHP/DEMATEL/ISM stub run | `criteria` (1..10); matrices may be empty stubs in Phase 1 |

## Ranking rules (structural)

Let `n = len(criteria)`, `m = len(alternatives)`.

| ID | Rule | Fail `issues[].code` (stable) | Example `path` |
|----|------|-------------------------------|----------------|
| AC05 | `1 ≤ m,n ≤ 10`; matrix exactly `m`×`n` real cells | `dimension_invalid` / `matrix_shape` | `performance_matrix` |
| AC06 | `n=0` or `m=0` or `n>10` or `m>10` | `dimension_invalid` | `criteria` / `alternatives` |
| AC07 | Row length ≠ `n`; weights/types length ≠ `n` | `length_mismatch` | `performance_matrix.1`, `weights`, `types` |
| AC08 | Cell `null`/missing, non-numeric, negative, NaN, Inf — **never coerce empty→0** | `empty_cell` / `non_numeric` / `negative_value` / `non_finite` | `performance_matrix.i.j` |
| AC09 | `types[j]==cost` and matrix cell `== 0` | `cost_zero` | `performance_matrix.i.j` |
| AC10 | Any weight `< 0` or `sum(weights)==0` | `weight_negative` / `weights_all_zero` | `weights.j` / `weights` |
| AC11 | `normalize([2,3]) == normalize([20,30])` | (test helper; not a request error) | — |
| AC12 | Empty/duplicate name; type ∉ {`benefit`,`cost`} | `name_empty` / `name_duplicate` / `invalid_type` | `criteria.i` / `types.j` |

## Weight normalization (helper)

```text
w[j] = weights[j] / sum(weights)   # sum > 0 guaranteed after AC10
```

Used for AC11 unit tests and later engines; Phase 1 does not persist normalized weights unless included inside a future run result.

## Error envelope (O03 interim)

HTTP `400`:

```json
{
  "error": {
    "code": "decision_input_invalid",
    "message": "Decision input validation failed.",
    "details": {
      "issues": [
        {
          "code": "empty_cell",
          "path": "performance_matrix.0.1",
          "message": "Cell cannot be empty."
        }
      ]
    }
  }
}
```

- `path`: dotted path; matrix cells `performance_matrix.{row}.{col}` (0-based).
- Multiple issues MAY be returned in one response.
- Invalid input MUST NOT create a successful `DecisionRun` (AC26).

**Open**: Final cross-module envelope (O03) and name/digit normalization (O04) remain undecided; this shape is Phase-1 interim only.

## Name policy (O04 interim)

1. Trim leading/trailing whitespace.  
2. Reject if empty after trim.  
3. Uniqueness: exact string equality within the list.  
4. Do **not** implement Persian digit folding or fuzzy equality until O04 is decided.

## Non-goals

- Column all-zero benefit rejection (AC13) — Phase 2 SAW/TOPSIS.  
- AHP CR, DEMATEL singularity, ISM layering — later phases.  
- Treating JSON `0` as empty.
