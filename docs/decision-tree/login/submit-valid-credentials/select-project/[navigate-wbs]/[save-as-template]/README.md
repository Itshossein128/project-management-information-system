# Decision: Save WBS as a template

## Context & Screen

- **Route**: `/projects/:projectId/wbs`
- **Component**: `ProjectWBSPage`
- **Initial State**: Continue from WBS. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Save as Template, enter details and confirm.
- **Inputs**: Relevant node/template fields and selected record ID.

## Authorization & Permissions

- **Required Permissions**: edit_wbs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST saveProjectAsTemplate.
- **State Change**: Template is saved; system template creation additionally requires global admin.
- **Navigation**: `/projects/:projectId/wbs`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [WBS](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-wbs.tsx](../../../../../../../apps/web/src/app/routes/project-wbs.tsx)
- [apps/api/core/wbs/views.py](../../../../../../../apps/api/core/wbs/views.py)
- [apps/web/src/components/wbs/wbs-node.tsx](../../../../../../../apps/web/src/components/wbs/wbs-node.tsx)
- [apps/web/src/components/wbs/wbs-empty-state.tsx](../../../../../../../apps/web/src/components/wbs/wbs-empty-state.tsx)
- [apps/web/src/components/templates/save-as-template-modal.tsx](../../../../../../../apps/web/src/components/templates/save-as-template-modal.tsx)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../../apps/web/src/app/lib/api/wbs.ts)
- [apps/web/src/app/lib/api/templates.ts](../../../../../../../apps/web/src/app/lib/api/templates.ts)
