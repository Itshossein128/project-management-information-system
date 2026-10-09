# Decision: Create the draft project

## Context & Screen

- **Route**: `/projects/new`
- **Component**: `ProjectCreateWizardPage`
- **Initial State**: Continue from Complete dates. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Create Project or Skip Team (both invoke the same mutation).
- **Inputs**: Project fields, all accumulated members, optional template.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: POST createProject; then sequential addMember calls and optional applyProjectTemplate.
- **State Change**: Project is created in draft and creator membership is assigned. Selected template opens WBS; otherwise opens overview.
- **Navigation**: `/projects/:projectId/wbs with template; otherwise /projects/:projectId/overview.`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

These requests are sequential, not one transaction. A member/template failure can occur after project creation; the wizard displays an error without rolling back the created project. Retry is not guaranteed to be idempotent. Skip Team does not clear existing draft members.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Select a project](../../../../select-project/README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-create-wizard.tsx](../../../../../../../../apps/web/src/app/routes/project-create-wizard.tsx)
- [apps/api/core/projects/views.py](../../../../../../../../apps/api/core/projects/views.py)
- [apps/web/src/app/lib/api/projects.ts](../../../../../../../../apps/web/src/app/lib/api/projects.ts)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/templates.ts](../../../../../../../../apps/web/src/app/lib/api/templates.ts)
- [apps/api/core/projects/services.py](../../../../../../../../apps/api/core/projects/services.py)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)
