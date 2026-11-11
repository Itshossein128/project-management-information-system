# Feature Specification: Reference Project and Base Data

**Feature Branch**: `051-a7-p1-project-reference`

**Created**: 2026-11-10

**Status**: Draft

**Input**: User description: "A.7-P1 — a reconstructable reference project with identity, roles, base data, a three-level work breakdown, and a lifecycle scenario, plus a versioned schedule-file contract. Audit owners: P01, P02, P03, P04, P05, P06, P07, P09, P10, P11, W01, W02, W03, W05, W06, M01, M02, M03, M04, D01."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register and reopen a real project (Priority: P1)

An authorized project creator records a project with its identity, purpose, scope, deliverables, employer, manager, dates, contract identity, currency, amount, and owning organization unit. The project starts as a draft. A duplicate project code is refused with a clear message and does not leave a partial project. After the record is reopened, every saved field matches what was entered.

**Why this priority**: Later schedule import has no meaning until one real project can be created, stored, and read back.

**Independent Test**: Create one project with every identity field populated, reopen it, and attempt a second project with the same code.

**Acceptance Scenarios**:

1. **Given** an authorized creator, **When** they save a complete project, **Then** it is stored as a draft and the same values are visible when the project is opened again.
2. **Given** a project code that already exists, **When** another project is saved with that code, **Then** the save is refused with an understandable message and no second project is created.
3. **Given** a draft, **When** the creator records the six charter sections (justification, success criteria, constraints, assumptions, key stakeholders, and the manager's authority), **Then** each section is visible again from the project details.

---

### User Story 2 - Move the project through the approved life cycle (Priority: P1)

A person with the current role policy submits a draft, and a different authorized person approves it only when a manager, a scope, and a budget amount are all present. Entering an amount alone does not activate the project. Before approval, and while the project is suspended, binding commitments and a locked baseline cannot be created. Direct edits to approved identity facts (dates, amount, employer, and scope) are refused; an approved change request updates the value, and a rejected or cancelled request leaves it unchanged. Suspension, completion, archive, leaving archive, and undoing completion keep their current role rules, require a reason and a fresh confirmation where the current policy already requires them, do not repeat the effect, and leave documents, financial records, and baselines in place.

**Why this priority**: The reference project must prove the approved life cycle before any imported schedule is treated as approved work.

**Independent Test**: Walk one project from draft through submit, failed approval, successful approval, suspend, resume, complete, archive, and a refused direct edit of a protected field.

**Acceptance Scenarios**:

1. **Given** a draft missing the manager, the scope, and the amount together, **When** approval is attempted, **Then** each missing condition is reported and the project stays unapproved.
2. **Given** a draft or a project waiting for approval, or a suspended project, **When** someone tries to create a binding commitment or lock a baseline, **Then** that path is blocked, and an imported schedule copy is not treated as an approved locked baseline.
3. **Given** an approved protected value, **When** it is edited directly, **Then** the edit is refused; **When** a change request is approved, **Then** the value changes; **When** the request is rejected or cancelled, **Then** the value stays the same.
4. **Given** an archived project that was active, suspended, or completed, **When** an authorized system administrator restores it with a fresh confirmation and a reason, **Then** it returns to that same prior state. A person without that authority, or a stale confirmation, is refused.
5. **Given** a completed restore or status correction, **When** the same action is repeated or the response is interrupted and retried, **Then** a second success is not created, and prior approvals, documents, financial records, and baselines remain.

---

### User Story 3 - Build a three-level work breakdown on the reference project (Priority: P1)

An authorized member builds a manual work breakdown of at least three levels on the reference project. A work package can store a code, title, description, parent, level, responsible person, completion criterion, status, and weights. The package stays distinct from a schedule activity and from a cost classification. A duplicate code, a parent from another project, and moving a node under its own descendant are refused. Moving a node updates the parent, depth, order, and dependent codes. A reusable template can be applied to a new project. Editing that template does not change a project that already received it. Replacing a template on a project that depends on it stays safe.

**Why this priority**: The reference project is the place where work structure is proven before import replaces or merges anything.

**Independent Test**: Create three levels with a responsible person and a completion criterion, then reject a duplicate code, a foreign parent, and a cycle, and show that a template edit does not change the earlier project.

**Acceptance Scenarios**:

1. **Given** the reference project, **When** three nested work packages are saved, **Then** the project, the parent, and the package can all be seen again, including the responsible person and the completion criterion.
2. **Given** an existing code, a parent that belongs to another project, or a move that would place a node under its own child, **When** the save or move is attempted, **Then** it is refused.
3. **Given** a template applied to a project, **When** the template is later edited, **Then** the earlier project keeps the structure it already had.

---

### User Story 4 - Keep organization references governed (Priority: P1)

An organization steward who is allowed to maintain organization references can add an organization unit, a contract type, and a measurement unit, and an authorized project creator can select the new unit and the new contract type while registering a project. A person who is only marked as staff, without the organization-reference role, cannot create an organization unit. A contract type entered on a project must be a current catalog value, or left empty. An existing stored value that is not in the catalog may remain until someone changes it; a new or replacement value that is not in the catalog is refused. Measurement units already in use stay available for selection.

**Why this priority**: The audit found the staff-only expectation and the free-text contract type disagree with the approved access policy and the reference-catalog rule.

**Independent Test**: A staff-only account is refused when creating an organization unit. An allowed steward creates a unit, a contract type, and a measurement unit. A project can select the new unit and contract type, and an unknown contract type is refused.

**Acceptance Scenarios**:

1. **Given** an account that is only marked staff, **When** they try to create an organization unit, **Then** the unit is not created.
2. **Given** an allowed organization steward, **When** they add a unit, a contract type, and a measurement unit, **Then** each appears in the reference lists.
3. **Given** a new project, **When** the creator selects the new owning unit and an active contract type, **Then** both are stored and shown again.
4. **Given** a contract type that is not an active catalog entry, **When** it is newly saved on a project, **Then** the save is refused and the project is not created or not changed.

---

### User Story 5 - Keep project status on the approved life cycle (Priority: P2)

A reader of base data can see that project status is the approved life cycle (draft, waiting for approval, active, suspended, completed, archived), including the rules for who may move between those states. Organization stewards do not add a new project status from a free list. A legacy label kept only so older records can still be read is not a new life-cycle state.

**Why this priority**: The base-data catalog rule and the approved project life cycle disagree if status becomes an open list. The life cycle wins.

**Independent Test**: Confirm the visible status set and that there is no steward action that inserts an arbitrary new project status.

**Acceptance Scenarios**:

1. **Given** the approved life cycle, **When** a project changes status, **Then** it changes only through the existing transition, confirmation, and role rules.
2. **Given** an organization steward, **When** they manage reference catalogs, **Then** they cannot add a project status that has no defined transition.

---

### User Story 6 - Publish the schedule reference contract (Priority: P2)

A reviewer can identify the unchanged employer schedule file by a recorded fingerprint and version, and can read a field-support matrix and control figures whose extraction method does not depend on the product's own import mapping. Small authored examples cover a branch, a milestone, a relationship, and an error case. Historical audit counts are recorded as history, with an identifier and a cause for each known mismatch. They are not treated as approved expected totals, and no relationship is removed or reinterpreted to force the totals to match.

**Why this priority**: Later import work needs an independent contract. This phase does not rewrite import behavior.

**Independent Test**: Compare the employer file fingerprint with the recorded value, and check that each small example states its hand-counted rows, links, and intended warning cause.

**Acceptance Scenarios**:

1. **Given** the employer schedule file, **When** its fingerprint is recorded, **Then** the file bytes are unchanged.
2. **Given** a historical mismatch, **When** it is listed, **Then** it has an identifier and a cause, and it is labeled as historical evidence rather than an approved target count.
3. **Given** the small examples, **When** a later phase compares an importer, **Then** the examples already state which fields and units are in the support contract and which are out of support.

---

### Edge Cases

- A project code that differs only by surrounding spaces is treated as the same code after trimming.
- A blank contract type remains allowed. A legacy contract type already stored may be saved again unchanged. Any different non-catalog value is refused.
- Creating a measurement unit with a blank name, or with the same name as an existing unit ignoring letter case, is refused.
- An organization unit cannot use itself as its parent.
- Repeating archive restore, resume, or completion undo does not create a second effect.
- A dynamic table workbook is not a work-breakdown import. This phase does not add a separate spreadsheet path for the work breakdown.
- The employer schedule file is not edited to make counts match.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: An authorized creator MUST be able to store and reopen a project with identity, purpose, scope, deliverables, employer, manager, dates, contract identity, currency, amount, and owning organization unit. The new project MUST start as a draft.
- **FR-002**: A duplicate project code MUST be refused with an understandable message, and no partial project MUST remain.
- **FR-003**: The six charter sections MUST be stored and shown again from the project details.
- **FR-004**: Submit, reject, and approve MUST follow the current life cycle. Approval MUST require a manager, a scope, and a budget amount, and MUST report each missing item. Entering an amount alone MUST NOT activate the project. Approval MUST record the budget approval mark.
- **FR-005**: Binding commitments and a locked baseline MUST stay blocked in draft, waiting for approval, and suspension. An imported schedule copy MUST remain distinct from an approved locked baseline.
- **FR-006**: Direct edits of protected approved facts MUST be refused. An approved change request MUST change the value. A rejected or cancelled request MUST leave the value unchanged.
- **FR-007**: Suspension, completion, archive, leaving archive, and undoing completion MUST keep the current role policy, event origin, reason, fresh confirmation, single effect, and preservation of documents, financial records, and baselines. This phase MUST NOT invent a parallel archive or undo design.
- **FR-008**: The reference project MUST support a manual work breakdown of at least three levels, with a responsible person and a completion criterion on a work package, distinct from activities and cost classifications.
- **FR-009**: Duplicate work-package codes, parents from another project, and moves that create a cycle MUST be refused. A move MUST update parent, depth, order, and dependent codes.
- **FR-010**: A work-breakdown template MUST be reusable on a new project. Editing the template MUST NOT change a project that already received it. Replacing a template on a dependent project MUST remain safe.
- **FR-011**: Organization units, contract types, and measurement units MUST be maintainable by the current organization-reference stewards and selectable where a project or measurement needs them. Staff status alone MUST NOT grant creation of an organization unit.
- **FR-012**: A project contract type, when newly set or changed, MUST match an active catalog entry or be empty. An unchanged legacy value MAY remain.
- **FR-013**: Project status MUST remain the approved life cycle with its transition rules. Stewards MUST NOT add an arbitrary status that has no transition.
- **FR-014**: Dynamic-table workbooks MUST stay separate from specialized work-breakdown import. This phase does not add a new workbook journey for the reference project.
- **FR-015**: The employer schedule file MUST stay byte-for-byte unchanged, with a recorded fingerprint and version. Small authored examples MUST cover a branch, a milestone, a relationship, and an error, with hand-counted control figures and a field-support matrix for the later import phase. Historical mismatches MUST be identified with a cause and MUST NOT be used as approved target totals.

### Key Entities

- **Reference project**: One reconstructable project with identity, roles, charter, life cycle, owning unit, and contract type.
- **Organization unit**: An organization-wide unit that a project can name as its owner.
- **Contract type**: An organization-wide catalog entry that a project may select.
- **Measurement unit**: An organization-wide unit of measure that authorized stewards can add and that later measurement can select.
- **Work package**: A node in the project's work breakdown, with parent, code, responsible person, and completion criterion.
- **Work-breakdown template**: A reusable structure whose later edits do not rewrite projects that already copied it.
- **Schedule reference file**: The unchanged employer file plus small authored examples and their hand-counted expectations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: One reference project can be rebuilt from the recorded scenario and, when reopened, shows the same identity, owning unit, contract type, charter sections, and three work-breakdown levels.
- **SC-002**: In the reference scenario, a duplicate project code, an unknown new contract type, a staff-only organization-unit create, a duplicate work-package code, a foreign parent, and a cyclic move are each refused, and each refusal leaves the previous data unchanged.
- **SC-003**: The reference life-cycle walk reports the manager, scope, and amount gaps separately, and a repeated restore or status correction does not create a second effect.
- **SC-004**: A reviewer can match the employer file fingerprint to the recorded value and can read a cause for every listed historical mismatch without treating those historical counts as pass/fail targets.
- **SC-005**: An allowed steward can add one measurement unit and see it in the reference list in one sitting. The employer file used for later acceptance remains unmodified.
- **SC-006**: Employer acceptance of this phase is recorded as ready for review until the later delivery review. Unresolved access or interpretation is stated in the handoff rather than marked complete.

## Assumptions

- Approved access policy already decides who may maintain organization references: organization administrators and the business-setup role. The staff marker alone does not. The historical test that expected a staff-only create to succeed is the inconsistent artifact.
- Project status catalogs in the older base-data requirement do not override the approved project life cycle. Manageable catalogs cover organization units, contract types, and measurement units. Project status stays a governed life cycle.
- Existing project registration, charter, change request, archive, undo, and work-breakdown behavior is the baseline. This phase corrects only proven gaps and records the reference contract.
- Dynamic tables are not part of the reference-project journey. Their workbook import stays separate and is not expanded here.
- Replacing an imported work breakdown, rewriting preview, live schedule synchronization, full earned-value or finance work, and any weakening of the access policy are out of scope.
- The 2026-11-10 audit is historical evidence. Its row and link counts are not approved expected values.
- Employer expert sign-off is deferred to the later delivery review. This phase ends as ready for review when its own checks pass.
