# Decision: Start screen walkthrough

## Context & Screen

- **Route**: `/projects/:projectId/costs`
- **Component**: `ProjectCostsPage`
- **Initial State**: Navigated to Cost Control & Budget. This node describes the state reached by clicking the ProductTourButton.

## Action Taken

- **Trigger**: Click ProductTourButton.
- **Inputs**: Active project context and costs view.

## Authorization & Permissions

- **Required Permissions**: `view_costs`
- **Required Roles / Groups**: Project roles (e.g. `finance_manager`, `project_manager`, `project_controls`, `planning_engineer`) determine permissions.
- **Protection notation**: Standard authenticated project page; view_costs required to view financial summary and budget breakdown.

## Desired Result

- **API Call**: None; useProductTour / Driver.js UI state.
- **State Change**: Interactive walkthrough highlights Cost KPIs, financial tabs (Budget, Actual Costs, Variance, Cost Pools, CBS Commitments, Payments), budget versions, CBS grid, and budget change requests.
- **Navigation**: `/projects/:projectId/costs`
- **UI Feedback**: Driver.js popover highlights controls with step progress and Next/Prev/Close controls.

## Outcomes & Guards

- **Prerequisites**: Active project with initialized budget structure.
- **Empty States**: If no budget version exists, initial baseline creation controls are presented.
- **Recovery Steps**: Use Next/Prev buttons to navigate steps or Close button / Esc key to exit tour anytime. Replay via the tour button.

## Subsequent Decisions

Continue / return links:

- [Project Costs](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-costs.tsx](../../../../../../../apps/web/src/app/routes/project-costs.tsx)
- [apps/web/src/components/tour/ProductTourButton.tsx](../../../../../../../apps/web/src/components/tour/ProductTourButton.tsx)
- [apps/web/src/components/tour/useProductTour.ts](../../../../../../../apps/web/src/components/tour/useProductTour.ts)
