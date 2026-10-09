# Decision: Create organization unit

## Context & Screen

- **Route**: `/settings/org-refs`
- **Component**: `SettingsOrgRefsPage`
- **Initial State**: Continue from Organization references. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Enter unit code/name and submit.
- **Inputs**: Displayed reference form values.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: createOrganizationUnit mutation.
- **State Change**: Reference list refreshes.
- **Navigation**: `/settings/org-refs`
- **UI Feedback**: Accepted requests update the described state. Rejected requests follow the component’s error handler; explicit error feedback exists only where the component renders it.

## Outcomes & Guards

Use only the controls available for the current record status. Required form fields and server validation can prevent the success outcome.

A pending request uses the component’s busy/disabled state where implemented. Validation, permission or network failure follows its error handler; do not infer rollback or idempotency for a sequence of requests. Correct the input or access issue before retrying. Cancel/close on an unsent form makes no API write; closing after submission does not undo a request.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Organization references](../README.md)
- [Retry this action after correcting the failure](README.md)

## Source Evidence

- [apps/web/src/app/routes/settings-org-refs.tsx](../../../../../../apps/web/src/app/routes/settings-org-refs.tsx)
- [apps/api/core/master_data/ref_views.py](../../../../../../apps/api/core/master_data/ref_views.py)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../apps/web/src/app/lib/api/central-data.ts)
