# Feature Specification: Daily Report Lifecycle Lock

**Feature Branch**: `034-daily-lifecycle-lock`  
**Created**: 2026-10-25  
**Status**: Draft  
**Input**: User description: "Complete the approved daily-report lifecycle, correction, lineage, workflow-error, and unset-versus-zero behavior contracts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preserve an approved report during correction (Priority: P1)

As a workshop supervisor or resident inspector, I need an approved daily report to open a traceable correction version without losing any of its recorded work details, so that a legitimate correction cannot silently damage the historical operational record.

**Why this priority**: Losing crew, workforce, location, contractor, machinery, general-activity, visit, or incident information in a correction version damages the report record and makes a correction unsafe to use.

**Independent Test**: Start a correction from an approved current report that contains each supported child-row type and the listed activity and incident details; confirm that the editable successor contains the same values and is the next version in the same lineage.

**Acceptance Scenarios**:

1. **Given** a current approved report with activity rows containing crew name, foreman count, worker count, parcel, and referenced contractor, **When** an authorized user opens a correction with a valid reason, **Then** the new draft version retains every one of those values.
2. **Given** a current approved report with machinery, general-activity, visit, and incident rows, including incident severity and source discipline, **When** a correction is opened, **Then** every active row and its applicable recorded values are present in the new draft version.
3. **Given** an open correction already exists for a report lineage, **When** a user attempts to open another correction, **Then** no second correction is created and the user receives the standard client error `correction_already_open` with status 400.

---

### User Story 2 - Cancel a correction safely (Priority: P1)

As an authorized report editor, I need to cancel an accidental or no-longer-needed correction request from the daily-report screen, so that the approved record becomes current again without manual intervention.

**Why this priority**: A user who opens a correction currently has no self-service exit and can leave the reporting lineage in an unintended editable state.

**Independent Test**: Open a correction for an approved report, use the visible cancellation flow, confirm the action, and verify that the draft is gone and the prior approved version is current again.

**Acceptance Scenarios**:

1. **Given** the current report is a correction draft with a version number greater than one, **When** an authorized editor views the report, **Then** they can select a clearly labelled “انصراف از اصلاح / لغو درخواست” action and must confirm it before cancellation.
2. **Given** the editor confirms cancellation of an open correction, **When** the cancellation succeeds, **Then** the temporary correction draft is removed, the preceding approved version becomes current again, and the editor is taken to that current approved version.
3. **Given** a report is not an open correction draft, **When** an editor views it, **Then** the cancellation action is not offered.

---

### User Story 3 - Understand version lineage (Priority: P2)

As a project manager or reviewer, I need version history to show who changed a report, why it was corrected, and when it was approved, so that I can assess the record’s lineage without reconstructing it from separate screens.

**Why this priority**: Version number and lock state alone do not provide sufficient accountability for an approved operational record.

**Independent Test**: Create and approve a corrected version, open the version history from either version in the lineage, and verify the listed modifier, correction reason, formal approval time, version number, status, and lock/current markers.

**Acceptance Scenarios**:

1. **Given** a report lineage has one or more corrections, **When** an authorized user requests its version history, **Then** each returned version identifies its number, current and lock state, modifier’s full name, associated correction reason, and formal approval timestamp.
2. **Given** a Persian user opens the expanded version-history view, **When** approval timestamps are present, **Then** they are displayed in a readable Jalali date-and-time format beside the applicable version details.
3. **Given** an original version has no correction request, **When** its history entry is displayed, **Then** its correction reason is presented as unavailable rather than incorrectly copied from a different version.

---

### User Story 4 - Receive precise lifecycle validation (Priority: P1)

As a report author or reviewer, I need invalid workflow actions and incomplete measured quantities to give stable, understandable outcomes, so that I know how to correct the report without mistaking missing work for zero work.

**Why this priority**: Ambiguous validation can permit incorrect workflow handling and make incomplete performance data appear to be an actual zero.

**Independent Test**: Attempt each disallowed submission and rejection input, submit an activity whose measured quantity is missing, submit one explicitly set to zero, and inspect the exact returned code and visible quantity state.

**Acceptance Scenarios**:

1. **Given** a report is neither a draft nor rejected, **When** a user attempts to submit it, **Then** the action is refused with the standard error code `report_not_in_submittable_state`.
2. **Given** a reviewer rejects a report without a reason, **When** they submit the action, **Then** it is refused with `rejection_reason_required`; **given** a non-empty reason shorter than 10 characters, **Then** it is refused with `rejection_reason_min_length_10`.
3. **Given** an activity is marked as measured but its quantity is not set, **When** a user submits the report, **Then** submission is refused with `quantity_unset_invalid` and the exact message «مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود».
4. **Given** an activity’s quantity is unset or marked as not measured, **When** it appears in an editable, read-only, or summary activity table, **Then** it displays a visually distinct muted warning label reading «ثبت‌نشده» instead of zero or a plain dash.
5. **Given** an activity quantity is explicitly zero, **When** it appears in those same tables or the report is submitted, **Then** the numeric zero remains visible and is accepted as a valid recorded value.

### Edge Cases

