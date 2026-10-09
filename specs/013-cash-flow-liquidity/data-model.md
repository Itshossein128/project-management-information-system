# Data Model: Cash Flow & Liquidity Allocation Gap Closure

## Existing (unchanged semantics)

### CashTransaction

Actual (and optional manual forecast-flagged) ledger rows. Remains source of **actual** monthly series.

### CashFlowForecast

Manual monthly expected in/out. Reported separately as `manual_forecast`; does not replace computed projection.

## Derived (not persisted as ledger): Projected monthly series

Computed by `projection_service` for a project and month range:

| Field | Notes |
|-------|-------|
| month | First of month |
| projected_inflow | Sum of remaining receivable on approved unpaid IPCs whose due month matches |
| projected_outflow | Sum of open commitment amounts (approved − posted payments) with `due_date` in month |
| net_need | projected_inflow − projected_outflow (negative ⇒ surplus) |
| sources | Optional detail lines: `{source_type, source_id, amount, due_date}` |

Empty inflow when no IPCs → series omits or marks `status: unregistered` for inflow (not silent zero-as-complete).

## ProjectPriorityScore (new)

| Field | Type | Notes |
|-------|------|-------|
| project | FK Project, unique active | One current scorecard per project |
| urgency | Decimal 0–100 | |
| return_score | Decimal 0–100 | Named to avoid Python `return` |
| recovery_speed | Decimal 0–100 | |
| risk | Decimal 0–100 | Higher = more risk (ranking may invert: use (100−risk) in composite) |
| composite | Decimal, computed | Equal weights: (urgency + return + recovery + (100−risk)) / 4 |
| notes | Text, blank | |
| updated_by | FK User | |

**Validation**: Each component 0–100; incomplete if any null → exclude from auto-rank.

## LiquidityAllocationCycle (new)

A decision window / pool snapshot.

| Field | Type | Notes |
|-------|------|-------|
| name | Char | e.g. "2026-Q4 liquidity" |
| period_start | Date | |
| period_end | Date | |
| available_liquidity | Decimal | Entered by finance |
| currency | Char(3) | Default org/project reporting currency |
| status | draft \| proposed \| decided \| closed | |
| created_by | FK User | |

## AllocationProposal / AllocationProposalLine (new)

| Proposal | Lines |
|----------|-------|
| cycle FK, generated_at, algorithm_note | project FK, suggested_amount, rank, composite_snapshot, need_snapshot |

Generated, not user-edited (re-generate replaces draft proposal for cycle).

## AllocationDecision / AllocationDecisionLine (new)

| Decision | Lines |
|----------|-------|
| cycle FK, owner FK User (**required**), rationale Text (**required**), decided_at, proposal FK null, acknowledge_overlap bool, created_by | project FK, amount, schedule_impact Text, cost_impact Text, period_start, period_end |

**Validation**:

- owner + rationale required (SC-002).
- If overlap with another active decision line (same project, overlapping [period_start, period_end]) and not `acknowledge_overlap` → `overlapping_allocation` warning/error.
- Sum of line amounts SHOULD be ≤ cycle.available_liquidity (warn if exceeded).

## AllocationSimulation (new)

| Field | Type | Notes |
|-------|------|-------|
| cycle | FK | |
| name | Char | |
| payload | JSON | `{lines: [{project_id, amount}], notes}` |
| created_by | FK | |
| created_at | | |

Comparable to current proposal via service (diff amounts by project).

## Relationships

```
Project 1──1 ProjectPriorityScore
LiquidityAllocationCycle 1──* AllocationProposal 1──* AllocationProposalLine
LiquidityAllocationCycle 1──* AllocationDecision 1──* AllocationDecisionLine
LiquidityAllocationCycle 1──* AllocationSimulation
IPC / Commitment ──(read-only feed)──→ projected monthly series
```

## Migration notes

- New tables only; no destructive change to `cash_transactions` / `cash_flow_forecasts`.
- Backfill: none required for scores (empty until entered).
