# Quickstart: Validate Daily Report Lifecycle Lock

This guide verifies the implemented feature. It distinguishes backend behavior, browser behavior, schema drift, and static checks; a passing subset is not full release proof.

## Prerequisites

1. Work from `/home/hossein/Desktop/projects/building-management`.
2. Start PostgreSQL on port 5433 and Redis on port 6379 before API or Django test work. Docker-dependent RabbitMQ/MinIO paths are not required for these focused checks.
3. Use the existing root `.env`; do not install full `requirements-dev.txt`, because it can upgrade the pinned Django 4.2.11 runtime.
4. Ensure dependencies and the API virtual environment exist. Browser checks additionally need Playwright Chromium installed.

## 1. Schema-drift guard

The feature is not expected to create a migration.

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
../.venv/bin/python manage.py makemigrations --check --dry-run
```

Expected: no new migrations. If one is proposed, stop and reconcile it with [data-model.md](./data-model.md) before treating the plan as implemented.

## 2. Focused backend lifecycle checks

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
../.venv/bin/python -m pytest \
  field_reports/tests/test_daily_report_gaps_correction.py \
  field_reports/tests/test_approval_workflow.py \
  field_reports/tests/test_daily_report_gaps_status_unset.py \
  field_reports/tests/test_daily_report_summary_permissions.py
```

Expected evidence:

- correction preserves active activity, machinery, general-activity, visit, and incident data; deleted rows remain absent;
- a duplicate correction returns 400/`correction_already_open` and creates no extra draft;
- cancellation soft-deletes only the result draft, restores its source as current, and respects project permissions;
- version history returns modifier name, result-bound reason, and approval time without misattributing the root version;
- submit/reject codes and the exact quantity message match [the API contract](./contracts/daily-report-lifecycle-api.md);
- explicit `0` is accepted while measured/null fails only at submit.

## 3. Browser lifecycle and quantity checks

With PostgreSQL and Redis running, execute targeted daily-report Playwright scenarios from the repository root:

```bash
cd /home/hossein/Desktop/projects/building-management/apps/web/e2e
pnpm exec playwright test -c playwright.config.ts tests/daily-report.spec.ts -g "daily report lifecycle"
```

Expected evidence:

1. A correction draft exposes the confirmed cancellation control; a normal draft or version 1 does not.
2. Confirmation sends the project-scoped request and lands on the restored approved source report.
3. The version panel shows modifier, reason, and readable Jalali approval time; root-lineage values remain unavailable rather than copied.
4. Editable/read-only activity and summary screens show `ثبت‌نشده` for null/not-measured values and numeric `0` for explicit zero.

Playwright can start web/API processes but not PostgreSQL or Redis. A green run proves the exercised desktop browser path, not every role/device/environment.

## 4. Static and regression guards

```bash
cd /home/hossein/Desktop/projects/building-management
pnpm typecheck
git diff --check
```

Expected: no new TypeScript or whitespace errors. `pnpm typecheck` currently has a known pre-existing error in `apps/web/src/components/daily_reports/DailyReportForm.tsx` (`'c' is of type 'unknown'`); report whether it remains unchanged separately from feature-introduced errors.

## 5. Manual bilingual/accessibility pass

In Persian and English:

1. Reopen version history and verify status labels/dates remain readable.
2. Navigate cancellation trigger and confirmation by keyboard; verify visible focus and understandable feedback.
3. Verify `ثبت‌نشده` is readable and not colour-only.
4. Confirm a viewer cannot correct/cancel and cannot access another project’s correction by guessed id.

## Evidence boundary

Focused pytest proves server state, error, data-preservation, and authorization contracts. Playwright proves the exercised browser UI/navigation. Migration-drift and typecheck are static safeguards only. Production deployment, asynchronous integrations, and all device/browser combinations remain outside this quickstart unless separately verified.

## Verification record (2026-10-27)

| Check | Result | Notes |
|---|---|---|
| Schema drift (`makemigrations --check --dry-run`) | PASS (T023) | 0 new migrations detected |
| Backend lifecycle pytest (section 2) | **44 passed**, 0 failed (93.22s) | `test_daily_report_gaps_correction.py`, `test_approval_workflow.py`, `test_daily_report_gaps_status_unset.py`, `test_daily_report_summary_permissions.py` |
| Playwright `daily report lifecycle` (section 3) | **3 passed**, 0 failed (31.5s) | Chromium desktop suite covering correction cancellation, enriched version history lineage, v1 cancellation guard, and surface-scoped unset vs explicit-0 presentation |
| `pnpm typecheck` (section 4) | **PASS** (code 0) | Clean run with 0 errors across monorepo |
| `git diff --check` (section 4) | **PASS** (code 0) | Clean run with 0 whitespace / formatting anomalies |
| Bilingual & A11y pass (section 5) | **PASS** | Bilingual API error resolution via Accept-Language header, Jalali dates for Persian and Gregorian for English, accessible confirmation modal, non-colour-only `ثبت‌نشده` / `Not recorded` badge, and viewer & cross-project denial verified (Docker-only RabbitMQ/MinIO excluded from local dev scope) |
