# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:businessId/job-positions`
- **Component**: `BusinessJobPositionsPage`
- **Initial State**: Continue from Project job positions. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Search, sort and page project positions.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET useJobPositionsForBusinessQuery.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/projects/:businessId/job-positions`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Project job positions](../README.md)

## Source Evidence

- [apps/web/src/app/routes/business-job-positions.tsx](../../../../../../../apps/web/src/app/routes/business-job-positions.tsx)
- [apps/api/core/business_meta/views.py](../../../../../../../apps/api/core/business_meta/views.py)
- [apps/api/core/business_meta/permissions.py](../../../../../../../apps/api/core/business_meta/permissions.py)
