# Decision: Open/download a document

## Context & Screen

- **Route**: `/projects/:projectId/documents`
- **Component**: `ProjectDocumentsPage`
- **Initial State**: Continue from Documents and correspondence. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click document file link.
- **Inputs**: file_url.

## Authorization & Permissions

- **Required Permissions**: view_documents and document visibility
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: Browser follows file_url.
- **State Change**: File opens/downloads if its URL is accessible; no archive mutation.
- **Navigation**: `/projects/:projectId/documents`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Documents and correspondence](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-documents.tsx](../../../../../../../apps/web/src/app/routes/project-documents.tsx)
- [apps/api/core/documents/views.py](../../../../../../../apps/api/core/documents/views.py)
- [apps/web/src/app/lib/api/documents.ts](../../../../../../../apps/web/src/app/lib/api/documents.ts)
