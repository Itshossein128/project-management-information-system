# Developer Quickstart: Shiraz Excel Parity & Official PDF Standardization

## Overview

This guide explains how to verify and test the Shiraz Excel Parity and Official PDF Standardization features.

---

## 1. Environment Verification

Ensure PostgreSQL and Redis are running:
```bash
pg_isready -p 5433
redis-cli ping
```

---

## 2. Running Automated Backend Tests

Run the dedicated test suites for daily reports, sub-reports, Excel exports, and PDF formatting:
```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest field_reports/tests/ sub_reports/tests/ --reuse-db
```

---

## 3. Verifying Endpoints via cURL

### 3.1 Shiraz FILE 4 Daily Report Excel Export
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/v1/projects/<PROJECT_ID>/daily-reports/<REPORT_ID>/excel/ \
  -o daily-report.xlsx
```
Verify:
- Worksheet orientation is Right-to-Left (`RTL`).
- Section A contains 34 indirect titles with `=SUM(...)` subtotal.
- Section B contains 32 direct titles with `=SUM(...)` subtotal and grand total.

### 3.2 Shiraz FILE 5 Civil Sub-Report Excel Export
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/v1/projects/<PROJECT_ID>/units/buildings/daily-reports/<REPORT_ID>/excel/ \
  -o civil-subreport.xlsx
```
Verify:
- Header contains "شرکت پی‌چین" and "اجرای ابنیه".
- Contains columns `قطعه` and `درصد اجرا` (formatted as `0.0%`).

### 3.3 Shiraz FILE 6 Electrical Sub-Report Excel Export
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/v1/projects/<PROJECT_ID>/units/electrical/daily-reports/<REPORT_ID>/excel/ \
  -o electrical-subreport.xlsx
```
Verify:
- Header contains "اجرای تأسیسات برقی".
- Strictly omits `قطعه` and `درصد اجرا`.

### 3.4 Official PDF Export with Signatures & Watermark
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/api/v1/projects/<PROJECT_ID>/daily-reports/<REPORT_ID>/pdf/ \
  -o daily-report.pdf
```
Verify:
- Draft reports have diagonal "پیش‌نویس — غیرقابل استناد رسمی (DRAFT)" watermark.
- Approved reports omit the watermark.
- Concluding page features 3 signature boxes with Audit Hash.
- Attachment filename is `daily-report-{report_date}-{shift}.pdf`.

---

## 4. Frontend Verification & Build

```bash
pnpm --filter web build
```
Verify:
- `daily-reports-list.tsx`: Filter state persists in browser URL query string.
- `project-activity-log.tsx`: Multi-dimensional filters persist in browser URL query string, summary bar calculates man-days and unit quantities, and "خروجی اکسل (FILE 1)" triggers database download.
- `daily-report-view.tsx`: Excel FILE 4 and PDF download buttons operate properly.
- `unit-daily-report-panel.tsx`: Excel download button is present.
