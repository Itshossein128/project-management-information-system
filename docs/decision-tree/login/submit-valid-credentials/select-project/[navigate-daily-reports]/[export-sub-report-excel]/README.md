# Decision: Export specialty sub-report Excel (FILE 5 / FILE 6)

## Context & Screen

- **Route**: `/projects/:businessId/{buildings,electrical,mechanical,machinery,warehouse,security}` or embedded sub-report panel within Daily Reports
- **Component**: `UnitDailyReportPanel` (`apps/web/src/components/department/unit-daily-report-panel.tsx`)
- **Initial State**: Continue from Specialty Unit management or Daily reports sub-report preview.

## Action Taken

- **Trigger**: Click "خروجی اکسل ابنیه (FILE 5)" or "خروجی اکسل برق (FILE 6)".
- **Inputs**: `:projectId`, `:unit` (discipline name), `:subReportId`.

## Authorization & Permissions

- **Required Permissions**: `view_reports`
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets `[export-sub-report-excel]`.

## Desired Result

- **API Call**: `GET /api/v1/projects/:projectId/units/:unit/daily-reports/:subReportId/excel/` via `fetchSubReportExcel`.
- **State Change**: Browser downloads specialized Excel workbook:
  - **Civil / Architectural (FILE 5)**: Attachment `civil-subreport-{date}-{shift}.xlsx` with columns: `ردیف`, `شیفت`, `پیمانکار`, `استادکار`, `کارگر`, `قطعه`, `بلوک`, `طبقه`, `شرح فعالیت`, `واحد`, `مقدار`, `درصد اجرا` (percentage formatted `0.0%`).
  - **Electrical / Mechanical (FILE 6)**: Attachment `{unit}-subreport-{date}-{shift}.xlsx` with columns: `ردیف`, `شیفت`, `پیمانکار`, `استادکار`, `کارگر`, `بلوک`, `طبقه`, `شرح فعالیت`, `واحد`, `مقدار` (omits parcel and execution percentage).
- **Navigation**: Remains on the specialty unit panel or daily report view.
- **UI Feedback**: Binary spreadsheet downloaded cleanly.

## Outcomes & Guards

Guarded by `canView` (`has("view_reports")`) and backend `HasProjectPermission('view_reports')`.

## Subsequent Decisions

Continue / return links:

- [Project daily reports](../README.md)
- [Discipline subreports](../../%5Bnavigate-sub-reports%5D/README.md)

## Source Evidence

- [apps/web/src/components/department/unit-daily-report-panel.tsx](../../../../../../../apps/web/src/components/department/unit-daily-report-panel.tsx)
- [apps/api/core/sub_reports/shiraz_subreport_excel.py](../../../../../../../apps/api/core/sub_reports/shiraz_subreport_excel.py)
- [apps/api/core/sub_reports/unit_report_views.py](../../../../../../../apps/api/core/sub_reports/unit_report_views.py)
- [apps/web/src/app/lib/api/unit-reports.ts](../../../../../../../apps/web/src/app/lib/api/unit-reports.ts)
