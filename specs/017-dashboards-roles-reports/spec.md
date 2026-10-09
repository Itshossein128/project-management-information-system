# Feature Specification: Dashboards, Roles & Reports

**Feature Branch**: `017-dashboards-roles-reports`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: Implementation Spec `16-داشبوردها نقش‌ها و گزارش‌ها.md` (FR-RPT) — role-based summary views of registered data, filterable standard reports, and role×project access—without making dashboards the system of record for operational facts.

**Source**: [16-داشبوردها نقش‌ها و گزارش‌ها.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/16-داشبوردها%20نقش‌ها%20و%20گزارش‌ها.md) (`FR-RPT`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), approved outputs of features corresponding to implementation specs 07–15 (progress, budget, contracts, cost, cash, EVM, risk/quality, collaboration/workflow)

## Gap Analysis (current vs FR-RPT)

Partial reporting already exists: project-scoped roles and permissions, unified project KPI aggregation, progress/EVM dashboard with some figure provenance, weekly/monthly progress reports, portfolio liquidity report, and various domain lists. This feature closes **unmet** FR-RPT portions: **drill-through** from every dashboard figure to source records with approval status and last-updated time; **role-packaged dashboards** (executive, PM, controls, finance, HR/site, unit managers) filtered by assigned projects and role-appropriate indicators; **segregation of duties** so the creator of a material transaction cannot alone give final approval; a catalog of **standard reports** with common filters and **export metadata** (extraction date + filters); alignment of minimum role set; confidential-field masking on reports; and rule that standard period/portfolio reports use approved data (or explicitly label unapproved).

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-RPT-001 | Dashboard is summary, not SoR | Domain modules are SoR; dashboards partial | Keep SoR in domains; dashboards read-only aggregates |
| FR-RPT-002 | Every figure drills to source + approval + last update | Partial provenance on some progress figures | Systematic drill-through contract for dashboard KPIs |
| FR-RPT-003 | Role + allowed projects filter access and indicators | Project membership + permissions exist; role packs incomplete | Role-based dashboard packs + project scope enforcement |
| FR-RPT-004–009 | Role-specific dashboard contents | Fragmented KPIs / progress / cash / risk UIs | Define and deliver packs (phase-1 subset OK per assumptions) |
| FR-RPT-010–012, 016 | Standard reports, filters, export metadata, approved data | Some period reports; export metadata incomplete | Standard report catalog + filter set + export provenance |
| FR-RPT-013 | Minimum role set | Subset of system roles | Align / document FR minimum roles (map or add) |
| FR-RPT-014 | SoD: create vs final approve | Not consistently enforced | SoD on material transactions |
| FR-RPT-015 | Confidential data hidden by permission | Partial (e.g. wage, contacts) | Apply to report/dashboard surfaces |
| SC-RPT-001–005 | Traceability, access, SoD 0%, export metadata 100%, UAT | Partial | Close with tests and acceptance scenarios |

**In scope**: Role-based dashboards; standard reports; filters; printable/file export with extraction metadata; minimum roles; segregation of create/review/approve for material transactions.

**Out of scope**: Primary capture of operational data (owned by domain specs); visual brand design system; inventing fake zeros for disabled modules.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trace a dashboard figure to its source (Priority: P1)

As an executive or project manager, I can follow any dashboard figure to the underlying records, their approval status, and the time they were last updated.

**Why this priority**: Without drill-through, dashboards cannot be trusted for decisions (FR-RPT-002, SC-RPT-001).

**Independent Test**: Open a budget or progress KPI → drill in → see the constituent records with approval status and last-updated timestamps.

**Acceptance Scenarios**:

1. **Given** a dashboard showing an indicator, **When** the user selects that figure, **Then** they reach the source records with approval status and last-updated time.
2. **Given** unapproved data exists, **When** a standard report is produced from approved data, **Then** that unapproved data is excluded from final totals unless explicitly labeled “unapproved.”

