# Quickstart & Verification: Site Inactivity Reasons, Conflict Guard, and Daily-Report Access Hardening

**Feature**: `specs/031-site-inactivity-security` | **Date**: 2026-10-22

Prerequisites: native Postgres (port 5433) and Redis running; API venv at `apps/api/.venv`; `.env` sourced for `DATABASE_URL`. Docker-only services (RabbitMQ, MinIO) are not required by this feature.

## 1. Backend invariants (evidence category: pytest)

```bash
cd apps/api/core && set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest field_reports/tests/test_spec_01_daily_header_weather.py field_reports/tests/test_daily_report_summary_permissions.py -q
../.venv/bin/python manage.py verify_blueprint_schema
```

Expected: all inactivity-reason tests pass (five values accepted, unknown/retired rejected, `inactivity_reason_required` attached to `inactivity_reason`, active clears reason, aggregation preserves/clears per status, PDF row contains the localized reason for weather, active PDF renders none); viewer cannot POST by-date (403) and can GET existing by-date (200 / 404 for missing date without creating).

## 2. Frontend typecheck + guard unit tests (evidence category: node tests)

```bash
pnpm typecheck
node --test --experimental-strip-types apps/web/src/app/lib/__tests__/activityGuard.test.ts
```

Expected: typecheck exits 0; unit tests confirm the approved fa/en warning strings match the catalog texts verbatim, the predicate triggers only on inactive + strictly positive numeric quantity, and blank/null/NaN/zero never trigger. (Create the unit test file during `/speckit-tasks` implementation if absent.)

## 3. Browser verification (evidence category: Playwright E2E)

```bash
pnpm exec playwright test e2e/tests/daily-report-inactivity-guard.spec.ts --reporter=line
```

Scenario coverage expected in the new spec file (mocked API per existing E2E conventions):

1. Set site status to inactive → reason selector appears with exactly the five localized options (fa and en projects).
2. Save inactive without reason → inline `inactivity_reason_required` message near the selector, no API write.
3. Inactive + positive-quantity activity row → dialog appears with the approved copy; test ids `inactive-activity-confirm-dialog`, `inactive-activity-confirm-btn`, `inactive-activity-cancel-btn`; confirm → row saved; cancel → no write, entry retained.
4. Inactive + zero/blank quantity and active + positive quantity → no dialog.
5. Existing coroutine projects (`chromium-desktop`, `mobile-chrome`) pass; `pwa-offline` skips like the rest of the suite ("Requires the dev server").

## 4. PDF extraction (evidence category: backend PDF)

Covered by the pytest module in step 1 (text-extraction assertions for the reason row). Manual re-check optionally with a report carrying `inactivity_reason=weather` and one active report: the inactive PDF's header table must contain «نامساعد بودن شرایط جوی» and the active PDF must contain no reason text.

## 5. Localization check (evidence category: bilingual)

`grep`-level check that `fa.json` and `en.json` both define `dailyReports.inactivityReasons.weather|holiday|strike_or_dispute|client_stop_order|safety_incident`, `errors.inactivity_reason_required`, `dailyReports.inactiveSiteActivityWarning` (with the approved wording), `dailyReports.confirmActivity`, `dailyReports.cancelActivity`, and the new dialog-title key; the ActivityTab lookup key matches the catalog key exactly.

## 6. Feature constitution evidence checklist

- [ ] Backend pytest re-run on the final tree
- [ ] `verify_blueprint_schema` — 40/40 blueprint tables
- [ ] `pnpm typecheck` exits 0
- [ ] Guard predicate unit tests pass
- [ ] Bilingual Playwright E2E passes (desktop + mobile; offline project skips)
- [ ] PDF extraction assertions pass
- [ ] Verification report names all evidence categories used (backend / schema / typecheck / unit / browser / PDF)
