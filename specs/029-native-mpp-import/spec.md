# Feature Specification: Native Microsoft Project MPP Import

**Feature Branch**: `029-native-mpp-import`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "Add native Microsoft Project MPP import to the existing MSP/P6 schedule import wizard so planners can upload `.mpp` directly and continue through the same preview, mode selection, progress, and result flow already available for MSP XML, without requiring Microsoft Project or an external conversion step."

**Depends on**: Existing MSP/P6 schedule import wizard and import-job behavior (WBS + activities + relations + baseline snapshot from import); project permission `edit_wbs`; [004-wbs-structure](../004-wbs-structure/spec.md); [005-schedule-baseline](../005-schedule-baseline/spec.md) (baseline/import notes remain applicable).

## Context (current vs desired)

Today the WBS schedule import wizard is labeled “MSP / P6” but only accepts Microsoft Project XML (`.xml`) and Primavera P6 XER (`.xer`). Native binary Microsoft Project files (`.mpp`) are rejected in the UI with guidance to export XML first. Planners who have an `.mpp` but not Microsoft Project installed cannot complete the import without an external conversion step.

This feature extends the **same** wizard so `.mpp` is a first-class accepted format alongside `.xml` and `.xer`, reusing preview, append/replace confirmation, progress, summary, permissions, project scoping, and audit/import-job traceability.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Import a native MPP through the existing wizard (Priority: P1)

A project planner with permission to edit the project WBS opens the existing MSP/P6 import wizard, uploads a genuine Microsoft Project `.mpp` file, reviews the schedule preview (WBS hierarchy, activities, warnings), chooses append or replace, confirms import, and receives a progress view plus a final success summary (created WBS nodes, activities, relationships, and warnings)—without opening Microsoft Project or converting the file externally.

**Why this priority**: This is the primary user value; without it, native MPP support does not exist.

**Independent Test**: With `edit_wbs` on a project, upload a representative valid `.mpp`, complete preview → confirm → summary, and verify project WBS/activities match the preview intent and no Microsoft Project installation was required.

**Acceptance Scenarios**:

1. **Given** a user with `edit_wbs` on project P and a valid supported `.mpp` schedule file, **When** they open the MSP/P6 import wizard, select the file, request preview, choose append or replace, and confirm import, **Then** they receive a successful summary including created WBS nodes, activities, relationships, and any non-blocking warnings, and the project reflects the imported structure.
2. **Given** an `.mpp` is selected, **When** the system prepares the preview, **Then** a meaningful processing state is shown, duplicate preview/import submissions are prevented while processing, and the selected filename remains visible in the wizard.
3. **Given** preview succeeds, **When** the user has not yet confirmed import, **Then** no permanent WBS, activity, relationship, or baseline changes from that import have been applied to the project.

---

### User Story 2 - MPP and MSP XML equivalence for supported data (Priority: P1)

A controls engineer verifies that the same representative schedule, once as native `.mpp` and once as Microsoft Project XML, yields equivalent supported imported WBS nodes, activities, relationships, and warnings—so switching formats does not silently change the domain model.

**Why this priority**: Trust requires that native MPP does not invent a second mapping model or drift from MSP XML behavior for fields already supported by the importer.

**Independent Test**: Import (or preview-compare) a paired MPP/XML fixture set; assert no unexplained differences in supported hierarchy, task identity/names, dates, durations, progress, milestones, predecessors (type/lag), and critical/slack fields currently supported by the MSP XML importer.

**Acceptance Scenarios**:

1. **Given** a representative schedule available as both `.mpp` and Microsoft Project XML with the same supported content, **When** each is previewed and imported under the same mode, **Then** supported WBS nodes, activities, relationships, and warnings match with no unexplained differences.
2. **Given** an MPP containing nested summary tasks, leaf tasks, milestones, and dependencies, **When** it is previewed and imported, **Then** summary tasks become WBS nodes, leaf tasks and milestones become activities under the appropriate WBS node, and supported hierarchy and schedule fields are preserved when present in the source.

---

