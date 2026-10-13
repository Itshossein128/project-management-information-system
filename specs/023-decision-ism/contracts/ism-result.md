# Contract: ISM Derivation and Immutable Result

**Requirements**: FR-005–FR-014 | **Input**: [ism-inputs-api.md](ism-inputs-api.md)

## Algorithm contract

1. Copy validated direct input into an internal integer binary matrix. Include identity with Boolean OR (set derived diagonal one); do not numerically add identity or overwrite direct input.
2. Complete transitive closure with Boolean Warshall, intermediate index outermost. Output exactly n×n native integer zero/one cells.
3. Start all original indices active. In every round, compute `Reach(i)={j active | closure[i][j]=1}`, `Antecedent(i)={j active | closure[j][i]=1}` and their intersection. Self belongs to each set.
4. Extract all active i satisfying `Reach(i)==Reach(i)∩Antecedent(i)` simultaneously. Emit the next consecutive level starting one, members in original order. Remove this layer and repeat with restricted sets. Do not substitute `Reach==Antecedent`.
5. Partition full-closure indices by mutual reachability. Emit maximal equivalence classes of at least two members; each must share one layer. Sort groups by level then first original member index, and members by original index. Singletons, including direct self-loops, are omitted.

Every criterion appears in exactly one layer, layer count ≤n, groups are disjoint maximal non-singleton classes, and complete all-zero input yields identity with one layer and no groups. Valid cycles finish normally. Defensive internal invariant failures abort with no record; they never reject cycles as such. No tolerances, thresholds or floating-point analysis are involved.

## Completed result shape

```json
{
  "status": "ok",
  "engine": "ism",
  "reachability_matrix": [[1,1,1],[0,1,1],[0,0,1]],
  "layers": [
    {"level":1,"criteria":["C"]},
    {"level":2,"criteria":["B"]},
    {"level":3,"criteria":["A"]}
  ],
  "mutual_groups": [],
  "derivation_policy": {
    "version":"ism-v1",
    "self_inclusion":"binary_or",
    "closure":"transitive",
    "layer_rule":"reach_equals_intersection",
    "layer_order":"top_to_bottom",
    "mutual_groups":"maximal_non_singleton"
  }
}
```

Layer/group `criteria` are frozen unique names from this run's ordered `input_snapshot.criteria`. Matrix axes use that exact order. A group is `{level: positive integer, criteria: at least two names}`. The result has no weights, alternative ranks, criterion deletion or method transfer. Policy identifiers remain language-independent and versioned; localized explanation is presentation.

## Independent reference networks

All unlisted edges are zero, including direct diagonals unless specified. Names appear in alphabetic original order.

| Network | Reachability rows | Layers | Mutual groups |
| --- | --- | --- | --- |
| A alone, diagonal 0 or 1 | `1` | 1:A | none |
| A/B/C all zero | `100 / 010 / 001` | 1:A,B,C | none |
| A→B→C | `111 / 011 / 001` | 1:C; 2:B; 3:A | none |
| A→B,A→C,B→D,C→D | `1111 / 0101 / 0011 / 0001` | 1:D; 2:B,C; 3:A | none |
| A→B; C isolated | `110 / 010 / 001` | 1:B,C; 2:A | none |
| A↔B; B→C | `111 / 111 / 001` | 1:C; 2:A,B | level 2:A,B |
| A→B→C→A | `111 / 111 / 111` | 1:A,B,C | level 1:A,B,C |
| A↔B; C↔D; B→C | `1111 / 1111 / 0011 / 0011` | 1:C,D; 2:A,B | level 1:C,D; level 2:A,B |
| A↔B; C↔D, disconnected | `1100 / 1100 / 0011 / 0011` | 1:A,B,C,D | separate level 1:A,B and C,D |

Add ten-criterion chain and ten-criterion cycle fixtures during implementation. A chain has an upper-triangular closure including diagonal and ten reversed single-member levels; a full cycle has all-one closure and one ten-member group/layer. Literal small fixtures plus an independent test-only traversal oracle must establish expectations without calling production computation.

## Frozen run envelope and compatibility

Existing run fields supply `id`, `project`, `case`, `method: ism`, `extracted_at` and `extracted_by`. `input_snapshot` deep-copies the original criterion order and submitted direct `ism_matrix`, preserving 0 versus 1 diagonal and accepted numeric values; existing unrelated input fields may also be included. Derivation never mutates the case. Repeated successful requests append distinct records; edits, reruns and language switching never rewrite prior records.

A completed result is recognized only by an explicit structural guard for `status:ok`, `engine:ism`, supported policy, binary matrix dimensions and valid ordered membership references. It does not recompute closure/layers/groups in the browser. Legacy `status:stub, engine:null` records are displayed as unavailable computation with their stored snapshot, never upgraded in place.
