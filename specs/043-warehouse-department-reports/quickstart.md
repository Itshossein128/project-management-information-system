# Quickstart & Verification Guide: Warehouse Department Reports

**Feature Branch**: `043-warehouse-department-reports`  
**Date**: 2026-10-28  

---

## 1. Prerequisites

1. Ensure PostgreSQL and Redis are running locally (as per `AGENTS.md`):
   ```bash
   sudo pg_ctlcluster 16 main start
   sudo redis-server /etc/redis/redis.conf --daemonize yes
   ```
2. Activate API virtual environment:
   ```bash
   cd apps/api/core
   source ../.venv/bin/activate
   ```

---

## 2. Automated Tests Execution

Run unit and integration tests covering warehouse activities, report generators, validation errors, and the warehouse balance endpoint:
```bash
cd apps/api/core
set -a && source /home/hossein/Desktop/projects/building-management/.env && set +a
../.venv/bin/python -m pytest inventory/tests.py -k "warehouse"
```

To run all sub_reports and inventory tests:
```bash
../.venv/bin/python -m pytest inventory/tests.py sub_reports/tests/
```

---

## 3. Frontend Verification

Run web frontend build to ensure zero type errors and clean bundle compilation:
```bash
pnpm --filter web build
```

---

## 4. Manual Verification Steps

### 4.1. Non-Positive Quantity Validation
1. Send a POST request to `/api/v1/projects/{project_id}/department-activity-records/` with payload:
   ```json
   {
     "department": "warehouse",
     "date": "2026-10-28",
     "material_type": "سیمان تیپ 2",
     "unit": "کیسه",
     "quantity_in": "0",
     "quantity_out": "0",
     "supplier": "تأمین‌کننده تست",
     "consumption_location": "کارگاه"
   }
   ```
2. Verify HTTP response is `400 Bad Request` with:
   ```json
   {
     "error": {
       "code": "at_least_one_quantity_must_be_positive",
       "message": "حداقل یکی از مقادیر ورودی یا خروجی باید بزرگتر از صفر باشد"
     }
   }
   ```

### 4.2. Warehouse Balance Endpoint
1. Send a GET request to:
   `/api/v1/projects/{project_id}/department-activity-records/warehouse-balance/?as_of_date=2026-10-28`
2. Verify HTTP 200 with an array of items:
   ```json
   [
     {
       "material_type": "سیمان تیپ 2",
       "unit": "کیسه",
       "total_in": 500.0,
       "total_out": 100.0,
       "current_balance": 400.0,
       "last_movement_date": "2026-10-28"
     }
   ]
   ```

### 4.3. Daily Report (Shiraz Format)
1. Download `/api/v1/projects/{project_id}/department-activity-records/reports/daily/?department=warehouse&date=2026-10-28`.
2. Inspect Excel:
   - Header: `گزارش روزانه گردش مصالح و انبار کارگاه — پروژه {proj_name}`
   - Tier 1: `مجموع ورودی روز:` `=SUM(D5:D...)`, `مجموع خروجی روز:` `=SUM(F5:F...)`
   - Tier 2: `تراز خالص گردش مصالح روز (خالص افزایش / کاهش موجودی):` `=D{sum_row}-F{sum_row}`

### 4.4. Weekly Report (Sheet 8 Cumulative Balance)
1. Download `/api/v1/projects/{project_id}/department-activity-records/reports/weekly/?department=warehouse&week_start=2026-10-24`.
2. Inspect Sheet 8:
   - Title: `بالانس تجمعی مصالح`
   - Grouping: unique `(material_type, unit)`
   - Column D: Opening balance (movements before `week_start`)
   - Column E: Total Inbound in week
   - Column F: Total Outbound in week
   - Column G: Native Excel formula `=D{row}+E{row}-F{row}`
   - Summary Row: `=SUM(...)` for columns D, E, F, G.