### User Story 3 - Clear format guidance and safe rejection of bad files (Priority: P1)

A planner sees accepted formats clearly listed (Microsoft Project `.mpp` and `.xml`; Primavera P6 `.xer`) without needing to understand internal format differences. Invalid, corrupt, password-protected, unreadable (including MPP formats the product cannot process), oversized, truncated, or misleadingly renamed files are rejected with localized, actionable errors and leave no partial project changes.

**Why this priority**: Removing the “export to XML first” forced path must not create silent corruption or ambiguous failures.

**Independent Test**: Attempt preview/import with corrupt bytes renamed to `.mpp`, a password-protected MPP, an oversized file, and a non-MPP file with `.mpp` extension; each fails with a distinct recoverable message and unchanged project schedule data.

**Acceptance Scenarios**:

1. **Given** the import wizard is open, **When** the user views help text and the file picker / drag-and-drop area, **Then** accepted formats are clearly listed as Microsoft Project (`.mpp` and `.xml`) and Primavera P6 (`.xer`), and copy does not require understanding that MPP is internally different from MSP XML.
2. **Given** a corrupt, truncated, or renamed non-MPP file presented as `.mpp`, **When** the user requests preview or import, **Then** the system rejects it before changing project data with a clear localized error distinguishing invalid type vs corrupt/unreadable MPP as appropriate.
3. **Given** a password-protected MPP, **When** the user requests preview or import, **Then** the system rejects it with a specific recovery message (e.g., remove password protection or export unprotected XML) and does not attempt to recover or bypass the password.
4. **Given** a file that is a genuine MPP but cannot be processed (format generation or structure the product cannot read), **When** preview or import is requested, **Then** the user receives a distinct unsupported-version (or equivalent “cannot process this MPP”) error with a recovery path (e.g., open in Microsoft Project and export XML, or use XER), and no project data changes.
5. **Given** a file exceeding the existing upload-size policy, **When** it is submitted, **Then** it is rejected as too large with a localized message and no project mutation.

---

### User Story 4 - Permissions, project isolation, and auditability (Priority: P1)

Only users with project membership and `edit_wbs` can preview or import MPP. Users cannot read or poll another project’s upload, preview, import job, progress, or result. Import attempts and outcomes remain traceable through the project’s existing import-job/audit behavior.

**Why this priority**: Constitution requires server-enforced authorization and tenant/project isolation; schedule imports are destructive when replace is chosen.

**Independent Test**: Deny `edit_wbs` and attempt preview/import (must fail). As a member of project A, attempt to access project B’s import job progress/result (must fail). Confirm successful/failed MPP attempts leave an auditable import-job trail scoped to the project.

**Acceptance Scenarios**:

1. **Given** a project member without `edit_wbs`, **When** they attempt to preview or import an MPP, **Then** the operation is denied and no project schedule data changes.
2. **Given** an import job created for project A, **When** a user authorized only for project B attempts to read or poll that job’s progress or result, **Then** access is denied.
3. **Given** an MPP preview or import attempt (success or failure), **When** auditors review project import history, **Then** the attempt and outcome remain traceable through the existing import-job/audit behavior for that project.

---

### User Story 5 - Append/replace, progress, and failure atomicity (Priority: P2)

MPP imports honor the same append (skip duplicate codes) and replace (remove existing WBS/activities per current safety rules) modes as MSP XML. Progress is reported. Processing failures or timeouts leave no partial imported WBS, activities, relationships, baselines, or import-job side effects that would leave the project in an inconsistent half-imported state; subsequent imports are not blocked.

**Why this priority**: Operational safety for destructive replace and reliability under failure; secondary to basic successful import but required before release.

**Independent Test**: Append with overlapping codes; replace on a project with existing structure; force a mid-processing failure/timeout and assert no partial structures and that a later import can proceed.

**Acceptance Scenarios**:

