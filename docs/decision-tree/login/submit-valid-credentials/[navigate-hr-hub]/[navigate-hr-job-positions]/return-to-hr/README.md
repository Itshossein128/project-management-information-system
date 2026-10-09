# Decision: Return to HR

## Context & Screen

- **Route**: `/hr/job-positions`
- **Component**: `HrJobPositionsPage`
- **Initial State**: Continue from HR job positions. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Back.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; client-side state only.
- **State Change**: Local selection changes; no server mutation.
- **Navigation**: `/hr`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open HR hub](../../README.md)

## Source Evidence

- [apps/web/src/app/routes/hr/job-positions.tsx](../../../../../../../apps/web/src/app/routes/hr/job-positions.tsx)
