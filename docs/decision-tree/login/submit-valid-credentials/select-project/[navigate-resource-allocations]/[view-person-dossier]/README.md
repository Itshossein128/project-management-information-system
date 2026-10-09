# Decision: View personnel dossier

## Context & Screen

- **Route**: `/projects/:projectId/resource-allocations`
- **Component**: `ProjectResourceAllocationsPage`
- **Initial State**: Continue from Resource allocations. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click a person name.
- **Inputs**: Person ID.

## Authorization & Permissions

- **Required Permissions**: view_hr; own dossier can be read by authenticated project member
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Special permission/role gate; directory uses brackets.

## Desired Result

- **API Call**: GET fetchPersonDossier.
- **State Change**: Dossier drawer opens; wage information is separately gated.
- **Navigation**: `/projects/:projectId/resource-allocations`
- **UI Feedback**: The selected state or view is displayed.

## Outcomes & Guards

Loading, empty results and unavailable permissions are states, not evidence of a successful write. Screen/backend guards remain authoritative.

## Subsequent Decisions

Continue / return links (the same state is documented once):

- [Resource allocations](../README.md)

## Source Evidence

- [apps/web/src/app/routes/project-resource-allocations.tsx](../../../../../../../apps/web/src/app/routes/project-resource-allocations.tsx)
- [apps/api/core/hr/capacity_views.py](../../../../../../../apps/api/core/hr/capacity_views.py)
- [apps/web/src/components/hr/PersonDossierPanel.tsx](../../../../../../../apps/web/src/components/hr/PersonDossierPanel.tsx)
- [apps/web/src/app/lib/api/hr-capacity.ts](../../../../../../../apps/web/src/app/lib/api/hr-capacity.ts)
- [apps/web/src/app/lib/api/activities.ts](../../../../../../../apps/web/src/app/lib/api/activities.ts)
- [apps/web/src/app/lib/api/central-data.ts](../../../../../../../apps/web/src/app/lib/api/central-data.ts)
- [apps/web/src/app/lib/api/members.ts](../../../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/wbs.ts](../../../../../../../apps/web/src/app/lib/api/wbs.ts)