1. **Given** existing WBS/activities and append mode, **When** an MPP is imported, **Then** existing structures are preserved according to current append behavior (duplicate codes skipped with warnings).
2. **Given** replace mode, **When** an MPP import completes successfully, **Then** replace follows the current dependency and safety rules used by MSP XML import.
3. **Given** a processing failure or timeout during MPP preview preparation or import, **When** the operation ends, **Then** the project has no partial imported WBS/activity/relationship/baseline changes from that failed attempt, the user sees a clear actionable failure (including timeout/internal conversion failure where applicable), and later imports are not blocked.
4. **Given** existing XML and XER acceptance scenarios, **When** they are re-run after MPP support is added, **Then** they continue to pass (backward compatibility).

---

### User Story 6 - Accessible bilingual wizard states (Priority: P3)

Throughout file selection, processing, preview, confirmation, progress, error, and completion, the wizard remains keyboard-accessible and usable in both RTL and LTR layouts. Non-blocking warnings are visually distinct from fatal errors. Fatal errors offer a direct recovery path (select another file, export to XML when appropriate, or retry).

**Why this priority**: Constitution requires bilingual/locale-correct and accessible construction-management UX; polish after core import works.

**Independent Test**: Exercise the full wizard with keyboard only in Persian RTL and English LTR; inject a warning-only preview and a fatal error; confirm distinction and recovery actions.

**Acceptance Scenarios**:

1. **Given** the wizard in any of its states (selection, processing, preview, confirm, progress, error, completion), **When** a user operates with keyboard only in RTL and LTR, **Then** all primary actions remain reachable and usable.
2. **Given** a preview with non-blocking warnings, **When** displayed, **Then** warnings are visually distinct from fatal validation errors.
3. **Given** a fatal validation or processing error, **When** shown, **Then** the user is offered a direct recovery path such as selecting another file, exporting to XML, or retrying when appropriate.

---

### Edge Cases

