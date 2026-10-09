# Decision: Documents and correspondence

## Context & Screen

- **Route**: `/projects/:projectId/documents`
- **Component**: `ProjectDocumentsPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose the corresponding navigation link, card, row action, or open the registered URL.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: view_documents or view_correspondence depending on tab
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchDocuments, fetchCorrespondence, fetchMeetings.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/documents`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

ProjectProvider fetches the project. The registered route remains distinct from sidebar visibility; disabled capabilities hide matching menu entries without removing route registration. Correspondence UI accepts view_correspondence OR view_documents, but its list API specifically requires view_correspondence. Meetings use view_documents.

## Subsequent Decisions

- [Filter or change the displayed view](filter-and-change-view/README.md)
- [Upload a document](%5Bupload-document%5D/README.md)
- [Open/download a document](%5Bdownload-document%5D/README.md)
- [Create correspondence](%5Bcreate-correspondence%5D/README.md)
- [Respond to correspondence](%5Brespond-correspondence%5D/README.md)
- [View meeting minutes](%5Bview-meeting-minutes%5D/README.md)
- [Retry failed load](retry-failed-load/README.md)

Continue / return links (the same state is documented once):

- [Select a project](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-documents.tsx](../../../../../../apps/web/src/app/routes/project-documents.tsx)
- [apps/api/core/documents/views.py](../../../../../../apps/api/core/documents/views.py)
- [apps/web/src/app/lib/api/documents.ts](../../../../../../apps/web/src/app/lib/api/documents.ts)
