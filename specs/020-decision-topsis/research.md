# Research: Decision Support TOPSIS Ranking (Phase 3)

**Feature**: `020-decision-topsis` | **Date**: 2026-10-10

## R1 — TOPSIS Service Return Shape

**Decision**: `compute_topsis()` returns a dict with `ranking` (list of row dicts) and `weights_normalized` (list of floats), mirroring the SAW shape exactly, with extra fields per row.

**Rationale**: `SawMethodPanel` already passes `run.result.ranking` to `RankingResultTable`. Keeping the same key means `TopsisMethodPanel` can do the same without changing the API client or run serializer. The extra distance fields (`d_best`, `d_worst`, `closeness`) sit alongside `score` and `rank` in each row, so a union type on the frontend covers both without forking.

**Exact return shape**:
```python
{
    "ranking": [
        {
            "option": str,      # alternative name
            "d_best": float,    # distance to ideal best
            "d_worst": float,   # distance to ideal worst
            "score": float,     # closeness (d_worst / (d_best + d_worst)); 0.5 if both zero
            "rank": int,        # 1-based ordinal, stable on ties
        },
        ...
    ],
    "weights_normalized": [float, ...],
}
```

> [!NOTE] The `score` key (not `closeness`) is used so the SAW and TOPSIS result rows share the same structural key for the score column in `RankingResultTable`. The `closeness` semantic is documented in the contract and preserved in `d_best`/`d_worst`. This matches the "interim product choice" in the spec (section "Interim policy").

**Alternatives considered**:
- Using `closeness` as the key instead of `score`: Rejected — the result table already renders `row.score` for SAW; using the same key allows the shared table header "Score" to remain, with a TOPSIS-specific tooltip or label applied via the `method` prop.

---

## R2 — All-Zero Column Guard (TOPSIS Denominator Zero)

**Decision**: The all-zero column check for TOPSIS (denom = 0) is placed inside `topsis_service.py` as a TOPSIS-specific engine guard, **not** in `validators.py`.

**Rationale**:
- `validators.py` already checks `benefit_column_all_zero` for SAW (AC13). That check applies only to benefit columns because SAW's normalization divides by the column max — a zero max on a cost column is impossible (cost cells must be > 0 per AC09).
- TOPSIS vector normalization uses `sqrt(sum_i(x[i,j]^2))` for **all** columns regardless of type. A column of all-zeros produces denom = 0, which is a TOPSIS-specific error.
- Adding a `topsis_denom_zero` error to `validators.py` would couple a TOPSIS-specific rule to the shared contract, violating Constitution Principle V (minimal coherent changes).
- The existing pattern in `saw_service.py` confirms this: SAW's `benefit_column_all_zero` guard is also inside `compute_saw()`, not only in `validators.py`.

**Implementation location**: Early in `compute_topsis()`, after `validate_ranking_inputs()` passes:
```python
for j in range(n):
    denom = sqrt(sum(x[i][j] ** 2 for i in range(m)))
    if denom == 0.0:
        issues.append(_issue(
            'topsis_denom_zero',
            f'criteria.{j}',
            'TOPSIS column has zero normalization denominator (all cells are zero).',
        ))
raise_issues(issues)
```

**Error code**: `topsis_denom_zero` at path `criteria.{j}`. This is distinct from `benefit_column_all_zero` (which applies to SAW only); both appear in i18n as separate error strings.

**Alternatives considered**:
- Merging into `validate_ranking_inputs()` as a TOPSIS flag parameter: Rejected — adds coupling and makes the validator aware of method-specific math.

---

## R3 — RankingResultTable TypeScript Extension

**Decision**: Extend `RankingResultTable` with a `method: 'saw' | 'topsis'` union and an optional `extraColumns` prop that renders additional cells when present.