---

### User Story 2 - Role-based dashboard and segregation of duties (Priority: P1)

As a user with a specific role, I see only the indicators and projects I am allowed to see; I cannot alone finally approve a material transaction I created.

**Why this priority**: Access boundaries and SoD are governance requirements for multi-role projects (FR-RPT-003, FR-RPT-014, SC-RPT-002–003).

**Independent Test**: A finance user sees only assigned projects and finance indicators; attempting final approve on own-created material transaction is rejected.

**Acceptance Scenarios**:

1. **Given** a finance role on projects A and B only, **When** the dashboard opens, **Then** project C does not appear.
2. **Given** segregation of duties, **When** the same user created a material transaction, **Then** that user cannot alone complete final approval of that same transaction.
3. **Given** a viewer role, **When** they open dashboards or reports, **Then** they can read allowed summaries but cannot perform workflow actions.

---

### User Story 3 - Standard reports and export metadata (Priority: P2)

As a project controls user, I generate daily/weekly/monthly/portfolio (and other catalog) reports with filters for project, unit, period, contract, WBS/CBS, owner, and status; the export records extraction date and filters used.

**Why this priority**: Operational reporting and audit of what was exported (FR-RPT-010–012, SC-RPT-004).

**Independent Test**: Produce an export with two filters applied → extraction metadata on the file/version shows both filters and extraction date.

**Acceptance Scenarios**:

1. **Given** authorized access, **When** a standard report is requested with filters, **Then** results respect those filters.
2. **Given** an export is generated, **When** the output is inspected, **Then** it includes extraction date and the filter set used (100% of tested cases).
3. **Given** confidential fields (e.g. labor rates), **When** a user without permission views the report, **Then** those fields are hidden.

---

### User Story 4 - Role dashboard packs (Priority: P2)

As users in executive, PM, controls, finance, HR/site, or unit-manager roles, I see a packaged summary covering the indicators defined for my role (using data already registered in upstream domains).

**Why this priority**: Completes FR-RPT-004–009; can ship as an incremental pack after drill-through and access rules exist.

**Independent Test**: For each delivered pack, a user of that role sees the listed indicator groups for allowed projects and does not see packs/indicators outside their role.

**Acceptance Scenarios**:

1. **Given** an executive/steering pack, **When** opened for allowed portfolio scope, **Then** it surfaces portfolio status, budget and forecast final cost, profitability, liquidity need, high risks, milestone delays, and overdue decisions (where upstream data exists).
2. **Given** a PM pack, **When** opened for a project, **Then** it surfaces scope, milestones, plan vs actual, critical activities, unapproved daily reports, risks, open changes, contract status, and overdue actions (where data exists).
3. **Given** a project capability/module is disabled, **When** a dependent indicator would otherwise show, **Then** it is hidden or shown as “inactive,” not as a fabricated zero.

---

### Edge Cases

