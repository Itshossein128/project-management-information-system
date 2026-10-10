# Implementation Plan: Decision Support AHP Criteria Weighting (Phase 4)

**Branch**: `021-decision-ahp` | **Date**: 2026-10-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/021-decision-ahp/spec.md`

## Summary

Phase 4 delivers an independent AHP criteria-weighting engine via pairwise comparison ($1 \le n \le 10$). AHP executes without requiring alternatives, ranking performance matrices, or SAW/TOPSIS execution (AC02). Running AHP never mutates the case's ranking weights or alternatives (AC04). The engine calculates geometric mean weights, principal eigenvalue $\lambda_{\max}$, Consistency Index $CI$, and Consistency Ratio $CR$ against Saaty's standard Random Index ($RI$) table. Inconsistent comparisons ($CR > 0.10$) trigger a prominent UI advisory alert while preserving audit run records. The frontend introduces `SquareMatrixEditor` in pairwise reciprocal mode, `CriteriaWeightTable`, and `AhpMethodPanel` integrated into the project decision support workspace.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x / React 18 (frontend)

**Primary Dependencies**:
- Backend: Django 4.2.11, Django REST Framework, `math` stdlib (pure calculation; no NumPy, matching existing services)
- Frontend: React Router 7, TanStack Query, react-i18next, Tailwind CSS, Lucide icons, Radix UI

**Storage**: PostgreSQL 16 on port 5433.
- `DecisionCase` already contains `ahp_matrix = models.JSONField(default=list, blank=True)`.
- `DecisionRun` already stores generic `input_snapshot` and `result` (JSONField).
- No database migrations or schema alterations required.

**Testing**: `pytest` + `pytest-django` (backend); Node test runner (`node --test`) for frontend unit tests in `apps/web/src/components/decision-support/`.

**Target Platform**: Linux server (Django API on port 8000, Vite dev on 5173).

**Project Type**: Monorepo (`apps/api` + `apps/web`).

**Performance Goals**: Instant evaluation ($O(n^2)$ with $n \le 10 \implies < 5\text{ms}$ execution latency).

**Constraints**:
- Pure calculation in `ahp_service.py`; zero math formulas in API views or client React.
- Django pinned to 4.2.11; do not install dev dependencies that upgrade Django.
- Coded, locatable errors with cell paths (`ahp_matrix.{j}.{k}`).
- Strict isolation: AHP run leaves ranking inputs (`weights`, `types`, `performance_matrix`) untouched (AC04).

## Constitution Check

| Principle | Gate | Assessment |
|---|---|---|
| I — AuthZ | AHP run endpoints enforce project permissions | ✅ Reuses `DecisionRunViewSet` and `HasProjectPermission` with `run_decision_method` |
| II — Data Integrity | No model migration needed; JSONField absorbs payload | ✅ `ahp_matrix` exists on `DecisionCase`; `DecisionRun.result` is JSON |
| III — Bilingual | AHP panel, CR warning banner, table headers, error codes localized in `en.json` & `fa.json` | ✅ Fully mapped in contracts & data-model |
| IV — Safe Mutations | AHP runs are append-only; immutable snapshots | ✅ Verified by `test_runs_immutability.py` and `test_ahp_api.py` |
| V — Minimal Coherent Changes | Reuses case workspace, nav, and history; extracts `SquareMatrixEditor` with pairwise mode | ✅ Cohesive extensions within `decision_support` |
| VI — Evidence-Based Verification | Verified via pytest (engine + API) and node test runner (frontend math audit) | ✅ Comprehensive test suite planned in quickstart.md |
| VII — Accessible UX | Keyboard-accessible grid inputs, clear tooltips, bilingual numbers | ✅ Built with accessible form and table patterns |

## Project Structure

### Documentation (this feature)

```text
specs/021-decision-ahp/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── ahp-pairwise-matrix.md
│   └── ahp-run-result.md
└── tasks.md             # Phase 2 output
```

### Source Code

```text
apps/api/core/decision_support/
├── services/
│   ├── ahp_service.py         # NEW — pure AHP engine (geometric mean, lambda_max, CI, CR, Saaty RI)
│   ├── validators.py          # MODIFY — add validate_ahp_inputs (dimensions, positive, diagonal 1, reciprocal)
│   └── execution_service.py   # MODIFY — wire AHP engine branch in create_run
└── tests/
    ├── test_ahp_service.py    # NEW — unit tests for AC17, AC18, n=1, n=2, validation guards
    └── test_ahp_api.py        # NEW — integration tests for AC02 (no alts), AC04 (no auto-feed), AC23-24 (immutability)

apps/web/src/
├── app/lib/api/
│   └── decision-support.ts            # MODIFY — add AhpWeightRow, AhpRunResult, update DecisionRunResult
├── components/decision-support/
│   ├── SquareMatrixEditor.tsx         # NEW — n×n grid with pairwise reciprocal auto-sync & diagonal 1
│   ├── SquareMatrixEditor.test.ts     # NEW — test reciprocal auto-update and diagonal locking
│   ├── CriteriaWeightTable.tsx        # NEW — displays criteria weights, % values, ranks, CR status
│   ├── CriteriaWeightTable.test.ts    # NEW — test weight table formatting and rendering
│   ├── AhpMethodPanel.tsx             # NEW — panel combining pairwise editor, run button, CR alert, weight table
│   └── no-client-ahp-math.test.ts     # NEW — verify zero calculation math in React components
├── app/routes/
│   └── project-decision-support.tsx   # MODIFY — render AhpMethodPanel when ahp selected
└── app/locales/
    ├── en.json                        # MODIFY — add AHP keys, headers, error messages
    └── fa.json                        # MODIFY — add Persian translations
```

## Complexity Tracking

- No schema migrations.
- Minimal dependencies: Python standard library `math` only.
- Frontend component `SquareMatrixEditor` designed to be reused in Phase 5 (DEMATEL) and Phase 6 (ISM).
