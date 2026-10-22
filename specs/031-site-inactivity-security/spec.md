# Feature Specification: Site Inactivity Reasons, Conflict Guard, and Daily-Report Access Hardening

**Feature Branch**: `N/A — no before_specify branch hook configured`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Implement the site-closure management cycle: five standard inactivity reasons with conditional mandatory validation, dynamic header UI for closure reasons, inactive-day execution conflict warnings, PDF parity for closure reasons, and hardening of the daily-report by-date creation permission."

**Source References**:
- `reports_gaps/01/speckit-specify-prompts/03-PROMPT-MODULAR-INACTIVITY-SECURITY.md` (PROMPT-03-MODULAR-INACTIVITY-SECURITY)
- `reports_gaps/01/GAP-SPEC-01-DAILY-HEADER-WEATHER.md` (sections US-DR-02, US-DR-03)
- `specs/030-daily-header-weather/spec.md` (adjacent daily-report header feature; site-status rules were explicitly out of scope there and are in scope here)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record a standard inactivity reason when the site is closed (Priority: P1)

An authorized report editor marks the daily report's site status as closed (inactive) and must document the official reason for the shutdown from a fixed, projects-shared vocabulary of five standard inactivity reasons. Reviewers see the same closure reason in the report header, the detailed record, and the official PDF.

**Why this priority**: A closed site without a documented official reason is unexplainable in audits and client claims; the closure reason is what makes the site-status data itself trustworthy.

**Independent Test**: Mark one report inactive without a reason and observe the rejection, enter each of the five reasons in turn and observe acceptance and readback in header, detail, and PDF, then set the report back to active and confirm the reason rule no longer applies.

**Acceptance Scenarios**:

1. **Given** an editor sets the site status to inactive without choosing a closure reason, **When** the report is saved, **Then** saving is rejected with a field-specific validation error carrying the stable error code `inactivity_reason_required`, the error is attached to `inactivity_reason`, and no report row is persisted with an inactive status and empty reason.
2. **Given** an editor sets an inactive site status, **When** the header editing surface is inspected, **Then** the closure-reason selector becomes dynamically visible exactly while the status is inactive and offers exactly the five standard reasons.
3. **Given** each of the five approved reasons is selected for an inactive report, **When** the report is saved and reopened, **Then** the chosen reason is displayed with its localized label in the header editing surface, the read-only detail display, and the official PDF header table.
4. **Given** the report is set back to active, **When** it is saved, **Then** the closure reason is cleared or ignored and saving succeeds without any reason being required.
5. **Given** a report with an active site status, **When** the official PDF is generated, **Then** the header table shows the active status and does not present a closure-reason value as though one exists.

---

### User Story 2 - Guard positive execution volumes on a closed day (Priority: P2)

When the daily report records a closed site, an editor entering or editing an activity row with a positive done quantity in the activities surface is confronted with an explicit double-confirmation warning before the row is accepted. This makes any work recorded against a closed day deliberate, not accidental.

**Why this priority**: It protects the integrity of quantities against a closed status but is a safety UX layer on top of existing functional data entry; it can ship after the closure-reason cycle without blocking MVP.

**Independent Test**: With a report marked inactive, open the activities surface, enter a positive-quantity row, observe the warning and both outcomes (confirm proceeds, cancel aborts), and repeat with a zero-quantity row where no warning appears.

**Acceptance Scenarios**:

1. **Given** the daily report's site status is inactive, **When** an editor creates or edits an activity row whose done quantity is greater than zero, **Then** a warning dialog appears with the localized message «کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت فعالیت اجرایی با حجم مثبت اطمینان دارید؟» before the row is committed.
2. **Given** the same warning dialog is shown, **When** the editor confirms, **Then** the activity row is recorded exactly as entered.
3. **Given** the same warning dialog is shown, **When** the editor cancels, **Then** no row is saved or updated and the editor retains their in-progress entry.
4. **Given** the daily report's site status is inactive, **When** an editor creates or edits an activity row whose done quantity is zero or not supplied, **Then** no warning dialog appears and the row saves as normal.
5. **Given** the daily report's site status is active, **When** any activity row is entered with a positive quantity, **Then** no warning dialog appears.

