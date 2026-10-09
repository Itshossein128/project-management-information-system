# Verification Checklist: Schedule & Baseline Gap Closure

**Feature**: `005-schedule-baseline`  
**Date**: 2026-10-08

## Success criteria → evidence

| SC | Criterion (from spec) | Evidence |
|----|----------------------|----------|
| SC-001 | Planned / actual / forecast dates remain distinct; calendar + impossible-date validation | `schedule/tests/test_activity_forecast_and_validation.py`, `test_working_calendars.py` |
| SC-002 | Approve-lock baseline; live edits do not rewrite locked snapshots | `schedule/tests/test_baseline_lock.py` |
| SC-003 | Change request approve creates new locked current baseline; prior retained; in-flight submit conflict | `schedule/tests/test_schedule_change_request.py` |
| SC-004 | Status report exposes four-way dates (baseline / planned / actual / forecast) | `schedule/tests/test_schedule_status_and_critical_validity.py` |
| SC-005 | Incomplete durations → `critical_path.valid=false` with empty critical ID arrays; Gantt carries validity object | `test_schedule_status_and_critical_validity.py`, `test_gantt.py` |

## Smoke command (backend)

```bash
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  schedule/tests/test_working_calendars.py \
  schedule/tests/test_activity_forecast_and_validation.py \
  schedule/tests/test_baseline_lock.py \
  schedule/tests/test_schedule_change_request.py \
  schedule/tests/test_schedule_status_and_critical_validity.py \
  schedule/tests/test_activities.py \
  schedule/tests/test_gantt.py \
  schedule/tests/test_relations.py \
  -q
```

## Evidence categories

| Category | Status |
|----------|--------|
| pytest (schedule FR-SCH suite) | Done — 28+ cases in FR-SCH modules (full suite 42 with activities/relations) |
| typecheck / UI | Done — activity drawer, Gantt approve-lock, change requests, schedule status route; `pnpm typecheck` clean |
| Near-critical legend (FR-SCH-007 polish) | Done — schedule status `data-testid="near-critical-legend"`; `e2e/tests/specs-04-05-07-polish.spec.ts` |
| MSP/P6 import unlock-then-approve | Documented in `apps/api/core/schedule/ENDPOINTS.md` |
