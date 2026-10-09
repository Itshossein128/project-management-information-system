# Decision: Confirm schedule import

## Context & Screen

- **Route**: `/projects/:projectId/wbs`
- **Component**: `ProjectWBSPage`
- **Initial State**: Continue from Import MSP or P6 schedule. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose append/replace and click Import.
- **Inputs**: The previously previewed file and replace selection.

## Authorization & Permissions

- **Required Permissions**: edit_wbs (start); view_wbs (status polling)
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST startMspImport / startP6Import; GET the corresponding import status.
- **State Change**: Job is polled until success/failure. Success refreshes WBS and activities; parser/job failure stays visible.
- **Navigation**: `/projects/:projectId/wbs`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

The wizard is shared for MSP and P6. A preview is not proof that the queued import completed.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Import MSP or P6 schedule](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-wbs.tsx](../../../../../../../../apps/web/src/app/routes/project-wbs.tsx)
- [apps/api/core/wbs/views.py](../../../../../../../../apps/api/core/wbs/views.py)
- [apps/web/src/components/wbs/msp-import-wizard.tsx](../../../../../../../../apps/web/src/components/wbs/msp-import-wizard.tsx)
- [apps/api/core/schedule/views.py](../../../../../../../../apps/api/core/schedule/views.py)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../../../apps/web/src/app/lib/api/wbs.ts)
