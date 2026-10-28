# Quickstart: Department Activity Reports & Excel Workbooks

**Feature**: `042-department-activity-reports`  

---

## 1. Running Database Migrations

Apply the migration for `executed_quantity`:
```bash
apps/api/.venv/bin/python apps/api/core/manage.py makemigrations inventory
apps/api/.venv/bin/python apps/api/core/manage.py migrate
```

---

## 2. Running Automated Tests

Run the backend pytest suite:
```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest inventory/tests.py -k "test_export or test_import or test_report or test_department" --reuse-db -v
```

Run web frontend build:
```bash
pnpm --filter web build
```

---

## 3. Key Endpoint Verification Examples

### 3.1 Daily Report (.xlsx)
```bash
curl -X GET "http://localhost:8000/api/v1/projects/1/department-activity-records/reports/daily/?department=civil&date=2026-10-17" \
  -H "Authorization: Bearer <TOKEN>" \
  -o civil_daily_2026-10-17.xlsx
```
*Verify*: Inspect the file with LibreOffice or Excel. Confirm RTL is enabled, title row is present, and total row contains `=SUM(...)`.

### 3.2 Weekly Report (.xlsx)
```bash
curl -X GET "http://localhost:8000/api/v1/projects/1/department-activity-records/reports/weekly/?department=mechanical&week_start=2026-10-17" \
  -H "Authorization: Bearer <TOKEN>" \
  -o mechanical_weekly_2026-10-17.xlsx
```
*Verify*: Confirm exactly 8 sheets (Saturday to Friday + Weekly Summary) with active summation formulas.

### 3.3 Atomic Batch Import
```bash
curl -X POST "http://localhost:8000/api/v1/projects/1/department-activity-records/import/?department=civil" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@activities_upload.xlsx"
```
*Verify*: If row 4 has invalid text for `executed_quantity`, server responds with HTTP 400 and Persian message `خطا در سطر ۴...`, and zero rows are persisted in the database.
