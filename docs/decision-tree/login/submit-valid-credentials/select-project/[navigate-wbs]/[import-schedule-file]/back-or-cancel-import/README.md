# Decision: Return or cancel import

## Context & Screen

- **Route**: `/projects/:projectId/wbs`
- **Component**: `ProjectWBSPage`
- **Initial State**: Continue from Import MSP or P6 schedule. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click Back or close the wizard.
- **Inputs**: None.

## Authorization & Permissions

- **Required Permissions**: None beyond the parent screen authorization.
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: None; client-side state only.
- **State Change**: Preview selection changes or dialog closes; closing the UI does not imply cancellation of a started server job.
- **Navigation**: `/projects/:projectId/wbs`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [WBS](../../README.md)
- [Import MSP or P6 schedule](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-wbs.tsx](../../../../../../../../apps/web/src/app/routes/project-wbs.tsx)
- [apps/api/core/wbs/views.py](../../../../../../../../apps/api/core/wbs/views.py)
- [apps/web/src/components/wbs/msp-import-wizard.tsx](../../../../../../../../apps/web/src/components/wbs/msp-import-wizard.tsx)
- [apps/api/core/schedule/views.py](../../../../../../../../apps/api/core/schedule/views.py)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../../../apps/web/src/app/lib/api/wbs.ts)
