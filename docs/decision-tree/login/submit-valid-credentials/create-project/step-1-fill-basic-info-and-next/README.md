# Decision: Complete basic information

## Context & Screen

- **Route**: `/projects/new`
- **Component**: `ProjectCreateWizardPage`
- **Initial State**: Continue from Create a project. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Enter basic information and click Next.
- **Inputs**: project_name, project_code, employer; optional scope, contract, location, manager and unit.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; client-side state only.
- **State Change**: step becomes 2; Next is disabled until name, code and employer are nonempty.
- **Navigation**: `/projects/new`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Complete dates](step-2-fill-dates-and-next/README.md)
- [Return to basic information](step-2-back-to-basic-info/README.md)

Continue / return links (the same state is documented once):

- [Create a project](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-create-wizard.tsx](../../../../../../apps/web/src/app/routes/project-create-wizard.tsx)
- [apps/api/core/projects/views.py](../../../../../../apps/api/core/projects/views.py)
- [apps/web/src/app/lib/api/members.ts](../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/projects.ts](../../../../../../apps/web/src/app/lib/api/projects.ts)
- [apps/web/src/app/lib/api/templates.ts](../../../../../../apps/web/src/app/lib/api/templates.ts)
