# Decision: Select or clear a template

## Context & Screen

- **Route**: `/projects/new`
- **Component**: `ProjectCreateWizardPage`
- **Initial State**: Continue from Create a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click a template card.
- **Inputs**: template_id.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET fetchProjectTemplate for the selected template.
- **State Change**: Selection and WBS preview update; EPC templates may set contract_type. No project exists yet.
- **Navigation**: `/projects/new`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Create a project](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-create-wizard.tsx](../../../../../../apps/web/src/app/routes/project-create-wizard.tsx)
- [apps/api/core/projects/views.py](../../../../../../apps/api/core/projects/views.py)
- [apps/web/src/app/lib/api/templates.ts](../../../../../../apps/web/src/app/lib/api/templates.ts)
- [apps/web/src/app/lib/api/members.ts](../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/projects.ts](../../../../../../apps/web/src/app/lib/api/projects.ts)
