# Decision: Start product tour

## Context & Screen

- **Route**: `/projects/:projectId/risk-register`
- **Component**: `ProjectRiskRegisterPage`
- **Initial State**: Continue from Risk and delay register. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click the product tour guide button in the page header.
- **Inputs**: Mouse click / keyboard interaction on ProductTourButton.

## Authorization & Permissions

- **Required Permissions**: view_reports
- **Required Roles / Groups**: Standard authenticated project members with access to the risk register screen.
- **Protection notation**: Public/standard decision within protected screen; directory does not use brackets.

## Desired Result

- **API Call**: No network call.
- **State Change**: Interactive Driver.js overlay starts, highlighting elements sequentially (`data-tour="risk-matrix"`, `data-tour="risk-filters"`, `data-tour="risk-new-button"`, `data-tour="risk-events-list"`). Saves `tour_seen_project-risk-register` in localStorage.
- **Navigation**: Stays on `/projects/:projectId/risk-register`.
- **UI Feedback**: Driver.js step popovers with Persian/English titles and descriptions, next/prev/done controls.

## Outcomes & Guards

Available on initial load auto-start or manual replay click. Dismissing or completing marks tour as seen in local storage.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Risk and delay register](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-risk-register.tsx](../../../../../../../apps/web/src/app/routes/project-risk-register.tsx)
- [apps/web/src/components/tour/useProductTour.ts](../../../../../../../apps/web/src/components/tour/useProductTour.ts)
- [apps/web/src/components/tour/ProductTourButton.tsx](../../../../../../../apps/web/src/components/tour/ProductTourButton.tsx)
