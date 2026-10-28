# Decision: Export daily report PDF

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/:reportId/view`
- **Component**: `DailyReportViewPage` (`apps/web/src/app/routes/daily-report-view.tsx`)
- **Initial State**: Continue from View daily report. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Export PDF ("خروجی PDF").
- **Inputs**: `:projectId`, `:reportId`.

## Authorization & Permissions

- **Required Permissions**: `view_reports`
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets `[export-report-pdf]`.

## Desired Result

- **API Call**: `GET /api/v1/projects/:projectId/daily-reports/:reportId/pdf/` via `fetchReportPdf`.
- **State Change**: Browser downloads standardized PDF named `daily-report-{report_date}-{shift}.pdf`.
- **Security & Formatting Enhancements**:
  - **Draft Watermark**: For non-approved reports (`DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `REJECTED`), a prominent 45-degree diagonal semi-transparent watermark is rendered across every page: «پیش‌نویس — غیرقابل استناد رسمی (DRAFT)».
  - **Approval Signature Blocks**: For approved reports, a formal 3-tier signature table is appended at the document footer:
    1. `تنظیم‌کننده (سرپرست کارگاه)` — Prepared by username + timestamp.
    2. `بررسی‌کننده (دفتر فنی)` — Technical office reviewer username + timestamp.
    3. `تأییدکننده (مدیر پروژه / ناظر مقیم)` — Approver username + timestamp.
  - **Audit Security Fingerprint**: Deterministic 16-character uppercase SHA-256 fingerprint generated from report identity, lineage, report date, shift, status, and approval metadata, displayed in the official footer.
- **Navigation**: Remains on `/projects/:projectId/daily-reports/:reportId/view`.
- **UI Feedback**: PDF binary stream delivered as attachment.

## Outcomes & Guards

Loading, empty results, and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [View daily report](../README.md)

## Source Evidence

- [apps/web/src/app/routes/daily-report-view.tsx](../../../../../../../../apps/web/src/app/routes/daily-report-view.tsx)
- [apps/api/core/field_reports/pdf.py](../../../../../../../../apps/api/core/field_reports/pdf.py)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../../apps/api/core/field_reports/daily_report_views.py)
- [apps/web/src/app/lib/api/daily-reports.ts](../../../../../../../../apps/web/src/app/lib/api/daily-reports.ts)
