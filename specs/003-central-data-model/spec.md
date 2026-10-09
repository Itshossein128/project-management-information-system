# Feature Specification: Central Data Model

**Feature Branch**: `003-central-data-model`

**Created**: 2026-10-07

**Status**: Draft

**Input**: User description: "Generate Spec Kit specify, plan, and tasks for Velora Implementation Spec `02-مدل داده مرکزی.md` (FR-DATA). Do not implement yet."

**Source**: [02-مدل داده مرکزی.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/02-مدل%20داده%20مرکزی.md) (`FR-DATA`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md) / Implementation Spec 01

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Trace from activity to project and portfolio (Priority: P1)

As a project controls user, I navigate from a daily report or progress entry to its activity, WBS package, and project, and I can roll values up to a portfolio view across projects.

**Why this priority**: FR-DATA-007’s operational chain is the backbone for progress and reporting; without explicit links, drill-down and portfolio aggregation fail.

**Independent Test**: Create one full chain project ← WBS ← activity ← daily report (or progress); from each child open/navigate to its parent; request a portfolio aggregation over at least two projects.

**Acceptance Scenarios**:

1. **Given** an activity linked to a WBS package, **When** the user views activity details, **Then** the related project and WBS package are clearly identified.
2. **Given** multiple projects in the organization, **When** a portfolio report is requested, **Then** aggregation is possible through the defined project-scoped links (not orphaned records).
3. **Given** an approved daily report line tied to an activity, **When** the user drills upward, **Then** they reach project in at most three logical navigation steps.

---

### User Story 2 - Financial transactions with partial collection/payment (Priority: P1)

As a finance user, I record partial receipts or payments as multiple related rows without overwriting the original document amount (e.g., IPC submitted amount stays fixed while collections accumulate).

**Why this priority**: FR-DATA-004/005 and SC-DATA-002 are explicit acceptance bars; current single payment-date patterns fail partial collection.

**Independent Test**: Create an IPC (or equivalent financial document) with a fixed submitted amount; add two partial collection rows; verify original amount unchanged and collections sum separately.

**Acceptance Scenarios**:

1. **Given** a payment certificate with a fixed submitted amount, **When** a partial collection is recorded, **Then** the original amount is unchanged and a new collection row is added.
2. **Given** a financial transaction save, **When** it is persisted, **Then** gross, deductions, net, document date, due date, currency, optional FX rate, WBS and/or CBS code, approval status, and attachment reference can be stored.
3. **Given** two partial collections totaling less than the approved payable, **When** the user views the certificate, **Then** remaining receivable is computable without mutating historical rows.

---

### User Story 3 - Cost classification chain with CBS and commitment (Priority: P1)

As a cost engineer, I classify budget, commitment, actual cost, and payment using both WBS (where work sits) and CBS (what cost type/center), and I keep commitment distinct from actual cost and payment.

**Why this priority**: FR-DATA-007 requires `project ← CBS/WBS ← budget ← commitment ← cost ← payment`; CBS and Commitment are currently missing from the model.

**Independent Test**: Create a CBS node; link a budget line and a commitment to WBS+CBS; post an actual cost and a payment against the commitment; confirm reports show three separate amounts.

**Acceptance Scenarios**:

1. **Given** a project, **When** a user creates a CBS hierarchy node, **Then** it has code, title, optional parent, and cost type, unique within the project.
2. **Given** a commitment, **When** it is saved, **Then** it stores amount, currency, date, counterparty, WBS and/or CBS, payment terms status, and does not equal or overwrite actual cost.
3. **Given** budget, commitment, and actual cost rows, **When** remaining is shown, **Then** commitment and actual are not double-counted as the same measure.

---

### User Story 4 - Managed reference catalogs (Priority: P2)

As a system administrator, I manage units, contract types, statuses, and cost codes from reference tables instead of scattered free-text-only fields on base forms.

**Why this priority**: FR-DATA-003 / SC-DATA-004; free-text-only critical references break reporting consistency.

**Independent Test**: Add a new reference unit (and where missing: contract type / cost code); use it on a new record; confirm the record stores the reference id, not only free text.

**Acceptance Scenarios**:

1. **Given** a new unit in the reference catalog, **When** a user creates an activity or material movement requiring a unit, **Then** they can select that unit from the catalog.
2. **Given** contract type and cost-category/CBS codes as managed references, **When** contracts or budget lines are created, **Then** those fields come from catalogs (free text may remain optional secondary labels only).
3. **Given** organization-wide reference rows (no project_id), **When** listed, **Then** they are available across projects without project filter deletion.

---

### User Story 5 - Organization, OBS, and stakeholder stubs (Priority: P2)

As a PMO admin, I register organization units (OBS) and project stakeholders so projects and communications can link to real parties—not only a free-text employer string.

**Why this priority**: Entity table in FR-DATA lists Organization and Stakeholder; without them, later collab/HR specs cannot attach cleanly.

**Independent Test**: Create an org unit and a stakeholder on a project; link the project’s owning unit and at least one stakeholder; list them back.

**Acceptance Scenarios**:

