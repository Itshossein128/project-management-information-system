# Data Model: Earned Value & Project Control (EVM)

## Existing sources (unchanged ownership)

| Source | Role in EVM |
|--------|-------------|
| `schedule.Baseline` (`is_locked`) | Schedule baseline validity |
| `cost_control.BudgetVersion` (`status`, `is_control`) | Budget baseline / BAC version |
| `cost_control.Budget` (lines: project/phase/WBS/CBS/activity) | BAC by scope |
| `cost_control.CostBreakdownNode` | CBS hierarchy for slices |
| `cost_control.ActualCost` | AC by project/cbs/date |
| `schedule.ActivityProgress` (`approved_progress`, `measurement_version`, `report_date`) | EV progress feed |
| `schedule.ActivityMeasurementDefinition` / `ActivityMeasurementVersion` | Approved method versions (009) |
| `projects.Activity` + `projects.WBS` | Weights, phase/WBS scoping, planned dates |

No new persisted EVM fact table in v1. Reports are **derived DTOs**.

## Derived: EVM Report Point

Computed for `(project_id, as_of_date, scope)` where scope is `project` | `phase:{wbs_id}` | `cbs:{cbs_id}`.

| Field | Type | Notes |
|-------|------|-------|
| as_of_date | date | Cut-off |
| scope_type | enum | `project` \| `phase` \| `cbs` |
| scope_id | uuid \| null | null for project |
| validity | enum | `valid` \| `partial` \| `invalid` |
| warnings | string[] | e.g. `baseline_not_locked`, `budget_baseline_not_control`, `mixed_currency` |
| schedule_baseline | object | `{locked: bool, baseline_id?, locked_at?}` |
| budget_baseline | object | `{approved: bool, is_control: bool, version_id?, currency?}` |

**Validity rules**:

- `valid`: schedule baseline locked **and** budget control/approved version present **and** no blocking currency issue.
- `partial`: numbers computed but at least one soft warning (e.g. unlocked baseline).
- `invalid`: cannot produce a trustworthy roll-up (e.g. mixed currency without conversion when aggregation requested).

## Derived: Measure (PV / EV / AC)

| Field | Type | Notes |
|-------|------|-------|
| amount | decimal \| null | null when unregistered |
| status | enum | `registered` \| `unregistered` \| `incomplete` |
| currency | char(3) \| null | reporting currency when single-currency |

**Semantics**:

- **PV**: BAC_scope × planned_progress_scope; `unregistered` if no planned baseline/activities in scope.
- **EV**: BAC_scope × approved_progress_scope; `unregistered` if no `approved_progress` rows in scope ≤ as_of (do not treat as registered zero).
- **AC**: sum ActualCost in scope ≤ as_of; `unregistered` if no cost rows (distinct from registered 0 if product later supports explicit zero postings—v1: no rows ⇒ unregistered).

**Invariant**: EV is never copied from AC or IPC amounts.

## Derived: Indices & variances

| Code | Formula when computable | Not computable when |
|------|-------------------------|---------------------|
| SV | EV − PV | EV or PV not registered |
| CV | EV − AC | EV or AC not registered |
| SPI | EV / PV | PV not registered or PV = 0 |
| CPI | EV / AC | EV or AC not registered or AC = 0 |
| EAC | BAC / CPI | CPI not computable or BAC missing |
| ETC | EAC − AC | EAC not computable |
| VAC | BAC − EAC | EAC not computable |

Each index field: `{value: number|null, status: computable|not_computable, reason?: code}`.

## Derived: Finish forecast

Same common method as current project KPIs; status mirrors CPI/BAC readiness. Inflation-adjusted EAC remains economic-domain overlay (not part of this DTO’s required fields).

## Derived: Slice roll-up

| Slice | BAC | Progress | AC |
|-------|-----|----------|----|
| Phase | Budget lines with `level=phase` for WBS id, else sum child WBS/activity budgets under subtree | Weighted approved/planned progress of activities under WBS subtree | ActualCost linked to activities/WBS in subtree when link exists; else allocate only when cost rows carry wbs—document `ac_allocation=direct_only` if unlinked costs excluded |
| CBS | Budget lines with `cbs_id` in node subtree | Activities linked via budget activity lines on that CBS; if none, EV may be `incomplete` for that node | ActualCost.cbs in subtree |

**Roll-up**: Project BAC/EV/PV/AC equal sum of **top-level phase slices** when phase budgets partition the control BAC; if partitions incomplete, project total remains global compute and slices are annotated `roll_up=partial`.

## Validation rules (service-level)

1. `as_of` required (default today).
2. Locked/control checks always populate `warnings` / `validity` (never silent).
3. Ratio endpoints never return `0.0` for SPI/CPI when status is `not_computable`.
4. Multi-currency: block aggregated `amount` when >1 currency and no conversion context.
5. Cache keys must include scope + as_of; invalidate on progress approval, baseline lock, budget version approve, actual cost write (extend existing invalidation).

## State transitions

Not applicable for persisted entities. Source transitions that affect EVM:

- Baseline draft → locked ⇒ may clear `baseline_not_locked`.
- Budget version → approved/control ⇒ may clear budget validity warning.
- Progress row → `approved_progress` set ⇒ EV may move `unregistered` → `registered`.
- Measurement definition edit without approve ⇒ EV unchanged (versioned progress rows).
