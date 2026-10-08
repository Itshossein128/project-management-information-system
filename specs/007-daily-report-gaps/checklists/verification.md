# Verification stub: Daily Report Gaps (007)

**Feature**: `007-daily-report-gaps`  
**Date**: 2026-10-08

Lightweight checklist for polish items closed with Specs 01–07 gap plan. Full suite remains in `field_reports/tests/`.

## Automated / UI evidence

| Item | Evidence |
|------|----------|
| FR-DR-002 responsible_user picker on activity tab | `e2e/tests/specs-04-05-07-polish.spec.ts` (`activity-responsible-user`) |
| Existing CRUD / workflow API | `field_reports/tests/test_daily_report_*.py` |

## Smoke command

```bash
cd apps/web && CI= pnpm exec playwright test e2e/tests/specs-04-05-07-polish.spec.ts --workers=1
```

## Spec Kit deferred (out of polish plan)

- Per-person attendance/shift ledger (FR-HR-006)
- Labor-by-contractor grid redesign
- Material `quantity_measured` redesign
