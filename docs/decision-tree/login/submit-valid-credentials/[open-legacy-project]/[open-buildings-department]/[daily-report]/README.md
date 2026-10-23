# Decision: Specialty unit daily report & activity export

## Context & Screen

- **Route**: `/projects/:businessId/buildings`
- **Component**: `BusinessBuildingsRoute`
- **Initial State**: Continue from Buildings department activity. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Interact with `UnitDailyReportPanel` (open draft, submit, approve, reject, or correct unit report) or click Activity Log Export.
- **Inputs**: `:businessId`, `report_date` (Jalali date picker or `?date=YYYY-MM-DD` query param), report content / activity records, optional rejection reason for reject.

## Authorization & Permissions

- **Required Permissions**: `view_reports` to read report status & version history; `edit_reports` (with project membership & unit assignment) to open draft, submit, or correct; `approve_reports` (or superuser) to approve or reject. Segregation of Duties (SoD) enforced: submitter cannot approve their own report.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: `POST /api/v1/projects/:projectId/units/buildings/daily-reports/open/` (open/create draft); `POST .../daily-reports/:id/submit/` (submit draft); `POST .../daily-reports/:id/approve/` (approve submitted report); `POST .../daily-reports/:id/reject/` (reject with reason); `POST .../daily-reports/:id/correct/` (create version n+1 draft); `GET .../daily-reports/:id/history/` (view version lineage); or `GET /api/v1/projects/:businessId/department-activity-records/reports/daily/` (export activity log).
- **State Change**: Canonical unit daily report advances through lifecycle (`draft` → `submitted` → `approved` / `rejected`); approved versions deterministically contribute to project daily report summary with full provenance.
- **Navigation**: `/projects/:businessId/buildings`
- **UI Feedback**: Report status badge updates, actionable buttons refresh based on role and SoD constraints, banner displays completeness and feedback.

## Outcomes & Guards

Submitted and approved reports are immutable. An approved report cannot be directly edited; requesting a correction creates a new monotonically incremented version (`version_number` n+1) sharing the same `lineage_id`. Segregation of duties prevents the preparer or submitter from approving their own report unless a superuser break-glass override is used.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Buildings department activity](../README.md)

## Source Evidence

- [apps/web/src/app/routes/business-buildings.tsx](../../../../../../../apps/web/src/app/routes/business-buildings.tsx)
- [apps/web/src/components/department/unit-daily-report-panel.tsx](../../../../../../../apps/web/src/components/department/unit-daily-report-panel.tsx)
- [apps/web/src/components/department/department-page.tsx](../../../../../../../apps/web/src/components/department/department-page.tsx)
- [apps/api/core/sub_reports/views.py](../../../../../../../apps/api/core/sub_reports/views.py)
- [apps/api/core/inventory/views.py](../../../../../../../apps/api/core/inventory/views.py)
