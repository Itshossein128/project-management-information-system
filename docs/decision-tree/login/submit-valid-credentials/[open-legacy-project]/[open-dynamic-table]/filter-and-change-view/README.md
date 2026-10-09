# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:businessId/tables/:tableSlug`
- **Component**: `BusinessTablePage`
- **Initial State**: Continue from Open dynamic table. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Page dynamic table rows.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET the selected dynamic table rows.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/projects/:businessId/tables/:tableSlug`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open dynamic table](../README.md)

## Source Evidence

- [apps/web/src/app/routes/business-table.tsx](../../../../../../../apps/web/src/app/routes/business-table.tsx)
- [apps/api/core/business_meta/data_views.py](../../../../../../../apps/api/core/business_meta/data_views.py)
- [apps/api/core/business_meta/views.py](../../../../../../../apps/api/core/business_meta/views.py)
