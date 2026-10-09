# Implementation Plan: Earned Value & Project Control (EVM)

**Branch**: `014-earned-value-control` | **Date**: 2026-10-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/014-earned-value-control/spec.md` (FR-EVM gap closure)

## Summary

Extend the existing project-level EVM spine (`schedule.services.evm_service` + `progress/kpis/`) so PV/EV/AC, variances, indices, and common-method finish forecasts are **valid only with locked baselines**, use **approved/versioned measurement progress for EV**, expose explicit **not-computable / unregistered** states (never misleading zeros), and support **phase and CBS slices with project roll-up**—without forking a parallel EVM product or redesigning the economic inflation engine.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2), TypeScript (React Router 7)  
**Primary Dependencies**: DRF, drf-spectacular, TanStack Query; apps `schedule`, `cost_control`, `projects`, `wbs`; reuse progress measurement (009) and budget versions (010)  
**Storage**: PostgreSQL (UUID PKs); EVM primarily **computed on read** with existing KPI cache invalidation; no new ledger of PV/EV/AC rows in v1  
**Testing**: pytest + pytest-django per gap (baseline gate, not-computable, phase/CBS, EV≠AC); UI smoke on progress KPI grid after API green  
**Target Platform**: Velora monorepo (`apps/api/core`, `apps/web`)  
**Project Type**: Web + API monorepo  
**Performance Goals**: Project EVM stay O(activities + budget/cost aggregates) with cache ≤30 min (existing); phase/CBS slice O(nodes × local aggregates); force_refresh supported  
**Constraints**: Project tenancy + `view_dashboard` (or equivalent progress view perm); bilingual not-computable labels; multi-currency totals only with explicit conversion; do not equate EV to AC/IPC  
**Scale/Scope**: Extend `evm_service` + progress KPI contract; phase/CBS report endpoints; progress UI validity banners; consume measurement approval + schedule/budget lock state

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status |
|-----------|--------|
| I. Server-enforced authz / project isolation | Pass — routes under `/projects/{uuid}/`; reuse `IsProjectMember` + `HasProjectPermission` |
| II. Data integrity end-to-end | Pass — EV tied to approved measurement versions; BAC from control/locked budget; AC from ActualCost; invalidate caches on progress/cost/baseline change |
| III. Bilingual UX | Pass — not-computable, unregistered, baseline-unlocked strings in `en.json` / `fa.json` |
| IV. Explicit safe mutations | Pass — this feature is mostly read/report; no silent rewrite of historical EV when method changes without approval |
| V. Minimal coherent changes | Pass — extend `schedule` EVM + progress UI; read cost_control/wbs; do not create parallel EVM app |
| VI. Evidence-based verification | Pass — pytest per FR gap; name suites in quickstart |
| VII. Accessible practical UX | Pass — explicit incomplete/unlocked states; no fake SPI/CPI = 1.0 |

**Post-Phase 1 re-check**: Pass — design is additive computed reports + status flags; no unjustified new bounded contexts.

## Project Structure

### Documentation (this feature)

```text
specs/014-earned-value-control/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── evm-report.md
│   ├── evm-by-phase.md
│   └── evm-by-cbs.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks — NOT created here
```

### Source Code (touched)

```text
apps/api/core/schedule/
  services/evm_service.py              # validity flags, approved EV, not-computable semantics
  services/evm_slice_service.py        # NEW: phase (WBS) + CBS aggregation helpers
  services/progress_service.py         # ensure approved-progress feed for EV; cache invalidation
  progress_views.py / urls.py          # extend kpis; add phase/CBS report endpoints
  serializers.py                       # response shapes with status enums
  tests/test_evm_baseline_gate.py
  tests/test_evm_not_computable.py
  tests/test_evm_approved_progress.py
  tests/test_evm_phase_cbs.py
  ENDPOINTS.md

apps/api/core/cost_control/
  models.py                            # read BudgetVersion/Budget/ActualCost/CBS (no fork)
  # optional thin helpers if BAC-by-cbs already partial elsewhere

apps/web/src/
  app/lib/api/progress.ts              # typed EVM report + slice clients
  app/routes/project-progress.tsx      # validity banner; not-computable labels; PV/EV/AC cards
  components/progress/EvmReportPanel.tsx   # NEW or extend KPI grid
  components/progress/EvmSliceTable.tsx    # phase / CBS tables
  locales en.json / fa.json
```

**Structure Decision**: Keep EVM in `schedule` (existing `compute_evm` + progress dashboard). Cost and CBS data are read from `cost_control`. UI stays on project progress (primary) with optional deep-link from economic forecast panel for standard (non-inflation) EVM consistency.

## Complexity Tracking

None — additive semantics and slice reports on the existing EVM spine.

## Implementation Phases

1. **P1 Validity + not-computable** — Baseline lock/control-budget gate; status flags; EV from approved progress; CPI/SPI/EAC chain not-computable rules; UI labels (FR-001, 005–008).
2. **P1 EV integrity** — Never substitute AC/IPC for EV; consume measurement version from 009 (FR-007, 009; SC-005–006).
3. **P2 Multi-level** — Phase (WBS phase-level) and CBS slice reports + project roll-up; multi-currency guard (FR-004, 010).
4. **Polish** — ENDPOINTS.md, cache invalidation on baseline/progress/cost changes, locales, pytest subset + progress UI smoke.
