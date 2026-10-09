# Decision: Select a project

## Context & Screen

- **Route**: `/projects/:projectId/overview`
- **Component**: `ProjectOverviewPage`
- **Initial State**: Continue from Submit valid credentials. This node describes the state reached by the action below.

## Action Taken

- **Trigger**: Click a project row or its View action.
- **Inputs**: :projectId / :businessId and detail IDs are the selected records; query parameters are optional filters.

## Authorization & Permissions

- **Required Permissions**: IsAuthenticated; active project membership (or global admin).
- **Required Roles / Groups**: Project roles and member overrides determine codenames; see the permission catalog.
- **Protection notation**: Public, standard authenticated, or local action; any parent screen gate still applies.

## Desired Result

- **API Call**: GET through fetchProject, fetchMembers; fetchProjectKpis when view_dashboard is effective.
- **State Change**: Route loads; queries show loading, data or an empty/error state.
- **Navigation**: `/projects/:projectId/overview`
- **UI Feedback**: Permission-gated components may show AccessDenied; APIs may return 403 even when navigation is visible.

## Outcomes & Guards

Sidebar availability is affected by capabilities, not uniformly by project codenames. Overview can load without view_dashboard; KPI requests remain gated.

## Subsequent Decisions

- [Submit project](%5Bsubmit-project%5D/README.md)
- [Approve project](%5Bapprove-project%5D/README.md)
- [Reject project](%5Breject-project%5D/README.md)
- [Suspend project](%5Bsuspend-project%5D/README.md)
- [Resume project](%5Bresume-project%5D/README.md)
- [Complete project](%5Bcomplete-project%5D/README.md)
- [Archive project](%5Barchive-project%5D/README.md)
- [Save kickoff charter](%5Bsave-kickoff-charter%5D/README.md)
- [WBS](%5Bnavigate-wbs%5D/README.md)
- [Activities](%5Bnavigate-activities%5D/README.md)
- [Schedule Gantt](%5Bnavigate-gantt%5D/README.md)
- [Schedule status](%5Bnavigate-schedule-status%5D/README.md)
- [Progress dashboard](%5Bnavigate-progress%5D/README.md)
- [Activity bank](%5Bnavigate-activity-log%5D/README.md)
- [Daily reports](%5Bnavigate-daily-reports%5D/README.md)
- [Sync conflicts](navigate-sync-conflicts/README.md)
- [Weather logs](%5Bnavigate-weather%5D/README.md)
- [Barriers](%5Bnavigate-barriers%5D/README.md)
- [Risk and delay register](%5Bnavigate-risk-register%5D/README.md)
- [Alerts](%5Bnavigate-alerts%5D/README.md)
- [Contracts](%5Bnavigate-contracts%5D/README.md)
- [Subcontractors](%5Bnavigate-subcontractors%5D/README.md)
- [Documents and correspondence](%5Bnavigate-documents%5D/README.md)
- [Cash flow](%5Bnavigate-cash-flow%5D/README.md)
- [Cost control](%5Bnavigate-costs%5D/README.md)
- [Material balance](%5Bnavigate-material-balance%5D/README.md)
- [Procurement](%5Bnavigate-procurement%5D/README.md)
- [Economic analysis](%5Bnavigate-economic%5D/README.md)
- [Equipment utilization](%5Bnavigate-equipment-utilization%5D/README.md)
- [Equipment logs](%5Bnavigate-equipment-log%5D/README.md)
- [Labor productivity](%5Bnavigate-labor-productivity%5D/README.md)
- [Personnel summary](%5Bnavigate-personnel-summary%5D/README.md)
- [Manpower](%5Bnavigate-manpower%5D/README.md)
- [Labor camp](%5Bnavigate-labor-camp%5D/README.md)
- [Overtime requests](%5Bnavigate-overtime-requests%5D/README.md)
- [Leave requests](%5Bnavigate-leave-requests%5D/README.md)
- [Resource allocations](%5Bnavigate-resource-allocations%5D/README.md)
- [Project settings](navigate-project-settings/README.md)
- [Project members](%5Bnavigate-project-members%5D/README.md)
- [Stakeholders](%5Bnavigate-stakeholders%5D/README.md)
- [Discipline subreports](%5Bnavigate-sub-reports%5D/README.md)
- [Concrete operations](%5Bnavigate-concrete-operations%5D/README.md)
- [Retry failed load](retry-failed-load/README.md)

Continue / return links (the same state is documented once):

- [Submit valid credentials](../README.md)

Global header/navigation decisions also remain available: [authenticated app shell](../README.md).

## Source Evidence

- [apps/web/src/app/routes/project-overview.tsx](../../../../../apps/web/src/app/routes/project-overview.tsx)
- [apps/api/core/projects/views.py](../../../../../apps/api/core/projects/views.py)
- [apps/api/core/projects/kpi_views.py](../../../../../apps/api/core/projects/kpi_views.py)
- [apps/web/src/app/lib/api/members.ts](../../../../../apps/web/src/app/lib/api/members.ts)
- [apps/web/src/app/lib/api/kpis.ts](../../../../../apps/web/src/app/lib/api/kpis.ts)
