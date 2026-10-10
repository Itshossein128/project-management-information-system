# Contract: Decision Runs (Execution Records)

Base: `/api/v1/projects/{project_id}/decision-cases/{case_id}/runs/`

Auth: JWT + project membership.

| Action | Permission |
|--------|------------|
| GET list/detail | `view_decision_support` |
| POST create (append) | `edit_decision_support` |
| PATCH / PUT / DELETE | **Not allowed** → `run_immutable` (or HTTP 405) |

## List

`GET …/runs/`

Ordered by `-extracted_at`. Each item: `id`, `method`, `extracted_at`, `extracted_by` (id + display name), `result.status` (e.g. `stub`).

## Retrieve

`GET …/runs/{run_id}/`

Full run including `input_snapshot` and `result` (for InputSnapshotViewer).

## Create (Phase 1 stub execution)

`POST …/runs/`

```json
{
  "method": "saw"
}
```

**Behavior**:

1. Resolve case in project; require `method` ∈ selected methods **or** allow any of the five for Phase 1 testing if product prefers — **decision**: method MUST be one of the five ids; SHOULD be in `case.selected_methods` (reject with `method_not_selected` if not selected).
2. Validate inputs required for that method family ([input-validation.md](./input-validation.md)):
   - `saw` / `topsis`: full ranking contract (criteria, alternatives, weights, types, matrix).
   - `ahp` / `dematel` / `ism`: criteria list + corresponding stub matrix rules (Phase 1: criteria 1..10 unique; matrix may be empty stub → reject run for engines later; for Phase 1 stub runs of criteria methods, require criteria only and freeze empty matrix stubs).
3. Deep-copy live inputs into `input_snapshot`.
4. Set `result` to `{ "status": "stub", "engine": null }` (no scores).
5. Set `extracted_at=now`, `extracted_by=request.user`.
6. Persist new row; return `201`.

**AC23**: Snapshot retains user-facing criterion/alternative names and aligned vectors/matrices.  
**AC24**: Subsequent case PATCH + new POST creates a second run; GET first run returns original snapshot unchanged.

## Mutation rejection

`PATCH|PUT|DELETE …/runs/{run_id}/`

```json
{
  "error": {
    "code": "run_immutable",
    "message": "…",
    "details": {}
  }
}
```

## Errors

- `400` `decision_input_invalid` — validation issues; no run created (AC26).
- `400` `method_not_selected` — method not on case.
- `403` / `404` — authz / wrong project.

## Non-goals

- Real SAW/TOPSIS/AHP/DEMATEL/ISM result payloads (later phases replace stub `result`).
- Combined multi-method single run.
