# Feature Specification: Daily Report Correction Lineage and Lossless Cloning

**Feature Branch**: `035-correction-lineage-cloning`

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "پیاده‌سازی نیازمندی‌های مصوب درخواست اصلاح گزارش قفل‌شده، رفع باگ کلونینگ ردیف‌ها، جریان انصراف و غنی‌سازی تاریخچه نسخه‌ها مطابق سناریوهای US-DR-13 سند SPEC-03 و گزارش GAP-SPEC-03"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Lossless Preservation of All Work Details during Correction (Priority: P1)

As a resident engineer or site supervisor, I need opening a correction on an approved daily report to carry over all operational details with complete fidelity, so that editing an approved record never silently loses recorded labor headcounts, contractor allocations, machinery summaries, site visits, general activities, or incident severity data.

**Why this priority**: When a supervisor requests a correction to adjust one entry, silently losing crew names, worker counts, machinery hours, or safety incidents corrupts the legal and operational history of the project and destroys user trust.

**Independent Test**: Can be fully tested by taking an approved report containing every supported child-row category and specific detail fields (crew name, contractor, foreman/worker counts, parcel, machinery summaries, general tasks, official visits, incident severity), opening a correction draft, and verifying that every single active row and field is accurately duplicated in the editable successor.

**Acceptance Scenarios**:

1. **Given** an approved report containing activities with contractor reference, crew name, foreman count, worker count, and parcel location, **When** an authorized user opens a correction request with a valid justification reason, **Then** the newly created draft version contains exact copies of all activity rows with every one of those five attributes intact.
2. **Given** an approved report containing machinery summary rows, general workshop activities, site visits, and incident entries with severity level and source discipline, **When** a correction request is opened, **Then** the new draft version contains identical active copies of all machinery, general activity, visit, and incident records.
3. **Given** an approved report containing soft-deleted child rows from earlier edits, **When** a correction is opened, **Then** only active rows are cloned into the successor version, and previously deleted rows remain absent.

---

### User Story 2 - Safe and Traceable Cancellation of an Open Correction (Priority: P1)

As an authorized report author, I need the ability to safely cancel an unneeded or accidental correction draft directly from the interface, so that the temporary draft is cleanly discarded and the approved predecessor is immediately restored as the current active version without manual administrative intervention.

**Why this priority**: Without a cancellation path, an unintended correction leaves the reporting lineage permanently stuck in a draft state, locking out subsequent workflows or forcing users to submit inaccurate data.

**Independent Test**: Can be fully tested by opening a correction on an approved report, verifying the presence of the cancellation action on the draft, triggering the confirmation dialog, confirming cancellation, and verifying that the temporary draft is deleted and the preceding approved version is restored as current.

**Acceptance Scenarios**:

1. **Given** an active daily report is a correction draft (version number greater than one), **When** an authorized editor views the report form or summary bar, **Then** an explicit "انصراف از اصلاح / Cancel Correction" action is clearly visible with protective visual styling.
2. **Given** an editor clicks the cancellation action, **When** the prompt appears, **Then** a confirmation dialog explains that current uncommitted draft changes will be discarded and the prior approved version will be restored as current, requiring explicit user confirmation before proceeding.
3. **Given** the editor confirms the cancellation, **When** the operation finishes, **Then** the system discards the correction draft, marks the preceding approved report as the current active version, displays a success notification, and navigates the user to the view of the restored approved version.
4. **Given** a daily report is an initial draft (version 1) or is in a locked/approved state, **When** an editor views the report, **Then** the correction cancellation control is not displayed.

---

### User Story 3 - Full Provenance and Clarity in Version Lineage (Priority: P2)

As a project manager or technical auditor, I need to inspect the complete version history of any daily report with clear attribution of who modified each version, why the correction was made, and when it was approved, so that the full governance lifecycle is transparent and auditable.

**Why this priority**: Version numbers alone fail to provide necessary accountability; stakeholders must understand the human context, approval timeline, and justification behind each historical iteration.

**Independent Test**: Can be fully tested by opening the version history panel on a multi-version report lineage, verifying that each historical version displays its modifier's full name, the associated correction reason, its lifecycle status, and its localized approval timestamp.

**Acceptance Scenarios**:

1. **Given** a daily report with one or more approved correction cycles, **When** an authorized user opens the version history panel, **Then** each version entry shows its version number, status badge (current, locked, draft), modifier name, recorded correction reason, and approval timestamp.
2. **Given** a report's initial version (version 1) in the version history, **When** inspected, **Then** its correction reason is presented as unavailable or "ثبت اولیه / Initial submission", never inheriting or displaying a correction reason belonging to a successor version.
3. **Given** a user viewing the version history in Persian locale, **When** approval timestamps are displayed, **Then** the dates and times are formatted in the Persian Jalali calendar.
4. **Given** any historical version in the history list, **When** an authorized user clicks the view action, **Then** they can navigate to inspect the read-only snapshot of that historical version.

---

### User Story 4 - Deterministic Protection against Concurrent Corrections (Priority: P2)

As a project collaborator, I need the system to prevent opening duplicate or conflicting corrections when another correction is already in progress, so that the lineage cannot fork into divergent drafts.

