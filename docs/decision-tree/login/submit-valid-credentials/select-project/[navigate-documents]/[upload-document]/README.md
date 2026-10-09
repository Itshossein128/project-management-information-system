# Decision: Upload a document

## Context & Screen

- **Route**: `/projects/:projectId/documents`
- **Component**: `ProjectDocumentsPage`
- **Initial State**: Continue from Documents and correspondence. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open Upload, choose file and metadata and confirm.
- **Inputs**: File, title/type, discipline, access level and associations.

## Authorization & Permissions

- **Required Permissions**: upload_documents
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: Multipart POST uploadDocument.
- **State Change**: Archive query reloads after upload; restricted documents obey backend visibility rules.
- **Navigation**: `/projects/:projectId/documents`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

File storage must be available for success. This documentation does not establish upload runtime readiness.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Documents and correspondence](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-documents.tsx](../../../../../../../apps/web/src/app/routes/project-documents.tsx)
- [apps/api/core/documents/views.py](../../../../../../../apps/api/core/documents/views.py)
- [apps/web/src/app/lib/api/documents.ts](../../../../../../../apps/web/src/app/lib/api/documents.ts)
