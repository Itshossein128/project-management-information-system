# Contract: Pure SAW Engine

**Sources**: [03-saw.md](../../../docs/decision-support/03-saw.md), [09-ranking-reference.md](../../../docs/decision-support/09-ranking-reference.md)  
**Acceptance**: AC01 (independence of callable), AC11 (via scores), AC13–AC14, engine portions of AC09–AC10

## Interface (conceptual)

```text
compute_saw(criteria, alternatives, weights, types, matrix) -> {
  ranking: [ { option, score, rank }, … ]  # score-desc, stable ties, ordinal rank
  weights_normalized: [ float, … ]
}
```

- **Pure**: no ORM, HTTP, i18n, or side effects.
- **Independent**: MUST NOT compute or return TOPSIS (AC01).
- Callers MUST pass structurally validated inputs **or** the engine re-validates and raises the same coded issues.

## Formulas

```text
w[j] = weights[j] / sum(weights)          # sum > 0
benefit: r[i,j] = x[i,j] / max_i(x[i,j])  # max > 0
cost:    r[i,j] = min_i(x[i,j]) / x[i,j]  # x[i,j] > 0
score[i] = sum_j(w[j] * r[i,j])
```

## Ordering (interim — O01/O02 open)

1. Sort by `score` descending.
2. Equal scores: preserve relative order of alternatives in the input list (stable).
3. Assign `rank` = 1-based position in the sorted list (ordinal; not shared ties).

## Engine rejection codes

| Condition | `issues[].code` | `path` |
|-----------|-----------------|--------|
| Cost cell ≤ 0 | `cost_zero` | `performance_matrix.{i}.{j}` |
| Weight < 0 | `weight_negative` | `weights.{j}` |
| Sum(weights) ≤ 0 | `weights_all_zero` | `weights` |
| Benefit column all zeros (even if weight 0) | `benefit_column_all_zero` | `criteria.{j}` |

Raise via the same `decision_input_invalid` / issues list pattern as Phase 1 ([018 input-validation](../../018-decision-case-shell/contracts/input-validation.md)).

## Acceptance fixture (AC14)

```text
criteria = ["تجربه", "قیمت"]
alternatives = ["پیمانکار الف", "پیمانکار ب"]
weights = [1, 1]
types = ["benefit", "cost"]
matrix = [[10, 100], [5, 200]]
```

Expected ranking:

| option | score | rank |
|--------|-------|------|
| پیمانکار الف | 1.0 | 1 |
| پیمانکار ب | 0.5 | 2 |

## AC11

Identical scores for weights `[2, 3]` and `[20, 30]` on otherwise equal valid inputs.

## Non-goals

- TOPSIS, AHP, DEMATEL, ISM
- Shared/tied rank policies (final O01)
- HTTP envelope (owned by execution layer)
