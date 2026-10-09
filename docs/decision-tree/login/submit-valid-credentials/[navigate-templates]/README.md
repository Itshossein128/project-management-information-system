# Decision: Template settings

## Context & Screen

- **Route**: `/settings/templates`
- **Component**: `SettingsTemplatesPage`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Templates in global navigation.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: Sidebar roles admin/hr/business-setup; backend IsAuthenticated
- **Required Roles / Groups**: Sidebar: admin, hr or business-setup. API only requires an authenticated user.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET through fetchProjectTemplates.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/settings/templates`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Sidebar role filtering does not enforce an equivalent API role gate; ProjectTemplateViewSet uses IsAuthenticated. System templates cannot be edited/deleted.

## Subsequent Decisions

- [Create project template](create-template/README.md)
- [Delete project template](delete-template/README.md)

Continue / return links (the same state is documented once):

- [Submit valid credentials](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../README.md).

## Source Evidence

- [apps/web/src/app/routes/settings-templates.tsx](../../../../../apps/web/src/app/routes/settings-templates.tsx)
- [apps/api/core/project_templates/views.py](../../../../../apps/api/core/project_templates/views.py)
- [apps/web/src/app/lib/api/templates.ts](../../../../../apps/web/src/app/lib/api/templates.ts)
