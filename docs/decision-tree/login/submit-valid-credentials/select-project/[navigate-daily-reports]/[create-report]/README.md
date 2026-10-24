# Decision: Create daily report

## Context & Screen

- **Route**: `/projects/:projectId/daily-reports/new` (or `/projects/:projectId/daily-reports/:reportId/edit`)
- **Component**: `DailyReportNewPage` / `DailyReportForm`
- **Initial State**: Continue from Daily reports list.

## Workflow & Features

- **Header Logging**: Set report date (Jalali picker), shift (day/night/full), site status (active/inactive), max/min temperatures, work front, location notes, weather conditions, and general notes.
- **Autosave & Draft Handling**: Automatic offline/online debounced header draft saving. Click "Save Header" / "ایجاد گزارش" to create or update report draft explicitly.
- **Field Section Tabs**: Detail logging across 7 tabs:
  1. *Activities* (فعالیت‌ها)
  2. *Labor* (نیروی انسانی)
  3. *Equipment* (ماشین‌آلات)
  4. *Materials* (مصالح)
  5. *Concrete* (بتن‌ریزی)
  6. *Labor Camp* (کمپ کارگری)
  7. *Incidents* (حوادث)
- **Approval Workflow**:
  - `Submit`: Transition draft report to `submitted` status.
  - `Review`: Change status to `under_review`.
  - `Approve`: Transition status to `approved` and lock report (`is_locked`).
  - `Reject`: Reject report with mandatory reason text.
  - `Correction Request`: Create a new version for locked/approved reports.

## Product Tour & User Onboarding

- **Tour ID**: `project-daily-report-form`
- **Data Tour Anchors**:
  - `[data-tour='daily-report-header']`: Highlights report date, shift, weather, and general location fields.
  - `[data-tour='daily-report-save-header']`: Highlights header save and initial draft creation button.
  - `[data-tour='daily-report-tabs']`: Highlights section tabs for labor, activities, equipment, materials, and incidents.
  - `[data-tour='daily-report-approval-status']`: Highlights approval status bar, version history, and workflow actions (submit, review, approve, reject).

## Authorization & Permissions

- **Required Permissions**: `edit_reports` (for creating and editing drafts), `approve_reports` (for review, approval, and rejection).
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Recovery & Empty/Offline States

- **Offline Support**: Header and tab entries cache locally via IndexedDB (`useDailyReportForm`). When offline, an alert banner indicates local saving; changes automatically sync upon reconnecting.
- **Locked State**: Approved or locked reports disable form fields and display a read-only notification banner with optional correction request trigger.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Save report header](%5Bsave-report-header%5D/README.md)
- [Edit report sections](%5Bedit-report-sections%5D/README.md)

Continue / return links (the same state is documented once):

- [Daily reports](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../README.md).

## Source Evidence

- [apps/web/src/app/routes/daily-report-form.tsx](../../../../../../../apps/web/src/app/routes/daily-report-form.tsx)
- [apps/api/core/field_reports/daily_report_views.py](../../../../../../../apps/api/core/field_reports/daily_report_views.py)
