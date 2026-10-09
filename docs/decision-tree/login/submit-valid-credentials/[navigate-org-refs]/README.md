# Decision: Organization references

## Context & Screen

- **Route**: `/settings/org-refs`
- **Component**: `SettingsOrgRefsPage`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Org Refs in global navigation.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: Sidebar roles admin/hr/business-setup; backend IsAuthenticated
- **Required Roles / Groups**: Sidebar: admin, hr or business-setup. API only requires an authenticated user.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchOrganizationUnits, fetchContractTypes.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/settings/org-refs`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

The route and reference APIs do not enforce the sidebar role list as a server role gate.

## Subsequent Decisions

- [Create organization unit](create-unit/README.md)
- [Create contract type](create-contract-type/README.md)

Continue / return links (the same state is documented once):

- [Submit valid credentials](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../README.md).

## Source Evidence

- [apps/web/src/app/routes/settings-org-refs.tsx](../../../../../apps/web/src/app/routes/settings-org-refs.tsx)
- [apps/api/core/master_data/ref_views.py](../../../../../apps/api/core/master_data/ref_views.py)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../apps/web/src/app/lib/api/central-data.ts)
