# Decision: Decisions and workflow

## Context & Screen

- **Route**: `/projects/:projectId/decisions-workflow`
- **Component**: `DecisionsWorkflowPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Decisions & workflow link in commercial sidebar navigation.
- **Inputs**: :projectId path parameter, decision record fields (subject, rationale, execution owner), workflow definition fields, instance trigger comments.

## Authorization & Permissions

- **Required Permissions**: view_project OR view_documents (viewing); edit_project (creating decisions, workflow definitions, and instances).
- **Required Roles / Groups**: Project member with view_project or view_documents permission.
- **Protection notation**: Protected action requiring specific permissions or roles.

## Desired Result

- **API Call**: GET `/v1/projects/:projectId/decisions/` via `fetchDecisions`, GET `/v1/projects/:projectId/workflow-definitions/` via `fetchWorkflowDefinitions`, GET `/v1/projects/:projectId/workflow-instances/` via `fetchWorkflowInstances`, POST mutations via respective workflow APIs.
- **State Change**: Decisions list and workflow execution instances displayed; creation forms submit new decisions or start workflow executions.
- **Navigation**: `/projects/:projectId/decisions-workflow`
- **UI Feedback**: Tabbed interface, status pills, execution instance logs drawer, success toasts.

## Outcomes & Guards

Viewing requires active project membership and view_project or view_documents permission. Creating decisions or starting workflow instances requires edit_project permission.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Select a project](../README.md)
- [Contracts](../%5Bnavigate-contracts%5D/README.md)
- [Documents and correspondence](../%5Bnavigate-documents%5D/README.md)
- [Retry this action after correcting the failure](README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-decisions-workflow.tsx](../../../../../../apps/web/src/app/routes/project-decisions-workflow.tsx)
- [apps/web/src/app/lib/api/workflow.ts](../../../../../../apps/web/src/app/lib/api/workflow.ts)
- [apps/api/core/workflow/views.py](../../../../../../apps/api/core/workflow/views.py)
- [apps/api/core/workflow/urls.py](../../../../../../apps/api/core/workflow/urls.py)
