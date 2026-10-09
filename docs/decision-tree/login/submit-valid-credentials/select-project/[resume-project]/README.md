# Decision: Resume project

## Context & Screen

- **Route**: `/projects/:projectId/overview`
- **Component**: `ProjectOverviewPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click resume in ProjectLifecycleBar.
- **Inputs**: suspended project; optional reason when applicable.

## Authorization & Permissions

- **Required Permissions**: edit_project
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST /api/v1/projects/:projectId/resume/
- **State Change**: Lifecycle changes from suspended to active; project query is invalidated.
- **Navigation**: `/projects/:projectId/overview`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Approval/resume require a project manager, nonempty scope_description and contract_amount. Missing prerequisites return activation_gates_failed. Only transitions allowed by current lifecycle state are valid; archive is read-only for non-global-admin mutations covered by the service.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Select a project](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-overview.tsx](../../../../../../apps/web/src/app/routes/project-overview.tsx)
- [apps/api/core/projects/views.py](../../../../../../apps/api/core/projects/views.py)
- [apps/api/core/projects/kpi_views.py](../../../../../../apps/api/core/projects/kpi_views.py)
- [apps/web/src/components/projects/ProjectLifecycleBar.tsx](../../../../../../apps/web/src/components/projects/ProjectLifecycleBar.tsx)
- [apps/web/src/app/lib/api/projects.ts](../../../../../../apps/web/src/app/lib/api/projects.ts)
- [apps/api/core/projects/lifecycle_service.py](../../../../../../apps/api/core/projects/lifecycle_service.py)
- [apps/web/src/app/lib/api/members.ts](../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/kpis.ts](../../../../../../apps/web/src/app/lib/api/kpis.ts)
