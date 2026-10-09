# Decision: Undo first WBS root creation

## Context & Screen

- **Route**: `/projects/:projectId/wbs`
- **Component**: `ProjectWBSPage`
- **Initial State**: Continue from Create the first WBS node. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Undo in the 10-second creation toast.
- **Inputs**: The newly created WBS ID.

## Authorization & Permissions

- **Required Permissions**: edit_wbs
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: DELETE deleteWBSNode.
- **State Change**: Created root is deleted if backend dependency checks permit; WBS query refreshes.
- **Navigation**: `/projects/:projectId/wbs`
- **UI Feedback**: Success updates the visible state. An unsuccessful request shows the handler’s error feedback and does not take the success navigation.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Create the first WBS node](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-wbs.tsx](../../../../../../../../apps/web/src/app/routes/project-wbs.tsx)
- [apps/api/core/wbs/views.py](../../../../../../../../apps/api/core/wbs/views.py)
- [apps/web/src/components/wbs/wbs-node.tsx](../../../../../../../../apps/web/src/components/wbs/wbs-node.tsx)
- [apps/web/src/components/wbs/wbs-empty-state.tsx](../../../../../../../../apps/web/src/components/wbs/wbs-empty-state.tsx)
- [apps/web/src/components/templates/save-as-template-modal.tsx](../../../../../../../../apps/web/src/components/templates/save-as-template-modal.tsx)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../../../apps/web/src/app/lib/api/wbs.ts)
- [apps/web/src/app/lib/api/templates.ts](../../../../../../../../apps/web/src/app/lib/api/templates.ts)
