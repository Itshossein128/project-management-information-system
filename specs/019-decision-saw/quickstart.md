# Quickstart: Decision Support SAW Ranking (Phase 2)

Validate Phase 2 against [spec.md](./spec.md). Builds on Phase 1 shell ([018 quickstart](../018-decision-case-shell/quickstart.md)).

## Prerequisites

- Phase 1 `decision_support` app migrated and permissions seeded
- PostgreSQL + Redis; API venv; root `.env` with `DATABASE_URL`
- Project member with `edit_decision_support`

## Automated checks (primary evidence)

From `apps/api/core` with env sourced:

```bash
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest decision_support/tests/test_saw_service.py -q
../.venv/bin/python -m pytest decision_support/tests/test_saw_api.py -q
../.venv/bin/python -m pytest decision_support/tests/test_runs_immutability.py -q
```

**Expect**:

| Suite | Covers |
|-------|--------|
| `test_saw_service` | AC14 sample scores/order; AC11 score equality for scaled weights; AC13 benefit all-zero; cost-zero reject; **no** TOPSIS output |
| `test_saw_api` | POST run `method=saw` → `result.engine=saw` + ranking; AC01 (response has no TOPSIS); invalid fixtures AC09/AC10/AC13 → 400 + issues path, **zero** new runs (AC26) |
| `test_runs_immutability` (extended) | Real SAW snapshot/result unchanged after case PATCH + second SAW run (AC23–AC24) |

Optional structural guard:

```bash
../.venv/bin/python -m pytest decision_support/tests/test_no_math_in_views.py -q
```

## Manual API smoke (optional)

Contracts: [saw-runs.md](./contracts/saw-runs.md), [saw-engine.md](./contracts/saw-engine.md)

1. Create/PATCH case with acceptance sample inputs and `selected_methods: ["saw"]` only.
2. `POST …/runs/` `{"method":"saw"}` → `201`; ranking scores `1.0` / `0.5`, order الف then ب; no TOPSIS fields.
3. `POST` with all-zero benefit column → `400` `benefit_column_all_zero`; run count unchanged.
4. PATCH one weight → second SAW run → GET first run unchanged.

## UI smoke (after SawMethodPanel)

1. Open project Decision Support → case with SAW selected.
2. Edit weights, types, m×n matrix via shared editors; save.
3. Run SAW → RankingResultTable shows name/score/rank; history lists the run.
4. Force invalid cell → ValidationIssueList shows path; no successful run.
5. Switch `fa` / `en` → panel/editor/result labels localized.

## Out of scope for this quickstart

- TOPSIS / AHP / DEMATEL / ISM engines  
- Auto weight import  
- Final shared-rank policy (O01)  

## Evidence categories (constitution VI)

| Claim | Evidence |
|-------|----------|
| SAW math AC14 / AC11 / AC13 | pytest `test_saw_service` |
| SAW-only run + locatable errors | pytest `test_saw_api` |
| Immutability with real results | pytest immutability (SAW) |
| No presentation-layer math | optional structural test + code review |
| Bilingual ranking UX | UI smoke / locale key review |
