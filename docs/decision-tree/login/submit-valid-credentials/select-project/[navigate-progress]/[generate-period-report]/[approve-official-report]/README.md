# Decision: Approve official period report

## Context & Screen

- **Route**: `/projects/:projectId/progress`
- **Trigger**: Select a generated weekly or monthly report and choose the official approval action.

## Authorization & Permissions

- **Required Permission**: `approve_reports`
- **Project scope**: The server resolves the report through the requested project and rejects cross-project access.

## Desired Result

- **API Call**: `POST /api/v1/projects/:projectId/progress-reports/:reportId/approve/`
- **State Change**: The report becomes `approved`, receives an immutable official serial number, and records `approved_at`/`approved_by`.
- **UI Feedback**: Serial number and extraction timestamp remain visible in the report header; approved figures cannot be overridden.

## Outcomes & Guards

Superseded reports cannot be approved. Repeating approval is idempotent for an already-approved report. Subsequent generation creates a new revision and does not mutate the released record.
