# Decision: Edit legacy project row

## Context & Screen

- **Route**: `/projects/setup`
- **Component**: `BusinessSetup`
- **Initial State**: Continue from Legacy project setup list. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Edit, fill legacy name/slug fields and save.
- **Inputs**: Legacy row/form fields.

## Authorization & Permissions

- **Required Permissions**: Frontend business-setup; project API edit_project
- **Required Roles / Groups**: business-setup for the frontend/schema gate; additional project write permission where stated.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: PATCH /api/v1/projects/:businessId/.
- **State Change**: Legacy handler attempts update and reloads list; backend field/permission rejection remains possible.
- **Navigation**: `/projects/setup`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Legacy project setup list](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/business-setup.tsx](../../../../../../../apps/web/src/app/routes/business-setup.tsx)
- [apps/api/core/projects/views.py](../../../../../../../apps/api/core/projects/views.py)