- A second correction request must not create another draft or change which approved version is current while an earlier correction remains open.
- Cancelling a correction must not delete or alter the preceding approved version, its approval information, or unrelated versions in the lineage.
- A child row marked deleted before correction must not be restored as an active row in the correction draft.
- The absence of a correction reason or approval time for a version that has never been corrected or approved must be represented honestly and must not cause the history view to fail.
- Whitespace-only rejection reasons are treated as missing; a reason containing fewer than 10 characters after trimming is treated as too short.
- A quantity displayed as `0` is never relabelled as «ثبت‌نشده», and an unset quantity is never silently converted to zero.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST create a correction draft only from the permitted current approved report and preserve its lineage identity while assigning the next version number.
- **FR-002**: When creating a correction draft, the system MUST preserve all active activity-row values, including crew name, foreman count, worker count, parcel, and referenced contractor.
- **FR-003**: When creating a correction draft, the system MUST preserve all active machinery, general-activity, and visit rows, plus applicable incident severity and source-discipline values.
- **FR-004**: The system MUST refuse a concurrent correction request with status 400 and the stable error code `correction_already_open`, without creating or changing a report version.
- **FR-005**: The system MUST offer authorized users a confirmed self-service cancellation action only for an open correction draft that is the current report and has a version number greater than one.
- **FR-006**: On a successful correction cancellation, the system MUST remove the temporary draft, restore the preceding approved version as current, and direct the user to that restored version.
- **FR-007**: The system MUST expose every version in a report lineage with version number, status, current state, lock state, modifier full name, correction reason, and formal approval timestamp.
- **FR-008**: The version-history experience MUST show the modifier, correction reason, and a readable Jalali approval date-and-time for each applicable version; absent values MUST be shown without inventing lineage information.
- **FR-009**: The system MUST refuse submission from a state other than draft or rejected with the stable error code `report_not_in_submittable_state`.
- **FR-010**: The system MUST refuse a missing rejection reason with `rejection_reason_required` and a trimmed rejection reason shorter than 10 characters with `rejection_reason_min_length_10`; each outcome MUST provide its corresponding localized user message.
- **FR-011**: The system MUST refuse submission when an activity is marked measured and has no quantity, using `quantity_unset_invalid` and the exact approved message: «مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود».
- **FR-012**: The system MUST treat an explicitly recorded numeric zero as a valid quantity and MUST keep it distinct from an unset or not-measured quantity throughout editing, read-only reporting, and summary views.
- **FR-013**: Every requested activity-table view MUST render an unset or not-measured quantity as the visually distinct muted warning label «ثبت‌نشده», rather than as numeric zero or a plain dash.
- **FR-014**: The delivered behavior MUST have automated coverage for correction-data preservation, concurrent-correction refusal, cancellation restoration, lineage metadata, lifecycle error contracts, measured-but-unset quantity validation, explicit zero acceptance, and the requested unset presentation.

### Key Entities *(include if feature involves data)*

- **Daily report**: A project record with a workflow state, lock state, current-version marker, and report date.
- **Report lineage version**: A numbered member of one daily report’s correction history, retaining approval and modifier information.
- **Correction request**: The formal, reasoned request that creates a temporary editable successor to an approved report and can be cancelled.
- **Activity row**: A recorded work item with quantity state and workforce, crew, location, and contractor context.
- **Associated child row**: A machinery, general-activity, visit, or incident record that belongs to a daily report and must retain its applicable details through correction.
- **Quantity state**: The distinction between an explicit numeric quantity (including zero) and a quantity that is unset or not measured.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In an acceptance dataset containing every listed activity attribute and child-row type, 100% of active records and applicable values are preserved in a newly opened correction version.
- **SC-002**: In 100% of tested cancellation flows, one confirmation returns the user to the preceding approved current version and leaves no temporary correction draft.
- **SC-003**: In 100% of tested invalid submit, reject, concurrent-correction, and measured-but-unset cases, the user receives the specified stable error code; the concurrent-correction response has status 400.
- **SC-004**: In every requested editable, read-only, and summary activity-table state, unset quantities display «ثبت‌نشده» and explicit zero quantities display a numeric zero, with no ambiguous substitution observed in acceptance checks.
- **SC-005**: A reviewer can identify the modifier, correction reason, and approval date for each applicable version from one version-history view, without opening another report screen or consulting a separate audit record.

## Assumptions

- Existing authorization and project-isolation rules continue to govern report viewing, correction, cancellation, and version-history access; this feature does not broaden permissions.
- The existing approval and lock behavior remains the source of truth. Redesigning the already-conforming approval, review, or lock transitions is outside this feature’s scope.
- An active child row means a row that has not been deleted before correction; deleted rows are not resurrected by cloning.
- The correction reason shown for a version is the reason recorded by the correction request that created that version; unavailable lineage data is shown as unavailable rather than inferred.
- The requested visible quantity distinction applies to activity grids and the daily-report activity summary, in both editable and read-only contexts; it does not redefine calculations or replace the existing numeric data model.
- Localized user messages follow the established Persian and English experience while the specified error codes remain language-independent contracts.

## Scope Boundaries

- This feature closes the specified correction integrity, cancellation, lineage metadata, error-contract, and quantity-presentation gaps only.
- It does not introduce a new approval workflow, alter the criteria for final approval, or migrate unrelated report domains.
- It does not change an explicitly recorded zero into an unset value, nor permit an unset measured quantity to be submitted.
