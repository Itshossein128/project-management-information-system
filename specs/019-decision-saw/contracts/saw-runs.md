# Contract: SAW Execution via Decision Runs

Extends [018 decision-runs](../../018-decision-case-shell/contracts/decision-runs.md).

Base: `/api/v1/projects/{project_id}/decision-cases/{case_id}/runs/`

Auth / permissions unchanged (`view_decision_support` / `edit_decision_support`). Runs remain create-only (immutable).

## Create SAW run

`POST …/runs/`

```json
{
  "method": "saw"
}
```

### Behavior

1. Resolve case in project; `method` MUST be `saw` and MUST appear in `case.selected_methods` (`method_not_selected` otherwise).
2. Validate full ranking contract on live case fields ([ranking-inputs.md](./ranking-inputs.md)).
3. Call pure SAW engine ([saw-engine.md](./saw-engine.md)) — **never** invoke TOPSIS (AC01).
4. On engine/validation failure: HTTP `400` `decision_input_invalid` with `issues[]`; **no** run row (AC26).
5. On success:
   - Deep-copy snapshot including `weights_normalized`.
   - Persist `result` per [data-model.md](../data-model.md) (`status=ok`, `engine=saw`, ordered `ranking`).
   - Set `extracted_at`, `extracted_by`.
   - Return `201` with full run.

### Success response (excerpt)

```json
{
  "id": "…",
  "method": "saw",
  "extracted_at": "…",
  "extracted_by": { "id": "…", "display_name": "…" },
  "input_snapshot": {
    "criteria": ["تجربه", "قیمت"],
    "alternatives": ["پیمانکار الف", "پیمانکار ب"],
    "weights": [1, 1],
    "weights_normalized": [0.5, 0.5],
    "types": ["benefit", "cost"],
    "performance_matrix": [[10, 100], [5, 200]]
  },
  "result": {
    "status": "ok",
    "engine": "saw",
    "ranking": [
      { "option": "پیمانکار الف", "score": 1.0, "rank": 1 },
      { "option": "پیمانکار ب", "score": 0.5, "rank": 2 }
    ]
  }
}
```

## List / retrieve

Unchanged paths. List MAY expose `result.status` and `result.engine` so UI can distinguish stub vs SAW. Retrieve returns full snapshot + ranking for `RankingResultTable` / `InputSnapshotViewer`.

## Immutability (AC23–AC24)

- After SAW run A, PATCH case (weight or cell) + POST SAW run B → GET A returns original snapshot and scores.
- `PATCH|PUT|DELETE` on any run → `run_immutable`.

## Other methods

- `topsis` / `ahp` / `dematel` / `ism`: Phase 1 stub behavior MAY remain until their phases (no SAW math).
- Combined multi-method single run: **not allowed**.

## Errors

| HTTP | code | When |
|------|------|------|
| 400 | `decision_input_invalid` | Structural or engine issues; no run |
| 400 | `method_not_selected` | `saw` not on case |
| 403 / 404 | — | Authz / wrong project |

## Non-goals

- Auto weight import from AHP/DEMATEL
- Blended SAW+TOPSIS scores
- Client-side score computation as source of truth
