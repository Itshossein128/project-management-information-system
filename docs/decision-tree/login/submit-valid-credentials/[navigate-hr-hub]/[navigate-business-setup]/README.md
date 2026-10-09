# Decision: Legacy project setup list

## Context & Screen

- **Route**: `/projects/setup`
- **Component**: `BusinessSetup`
- **Initial State**: Continue from Open HR hub. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Businesses setup card (visible to business-setup), or open /projects/setup.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: Frontend business-setup; list API IsAuthenticated
- **Required Roles / Groups**: business-setup for the frontend/schema gate; additional project write permission where stated.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through apiJson project list.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/setup`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Legacy BusinessSetup expects the old business shape. This route is registered, but response compatibility is not established by this source-only pass.

## Subsequent Decisions

- [Edit legacy project row](%5Bedit-legacy-project%5D/README.md)
- [Open project wizard](open-create-wizard/README.md)

Continue / return links (the same state is documented once):

- [Open HR hub](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../../README.md).

## Source Evidence

- [apps/web/src/app/routes/business-setup.tsx](../../../../../../apps/web/src/app/routes/business-setup.tsx)
- [apps/api/core/projects/views.py](../../../../../../apps/api/core/projects/views.py)
