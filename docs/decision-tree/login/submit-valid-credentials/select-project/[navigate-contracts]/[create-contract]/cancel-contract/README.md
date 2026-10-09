# Decision: Cancel creation

## Context & Screen

- **Route**: `/projects/:projectId/contracts/new`
- **Component**: `ProjectContractFormPage`
- **Initial State**: Continue from Create contract. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Cancel / Contracts.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; client-side state only.
- **State Change**: Local selection changes; no server mutation.
- **Navigation**: `/projects/:projectId/contracts`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Contracts](../../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-contract-form.tsx](../../../../../../../../apps/web/src/app/routes/project-contract-form.tsx)
- [apps/api/core/contracts/views.py](../../../../../../../../apps/api/core/contracts/views.py)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/contracts.ts](../../../../../../../../apps/web/src/app/lib/api/contracts.ts)
