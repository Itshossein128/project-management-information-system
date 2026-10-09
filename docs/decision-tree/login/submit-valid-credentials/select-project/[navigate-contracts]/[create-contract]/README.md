# Decision: Create contract

## Context & Screen

- **Route**: `/projects/:projectId/contracts/new`
- **Component**: `ProjectContractFormPage`
- **Initial State**: Continue from Contracts. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click New Contract.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: edit_contracts
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchContractTypes.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/contracts/new`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Save contract](%5Bsave-contract%5D/README.md)
- [Cancel creation](cancel-contract/README.md)

Continue / return links (the same state is documented once):

- [Contracts](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-contract-form.tsx](../../../../../../../apps/web/src/app/routes/project-contract-form.tsx)
- [apps/api/core/contracts/views.py](../../../../../../../apps/api/core/contracts/views.py)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/contracts.ts](../../../../../../../apps/web/src/app/lib/api/contracts.ts)