1. **Given** an organization unit with optional parent, **When** saved, **Then** it is an org-wide record (no required project_id) with status.
2. **Given** a project stakeholder, **When** saved, **Then** person/org name, role, contact, influence, interest, and communication need can be stored and linked to the project.
3. **Given** a project, **When** an owning org unit is set, **Then** the link is explicit and queryable.

---

### Edge Cases

- Organization-wide entities without `project_id` are allowed; project filters must not hide them incorrectly.
- Financial rows in a different currency than the project require an explicit FX rate; silent cross-currency sums are forbidden (reuse core money rules from 002).
- Approved records needing correction use version/reversal only—no hard delete (reuse 01/002 rules).
- Partial collections that exceed approved payable are rejected or warned per finance policy (default: reject over-collection).
- CBS node with children or linked budget/commitment/cost rows cannot be hard-deleted; soft-delete or block applies.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every durable record MUST have a unique identifier and explicit relationships to related entities.
- **FR-002**: Project-scoped records MUST carry a project identifier unless they are intentionally organization-wide reference/org entities.
- **FR-003**: Critical reference data (unit, contract type, status catalogs, cost codes/CBS) MUST be readable from manageable tables.
- **FR-004**: Financial transaction records MUST support gross, deductions, net, document date, due date, payment/collection date(s), currency, optional FX rate, WBS and/or CBS codes, approval status, and attachment reference.
- **FR-005**: Partial receipt/payment MUST be stored as multiple related rows; overwriting the original document amount is forbidden.
- **FR-006**: Physical delete of approved records is forbidden; corrections use version or reversing transactions with reason (aligned with 002).
- **FR-007**: The system MUST support these link chains: project←WBS←activity←daily report/progress; project←contract←IPC←approval←collection; project←CBS/WBS←budget←commitment←actual cost←payment.
- **FR-008**: Portfolio aggregation MUST be possible by summing/joining across projects the user is allowed to see, using the same entity links.
- **FR-009**: CBS MUST exist as a hierarchy distinct from WBS (cost classification vs work breakdown).
- **FR-010**: Commitment MUST be a first-class entity distinct from actual cost and from payment/collection.
- **FR-011**: Organization unit (OBS) and Stakeholder entities MUST be creatable and linkable as specified in Key Entities.
- **FR-012**: Navigation from daily report (or progress) to project MUST be achievable in ≤3 logical steps in product UX.

### Key Entities

- **OrganizationUnit (OBS)**: id, name, parent unit, status; links to users and projects.
- **User/Role** (existing): id, name, unit, roles, access status — extended with optional org unit link if missing.
- **Project** (existing): unique code, name, employer, manager, dates, status, currency, budget ceiling; links to contracts, WBS, budget, reports; optional owning org unit.
- **Contract** (existing): number, party, type, amount, validity, payment terms — type from managed reference where possible.
- **Stakeholder**: person/org, role, contact, influence, interest, communication need; project-scoped.
- **WBS & Activity** (existing): code, title, parent, package, responsible, duration, dates, predecessors.
- **CBS / Cost center**: code, title, parent, cost type; project-scoped hierarchy.
- **Baseline/budget version**: version number, baseline date, status, approver (minimal stub if full versioning deferred to budget spec 09 — must not block CBS/commitment).
- **Operational register** (daily report existing): work date, weather, site, activity, quantity, unit, approval.
- **Resource/person** (existing members/HR minimal): code, skill/type, capacity, cost rate.
- **Purchase request / Commitment / Cost**: number, amount, currency, date, status, evidence, WBS/CBS codes.
- **IPC & Collection**: period, submitted/approved amounts, deductions, due date, partial collection rows.
- **Risk/Issue/Change** (existing risk + barriers): description, cause, impact, probability, owner, action, status.
- **Document/Correspondence/Decision** (existing docs/meetings): type, number, version, date, owner, attachment, status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For each entity in the source FR-DATA table that this feature scopes as in-MVP (OrganizationUnit, Stakeholder, CBS, Commitment, IPC Collection, Payment stub, managed contract-type/cost-code references), a sample record can be created with the listed key fields (≥1 automated create/read test per entity).
- **SC-002**: In 100% of automated partial collection/payment cases, the original document amount is unchanged and related rows are appended.
- **SC-003**: Drill-up from daily report (or progress) to project is possible in ≤3 logical API/UI steps (verified by integration or documented navigation contract).
- **SC-004**: No critical reference (unit, contract type, cost code/CBS) is *only* a mandatory free-text field in the base model for surfaces touched by this feature.
- **SC-005**: Portfolio endpoint or service returns aggregated totals for ≥2 projects without requiring duplicate data entry.

## Assumptions

- Spec 01 / feature 002 shared rules (UUID, soft-delete, currency, audit) are reused; this feature does not re-implement them.
- Full budget versioning UX may remain owned by spec 09; this feature only ensures link fields and a minimal version stub if required for FR-007.
- Payment entity may start as rows linked to commitment and/or IPC collections; a dedicated AP payment register is in scope at least as a minimal model.
- Stakeholder and OrganizationUnit here are data foundations for spec 15; full communication plans/workflows stay out of scope.
- ERP/legal accounting remain out of scope.
- Physical DB indexing strategy is out of scope per source doc; Django models + migrations are the delivery vehicle.
- No application implementation in this Spec Kit pass — specify/plan/tasks only.
