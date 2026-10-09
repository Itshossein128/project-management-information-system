# Research: Earned Value & Project Control (EVM)

**Date**: 2026-10-09

## Findings

### Existing coverage (keep)

- `schedule.services.evm_service.compute_evm`: project BAC (sum of Budget lines), PV = BAC × planned %, EV = BAC × actual %, AC = sum ActualCost ≤ as_of; SV/CV; SPI/CPI null when PV/AC zero; EAC = BAC/CPI, ETC, VAC.
- `GET .../progress/kpis/` cached 30 min; also consumed by `projects.kpi_service` and `economic` forecast (inflation layer).
- Progress UI (`project-progress.tsx`): SPI/CPI/EAC/ETC/VAC cards; “—” when missing; cost footer when no AC.
- Schedule baseline `is_locked` + approve-lock flow (005).
- Budget versions with draft/approved/`is_control` (010); Budget lines at project/phase/WBS/CBS/activity.
- CBS tree `CostBreakdownNode`; ActualCost and Budget can FK to `cbs`.
- Measurement definitions/versions + `approved_progress` on `ActivityProgress` (009).
- Economic `EvmForecastPanel` overlays inflation-adjusted EAC — out of scope to redesign; must keep reading consistent base EVM.

### Gaps to close

1. EVM does **not** check schedule baseline lock or control/approved budget version → no “baseline not locked” validity.
2. EV uses weighted **actual_progress**, not clearly gated on **approved** progress / measurement version → risk of unapproved method feeding EV.
3. Incomplete data often surfaces as numeric **0** for EV/PV (progress 0 × BAC) without `unregistered` / `not_computable` status.
4. No phase or CBS EVM slices / roll-up.
5. UI does not consistently say “not computable” for dependent forecasts when CPI is null.
6. Multi-currency BAC/AC sum is silent today (sum amounts ignoring currency).

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage | **Computed on read** (extend `compute_evm`); optional cache key includes as_of + scope; no persisted EVM snapshot table in v1 | Matches current pattern; avoids dual-write; audit via source systems |
| Schedule baseline validity | Fully valid only if there is an **active locked** schedule baseline for the project | Spec FR-001 / SC-004 |
| Budget baseline validity | Fully valid only if there is an **approved control** budget version (`is_control` + approved status), or the sole approved active version if control flag unused | Aligns with 010; document fallback in API `meta.budget_baseline` |
| BAC source | Sum of budget lines on the control/approved version (prefer version-scoped lines; fallback to current project budgets only if no versions yet, with `bac_source` warning) | Avoid mixing draft lines into BAC |
| EV progress feed | Weighted % from latest **approved_progress** per activity ≤ as_of; if no activity has approved progress, EV status = `unregistered` (not numeric zero-as-complete) | FR-006, FR-007, SC-002 |
| Planned % for PV | Keep planned curve from schedule/baseline dates (existing `get_planned_progress_on_date`); if unlocked baseline, still compute but `validity=partial` + warning | Controllers can still inspect draft plans |
| Not-computable rules | SPI null/not_computable if PV status not `registered` or PV == 0 with no planned work; CPI if EV or AC not registered/zero-meaningless; EAC/ETC/VAC not_computable if CPI not_computable | Spec FR-005, FR-008 |
| Zero vs unregistered | Distinguish: `amount` may be 0 with `status=registered` (truly zero earned) vs `status=unregistered` (no approved progress rows) | SC-002 |
| EV ≠ AC/IPC | Never set EV from ActualCost or IPC totals; unit tests assert independence | FR-007, SC-005 |
| Common EAC method | EAC = BAC / CPI; ETC = EAC − AC; VAC = BAC − EAC | Spec assumption; keep parity with current project KPIs |
| Phase slice | Budget `level=phase` (or WBS nodes marked/used as phase) + activities under that WBS subtree; BAC/EV/PV/AC scoped to subtree | Spec “phase”; reuse WBS hierarchy |
| CBS slice | Aggregate Budget/ActualCost (and progress mapped via activity→budget/cbs links where present) per `CostBreakdownNode`; roll-up by tree | FR-004 |
| Multi-currency | If slice contains >1 distinct currency without `reporting_currency` + rate table, return `aggregation=blocked` and per-currency breakdown | FR-010 |
| Permissions | Reuse progress dashboard: `view_dashboard` (existing KPI); no new mutation perms for v1 | Minimal |
| Economic panel | Continue to call shared `compute_evm` / progress KPIs; inflation remains economic-only overlay | Out of scope for inflation redesign |
| Measurement change | EV at as_of uses approved progress rows stamped with `measurement_version`; unapproved definition edits do not change those rows | SC-003 / FR-009 |

## Alternatives considered

- **Persist EVM snapshot table per cut-off** — useful for audit freeze; deferred (v1 computed; optional later if controllers demand frozen periods).
- **New `evm` Django app** — rejected; duplicates schedule progress ownership (Principle V).
- **Hard-block EVM when baseline unlocked** — stricter than spec (“warn”); rejected in favor of `validity=invalid`/`partial` + warning while still returning numbers.
- **SPI = actual/planned progress ratio without BAC** — keep money-based SPI = EV/PV for FR-EVM alignment; progress % remains on snapshot cards separately.
- **Map EV to IPC approved amounts** — explicitly forbidden by FR-EVM-007.

## NEEDS CLARIFICATION

None remaining — Technical Context unknowns resolved above.