- Empty or zero-byte “`.mpp`” file → reject as invalid/unreadable before project mutation.
- Extension `.mpp` but content is XML, XER, ZIP, or arbitrary binary → reject based on genuine file validation, not extension or client MIME alone.
- Client-reported MIME disagrees with detected content → trust content validation; do not accept solely on extension/MIME.
- Extremely deep outline hierarchy exceeding project max depth → follow current importer warning/skip behavior; do not invent a new depth model.
- MPP with no summary tasks → follow current MSP XML fallback behavior for mapping (do not change the WBS-vs-activity presentation model).
- Duplicate WBS or activity codes in append mode → skip duplicates with warnings (current behavior).
- Concurrent imports on the same project → existing job/progress semantics apply; a failed/timed-out job must terminate cleanly and not block later imports.
- Temporary uploaded or derived processing artifacts → follow existing retention and cleanup expectations; users must not access another project’s artifacts.
- Locale: all user-facing labels, help, validation, processing errors, and recovery instructions follow the active application locale (Persian/English).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept native Microsoft Project `.mpp` files in the existing MSP/P6 schedule import wizard alongside existing `.xml` and `.xer` formats.
- **FR-002**: Existing MSP XML and P6 XER preview and import behavior MUST remain backward-compatible (no regressions to current acceptance scenarios).
- **FR-003**: MPP import MUST reuse the same user-visible preview and confirmation workflow as MSP XML (preview mandatory before import; append vs replace selection; progress; result summary).
- **FR-004**: Preview and final import MUST interpret the same uploaded file consistently (same file bytes yield consistent supported mapping between preview and commit).
- **FR-005**: When present in the MPP source, the system MUST preserve all schedule information already supported by the existing MSP XML importer, including: task identifiers and names; outline hierarchy and WBS codes; summary-task status; start and finish dates; durations; completion percentages; milestones; predecessor relationships, relationship types, and supported lags; critical-path and slack information currently supported by the importer.
- **FR-006**: Domain mapping MUST remain: Microsoft Project summary tasks → WBS nodes; leaf tasks and milestones → project activities under the appropriate WBS node. Direct MPP support MUST NOT silently change this presentation model.
- **FR-007**: Existing append and replace modes, permission checks (`edit_wbs` + project membership), background progress reporting, result summaries (including created relationships), and project scoping MUST apply to MPP imports the same way they apply to MSP XML.
- **FR-008**: The existing upload-size policy (currently 50 MB for schedule uploads) MUST apply to MPP files; this feature does not introduce a product-level size exception.
- **FR-009**: The system MUST validate that an uploaded file is a genuine, supported Microsoft Project file and MUST NOT trust file extension or client-provided MIME type alone.
- **FR-010**: Corrupt, truncated, password-protected, unsupported-version, misleadingly renamed, or otherwise unreadable files MUST be rejected safely with no partial project WBS, activity, relationship, baseline, or inconsistent import-job mutation.
- **FR-011**: Failed preview or import operations (including processing timeout or internal conversion/processing failure) MUST terminate cleanly, present a clear localized actionable error, leave no partial imported structures, and MUST NOT block later imports.
- **FR-012**: User-facing file labels, help text, validation errors, processing errors, and recovery instructions MUST follow the active application locale.
- **FR-013**: Error messages MUST distinguish at least: invalid file type; corrupt or unreadable MPP; password-protected MPP; unsupported MPP version; file too large; processing timeout or internal conversion failure.
- **FR-014**: Import attempts and outcomes MUST remain traceable through the project’s existing import-job/audit behavior.
- **FR-015**: While an MPP file is being prepared for preview, the UI MUST show a meaningful processing state and prevent duplicate submissions; the selected filename MUST remain visible.
- **FR-016**: Non-blocking import warnings MUST be visually distinct from fatal validation errors; fatal errors MUST provide a direct recovery path (select another file, export to XML when appropriate, or retry).
- **FR-017**: The interface MUST remain keyboard-accessible and usable in both RTL and LTR layouts across file selection, preview, confirmation, progress, error, and completion states.
- **FR-018**: Project membership and `edit_wbs` authorization MUST be enforced server-side for MPP preview and import; users MUST NOT access another project’s uploaded file, preview, import job, progress, or result.
- **FR-019**: Temporary uploaded or derived data MUST follow the project’s existing retention and cleanup expectations.
- **FR-020**: Processing of untrusted project files MUST have bounded time and resource consumption.
- **FR-021**: The product MUST maintain a representative compatibility corpus covering hierarchy, milestones, dependencies, dates, durations, progress values, and malformed files (including corrupt/renamed/protected cases) for ongoing verification.
- **FR-022**: Version policy is best-effort: the system MUST accept any genuine MPP that processing can successfully read. The distinct “unsupported MPP version” (or equivalent cannot-process) error MUST be used only when the file is recognized as an MPP but cannot be processed—not as a fixed published list of Microsoft Project product years. Compatibility verification emphasizes readable vs not-readable fixtures rather than marketing version labels.

### Key Entities

- **Schedule Import Wizard Session**: User-facing flow for selecting a schedule file, viewing preview, choosing append/replace, observing progress, and seeing success or failure—shared across `.mpp`, `.xml`, and `.xer`.
- **Uploaded Schedule File**: Untrusted project-scoped upload identified by name and content; validated as genuine MSP XML, P6 XER, or native MPP before processing.
- **Schedule Preview**: Non-destructive projection of resulting WBS hierarchy, activities, and warnings before any permanent project mutation.
- **Import Mode**: Append (preserve existing; skip duplicate codes with warnings) or Replace (apply current replace safety rules to existing WBS/activities/relations before importing).
- **Import Job**: Project-scoped record of an import attempt with status, progress, filename, mode, result summary (WBS/activity/relationship counts, warnings), and error information for audit/traceability.
- **WBS Node (from summary task)**: Hierarchical work package created from Microsoft Project summary tasks.
- **Activity (from leaf/milestone)**: Schedule activity under a WBS node created from non-summary tasks, including milestones when present.
- **Activity Relationship**: Predecessor link with type and supported lag as currently modeled for MSP imports.
- **Compatibility Fixture**: Curated representative schedule (and paired XML where applicable) used to prove equivalence, coverage, and rejection behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users with `edit_wbs` can complete a normal MPP upload-to-preview flow without Microsoft Project installed and without an external conversion step.
- **SC-002**: At least 95% of representative supported MPP fixtures in the compatibility corpus reach preview successfully.
- **SC-003**: Equivalent MPP and Microsoft Project XML fixtures produce no unexplained differences in supported imported WBS nodes, activities, relationships, and warnings.
- **SC-004**: 100% of invalid, corrupt, password-protected, oversized, and unauthorized test cases fail without partial project mutation.
- **SC-005**: Existing XML and XER acceptance scenarios remain successful after MPP support is introduced.
- **SC-006**: Users always receive either a preview or a clear actionable failure state; the wizard must not remain indefinitely in an ambiguous processing state (bounded processing with terminal success or failure feedback).
- **SC-007**: 100% of cross-project import-job access attempts in the test suite are denied.
- **SC-008**: Keyboard-only completion of the happy path and of a fatal-error recovery path succeeds in both RTL and LTR verification.

