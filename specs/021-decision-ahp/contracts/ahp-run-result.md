# Contract: AHP Run Snapshot and Result

## Serialized envelope

Existing serializer returns `id`, `method`, `input_snapshot`, `result`, `extracted_at`, `extracted_by`, `extracted_by_name`, `created_at`. Server generates identity/time/actor. List uses the same serializer inside pagination.

Snapshot retains the full-case superset in [data-model.md](../data-model.md), deep copied independently from live case. Criteria/matrix are sufficient AHP inputs; other frozen fields do not become dependencies. AHP never replaces manual ranking weights or adds ranking-normalized weights to the case.

## Required result fields

| Field | Type | Meaning |
|---|---|---|
| status | Literal `ok` | Includes inconsistent success |
| engine | Literal `ahp` | Completed AHP discriminator |
| weights | Array length n | New results retain criteria input order |
| weights[i].criterion | String | Matches snapshot.criteria[i] for new results |
| weights[i].weight | Finite number, >0 and ≤1 | Normalized geometric mean |
| weights[i].rank | Integer 1..n | Descending-weight ordinal rank, input-index tie-break |
| lambda_max | Finite number | Spec's eigenvalue approximation |
| ci, cr | Finite nonnegative numbers | Consistency index/ratio |
| is_consistent | Boolean | True for n≤2; otherwise cr≤0.10 |

Weights sum to 1±1e-6; ranks form a permutation 1..n, including ties. Preserve computation precision. Existing historical rows may be sorted by weight; retain their stored values and identify rows by criterion name.

## Numerical contract

```text
g[j] = product_k(A[j,k]) ** (1/n)
w[j] = g[j] / sum_k(g[k])
lambda_max = mean_j(sum_k(A[j,k]*w[k]) / w[j])
ci = 0 if n == 1 else max(0, (lambda_max-n)/(n-1))
cr = 0 if n <= 2 else ci / RI[n]
is_consistent = true if n <= 2 else cr <= 0.10
```

Equivalent log-domain geometric means are permitted. Do not substitute an exact eigenvector algorithm. RI for n=1..10: `[0,0,0.58,0.90,1.12,1.24,1.32,1.41,1.45,1.49]`. Reject unsupported sizes instead of an RI fallback. Unrepresentable results use the coded input error and create no run.

## Fixtures

Criteria Quality/Cost/Schedule and `[[1,2,6],[0.5,1,3],[1/6,1/3,1]]`, within floating tolerance:

```json
{
  "status":"ok","engine":"ahp",
  "weights":[
    {"criterion":"Quality","weight":0.6,"rank":1},
    {"criterion":"Cost","weight":0.3,"rank":2},
    {"criterion":"Schedule","weight":0.1,"rank":3}
  ],
  "lambda_max":3,"ci":0,"cr":0,"is_consistent":true
}
```

Lower/Higher with `[[1,0.25],[4,1]]`: rows remain Lower/Higher, weights 0.2/0.8, ranks 2/1. Equal weights receive distinct input-order ordinal ranks. Circular `[[1,5,0.2],[0.2,1,5],[5,0.2,1]]`: equal weights, lambda≈6.2, ci≈1.6, cr≈2.75862 and false consistency; still HTTP 201 and a frozen record.
