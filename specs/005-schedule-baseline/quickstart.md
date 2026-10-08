# Quickstart Validation: Schedule & Baseline Gap Closure

**Feature**: `005-schedule-baseline`  
**Date**: 2026-10-08

## Purpose

Validation guide for `/speckit-implement`. **Do not implement from this Spec Kit pass.**

## Prerequisites

- Specs **002** / **004** patterns available (audit/soft-delete, WBS packages)
- Postgres + Redis; migrated DB; seeded users
- Auth as project member with `view_activities` / `edit_activities`
- Existing activity + relation APIs functional

## Suggested test map

| Story | Automated focus |
|-------|-----------------|
| US1 Calendar / duration / forecast | Create calendar; activity with forecast; milestone duration 0; reject finish&lt;start and non-working day |
| US2 Baseline lock | Approve-lock; PATCH live activity; assert baseline snapshot unchanged; reject locked snapshot edit |
| US3 Change request | Draft→submit→approve creates new locked baseline; prior retained; reject while in-flight |
| US4 Status report | Complete data → milestones/delays; incomplete duration → `critical_path.valid=false` |

Contracts: [working-calendars.md](./contracts/working-calendars.md), [activities-extended.md](./contracts/activities-extended.md), [baselines-and-change-requests.md](./contracts/baselines-and-change-requests.md), [schedule-status-report.md](./contracts/schedule-status-report.md).  
Data model: [data-model.md](./data-model.md).

## Smoke commands (after implement)

```bash
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  schedule/tests/test_working_calendars.py \
  schedule/tests/test_activity_forecast_and_validation.py \
  schedule/tests/test_baseline_lock.py \
  schedule/tests/test_schedule_change_request.py \
  schedule/tests/test_schedule_status_and_critical_validity.py \
  -q
pnpm typecheck
```

Optional UI: open project schedule status + activities forms; confirm four date sets and Jalali display in fa/en.

## Expected outcomes

- SC-001–SC-005 covered by automated tests (verification checklist may be added at implement polish)
- Locked baseline immutable under live edits
- Approved change request → new baseline version; prior version still listable
- Incomplete network → critical path labeled not valid (empty critical IDs)
