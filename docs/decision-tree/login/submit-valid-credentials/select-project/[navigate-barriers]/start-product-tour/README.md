# Decision: Start Product Tour

## Context & Screen

- **Route**: `/projects/:projectId/barriers`
- **Component**: `ProjectBarriersPage`
- **Initial State**: User is on the Barriers & Issues page.

## Action Taken

- **Trigger**: Click the product tour guide button (`ProductTourButton`) in the page header actions.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: view_reports
- **Required Roles / Groups**: Any project member with view permissions.

## Desired Result

- **API Call**: None.
- **State Change**: Interactive Driver.js product tour initializes and highlights key elements (`barriers-filters`, `barriers-add-button`, `barriers-table`, `barriers-resolve`).
- **Navigation**: `/projects/:projectId/barriers`
- **UI Feedback**: Driver.js popover overlay opens with step-by-step Persian/English guidance.

## Outcomes & Guards

The tour automatically marks itself as seen in `localStorage` (`tour_seen_project-barriers`) upon first launch or completion. Subsequent manual replaying is accessible at any time via the tour button.

## Subsequent Decisions

Continue / return links:

- [Barriers](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-barriers.tsx](../../../../../../../apps/web/src/app/routes/project-barriers.tsx)
- [apps/web/src/components/barriers/BarriersGrid.tsx](../../../../../../../apps/web/src/components/barriers/BarriersGrid.tsx)
- [apps/web/src/components/tour/useProductTour.ts](../../../../../../../apps/web/src/components/tour/useProductTour.ts)
