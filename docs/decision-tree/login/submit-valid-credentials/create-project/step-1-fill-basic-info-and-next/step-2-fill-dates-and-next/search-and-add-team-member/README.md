# Decision: Prepare team membership

## Context & Screen

- **Route**: `/projects/new`
- **Component**: `ProjectCreateWizardPage`
- **Initial State**: Continue from Complete dates. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Select a role, search a user (at least two characters) and choose a result; or add an email invite.
- **Inputs**: User or email and role ID.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET lookupUsers; membership additions are deferred.
- **State Change**: Draft members append to the local array; no member API write yet.
- **Navigation**: `/projects/new`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Complete dates](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-create-wizard.tsx](../../../../../../../../apps/web/src/app/routes/project-create-wizard.tsx)
- [apps/api/core/projects/views.py](../../../../../../../../apps/api/core/projects/views.py)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/projects.ts](../../../../../../../../apps/web/src/app/lib/api/projects.ts)
- [apps/web/src/app/lib/api/templates.ts](../../../../../../../../apps/web/src/app/lib/api/templates.ts)
