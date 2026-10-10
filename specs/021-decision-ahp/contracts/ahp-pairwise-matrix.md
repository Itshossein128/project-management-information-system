# Contract: AHP Pairwise Comparison Matrix

**Endpoint**: `POST /api/v1/projects/{project_id}/decision-cases/{case_id}/runs/`
**Action**: Execute method `"ahp"`

## Request Payload

```json
{
  "method": "ahp"
}
```

The execution reads `criteria` and `ahp_matrix` directly from the `DecisionCase` record.

### Required Case Fields
- `criteria`: `string[]` of length $n$ ($1 \le n \le 10$). Each name unique, non-empty, trimmed.
- `ahp_matrix`: `number[][]` of size $n \times n$.
  - $a_{j,j} = 1.0$ for $0 \le j < n$.
  - $a_{j,k} > 0$ for all $j, k$.
  - $a_{k,j} = 1 / a_{j,k}$ (reciprocal symmetry).

### Success Response (`201 Created`)
Returns serialized `DecisionRun` with `method: "ahp"` and populated `result` containing weights, eigenvalue, CI, CR, and consistency boolean.

### Error Responses (`400 Bad Request`)
Returns `{ "code": "decision_input_invalid", "issues": [ { "code": "...", "path": "...", "message": "..." } ] }`.
