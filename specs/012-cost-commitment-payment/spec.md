# Feature Specification: Cost Commitment & Payment Gap Closure

**Feature Branch**: `012-cost-commitment-payment`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: Implementation Spec `11-تعهد هزینه و پرداخت.md` (FR-CST) — close gaps versus the current application so the purchase/order-to-commitment cycle, actual cost separate from commitment, duplicate-safe payments, and contract/order remaining balance are fully covered.

**Source**: [11-تعهد هزینه و پرداخت.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/11-تعهد%20هزینه%20و%20پرداخت.md) (`FR-CST`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [003-central-data-model](../003-central-data-model/spec.md), [010-multi-level-budget](../010-multi-level-budget/spec.md) (remaining allocatable / ceiling), [011-contracts-ipc](../011-contracts-ipc/spec.md) (contract as optional origin of order/commitment)

## Gap Analysis (current vs FR-CST)

Much of FR-CST already exists as a cost-control spine (Commitment, ActualCost, Payment, budget remaining by heading) plus a separate procurement requisition workflow and a legacy inventory purchase order. This feature closes **only unmet** portions and the end-to-end join between them.

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-CST-001 | Purchase cycle: request → technical/financial review → approve → order or contract | Requisition multi-stage approvals exist; no explicit financial-review gate; no convert-to-order/contract/commitment; legacy PO disconnected from commitment | Link approved request → order/contract → commitment; financial review in cycle |
| FR-CST-002 | Commitment: amount, currency, date, party, WBS/CBS, payment terms, status | Core fields + WBS/CBS + status exist; **payment terms** missing; party is free-text counterparty | Add payment terms; allow structured party/contract link where applicable |
| FR-CST-003 | Actual cost separate: document, occurrence/register dates, approval status | Separate ActualCost model; optional commitment link; invoice-based document; **no distinct occurrence vs register dates**; **no approval status workflow** | Occurrence + register dates; approval status; document required when project policy says so |
| FR-CST-004 | Payment linked to commitment and/or cost; no duplicate payment for same document | Payment links exist; commitment remaining = amount − posted payments; **no duplicate document_ref guard on payments**; no payment UI | Duplicate-document guard with authorized exception; payment recording in project cost UX |
| FR-CST-005 | Contract/order remaining = approved amount − valid payments | Commitment remaining exists; **contract and purchase-order remaining via same payment ledger not exposed** | Remaining on contract/order from approved amount − valid payments |
| FR-CST-006 | No final cost without project and required classification | Project-scoped; classification not always enforced on final cost save | Hard block final cost without project + required WBS/CBS (or equivalent policy classification) |
| FR-CST-007 | Commitment and actual are two values; no double-count in control reports | Separate models; remaining math may subtract both when they represent the same economic event | Reports and remaining rules treat commitment vs actual without double-counting the same event |
| SC-CST-001 | Heading remaining after commitment and actual | Partial via budgets/remaining | Align with 010 remaining rules + non-double-count |
| SC-CST-002 | 100% of tested cases: duplicate payment without exception not registered | Not enforced on Payment | Guard + exception path |
| SC-CST-003 | Report shows cost, commitment, payment separately, traceable to document | Partial lists; no unified traceable cost–commitment–payment report | Traceable report lines by document |

**Out of scope**: Employer IPC / receivables (10 / `011-contracts-ipc`); inter-project liquidity allocation (12); general ledger / accounting package; redesign of the full procurement warehouse/GRN stack beyond the financial handoff to commitment.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register a financial commitment (Priority: P1)

As purchasing / finance, I register a commitment with amount, currency, date, counterparty (or linked contract/party), WBS/CBS codes, payment terms, and status, tied to a project and budget heading so allocable remaining reflects the commitment.

**Why this priority**: Without a complete commitment record, budget control and downstream cost/payment cannot start (FR-CST-002, SC-CST-001).

**Independent Test**: Create an approved commitment on a project with WBS/CBS and payment terms; observe allocable remaining on that heading decrease conceptually by the committed amount (without inventing a second “actual” line for the same event).

**Acceptance Scenarios**:

1. **Given** an approved budget heading for a project, **When** a valid commitment is finalized/approved, **Then** allocable remaining for that heading is reduced by the commitment in control views.
2. **Given** a commitment missing project or required classification (WBS/CBS per project rules), **When** final registration is attempted, **Then** it is rejected with a clear reason.
3. **Given** an authorized user, **When** they save a commitment with amount, currency, date, party, WBS/CBS, payment terms, and status, **Then** all of those attributes are stored and retrievable.

---

### User Story 2 - Record actual cost separate from commitment (Priority: P1)

As finance, I store actual cost with supporting document, occurrence date, registration date, and approval status as a value distinct from any related commitment so control reports never double-count commitment and actual for the same economic event.

**Why this priority**: Separating committed vs incurred is the core control principle of FR-CST-003 and FR-CST-007.

**Independent Test**: One order/commitment then one actual cost against it; both amounts appear as separate figures; remaining/control math does not add them as if they were independent full consumes of the same spend.

**Acceptance Scenarios**:

1. **Given** an existing commitment, **When** an actual cost is registered against it (or standalone when policy allows), **Then** actual cost is stored as a separate amount and reports show commitment and actual distinctly.
2. **Given** project policy that requires a supporting document, **When** final save is attempted without a document reference, **Then** the system blocks with a blocking warning/error.
3. **Given** no project or required classification, **When** final cost registration is attempted, **Then** it is rejected (FR-CST-006).

---

### User Story 3 - Pay without duplicate documents; see contract/order remaining (Priority: P1)

As finance, I link a payment to a commitment and/or actual cost, prevent a second payment for the same supporting document unless an authorized exception is recorded, and see contract/order remaining as approved amount minus valid payments.

**Why this priority**: Duplicate payments and opaque remaining balances are high-risk finance failures (FR-CST-004, FR-CST-005, SC-CST-002).

**Independent Test**: Post one valid payment for a document; second payment for the same document is warned/rejected unless exception; remaining equals approved − sum of valid payments.

**Acceptance Scenarios**:

1. **Given** a commitment/cost that already has one valid payment for a document, **When** a second payment for the same document is submitted, **Then** the system warns or rejects unless an authorized exception is recorded.
2. **Given** a contract or order with an approved amount and valid payments, **When** remaining is calculated, **Then** it equals approved amount minus the sum of valid payments.
3. **Given** partial multi-installment payments, **When** several payment rows are linked to the same source, **Then** the original document/source amount is preserved and remaining decreases correctly.

---

### User Story 4 - Purchase request to order/contract handoff (Priority: P2)

As purchasing, I move a purchase request through technical and financial review to approval and convert it into an order or contract that can originate a commitment, without leaving a disconnected parallel purchase path.

**Why this priority**: Completes the upstream cycle (FR-CST-001) once commitment/cost/payment core is solid.

**Independent Test**: Approve a request with financial review complete → create order or link contract → create commitment from that origin; origin is traceable on the commitment.

**Acceptance Scenarios**:

1. **Given** a purchase request in review, **When** technical and financial reviews complete and it is approved, **Then** it can be converted to an order or linked to a contract as the origin of a commitment.
2. **Given** an approved request without financial review where the project requires it, **When** conversion to order/commitment is attempted, **Then** it is blocked.

---

### Edge Cases

- **Actual cost without prior commitment**: Allowed when project policy permits; still requires project and required WBS/CBS (or equivalent classification).
- **Partial multi-installment payments**: Multiple payment rows against one source; original source amount unchanged; remaining decreases by each valid payment.
- **Voiding an approved actual cost**: Uses reverse document / versioned correction path consistent with core domain principles (specs 002/003); does not silently rewrite history.
- **Same economic event as both commitment and actual**: Control remaining and reports must not consume the budget twice for that event.
- **Authorized duplicate-document exception**: Second payment for the same document is allowed only when an authorized exception is explicitly recorded with reason and actor.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The purchase/order cycle MUST support request, technical review, financial review, approval, and conversion to an order or contract that can originate a commitment.
- **FR-002**: A commitment MUST capture amount, currency, date, party (or linked counterparty/contract), WBS and/or CBS codes, payment terms, and status, and MUST be project-scoped.
- **FR-003**: Finalizing a commitment without a project or without required classification (WBS/CBS per project rules) MUST be rejected.
- **FR-004**: An approved commitment MUST reduce allocable remaining on the related budget heading in line with multi-level budget rules (feature 010).
- **FR-005**: Actual cost MUST be stored separately from commitment, with supporting document reference, occurrence date, registration date, and approval status.
- **FR-006**: When project policy requires a supporting document, finalizing actual cost without one MUST be blocked.
- **FR-007**: Finalizing actual cost without a project or required classification MUST be rejected.
- **FR-008**: A payment MUST link to a commitment and/or an actual cost and MUST prevent a second valid payment for the same supporting document unless an authorized exception is recorded.
- **FR-009**: Remaining balance for a contract or order MUST equal approved amount minus the sum of valid payments against that contract/order (and its linked commitments as applicable).
- **FR-010**: Commitment and actual cost MUST remain two distinct reportable values; control and remaining calculations MUST NOT double-count the same economic event as both full commitment consume and full actual consume.
- **FR-011**: Users MUST be able to view a cost–commitment–payment report (or equivalent project cost view) that shows the three amounts separately and traces each line to its supporting document where present.
- **FR-012**: Partial installment payments MUST be representable as multiple payment rows without overwriting the original source amount.

### Key Entities

- **Purchase Request**: Upstream demand that passes technical/financial review and can convert to an order or contract origin for commitment.
- **Financial Commitment**: Project-scoped pledged spend (amount, currency, dates, party, WBS/CBS, payment terms, status); consumes allocable remaining when approved.
- **Actual Cost**: Incurred amount with document, occurrence/register dates, and approval status; optionally linked to a commitment; never merely a rename of commitment.
- **Payment**: Cash (or equivalent) outflow linked to commitment and/or actual cost; carries document reference and validity; subject to duplicate-document rules.
- **Contract/Order Remaining**: Derived balance = approved amount − valid payments for that contract or order.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For every tested approved commitment on a budget heading, allocable remaining decreases by the committed amount without inventing a duplicate actual line for that same pledge alone.
- **SC-002**: In 100% of test cases, a second payment for the same supporting document is not registered as valid without an authorized exception.
- **SC-003**: Finance users can open a project cost view/report and see commitment, actual cost, and payment as separate, document-traceable figures for a sample order in under 2 minutes.
- **SC-004**: For every tested contract or order with approved amount and valid payments, displayed remaining equals approved amount minus the sum of those valid payments.
- **SC-005**: In 100% of test cases, finalizing actual cost without project or required classification is rejected.
- **SC-006**: When the same economic event has both a commitment and a matching actual, control remaining does not reduce the heading by the sum of both full amounts (no double-count).

## Assumptions

- Budget ceiling and remaining allocatable semantics come from feature `010-multi-level-budget`; this feature consumes those rules rather than redefining budget versions.
- A contract from feature `011-contracts-ipc` may be the origin of an order/commitment; employer IPC collections remain out of scope here.
- Existing Commitment / ActualCost / Payment records remain the primary financial spine; gaps are closed by extending them and joining the purchase-request cycle, not by inventing a parallel ledger.
- Legacy inventory purchase orders may continue to exist operationally, but new financial handoffs for FR-CST use the commitment spine so remaining and duplicate-payment rules are consistent.
- “Valid payment” means a posted/non-voided payment that counts toward remaining; voided or reversed payments do not.
- Project policy may allow actual cost without a prior commitment; default when unspecified is to allow it if project + classification are present.
- Document identity for duplicate detection is the payment’s supporting document reference within the same project (same document string / identifier).
- Cash-flow module (spec 12) will later consume commitment due dates and planned payments; building that module is out of scope here.
- Bilingual (Persian/English) labels and validation messages follow constitution Principle III; permission checks are project-scoped per Principle I.
