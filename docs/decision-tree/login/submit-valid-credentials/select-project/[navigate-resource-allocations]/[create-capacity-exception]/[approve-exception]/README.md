# Decision: Approve capacity exception

## Context & Screen

- **Route**: `/projects/:projectId/resource-allocations`
- **Component**: `ProjectResourceAllocationsPage`
- **Initial State**: Continue from Create capacity exception. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click approve for an eligible exception.
- **Inputs**: Exception ID and decision notes.

## Authorization & Permissions

- **Required Permissions**: approve_hr
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: approveCapacityException mutation.
- **State Change**: Exception workflow updates; an approved exception may enable allocation retry.
- **Navigation**: `/projects/:projectId/resource-allocations`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Resource allocations](../../README.md)
- [Create capacity exception](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-resource-allocations.tsx](../../../../../../../../apps/web/src/app/routes/project-resource-allocations.tsx)
- [apps/api/core/hr/capacity_views.py](../../../../../../../../apps/api/core/hr/capacity_views.py)
- [apps/web/src/app/lib/api/hr-capacity.ts](../../../../../../../../apps/web/src/app/lib/api/hr-capacity.ts)
- [apps/web/src/components/hr/CapacityExceptionPanel.tsx](../../../../../../../../apps/web/src/components/hr/CapacityExceptionPanel.tsx)
- [apps/web/src/app/lib/api/activities.ts](../../../../../../../../apps/web/src/app/lib/api/activities.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../../../apps/web/src/app/lib/api/wbs.ts)
