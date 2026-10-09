# Decision: Respond to correspondence

## Context & Screen

- **Route**: `/projects/:projectId/documents`
- **Component**: `ProjectDocumentsPage`
- **Initial State**: Continue from Documents and correspondence. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click the row response action and supply its required response.
- **Inputs**: Correspondence ID and response payload.

## Authorization & Permissions

- **Required Permissions**: edit_correspondence
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST respondCorrespondence.
- **State Change**: Response/status is updated.
- **Navigation**: `/projects/:projectId/documents`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Documents and correspondence](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-documents.tsx](../../../../../../../apps/web/src/app/routes/project-documents.tsx)
- [apps/api/core/documents/views.py](../../../../../../../apps/api/core/documents/views.py)
- [apps/web/src/app/lib/api/documents.ts](../../../../../../../apps/web/src/app/lib/api/documents.ts)
