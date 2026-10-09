# Decision: Create approved labor rate

## Context & Screen

- **Route**: `/projects/:projectId/resource-allocations`
- **Component**: `ProjectResourceAllocationsPage`
- **Initial State**: Continue from Resource allocations. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Enter amount, validity dates and currency; click Add.
- **Inputs**: Labor-rate form.

## Authorization & Permissions

- **Required Permissions**: edit_wage
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST /api/v1/projects/:projectId/approved-labor-rates/ through apiJson in LaborRatesPanel.
- **State Change**: Rate list refreshes.
- **Navigation**: `/projects/:projectId/resource-allocations`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Resource allocations](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-resource-allocations.tsx](../../../../../../../apps/web/src/app/routes/project-resource-allocations.tsx)
- [apps/api/core/hr/capacity_views.py](../../../../../../../apps/api/core/hr/capacity_views.py)
- [apps/web/src/components/hr/LaborRatesPanel.tsx](../../../../../../../apps/web/src/components/hr/LaborRatesPanel.tsx)
- [apps/web/src/app/lib/api/hr-capacity.ts](../../../../../../../apps/web/src/app/lib/api/hr-capacity.ts)
- [apps/web/src/app/lib/api/activities.ts](../../../../../../../apps/web/src/app/lib/api/activities.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../../apps/web/src/app/lib/api/wbs.ts)
