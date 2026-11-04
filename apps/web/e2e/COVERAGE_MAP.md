# Complete Application E2E Decision-Tree Coverage Map

## Doc-scenario suite (2026-11-04)

Authoritative scenario contract for `docs/decision-tree/`, `specs/*/spec.md`, and `docs/delivery/R0-scope-and-reports-contract.md`. These tests assert the documented outcome. They do not change application code when the product disagrees with the document.

| Suite | Scenarios registered | File |
|---|---|---|
| Decision-tree nodes, plus a non-member denial for each protected page or mutation | 525 nodes inside the 1706-test suite | `tests/doc-scenarios/decision-tree.spec.ts` |
| Spec acceptance scenarios and edge requirements | 754 acceptance + 111 edge | `tests/doc-scenarios/user-stories.spec.ts` |
| R0 reference fixtures, no standalone transmittal route, report catalog including six T036 names, FILE 4 workbook, daily PDF | 8 | `tests/doc-scenarios/r0-reports-contract.spec.ts` |

`playwright test doc-scenarios --list` registers **1706** tests, including `deep-offline-warehouse.spec.ts` for specs 037, 042, and 043. A sample run on 2026-11-04 passed the login theme toggle, the FILE 4 download (RTL sheet, 34 staff rows, 32 craft rows, native `SUM` formulas), the warehouse field labels, the zero-quantity message, the Shiraz warehouse export labels, and the absence of a transmittal route. Failures were left in place: the machinery workbook path in R0 does not match the file on disk, the report catalog does not yet list the six T036 names, the buildings weekly action is not labeled «دانلود گزارش هفتگی», and an offline unit save does not show «در انتظار همگام‌سازی».

Run: `pnpm --dir apps/web exec playwright test --config e2e/playwright.config.ts doc-scenarios --project=chromium-desktop`

Two inventoried org-ref actions have no README (`create-contract-type`, `create-unit`). Their tests fail until the decision tree documents them. Catalog names that R0 still lists as in progress fail until that catalog is complete.

Source baseline: **2026-10-18**
Decision Tree Validation: **556 decisions, 82 registered routes, 4196 local links; 100% valid & reachable**. The table below is the earlier navigation smoke, not this scenario contract.

| Module / Domain | Flow | Tested Branches | Total Branches | Coverage Score | Test Suite Reference |
|---|---|---|---|---|---|
| **AUTH & ONBOARDING** | Standard login, error feedback, theme toggle, RTL language switcher, password toggle, register link, forgot-password link, logout | 8 | 8 | **100%** | `decision-tree-auth-portfolio.spec.ts` |
| **PORTFOLIO & WORKSPACE** | Portfolio dashboard, figure drill-down drawer, liquidity workbench, HR hub & users navigation | 4 | 4 | **100%** | `decision-tree-auth-portfolio.spec.ts` |
| **GLOBAL ADMIN & SETUP** | Legacy project setup, org refs, templates, roles and permissions catalog | 4 | 4 | **100%** | `decision-tree-auth-portfolio.spec.ts` |
| **PROJECT WIZARD** | Step 1 basic info, step 2 dates, step 3 team, wizard cancellation, draft creation, overview redirect | 10 | 10 | **100%** | `decision-tree-project-wizard-lifecycle.spec.ts` |
| **PROJECT LIFECYCLE** | Kickoff charter save, submit project, approve project, project settings, member management, stakeholders | 8 | 8 | **100%** | `decision-tree-project-wizard-lifecycle.spec.ts` |
| **PLANNING DOMAIN** | WBS tree, activities CRUD, Gantt chart, schedule status, progress curve, activity log, decision support | 10 | 10 | **100%** | `decision-tree-project-domains.spec.ts` |
| **FIELD DOMAIN** | Daily reports list, new daily report, sub-reports, concrete operations, weather log, barriers, risk register, quality & HSE, alerts, sync conflicts | 15 | 15 | **100%** | `decision-tree-project-domains.spec.ts` |
| **COMMERCIAL DOMAIN** | Contracts list, new contract, subcontractors, documents, decisions workflow, cash flow, costs, material balance, procurement (list, new, officer, inventory, reports, blocks, transfers), economic analysis | 18 | 18 | **100%** | `decision-tree-project-domains.spec.ts` |
| **RESOURCES & REPORTING** | Equipment utilization & log, labor productivity, personnel summary, manpower, labor camp, overtime requests, leave requests, resource allocations, role dashboard, standard reports | 12 | 12 | **100%** | `decision-tree-project-domains.spec.ts` |
| **INTERACTIVE WORKFLOWS** | Contracts & IPC tab switching, new contract validation, daily report tabs & sync-conflicts, procurement multi-view workbenches, MCDA decision support engine, Quality & HSE tabs, cost control & budget variance | 15 | 15 | **100%** | `decision-tree-interactive-workflows.spec.ts` |

