# Feature Specification: Contractor Stakeholder Select

**Feature Branch**: `027-contractor-stakeholder-select`

**Created**: 2026-10-17

**Status**: Draft

**Input**: User description: "Everywhere a field exists to select پیمانکار, it should be a dropdown of current existing contractors. Contractors would be created in stakeholders (ذینفعان) page." (Triggered from department activity record create form contractor field.)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select contractor from stakeholders when logging department activity (Priority: P1)

As a department user logging an activity, I choose پیمانکار from a list of contractors already registered for this project on the stakeholders (ذینفعان) page, instead of typing a free-text name.

**Why this priority**: The reported surface is the department activity create/edit form; consistent contractor identity starts here and prevents spelling drift across activity rows.

**Independent Test**: Register at least one active contractor stakeholder → open department activity create → contractor control shows that name → save with selection → list/detail shows the same contractor.

**Acceptance Scenarios**:

1. **Given** the project has one or more active contractors on ذینفعان, **When** the user opens the department activity create form, **Then** the پیمانکار field is a selection control listing those contractors (not a free-text box).
2. **Given** the user selects a contractor and completes required fields, **When** they save, **Then** the activity record stores that contractor choice and displays the contractor’s name in the activity log.
3. **Given** the project has no contractors yet, **When** the user opens the پیمانکار control, **Then** they see an empty list (or clear empty state) and cannot invent a new contractor name in that field; they must add the contractor on ذینفعان first.

---

### User Story 2 - Register contractors on stakeholders page (Priority: P1)

As a project coordinator, I create and maintain contractors on the ذینفعان page so they appear in every پیمانکار selection elsewhere.

**Why this priority**: Stakeholders are the declared source of truth; without a clear way to register someone as a contractor, selection lists stay empty.

**Independent Test**: On ذینفعان, create a stakeholder marked as contractor → open any in-scope پیمانکار field → that stakeholder appears in the options.

**Acceptance Scenarios**:

1. **Given** a user with permission to manage stakeholders, **When** they add or edit a stakeholder as a contractor for the project, **Then** that party is available in پیمانکار selection lists for the same project.
2. **Given** a contractor stakeholder is set inactive (or removed from active contractor status), **When** a user opens a پیمانکار selection for a new record, **Then** that party no longer appears as a selectable option.
3. **Given** a non-contractor stakeholder exists, **When** a user opens a پیمانکار selection, **Then** that stakeholder does not appear in the contractor options.

---

### User Story 3 - Same contractor list on all پیمانکار selection fields (Priority: P2)

As a project user, wherever the UI asks me to choose پیمانکار for operational records (activity logs, filters, daily report / labor lines that choose a contractor, and similar), I get the same project contractor list sourced from ذینفعان.

**Why this priority**: “Everywhere” consistency prevents parallel free-text pockets; secondary to fixing the primary department activity path and the register itself.

**Independent Test**: With the same contractor set, open each in-scope پیمانکار field → options match (same names/identities for the project).

**Acceptance Scenarios**:

1. **Given** contractors registered on ذینفعان, **When** the user uses any in-scope پیمانکار selection (including department activity filter/search where a contractor is chosen), **Then** options come from that same project contractor set.
2. **Given** a contractor was selected on an existing record, **When** that contractor later becomes inactive, **Then** historical records still show the contractor name that was chosen; new selections cannot pick the inactive contractor.

---

### Edge Cases

