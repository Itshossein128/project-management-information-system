# Feature Specification: Contracts & IPC Gap Closure

**Feature Branch**: `011-contracts-ipc`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: Implementation Spec `10-قرارداد و صورت‌وضعیت.md` (FR-CON) — close gaps versus the current application so contracts with payment terms and addenda, IPC submitted/approved amounts with deductions and due dates, partial collections that never mutate approval status, and overdue/near-due receivables reporting are fully covered.

**Source**: [10-قرارداد و صورت‌وضعیت.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/10-قرارداد%20و%20صورت‌وضعیت.md) (`FR-CON`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [003-central-data-model](../003-central-data-model/spec.md) (IPC collections), [008-project-registration](../008-project-registration/spec.md)

## Gap Analysis (current vs FR-CON)

Much of FR-CON already exists (Contract + ChangeOrder, IPC workflow, deductions, IPCCollection, overdue IPC filter, cash-flow receivables summary). This feature closes **only unmet** portions.

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-CON-001 | Contract: number, amount, type, validity, **payment terms**, addenda, project-linked | Number/amount/type/dates/pct fields/change orders exist; free-text **payment terms** missing | Add `payment_terms` + form field |
| FR-CON-002 | IPC: period, **submitted amount**, **approved amount**, deductions, final payable, approval status, due date | `gross_amount` + deductions + `net_amount` + status + `planned_payment_date`; no distinct submitted vs approved snapshot | Snapshot `submitted_amount` on submit; `approved_amount` on approve (editable ≤ submitted with note) |
| FR-CON-003 | Cash receipt must not auto-change approval status | Collections do not change status; `pay` is separate — needs regression lock | Explicit invariant test + guard if any path auto-PAIDs from collection |
| FR-CON-004 | Multi partial collections on same IPC; never overwrite original amounts | Implemented in 003 | Regression tests only |
| FR-CON-005 | Overdue **and near-due** receivables reportable | `?overdue=true` + cash-flow totals; no near-due band or contracts-native line report | Receivables report: overdue + near-due (N days) with IPC lines |
| FR-CON-006 | Traceable through final collection | Detail includes collections; OK | Ensure final-collection remaining=0 visible in report |
| FR-CON-007 | IPC without project forbidden | Project FK required | Regression |
| SC-CON-001 | Trace to final collection | Partial | Report + UI |
| SC-CON-002 | Partial collection never rewrites submitted | Exists | Locked by test |
| SC-CON-003 | Overdue approved unpaid IPCs in report | Filter exists | Near-due + dedicated report payload |

**Out of scope**: Purchase commitments/cost payments (11); aggregated cash-flow module redesign (12); subcontract CRM beyond existing links.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register contract with payment terms and addenda (Priority: P1)

As a contracts officer, I register a project contract with number, amount, type, validity dates, **payment terms text**, and later add an addendum (change order) that updates amount while preserving history.

**Why this priority**: Completes FR-CON-001.

**Independent Test**: Create contract with payment_terms; add and approve change order → adjusted amount updates; payment_terms persists.

**Acceptance Scenarios**:

1. **Given** an active project, **When** a contract is saved with number, amount, type, start/finish, payment terms, **Then** it is linked to the project and retrievable with those fields.
2. **Given** an existing contract, **When** an addendum (change order) is registered and approved, **Then** amount/conditions are updated and history is retained.

---

### User Story 2 - IPC cycle: submit → approve amounts → partial collections (Priority: P1)

As finance / technical office, I submit an IPC with a submitted amount, approve with an approved amount and deductions and a due date; I record partial collections without changing approval status or rewriting submitted/approved amounts.

**Why this priority**: FR-CON-002–004, SC-CON-001–002.

**Independent Test**: Submit → approve (approved ≤ submitted) → two collections → status still approved; gross/submitted unchanged; remaining decreases.

**Acceptance Scenarios**:

1. **Given** a submitted IPC, **When** technical/financial approval happens, **Then** approved amount and deductions are stored separately from submitted amount, with due date.
2. **Given** cash received, **When** a collection is recorded, **Then** approval status does not auto-change solely because of receipt.
3. **Given** multiple partial receipts, **When** collections are listed, **Then** all appear on the same IPC and submitted/approved amounts are not overwritten.

---

### User Story 3 - Overdue and near-due receivables report (Priority: P2)

As finance manager, I get a report of overdue and near-due approved unpaid IPCs (receivables).

**Why this priority**: FR-CON-005, SC-CON-003.

**Independent Test**: Approved IPC with past due date appears in overdue; one due within N days appears in near-due; fully collected does not.

**Acceptance Scenarios**:

1. **Given** approved IPCs with past planned payment dates and remaining receivable &gt; 0, **When** the receivables report is requested, **Then** they appear as overdue.
2. **Given** approved IPCs due within the near-due window, **When** the report is requested, **Then** they appear as near-due.
3. **Given** an IPC with remaining receivable 0, **When** reported, **Then** it is excluded from overdue/near-due open receivables.

---

### Edge Cases

- Approved amount less than submitted → variance/deduction note required or stored.
- Contract without IPCs → allowed.
- Multiple contracts per project → report aggregates at project level.
- Collection before approve → rejected (policy: collections only when approved).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Contracts MUST store payment terms text in addition to existing commercial fields and support addenda that update amount with history.
- **FR-002**: IPCs MUST maintain distinct submitted and approved amounts, deductions, final payable, approval status, and collection due date.
- **FR-003**: Recording a collection MUST NOT automatically change IPC approval/workflow status; pay/mark-paid remains a separate action.
- **FR-004**: Multiple partial collections MUST coexist on one IPC without rewriting submitted/approved amounts.
- **FR-005**: System MUST expose overdue and near-due receivables for approved IPCs with remaining receivable &gt; 0.
- **FR-006**: Users MUST be able to trace an IPC through approval to remaining receivable / final collection.
- **FR-007**: Creating an IPC without a project MUST be rejected.

### Key Entities

- **Contract** (+ payment_terms): project-scoped commercial agreement.
- **ChangeOrder (addendum)**: historical amount/condition changes.
- **IPC**: progress statement with submitted/approved amounts, deductions, due date, status.
- **IPCCollection**: partial cash receipt rows.
- **Receivables report row**: derived view of open approved IPCs by due band.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An IPC can be followed from submit → approve → partial collections → remaining zero without losing submitted amount history.
- **SC-002**: In 100% of tested cases, adding a collection does not change status and does not alter submitted/approved amounts.
- **SC-003**: Receivables report includes all approved unpaid past-due IPCs and those due within the configured near-due window.

## Assumptions

- Existing Contract/ChangeOrder/IPC/Deduction/Collection stack is extended, not replaced.
- Near-due window default = 7 calendar days (configurable query param).
- Cash-flow module continues to consume IPC due/collection data; this feature adds a contracts-native report, not a cash-flow redesign.
- “الحاقیه” maps to existing ChangeOrder.
