# Implementation Plan: Decision Support TOPSIS Ranking (Phase 3)

**Branch**: `020-decision-topsis` | **Date**: 2026-10-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/020-decision-topsis/spec.md`

## Summary

Phase 3 delivers an independent TOPSIS ranking engine that can execute without SAW. It reuses the Phase 2 case shell, shared ranking editors (`WeightVectorEditor`, `CriterionTypeToggle`, `RectangularMatrixEditor`, `RunActionBar`), and extends `RankingResultTable` with optional extra columns for distances. The backend adds a pure `topsis_service.py`, wires it into `execution_service.py`, and replaces the stub `result={'status':'stub'}` with real engine output. The frontend adds `TopsisMethodPanel` alongside `SawMethodPanel` and extends the route to render it when TOPSIS is selected.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x / React 18 (frontend)

**Primary Dependencies**:
- Backend: Django 4.2.11, Django REST Framework, `math` stdlib (no NumPy — matches sample)
- Frontend: React Router 7, TanStack Query, react-i18next, Tailwind CSS, Radix UI / shadcn

**Storage**: PostgreSQL 16 on port 5433. No schema changes needed — `DecisionRun.result` (JSONField) already stores the ranking payload; the TOPSIS result shape is a superset of the SAW shape (extra `d_best`/`d_worst` fields per row). No new migrations required.

**Testing**: `pytest` + `pytest-django` (backend); vitest (frontend unit tests for `.test.ts` files already in `components/decision-support/`)

**Target Platform**: Linux server (Django API on port 8000, Vite dev on 5173)

**Project Type**: Web service (monorepo: `apps/api` + `apps/web`)

**Performance Goals**: No specific throughput goals. TOPSIS on 10×10 matrix is O(m×n) — negligible latency.

**Constraints**:
- No NumPy; use `math.sqrt` only (matches reference sample and avoids additional deps)
- Django must stay pinned to 4.2.11
- No model migrations (result shape is stored as JSON)
- Open items O01/O02 remain open; only interim contract is implemented

**Scale/Scope**:
- Matrix max 10×10; 1–10 alternatives and criteria
- No SAW invocation from TOPSIS path (AC01 hard constraint)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Gate | Assessment |
|-----------|------|------------|
| I — AuthZ | TOPSIS run endpoints must enforce `edit_decision_support` | ✅ Reuses existing `DecisionRunViewSet` gating; no new endpoint |
| II — Data Integrity | JSON result shape change in `DecisionRun.result` | ✅ No migration needed; JSON field absorbs new row shape without schema change |
| III — Bilingual | TOPSIS panel labels, distance column headers, error codes in `en.json` + `fa.json` | ✅ Enumerated in data-model; must be delivered before completion claim |
| IV — Safe Mutations | TOPSIS runs are append-only; existing immutability enforcement applies | ✅ `DecisionRunViewSet.partial_update/update/destroy` all raise `run_immutable` |
| V — Minimal Coherent Changes | `TopsisMethodPanel` composes existing editors; `RankingResultTable` extended via props, not forked | ✅ Explicitly designed this way |
| VI — Evidence-Based Verification | Must prove via pytest (AC15, AC16, AC01, AC03/AC25, AC23/AC24) and UI wiring evidence | ✅ Test plan in quickstart.md |
| VII — Accessible UX | Distance columns follow same table pattern; bilingual | ✅ Same `<table>` structure as SAW result |

**Post-Phase 1 re-check**: No design decision in Phase 1 artifacts creates a violation. The TOPSIS result row is a strict superset of `SawRankingRow` (adds `d_best`, `d_worst`, `closeness`); the `RankingResultTable` extension via union type does not break SAW display.

## Project Structure

### Documentation (this feature)

```text
specs/020-decision-topsis/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   ├── topsis-run-result.md
│   └── topsis-ranking-row.md
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
apps/api/core/decision_support/
├── services/
│   ├── validators.py          # EXISTING — shared ranking contract (AC05–AC12)
│   ├── weights.py             # EXISTING — normalize_weights helper
│   ├── saw_service.py         # EXISTING — pure SAW engine
│   ├── topsis_service.py      # NEW — pure TOPSIS engine (FR-001 to FR-008)
│   ├── execution_service.py   # MODIFY — wire TOPSIS; replace stub branch
│   └── case_service.py        # EXISTING — no change needed
├── tests/
│   ├── test_saw_service.py    # EXISTING
│   ├── test_saw_api.py        # EXISTING
│   ├── test_topsis_service.py # NEW — AC15, AC16, AC01 independence, AC04 zero-denom
│   └── test_topsis_api.py     # NEW — AC15, AC16, AC01 (no SAW side-effect), AC03/AC25, AC23/AC24
├── models.py                  # EXISTING — no change
├── serializers.py             # EXISTING — no change (DecisionRunSerializer already generic)
├── views.py                   # EXISTING — no change (DecisionRunViewSet already generic)
└── urls.py                    # EXISTING — no change

apps/web/src/
├── components/decision-support/
│   ├── RankingResultTable.tsx           # MODIFY — extend Props for TOPSIS extra columns
│   ├── TopsisMethodPanel.tsx            # NEW — composes shared editors + TOPSIS run/result
│   ├── ranking-result-rows.ts           # MODIFY — add TopsisRankingRow type
│   └── no-client-topsis-math.test.ts   # NEW — AC01 mirror: no math in TopsisMethodPanel
├── app/lib/api/
│   └── decision-support.ts             # MODIFY — add TopsisRankingRow type; update DecisionRunResult
└── app/routes/
    └── project-decision-support.tsx    # MODIFY — render TopsisMethodPanel when topsis selected

apps/web/src/app/locales/
├── en.json                     # MODIFY — add TOPSIS i18n keys
└── fa.json                     # MODIFY — add TOPSIS i18n keys (Persian)
```

**Structure Decision**: Web application (Option 2). TOPSIS follows the exact same file-per-service pattern as SAW. No new Django app, no new routes, no new models or migrations. All changes are additive within the existing `decision_support` app and `components/decision-support/` directory.

## Complexity Tracking

No Constitution Check violations requiring justification.
