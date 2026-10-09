# Feature Specification: Stakeholders, Documents, Decisions & Workflow

**Feature Branch**: `016-stakeholders-docs-workflow`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: Implementation Spec `15-ذی‌نفعان اسناد تصمیم و گردش‌کار.md` (FR-COL) — keep relational and management data in the same project base: stakeholders, meetings, correspondence, versioned documents, decisions with rationale, and a configurable general workflow engine.

**Source**: [15-ذی‌نفعان اسناد تصمیم و گردش‌کار.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/15-ذی‌نفعان%20اسناد%20تصمیم%20و%20گردش‌کار.md) (`FR-COL`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [003-central-data-model](../003-central-data-model/spec.md), [008-project-registration](../008-project-registration/spec.md)

## Gap Analysis (current vs FR-COL)

Partial collaboration surfaces already exist: project stakeholders (role, influence, interest, communication need), project documents with revision history, correspondence, and meeting minutes with free-text decisions/actions. This feature closes **unmet** FR-COL portions: relationship owner and communication plan, structured meeting actions and open-action reporting, sensitive-contact protection, full document identity/approver/status rules with non-destructive versioning guarantees, first-class management decisions with mandatory rationale and impact links, and a **shared configurable workflow engine** with audit history (instead of one-off approval paths per domain).

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-COL-001 | Stakeholder: person/org, role, influence, interest, communication need, relationship owner, status | Stakeholder exists; no relationship owner | Add owner + complete register fields |
| FR-COL-002 | Influence–interest matrix + communication plan | Influence/interest only; no plan entity | Matrix view + communication plan records |
| FR-COL-003 | Meetings: topic, attendees, agenda, resolutions, actions with owner/due | Minutes exist; actions as free text | Structured actions + open-action report |
| FR-COL-004 | Correspondence: number, date, party, subject, attachment, status, project/contract link | Mostly present; contract link incomplete | Complete fields + contract link |
| FR-COL-005 | Documents: unique id, version, date, author, approver, status; old versions not physically deleted | Documents + revisions; approver/status incomplete | Completeness + non-destructive version guarantee |
| FR-COL-006–007 | Decision with options, criteria, approvers, rationale, impacts, links | No first-class management decision | Decision register with required rationale |
| FR-COL-008–011 | Configurable general workflow + action audit log | Domain-specific approvals only | Shared workflow definitions, instances, history |
| FR-COL-012 | Configurable links to project/contract/WBS | Partial per entity | Consistent optional/required linking rules |
| SC-COL-001–004 | Register collab data; decision with rationale; auditable workflow; versions preserved | Partial | Close remaining gaps |

**In scope**: Stakeholder and communication plan; meeting and action; correspondence; document and version; management decision; workflow definition and running instance; workflow action log.

**Out of scope**: Separate per-domain workflow engines without the shared motor; specialized budget/IPC content (domains 09–11 consume this workflow as clients only); portfolio-level collaboration dashboards.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Stakeholders, meetings, and actions (Priority: P1)

As a project manager, I register stakeholders with role and influence/interest, run a meeting with resolutions, and track open actions with owners and due dates.

**Why this priority**: Stakeholder engagement and action follow-up are the operational backbone of project communication (FR-COL-001–003, SC-COL-001).

**Independent Test**: Create a stakeholder and a meeting with two actions → open-action report lists both overdue/open items with owners.

**Acceptance Scenarios**:

1. **Given** a project, **When** a stakeholder is saved with role, influence, interest, communication need, relationship owner, and status, **Then** it appears in the project stakeholder list.
2. **Given** a meeting with resolutions, **When** an action is recorded with owner and due date, **Then** it appears in the open-actions report while incomplete.
3. **Given** sensitive contact data, **When** a user without permission views the stakeholder, **Then** contact details are hidden or access is denied.

---

### User Story 2 - Versioned documents (Priority: P1)

As a technical office user, I store a document with versions; editing creates a new version and the previous version is not physically deleted.

**Why this priority**: Auditability of drawings/specs depends on immutable prior versions (FR-COL-005, SC-COL-004).

**Independent Test**: Upload version 1 and version 2 → older version leaves general access but remains recoverable for authorized users; physical content of v1 still exists.

**Acceptance Scenarios**:

1. **Given** an existing document, **When** an authorized user revises it, **Then** a new version is created and the previous version is retained.
2. **Given** document search, **When** filters for project, type, date, and status are applied, **Then** results match the filters.
3. **Given** a document record, **When** it is saved, **Then** it has a unique identity, version, date, author, approver (when applicable), and status.

---

### User Story 3 - Decisions with rationale and general workflow (Priority: P1)

As a project manager, I record a decision with options, criteria, approvers, rationale, and impacts; a shared workflow engine manages approve, reject/return, and full history.

**Why this priority**: Auditable decisions and a reusable approval motor are required for governance and for other domains that consume approvals (FR-COL-006–011, SC-COL-002–003).

**Independent Test**: Define a sample “budget change approval” workflow → run one request with reject then approve → complete action log exists.

**Acceptance Scenarios**:

1. **Given** decision entry, **When** save is attempted without rationale, **Then** the save is rejected.
2. **Given** a defined workflow with multiple approvers, **When** one stage rejects, **Then** return/stop follows the definition and history is recorded.
3. **Given** any workflow action, **When** it completes, **Then** user, time, previous status, and new status are in the log.

---

### User Story 4 - Correspondence and communication plan (Priority: P2)

As a project coordinator, I log correspondence and maintain a communication plan (audience, message, type, frequency, owner) supported by an influence–interest view of stakeholders.

**Why this priority**: Completes FR-COL-002 and FR-COL-004; valuable once stakeholders exist, but secondary to versioned docs and the workflow motor for cross-domain value.

**Independent Test**: Create two communication-plan rows and one correspondence linked to the project → both appear in project lists; matrix groups stakeholders by influence/interest.

**Acceptance Scenarios**:

1. **Given** stakeholders with influence and interest, **When** the influence–interest matrix (or equivalent grouping) is opened, **Then** stakeholders are shown by those levels.
2. **Given** a communication plan entry (audience, message, type, frequency, owner), **When** it is saved, **Then** it is listed for the project.
3. **Given** a correspondence record with number, date, party, subject, attachment, and status, **When** it is linked to project and optionally contract, **Then** it is findable under that project (and contract when linked).

---

### Edge Cases

- **Workflow stage without approver**: Definition is incomplete; activation/publishing is blocked.
- **Decision without optional links**: Project link is required; links to risk, activity, or contract are optional.
- **Stage past deadline**: Notify the responsible party and report the stage as overdue.
- **Sensitive contact fields**: Users without the required permission never see full contact data (hide or deny).
- **Document revise without permission**: Revision is rejected; existing versions unchanged.
- **Open action completed**: Leaves the open-actions report (or moves to completed) with completion recorded.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Stakeholder register MUST cover person/organization, role, influence level, interest/impact level, communication need, relationship owner, and status.
- **FR-002**: System MUST support an influence–interest matrix (or equivalent model) and a communication plan (audience, message, type, frequency, owner).
- **FR-003**: Meetings MUST support topic, participants, agenda, resolutions, and actions with owner and due date.
- **FR-004**: Correspondence MUST support number, date, party, subject, attachment, status, and links to project and contract.
- **FR-005**: Documents MUST have unique identity, version, date, author, approver, and status; prior versions MUST NOT be physically deleted on revision.
- **FR-006**: A management decision MUST include subject, options, criteria, proposer, approvers, final decision, execution owner, due date, attachments, impact on schedule/cost/contract/risk, execution status, and **mandatory rationale**.
- **FR-007**: A decision MUST be linkable to project (required) and optionally to risk, activity, or contract.
- **FR-008**: A general workflow engine MUST support workflow type, stages, approver, pass/stop conditions, deadlines, notifications, and status transitions.
- **FR-009**: Workflows MUST be configurable and MUST support concurrent multi-approver or conditional approval patterns.
- **FR-010**: The engine MUST be able to cover sample flows such as: purchase request, IPC approval, payment approval, budget-change approval, schedule-change approval, and inspection approval (as consumers of the shared motor).
- **FR-011**: Every workflow action MUST be logged with user, time, previous action/status, and new action/status.
- **FR-012**: Links of collaboration items to project, contract, and/or WBS MUST be configurable per item type according to domain rules (project required where stated).
- **FR-013**: Users without permission for sensitive contact data MUST NOT see that data (hidden fields or access denied).
- **FR-014**: Document search MUST support filters by project, type, date, and status.
- **FR-015**: Activating a workflow definition that has a stage without an approver MUST be rejected.

### Key Entities

- **Stakeholder & Communication Plan**: Project party with influence/interest and planned communications.
- **Meeting & Action**: Meeting record with resolutions and trackable actions (owner, due, open/closed).
- **Correspondence**: Formal inbound/outbound/internal communication with status and links.
- **Document & Version**: Controlled document identity with immutable prior versions.
- **Management Decision**: Structured decision with mandatory rationale and impact/link fields.
- **Workflow Definition & Running Instance**: Configurable approval path and a live instance of that path.
- **Workflow Action Log**: Auditable history of each transition on an instance.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Authorized users can register stakeholders, meetings, actions, correspondence, versioned documents, and decisions for a project from the product UI without a side spreadsheet as the only path.
- **SC-002**: In 100% of tested cases, saving a decision without rationale is rejected; saving with rationale and an execution owner succeeds.
- **SC-003**: A configured workflow manages approve, reject/return, and history so that an auditor can reconstruct who changed status and when for every tested transition.
- **SC-004**: In 100% of tested revision cases, the previous document version remains physically available after a new version is created.
- **SC-005**: A project manager can create a stakeholder and a meeting with two open actions, then see those actions on the open-actions report, in under 5 minutes on a seeded project.
- **SC-006**: In 100% of tested cases, activating a workflow definition with a stage missing an approver is blocked.

## Assumptions

- Access rules and sensitive-data handling follow core domain principles (spec 002 / implementation spec 01).
- Domains 09–11 and 14 (budget, contracts/IPC, cost/payment, risk/quality) consume this shared workflow for approvals; they do not each implement a separate engine.
- Phase 1 delivery MAY ship stakeholders, meetings/actions, correspondence, and versioned documents before every sample workflow type is wired; the engine and at least one end-to-end sample (e.g. budget-change approval) are still in scope for SC-003.
- Kickoff “key stakeholders summary” (spec 008) remains a charter summary; this feature is the operational stakeholder CRM and communication plan.
- Meeting free-text minutes may be migrated or dual-written into structured actions during planning; structured actions are the system of record for open-action reporting.
- Document “approver” may be a person or role reference consistent with project membership; exact binding is a planning detail.
- Notifications for overdue workflow stages reuse the product’s existing notification capability where available.
- Bilingual (Persian/English) labels and project-scoped authorization follow the project constitution.
- Portfolio collaboration analytics remain out of scope.
