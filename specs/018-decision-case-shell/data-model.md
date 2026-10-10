# Data Model: Decision Support Case Shell (Phase 1)

**Date**: 2026-10-10  
**Related**: [spec.md](./spec.md), [research.md](./research.md), [contracts/](./contracts/)

## Entities

### DecisionCase

Project-scoped editable decision dossier (live inputs).

| Field | Type | Rules |
|-------|------|-------|
| `id` | UUID PK | Auto |
| `project` | FK → Project | CASCADE; tenancy scope |
| `title` | string | Required; non-empty after trim; max length ~200 |
| `selected_methods` | JSON list[str] | Subset of `saw\|topsis\|ahp\|dematel\|ism`; duplicates ignored; may be empty while drafting |
| `criteria` | JSON list[str] | Ordered; 0–10 while drafting; when validated for ranking/criteria ops: 1–10, unique non-empty |
| `alternatives` | JSON list[str] | Ordered; 0–10; required 1–10 when ranking contract validated |
| `weights` | JSON list[number\|null] | Length should match `n` when ranking validated; non-negative finite; sum > 0 |
| `types` | JSON list[str] | Length `n` when ranking validated; each `benefit` or `cost` |
| `performance_matrix` | JSON list[list] | `m` rows × `n` cols when ranking validated; cells number or null; null ≠ 0 |
| `ahp_matrix` | JSON list[list] | Stub `n×n` or `[]`; full rules in later phase |
| `dematel_matrix` | JSON list[list] | Stub or `[]` |
| `ism_matrix` | JSON list[list] | Stub or `[]` |
| `created_by` / `updated_by` | FK User nullable | Audit soft pattern if using `AuditSoftDeleteModel` |
| timestamps / soft-delete | per `common.models` | Prefer `AuditSoftDeleteModel` like `risk` |

**Relationships**: `project` 1—* `DecisionCase`; `DecisionCase` 1—* `DecisionRun`.

**Validation (live case)**:

- Title always non-empty on create/update.
- `selected_methods` values must be known method ids.
- Named lists: trim; reject empty entries; reject duplicates (exact); reject length > 10.
- When ranking fields are non-empty / run targets SAW|TOPSIS: apply full ranking contract ([input-validation](./contracts/input-validation.md)).
- Criteria-analysis-only cases may keep `alternatives` / `performance_matrix` empty.

### DecisionRun

Immutable execution record for one method on one case.

| Field | Type | Rules |
|-------|------|-------|
| `id` | UUID PK | Auto |
| `case` | FK → DecisionCase | CASCADE with case |
| `project` | FK → Project | Denormalized for tenancy queries (same as case.project); set on create |
| `method` | string | One of five method ids |
| `input_snapshot` | JSON object | Frozen copy of inputs used for this run (see shape below) |
| `result` | JSON object | Phase 1 stub: `{ "status": "stub", "engine": null }`; later phases fill scores/layers |
| `extracted_at` | datetime | Set once at create (UTC) |
| `extracted_by` | FK User | PROTECT; actor who recorded the run |

**Immutability**: No in-place update of `input_snapshot`, `result`, `method`, `extracted_at`, `extracted_by`. API exposes list/retrieve/create only.

**Snapshot shape** (minimum for AC23):

```json
{
  "title": "…",
  "criteria": ["…"],
  "alternatives": ["…"],
  "weights": [1, 1],
  "types": ["benefit", "cost"],
  "performance_matrix": [[10, 100], [5, 200]],
  "ahp_matrix": [],
  "dematel_matrix": [],
  "ism_matrix": [],
  "selected_methods": ["saw", "topsis"]
}
```

Snapshot MUST deep-copy lists/matrices so later case edits cannot mutate stored JSON by reference.

## State transitions

```text
[Draft case] --update inputs/methods--> [Draft case]
[Draft case] --POST run (valid)------> [Draft case] + append DecisionRun (immutable)
[DecisionRun] --PATCH/PUT-----------> REJECT (run_immutable)
```

No workflow states for Phase 1 (no draft/published run). Success = row exists; failure = validation error, no row.

## Indexes / constraints

- Index `(project_id, -created_at)` on cases.
- Index `(case_id, -extracted_at)` and `(project_id, -extracted_at)` on runs.
- DB check constraints optional; business rules enforced in services (JSON flexibility).

## Permission codes (catalog)

| Code | Use |
|------|-----|
| `view_decision_support` | List/retrieve cases and runs |
| `edit_decision_support` | Create/update/delete cases; create runs |

## Out of model (later phases)

- Engine-specific result schemas (scores, CR, prominence, layers).
- Normalized weight storage separate from raw (may add to snapshot in Phase 2).
- Excel import blobs; external job ids.
