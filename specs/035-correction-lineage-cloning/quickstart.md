# Quickstart: Validate Daily Report Correction Lineage and Lossless Cloning

This guide outlines runnable verification steps to validate the correction lifecycle, lossless cloning, concurrency protection, cancellation flow, and enriched version lineage.

---

## Prerequisites

1. Work from the project root: `/home/hossein/Desktop/projects/building-management`.
2. PostgreSQL must be active on port `5433` and Redis on port `6379`.
3. Sourced root `.env` (`AUDIT_LOG_ASYNC=false`, `CELERY_TASK_ALWAYS_EAGER=true`).
4. Pinned runtime: Django 4.2.11 (`apps/api/.venv/bin/python`).

---

## 1. Schema-Drift Guard

Verify no unplanned database migrations are created:

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
../.venv/bin/python manage.py makemigrations --check --dry-run
```

**Expected Outcome**: `No changes detected`.

---

## 2. Backend Unit & Integration Tests

Execute the focused correction lineage and permission pytest suites:

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
../.venv/bin/python -m pytest \
  field_reports/tests/test_daily_report_gaps_correction.py \
  field_reports/tests/test_daily_report_summary_permissions.py
```

**Expected Evidence**:
- `test_correction_clones_all_lifecycle_rows_and_version_metadata`: Verifies exact preservation of all 5 activity fields (`contractor_ref_id`, `crew_name`, `foreman_count`, `worker_count`, `parcel`), machinery summary rows, general activities, visits, and incident severity/discipline.
- `test_concurrent_open_correction_returns_400_with_distinct_code`: Validates HTTP 400 with `correction_already_open`.
- `test_cancel_correction_success`: Validates draft soft-deletion, restoration of source as current, and status transition to `cancelled`.
- `test_cancel_correction_permission_enforcement`: Confirms viewer roles and cross-project requests are strictly rejected.
- `test_version_history_fields_and_root_isolation`: Verifies `modifier_name`, result-bound reason, approval timestamp, and null reason for version 1.

---

## 3. Playwright Browser E2E Tests

Verify the correction, cancellation, and version history flows in the browser:

```bash
cd /home/hossein/Desktop/projects/building-management/apps/web/e2e
pnpm exec playwright test -c playwright.config.ts tests/daily-report.spec.ts -g "daily report lifecycle" --reporter=list --workers=1
```

**Expected Evidence**:
1. Opening a correction navigates to the new draft edit page.
2. The draft edit page displays the "انصراف از اصلاح / Cancel Correction" button; initial draft (v1) does not.
3. Clicking cancellation opens the confirmation modal with warning text.
4. Confirming cancellation redirects to the restored approved version with a success toast.
5. The version panel displays Jalali-formatted approval timestamps, modifier name, and version-bound justification reason.

---

## 4. Static Quality Checks

Verify that TypeScript and repository formatting adhere to guidelines:

```bash
cd /home/hossein/Desktop/projects/building-management
pnpm typecheck
git diff --check
```

**Expected Outcome**:
- `pnpm typecheck` exits with code 0 (zero errors).
- `git diff --check` exits with code 0 (zero trailing whitespace/EOF errors).

---

## 5. Manual Visual & Accessibility Pass

In both Persian and English interfaces:
1. **Focus & Keyboard Navigation**: Verify the "انصراف از اصلاح" button and the confirmation modal buttons can be navigated and triggered via keyboard (`Tab`, `Space`, `Enter`, `Escape`).
2. **Localization**: Confirm that the confirmation modal text, toast notifications, and version history dates display properly in the active locale without English/Persian mixing or broken digit glyphs.
3. **Audit Trail**: Confirm that the version history list clearly differentiates the current version, past approved versions, and draft states.
