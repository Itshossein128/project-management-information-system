# Feature Specification: Project Registration & Kickoff Gap Closure

**Feature Branch**: `008-project-registration`

**Created**: 2026-10-08

**Status**: Draft

**Input**: User description: Implementation Spec `03-ثبت پروژه و آغاز کار.md` (FR-PRJ) — close gaps versus the current application so project create → approval → active lifecycle, kickoff charter, and controlled change of approved fields are fully covered.

**Source**: [03-ثبت پروژه و آغاز کار.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/03-ثبت%20پروژه%20و%20آغاز%20کار.md) (`FR-PRJ`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [003-central-data-model](../003-central-data-model/spec.md), Implementation Specs 01 and 02

## Gap Analysis (current vs FR-PRJ)

This feature closes **only the unmet** portions of FR-PRJ. Existing unique project code, create wizard (name, code, employer, dates, currency, contract amount/type, location, owning unit, project manager), settings edit, portfolio list, and soft-delete/audit principles remain in place and are **out of scope** except where a gap explicitly extends them.

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-PRJ-001 | Create form: unique code, name, purpose, scope, deliverables, employer, PM, dates, contract type/number, currency, initial budget, owning unit, location, status | Code, name, employer, PM, dates, contract type/amount, currency, location, owning unit exist; **purpose, scope description, main deliverables, contract number, initial budget as approved ceiling distinct from raw amount** weak/missing; status not a true lifecycle | Missing core identity fields + status as lifecycle field on create |
| FR-PRJ-002 | Statuses: draft, pending approval, active, suspended, completed/closed, archived | `active`, `suspended`, `completed`, `handed_over` only; default **active** on create | Full lifecycle statuses; create as **draft** |
| FR-PRJ-003 | Status transitions authorized + gated; activate only with PM + scope + budget approved | No pending-approval path; no activation gates | Submit-for-approval + activate with gate checks |
| FR-PRJ-004 | Before approval: no definitive financial commitment or locked schedule baseline from this project | Projects start active; baselines/commitments can be created without FR-PRJ gates | Block definitive baseline / financial commitment creation while draft or pending approval |
| FR-PRJ-005 | Project kickoff / charter: justification, success criteria, constraints, assumptions, key stakeholders summary, PM authority | Absent as a first-class project kickoff record | Kickoff charter entity + view/edit on project |
| FR-PRJ-006 | Change to approved dates, budget ceiling, employer, or scope via change request only | Settings allow direct edit of employer, dates, amounts | Project change-request path; block direct edit of locked approved fields when active |
| FR-PRJ-007 | Project code unique in system | Unique constraint exists | Regression only |
| SC-PRJ-001 | Authorized user can create and submit for approval | Create exists; submit-for-approval does not | Submit draft → pending approval |
| SC-PRJ-002 | 100% of tested cases: cannot activate without PM / scope / approved budget | No gate | Enforce gates |
| SC-PRJ-003 | 0% success changing approved fields without change request | Direct PATCH succeeds | Enforce change-request-only for protected fields |

**Out of scope**: WBS detail (04), schedule/baseline detail beyond the “no definitive baseline while unapproved” rule (05), line-item budget (09), full contract module (10), full stakeholder CRM beyond kickoff summary (15), portfolio analytics beyond listing projects by status.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create draft and submit for approval (Priority: P1)

As an authorized user, I create a project with the required identity fields and save it as **draft**. When ready, I submit it for approval. The project must not become **active** while manager, scope, or approved budget are missing.

**Why this priority**: Closes FR-PRJ-001–003 and SC-PRJ-001–002; without draft/approval and activation gates, every other control assumes an uncontrolled “already active” project.

**Independent Test**: Create a draft with code and name; attempt activate without PM/scope/budget → blocked with clear missing conditions; complete gates and approve → active.

**Acceptance Scenarios**:

1. **Given** an authorized user, **When** they complete create with unique code, name, purpose, scope description, main deliverables, employer, project manager (optional at draft), start/end dates, contract type and number, currency, initial budget, owning unit, location, **Then** the project is stored as **draft** (not active by default).
2. **Given** a draft missing project manager, scope description, or approved initial budget, **When** activation (or approve-to-active) is requested, **Then** the system blocks the transition and lists the missing conditions.
3. **Given** a complete draft submitted for approval and approved by an authorized approver with all activation gates satisfied, **When** the status becomes active, **Then** the project is usable for downstream planning under existing modules.
4. **Given** a draft or pending-approval project, **When** a user attempts to create a definitive locked schedule baseline or a binding financial commitment attributed to that project, **Then** the system rejects it (FR-PRJ-004).

---

### User Story 2 - Project kickoff charter (Priority: P2)

As a project manager, I record a kickoff / charter sheet with justification, success criteria, constraints, assumptions, key stakeholders (summary), and PM authority, and I can view it from project details.

**Why this priority**: FR-PRJ-005; charter documents why the project exists and what success means before heavy planning.

**Independent Test**: Save a charter on an existing project; reopen project details and confirm all charter fields persist and display.

**Acceptance Scenarios**:

1. **Given** a project the user can edit, **When** they save kickoff fields (justification, success criteria, constraints, assumptions, key stakeholders summary, PM authority), **Then** the charter is stored and visible on project detail.
2. **Given** a charter already saved, **When** an authorized user updates it before archival rules say otherwise, **Then** the updated values persist (version history of charter is not required in v1).

---

### User Story 3 - Controlled change of approved fields (Priority: P1)

As a project manager on an **active** project, I cannot silently change approved dates, budget ceiling, employer, or scope. I must open a project change request with a reason and follow an approval path; only after approval do the protected fields update.

**Why this priority**: FR-PRJ-006 / SC-PRJ-003; protects contractual baseline of the project record itself (distinct from schedule change requests in 05).

**Independent Test**: On an active project with approved budget/scope, attempt direct edit of budget ceiling → rejected or redirected; create change request with reason → approve → field updates; prior values remain auditable via the change request record.

**Acceptance Scenarios**:

1. **Given** an active project with approved identity fields, **When** a user tries to directly change approved start/finish dates, budget ceiling, employer, or scope description, **Then** the change is rejected (or the UI only offers “request change”) and no silent overwrite occurs.
2. **Given** an authorized requester, **When** they create a project change request naming the field(s), proposed value(s), and reason, **Then** a pending change request is recorded with approval path.
3. **Given** a submitted change request, **When** an authorized approver approves it, **Then** the protected field(s) update to the approved values and the request is marked approved with decision metadata.
4. **Given** a rejected or cancelled change request, **When** viewing the project, **Then** protected fields remain unchanged.

---

### User Story 4 - Lifecycle statuses and archive rules (Priority: P2)

As a portfolio or system administrator, I move projects through suspended, completed/closed, and archived statuses with clear rules: suspended projects do not receive new definitive locked baselines; archived projects are view-only except for a system administrator role.

**Why this priority**: Completes FR-PRJ-002 edge behavior and operational control after go-live.

**Independent Test**: Suspend an active project → attempt new locked baseline → blocked; archive → non-admin edit blocked; admin can still view.

**Acceptance Scenarios**:

1. **Given** an active project, **When** an authorized user sets status to suspended, **Then** creating a new definitive locked schedule baseline is blocked until suspension is lifted (new binding commitments follow the same conservative rule unless a separate policy later relaxes commitments only).
2. **Given** an archived project, **When** a non–system-admin user attempts to edit project fields or charter, **Then** the action is rejected; view remains allowed for authorized members.
3. **Given** duplicate project code on create, **When** save is attempted, **Then** the system rejects with a clear uniqueness message (FR-PRJ-007).

---

### Edge Cases

- Duplicate project code → reject with clear message; no partial create.
- Incomplete draft submitted for approval → either allow pending approval but still block activate, or require minimum fields before submit; **default**: allow submit to pending approval with warnings, but activation always hard-gated on PM + scope + approved budget.
- Suspended project → no new definitive locked baseline; existing historical locked baselines remain readable.
- Archived → view-only except system administrator.
- Concurrent change requests on the same protected field → at most one open (draft/submitted) change request per protected field group at a time; second open attempt is rejected with a clear conflict message.
- Changing status backward (e.g. active → draft) → not allowed; corrections use change request or admin-controlled reopen to suspended/active only as defined in transitions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept project create/update identity fields: unique code, name, purpose, scope description, main deliverables, employer, project manager, start and finish dates, contract type, contract number, currency, initial budget (ceiling), owning unit, execution location, and lifecycle status.
- **FR-002**: Project lifecycle statuses MUST include at least: draft, pending approval, active, suspended, completed (closed), archived. Legacy labels such as handed_over MAY map to completed or remain as a synonym presentation only if documented; new work MUST use the FR-PRJ set.
- **FR-003**: Status transitions MUST be permission-checked. Transition to **active** MUST require: project manager assigned, non-empty scope description, and initial budget marked approved (or equivalent explicit budget-approval step).
- **FR-004**: While status is draft or pending approval, the system MUST NOT allow creation of a definitive locked schedule baseline or a binding financial commitment for that project.
- **FR-005**: System MUST support a project kickoff/charter record with justification, success criteria, constraints, assumptions, key stakeholders summary, and project manager authority.
- **FR-006**: After a project is active (approved identity in force), changes to approved start/finish dates, budget ceiling, employer, or scope description MUST go through a project change request with reason and approval; direct mutation of those fields MUST fail.
- **FR-007**: Project code MUST remain unique across the system; duplicate create/update MUST fail with a clear message.
- **FR-008**: Authorized users MUST be able to submit a draft for approval and authorized approvers MUST be able to approve or reject that submission.
- **FR-009**: Archived projects MUST be read-only for non–system-admin users.
- **FR-010**: Suspended projects MUST block new definitive locked schedule baselines until the project returns to active (or an explicitly allowed non-suspended operational status).

### Key Entities

- **Project**: Root project record with lifecycle status, identity fields, currency, and budget ceiling.
- **Project Kickoff Charter**: Start document attached to a project (justification, success criteria, constraints, assumptions, key stakeholders summary, PM authority).
- **Project Change Request**: Request to change one or more protected approved fields, with reason, proposed values, requester, decision status, and decision metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An authorized user can create a draft project and submit it for approval without the project becoming active until gates pass.
- **SC-002**: In 100% of tested activation attempts, a project missing project manager, scope description, or approved budget is blocked from becoming active, with the missing condition(s) shown.
- **SC-003**: Direct edits to protected approved fields (dates, budget ceiling, employer, scope) succeed in 0% of tested cases on active projects; approved change requests update those fields in 100% of tested approval paths.
- **SC-004**: A project manager can save and reopen a kickoff charter and see all required charter fields within one project-detail visit.
- **SC-005**: Duplicate project codes are rejected in 100% of tested create attempts with a user-understandable message.
- **SC-006**: Suspended and archived rules (no new locked baseline; archive read-only for non-admin) hold in 100% of tested attempts.

## Assumptions

- “Approved budget” for activation means the initial budget ceiling is present and an explicit approval action (submit + approve, or a dedicated budget-approved flag set during approval) has occurred—not merely that a number was typed on the draft form.
- Kickoff “key stakeholders” may be free-text summary; structured stakeholder registry remains under Implementation Spec 15 / central data stakeholders already delivered elsewhere.
- Project change requests are distinct from schedule change requests (FR-SCH); approving a project field change does not by itself create a new schedule baseline.
- Detailed WBS, activity schedules, and line-item budgets remain in specs 04 / 05 / 09.
- Contract commercial detail beyond type/number on the project record remains in Implementation Spec 10.
- Existing projects that are already `active` remain active; migration maps unknown statuses into the nearest FR-PRJ status without auto-creating charters or change requests.
- Bilingual labels (fa/en) are required for new statuses and validation messages per constitution.
- Permissions reuse project-scoped authorization (create/edit/approve project) rather than inventing a parallel security model.
