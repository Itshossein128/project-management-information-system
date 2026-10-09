# Decision: Delete project template

## Context & Screen

- **Route**: `/settings/templates`
- **Component**: `SettingsTemplatesPage`
- **Initial State**: Continue from Template settings. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Open delete control, fill required values and save/confirm.
- **Inputs**: Template form or template ID.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: deleteProjectTemplate mutation.
- **State Change**: Template list refreshes; system template deletion returns 403.
- **Navigation**: `/settings/templates`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Template settings](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/settings-templates.tsx](../../../../../../apps/web/src/app/routes/settings-templates.tsx)
- [apps/api/core/project_templates/views.py](../../../../../../apps/api/core/project_templates/views.py)
- [apps/web/src/app/lib/api/templates.ts](../../../../../../apps/web/src/app/lib/api/templates.ts)
