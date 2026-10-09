# Research: Cash Flow & Liquidity Allocation Gap Closure

**Date**: 2026-10-09

## Findings

### Existing coverage (keep)

- `CashTransaction` (in/out, categories, `is_forecast`, optional IPC/contract, due/actual dates) and `CashFlowForecast` (manual monthly expected in/out).
- Services: monthly actual rollup, forecast vs actual, gap from **manual** forecasts, receivables/payables **totals** from approved unpaid IPCs.
- API under `/api/v1/projects/{id}/cash-flow/` (transactions, monthly, forecast, gap-analysis, receivables).
- IPC **pay** upserts an actual cash transaction; does not populate projected monthly series.
- UI: project cash-flow tabs (transactions / forecast / gap).
- Alert `cash_gap_detected` from manual forecast cumulative gaps.
- Commitment `due_date` + `Payment` (`paid_at`, posted) in `cost_control` — not yet consumed by `cash_flow`.
- IPC `planned_payment_date` / approved amounts / remaining receivable from 011.

### Gaps to close

1. Domain-fed **projected** monthly inflows (approved IPC remaining × due month) and outflows (commitment due / unpaid planned).
2. Monthly net need from projected series + **suggested** net need (FR-CASH-004).
3. Priority scores, allocation proposal, decisions, simulation, double-allocation warn.
4. Portfolio report surface.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Projection storage | **Computed on read** with optional cache; do not auto-write `CashTransaction(is_forecast=True)` rows for every IPC/commitment | Avoid dual-write drift; keep ledger for actuals + optional manual forecasts |
| Manual forecast | Remains; reported as `manual_forecast` series; never overwrites computed projection unless user explicitly sets period override flag later (v1: show side-by-side) | Spec FR-010 |
| Projected inflow source | Approved IPCs with remaining receivable > 0; month = `planned_payment_date` (fallback: period_end) | Aligns with 011 receivables |
| Projected outflow source | Approved commitments with `due_date` in month, amount minus posted payments (open commitment); plus draft/planned if only due_date exists | Aligns with 012 |
| Suggested net need | `due_open_commitments + essential_costs − certain_planned_receipts` for period; essential_costs = approved ActualCost with category in configurable set defaulting to labor/salary/site_overhead when tagged, else **0** and document in API meta | Spec assumption; avoid inventing tags |
| Score weights | Equal 0.25 each for urgency, return, recovery_speed, risk (0–100 inputs) | Spec assumption v1 |
| Incomplete scores | Exclude from auto-ranking; return `incomplete_score_projects` warning list | Spec AC |
| Available pool | Request body / cycle field `available_liquidity` entered by finance (not bank balance) | No treasury |
| Double allocation | Warn when new decision line overlaps project + overlapping date range with prior **active** decision; require `acknowledge_overlap` to save | Spec warn policy |
| Portfolio API | `GET /api/v1/cash-flow/portfolio/report/` and allocation endpoints under `/api/v1/cash-flow/portfolio/...` filtered to projects where user is active member with `view_cashflow` | Avoid fake project_pk |
| Permissions | Reuse `view_cashflow` / `edit_cashflow` for project; portfolio write needs `edit_cashflow` on all targeted projects or org finance role if present | Tenancy |
| Alerts | Optional follow-up: fire gap when projected cumulative need exceeds threshold; not blocking for MVP | Minimal |

## Alternatives considered

- **Materialize projection as CashTransaction rows** — sync complexity; rejected for v1.
- **Hard-block double allocation** — stricter than spec default; rejected (warn+ack).
- **Portfolio nested under a dummy project** — breaks tenancy model; rejected.
- **Reuse procurement liquidity report** — different meaning (block budget vs requisitions); rejected.

## NEEDS CLARIFICATION

None remaining — all Technical Context unknowns resolved above.
