# API Contract: TOPSIS Run — Create & Read

**Feature**: `020-decision-topsis` | **Status**: Interim (O01/O02 open)

This document defines the HTTP interface for creating and reading TOPSIS decision runs.
The underlying data structures are specified in [data-model.md](../data-model.md).

---

## Endpoint: Create TOPSIS Run

```
POST /api/v1/projects/{project_id}/decision-cases/{case_id}/runs/
```

### Authentication & Authorization

- **Authentication**: Bearer token (session cookie or JWT)
- **Membership**: Caller must be a member of `{project_id}`
- **Permission**: `edit_decision_support` on the project

### Request Body

```json
{
  "method": "topsis"
}
```

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `method` | string | Yes | Must be `"topsis"` |

### Preconditions (validated server-side)

1. `case_id` must exist and belong to `project_id`
2. `"topsis"` must be in `case.selected_methods`
3. Ranking inputs on the case must pass shared validation contract (doc 02)
4. No performance column may have a zero vector-normalization denominator (FR-004)

### Success Response — `201 Created`

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "method": "topsis",
  "input_snapshot": {
    "title": "Contractor selection",
    "criteria": ["تجربه", "قیمت"],
    "alternatives": ["پیمانکار الف", "پیمانکار ب"],
    "weights": [1, 1],
    "weights_normalized": [0.5, 0.5],
    "types": ["benefit", "cost"],
    "performance_matrix": [[10, 100], [5, 200]],
    "selected_methods": ["topsis"],
    "ahp_matrix": [],
    "dematel_matrix": [],
    "ism_matrix": []
  },
  "result": {
    "status": "ok",
    "engine": "topsis",
    "ranking": [
      {
        "option": "پیمانکار الف",
        "d_best": 0.0,
        "d_worst": 0.7071067811865476,
        "closeness": 1.0,
        "score": 1.0,
        "rank": 1
      },
      {
        "option": "پیمانکار ب",
        "d_best": 0.7071067811865476,
        "d_worst": 0.0,
        "closeness": 0.0,
        "score": 0.0,
        "rank": 2
      }
    ]
  },
  "extracted_at": "2026-10-10T19:00:00Z",
  "extracted_by": "uuid-of-user",
  "extracted_by_name": "Ali Ahmadi",
  "created_at": "2026-10-10T19:00:00Z"
}
```

### Error Responses

#### `400 Bad Request` — Validation failure (no run created)

```json
{
  "error": {
    "code": "decision_input_invalid",
    "message": "Decision input validation failed.",
    "details": {
      "issues": [
        {
          "code": "topsis_denom_zero",
          "path": "criteria.0",
          "message": "TOPSIS normalization denominator is zero: all values in this column are zero."
        }
      ]
    }
  }
}
```

Other possible `code` values in `issues`: `empty_cell`, `non_numeric`, `cost_zero`, `weights_all_zero`, `benefit_column_all_zero`, `length_mismatch`, `matrix_shape` (see [shared contract errors](./shared-ranking-errors.md)).

#### `400 Bad Request` — Method not selected

```json
{
  "error": {
    "code": "method_not_selected",
    "message": "Method is not selected on this case.",
    "details": {
      "issues": [
        {
          "code": "method_not_selected",
          "path": "method",
          "message": "Method is not selected on this case."
        }
      ]
    }
  }
}
```

#### `403 Forbidden` — Missing permission

Standard DRF 403 (not project member, or missing `edit_decision_support`).

#### `404 Not Found` — Case not found or does not belong to project

---

## Endpoint: List Runs (filtered to TOPSIS)

```
GET /api/v1/projects/{project_id}/decision-cases/{case_id}/runs/
```

### Permission

`view_decision_support`

### Response

Returns all runs for the case (all methods). The consumer filters by `method === "topsis"` client-side.

```json
{
  "count": 2,
  "results": [
    {
      "id": "...",
      "method": "topsis",
      "extracted_at": "2026-10-10T19:00:00Z",
      "extracted_by": "...",
      "extracted_by_name": "...",
      "result": { "status": "ok", "engine": "topsis", "ranking": [...] }
    },
    {
      "id": "...",
      "method": "saw",
      "extracted_at": "2026-10-10T18:55:00Z",
      "extracted_by": "...",
      "extracted_by_name": "...",
      "result": { "status": "ok", "engine": "saw", "ranking": [...] }
    }
  ]
}
```

> [!IMPORTANT] SAW and TOPSIS runs appear in the **same list** but are distinguished by `method`. The UI renders separate panels per method and does **not** blend results. The run history is shared but display is method-isolated.

---

## Immutability Contract

```
PATCH  /api/v1/projects/{project_id}/decision-cases/{case_id}/runs/{run_id}/
PUT    /api/v1/projects/{project_id}/decision-cases/{case_id}/runs/{run_id}/
DELETE /api/v1/projects/{project_id}/decision-cases/{case_id}/runs/{run_id}/
```

All three return `400 Bad Request` with `code: "run_immutable"`. This applies equally to TOPSIS runs and SAW runs (AC23, AC24).

---

## TOPSIS Result Row Schema

See [topsis-ranking-row.md](./topsis-ranking-row.md) for the per-row field specification.

---

## Independence Guarantee

Running TOPSIS (`POST /runs/` with `method: "topsis"`):
- Does **not** invoke `compute_saw()` on the server
- Does **not** create a `DecisionRun` with `method: "saw"`
- Does **not** modify existing SAW runs (AC01)

Verified by automated test `test_topsis_api.py::test_ac01_topsis_only_no_saw_run`.
