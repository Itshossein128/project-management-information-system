# Quickstart: Automated Project Daily Report Summary

Validation guide after implementation. Design refs: [data-model.md](data-model.md), [contracts/daily-report-summary-api.md](contracts/daily-report-summary-api.md), [contracts/daily-report-summary-ui.md](contracts/daily-report-summary-ui.md).

## Prerequisites

- Postgres + Redis up; API and web as in `AGENTS.md`
- Seeded project with users who can view reports and edit/submit specialty (رشته) reports
- At least two disciplines available (e.g. civil + electrical)

## 1. No project-level «گزارش جدید»

1. Open `/projects/{id}/daily-reports`.
2. Confirm there is **no** create / Plus / «گزارش جدید» control.
3. Confirm `/daily-reports/new` is not linked (redirect or 404/list).

**Expect**: Cannot start a blank project daily report from this page.

## 2. Specialty authoring still works

1. Open project **گزارش‌های رشته‌ای** / sub-reports.
2. Create a civil report for date D with ≥1 activity (and labor/material rows if UI supports them).
3. Submit the sub-report.

**Expect**: Submit succeeds; create controls remain on specialty UI.

## 3. Auto summary for date D

1. From daily reports, open date D (by-date ensure or list row after rebuild).
2. Summary view shows Excel-like sections; executed activities include the civil row(s).
3. Provenance / discipline attribution visible where implemented.
4. `aggregation.contributing_disciplines` includes `civil`; `is_partial` true if electrical/mechanical missing.

**Expect**: No manual “create project daily” step was required.

## 4. Aggregation update

1. Submit an electrical sub-report for the same date D with different activities / overlapping job titles if labor is supported.
2. Refresh summary for D.

**Expect**: Union of activities; labor counts for the same job title are **sums**; `contributing_disciplines` includes both; banner updates.

## 5. Empty / no specialty day

1. Open a date E with zero submitted specialty reports.
2. Ensure-by-date may create an empty shell or show empty state.

**Expect**: Clear “no specialty data” messaging; **no** blank create button; derived tables empty.

## 6. Read-only derived rows

1. On summary for D, attempt to add/edit an activity via any remaining project daily child editor or API `POST .../activities/`.

**Expect**: UI prevents edit; API returns 400 with message to use specialty reports.

## 7. Summary metadata survives rebuild

1. Set management opinion (and/or weather override) on summary D; save.
2. Update and resubmit a specialty report for D (trigger rebuild).

**Expect**: Opinion / override still present; derived rows refreshed.

## 8. Permissions

1. User with view-reports but without specialty edit: can open summary D; cannot create specialty report.
2. Cross-project: cannot ensure or read another project’s summary by id.

## 9. Bilingual smoke

Toggle fa/en: section titles, partial banner, read-only hint, empty state.

## Suggested automated checks

```bash
# From apps/api/core with .env sourced
../.venv/bin/python -m pytest field_reports/tests sub_reports -q -k "aggregat or daily_report or sub_report"
```

Frontend: `pnpm typecheck`; browser check list without create + by-date summary + specialty submit refresh.
