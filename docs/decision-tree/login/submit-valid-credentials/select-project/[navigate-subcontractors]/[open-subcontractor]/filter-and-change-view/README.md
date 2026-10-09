# Decision: Filter or change the displayed view

## Context & Screen

- **Route**: `/projects/:projectId/subcontractors/:subId`
- **Component**: `ProjectSubcontractorDetailPage`
- **Initial State**: Continue from Open subcontractor. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Switch Performance, Financial, Warnings and Activities tabs.
- **Inputs**: The visible filter values, grouping, pagination or view mode.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: Tab-specific queries load scores, warnings, activities and financial information.
- **State Change**: The selected query/view changes. Filtered results may be empty; existing records are unchanged.
- **Navigation**: `/projects/:projectId/subcontractors/:subId`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Open subcontractor](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-subcontractor-detail.tsx](../../../../../../../../apps/web/src/app/routes/project-subcontractor-detail.tsx)
- [apps/api/core/subcontractors/views.py](../../../../../../../../apps/api/core/subcontractors/views.py)
- [apps/web/src/app/lib/api/subcontractors.ts](../../../../../../../../apps/web/src/app/lib/api/subcontractors.ts)
- [apps/web/src/app/lib/api/contracts.ts](../../../../../../../../apps/web/src/app/lib/api/contracts.ts)
