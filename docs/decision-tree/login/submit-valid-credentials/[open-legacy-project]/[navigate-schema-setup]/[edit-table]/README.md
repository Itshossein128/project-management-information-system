# Decision: Edit dynamic table

## Context & Screen

- **Route**: `/projects/:businessId/setup`
- **Component**: `BusinessSetupSchema`
- **Initial State**: Continue from Legacy table/field schema setup. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Use table edit control and save or confirm.
- **Inputs**: Schema names/types/options and existing IDs.

## Authorization & Permissions

- **Required Permissions**: IsBusinessSetup
- **Required Roles / Groups**: business-setup for the frontend/schema gate; additional project write permission where stated.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: POST/PATCH/DELETE table or field schema endpoint selected by the handler.
- **State Change**: Schema list reloads; canceled forms make no mutation.
- **Navigation**: `/projects/:businessId/setup`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Legacy table/field schema setup](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/business-setup-schema.tsx](../../../../../../../apps/web/src/app/routes/business-setup-schema.tsx)
- [apps/api/core/business_meta/views.py](../../../../../../../apps/api/core/business_meta/views.py)
