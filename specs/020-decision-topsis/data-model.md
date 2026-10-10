# Data Model: Decision Support TOPSIS Ranking (Phase 3)

**Feature**: `020-decision-topsis` | **Date**: 2026-10-10

---

## Overview

Phase 3 adds no new database models or migrations. The existing `DecisionRun.result` (JSONField) already stores ranking output; the TOPSIS result is a superset of the SAW result shape. Phase 3 changes are entirely in:

1. **A new pure service** (`topsis_service.py`) that produces the richer row shape
2. **Wiring in `execution_service.py`** that calls the real service instead of the stub
3. **TypeScript types** for the new row shape in the frontend API client
4. **UI composition** in `TopsisMethodPanel` and `RankingResultTable`

---

## Entities

### 1. `DecisionCase` *(shared, unchanged)*

| Field | Type | Rules |
|-------|------|-------|
| `id` | UUID PK | Read-only |
| `project` | FK → Project | Required; scoped |
| `title` | CharField(200) | Non-empty |
| `selected_methods` | JSONField (list) | Subset of `{'saw', 'topsis', 'ahp', 'dematel', 'ism'}` |
| `criteria` | JSONField (list of str) | 1–10 unique non-empty names |
| `alternatives` | JSONField (list of str) | 1–10 unique non-empty names |
| `weights` | JSONField (list of float) | n non-negative values, sum > 0 |
| `types` | JSONField (list of str) | n values each `'benefit'` or `'cost'` |
| `performance_matrix` | JSONField (list of list) | m × n; non-negative finite; cost cells > 0; no empty cells |
| `ahp_matrix`, `dematel_matrix`, `ism_matrix` | JSONField | Not used by TOPSIS |

**TOPSIS-relevant validation additions** (enforced in `topsis_service.py`, after `validate_ranking_inputs` passes):
- `topsis_denom_zero`: For each column j, `sqrt(Σᵢ x[i,j]²)` must be > 0. Path: `criteria.{j}`.

### 2. `DecisionRun` *(shared, shape extended in result JSON)*

| Field | Type | Rules |
|-------|------|-------|
| `id` | UUID PK | Read-only, immutable |
| `case` | FK → DecisionCase | Cascade; never null |
| `project` | FK → Project | Cascade; denormalized for query |
| `method` | CharField(32) | `'topsis'` for TOPSIS runs |
| `input_snapshot` | JSONField | Frozen copy of case inputs at run time (see below) |
| `result` | JSONField | TOPSIS result shape (see below) |
| `extracted_at` | DateTimeField | Server-set at creation |
| `extracted_by` | FK → User | `PROTECT`; audit trail |

> [!IMPORTANT] `DecisionRun` is **append-only and immutable**. No UPDATE or DELETE is permitted after creation (enforced by `DecisionRunViewSet`). This applies equally to TOPSIS runs as to SAW runs (AC23, AC24).

### 3. TOPSIS `input_snapshot` Shape

Stored in `DecisionRun.input_snapshot` (JSONField). Identical structure to the SAW snapshot, with `weights_normalized` always present for TOPSIS (auditable computation trail):

```json
{
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
}
```

### 4. TOPSIS `result` Shape (Interim Contract — O02 open)

Stored in `DecisionRun.result` (JSONField):

```json
{
  "status": "ok",
  "engine": "topsis",
  "ranking": [
    {
      "option": "پیمانکار الف",
      "d_best": 0.0,
      "d_worst": 0.7071,
      "closeness": 1.0,
      "score": 1.0,
      "rank": 1
    },
    {
      "option": "پیمانکار ب",
      "d_best": 0.7071,
      "d_worst": 0.0,
      "closeness": 0.0,
      "score": 0.0,
      "rank": 2
    }
  ]
}
```

> [!NOTE] `score` is an alias for `closeness` (both carry the same float value). `score` is kept for backward-compatible consumption by `RankingResultTable`'s base score column. `closeness` is the canonical TOPSIS C* value. This is the **interim contract** for O02; distances are stored per Phase 3 policy. Final policy remains open.

### 5. TOPSIS Ranking Row (per row in `result.ranking`)

| Field | Type | Semantics |
|-------|------|-----------|
| `option` | string | Alternative name (user-defined, preserved from snapshot) |
| `d_best` | float ≥ 0 | Euclidean distance to ideal best vector A+ |
| `d_worst` | float ≥ 0 | Euclidean distance to ideal worst vector A− |
| `closeness` | float [0, 1] | `d_worst / (d_best + d_worst)`; `0.5` when both are 0 (AC16) |
| `score` | float [0, 1] | Alias for `closeness`; same value |
| `rank` | int ≥ 1 | 1-based ordinal rank by `closeness` descending; ties preserve input order (stable) |

**Ordering**: Ranked by `closeness` descending. Equal scores → stable sort (input alternative order preserved). Ordinal ranks: 1, 2, 3, … (no shared tie ranks; O01 interim).

---

## State Transitions

### TOPSIS Run Lifecycle

