# Feature Specification: Cash Flow & Liquidity Allocation Gap Closure

**Feature Branch**: `013-cash-flow-liquidity`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: Implementation Spec `12-جریان نقدی و تخصیص نقدینگی.md` (FR-CASH) — close gaps versus the current application so projected and actual project cash inflows/outflows, monthly net cash need, portfolio liquidity scoring and allocation decisions, double-allocation warnings, and manual simulation are fully covered.

**Source**: [12-جریان نقدی و تخصیص نقدینگی.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/12-جریان%20نقدی%20و%20تخصیص%20نقدینگی.md) (`FR-CASH`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [011-contracts-ipc](../011-contracts-ipc/spec.md) (IPC approval and collection due dates), [012-cost-commitment-payment](../012-cost-commitment-payment/spec.md) (commitment due dates and planned/posted payments)

## Gap Analysis (current vs FR-CASH)

A per-project cash ledger already exists (transactions, manual monthly forecasts, gap analysis, IPC receivables totals, UI tabs). This feature closes **only unmet** FR-CASH portions: domain-fed projections, net-need formula, and portfolio liquidity allocation.

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-CASH-001 | Keep forecast vs actual cash in/out separate per project | `is_forecast` txs + manual `CashFlowForecast`; series partially separate | Ensure projected series is first-class and not mixed with actuals in reports |
| FR-CASH-002 | Inflows from IPC approval + collection due; outflows from commitment dues and planned payments | Actual tx on IPC pay; receivables totals; **no auto monthly projection from IPC dues or commitments** | Build projected in/out from 10/11 feeds by month |
| FR-CASH-003 | Monthly net need = inflow − outflow | Net on actuals / manual forecast only | Monthly net need from projected (and separately actual) series |
| FR-CASH-004 | Suggested net need = essential/urgent costs + due commitments − certain planned receipts | Not implemented | Compute and expose suggested net cash need |
| FR-CASH-005 | Composite priority score: urgency, return, cash-recovery speed, risk | None | Project priority score components + composite |
| FR-CASH-006 | Allocation proposal from available resources + scores | None | Ranked allocation proposal across projects |
| FR-CASH-007 | Final decision with owner and rationale as audit history | None | Decision record with owner, rationale, impact notes |
| FR-CASH-008 | Double-allocation warning; manual simulation; record impact on schedule/cost | None | Overlap warning; save/compare simulation; impact fields |
| FR-CASH-009 | Reports for project and portfolio | Project-scoped only | Portfolio cash / need / allocation report |
| SC-CASH-001 | Cash + need reports for project and portfolio | Partial project | Portfolio + integrated project report |
| SC-CASH-002 | Every allocation decision has owner + rationale | N/A | Enforce on save |
| SC-CASH-003 | Double allocation warned in 100% of tested cases | N/A | Guard + tests |

**Out of scope**: Official company bank accounts / treasury system; Phase-3 advanced what-if scenario analytics beyond one saved manual simulation; redesign of procurement block “liquidity” report (budget vs requisitions).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View project cash flow and net need (Priority: P1)

As project finance, I see monthly projected and actual cash inflows and outflows separately, with monthly net cash need derived from those series, fed by IPC dues and commitment/planned payments where available.

**Why this priority**: Without integrated project cash and net need, allocation and portfolio control have no baseline (FR-CASH-001–004, SC-CASH-001).

**Independent Test**: With an approved IPC that has a collection due date and an approved commitment with a due date (and/or planned payment), open the project cash report → monthly projected in and out appear; net need = in − out; forecast and actual series remain distinct.

**Acceptance Scenarios**:

1. **Given** approved IPCs with collection due dates, **When** projected inflow is built, **Then** months are fed from those approvals and due dates (not only from paid cash).
2. **Given** commitments and planned/due payments, **When** projected outflow is built, **Then** months reflect those dues and the difference versus projected inflow yields monthly net need.
3. **Given** both projected and actual series, **When** the report opens, **Then** the two series are shown separately (no silent merge into one total).
4. **Given** essential/urgent costs, due commitments, and certain planned receipts, **When** suggested net need is requested, **Then** it equals essential/urgent costs + due commitments − certain planned receipts for the period.

---

### User Story 2 - Propose and record liquidity allocation (Priority: P2)

As a steering / finance committee member, I see an allocation proposal ranked by composite scores (urgency, return, cash-recovery speed, risk) against available liquidity, and I record a final decision with owner and rationale—even when it differs from the proposal.

**Why this priority**: Cross-project liquidity decisions need auditable proposals and outcomes (FR-CASH-005–007, SC-CASH-002).

**Independent Test**: Multiple projects with net need → generate proposal ordered by scores and available pool → save a different final decision with owner and reason → history is auditable.

**Acceptance Scenarios**:

1. **Given** several projects with cash need and scores, **When** an allocation proposal is run against available resources, **Then** projects are ordered by scores within the available pool.
2. **Given** a final allocation decision, **When** it is saved, **Then** owner, rationale, and noted impact on schedule/cost are stored as decision history.
3. **Given** incomplete scores for a project, **When** proposal runs, **Then** the system either warns of incomplete data or excludes that project from automatic ranking (with a clear message).

---

### User Story 3 - Prevent double allocation and simulate (Priority: P2)

As finance, I am warned when the same liquidity is allocated twice overlapping periods/projects, I can save a manual simulation and compare it, and allocation impact on each project’s schedule/cost notes is recorded.

**Why this priority**: Prevents silent over-commitment of the same cash (FR-CASH-008, SC-CASH-003).

**Independent Test**: Overlapping allocations warn; one simulation saved and compared; impact fields present on decision.

**Acceptance Scenarios**:

1. **Given** an existing allocation covering a project/period, **When** a second overlapping allocation is entered, **Then** the system warns (and does not silently accept as clean).
2. **Given** a manual simulation of different allocation amounts, **When** it is saved, **Then** it can be retrieved and compared to the current proposal or decision.
3. **Given** zero available resources, **When** proposal is requested, **Then** the proposal is empty with a clear message (not a silent zero fill).

---

### User Story 4 - Portfolio cash and allocation reports (Priority: P2)

As portfolio finance, I produce cash flow, net need, and recorded allocation reports for a single project and across the portfolio.

**Why this priority**: FR-CASH-009 / SC-CASH-001 require portfolio reach beyond project pages.

**Independent Test**: Same data visible at project report and rolled into portfolio report with allocations listed.

**Acceptance Scenarios**:

1. **Given** projects with projected cash and at least one recorded allocation decision, **When** portfolio report is requested, **Then** cash, net need, and decisions appear across projects.
2. **Given** a project without IPCs, **When** projected inflow is shown, **Then** it is empty/unregistered rather than a hidden zero that looks like “no need for data”.

---

### Edge Cases

- **Project without IPCs**: Projected inflow may be empty/unregistered, not a misleading silent zero.
- **Zero available liquidity**: Allocation proposal empty with clear message.
- **Incomplete priority scores**: Proposal warns or excludes from auto-ranking.
- **Actual without projection**: Actual series still reportable independently.
- **Currency**: Single-project reporting follows project/org currency rules from core domain principles; cross-project portfolio assumes a common reporting currency or explicit conversion policy already used by the product (document in assumptions).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST maintain separate projected and actual cash inflow and outflow series per project.
- **FR-002**: Projected inflows MUST be built from approved IPCs and their collection due dates; projected outflows MUST be built from commitment due dates and planned payments (feeds from contracts/IPC and cost commitment features).
- **FR-003**: For each month, the system MUST show net cash need as projected inflow minus projected outflow (and separately support actual in minus actual out).
- **FR-004**: The system MUST expose a suggested net cash need for a period equal to essential/urgent costs + due commitments − certain planned receipts.
- **FR-005**: Each project MUST be able to hold component scores for urgency, return, cash-recovery speed, and risk, plus a defined composite score used in ranking.
- **FR-006**: The system MUST produce an allocation proposal ordered by composite scores within a stated available liquidity pool.
- **FR-007**: Saving a final allocation decision MUST require owner and rationale and MUST retain an auditable history (including when the decision differs from the proposal).
- **FR-008**: The system MUST warn on overlapping/double allocation of the same liquidity for the same project/period; MUST allow saving a manual simulation for comparison; and MUST record noted impact of allocation on schedule and cost per project.
- **FR-009**: Users MUST be able to produce cash flow, net need, and recorded allocation reports for a project and for the portfolio.
- **FR-010**: Manual forecast entry MAY remain available as a supplement; it MUST NOT replace or silently overwrite domain-fed projected series unless the user explicitly chooses to override a period.

### Key Entities

- **Cash Flow Line**: Projected or actual, inflow or outflow, timed to a period/month, with source trace (IPC, commitment, payment, or manual).
- **Project Priority Score**: Urgency, return, recovery speed, risk components and composite.
- **Liquidity Allocation Proposal**: Ranked suggestion against available pool for a decision cycle.
- **Allocation Decision & History**: Final amounts, owner, rationale, impact notes, link to proposal/simulation.
- **Simulation Scenario**: Manual what-if allocation set saved for comparison.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a seeded project with at least one due IPC and one due commitment, finance users can open the project cash report and see distinct projected in, projected out, and monthly net need in under 2 minutes.
- **SC-002**: Portfolio and project reports for cash flow, net need, and recorded allocations are producible in the same product session without exporting to an external spreadsheet as the only path.
- **SC-003**: In 100% of test cases, saving an allocation decision without owner or rationale is rejected.
- **SC-004**: In 100% of test cases, overlapping double allocation of the same liquidity for the same project/period produces a warning (or blocking conflict per product policy), never a silent accept.
- **SC-005**: When available liquidity is zero, the allocation proposal is empty and the empty-state message is understandable to a non-technical finance user.

## Assumptions

- IPC approval and collection due dates come from feature `011-contracts-ipc`; commitment dues and planned/posted payments come from `012-cost-commitment-payment`.
- Existing per-project cash transactions and manual forecasts remain; this feature adds domain-fed projection and portfolio allocation rather than replacing the ledger.
- “Certain planned receipts” means approved IPCs (or equivalent) with due dates that are not yet fully collected; “due commitments” means approved commitments with due dates in the period (and planned payment rows when present).
- “Essential/urgent costs” defaults to approved actual costs or budget lines tagged/filtered as essential for the period when such tagging exists; otherwise due commitments alone drive the cost side of FR-004 with the gap documented in planning.
- Composite score default weights are equal across the four components unless the organization later configures weights; v1 ships equal weights.
- Double-allocation policy in v1 is **warn** (with explicit user acknowledgment to proceed) rather than hard-block, unless planning chooses hard-block.
- Official bank reconciliation and multi-currency FX treasury are out of scope; portfolio views use the organization’s existing reporting currency convention.
- Procurement block liquidity (requisition vs block budget) is a different report and stays unchanged.
- Bilingual (Persian/English) presentation and project-scoped permissions follow the project constitution.
