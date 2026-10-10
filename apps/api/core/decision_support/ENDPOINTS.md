# Decision Support API

Base: `/api/v1/projects/{project_id}/`

| Method | Path | Permission |
|--------|------|------------|
| GET/POST | `decision-cases/` | view / edit `*_decision_support` |
| GET/PATCH/DELETE | `decision-cases/{id}/` | view / edit |
| GET/POST | `decision-cases/{id}/runs/` | view / edit |
| GET | `decision-cases/{id}/runs/{run_id}/` | view |
| PUT/PATCH/DELETE | `decision-cases/{id}/runs/{run_id}/` | `run_immutable` |

## Validation error (interim O03)

```json
{
  "error": {
    "code": "decision_input_invalid",
    "message": "…",
    "details": {
      "issues": [
        { "code": "empty_cell", "path": "performance_matrix.0.1", "message": "Cell cannot be empty." },
        { "code": "benefit_column_all_zero", "path": "criteria.0", "message": "…" }
      ]
    }
  }
}
```

## SAW run (Phase 2)

`POST …/runs/` with `{"method":"saw"}` validates ranking inputs, runs pure SAW (never TOPSIS), and appends an immutable run.

**Success `result`** (interim ordinal ranks — O01/O02 remain open as final product policy):

```json
{
  "status": "ok",
  "engine": "saw",
  "ranking": [
    { "option": "پیمانکار الف", "score": 1.0, "rank": 1 },
    { "option": "پیمانکار ب", "score": 0.5, "rank": 2 }
  ]
}
```

**Snapshot** includes live frozen inputs plus `weights_normalized` for audit.

Non-SAW methods may still return Phase 1 stub: `{ "status": "stub", "engine": null }`.
