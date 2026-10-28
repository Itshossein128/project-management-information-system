# Quickstart & Verification Guide: Automated Periodic Reports Rollup

**Feature**: `041-periodic-reports-rollup`  
**Target Environment**: Linux, PostgreSQL 16 (port 5433), Redis (port 6379), Node/pnpm  

---

## 1. Prerequisites & Services Check

Make sure PostgreSQL and Redis are active:
```bash
# Check PostgreSQL status (port 5433)
pg_isready -p 5433

# Check Redis status (port 6379)
redis-cli ping
```

---

## 2. Backend Setup & Migrations

```bash
cd apps/api/core
set -a && source ../../../.env && set +a

# Create and apply migrations for schedule models
../.venv/bin/python manage.py makemigrations schedule
../.venv/bin/python manage.py migrate
```

---

## 3. Running Backend Tests

Execute pytest on the period reports test suite:
```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest --reuse-db schedule/tests/test_period_reports.py
```

---

## 4. Frontend Build & Typecheck

From the repository root:
```bash
# Verify frontend bundle builds cleanly without syntax or typing regressions
pnpm --filter web build
```

---

## 5. Manual API Flow Verification (cURL / HTTP)

### 5.1. Generate Weekly Report
```bash
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/progress-reports/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "weekly",
    "period_start": "2026-10-10",
    "period_end": "2026-10-16"
  }'
```

### 5.2. Query Figure Provenance
```bash
curl -X GET http://localhost:8000/api/v1/projects/{project_id}/progress-reports/figures/{figure_id}/sources/ \
  -H "Authorization: Bearer <TOKEN>"
```

### 5.3. Attempt Override with Invalid Reason (< 10 chars)
```bash
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/progress-reports/figures/{figure_id}/override/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "new_value": 150,
    "reason": "short"
  }'
# Expect HTTP 400: {"error": {"code": "override_reason_required", "message": "دلیل بازنویسی باید حداقل ۱۰ کاراکتر باشد."}}
```

### 5.4. Submit Valid Figure Override
```bash
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/progress-reports/figures/{figure_id}/override/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "new_value": 150,
    "reason": "مورد توافق مشاور مقیم در جلسه فنی مورخ ۱۴۰۵/۰۸/۰۱"
  }'
```

### 5.5. Officially Approve Monthly Report
```bash
curl -X POST http://localhost:8000/api/v1/projects/{project_id}/progress-reports/{report_id}/approve/ \
  -H "Authorization: Bearer <TOKEN>"
```
