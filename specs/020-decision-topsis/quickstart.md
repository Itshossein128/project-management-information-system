# Quickstart Validation Guide: Decision Support TOPSIS Ranking (Phase 3)

**Feature**: `020-decision-topsis` | **Date**: 2026-10-10

This guide describes how to validate the TOPSIS feature end-to-end after implementation. It covers prerequisites, service startup, and the automated and manual checks that constitute completion evidence.

> [!IMPORTANT] Per Constitution Principle VI, completion MUST NOT be claimed from source inspection or a single narrow test alone. This guide enumerates the required evidence categories. Run every category and record outcomes in the completion report.

---

## Prerequisites

### Services (must be running)

```bash
sudo pg_ctlcluster 16 main start          # PostgreSQL on port 5433
sudo redis-server /etc/redis/redis.conf --daemonize yes  # Redis on 6379
pnpm dev:api                              # Django API on port 8000
pnpm dev:web                              # Vite on port 5173 (for browser checks)
```

### Environment

```bash
# From project root — verify .env has:
AUDIT_LOG_ASYNC=false
CELERY_TASK_ALWAYS_EAGER=true
DATABASE_URL=postgres://ipcas:ipcas@localhost:5433/ipcas
```

### DB setup (fresh only)

```bash
pnpm db:migrate
pnpm db:seed   # creates admin +10000000001 / devpass123, sample projects
```

---

## Category 1 — Pure Engine Tests (pytest)

**What it proves**: TOPSIS math is correct (AC15, AC16); engine is isolated from SAW (AC01 unit).

**Run**:
```bash
cd apps/api/core
set -a && source /workspace/.env && set +a
../.venv/bin/python -m pytest decision_support/tests/test_topsis_service.py -v
```

**Expected passing tests**:

| Test | Acceptance ID | Fixture | Expected Result |
|------|--------------|---------|-----------------|
| `test_ac15_acceptance_sample` | AC15 | الف/ب, [10,100]/[5,200], benefit/cost, w=[1,1] | الف: closeness=1.0, rank=1; ب: closeness=0.0, rank=2 |
| `test_ac16_zero_total_distance` | AC16 | Single alt OR two identical rows | closeness=0.5 for each |
| `test_ac01_no_saw_in_topsis_output` | AC01 | Any valid TOPSIS call | Output dict has no `SAW`/`saw` key; no ideal-solution machinery from SAW module imported |
| `test_ac04_zero_denom_rejected` | FR-004 | Column of all-zeros | `CodedValidationError` with `topsis_denom_zero` at `criteria.{j}`; no run created |
| `test_equal_closeness_stable_order` | O01 interim | Equal closeness rows | Stable input order preserved; ordinal ranks 1, 2, … |
| `test_ac11_scaled_weights_same_scores` | AC11 | weights=[2,3] vs [20,30] | Identical closeness scores |

---

## Category 2 — API Integration Tests (pytest)

**What it proves**: TOPSIS runs through the full Django stack (serializer → execution service → DB); independence (AC01, AC03/AC25); immutability (AC23/AC24); error contract (AC26).

**Run**:
```bash
cd apps/api/core
set -a && source /workspace/.env && set +a
../.venv/bin/python -m pytest decision_support/tests/test_topsis_api.py -v
```

**Expected passing tests**:

| Test | ACs | Scenario | Expected |
|------|-----|----------|----------|
| `test_ac01_topsis_only_no_saw_run` | AC01 | POST run {method:topsis} on topsis-only case | 201; result.engine=topsis; result.status=ok; zero SAW runs created |
| `test_ac15_api_acceptance_sample` | AC15 | doc-10 fixture via API | الف closeness=1.0 rank=1; ب closeness=0.0 rank=2 |
| `test_ac16_api_zero_distance` | AC16 | Single-alternative case | closeness=0.5 in result |
| `test_topsis_denom_zero_rejected` | FR-004/AC26 | All-zero column in matrix | 400 with issues[].code=topsis_denom_zero; DecisionRun.objects.count unchanged |
| `test_ac03_ac25_saw_and_topsis_independent` | AC03, AC25 | SAW run then TOPSIS run on same case | Two DecisionRun records; methods differ; neither result mutates the other |
| `test_ac23_ac24_topsis_immutability` | AC23, AC24 | Run TOPSIS; patch weights; run TOPSIS again; GET first run | First run's input_snapshot and result unchanged; two independent runs exist |
| `test_ac26_validation_error_no_run` | AC26 | Invalid matrix (empty cell, wrong dims) | 400; no run created |
| `test_method_not_selected_rejected` | — | POST {method:topsis} on saw-only case | 400 with method_not_selected |

---

## Category 3 — Existing Tests Must Stay Green (no regression)

**Run**:
```bash
cd apps/api/core
set -a && source /workspace/.env && set +a
../.venv/bin/python -m pytest decision_support/tests/ -v
```

