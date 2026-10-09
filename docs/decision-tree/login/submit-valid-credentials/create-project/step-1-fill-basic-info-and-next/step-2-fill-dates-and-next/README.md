# Decision: Complete dates

## Context & Screen

- **Route**: `/projects/new`
- **Component**: `ProjectCreateWizardPage`
- **Initial State**: Continue from Complete basic information. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Select dates and click Next.
- **Inputs**: start_date required; optional planned_finish_date, amount and currency.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; client-side state only.
- **State Change**: step becomes 3; start_date enables Next; backend still validates the final payload.
- **Navigation**: `/projects/new`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

- [Prepare team membership](search-and-add-team-member/README.md)
- [Return to dates](step-3-back-to-dates/README.md)
- [Create the draft project](create-draft-project/README.md)

Continue / return links (the same state is documented once):

- [Complete basic information](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-create-wizard.tsx](../../../../../../../apps/web/src/app/routes/project-create-wizard.tsx)
- [apps/api/core/projects/views.py](../../../../../../../apps/api/core/projects/views.py)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/projects.ts](../../../../../../../apps/web/src/app/lib/api/projects.ts)
- [apps/web/src/app/lib/api/templates.ts](../../../../../../../apps/web/src/app/lib/api/templates.ts)
