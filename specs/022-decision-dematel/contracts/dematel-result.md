# Contract: DEMATEL Calculation and Frozen Result

**Requirements**: FR-006–FR-013 | **Reference**: [source](../../../docs/decision-support/06-dematel.md)

## Required calculation

For validated X, s=max(row sums of X), N=X/s, A=I−N, T=N×A⁻¹. Evaluate T via a right solve, `solve(A.T, N.T).T`. D is T's row sum, R its column sum, prominence D+R and relation D−R. Preserve criterion order. All calculations occur in the backend service; views, serializers and client display contain no DEMATEL formulas.

## Reliability policy v1

Use float64 NumPy with accurate scalar summation and localized coded failures:

1. Reject exact s=0 (`dematel_all_zero`). A positive subnormal scale is not automatically zero.
2. A singular solve raises `dematel_singular`. Handle linear algebra errors without an uncaught server error.
3. Reject nonfinite condition estimates or cond₂(A)>10⁸ as `dematel_unreliable`.
4. Reject normalized right-solve residual `||T A − N||∞ / max(1, ||T||∞ ||A||∞ + ||N||∞)` greater than 10⁻¹⁰.
5. Reject nonfinite N, T, D, R, prominence or relation. Handle arithmetic exceptions before JSON storage.
6. Let total-relation residue tolerance be `10⁻¹² × max(1, max(|T|))`. Reject T values below the negative tolerance; clamp only negative values within this roundoff tolerance to zero before deriving indicators. Do not clamp legitimate negative relation.
7. Use accurate sums for D/R. Classify relation >10⁻⁹ as influencing, <−10⁻⁹ as receiving, otherwise balanced. Retain signed unrounded relation even when its role is balanced.

Thresholds are a conservative acceptance policy, not a proof of every component's accuracy. Independent high-precision fixtures must confirm SC-002 for accepted cases and exercise rejection just beyond the reliability limit. No pseudoinverse, damping, alternate normalization or silent replacement result.

## Successful result shape

```json
{
  "status": "ok",
  "engine": "dematel",
  "normalization_factor": 4.0,
  "normalized_matrix": [[0,1,0],[0,0,0.5],[0,0,0]],
  "total_relation_matrix": [[0,1,0.5],[0,0,0.5],[0,0,0]],
  "criteria_results": [
    {"criterion":"A","d":1.5,"r":0,"prominence":1.5,"relation":1.5,"role":"influencing"},
    {"criterion":"B","d":0.5,"r":1,"prominence":1.5,"relation":-0.5,"role":"receiving"},
    {"criterion":"C","d":0,"r":1,"prominence":1,"relation":-1,"role":"receiving"}
  ],
  "numerical_policy": {
    "version": "dematel-v1",
    "normalization": "max_row_sum",
    "condition_limit": 100000000.0,
    "residual_tolerance": 1e-10,
    "total_relation_roundoff_factor": 1e-12,
    "role_neutrality_tolerance": 1e-9
  }
}
```

All matrices/rows match frozen criteria count/order; each criterion row name matches the corresponding input snapshot name. Retain unrounded finite values in storage; display may format them without recalculation. Stable role identifiers are localized only for presentation. No rank, combined method score, or ranking-weight vector is produced.

The existing run envelope supplies ID, method, `input_snapshot`, `result`, `extracted_at`, `extracted_by` and actor display name. Old `status: stub` or structurally invalid payloads must display unavailable computation, not synthesized indicators. Do not rewrite old records.

## Independent numerical acceptance references

- Directed A→B→C fixture above, plus an isolated fourth criterion with all zero indicators.
- Same chain scaled uniformly to small positive values: same N/T/indicators, changed s.
- n=10 directed chain: actual 10×10 dimensions, finite output.
- Decimals: A→B=1, B→C=0.25 produces T[A,B]=1, T[B,C]=0.25, T[A,C]=0.25.
- Valid symmetric nonregular three-criterion network: balanced relations without requiring equal row sums or equal prominence.
- All-zero n=1/n=3: no success; singular two-criterion loop: no success.
- `[[0,4],[4−δ,0]]` with δ=10⁻⁶: accepted high-condition reference; δ=10⁻⁸: rejected by condition policy. Independently compute expected accepted indicators with rational/Decimal arithmetic, not the production NumPy solve.
- Accurate signed-role classifications around ±10⁻⁹ and output-rounding boundaries.
