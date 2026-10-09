# Decision: Open project wizard

## Context & Screen

- **Route**: `/projects/setup`
- **Component**: `BusinessSetup`
- **Initial State**: Continue from Legacy project setup list. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Add Business.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; client-side state only.
- **State Change**: Local selection changes; no server mutation.
- **Navigation**: `/projects/new`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Create a project](../../../create-project/README.md)

## Source Evidence

- [apps/web/src/app/routes/business-setup.tsx](../../../../../../../apps/web/src/app/routes/business-setup.tsx)
- [apps/api/core/projects/views.py](../../../../../../../apps/api/core/projects/views.py)