---

### User Story 3 - Restrict daily-report creation to editors who can edit reports (Priority: P1)

Production of a new daily-report shell must require the same permission as editing daily-report content. Users whose role carries only report-view permission must no longer be able to trigger creation of new daily-report shells; only actual editors may do so. Read access for existing reports is untouched.

**Why this priority**: Authorization is a security boundary; leaving report creation behind a weaker permission than report editing would let observers generate official daily records, so it must be corrected at the same importance level as the core data flow.

**Independent Test**: Call the report-shell creation operation as a view-only member (expect denial) and as an editing member (expect success), without touching any read path.

**Acceptance Scenarios**:

1. **Given** a project member whose effective permissions include viewing but not editing reports, **When** they request creation of a daily-report shell for a new date, **Then** the request is denied with the standard forbidden outcome and no report row is created.
2. **Given** a project member whose effective permissions include editing reports, **When** they request creation of a daily-report shell for a new date, **Then** the shell is created or ensured as before, with no change to the surrounding lifecycle behavior.
3. **Given** any member with report-view permission, **When** they read an existing daily report or fetch an existing report by date, **Then** read behavior is unchanged.

### Edge Cases

- Switching site status active → inactive → active within one editing session must not leave a stale reason on the saved record once inactive is no longer selected.
- A partial update that changes only the site status to inactive must be validated against the record's stored reason when the request does not supply one.
- A partial update that changes only the inactivity reason while the stored status is inactive must itself pass validation; a sole reason change on an otherwise valid record is a normal edit.
- Rows at exactly zero quantity, or blank/not-supplied quantity, never trigger the inactive-day warning; warnings key solely on a strictly positive done quantity.
- Editing an already-saved positive-quantity activity row while the site is inactive must also raise the warning; creation and editing are treated identically.
- The site-status value and, during automatic summary reconciliation, an approved site-status override continue to take precedence over derived per-discipline statuses under existing rules; this feature does not change how the final status is computed, only that a closed final status demands a reason.
- Closure-reason rules apply at every supported write path (create, full update, partial update) so the interactive surface cannot be bypassed to persist an inactive report without a reason.
- A viewer-only member who previously managed to invoke report-shell creation must receive a clear denied outcome, not a silent success or a server error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The daily report MUST support an `inactivity_reason` value drawn from exactly five standard reasons: `weather` (unfavorable weather), `holiday` (official/calendar holiday), `strike_or_dispute` (labor dispute or strike), `client_stop_order` (stop order by the client or the consultant), and `safety_incident` (safety incident).
- **FR-002**: When the daily report's site status is inactive, `inactivity_reason` MUST be filled; saving an inactive report with an empty reason MUST be rejected with the stable error code `inactivity_reason_required` attached to the `inactivity_reason` field.
- **FR-003**: When the daily report's site status is active, `inactivity_reason` MUST NOT be required, and a previously recorded reason MUST be cleared or ignored on save of an active report.
- **FR-004**: In the report header editing surface, the closure-reason selector MUST appear dynamically while the selected site status is inactive and MUST offer exactly the five approved reasons in both Persian and English catalogs.
- **FR-005**: User-facing closure and reason labels and the inactive-day warning message MUST be available in Persian and English, while the stable reason values, field names, and error code remain language-independent.
- **FR-006**: When the daily report's site status is inactive, the official daily-report PDF MUST show both the inactive status and the recorded inactivity reason in the header table, using the same localized label chosen at save time.
- **FR-007**: When the daily report's site status is active, the official PDF MUST show the active status and MUST NOT render a fabricated closure reason.
- **FR-008**: When the daily report's site status is inactive, entering or editing an activity row with a done quantity strictly greater than zero MUST require an explicit confirmation warning before the row is accepted, with the exact localized warning text «کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت فعالیت اجرایی با حجم مثبت اطمینان دارید؟».
- **FR-009**: Confirming the inactive-day warning MUST persist the activity row as entered, and canceling MUST leave the record unchanged with the unsaved entry still in the editor.
- **FR-010**: The inactivity-reason requirement MUST be enforced on every supported create, full-update, and partial-update path so bypassing the interactive header cannot persist an inactive report without a reason.
- **FR-011**: The daily-report shell creation operation behind the existing by-date endpoint MUST be denied to members whose effective permissions lack report-edit permission, and MUST remain available to members who hold it.
- **FR-012**: Reading existing daily reports by date or by identifier MUST continue to work for members with report-view permission without any change in behavior.

