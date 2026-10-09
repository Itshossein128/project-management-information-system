# Quickstart: Earned Value & Project Control (EVM)

## Prerequisites

- Postgres + Redis running; API venv ready; root `.env` sourced
- Migrated DB; sample project with activities, weights, and (for full path) locked schedule baseline + approved control budget version
- Feature 009 measurement approval path available; 010 budget versions; 012 ActualCost rows

## Backend verify

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  schedule/tests/test_evm_baseline_gate.py \
  schedule/tests/test_evm_not_computable.py \
  schedule/tests/test_evm_approved_progress.py \
  schedule/tests/test_evm_phase_cbs.py \
  schedule/tests/test_progress.py \
  -q
```

## Manual API smoke

1. Unlocked baseline → `GET .../progress/kpis/` → `warnings` contains `baseline_not_locked`, `validity` ≠ `valid`.
2. No `approved_progress` → `ev.status=unregistered`; `cpi.status=not_computable` (not a numeric CPI).
3. Approve progress + post ActualCost → EV/AC registered; with PV > 0 and AC > 0, SPI/CPI computable; EAC = BAC/CPI.
4. Assert EV ≠ AC when only AC changes (no progress change).
5. `GET .../progress/evm/by-phase/` and `.../evm/by-cbs/` → slice rows; empty slices not SPI=1.0.
6. Mixed currency without conversion → aggregation blocked / warning (FR-010).

## UI

- Project → Progress: validity banner; PV/EV/AC cards with unregistered/not-computable labels (fa/en).
- Phase and CBS tables under the KPI grid.
- Economic “EVM forecast” tab still shows inflation overlay but base SPI/CPI match progress KPIs when CPI computable.

## Expected outcomes

| Check | Pass criteria |
|-------|----------------|
| SC-001 | Locked + progress + AC → project EVM readable in &lt; 2 min |
| SC-002 | Insufficient data → dependent index not_computable in 100% of pytest cases |
| SC-003 | Phase + CBS endpoints return slices in same session |
| SC-004 | Unlocked baseline → warning + not fully valid |
| SC-005 | EV never equals AC solely because AC exists |
| SC-006 | Unapproved measurement edit does not change historical approved EV feed |
