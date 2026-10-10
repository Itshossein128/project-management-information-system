# Data Model: Decision Support AHP Criteria Weighting (Phase 4)

**Branch**: `021-decision-ahp` | **Spec**: [spec.md](./spec.md)

This document specifies the data shapes, entities, and validation constraints for Phase 4 AHP criteria weighting.

---

## 1. Entities

### `DecisionCase` (Criteria weighting aspect)
Already defined in Django model `DecisionCase`:
```python
class DecisionCase(AuditSoftDeleteModel):
    project = models.ForeignKey(...)
    title = models.CharField(max_length=200)
    selected_methods = models.JSONField(default=list, blank=True)
    criteria = models.JSONField(default=list, blank=True)  # list[str], 1..10 unique non-empty names
    ahp_matrix = models.JSONField(default=list, blank=True)  # list[list[float]], n×n pairwise matrix
```

#### Constraints on `ahp_matrix`:
- Type: 2D array of floats `list[list[float]]`.
- Dimensions: $n \times n$ where $n = \text{len}(criteria)$, $1 \le n \le 10$.
- Element values: $a_{j,k} > 0$ for all $j, k \in [0, n-1]$.
- Diagonal: $a_{j,j} == 1.0$ for all $j \in [0, n-1]$.
- Reciprocal symmetry: $|a_{k,j} \cdot a_{j,k} - 1.0| < 10^{-4}$ for all $j, k$.

---

### `DecisionRun` (AHP execution record)
Already defined in Django model `DecisionRun`:
```python
class DecisionRun(UUIDModel, TimeStampedModel):
    case = models.ForeignKey(DecisionCase, ...)
    project = models.ForeignKey('projects.Project', ...)
    method = models.CharField(max_length=32)  # Literal "ahp"
    input_snapshot = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    extracted_at = models.DateTimeField()
    extracted_by = models.ForeignKey(settings.AUTH_USER_MODEL, ...)
```

#### Shape of `input_snapshot`:
```json
{
  "title": "Subcontractor Selection",
  "criteria": ["Cost", "Quality", "Schedule"],
  "ahp_matrix": [
    [1.0, 3.0, 5.0],
    [0.3333333333, 1.0, 2.0],
    [0.2, 0.5, 1.0]
  ],
  "selected_methods": ["ahp"]
}
```

#### Shape of `result`:
```json
{
  "status": "ok",
  "engine": "ahp",
  "weights": [
    {
      "criterion": "Cost",
      "weight": 0.63698559,
      "rank": 1
    },
    {
      "criterion": "Quality",
      "weight": 0.25828489,
      "rank": 2
    },
    {
      "criterion": "Schedule",
      "weight": 0.10472952,
      "rank": 3
    }
  ],
  "lambda_max": 3.038706,
  "ci": 0.019353,
  "cr": 0.033367,
  "is_consistent": true
}
```

---

## 2. Validation Issue Codes

The `validate_ahp_inputs(criteria, ahp_matrix)` function raises `CodedValidationError` with `{issues: [...]}`:

| Code | Path | Condition |
|---|---|---|
| `dimension_invalid` | `ahp_matrix` | Matrix is not a list of $n$ rows or length mismatch with criteria |
| `dimension_invalid` | `ahp_matrix.{j}` | Row $j$ does not contain exactly $n$ items |
| `cell_empty` | `ahp_matrix.{j}.{k}` | Cell $(j, k)$ is null or empty string |
| `cell_not_a_number` | `ahp_matrix.{j}.{k}` | Cell $(j, k)$ is not a number or is boolean |
| `cell_non_positive` | `ahp_matrix.{j}.{k}` | Cell $(j, k)$ is $\le 0$, negative, NaN, or infinity |
| `ahp_diagonal_invalid` | `ahp_matrix.{j}.{j}` | Diagonal cell $(j, j) \ne 1.0$ (tolerance $|a_{j,j} - 1.0| > 10^{-4}$) |
| `ahp_reciprocal_mismatch` | `ahp_matrix.{k}.{j}` | Reciprocal symmetry violated: $|a_{k,j} \cdot a_{j,k} - 1.0| \ge 10^{-4}$ |

---

## 3. Frontend Types (`decision-support.ts`)

```typescript
export interface AhpWeightRow {
  criterion: string;
  weight: number;
  rank: number;
}

export interface AhpRunResult {
  status: 'ok';
  engine: 'ahp';
  weights: AhpWeightRow[];
  lambda_max: number;
  ci: number;
  cr: number;
  is_consistent: boolean;
}
```