### Interface Compatibility Constraints

- Consumers may rely on the stable field name `inactivity_reason`, stable reason values (`weather`, `holiday`, `strike_or_dispute`, `client_stop_order`, `safety_incident`), and the stable error code `inactivity_reason_required`.
- Denial of report-shell creation for a non-editor must present the existing project's standard permission-denied outcome rather than a new error shape.
- The existing comprehensive 24-hour daily-report architecture, the automatic-summary status reconciliation, and the approval/lifecycle behavior remain unchanged except for the closure-reason rules, the warning interaction, and the affected creation permission.

### Key Entities *(include if feature involves data)*

- **Daily Report**: The comprehensive 24-hour project record whose header holds the site status, the optional inactivity reason, and the derived/edited activity rows for the date.
- **Inactivity Reason**: One of five language-independent values with localized Persian and English labels; meaningful only while the recorded site status is inactive.
- **Activity Row**: A per-date activity entry with an execution volume; positive volumes on an inactive day require deliberate confirmation.
- **Project Member Permissions**: The existing effective project-level permissions distinguishing report viewing from report editing, which now gate daily-report shell creation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across a complete closure-reason test matrix, 100% of the five approved reasons are available, accepted, and read back in header, detail, and PDF, and 100% of unknown or retired reason strings are rejected on new saves.
- **SC-002**: 100% of tested inactive-save attempts without a reason are rejected with the code `inactivity_reason_required` attached to `inactivity_reason`, across create, full update, and partial update.
- **SC-003**: In closure-reason testing, every tested report switched back to active saves successfully with its reason requirement lifted, and no stale reason remains on the saved active record.
- **SC-004**: In inactive-day activity testing, 100% of positive-quantity creates and edits trigger the warning; confirming proceeds 100% of the time and canceling saves nothing 100% of the time; zero-quantity and blank-quantity entries never trigger the warning.
- **SC-005**: In permission testing, 100% of shell-creation attempts by view-only members are denied with the standard forbidden outcome, 100% of attempts by editing members succeed as before, and read-by-date behavior for viewers is unchanged.
- **SC-006**: In official PDF verification, 100% of inactive reports display the recorded reason in the header table and 100% of active reports show no fabricated closure-reason text.
- **SC-007**: At least 90% of representative Persian- and English-language editors can mark a site closed, choose a reason, record the closure cycle, and acknowledge or cancel the inactive-day warning on the first attempt without external assistance.

## Assumptions

- The five inactivity reasons form the complete approved vocabulary for this feature; new reasons are out of scope.
- The closure-reason rule applies only to the comprehensive daily-report header; per-discipline specialty reports are not extended with reasons or status rules by this feature.
- During automatic summary reconciliation, an approved project-level site-status override continues to take precedence as today; if the reconciled or overridden final status is inactive, the reason rule applies to the saved summary record.
- The inactive-day warning is an intentional confirmation interaction, not a prohibition: the server continues to accept a confirmed positive-quantity row, and the confirmation is enforced at the interactive surface.
- Existing authentication, project membership, retrieval, PDF generation, and audit behavior remain in force; this feature changes only the closure-reason data, the warning interaction, and the one creation permission.
- Report-shell creation denial uses the project's existing standard forbidden response semantics; no new error contract is introduced for it.
- The reason selector appears in both editable daily-report header surfaces (the report form header and the auto-summary metadata editor) for consistency.