```text
[Case exists, TOPSIS in selected_methods]
    │
    ▼
User triggers TOPSIS run
    │
    ▼
[Client-side validation] → issues? → Display ValidationIssueList; no run created
    │ OK
    ▼
[PATCH case with live inputs] → 400? → Display issues
    │ 200
    ▼
[POST /runs/ {method: "topsis"}]
    │
    ▼
[execution_service.create_run()]
    ├─ validate method in selected_methods
    ├─ compute_topsis() ──→ topsis_denom_zero? → 400 CodedValidationError; no run
    │                   └─ other validation fails → 400; no run
    ├─ snapshot from case (with weights_normalized)
    ├─ result = {status: ok, engine: topsis, ranking: [...]}
    └─ DecisionRun.objects.create(...)  ──→ immutable; never updated
    │
    ▼
[201 Created] → TopsisMethodPanel updates result display
              → ExecutionHistoryList invalidated (shows new TOPSIS run)
```

**Independence guarantee (AC01)**: The `method == 'topsis'` branch in `execution_service.py` never calls `compute_saw()`. SAW runs are not created, touched, or read during a TOPSIS execution.

**Separate result history (AC03/AC25)**: SAW and TOPSIS runs are separate `DecisionRun` records with different `method` values. The route renders `SawMethodPanel` and `TopsisMethodPanel` independently; each displays only its own method's runs. No blended rank field exists.

---

## Frontend Type Model

### `decision-support.ts` Types

```typescript
// EXISTING (unchanged):
export type SawRankingRow = {
  option: string;
  score: number;
  rank: number;
};

// NEW:
export type TopsisRankingRow = {
  option: string;
  d_best: number;
  d_worst: number;
  closeness: number;
  score: number;   // = closeness; kept for RankingResultTable compat
  rank: number;
};

export type RankingRow = SawRankingRow | TopsisRankingRow;

// MODIFIED (was SawRankingRow[]):
export type DecisionRunResult = {
  status?: string;
  engine?: string | null;
  ranking?: RankingRow[];
};
```

### `TopsisMethodPanel` Props

```typescript
type Props = {
  projectId: string;
  caseId: string;
  criteria: string[];
  alternatives: string[];
  weights: number[];
  types: CriterionType[];
  matrix: (number | null)[][];
  onWeightsChange: (w: number[]) => void;
  onTypesChange: (t: CriterionType[]) => void;
  onMatrixChange: (m: (number | null)[][]) => void;
  latestRanking?: TopsisRankingRow[];
};
```

### `RankingResultTable` Extended Props

```typescript
type Props =
  | { method: "saw"; ranking: SawRankingRow[]; extraColumns?: never }
  | {
      method: "topsis";
      ranking: TopsisRankingRow[];
      extraColumns?: Array<{ key: keyof TopsisRankingRow; header: string }>;
    };
```

---

## i18n Keys (New in Phase 3)

### `en.json` — additions to `decisionSupport`

| Key | Value |
|-----|-------|
| `topsisPanelTitle` | `"TOPSIS ranking"` |
| `topsisPanelHint` | `"Run TOPSIS alone with manual weights — no other method is required."` |
| `colDBest` | `"D⁺ (best)"` |
| `colDWorst` | `"D⁻ (worst)"` |
| `colCloseness` | `"Closeness (C*)"` |
| `errors.topsis_denom_zero` | `"TOPSIS column normalization denominator is zero — all values in this criterion column cannot be zero."` |

### `fa.json` — additions to `decisionSupport`

| Key | Value |
|-----|-------|
| `topsisPanelTitle` | `"رتبه‌بندی TOPSIS"` |
| `topsisPanelHint` | `"فقط TOPSIS را با وزن دستی اجرا کنید — روش دیگری لازم نیست."` |
| `colDBest` | `"D⁺ (بهترین)"` |
| `colDWorst` | `"D⁻ (بدترین)"` |
| `colCloseness` | `"نزدیکی (C*)"` |
| `errors.topsis_denom_zero` | `"مخرج نرمال‌سازی ستون TOPSIS صفر است — مقادیر ستون یک معیار نمی‌توانند همگی صفر باشند."` |

---

## Validation Rules Summary (TOPSIS Path)

| Rule | Source | Error Code | Path |
|------|--------|------------|------|
| Shared ranking contract (names, dims, weights, types, matrix) | `validators.validate_ranking_inputs()` | Various | Various |
| All-zero benefit column | `validators.validate_ranking_inputs()` (AC13) | `benefit_column_all_zero` | `criteria.{j}` |
| TOPSIS column denom = 0 | `topsis_service._check_topsis_denominators()` | `topsis_denom_zero` | `criteria.{j}` |
| AC16 closeness = 0.5 when d_best + d_worst = 0 | `topsis_service.compute_topsis()` | *(no error; produces `0.5`)* | — |
| Method not in selected_methods | `execution_service.create_run()` | `method_not_selected` | `method` |
| Run immutability | `DecisionRunViewSet.partial_update/update/destroy` | `run_immutable` | — |