- No contractors registered: selection is empty; user is guided that contractors are managed on ذینفعان (no inline free-text create in the پیمانکار field).
- Duplicate or similar names: each option remains a distinct contractor identity so choosing one does not ambiguity-match another.
- Legacy free-text contractor values on existing records: still readable in lists/details; editing such a record requires choosing from the current contractor list (or clearing and re-selecting) rather than keeping an unbound typed string for new saves.
- Soft-deleted or inactive contractors: excluded from new selections; retained for display on historical records.
- Project isolation: contractor options are only from the current project’s ذینفعان, never from another project.
- Import/bulk entry of activities that reference پیمانکار: imported values must resolve to an existing project contractor or fail validation with a clear message (no silent new free-text contractors).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every in-scope UI field labeled پیمانکار (contractor) that is used to choose a contractor for a project operational record MUST present a selection of existing project contractors, not free-text entry of an arbitrary name.
- **FR-002**: The source of contractor options MUST be contractors registered on the project’s stakeholders (ذینفعان) register.
- **FR-003**: Users MUST be able to create and update contractor parties on the ذینفعان page so they appear in پیمانکار selections for that project.
- **FR-004**: پیمانکار selections MUST only include active contractors for the current project.
- **FR-005**: Saving an in-scope record with a پیمانکار value MUST store a durable link to the chosen contractor identity (not only a typed string that can diverge from the register).
- **FR-006**: Display of historical records MUST show the contractor’s name even if the contractor later becomes inactive.
- **FR-007**: Users MUST NOT be able to create a new contractor by typing a novel name into an in-scope پیمانکار field; creation happens on ذینفعان.
- **FR-008**: Non-contractor stakeholders MUST NOT appear in پیمانکار selection lists.
- **FR-009**: In-scope surfaces include at least: department activity create/edit and contractor filter/search; and any other project operational forms/grids that currently offer free-text پیمانکار for choosing a contractor party (e.g. daily report / labor lines labeled پیمانکار). Out of scope: free-text decision-analysis alternatives that merely use “پیمانکار” as sample wording; the separate پیمانکار فرعی (subcontractor performance) register unless it is the same labeled selection field; narrative project-charter text that is not a contractor picker.

### Key Entities

- **Contractor (stakeholder role)**: A project stakeholder recorded on ذینفعان and classified as a contractor; has a display name and active/inactive status; is the only allowed choice for in-scope پیمانکار fields.
- **Stakeholder register (ذینفعان)**: Project-scoped list where contractors (and other stakeholder types) are created and maintained.
- **Operational record with contractor**: Any in-scope activity, filter, or report line that references a contractor via پیمانکار; holds a reference to the chosen contractor identity and displays its name.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a walkthrough of all in-scope پیمانکار fields on a sample project, 100% present a contractor selection from ذینفعان and 0% accept a new free-text contractor name on save.
- **SC-002**: After registering a new contractor on ذینفعان, a user can select that contractor on the department activity form and see it on the saved row within one uninterrupted attempt (no page refresh workaround required beyond normal navigation).
- **SC-003**: Two activity records that select the same contractor always display the same canonical contractor name (no spelling variants for the same identity).
- **SC-004**: When no contractors exist, users attempting to save an activity that requires پیمانکار receive clear feedback that a contractor must be registered on ذینفعان first; they do not successfully save with an invented name.
- **SC-005**: Contractor options from project A never appear when working in project B (verified on at least two projects with different contractor sets).

## Assumptions

- “Contractors” are a subset of project stakeholders on ذینفعان, distinguished by contractor classification (e.g. role/type set to پیمانکار / contractor), not every stakeholder of any role.
- The separate “پیمانکاران فرعی” (subcontractor performance / contracts) area remains its own domain unless a screen uses the same پیمانکار picker pattern for the stakeholder-sourced list; this feature does not merge those registers.
- Project settings / create-wizard “پیمانکار” free text that describes the project’s main contractor party is treated as in-scope if it is a picker for a party; if product intent is a one-line project description only, it may stay free text — default for this spec: align it to the same contractor selection when the label is پیمانکار and the intent is choosing a party.
- Inline “create contractor while filling the form” is out of scope for v1; users navigate to ذینفعان.
- Existing free-text contractor strings on old records remain visible until edited; new saves must use the stakeholder-backed selection.
- Permissions to view/select contractors for operational forms follow existing project membership; creating contractors follows existing ذینفعان manage permissions.