**Current code** ([RankingResultTable.tsx](file:///home/hossein/Desktop/projects/building-management/apps/web/src/components/decision-support/RankingResultTable.tsx#L4-L7)):
```typescript
type Props = {
  method: "saw";
  ranking: SawRankingRow[];
};
```

**Recommended new shape**:
```typescript
// In ranking-result-rows.ts (extend, not fork):
export type SawRankingRow = { option: string; score: number; rank: number };
export type TopsisRankingRow = SawRankingRow & {
  d_best: number;
  d_worst: number;
  // score = closeness; rank = ordinal
};
export type RankingRow = SawRankingRow | TopsisRankingRow;

// In RankingResultTable.tsx:
type ExtraColumn<T> = {
  key: keyof T & string;
  header: string;
  render?: (val: unknown) => ReactNode;
};

type Props<T extends RankingRow = SawRankingRow> = {
  method: "saw" | "topsis";
  ranking: T[];
  extraColumns?: ExtraColumn<T>[];
};
```

`TopsisMethodPanel` passes:
```tsx
<RankingResultTable
  method="topsis"
  ranking={ranking}
  extraColumns={[
    { key: "d_best", header: t("decisionSupport.colDistBest") },
    { key: "d_worst", header: t("decisionSupport.colDistWorst") },
  ]}
/>
```

**Rationale**: This is fully backward-compatible — `SawMethodPanel` passes no `extraColumns` and the table renders exactly as before. No forking of the component. Satisfies FR-011 and component inventory section C.

**Alternatives considered**:
- Full `renderRow` prop (render function): More flexible but overkill; extra columns approach covers all needed cases.
- Separate `TopsisResultTable` component: Explicitly prohibited by inventory ("No silent merge… separate instances of the same component").

---

## R4 — execution_service.py TOPSIS Wiring

**Decision**: Replace the stub TOPSIS branch with a real `compute_topsis()` call, parallel to the SAW branch.

**Current stub** ([execution_service.py](file:///home/hossein/Desktop/projects/building-management/apps/api/core/decision_support/services/execution_service.py#L71-L81)):
```python
elif method in RANKING_METHODS:
    # topsis (and future ranking) — Phase 1 stub until their engine phases
    validate_ranking_inputs(...)
    snapshot = _snapshot_from_case(case)
    result = {'status': 'stub', 'engine': None}
```

**Replacement** (only the TOPSIS branch changes; `elif method in RANKING_METHODS` stays for future methods):
```python
elif method == 'topsis':
    topsis_out = compute_topsis(
        case.criteria or [],
        case.alternatives or [],
        case.weights or [],
        case.types or [],
        case.performance_matrix or [],
    )
    snapshot = _snapshot_from_case(case, weights_normalized=topsis_out['weights_normalized'])
    result = {
        'status': 'ok',
        'engine': 'topsis',
        'ranking': topsis_out['ranking'],
    }
elif method in RANKING_METHODS:
    # future ranking methods
    validate_ranking_inputs(...)
    snapshot = _snapshot_from_case(case)
    result = {'status': 'stub', 'engine': None}
```

This ensures `method == 'topsis'` is checked before the generic `RANKING_METHODS` fallback, and SAW is never touched when TOPSIS runs (AC01 at the orchestration layer).

---

## R5 — i18n Keys Required

**Decision**: Add 6 new keys to the `decisionSupport` namespace in both `en.json` and `fa.json`.

### New keys — `en.json`

```jsonc
"decisionSupport": {
  // ... existing keys ...
  "topsisPanel Title": "TOPSIS ranking",              // key: topsis PanelTitle
  "topsisPanel Hint": "Run TOPSIS alone — no other method is required.",  // key: topsis PanelHint
  "colCloseness": "Closeness",
  "colDistBest": "Distance to best",
  "colDistWorst": "Distance to worst",
  "errors": {
    // ... existing error keys ...
    "topsis_denom_zero": "TOPSIS column cannot be all zeros (normalization denominator is zero)."
  }
}
```

> [!NOTE] Keys use camelCase: `topsisPanel Title` → corrected: `topsisPanelTitle`, `topsisPanelHint`

### New keys — `fa.json`

```jsonc
"decisionSupport": {
  "topsisPanelTitle": "رتبه‌بندی TOPSIS",
  "topsisPanelHint": "فقط TOPSIS را اجرا کنید — روش دیگری لازم نیست.",
  "colCloseness": "نزدیکی",
  "colDistBest": "فاصله تا بهترین حالت",
  "colDistWorst": "فاصله تا بدترین حالت",
  "errors": {
    "topsis_denom_zero": "ستون TOPSIS نمی‌تواند همگی صفر باشد (مخرج نرمال‌سازی صفر است)."
  }
}
```

**Rationale**: Separate `topsisPanelTitle` / `topsisPanelHint` from SAW equivalents; `colCloseness` may be used as an additional tooltip-level label for the `colScore` column when method is TOPSIS. `colDistBest`/`colDistWorst` are the `extraColumns` headers.

---

## R6 — No-Math-in-Panel Test Strategy

**Decision**: Add `no-client-topsis-math.test.ts` mirroring the existing `no-client-saw-math.test.ts`.

The test reads the source of `TopsisMethodPanel.tsx` as a string and asserts that TOPSIS calculation keywords (`sqrt`, `d_best`, `d_worst`, `ideal_best`, `closeness`) do not appear. This mechanically proves FR-005 (no math in views/UI) at CI level.

**Existing pattern** (from `no-client-saw-math.test.ts`):
```typescript
import sawSrc from "./SawMethodPanel.tsx?raw";
it("contains no SAW scoring math", () => {
  expect(sawSrc).not.toMatch(/\bsaw\b.*score/);
  // etc.
});
```

---

## Open Items (Inherited, Not Closed by Phase 3)

| Item | Status |
|------|--------|
| O01 — Tie rank policy (shared ties vs ordinal) | OPEN — Phase 3 implements ordinal (interim, consistent with SAW) |
| O02 — Distances in output (interim choice) | OPEN — Phase 3 includes distances per interim contract; not final |
| O03–O10 | OPEN — unchanged |
