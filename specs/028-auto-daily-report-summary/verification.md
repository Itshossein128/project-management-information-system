# Verification: Automated Project Daily Report Summary

**Feature**: `028-auto-daily-report-summary`  
**Started**: 2026-10-18

## Baseline (T001)

- Git branch: `develop` (logical feature key `028-auto-daily-report-summary`)
- Python 3.12.3 / Django 4.2.11
- Postgres 16 (running) / Redis PONG
- Approach: TDD per `tasks.md`

## Test modules

| Module | Stories |
|--------|---------|
| `field_reports/tests/daily_report_summary_helpers.py` | fixtures |
| `field_reports/tests/test_daily_report_summary_models.py` | Phase 2 |
| `field_reports/tests/test_daily_report_aggregation_include.py` | Phase 2, US3 |
| `field_reports/tests/test_daily_report_no_blank_create.py` | Phase 2 |
| `field_reports/tests/test_daily_report_by_date.py` | US1, US2 |
| `field_reports/tests/test_daily_report_aggregation_activities.py` | US1 |
| `field_reports/tests/test_daily_report_aggregation_rebuild.py` | US1 |
| `field_reports/tests/test_daily_report_derived_readonly.py` | US1 |
| `field_reports/tests/test_daily_report_aggregation_sections.py` | US2 |
| `sub_reports/tests/test_sub_report_contributions.py` | US2 |
| `field_reports/tests/test_daily_report_aggregation_partial.py` | US3 |
| `field_reports/tests/test_daily_report_summary_permissions.py` | US3 |
| `field_reports/tests/test_daily_report_summary_metadata.py` | US4 |
| `field_reports/tests/test_daily_report_summary_approvals.py` | US4 |
| `field_reports/tests/test_daily_report_summary_isolation.py` | Polish |

Quickstart: [quickstart.md](quickstart.md)

## Run log

- 2026-10-18: Foundation + US1–US4 + polish implemented (TDD).
- Pytest (summary suite): **34 passed** (`test_daily_report_summary_*`, aggregation, by-date, crud create rejection, sub_reports contributions).
- Web: removed «گزارش جدید», by-date ensure, Excel-like `DailyReportSummaryView`, `/daily-reports/new` redirects to list; fa/en summary strings added.
- Migrations: `field_reports.0017_auto_daily_report_summary`, `sub_reports.0002_auto_daily_report_summary`.

## Phase 8 (T063–T072) — 2026-10-18

| Quickstart / check | Result | Evidence |
|--------------------|--------|----------|
| § List has no «گزارش جدید» | PASS | E2E `daily-report.spec.ts` + list UI; `daily-report-new-btn` count 0 |
| § `/daily-reports/new` redirects | PASS | E2E redirect assert; decision-tree interactive/domains updated |
| § Open by date / specialty seed | PASS | `createDailyReportViaApi` → sub-report submit + by-date ensure |
| § Specialty contribution UI | PASS | `SpecialtyContributionForm` + nested API fields on `project-sub-reports` |
| § Excel sections (shifts, general, visits, contract) | PASS | `DailyReportSummaryView` sections + project identity props |
| § Overrides on summary | PASS | weather/site override toggles on `daily-report-view` |
| § Specialty toast + invalidate | PASS | create/submit toasts + invalidate `daily-reports` queries |
| § Offline no blank POST | PASS | `offlineWrite`/`syncService` → `/by-date/`; sync-batch ensure shell |
| § Site status derive (Decision 7) | PASS | `site_status` on `DisciplineSubReport` + `test_daily_report_site_status_derive.py` |
| § Decision-tree `[create-report]` | PASS | Superseded README + `open-by-date` + inventory.json |
| Migrations | PASS | `sub_reports.0003_disciplinesubreport_site_status` |
| Pytest site_status + sync-batch | PASS | `test_daily_report_site_status_derive` (3) + sync-batch ensure/reject children |
