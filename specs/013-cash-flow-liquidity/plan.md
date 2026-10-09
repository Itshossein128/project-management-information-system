# Implementation Plan: Cash Flow & Liquidity Allocation Gap Closure

**Branch**: `013-cash-flow-liquidity` | **Date**: 2026-10-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/013-cash-flow-liquidity/spec.md` (FR-CASH gap closure)

## Summary

Extend the existing `cash_flow` app so projected monthly inflows/outflows are **domain-fed** from approved IPC collection dues (011) and commitment dues / planned payments (012), expose monthly and suggested net cash need separately from actuals, and add **portfolio** liquidity scoring, allocation proposals, auditable decisions, double-allocation warnings, and a saved manual simulation—without replacing the current transaction ledger or redesigning procurement block liquidity.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2), TypeScript (React Router 7)  
**Primary Dependencies**: DRF, drf-spectacular, TanStack Query; apps `cash_flow`, `contracts`, `cost_control`, `alerts`  
**Storage**: PostgreSQL (UUID PKs, soft-delete audit models)  
**Testing**: pytest + pytest-django for each gap; prefer failing test before implementation (same discipline as 012); UI smoke after API green  
**Target Platform**: Velora monorepo (`apps/api/core`, `apps/web`)  
**Project Type**: Web + API monorepo  
**Performance Goals**: Projection rebuild O(IPCs + commitments + payments in range); portfolio proposal O(projects × months) with aggregates; cache project monthly/projection like existing cashflow caches  
**Constraints**: Keep project tenancy; portfolio endpoints require org/portfolio permission (reuse or add `view_cashflow` at portfolio scope); no bank/treasury integration; equal score weights in v1; double-allocation = warn + ack  
**Scale/Scope**: Projection service + net-need API; new score/proposal/decision/simulation models; portfolio report route; project cash UI + portfolio liquidity page

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status |
|-----------|--------|
| I. Server-enforced authz / project isolation | Pass — project routes under `/projects/{uuid}/`; portfolio routes list only projects the user can view |
| II. Data integrity end-to-end | Pass — projection sources traced to IPC/commitment; decisions audited; migrations for new entities |
| III. Bilingual UX | Pass — new strings in `en.json` / `fa.json` |
| IV. Explicit safe mutations | Pass — decision requires owner+rationale; double-alloc warn+ack; no silent overwrite of domain projection by manual forecast |
| V. Minimal coherent changes | Pass — extend `cash_flow`; read from contracts/cost_control; do not fork ledger |
| VI. Evidence-based verification | Pass — pytest per gap; name suites in verification |
| VII. Accessible practical UX | Pass — clear empty states (no IPC → unregistered inflow; zero pool → empty proposal) |

**Post-Phase 1 re-check**: Pass — design stays additive; portfolio scope filtered by membership.

## Project Structure

### Documentation (this feature)

```text
specs/013-cash-flow-liquidity/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── projected-cash-series.md
│   ├── net-need.md
│   ├── liquidity-allocation.md
│   └── portfolio-report.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks — NOT created here
```

### Source Code (touched)

```text
apps/api/core/cash_flow/
  models.py                 # ProjectPriorityScore, LiquidityPool cycle, AllocationProposal/Line,
                            # AllocationDecision/Line, AllocationSimulation; optional ProjectionSnapshot
  migrations/000X_*.py
  services/cashflow_service.py          # keep actuals/manual forecast
  services/projection_service.py        # NEW: IPC + commitment fed monthly projected in/out
  services/net_need_service.py          # NEW: monthly net + FR-004 suggested need
  services/allocation_service.py        # NEW: scores, proposal, decision, overlap warn, simulation
  services/portfolio_report_service.py  # NEW
  views.py / urls.py / serializers.py
  tests/test_projection_series.py
  tests/test_net_need.py
  tests/test_allocation_proposal_decision.py
  tests/test_double_allocation_warn.py
  tests/test_portfolio_cash_report.py
  ENDPOINTS.md

apps/web/src/
  app/lib/api/cashflow.ts
  app/routes/project-cash-flow.tsx       # projected vs actual + net need panels
  components/cashflow/*                 # ProjectionPanel, NetNeedPanel
  app/routes/portfolio-liquidity.tsx    # NEW (or org-level route if pattern exists)
  components/cashflow/allocation/*      # proposal, decision form, simulation
  locales en.json / fa.json
```

**Structure Decision**: Stay in `cash_flow` app; portfolio APIs under `/api/v1/cash-flow/portfolio/...` (global, membership-filtered) to avoid fake project nesting. UI: extend project cash-flow page; add portfolio liquidity route consistent with existing org/portfolio navigation if present, else under a finance section.

## Complexity Tracking

None — additive domain on existing cash_flow spine. Portfolio is a new surface but reuses project membership filtering.

## Implementation Phases

1. **P1 Projection + net need** — Build monthly projected in/out from IPC dues + commitment dues/payments; separate from actuals; suggested net need (FR-001–004).
2. **P2 Scores + proposal + decision** — Priority scores, available pool, ranked proposal, decision with owner/rationale/impact (FR-005–007).
3. **P2 Double-alloc + simulation** — Overlap warning + ack; save/compare simulation (FR-008).
4. **P2 Portfolio report + UI** — Portfolio cash/need/allocations; project + portfolio UI polish (FR-009).
5. **Polish** — ENDPOINTS.md, alerts hook optional (`cash_gap` from projected need), locales, pytest subset.
