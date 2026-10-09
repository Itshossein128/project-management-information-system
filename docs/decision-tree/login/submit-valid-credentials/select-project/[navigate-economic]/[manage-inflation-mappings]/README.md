# Decision: Manage inflation mappings

## Context & Screen

- **Route**: `/projects/:projectId/economic`
- **Component**: `ProjectEconomicPage`
- **Initial State**: Continue from Economic analysis. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open Add Mapping and save, or delete an editable project mapping.
- **Inputs**: Category/index/weight and mapping ID.

## Authorization & Permissions

- **Required Permissions**: edit_cashflow
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: createInflationMapping / deleteInflationMapping.
- **State Change**: Project mappings refresh; global mapping edits remain server restricted.
- **Navigation**: `/projects/:projectId/economic`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Economic analysis](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-economic.tsx](../../../../../../../apps/web/src/app/routes/project-economic.tsx)
- [apps/api/core/economic/views.py](../../../../../../../apps/api/core/economic/views.py)
- [apps/web/src/components/economic/InflationDetailTable.tsx](../../../../../../../apps/web/src/components/economic/InflationDetailTable.tsx)
- [apps/web/src/app/lib/api/economic.ts](../../../../../../../apps/web/src/app/lib/api/economic.ts)
