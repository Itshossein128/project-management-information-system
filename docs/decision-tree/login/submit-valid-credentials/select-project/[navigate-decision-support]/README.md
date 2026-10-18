# Decision: Decision support

## Context & Screen

- **Route**: `/projects/:projectId/decision-support`
- **Component**: `DecisionSupportPage`
- **Initial State**: Continue from Select a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Decision support link in planning sidebar.
- **Inputs**: :projectId path parameter, decision case selections, method matrices (AHP, SAW, TOPSIS, ISM).

## Authorization & Permissions

- **Required Permissions**: view_decision_support (viewing); edit_decision_support (creating/updating cases and running analysis).
- **Required Roles / Groups**: Project member with decision support roles.
- **Protection notation**: Protected action requiring specific permissions or roles.

## Desired Result

- **API Call**: GET `/v1/projects/:projectId/decision-cases/` via `listDecisionCases`, POST/PATCH case via `createDecisionCase`/`patchDecisionCase`, POST `/v1/projects/:projectId/decision-cases/:caseId/runs/` via `createRun`.
- **State Change**: Case loaded/hydrated, matrix entered, calculation executed, ranking results rendered, and execution run history logged.
- **Navigation**: `/projects/:projectId/decision-support`
- **UI Feedback**: Interactive method panels (AHP, TOPSIS, SAW, ISM), validation error badges, ranking result tables, run history pagination.

## Outcomes & Guards

Case evaluation requires pairwise matrices (AHP) or criteria weights and decision matrix (SAW, TOPSIS) or reachability matrix (ISM) to pass mathematical consistency checks. Insufficient permissions prevent mutation/execution.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Select a project](../README.md)
- [WBS](../%5Bnavigate-wbs%5D/README.md)
- [Retry this action after correcting the failure](README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-decision-support.tsx](../../../../../../apps/web/src/app/routes/project-decision-support.tsx)
- [apps/web/src/app/lib/api/decision-support.ts](../../../../../../apps/web/src/app/lib/api/decision-support.ts)
- [apps/api/core/decision_support/views.py](../../../../../../apps/api/core/decision_support/views.py)
- [apps/api/core/decision_support/models.py](../../../../../../apps/api/core/decision_support/models.py)
