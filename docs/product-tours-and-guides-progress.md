# Velora Product Tours & Practical User Guides Progress Checklist

Tracking the daily incremental implementation of Driver.js product tours and practical user guides across all registered routes in Velora.

---

## Status Overview

- **Completed**: 14 routes / workflows
- **In Review (Current PR)**: 1 route / workflow (`/projects/:projectId/costs`)
- **Remaining**: 61 routes / workflows

---

## Completed & Active Tours Matrix

| Route / Workflow | Tour ID | Data Tour Anchors | Guide & Decision Tree Doc | Status |
|---|---|---|---|---|
| `/projects/:projectId/manpower` | `project-manpower` | Date, Type, Counts, Save | Included in screen Tour | Completed |
| `/projects/:projectId/alerts` | `project-alerts` | Tabs, Active List, Ack, Bell, Rules | Included in screen Tour | Completed |
| `/projects/:projectId/procurement` | `procurement-list` | Filters, Fast Actions, Results, Open, Force Majeure Bell | Decision Tree & Tour | Completed |
| `/projects/:projectId/procurement/new` | `procurement-new` | Scope, Block, Scope Guide, GRN, Items, Notes, Save, Need Date, Req Type, Urgency | Decision Tree & Tour | Completed |
| `/projects/:projectId/procurement/req/:reqId` | `procurement-detail` | Stages, Summary, Banner, Items, History, Shortcut, Actions, Assignees, Partial Approve, Suspend | Decision Tree & Tour | Completed |
| `/projects/:projectId/procurement/blocks` | `procurement-blocks` | Actions, Add Block, List | Decision Tree & Tour | Completed |
| `/projects/:projectId/procurement/inventory` | `procurement-inventory` | Block Select, Container, Grid, Issue Transfer, GRN | Decision Tree & Tour | Completed |
| `/projects/:projectId/procurement/officer` | `procurement-officer` | Track Rows, Cards, Officer Identity, Metrics | Decision Tree & Tour | Completed |
| `/projects/:projectId/procurement/reports` | `procurement-reports` | Liquidity Tab, Results, Variance, Audit, Queue | Decision Tree & Tour | Completed |
| `/projects/:projectId/procurement/transfers` | `procurement-transfers` | Doc, Queue, PM Approval | Decision Tree & Tour | Completed |
| `/projects/:projectId/risk-register` | `project-risk-register` | Matrix, Filters, New Button, Event List | Decision Tree & Tour | Completed |
| `/projects/:projectId/daily-reports` | `project-daily-reports` | Stats, Filters, New Button, Table | Decision Tree & Tour | Completed |
| `/projects/:projectId/daily-reports/new` | `project-daily-report-form` | Header, Save Button, Tabs, Approval Status | Decision Tree & Tour | Completed |
| `/projects/:projectId/costs` | `project-costs` | KPI Grid, Tabs, Versions Panel, Budget Grid, Change Requests | Decision Tree & Tour | **In Review (Today)** |

---

## High-Priority Backlog (Next Slices)

1. **Contracts & Payment Certificates (IPC)** (`/projects/:projectId/contracts` & `/ipcs/:ipcId`): Subcontractor/Client contract workflow, IPC submission, and approval chain.
2. **Schedule & WBS** (`/projects/:projectId/wbs` & `/schedule/gantt`): Work breakdown structure, progress entry, and Gantt baseline comparison.
3. **Quality & HSE / Barrier Log** (`/projects/:projectId/barriers`): Non-conformance reporting, site barrier escalation, and closure workflow.
