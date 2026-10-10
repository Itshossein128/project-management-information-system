# Data Model: Decision Support SAW Ranking (Phase 2)

**Date**: 2026-10-10  
**Related**: [spec.md](./spec.md), [research.md](./research.md), [018 data-model](../018-decision-case-shell/data-model.md), [contracts/](./contracts/)

Phase 2 **extends** Phase 1 entities; no new tables required.

## Entities

### DecisionCase (live ranking inputs — activated)

Same fields as Phase 1. Phase 2 makes these first-class in the UI and in SAW runs:

| Field | Phase 2 rules |
|-------|----------------|
| `weights` | Length `n` when running SAW; finite non-negative; sum > 0 |
| `types` | Length `n`; each `benefit` \| `cost` |
| `performance_matrix` | Exactly `m`×`n`; finite non-negative numbers; no nulls at run time; cost cells > 0; no all-zero benefit column |

Criteria/alternatives/method selection unchanged. Stub square matrices unused by SAW.

### DecisionRun (SAW result)

Unchanged columns. Semantics for `method=saw` on successful create:

| Field | Phase 2 SAW value |
|-------|-------------------|
| `method` | `"saw"` |
| `input_snapshot` | Frozen case ranking inputs + optional `weights_normalized` (see below) |
| `result` | Real SAW payload (not stub) — see shape |
| `extracted_at` / `extracted_by` | Unchanged |

Other methods may still receive Phase 1 stub results until their phases.

### Snapshot shape (SAW)

```json
{
  "title": "…",
  "criteria": ["تجربه", "قیمت"],
  "alternatives": ["پیمانکار الف", "پیمانکار ب"],
  "weights": [1, 1],
  "weights_normalized": [0.5, 0.5],
  "types": ["benefit", "cost"],
  "performance_matrix": [[10, 100], [5, 200]],
  "ahp_matrix": [],
  "dematel_matrix": [],
  "ism_matrix": [],
  "selected_methods": ["saw"]
}
```

- Deep-copy all lists/matrices at create time.
- `weights_normalized` SHOULD be present on successful SAW runs (audit per doc 08).
- Prior runs without `weights_normalized` (Phase 1 stubs) remain valid history.

### Result shape (SAW — interim)

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

| Field | Rules |
|-------|--------|
| `status` | `"ok"` for successful SAW (stub remains `{status:"stub", engine:null}` for other methods) |
| `engine` | `"saw"` |
| `ranking` | Ordered by `score` descending; ties preserve case alternative order; `rank` = 1-based ordinal after that sort (interim; O01/O02 open) |
| `option` | Exact user-facing alternative name from snapshot |
| `score` | Float SAW score; acceptance sample must yield `1.0` and `0.5` |
| `rank` | Interim ordinal; **not** shared/tied ranks |

No TOPSIS keys. No blended scores.

### Pure value objects (not persisted alone)

| Name | Role |
|------|------|
| **Normalized weights** | `w[j] = weights[j] / sum(weights)` |
| **SAW Result Row** | `{ option, score, rank }` |
| **SawComputeOutput** | Ordered ranking rows (+ optional debug fields never required by API) |

## Validation rules (SAW path)

1. Method `saw` must be in `case.selected_methods`.
2. Full ranking contract ([ranking-inputs.md](./contracts/ranking-inputs.md) / Phase 1 input-validation).
3. Engine guards: cost cells > 0 (AC09); weights sum > 0 (AC10); no all-zero benefit column (AC13).
4. On any failure: no `DecisionRun` row.

## State transitions

```text
[Case with SAW + ranking inputs]
   --POST run method=saw (invalid)--> no new run; issues with path
   --POST run method=saw (valid)---> append DecisionRun (immutable, result.engine=saw)
[DecisionRun]
   --PATCH/PUT/DELETE--------------> REJECT run_immutable
[Case PATCH weights/matrix]
   --does not mutate--------------> prior DecisionRun rows
```

## Indexes / permissions

Unchanged from Phase 1 (`view_decision_support` / `edit_decision_support`).

## Out of model (later phases)

- TOPSIS distances / result schema
- AHP / DEMATEL / ISM results
- Final shared-rank policy (O01)
- Auto-imported weights from AHP/DEMATEL