**Why this priority**: Concurrent correction drafts for the same report date create data races and unmergeable discrepancies in project records.

**Independent Test**: Can be fully tested by opening a correction draft on an approved report, attempting to trigger a second correction request on the same lineage, and verifying that the second request is immediately rejected with a distinct client error code and zero duplicate drafts are created.

**Acceptance Scenarios**:

1. **Given** an approved report that already has an open correction draft in progress, **When** any user attempts to open another correction, **Then** the system rejects the request with a standard client error (`correction_already_open`), explains that an open correction already exists, and creates no new record.

---

### Edge Cases

- What happens if the network drops while confirming cancellation? The client displays a connection error, the draft remains intact, and the user can retry safely.
- What happens if a user with read-only/viewer permissions attempts to trigger cancellation? The cancellation button is hidden from their view, and any direct request is denied with an authorization error.
- What happens if a user attempts to cancel a correction belonging to another project? The request is strictly denied under project boundary isolation rules.
- What happens if a report version was created before user attribution was logged? The system gracefully displays an empty or placeholder modifier indicator without crashing or omitting the version row.
- What happens if an approved report has zero child rows in a particular section (e.g., no incidents)? The cloning process succeeds cleanly without error and initializes the section empty in the successor.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST create a new sequential draft version when an authorized user submits a correction request for a current approved report with a justification reason of at least 10 characters.
- **FR-002**: The system MUST copy 100% of active child rows and their domain attributes into the successor draft upon correction, specifically including:
  - Activities: contractor reference, crew name, foreman count, worker count, parcel, zone, block, floor, location detail, quantity, quantity measured flag, and unit.
  - Machinery: machinery type summaries, counts, operating hours, stoppage hours, and stoppage reason codes.
  - General activities: activity descriptions, shifts, and notes.
  - Site visits: visitor names, affiliations, purposes, and arrival/departure notes.
  - Incidents: incident descriptions, severity levels, source disciplines, injured counts, and actions taken.
- **FR-003**: The system MUST NOT clone soft-deleted child rows into the successor draft.
- **FR-004**: The system MUST reject any correction request on a lineage that already contains an active correction draft, returning a client validation error with error code `correction_already_open`.
- **FR-005**: The system MUST provide an explicit "Cancel Correction" action on any draft report whose version number is greater than one.
- **FR-006**: The system MUST require explicit user confirmation before cancelling an open correction, clearly stating that draft modifications will be lost and the prior approved version will be reinstated.
- **FR-007**: Upon confirmed cancellation, the system MUST remove the in-progress correction draft, restore the immediately preceding approved version as the current active version, and navigate the user to the restored approved version.
- **FR-008**: The system MUST NOT render or allow the correction cancellation action on initial draft reports (version 1) or on approved/locked reports.
- **FR-009**: The system MUST provide an accessible version history listing for every daily report, presenting all versions in chronological order with version number, current/locked status, modifier name, version-bound correction reason, and approval timestamp.
- **FR-010**: The system MUST display approval timestamps in the version history formatted in the localized calendar system (Persian Jalali format with date and time in Persian locale).
- **FR-011**: The system MUST associate each correction justification reason strictly with the resulting correction version, ensuring the initial version (version 1) displays no correction reason.
- **FR-012**: The system MUST enforce strict server-side authorization: only users with edit permissions on the specific project can initiate or cancel corrections, and cross-project operations MUST be rejected.

### Key Entities

- **Daily Report**: The primary aggregate representing site operations for a specific project date. Tracks version number, current active status (`is_current`), approval status (`draft`, `submitted`, `under_review`, `approved`, `rejected`), header conditions (weather, work front, site status), and associated child collections.
- **Daily Report Version**: Historical record of an iteration of a daily report. Exposes version number, current status, modifier identity, justification reason (bound to the correction that produced it), and formal approval timestamp.
- **Correction Request**: Domain record representing a request to modify an approved report. Holds reference to the author, the source approved report, the resulting draft report, the justification text, creation timestamp, and cancellation state.
- **Child Collections**: Granular site data linked to a specific report version, including activities, manpower, equipment, materials, machinery summaries, general workshop activities, visits, and incident logs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of active child rows and specialized attributes (contractor, crew, headcounts, parcel, machinery summaries, visits, general tasks, incident severity) are preserved without data loss when generating a correction draft.
- **SC-002**: Zero duplicate correction drafts can be spawned for any report lineage while a correction draft is already open.
- **SC-003**: Authorized users can cancel an unwanted correction draft in 2 interactions (click trigger, confirm dialog) and have the prior approved report restored in under 2 seconds.
- **SC-004**: 100% of historical report versions in the version history view display complete provenance (modifier name, version-bound reason, localized approval timestamp).
- **SC-005**: 100% of unauthorized, read-only, or cross-project correction and cancellation attempts are rejected server-side.

## Assumptions

- Users initiating or cancelling corrections have active project membership with authorized report editing permissions.
- Justification reasons for correction require at least 10 non-whitespace characters to prevent empty or frivolous edits.
- The approval timestamp shown in history corresponds to the official timestamp recorded when the report reached approved status.
- Localized date and time formatting relies on standard application-wide internationalization utilities (Jalali for Persian locale, Gregorian for English locale).
