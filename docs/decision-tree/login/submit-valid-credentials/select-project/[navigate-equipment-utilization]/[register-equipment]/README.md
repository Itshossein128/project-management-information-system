# Decision: Register equipment

## Context & Screen

- **Route**: `/projects/:projectId/equipment-utilization`
- **Component**: `ProjectEquipmentUtilizationPage`
- **Initial State**: Continue from Equipment utilization. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open registry drawer, fill fields and Save.
- **Inputs**: The displayed form/row values.

## Authorization & Permissions

- **Required Permissions**: edit_reports
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: createEquipment mutation.
- **State Change**: The screen’s affected query refreshes after acceptance.
- **Navigation**: `/projects/:projectId/equipment-utilization`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Equipment utilization](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/project-equipment-utilization.tsx](../../../../../../../apps/web/src/app/routes/project-equipment-utilization.tsx)
- [apps/web/src/app/lib/api/equipment.ts](../../../../../../../apps/web/src/app/lib/api/equipment.ts)