- **Viewer role**: Read-only; no workflow actions from dashboard/report surfaces.
- **Indicator depends on disabled project module**: Hide or show “inactive,” never invent zero performance.
- **Confidential wage/rate data**: Visible only to roles allowed by HR/core principles (specs 006 / 002).
- **Empty period / no approved data**: Report returns empty sections or zeros only where mathematically valid; no fake “perfect” status.
- **SoD with sole project member**: Final approve requires a different authorized user (or elevated admin path documented); creator alone cannot approve.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Dashboards MUST present a summary view of already-registered data and MUST NOT be the primary place to create operational facts.
- **FR-002**: Every dashboard figure MUST support navigation to constituent source records including approval status and last-updated time.
- **FR-003**: Dashboard access and visible indicators MUST be filtered by the user’s role and allowed projects.
- **FR-004**: An executive / steering dashboard MUST cover portfolio status, budget and forecast final cost, profitability, liquidity need, high risks, milestone delays, and overdue decisions (when upstream data exists).
- **FR-005**: A project manager dashboard MUST cover scope, milestones, plan vs actual, critical activities, unapproved daily reports, risks, open changes, contract status, and overdue actions (when upstream data exists).
- **FR-006**: A project controls dashboard MUST cover WBS, baseline, physical progress, EVM indices, variances, finish forecast, and schedule data quality (when upstream data exists).
- **FR-007**: A project finance dashboard MUST cover budget, commitment, cost, payment, IPC, receivables, collections, and projected cash flow (when upstream data exists).
- **FR-008**: An HR and site dashboard MUST cover capacity, assignment, work/attendance, machinery, materials, stoppages, and barriers (when upstream data exists).
- **FR-009**: A unit-manager dashboard MUST cover unit requests and approvals, pending work, and unit performance summary (when upstream data exists).
- **FR-010**: Standard reports MUST include at least: site daily report, weekly summary, monthly project report, portfolio report, next week/month plan, stakeholder status, changes, risk and issue, procurement and contract status, cash flow, and budget variance.
- **FR-011**: All standard reports MUST support filters by project, unit, time period, contract, WBS/CBS, responsible person, and status (as applicable to the report type).
- **FR-012**: Printable or filed exports MUST record extraction date and the filters used.
- **FR-013**: The product MUST support at least these roles (by name or clear mapping): system admin, executive/approver, project manager, project controls, site specialist, finance, HR, procurement/contracts, supervisor/consultant, viewer.
- **FR-014**: Creating, reviewing, and finally approving a material transaction MUST NOT be completable by a single user alone for the final approve step (segregation of duties).
- **FR-015**: Reports and dashboards MUST hide confidential fields according to the viewer’s permissions.
- **FR-016**: Daily, weekly, monthly, and portfolio standard reports MUST be produced from approved data, or must explicitly label any included unapproved data.

### Key Entities

- **User role and project scope**: Assignment of role(s) to a user within allowed projects.
- **Role dashboard configuration**: Which indicator groups a role pack exposes.
- **Standard report definition**: Named report type, allowed filters, approved-data rules.
- **Report export version**: Stored or downloadable output carrying extraction date and filter metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every tested dashboard figure that claims a numeric aggregate, a user can reach source records showing approval status and last-updated time in under 2 minutes on a seeded project.
- **SC-002**: In 100% of tested cases, a user without membership on a project cannot see that project on role dashboards or portfolio summaries they are allowed to open.
- **SC-003**: In segregation-of-duties tests, 0% of material transactions receive final approval solely from the same user who created them.
- **SC-004**: In 100% of tested exports, the output includes extraction date and the filter set used.
- **SC-005**: Primary operational acceptance scenarios for project manager, site, finance, and project controls roles are executable end-to-end against the delivered dashboards/reports before release (checklisted UAT).
- **SC-006**: Indicators for a disabled project module appear as hidden or “inactive” in 100% of tested cases (never as fabricated zero performance).

## Assumptions

- Indicators are meaningful only when upstream domain data from specs 07–15 is available; phase 1 MAY deliver a **base subset** of role packs (at minimum: PM + finance or controls + executive portfolio strip) with clear “inactive” for missing modules, then expand packs.
- EVM and liquidity calculations are consumed from earned-value and cash-flow features (014 / 013); this feature does not redefine those formulas.
- Security, audit history, and currency rules follow core domain principles (002 / implementation spec 01).
- “Material transaction” for SoD includes at least: cost/payment approvals, IPC approval, budget-change approval, and project lifecycle/change-request final approve; exact list confirmed in planning against existing approve endpoints.
- Existing system roles map to FR-RPT-013 where possible; missing roles (e.g. executive/approver, site specialist, supervisor/consultant) are added or aliased without removing current role codes relied on by tests.
- Brand-level visual design is out of scope; usability follows the existing product UI patterns and bilingual labels.
- Viewer remains read-only for workflow actions from these surfaces.
