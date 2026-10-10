# Contract: Decision Cases

Base: `/api/v1/projects/{project_id}/decision-cases/`

Auth: JWT + project membership.

| Action | Permission |
|--------|------------|
| GET list/detail | `view_decision_support` |
| POST create, PATCH update, DELETE | `edit_decision_support` |

## List

`GET /decision-cases/`

Returns paginated or array of case summaries: `id`, `title`, `selected_methods`, `criteria_count`, `alternatives_count`, `updated_at`.

## Create

`POST /decision-cases/`

```json
{
  "title": "انتخاب پیمانکار فاز ۲",
  "selected_methods": ["saw", "topsis"],
  "criteria": ["تجربه", "قیمت"],
  "alternatives": ["پیمانکار الف", "پیمانکار ب"],
  "weights": [1, 1],
  "types": ["benefit", "cost"],
  "performance_matrix": [],
  "ahp_matrix": [],
  "dematel_matrix": [],
  "ism_matrix": []
}
```

**Rules**:

- `title` required, non-empty.
- `selected_methods` optional; each value ∈ {`saw`,`topsis`,`ahp`,`dematel`,`ism`}.
- Named lists and ranking fields validated per [input-validation.md](./input-validation.md) when supplied.
- Empty `performance_matrix` allowed on create (Phase 1 stub).

**Response**: `201` + full case resource.

## Retrieve

`GET /decision-cases/{case_id}/`

Full case including live input fields.

## Partial update

`PATCH /decision-cases/{case_id}/`

Same fields as create (partial). Updates **live** case only; does not alter existing `DecisionRun` rows.

## Delete

`DELETE /decision-cases/{case_id}/`

Requires `edit_decision_support`. Cascades runs with the case.

## Errors

- `403` — not member / missing permission.
- `404` — case not in project (IDOR-safe).
- `400` — `error.code` typically `decision_input_invalid` or field validation; see [input-validation.md](./input-validation.md).

## Non-goals

- No method execution on case endpoints (runs are separate).
- No Excel import.
