# Research: Schedule & Baseline Gap Closure (FR-SCH)

**Feature**: `005-schedule-baseline`  
**Date**: 2026-10-08

## Current state (codebase)

| Area | Status | Notes |
|------|--------|-------|
| Activity ↔ WBS | Present | Required FK; planned/actual dates; responsible; status; quantity/weight |
| Duration | Derived | `planned_duration` property from start/finish only — not stored; no milestone flag |
| Forecast dates | Missing | No `forecast_start` / `forecast_finish` |
| Working calendar | Missing | No calendar model; dates not calendar-validated |
| Relations FS–SF + lag | Present | Cycle detection in `schedule/services/cycle_detection.py` |
| Impossible dates | Weak | Finish-before-start / calendar rules not systematically enforced |
| Baseline snapshot | Present | `BaselineSchedule` + `BaselineActivity`; `is_current`; import creates current |
| Baseline lock | Missing | No `is_locked`; live edits vs snapshot are separate rows (good), but no approve/lock API or forbid snapshot PATCH |
| Schedule change request | Missing | No entity/workflow |
| Critical path | Partial | `BaselineActivity.is_critical` from MSP/P6 import; Gantt reads flags; no validity gate |
| Milestone/delay report | Missing | No dedicated status endpoint/UI |
| Gantt compare | Present | Optional `baseline_id`; compares current vs baseline |

## Decisions

### D1 — Additive Activity fields (not a parallel schedule entity)

**Decision**: Add to `projects.Activity`: `duration_days` (int, null; 0 = milestone when `is_milestone`), `is_milestone` (bool), `forecast_start` / `forecast_finish` (date, null), `working_calendar` FK (null → project default).

**Rationale**: Spec attributes belong on the existing activity; keeps import/Gantt/progress consumers on one model.

**Alternatives considered**: Separate `ActivityScheduleExtension` 1:1 (extra joins); compute duration only (fails explicit milestone + FR-SCH-001).

### D2 — Project-scoped WorkingCalendar with exceptions

**Decision**: `WorkingCalendar` per project (`name`, `is_default`, weekday bitmask or `work_monday`…`work_sunday`). `CalendarException` rows for holidays/extra work days. Activities optionally override project default.

**Rationale**: Spec assumption: project-level calendars for v1; enough for impossible-date validation without org-wide library.

**Alternatives considered**: Global org calendars only (premature); full hour-level calendars (out of scope).

### D3 — Impossible-date validation rules

**Decision**: On create/update activity (and change-request apply):

1. Reject if planned finish < planned start (non-milestone).
2. Reject if forecast finish < forecast start when both set.
3. Milestone: `is_milestone=True` and `duration_days=0`; start/finish may be equal.
4. If calendar assigned (or default exists): planned/forecast start and finish MUST fall on working days (or warn-then-reject — **reject** for consistency with FR-SCH-003).
5. Keep cycle rejection on relations unchanged.

**Rationale**: Clear server-side rules; bilingual error codes.

### D4 — Baseline lock semantics

**Decision**: Add `is_locked`, `locked_at`, `locked_by` on `BaselineSchedule`. Actions:

- `POST .../baselines/` — create snapshot from current live activities (draft, unlocked) **or** keep import path creating current unlocked until approve.
- `POST .../baselines/{id}/approve-lock/` — set `approved_*`, `is_current=True`, `is_locked=True`; demote prior current’s `is_current` but **retain** prior rows (already behavior for `is_current`).
- Reject PATCH/DELETE of `BaselineActivity` rows when parent `is_locked`.
- Live `Activity` PATCH never mutates `BaselineActivity` (already true); add regression tests.

**Rationale**: Formalizes FR-SCH-005 without changing the snapshot-vs-live storage model.

**Alternatives considered**: Soft “approved” only without lock (insufficient); overwrite current snapshot in place (destroys history).

### D5 — ScheduleChangeRequest workflow

**Decision**: New `ScheduleChangeRequest` with status `draft` → `submitted` → `approved` | `rejected`. Fields: reason, milestone_impact, cost_impact, contract_impact, base_baseline FK, created_by, decided_by, decided_at, decision_notes. Optional `ScheduleChangeItem` rows for proposed planned date/duration deltas per activity.

On **approve**:

1. Apply proposed live activity updates (if items present) OR snapshot current live state as agreed.
2. Create **new** `BaselineSchedule` version (name from request), snapshot all activities → `BaselineActivity`, `is_current=True`, `is_locked=True`.
3. Prior current remains unlocked from “current” flag only (`is_current=False`) but stays locked historically.

Concurrency: at most one `submitted` request per project (or per current baseline); additional submit → `409 schedule_change_in_flight`.

Permissions: create/submit/reject draft with `edit_activities`; approve with `edit_activities` (v1). Soft SoD: prefer different approver than requester; hard SoD deferred to Spec 16.

**Alternatives considered**: Generic workflow engine (Spec 15 — out of scope); mutate locked baseline in place (forbidden).

### D6 — Critical-path validity (not full CPM rewrite)

**Decision**: Service `evaluate_critical_path_validity(project_id)` returns:

```text
{ valid: bool, reason_codes: [...], critical_activity_ids: [...], near_critical_activity_ids: [...] }
```

**Valid only if** every non-deleted, non-milestone-or-all activities used in the network have `duration_days` (or computable planned span) **and** the graph has no incomplete required edges for activities that claim critical flags — practical rule for v1:

- All active activities have known duration (`duration_days` not null, or planned start+finish).
- Relation set has no cycles (already enforced).
- If any active activity lacks duration → `valid=false`, `reason_codes` include `incomplete_durations`; **do not** return authoritative critical IDs (empty lists + message).
- If valid: expose critical from current baseline’s `is_critical` flags and/or float ≤ 5 days when `total_float` present; near-critical = float ≤ 5 and not critical.

**Rationale**: Meets FR-SCH-008 without shipping a new CPM solver; import-sourced flags remain useful when data complete.

**Alternatives considered**: Implement full forward/backward pass now (deferred); always hide critical (too harsh when imports are complete).

### D7 — Schedule status report as read API + UI route

**Decision**: `GET .../schedule-status/` aggregates milestones, delays (planned/baseline vs today or forecast), forecast project finish (max forecast_finish or planned_finish), and embeds validity payload. UI route under project schedule nav.

**Rationale**: FR-SCH-007 / SC-SCH-003 in one place; Gantt remains visualization.

### D8 — Permissions

**Decision**: Reuse `view_activities` / `edit_activities`. No new permission codes in v1.

## Open points resolved by assumption

- Auto forecast from progress → out of scope (manual forecast fields only).
- Hour-level calendars / resource leveling → out of scope.
- Near-critical threshold = 5 working days (spec assumption).
- Relation free-text note for non-FS → optional later; not required for plan.