---

## Decision-Tree E2E Test Suite Summary

1. **`decision-tree-auth-portfolio.spec.ts`** (5 tests):
   - Login screen theme toggling (dark/light mode).
   - Language switching (Persian RTL $\leftrightarrow$ English LTR).
   - Password visibility toggle.
   - Invalid credentials error feedback.
   - Navigation between Login, Register, and Forgot Password.
   - Authenticated app shell navigation across Executive Dashboard, Portfolio Liquidity, HR Hub & Users, Data Admin Setup, Organization Reference Data, Templates, Roles, Notification Drawer, and Sign Out.

2. **`decision-tree-project-wizard-lifecycle.spec.ts`** (3 tests):
   - Multi-step wizard cancellation returning to project list.
   - Full 3-step project wizard forward and backward navigation: Step 1 (Basic Info) $\rightarrow$ Step 2 (Dates) $\rightarrow$ Back to Step 1 $\rightarrow$ Step 2 $\rightarrow$ Step 3 (Team Assignment) $\rightarrow$ Draft Project Creation $\rightarrow$ Redirect to Overview.
   - Project overview charter configuration, settings, members, and stakeholders.

3. **`decision-tree-project-domains.spec.ts`** (4 tests):
   - Complete navigation and component verification across all 5 project domains and all 33 project sub-routes:
     - Planning Domain: WBS, Activities, Gantt, Status, Progress, Activity Log, Decision Support.
     - Field Domain: Daily Reports, New Report, Sub-reports, Concrete Operations, Weather, Barriers, Risk Register, Quality & HSE, Alerts, Sync Conflicts.
     - Commercial Domain: Contracts, New Contract, Subcontractors, Documents, Decisions & Workflow, Cash Flow, Costs, Material Balance, Procurement (List, New, Officer, Inventory, Reports, Blocks, Transfers), Economic.
     - Resources & Reporting: Equipment Utilization, Equipment Log, Labor Productivity, Personnel Summary, Manpower, Labor Camp, Overtime Requests, Leave Requests, Resource Allocations, Role Dashboard, Standard Reports.

4. **`decision-tree-interactive-workflows.spec.ts`** (6 tests):
   - Contracts & IPC Workflow: list navigation, tab switching (Contracts $\leftrightarrow$ IPCs), and new contract form validation.
   - Daily Reports Full Lifecycle: form tab rendering (Activities, Labor, Equipment, Materials, Concrete, Incidents), draft preparation, and `/sync-conflicts` offline recovery route.
   - Procurement Workflow: requisition creation page, line item configuration, officer workbench (`/procurement/officer`), inventory view, transfers, and block management.
   - Decision Support MCDA Engine: method switching, case creation, criteria and alternatives configuration.
   - Quality & HSE Operations: Inspections, NCRs / Corrective Actions, and Work Permits tab navigation.
   - Cost Control & Budget Variance: KPI cards, Budget, Actual Costs, Variance, and Cost Pools tabs with real backend data upsert.
