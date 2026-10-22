# Feature Specification: Daily Site Report Gap Closure

**Feature Branch**: `007-daily-report-gaps`

**Created**: 2026-10-08

**Status**: Draft

**Input**: User description: "Find gaps between application and requirements to fix them — Implementation Spec `07-گزارش روزانه کارگاه.md` (FR-DR)."

**Source**: [07-گزارش روزانه کارگاه.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/07-گزارش%20روزانه%20کارگاه.md) (`FR-DR`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [004-wbs-structure](../004-wbs-structure/spec.md), [005-schedule-baseline](../005-schedule-baseline/spec.md), Implementation Specs 01 / 03 / 04 / 05

## Gap Analysis (current vs FR-DR)

This feature closes **only the unmet** portions of FR-DR. Existing daily-report form tabs, draft→submit→review→approve/reject workflow, offline sync, photos on activities, unique (project, date, shift), Jalali display, and progress recalculation on approval remain in place and are **out of scope** except where a gap explicitly extends them.

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-DR-001 | Header: project, work front/location, Jalali date, shift, preparer, weather | Project, date, shift, weather, preparer exist; location only on activity rows (zone/block/floor) | Report-level **work front / site location** |
| FR-DR-002 | Activity row: WBS/activity, description, qty, unit, location, responsible, attachment | Activity link, description, qty, unit, zone/block/floor, photo; responsible person weak (subcontractor name only) | Explicit **responsible** on activity row |
| FR-DR-003 | Labor by group/contractor: headcount, work hours, **absence** | Job-title headcount grid + work/OT hours; no absence field | **Absence** count (or equivalent) on labor rows |
| FR-DR-004 | Equipment: type/id, work hours, idle, idle reason | Name/ref, productive/idle/repair hours, idle reason | None (regression only) |
| FR-DR-005 | Materials: receipt, consumption, **return**, waste + unit + consumption location | receipt / issue / waste; no return; location via activity only | **Return** transaction type; optional consumption location |
| FR-DR-006 | Incidents / stoppages / site orders / barriers with **owner** and **due date** | Incident type + description + corrective action only | Owner, due date; cover stoppage / site instruction / barrier as reportable site events |
| FR-DR-007 | Statuses: draft, supervisor confirm, PM (or designated) **lock** | draft / submitted / under_review / approved / rejected | Treat **approved = locked**; clarify labels; keep intermediate submit/review |
| FR-DR-008 / SC-DR-003 | Amend locked report only via correction request + retain prior version | Direct edit of approved blocked; **no** correction-request path | Full **correction request** lifecycle + version retention |
| FR-DR-009 | Report date, registration time, approval time separate | `report_date`, `created_at`, `submitted_at`, `approved_at` | None (regression only) |
| FR-DR-010 | Unset ≠ zero for required measured fields | `quantity_measured` on activities only; not consistent elsewhere | Extend unset-vs-zero for material qty and other required measured fields on submit |
| FR-DR-011 / SC-DR-001 | Mobile + desktop entry with attachments | Form + photos + offline sync exist | Regression; ensure header location and new fields usable on narrow viewports |
| SC-DR-002 | Material consumption reconciles with inventory when linked | Material rows can link to project materials; no explicit reconciliation check/view | Light **reconciliation signal** when linked material/inventory data exists |
| SC-DR-004 | Valid ordinary shift report in under 5 minutes | Largely true for current form | Preserve; do not add friction beyond required gaps |
| Edge: no activity rows | Warn or project setting | Submit validation may already require activity | Ensure **warning or block** per project setting (default: warn, allow if weather-only allowed later) |
| Edge: duplicate date/shift | Unique constraint | Exists for project+date+shift | Keep; if work-front becomes multi-report later, uniqueness includes front — **v1 keeps one report per date/shift** |

**Out of scope**: Formal cumulative progress and weekly/monthly reports (08); full warehouse/inventory module beyond daily materials + light reconciliation; concrete/labor-camp tabs (already beyond FR-DR minimum); redesign of Shiraz job-title labor grid into named-person attendance (06); generic workflow engine (15).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete header and activity responsibility (Priority: P1)

As a site engineer, I save a daily report with work front/location on the header, weather, Jalali date, shift, and activity rows that each have WBS/activity, quantity (or explicitly unset), unit, location detail, responsible person, and optional photo—so the report matches the official site-log definition.

**Why this priority**: Closes FR-DR-001 and FR-DR-002 gaps; without header location and row responsible, acceptance scenarios for a complete draft fail.

**Independent Test**: Create a draft with header work front, one activity with responsible and measured quantity, and one activity with quantity explicitly unset; confirm unset is not shown or validated as zero.

**Acceptance Scenarios**:

1. **Given** an active project, **When** a report is saved with project, work front/location, Jalali report date, shift, preparer, and weather, **Then** it is stored as draft and those header fields persist.
2. **Given** the activities section, **When** a row is saved with activity (or WBS-linked activity), description, quantity, unit, location, responsible, and optional attachment, **Then** it is linked to that report.
3. **Given** a required measured quantity left unset, **When** the user submits or the field is validated, **Then** the system treats it as “not recorded” and does not coerce it to zero.

---

### User Story 2 - Correction request for locked reports (Priority: P1)

As a site supervisor or project manager, once a report is approved (locked), nobody can edit it directly. Corrections require a correction request with a reason; the previous approved version is retained and a new editable version proceeds through approval again.

**Why this priority**: FR-DR-008 / SC-DR-003 are the largest compliance gaps; edit-block alone is insufficient without a lawful amend path.

**Independent Test**: Approve a report; attempt direct edit (denied); open correction request with reason; confirm prior version retained and new version is editable/submittable; approve new version.

**Acceptance Scenarios**:

1. **Given** an approved (locked) report, **When** a user attempts a direct field edit, **Then** the change is rejected in 100% of cases.
2. **Given** an approved report, **When** an authorized user opens a correction request with a mandatory reason, **Then** a new version becomes the editable working copy and the previous approved content remains available as history.
3. **Given** a correction version, **When** it is submitted and approved, **Then** it becomes the current locked version and prior versions remain readable (not hard-deleted).
4. **Given** a draft or rejected report (not locked), **When** the author edits it, **Then** no correction request is required (existing behavior retained).

---

### User Story 3 - Materials return, labor absence, and site events with owners (Priority: P2)

As a site supervisor, I record material receipt/consumption/return/waste, labor headcount with hours and absence, equipment idle with reason, and site events (incident, stoppage, site instruction, barrier) with follow-up owner and due date.

**Why this priority**: Closes FR-DR-003, FR-DR-005, FR-DR-006 and supports SC-DR-002 readiness.

**Independent Test**: Add one material return row, one labor row with absence, one equipment idle with reason, and one site event with owner and due date; view them on report detail.

**Acceptance Scenarios**:

1. **Given** the materials section, **When** receipt, consumption, return, or waste is recorded with quantity, unit, and optional consumption location, **Then** each type is distinguishable in the report.
2. **Given** a labor row, **When** headcount, work hours, and absence are entered, **Then** all three persist and absence is not inferred from zero headcount alone.
3. **Given** a site event (incident, stoppage, site instruction, or barrier), **When** description, follow-up owner, and due date are saved, **Then** they appear on the report and are usable for follow-up lists.
4. **Given** linked project materials/inventory data for a consumption row, **When** the user views reconciliation hints, **Then** the system indicates whether recorded consumption is consistent with available inventory signals (or clearly states data insufficient)—without blocking save of the daily report itself.

---

### User Story 4 - Status clarity: supervisor confirm and manager lock (Priority: P2)

As a project manager, I see statuses that match the business language: draft, supervisor-confirmed (submitted/under review), and locked (approved). Approval by the designated role locks the report; timestamps for report date, registration, and approval remain separate.

**Why this priority**: FR-DR-007 / FR-DR-009 alignment; reduces confusion that “approved” is editable or that lock is a separate missing state.

**Independent Test**: Walk draft → submit → (optional review) → approve; confirm UI/API language presents lock semantics; confirm report date ≠ created/approved times; confirm locked report cannot be edited without correction request.

**Acceptance Scenarios**:

1. **Given** a draft report, **When** the supervisor (or designated submitter) confirms/submits, **Then** status moves out of draft and submit time is stored separately from report date.
2. **Given** a submitted/under-review report, **When** the designated approver locks/approves it, **Then** status is locked, approval time is stored, and direct edits are denied.
3. **Given** a locked report, **When** a user views status labels in Persian or English, **Then** wording communicates that the report is locked (not merely “approved and still editable”).

---

### Edge Cases

- Report with no activity rows: system warns on submit; project setting may later require at least one activity—default for this feature is **warn but allow** only if weather and site status are filled; otherwise require at least one activity (match current strict validation if already stricter).
- Duplicate active report for same project + date + shift: rejected with a clear duplicate message (existing uniqueness retained).
- Photo on activity without quantity: allowed as evidence; does not replace technical progress approval (08).
- Correction request while another correction is already in draft for the same report lineage: at most one open (non-locked) correction version at a time.
- Material return exceeding prior receipt on the same report: warn (do not hard-block unless inventory rules later require it).
- Offline sync of a report that became locked on the server: client must not overwrite locked content; conflict/correction path applies.
- Soft-deleted draft reports do not block creating a new report for the same date/shift.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A daily report MUST capture project, work front or site location (header-level), report date (Jalali in UI), shift, preparer, and weather condition.
- **FR-002**: Activity rows MUST support linked schedule activity (hence WBS), description, quantity, unit, location, responsible person, and optional photo/attachment.
- **FR-003**: Labor rows MUST record headcount by group/job title (or contractor grouping as available), work hours, and absence distinctly from headcount.
- **FR-004**: Equipment rows MUST continue to record identity, productive hours, idle/stoppage hours, and idle reason.
- **FR-005**: Material rows MUST support receipt, consumption, return, and waste, each with quantity and unit; consumption location MUST be capturable when relevant.
- **FR-006**: Site events (incident, stoppage, site instruction, barrier) MUST support description, follow-up owner, and due date (plus existing type/corrective notes as applicable).
- **FR-007**: Lifecycle MUST include draft, supervisor confirmation (submit/review), and lock by designated approver; locked means approved and immutable except via correction request.
- **FR-008**: Amending a locked report MUST require a correction request with mandatory reason; the previous locked version MUST be retained; the new version MUST re-enter the approval path before becoming the current locked version.
- **FR-009**: Report date, registration/created time, and approval/lock time MUST remain separate fields.
- **FR-010**: For required measured fields (at least activity quantity and material quantity), “not recorded” MUST be distinguishable from zero; submit validation MUST not treat blank as zero.
- **FR-011**: Users MUST be able to complete the report on mobile-width and desktop layouts with attachments supported.
- **FR-012**: When a material consumption row is linked to project material/inventory data, the product MUST offer a reconciliation indication usable for SC-DR-002 (match / mismatch / insufficient data)—without requiring a full warehouse redesign.
- **FR-013**: Direct edit of locked reports MUST be denied in all cases; only draft and rejected (unlocked) reports remain freely editable by authorized authors.

### Key Entities

- **Daily Site Report**: Header for one project, date, shift (and work front); weather; preparer; lifecycle status; timestamps.
- **Daily Activity Row**: Work performed against a schedule activity; quantity/unit; location; responsible; optional evidence.
- **Daily Labor Row**: Headcount by category/title; work hours; absence.
- **Daily Equipment Row**: Equipment identity and hours including idle with reason.
- **Daily Material Row**: Material movement of type receipt, consumption, return, or waste.
- **Site Event Row**: Incident, stoppage, site instruction, or barrier with owner and due date.
- **Report Correction Request**: Reasoned request to amend a locked report; produces a new version while retaining prior locked versions.
- **Report Version**: Immutable snapshot identity of a locked report content set for history and comparison.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An authorized user can create a draft with header work front, weather, one complete activity row (including responsible), and save successfully on both a narrow (mobile-width) and a wide layout.
- **SC-002**: In 100% of automated checks, direct edit of a locked report is rejected; a correction request with reason is the only path that yields a new editable version while retaining the prior locked version.
- **SC-003**: Material return, labor absence, and a site event with owner + due date are each visible on report detail after save (verified in acceptance tests).
- **SC-004**: For activity and material quantities, blank/unset is never coerced to zero on save or submit in 100% of automated checks.
- **SC-005**: When linked inventory data exists for a consumed material, a reconciliation indication (match, mismatch, or insufficient data) is available to the user without blocking report save.
- **SC-006**: A typical shift report that already has reference data loaded can still be completed in under 5 minutes after these gaps close (no extra mandatory screens beyond the correction path when amending).

## Assumptions

- Existing multi-tab daily report, approval workflow, offline sync, photos, uniqueness of (project, date, shift), and progress recalculation on approval remain the foundation; this feature extends them.
- **Approved = locked** for FR-DR-007; product copy may say “locked” / «قفل‌شده» while the underlying status remains the terminal approved state (plus correction versions).
- One active report per project + date + shift remains the rule in v1; work front is a header attribute, not a second uniqueness key.
- Labor continues to use the job-title headcount grid; named-person attendance and capacity belong to Implementation Spec 06 / feature 006.
- Formal physical-progress measurement methods and weekly/monthly generators belong to Implementation Spec 08.
- Material–inventory reconciliation is advisory for daily-report save; hard stock blocks belong to warehouse/procurement rules if already present elsewhere.
- Correction versions supersede for “current locked” reporting; historical locked versions remain readable for audit.
- Localization (Persian/English) and Jalali display follow existing product rules; stored dates remain sortable standard dates.
- Barriers may already exist as a separate project log; this feature requires site events on the daily report itself (link to a barrier record is optional, not required for acceptance).
