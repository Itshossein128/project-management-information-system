# Decision: Quality and HSE

## Context & Screen

- **Route**: `/projects/:projectId/quality-hse`
- **Component**: `QualityHsePage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Quality & HSE link in field sidebar navigation.
- **Inputs**: :projectId path parameter, inspection form fields, nonconformity (NCR) fields, corrective action fields, HSE incident/near-miss entries, work permits, safety training records.

## Authorization & Permissions

- **Required Permissions**: view_reports (viewing report summary); edit_reports (saving inspections, NCRs, HSE events, permits, trainings).
- **Required Roles / Groups**: Project member with field / quality roles.
- **Protection notation**: Protected action requiring specific permissions or roles.

## Desired Result

- **API Call**: GET `/v1/projects/:projectId/quality-safety-report/` via `fetchQualitySafetyReport`, POST inspection/NCR/HSE/permit/training via respective API functions.
- **State Change**: Summary report reflects inspection counts and safety incidents; created records persist and invalidate query cache.
- **Navigation**: `/projects/:projectId/quality-hse`
- **UI Feedback**: Date range filters, metric summary cards, tabbed forms for inspection/NCR/HSE/permits/training, toast messages on save.

## Outcomes & Guards

Saving actions require edit_reports permission and authenticated project membership. Form validations require valid WBS selection and required dates.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Select a project](../README.md)
- [Daily reports](../%5Bnavigate-daily-reports%5D/README.md)
- [Barriers](../%5Bnavigate-barriers%5D/README.md)
- [Risk and delay register](../%5Bnavigate-risk-register%5D/README.md)
- [Retry this action after correcting the failure](README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-quality-hse.tsx](../../../../../../apps/web/src/app/routes/project-quality-hse.tsx)
- [apps/web/src/app/lib/api/quality-hse.ts](../../../../../../apps/web/src/app/lib/api/quality-hse.ts)
- [apps/api/core/risk/views.py](../../../../../../apps/api/core/risk/views.py)
- [apps/api/core/risk/urls.py](../../../../../../apps/api/core/risk/urls.py)
