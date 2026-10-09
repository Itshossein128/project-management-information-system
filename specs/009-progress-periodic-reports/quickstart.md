# Quickstart validation: FR-PRG gap closure

**Feature**: `009-progress-periodic-reports`  
**Purpose**: Runnable checks after `/speckit-implement` — not an implementation guide.

## Prerequisites

- Postgres + Redis up; API + web as in `AGENTS.md`
- Seeded project with WBS + activities (`pnpm db:seed` or existing fixtures)
- Auth as project member with `edit_activities` and (for approve) `approve_reports` or documented equivalent
- Spec artifacts: [data-model.md](./data-model.md), [contracts/](./contracts/)

## Scenarios

### US1 — Measurement method + period progress

1. Set activity measurement to `quantity` with total/unit; **approve** basis ([measurement-methods.md](./contracts/measurement-methods.md)).
2. Record period quantity (manual or approved daily path).
3. **Expect**: progress linked to WBS + `measurement_version_id`; cumulative updates.
4. Attempt save that implies >100% without quantity change → **400** `progress_exceeds_100` ([progress-validation.md](./contracts/progress-validation.md)).
5. Attach photo only; request technical approve without approve path → not treated as approved ([progress-four-way.md](./contracts/progress-four-way.md)).
6. Switch to `weighted_milestones` with incomplete weights → approve/report blocked `incomplete_measurement_basis`.

### US2 — Four-way display

1. Open project progress page / GET activities progress with a period window.
2. **Expect**: distinct `period_progress_pct`, `cumulative_progress_pct`, `planned_progress_pct`, `approved_progress_pct` with clear UI labels.
3. With recorded-but-unapproved progress → approved ≠ period/cumulative recorded.

### US3 — Weekly / monthly reports

1. Ensure ≥1 approved daily in the week; generate weekly report ([weekly-monthly-reports.md](./contracts/weekly-monthly-reports.md)).
2. **Expect**: sections for critical, next-week plan, barriers, decisions; each figure has source + `last_updated_at`.
3. Follow `source_path` → source + approval status (one step).
4. Attempt figure PATCH without override → rejected; override with reason → audit row exists.
5. Generate monthly with missing cost data → cost section `value_status=not_recorded` (not zero).

### US4 — Method versioning

1. With approved method + existing progress, submit method change with reason; approve.
2. **Expect**: new version; historical progress rows retain prior `measurement_version_id`; new writes use new version.
3. Draft/rejected change does not govern new progress.

## Suggested automated commands (post-implement)

```bash
# From apps/api/core with .env sourced
../.venv/bin/python -m pytest schedule/tests/test_measurement_methods.py \
  schedule/tests/test_progress_four_way.py \
  schedule/tests/test_progress_validation.py \
  schedule/tests/test_period_reports.py -q
```

Optional: Playwright smoke on `/projects/{id}/progress` four labels + generate weekly.

## Out of scope checks

- Full EVM indices (spec 13)
- Portfolio dashboard (16)
- Inventory department weekly PDF routes
