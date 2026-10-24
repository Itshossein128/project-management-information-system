# Decision: Organization references

## Context & Screen

- **Route**: `/settings/org-refs`
- **Component**: `SettingsOrgRefsPage`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Org Refs in global navigation.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: Sidebar roles admin, hr, or business-setup. Catalog reads require `IsAuthenticated`. Creates and updates require `IsOrgRefWriterOrReadOnly`.
- **Required Roles / Groups**: Navigation: `admin`, `hr`, or `business-setup`. Writes also allow staff and superuser. A signed-in user in none of those groups can read the catalogs and cannot create or update them.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchOrganizationUnits, fetchContractTypes.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/settings/org-refs`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Catalog reads stay open to any authenticated user so project setup can load them. Creates and updates require staff, superuser, or the `admin`, `hr`, or `business-setup` groups.

## Subsequent Decisions

- [Create organization unit](%5Bcreate-unit%5D/README.md)
- [Create contract type](%5Bcreate-contract-type%5D/README.md)

Continue / return links (the same state is documented once):

- [Submit valid credentials](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../README.md).

## Source Evidence

- [apps/web/src/app/routes/settings-org-refs.tsx](../../../../../apps/web/src/app/routes/settings-org-refs.tsx)
- [apps/api/core/master_data/ref_views.py](../../../../../apps/api/core/master_data/ref_views.py)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../apps/web/src/app/lib/api/central-data.ts)
