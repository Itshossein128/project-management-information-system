# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/documents`
- **Component**: `ProjectDocumentsPage`
- **Initial State**: Continue from Documents and correspondence. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Choose Archive, Correspondence or Meetings; search archive or toggle overdue correspondence.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchDocuments / fetchCorrespondence / fetchMeetings.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
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
