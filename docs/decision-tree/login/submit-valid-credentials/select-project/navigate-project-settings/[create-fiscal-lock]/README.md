# Decision: Lock fiscal period

## Context & Screen

- **Route**: `/projects/:projectId/settings`
- **Component**: `ProjectSettingsPage`
- **Initial State**: Continue from Project settings. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Enter period start/end and reason and submit.
- **Inputs**: Selected project and action form fields.

## Authorization & Permissions

- **Required Permissions**: edit_project
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: createFiscalLock mutation.
- **State Change**: Active fiscal lock is recorded.
- **Navigation**: `/projects/:projectId/settings`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Project settings](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-settings.tsx](../../../../../../../apps/web/src/app/routes/project-settings.tsx)
- [apps/api/core/projects/views.py](../../../../../../../apps/api/core/projects/views.py)
- [apps/web/src/app/lib/api/projects.ts](../../../../../../../apps/web/src/app/lib/api/projects.ts)
- [apps/web/src/app/lib/api/project-core.ts](../../../../../../../apps/web/src/app/lib/api/project-core.ts)
- [apps/api/core/projects/core_principle_views.py](../../../../../../../apps/api/core/projects/core_principle_views.py)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../apps/web/src/app/lib/api/central-data.ts)
