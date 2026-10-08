# Data Model: Schedule & Baseline Gap Closure

**Feature**: `005-schedule-baseline`  
**Date**: 2026-10-08

## Entities

### Activity (existing — extend)

| Field | Type | Notes |
|-------|------|-------|
| id, project, wbs, activity_code, activity_name | existing | WBS required |
| unit, total_quantity, weight | existing | planned quantity/weight |
| planned_start / planned_finish | Date, null | existing |
| actual_start / actual_finish | Date, null | existing |
| responsible, status, description | existing | |
| soft-delete / audit | existing | `AuditSoftDeleteModel` |
| **duration_days** | Integer, null | **NEW** — working-day or calendar-day count; `0` with milestone |
| **is_milestone** | Bool, default False | **NEW** |
| **forecast_start** | Date, null | **NEW** — never overwrites planned/actual |
| **forecast_finish** | Date, null | **NEW** |
| **working_calendar** | FK → WorkingCalendar, null | **NEW** — null → project default calendar |

**Invariants**:

- Non-milestone: planned_finish ≥ planned_start when both set; same for forecast.
- Milestone: `is_milestone=True` and `duration_days=0`; start may equal finish.
- Soft-deleted activities excluded from cycle checks and status validity.

### WorkingCalendar (new)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| project | FK → Project | CASCADE |
| name | Char | |
| is_default | Bool | at most one default per project (enforce in service) |
| work_monday … work_sunday | Bool | default Mon–Fri true, Sat–Sun false (or project locale default) |
| soft-delete / audit | Yes | |

### CalendarException (new)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| calendar | FK → WorkingCalendar | CASCADE |
| exception_date | Date | |
| is_working | Bool | True = extra work day; False = holiday |
| name | Char, blank | optional label |

Unique `(calendar, exception_date)` among non-deleted.

### ActivityRelation (existing)

No schema change required for v1. Optional later: `notes` text for non-FS explanation.

### BaselineSchedule (existing — extend)

| Field | Type | Notes |
|-------|------|-------|
| id, project, version_name | existing | |
| approved_at, approved_by | existing | |
| is_current | Bool | existing — only one current per project |
| **is_locked** | Bool, default False | **NEW** |
| **locked_at** | DateTime, null | **NEW** |
| **locked_by** | FK User, null | **NEW** |
| **source_change_request** | FK ScheduleChangeRequest, null | **NEW** — set when created from approval |

### BaselineActivity (existing)

Unchanged fields. **Mutation rule**: if parent `is_locked`, reject create/update/delete of snapshot rows (except system create during new version publish).

### ScheduleChangeRequest (new)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| project | FK → Project | |
| base_baseline | FK → BaselineSchedule, null | current locked baseline at create time |
| reason | Text | required on submit |
| milestone_impact | Text | required on submit |
| cost_impact | Text | required on submit |
| contract_impact | Text | required on submit |
| status | Enum | `draft` / `submitted` / `approved` / `rejected` |
| created_by | FK User | |
| submitted_at | DateTime, null | |
| decided_by | FK User, null | |
| decided_at | DateTime, null | |
| decision_notes | Text, blank | |
| resulting_baseline | FK → BaselineSchedule, null | set on approve |
| soft-delete / audit | Yes | |

### ScheduleChangeItem (new, optional but recommended)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| change_request | FK | CASCADE |
| activity | FK → Activity | |
| proposed_planned_start / finish | Date, null | |
| proposed_duration_days | Integer, null | |
| proposed_forecast_start / finish | Date, null | |
| notes | Text, blank | |

## Relationships

```text
Project 1──* WorkingCalendar 1──* CalendarException
Project 1──* Activity ──? WorkingCalendar
Activity 1──* ActivityRelation (as pred/succ)
Project 1──* BaselineSchedule 1──* BaselineActivity ── Activity
Project 1──* ScheduleChangeRequest ──? BaselineSchedule (base / resulting)
ScheduleChangeRequest 1──* ScheduleChangeItem ── Activity
```

## State transitions

### Baseline

```text
(created / imported, unlocked) → approve-lock → locked + is_current
locked current → (via approved change request) → new locked current; prior remains locked, is_current=false
```

### ScheduleChangeRequest

```text
draft → submitted → approved → (creates locked baseline)
                ↘ rejected
draft ← (optional withdraw from submitted by requester — if allowed)
```

Only one `submitted` request per project at a time.

## Validation rules

| Rule | Enforcement |
|------|-------------|
| Finish ≥ start (planned/forecast) | service / serializer |
| Milestone duration 0 | service |
| Calendar working-day for date fields | service using calendar + exceptions |
| Cycle on relations | existing |
| Locked baseline snapshot immutable | service on BaselineActivity writes |
| Change request fields on submit | service |
| Approve creates new baseline version | transactional service |
| Critical path validity | read service for status/gantt consumers |
