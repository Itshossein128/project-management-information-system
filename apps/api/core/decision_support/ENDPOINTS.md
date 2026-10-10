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
        { "code": "empty_cell", "path": "performance_matrix.0.1", "message": "Cell cannot be empty." }
      ]
    }
  }
}
```

Phase 1 runs store `result: { "status": "stub", "engine": null }` — no SAW/TOPSIS/AHP/DEMATEL/ISM engines.
