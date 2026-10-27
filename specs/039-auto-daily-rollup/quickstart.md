# Quickstart: Feature 039 Auto Daily Rollup & Activity Master Log Sync

This document provides setup and verification instructions for Feature 039.

## 1. Prerequisites & Services

Ensure native Postgres and Redis services are running on their designated dev ports (see `AGENTS.md`):

```bash
# Verify PostgreSQL (port 5433)
sudo pg_ctlcluster 16 main status

# Verify Redis (port 6379)
sudo redis-cli ping
# Expected: PONG
```

## 2. Environment & Database Setup

Source `.env` and verify database migrations:

```bash
cd apps/api/core
set -a && source /home/hossein/Desktop/projects/building-management/.env && set +a

# Run migrations
../.venv/bin/python manage.py migrate
```

## 3. Running Backend Tests

Run pytest for daily report aggregation, by-date provisioning, derived readonly locking, contractor bucketing, and activity log sync:

```bash
cd apps/api/core
set -a && source /home/hossein/Desktop/projects/building-management/.env && set +a

../.venv/bin/python -m pytest field_reports/tests/test_daily_report_by_date.py -v
../.venv/bin/python -m pytest field_reports/tests/test_daily_report_derived_readonly.py -v
../.venv/bin/python -m pytest field_reports/tests/test_daily_report_contractor_ref.py -v
../.venv/bin/python -m pytest field_reports/tests/test_receipts_only_summary.py -v
```

## 4. Running Frontend Verification

Verify typechecking and production build:

```bash
cd /home/hossein/Desktop/projects/building-management
pnpm --filter web build
```

## 5. End-to-End User Scenario Verification

1. **Date Shell Auto-Provisioning**:
   - Query `GET /api/v1/projects/{project_pk}/daily-reports/by-date/?date=2026-11-01`.
   - Result: 200 OK with `is_auto_summary: true`, `status: "draft"`.
2. **Contractor Labor Separation**:
   - Create two sub-reports with identical job titles but different contractors.
   - Aggregate via by-date.
   - Result: `labor_entries` contains 2 separate rows preserving each contractor's name and reference.
3. **Derived Collection Lock**:
   - Send `POST` to `/daily-reports/{report_id}/activities/`.
   - Result: 400 Bad Request with `derived_collection_read_only`.
4. **Activity Master Log Alignment**:
   - View `/projects/{projectId}/activity-log`.
   - Result: Table displays "دیسیپلین" and "قطعه" columns. Approving a report makes new activities appear immediately.
5. **Completeness Banner**:
   - When all disciplines submitted, view displays green banner «تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند».
