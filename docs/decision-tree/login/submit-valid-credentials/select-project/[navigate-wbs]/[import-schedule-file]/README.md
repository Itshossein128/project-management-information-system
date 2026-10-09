# Decision: Import MSP or P6 schedule

## Context & Screen

- **Route**: `/projects/:projectId/wbs`
- **Component**: `ProjectWBSPage`
- **Initial State**: Continue from WBS. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Import; choose MSP XML or P6 XER and request Preview.
- **Inputs**: File and format.

## Authorization & Permissions

- **Required Permissions**: edit_wbs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST previewMspImport or previewP6Import.
- **State Change**: Wizard displays the preview, parser warnings and replacement options.
- **Navigation**: `/projects/:projectId/wbs`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

- [Confirm schedule import](%5Bconfirm-import%5D/README.md)
- [Return or cancel import](back-or-cancel-import/README.md)

Continue / return links (the same state is documented once):

- [WBS](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-wbs.tsx](../../../../../../../apps/web/src/app/routes/project-wbs.tsx)
- [apps/api/core/wbs/views.py](../../../../../../../apps/api/core/wbs/views.py)
- [apps/web/src/components/wbs/msp-import-wizard.tsx](../../../../../../../apps/web/src/components/wbs/msp-import-wizard.tsx)
- [apps/api/core/schedule/views.py](../../../../../../../apps/api/core/schedule/views.py)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../../apps/web/src/app/lib/api/wbs.ts)
