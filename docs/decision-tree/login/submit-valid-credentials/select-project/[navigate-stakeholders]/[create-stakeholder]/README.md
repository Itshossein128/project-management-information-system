# Decision: Create stakeholder

## Context & Screen

- **Route**: `/projects/:projectId/stakeholders`
- **Component**: `ProjectStakeholdersPage`
- **Initial State**: Continue from Stakeholders. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Enter stakeholder form and click Add.
- **Inputs**: Stakeholder name/type/contact and displayed values.

## Authorization & Permissions

- **Required Permissions**: edit_project
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST createStakeholder.
- **State Change**: Stakeholder table refreshes.
- **Navigation**: `/projects/:projectId/stakeholders`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Stakeholders](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-stakeholders.tsx](../../../../../../../apps/web/src/app/routes/project-stakeholders.tsx)
- [apps/api/core/projects/stakeholder_views.py](../../../../../../../apps/api/core/projects/stakeholder_views.py)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../apps/web/src/app/lib/api/central-data.ts)