## Assumptions

- Native MPP support extends the existing MSP import path’s domain semantics; it does not redefine WBS-vs-activity mapping or invent a parallel schedule model.
- Upload size remains the current schedule-upload policy (50 MB) with no exception for MPP.
- Append and replace semantics for MPP match current MSP XML behavior (including duplicate-code skipping and replace’s removal rules).
- Baseline snapshot creation that already occurs as part of successful MSP import continues to apply to successful MPP imports under the same product rules (imported baselines remain subject to existing lock/approve policies documented for schedule/baseline).
- Password-protected files are never decrypted or bypassed; users must supply an unprotected file or use another accepted format.
- “Supported fields” means the intersection of fields already imported from MSP XML today and fields available in the MPP source—not every Microsoft Project field that exists in the product.
- Temporary processing artifacts follow existing import-job / storage cleanup practices already used for schedule imports.
- P6 XER remains a separate accepted format in the same wizard; this feature does not change XER mapping rules.
- Representative compatibility corpus will be curated during planning/implementation; the specification requires its existence and coverage themes, not a specific file inventory yet.
- Supported MPP “versions” are not a fixed Microsoft Project year list: v1 accepts any genuine MPP the processing path can read; unreadable genuine MPPs surface as unsupported/cannot-process with recovery guidance (clarification Q1 → option C).

## Dependencies

- Existing MSP/P6 import wizard UX and localized messaging.
- Existing project tenancy and `edit_wbs` permission enforcement.
- Existing MSP XML-supported field set and summary→WBS / leaf→activity mapping.
- Existing import-job progress, result summary, and audit/traceability behavior.
- Existing upload validation size policy for schedule files.
- Related specs: 004 (WBS structure), 005 (schedule & baseline gap closure—import/baseline notes).

## Out of Scope

- Editing MPP files inside Velora.
- Exporting projects from Velora to MPP.
- Bidirectional synchronization with Microsoft Project.
- Recovering or bypassing passwords on protected files.
- Changing the existing rule that summary tasks map to WBS nodes and leaf tasks map to activities.
- Redesigning the complete WBS, Activities, or Gantt interfaces.
- Providing a standalone MPP-to-XML download/conversion tool for end users.
- Expanding imported fields beyond what the current MSP XML importer already supports (unless those fields are already supported and merely need to be read from MPP).
- Changing P6 XER domain mapping rules.

## Compatibility Corpus (required themes)

The verification corpus MUST include at least:

1. Nested summary hierarchy with leaf tasks under multiple levels.
2. Milestones and non-zero duration tasks.
3. Predecessor relationships with supported types and lags.
4. Start/finish dates, durations, and completion percentages.
5. Critical / slack fields currently supported by the MSP XML importer (when present).
6. Paired MPP + Microsoft Project XML of the same schedule for equivalence checks.
7. Malformed / rejection set: corrupt/truncated, wrong-content-with-`.mpp`-name, password-protected, oversized, and at least one genuine MPP that processing cannot read (for the unsupported/cannot-process path), emphasizing readable vs not-readable rather than year-labeled version matrices.