**Critical tests that must still pass after Phase 3 changes**:
- `test_saw_service.py::test_ac01_no_topsis_in_output_or_module` — SAW module still has no TOPSIS machinery
- `test_saw_api.py::test_ac01_ac14_saw_only_run` — SAW result unchanged
- `test_saw_api.py::test_ac23_ac24_saw_immutability` — SAW immutability unchanged
- `test_runs_immutability.py` — All immutability scenarios

---

## Category 4 — Frontend Type Check

**What it proves**: TypeScript types are coherent; no regression from `RankingResultTable` change.

```bash
pnpm typecheck
```

> [!NOTE] There is a pre-existing `tsc` error in `DailyReportForm.tsx`. The typecheck command may exit non-zero for that reason regardless. Confirm the error count does not *increase* — only the pre-existing error should remain.

The key new assertions (enforced by the discriminated union):
- `<RankingResultTable method="saw" ranking={sawRows} />` compiles (no `extraColumns` required)
- `<RankingResultTable method="topsis" ranking={topsisRows} extraColumns={[...]} />` compiles
- Passing `extraColumns` to `method="saw"` is a type error (enforced by `never`)

---

## Category 5 — No-Math-in-Panel Test

**What it proves**: FR-005 — no TOPSIS math in the UI layer.

```bash
# From repo root (vitest):
pnpm --filter @building-management/web test --run components/decision-support/no-client-topsis-math.test.ts
```

**Expectation**: Test reads `TopsisMethodPanel.tsx?raw` as a string and asserts no occurrence of `d_best`, `d_worst`, `ideal_best`, `Math.sqrt`, `sqrt(`, etc.

---

## Category 6 — Browser Validation (Manual)

**What it proves**: UI wiring is correct; bilingual labels; separate result tables; no blended rank.

**Setup**: Start services per prerequisites. Log in as `+10000000001` / `devpass123`. Open an existing project.

### Scenario A — TOPSIS-only run (AC01, AC15, US1)

1. Navigate to Decision Support for any project
2. Create a new case: title "TOPSIS Validation", methods: **TOPSIS only** (no SAW)
3. Add criteria: `تجربه` (benefit), `قیمت` (cost)
4. Add alternatives: `پیمانکار الف`, `پیمانکار ب`
5. Set weights: `1`, `1`
6. Fill matrix: row الف = `[10, 100]`, row ب = `[5, 200]`
7. Save case
8. Click "Run TOPSIS" in the TopsisMethodPanel

**Expected**:
- Result table shows: الف rank 1 closeness 1.0, ب rank 2 closeness 0.0
- Distance columns (D⁺, D⁻) are visible in the result table
- No SAW result appears (SAW panel is not shown)
- Execution history shows 1 run with method TOPSIS
- Result is correct in Persian and English locales (switch via locale selector)

### Scenario B — SAW + TOPSIS side-by-side (AC03, AC25, US3)

1. Use the same case from Scenario A (or create a new one with both SAW and TOPSIS selected)
2. Run SAW (using SawMethodPanel)
3. Run TOPSIS (using TopsisMethodPanel)
4. Observe the case page

**Expected**:
- Two separate panels or clearly labeled sections: one for SAW, one for TOPSIS
- SAW panel shows SAW scores/ranks only
- TOPSIS panel shows TOPSIS closeness/distances/ranks only
- No blended rank column or combined table
- Execution history shows 2 runs with different methods

### Scenario C — AC16 edge case (single alternative)

1. Create a case with TOPSIS only; 1 alternative; 1 criterion (benefit); weight=1; matrix=[[5]]
2. Run TOPSIS

**Expected**: closeness = 0.5, rank = 1

### Scenario D — All-zero column rejection (FR-004)

1. Create a case with 1 criterion (benefit), 2 alternatives; matrix=[[0],[0]]; TOPSIS selected
2. Save case; click "Run TOPSIS"

**Expected**: Error displayed showing `topsis_denom_zero` or equivalent localized message; no run created in history

### Scenario E — Re-run appends; prior run unchanged (AC24)

1. Run TOPSIS on a valid case → verify result
2. Change a weight value and run again
3. Check execution history → 2 TOPSIS runs
4. Click the first run in history → input snapshot must reflect the original weights

---

## Completion Criteria Mapping

| Acceptance ID | Evidence Category | Notes |
|--------------|-------------------|-------|
| AC15 (TOPSIS sample) | Category 1, 2, 6A | Numeric correctness |
| AC16 (closeness=0.5) | Category 1, 2, 6C | Edge case |
| AC01 (TOPSIS-only) | Category 1, 2, 6A | Independence from SAW |
| AC03/AC25 (separate results) | Category 2, 6B | No blended rank |
| AC23/AC24 (immutability) | Category 2, 6E | Frozen snapshot |
| AC26 (error location) | Category 2, 6D | Cell/field path |
| FR-005 (no math in UI) | Category 5 | Source scan |
| FR-012 (bilingual) | Category 6A | Manual locale switch |
| SC-001 to SC-007 | Category 1, 2, 6 | Full coverage |
