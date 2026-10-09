# Feature Specification: Multi-Level Budget Gap Closure

**Feature Branch**: `010-multi-level-budget`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: Implementation Spec `09-بودجه چندسطحی.md` (FR-BUD) — close gaps versus the current application so multi-level budget versions, approved-change-only edits, remaining allocatable, and project ceiling control are fully covered.

**Source**: [09-بودجه چندسطحی.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/09-بودجه%20چندسطحی.md) (`FR-BUD`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [003-central-data-model](../003-central-data-model/spec.md), [004-wbs-structure](../004-wbs-structure/spec.md), [008-project-registration](../008-project-registration/spec.md), Implementation Specs 01–04; feeds remaining from commitments/actuals (spec 11 / existing cost_control)

## Gap Analysis (current vs FR-BUD)

This feature closes **only the unmet** portions of FR-BUD. Existing flat budget rows (WBS/activity × cost category), bulk upsert grid, CBS tree, commitments/payments, cost summary KPIs, and variance remain in place and are **out of scope** except where a gap explicitly extends them.

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-BUD-001 | Budget structure at project, phase, contract, WBS package, CBS, and optional time period | `Budget` rows: WBS and/or activity required; optional CBS; no project-only, phase, contract, or period dimensions | Multi-level lines on a version; phase = WBS phase node; contract FK; optional period dates; project-level lines |
| FR-BUD-002 | Separate initial / approved / revised / final-forecast versions; comparable | No version entity; all rows are mutable live amounts | `BudgetVersion` types + status; compare versions |
| FR-BUD-003 | Change approved budget only via change request (reason, amount, affected headings, project impact, approvers, new version) | Direct create/PATCH/bulk upsert always allowed | Lock approved versions; `BudgetChangeRequest` lifecycle → new revised version |
| FR-BUD-004 | Remaining allocatable = approved − consumed − committed | Summary has total budget/actual/committed; no per-heading remaining allocatable API/UI | Remaining by line / CBS / category from approved version |
| FR-BUD-005 | Intra-budget transfer with ceiling and allowed headings | No transfer API | Transfer between lines under approved version with rules |
| FR-BUD-006 | Must not exceed project approved ceiling without approved budget change | WBS overrun is warning only; no hard project ceiling gate on allocation | Hard block when allocation/transfer would exceed approved project ceiling |
| FR-BUD-007 | Register initial budget and submit for approval | Bulk upsert with no draft/submit/approve | Version draft → submit → approve → becomes approved baseline |
| SC-BUD-001 | User can register initial budget and submit for approval | Partial (register only) | Full submit path |
| SC-BUD-002 | Budget change only via approved workflow | Not enforced | Enforce |
| SC-BUD-003 | Remaining per heading; block over-allocation | Not enforced | Compute + block |

**Out of scope**: Official general ledger; detailed commitment/actual posting rules beyond consuming remaining (11); full EVM (13); portfolio budget rollups (16).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register and submit initial budget for approval (Priority: P1)

As project controls / finance, I register an initial budget at allowed levels (project, phase, contract, WBS package, CBS, optional period) and submit it for approval. After approval it becomes the comparable approved version.

**Why this priority**: Closes FR-BUD-001, FR-BUD-002, FR-BUD-007, SC-BUD-001; without versioned approval there is no control baseline.

**Independent Test**: Create draft initial version with WBS and CBS lines; submit; approve → status approved and comparable; direct edit of approved lines rejected.

**Acceptance Scenarios**:

1. **Given** an active project, **When** an authorized user creates a draft **initial** budget version and adds lines at project / phase (WBS phase) / contract / WBS / CBS (optional period), **Then** a comparable version with those lines is stored.
2. **Given** a draft initial version with at least one line, **When** it is submitted and approved by an authorized approver, **Then** it is versioned as **approved** and becomes the ceiling baseline for control.
3. **Given** an approved version, **When** a user attempts direct line create/update/delete or bulk overwrite on that version, **Then** the system rejects the mutation.

---

### User Story 2 - Budget change only via approved workflow (Priority: P1)

As a project manager, changing an approved budget requires a change request that captures reason, amount delta, affected headings, impact on project outcome, approvers, and produces a new revised version on approval. Allocation that would exceed the project approved ceiling without an approved change is blocked.

**Why this priority**: FR-BUD-003, FR-BUD-006, SC-BUD-002.

**Independent Test**: Direct edit of approved budget rejected; create change request → approve → new revised version; attempt allocation past project ceiling without CR → blocked.

**Acceptance Scenarios**:

1. **Given** an approved budget, **When** a change request is registered with reason, amount, affected headings, project-impact note, and intended approver role path, **Then** the request is stored and a new version is prepared only after approval.
2. **Given** no approved change that raises the ceiling, **When** an allocation or transfer would push total allocated above the project approved budget ceiling, **Then** the system blocks the action with a clear code.
3. **Given** a rejected or cancelled change request, **When** viewing the budget, **Then** the approved version amounts are unchanged.

---

### User Story 3 - Remaining allocatable and controlled transfers (Priority: P2)

As project finance, I see remaining allocatable per heading (approved − committed − consumed) and can move amounts within the budget only under ceiling and allowed-heading rules.

**Why this priority**: FR-BUD-004, FR-BUD-005, SC-BUD-003.

**Independent Test**: After posting commitment and actual against a CBS/WBS heading, remaining updates; transfer within allowed headings succeeds; transfer that violates ceiling or forbidden heading fails.

**Acceptance Scenarios**:

1. **Given** an approved version and posted commitments/actuals linked to headings, **When** remaining allocatable is requested, **Then** each heading shows approved − committed − consumed (not below zero without explicit overspend policy — v1 clamps display to zero with overrun flag).
2. **Given** an approved version, **When** a transfer moves amount from heading A to heading B within allowed set and under project ceiling, **Then** both lines update on a transfer audit entry (same version; does not require full CR if net project total unchanged).
3. **Given** a heading without CBS when CBS is expected for commitment/actual finalization, **When** viewing remaining, **Then** a warning is surfaced (blocking of cost/commitment finalize remains with module 11 / existing CBS rules).

---

### Edge Cases

- Heading without CBS → warning on remaining views; final commitment/cost posting may still be blocked by existing CBS rules (11).
- Comparing versions in different currencies → only with an explicit FX rate supplied on the compare request (otherwise reject).
- Final forecast without approval → visible and comparable but **not** used as ceiling control baseline.
- Existing legacy `Budget` rows without a version → migration attaches them to a synthetic approved initial version per project (or draft if project budget never approved) so the grid keeps working.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow budget lines on a version at levels: project, phase (WBS phase node), contract, WBS package, CBS, and optional time period (`period_start`/`period_end`).
- **FR-002**: System MUST maintain separate version kinds: initial, approved, revised, final_forecast; versions MUST be listable and comparable.
- **FR-003**: Changing amounts on an approved control baseline MUST require a budget change request with reason, amount delta, affected headings, project-impact text, and approval path; approval MUST produce a new revised version.
- **FR-004**: System MUST compute remaining allocatable as approved amount − committed − consumed for headings and expose it in API/UI.
- **FR-005**: Intra-budget transfers MUST enforce project ceiling and allowed source/target headings; net-zero transfers that stay under ceiling MAY proceed without a full change request.
- **FR-006**: Allocation or transfer that would exceed the project approved budget ceiling without an approved raising change MUST be rejected.
- **FR-007**: Users MUST be able to create a draft initial version, edit its lines, submit for approval, and approve/reject.
- **FR-008**: Final forecast versions MUST be creatable and visible without becoming the ceiling baseline until explicitly approved via the same approval path (if promoted).

### Key Entities

- **BudgetVersion**: Project-scoped version with kind (initial/approved/revised/final_forecast), status (draft/submitted/approved/rejected), version number, currency, optional notes, audit fields.
- **BudgetLine** (extends current Budget): Belongs to a version; level + optional FKs (wbs/phase wbs, contract, cbs, activity); cost category; amount; optional period; notes.
- **BudgetChangeRequest**: Reason, amount delta, affected line proposals, project impact, status, requester, decision metadata, resulting version FK.
- **BudgetTransfer**: Audit of intra-version moves (from/to line, amount, actor, timestamp).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authorized user can register an initial budget version and submit it for approval in one guided flow; approval produces an approved baseline within the same session for typical project sizes (&lt;500 lines).
- **SC-002**: In 100% of tested cases, direct mutation of an approved control baseline fails; only approved change requests alter control amounts.
- **SC-003**: Remaining allocatable matches approved − committed − consumed for sampled headings; 100% of tested over-ceiling allocations are blocked.
- **SC-004**: Users can compare two versions and see per-heading amount differences when currencies match (or explicit FX is provided).

## Assumptions

- Commitments and actual costs already in `cost_control` feed consumed/committed for remaining (spec 11); this feature does not redesign posting.
- Project approved ceiling for FR-BUD-006 is the sum of amounts on the current **approved control** budget version (kinds `approved` or latest approved `revised`); project `contract_amount` / `budget_approved_at` from FR-PRJ remain the project-registration gate and are not replaced.
- Phase level uses existing WBS nodes marked as phase (or top-level / `package_type` phase where present); no separate Phase master table in v1.
- “Approvers” on change requests reuse project permission `approve_costs` (same pattern as project CR `approve_project`); named multi-step approver lists are out of scope for v1.
- Legacy budget rows are migrated onto one version per project so existing BudgetGrid continues to function against the working draft or approved version.
- This module is not a legal ledger (constitution / spec 01).
