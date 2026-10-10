# Contract: TOPSIS Ranking Row

**Feature**: `020-decision-topsis` | **Status**: Interim (O01/O02 open)

This document specifies the shape of each row in `DecisionRun.result.ranking` for TOPSIS runs.

---

## Row Schema

A single TOPSIS ranking row (element of `result.ranking` array):

```typescript
type TopsisRankingRow = {
  option: string;     // Alternative name — preserved from input_snapshot.alternatives
  d_best: number;     // Euclidean distance to positive ideal solution A+; float ≥ 0
  d_worst: number;    // Euclidean distance to negative ideal solution A−; float ≥ 0
  closeness: number;  // Relative closeness C* = d_worst / (d_best + d_worst); range [0, 1]
  score: number;      // Alias for closeness; same float value; kept for RankingResultTable compat
  rank: number;       // 1-based ordinal rank; 1 = best (highest closeness)
};
```

---

## Computation Summary (from [04-topsis.md](../../../docs/decision-support/04-topsis.md))

```
Input: criteria[n], alternatives[m], weights[n] (raw), types[n], matrix[m][n]

Step 1: Normalize weights
  w[j] = weights[j] / sum(weights)

Step 2: Vector normalize each column
  denom[j] = sqrt(Σᵢ x[i,j]²)
  v[i,j] = w[j] * x[i,j] / denom[j]
  REJECT if denom[j] == 0 → error code: topsis_denom_zero

Step 3: Identify ideal solutions
  For benefit criterion j: best[j] = max(v[:,j]), worst[j] = min(v[:,j])
  For cost    criterion j: best[j] = min(v[:,j]), worst[j] = max(v[:,j])

Step 4: Compute distances per alternative
  d_best[i]  = sqrt(Σⱼ (v[i,j] - best[j])²)
  d_worst[i] = sqrt(Σⱼ (v[i,j] - worst[j])²)

Step 5: Compute closeness
  total = d_best[i] + d_worst[i]
  closeness[i] = d_worst[i] / total   if total > 0
               = 0.5                  if total == 0  (AC16)

Step 6: Sort and rank
  Sort alternatives by closeness descending (stable: ties preserve input order)
  rank = 1-based ordinal position in sorted order
```

---

## Numeric Properties

| Property | Value |
|----------|-------|
| `closeness` range | [0.0, 1.0] inclusive |
| `closeness` when d_best + d_worst = 0 | Exactly `0.5` (AC16) |
| `score` | Always equal to `closeness` |
| `d_best` when alternative equals ideal best on all criteria | `0.0` |
| `d_worst` when alternative equals ideal worst on all criteria | `0.0` |
| Tie ordering | Input order of alternatives preserved (stable sort) |
| Rank numbering | 1, 2, 3, … (ordinal; no shared ties in this interim contract — O01 open) |

---

## Acceptance Sample (AC15)

Given:
```
criteria    = ["تجربه", "قیمت"]
alternatives = ["پیمانکار الف", "پیمانکار ب"]
weights     = [1, 1]
types       = ["benefit", "cost"]
matrix      = [[10, 100], [5, 200]]
```

Expected TOPSIS ranking (from [10-acceptance-checks.md](../../../docs/decision-support/10-acceptance-checks.md)):

| rank | option | closeness | d_best | d_worst |
|------|--------|-----------|--------|---------|
| 1 | پیمانکار الف | 1.0 | 0.0 | ~0.707 |
| 2 | پیمانکار ب | 0.0 | ~0.707 | 0.0 |

**Verification**: الف achieves best on both criteria (highest benefit, lowest cost), so it is at the positive ideal with d_best = 0 and closeness = 1.0. ب is at the negative ideal with d_worst = 0 and closeness = 0.0.

---

## AC16 Sample

Given a single alternative or two identical rows:
```
criteria    = ["c1"]
alternatives = ["a1"]
weights     = [1]
types       = ["benefit"]
matrix      = [[5]]
```

Expected:
```json
{ "option": "a1", "d_best": 0.0, "d_worst": 0.0, "closeness": 0.5, "score": 0.5, "rank": 1 }
```

The alternative is simultaneously the best and worst on all criteria; total distance = 0 → closeness = 0.5.

---

## Relationship to SAW Row Shape

| Field | SAW Row | TOPSIS Row |
|-------|---------|------------|
| `option` | ✅ | ✅ |
| `score` | ✅ (weighted normalized sum) | ✅ (alias for closeness) |
| `rank` | ✅ (ordinal) | ✅ (ordinal) |
| `d_best` | ✗ | ✅ |
| `d_worst` | ✗ | ✅ |
| `closeness` | ✗ | ✅ |

TOPSIS rows are a **strict superset** of SAW rows. Consumers reading `option`, `score`, `rank` work on both; TOPSIS-specific consumers additionally read `d_best`, `d_worst`, `closeness`.

---

## Open Items

- **O01**: Tie rank policy. If two alternatives have equal `closeness`, both receive sequential ordinal ranks in input order. This is interim; shared/dense tie ranks remain undecided.
- **O02**: Whether distances are part of the final product contract. Phase 3 includes them per the interim choice documented in the spec. Final policy requires explicit product decision.
