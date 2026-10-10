# Implementation Plan: Decision Support SAW Ranking (Phase 2)

**Branch**: `019-decision-saw` | **Date**: 2026-10-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/019-decision-saw/spec.md`

## Summary

Deliver **independent SAW ranking** on the Phase 1 `decision_support` shell: a pure `saw_service` (port SAW path from [09-ranking-reference.md](../../docs/decision-support/09-ranking-reference.md) / [03-saw.md](../../docs/decision-support/03-saw.md)) plus shared `normalize_weights`; replace stub execution for `method=saw` with validate → compute → append immutable `DecisionRun` carrying frozen inputs (raw + optional normalized weights) and SAW scores/order under the spec’s **interim ordinal rank** policy. Expose ranking input persistence (weights, types, m×n matrix) via existing case PATCH; web adds shared editors (`WeightVectorEditor`, `CriterionTypeToggle`, `RectangularMatrixEditor`) composed in `SawMethodPanel` with `RunActionBar` + `RankingResultTable` — **no** client-side SAW math, **no** TOPSIS requirement (AC01). Pytest proves AC14 sample + AC09–AC13 guards + AC23–AC24/AC26 on the SAW path.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2), TypeScript (React Router 7 + Vite)  
**Primary Dependencies**: Existing `decision_support` app (Phase 1); DRF + `CodedValidationError`; `normalize_weights` in `services/weights.py`; TanStack Query; i18n `en`/`fa`  
**Storage**: PostgreSQL — extend live case JSON usage (already has `weights`/`types`/`performance_matrix`); `DecisionRun.result` becomes real SAW payload (no new tables required)  
**Testing**: pytest — `test_saw_service.py` (AC14, AC11 scores, AC13), API run tests (AC01, AC09–AC10, AC23–AC26); UI unit tests for editor/result helpers as needed; structural guard that views/React do not embed SAW formulas  
**Target Platform**: Velora monorepo (`apps/api/core/decision_support`, `apps/web`)  
**Project Type**: Web + API monorepo  
**Performance Goals**: SAW on ≤10×10 is interactive/sync; no Celery  
**Constraints**: Pure engine (no math in views/React); SAW-only execution; empty≠0; immutable runs; interim rank policy only (O01/O02 remain open as final policy); no auto weight import  
**Scale/Scope**: One engine module + execution-path upgrade; shared ranking UI components; one method panel on existing case page

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status |
|-----------|--------|
| I. Server-enforced authz / project isolation | Pass — reuse Phase 1 case/run routes + `view_decision_support` / `edit_decision_support`; no new cross-tenant paths |
| II. Data integrity end-to-end | Pass — live ranking fields → validators → `saw_service` → frozen snapshot + result; case PATCH never mutates prior runs |
| III. Bilingual UX | Pass — new editor/panel/result/validation strings in `en.json` / `fa.json` |
| IV. Explicit safe mutations | Pass — SAW success appends run only; failures create no run; runs stay immutable |
| V. Minimal coherent changes | Pass — extend `decision_support` services/UI; shared editors for later TOPSIS; no new app; no other engines |
| VI. Evidence-based verification | Pass — quickstart names pytest suites vs UI smoke; AC14 is automated |
| VII. Accessible practical UX | Pass — cell/field paths; keyboard-friendly numeric grids; clear validate→run feedback |

**Post-Phase 1 design re-check**: Pass — contracts define SAW result shape + interim ranks without closing O01/O02; AC13 issue code added; stub run retained for non-SAW methods; UI inventory components are thin wrappers over case PATCH + run POST.

## Project Structure

### Documentation (this feature)

```text
specs/019-decision-saw/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── saw-engine.md
│   ├── saw-runs.md
│   └── ranking-inputs.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks — NOT created here
```

### Source Code (touched)

```text
apps/api/core/decision_support/
  services/
    weights.py                 # existing — keep shared normalize
    validators.py              # ensure AC09–AC10/AC13 paths align with engine
    saw_service.py             # NEW pure SAW engine
    execution_service.py       # branch: saw → real engine; others stub/reject as today
  views.py / serializers.py    # thin; no formulas
  tests/
    test_saw_service.py        # NEW AC14, AC11 scores, AC13, cost zeros
    test_saw_api.py            # NEW run SAW AC01/AC23–AC26; no TOPSIS side-effect
    test_runs_immutability.py  # extend or mirror for real SAW results
    test_no_math_in_views.py   # OPTIONAL structural guard (grep/AST)

apps/web/src/
  app/lib/api/decision-support.ts   # patch ranking fields; run SAW; types for result
  app/routes/project-decision-support.tsx  # wire SawMethodPanel when saw selected
  components/decision-support/
    WeightVectorEditor.tsx
    CriterionTypeToggle.tsx
    RectangularMatrixEditor.tsx
    RankingResultTable.tsx
    RunActionBar.tsx
    SawMethodPanel.tsx
    # reuse ValidationIssueList, ExecutionHistoryList, InputSnapshotViewer
  locales/en.json, fa.json
```

**Structure Decision**: Stay inside **`decision_support`** (Principle V). Split sample `rank_options` into **`compute_saw(...)` only** — never call TOPSIS from this path. UI: shared ranking editors under `components/decision-support/`; `SawMethodPanel` is the only SAW-specific composition; TOPSIS panel deferred to Phase 3 reusing the same editors.

## Complexity Tracking

None — engine + execution branch + shared editors are the minimum coherent slice for AC01/AC14.

## Implementation Phases

1. **Pure SAW + tests** — `saw_service.compute_saw`; AC14 fixture; AC11 score equality; AC13 / cost-zero rejects with paths.
2. **Execution path** — `create_run` for `saw`: validate ranking → normalize → compute → snapshot (+ `weights_normalized`) → `result.status=ok`, `engine=saw`, ordered rows; keep stub for other methods; pytest AC01/AC23–AC26.
3. **Case ranking fields API/UI data** — ensure PATCH persists weights/types/matrix; client types + hydrate on case load.
4. **Shared ranking UI + SawMethodPanel** — editors, RunActionBar, RankingResultTable, i18n; wire into project case page.
5. **Guards + polish** — structural no-math checks; spectacular/docs; quickstart verification pass.
