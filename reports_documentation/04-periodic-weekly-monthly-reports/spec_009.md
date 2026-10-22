# Feature Specification: Physical Progress & Periodic Reports Gap Closure

**Feature Branch**: `009-progress-periodic-reports`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: "Implementation Spec `08-پیشرفت فیزیکی و گزارش‌های دوره‌ای.md` (FR-PRG) — physical progress measurement methods, four-way progress display, and weekly/monthly reports from approved records."

**Source**: [08-پیشرفت فیزیکی و گزارش‌های دوره‌ای.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/08-پیشرفت%20فیزیکی%20و%20گزارش‌های%20دوره‌ای.md) (`FR-PRG`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [004-wbs-structure](../004-wbs-structure/spec.md), [005-schedule-baseline](../005-schedule-baseline/spec.md), [007-daily-report-gaps](../007-daily-report-gaps/spec.md), Implementation Specs 01 / 04 / 05 / 07

## Gap Analysis (current vs FR-PRG)

This feature closes **only the unmet** portions of FR-PRG. Existing Sprint 6 progress dashboard, S-curve, weighted rollup, progress history from approved daily reports, and manual progress entry remain in place and are **out of scope** except where a gap explicitly extends them.

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-PRG-001 | Measurement method per activity: quantity-based, weighted milestones, or evidence-backed % | Implicit quantity path only (daily measured qty / total qty) | Selectable measurement method on activity/package |
| FR-PRG-002 | Total qty, unit, weights approved before reporting | Fields exist; no approval gate | Gate: approved totals/units/weights required before progress reporting for that method |
| FR-PRG-003 | Reject % > 100 unless approved quantity change | Manual/recalc **clamp** to 100% | **Reject** over-100% unless linked approved quantity change; no silent clamp as success |
| FR-PRG-004 | Period, cumulative, planned, approved shown separately | Planned vs actual (cumulative-ish); no period; no distinct approved | Four labeled values: period / cumulative / planned / approved |
| FR-PRG-005 | Photo alone ≠ technical approval | Photos on daily activity rows | Approved progress requires technical approval; photo is evidence only |
| FR-PRG-006 | Progress linked to WBS + measurement method | Linked to WBS via activity; method not recorded | Persist method on progress records; keep WBS link |
| FR-PRG-007 | Weekly project report from dailies + critical + lookahead + barriers + decisions | Schedule-status / alerts / dailies exist separately; no project weekly report | Generate weekly project report from approved sources |
| FR-PRG-008 | Monthly report: progress, baseline variance, cost, commitments, IPC, risks, next-month forecast | Domain pieces exist in other modules | Compose monthly project report; missing sections show “not recorded” |
| FR-PRG-009 | Auto reports show source + last updated per figure | Partial on progress history | Provenance on every weekly/monthly figure |
| FR-PRG-010 | No silent edit of final report output | N/A (no editable auto report yet) | Block or audit-trail any override of generated figures |
| FR-PRG-011 | Measurement method change needs version + approval | Absent | Versioned method change with approval |
| SC-PRG-001 | Progress value tied to WBS + method | Partial (WBS only) | Method binding |
| SC-PRG-002 | Weekly/monthly from approved records | Missing | Generators |
| SC-PRG-003 | 100% of tested cases: >100% without approved change rejected | Clamp instead | Reject semantics |
| SC-PRG-004 | One step from report figure to source + approval status | Partial | Provenance navigation on period reports |

**Out of scope**: Full EVM calculations (spec 13); portfolio dashboard (16); redesign of S-curve charting intervals as “weekly/monthly reports”; legacy department/inventory weekly PDF; live ERP/P6 sync.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record progress with an approved measurement method (Priority: P1)

As a project controls engineer, I choose a measurement method for each activity (quantity-based, weighted milestones, or evidence-backed percent), ensure totals/units/weights are approved, and record progress with evidence so percent is computed by that method and stays linked to WBS.

**Why this priority**: FR-PRG-001 / 002 / 006 / SC-PRG-001; without method and approved basis, progress numbers are not auditable.

**Independent Test**: Define total quantity and quantity-based method; record period progress; see cumulative update; confirm WBS link and method on the record.

**Acceptance Scenarios**:

1. **Given** an activity with quantity-based method and approved total quantity/unit, **When** executed quantity for a period is recorded, **Then** percent is calculated by that method and the progress value is linked to the activity’s WBS package and method.
2. **Given** percent would exceed 100% without an approved quantity change, **When** the user saves, **Then** the system rejects the save (does not silently cap as success).
3. **Given** only a photo is attached without technical approval, **When** approved progress is requested or shown, **Then** the photo alone does not count as technical approval or as approved progress.
4. **Given** weighted-milestone method with incomplete milestone weights, **When** reporting is attempted, **Then** reporting is blocked or clearly warned as incomplete data (no silent zeros).
5. **Given** quantity-based method but no approved total quantity, **When** the user tries to use that method for reporting, **Then** the method is unavailable until total quantity is completed and approved.

---

### User Story 2 - See period, cumulative, planned, and approved progress separately (Priority: P1)

As a project manager, I open the progress view and see period (this interval), cumulative, planned, and approved progress as four distinct, clearly labeled values—never conflating unapproved recorded progress with approved progress.

**Why this priority**: FR-PRG-004; managers currently cannot tell period vs approved vs planned at a glance.

**Independent Test**: Open progress for an activity that has period actual and planned values; assert four distinct labeled fields; assert unapproved recorded ≠ approved.

**Acceptance Scenarios**:

1. **Given** an activity with period progress and planned progress, **When** the progress page is opened, **Then** period, cumulative, planned, and approved values appear separately with clear labels.
2. **Given** progress that is recorded but not technically approved, **When** the user looks at the approved value, **Then** it is not treated as equal to the period/recorded value.

---

### User Story 3 - Generate weekly and monthly project reports from approved records (Priority: P2)

As a project manager, I generate a weekly report from approved daily data (critical activities, next-week plan, barriers, decisions needed) and a monthly report summarizing progress, baseline variance, cost, commitments, payment certificates, key risks, and next-month forecast—each figure showing its source and last update time, with no silent hand-edit of final figures.

**Why this priority**: FR-PRG-007–010 / SC-PRG-002 / SC-PRG-004; closes the periodic-reporting half of FR-PRG without inventing EVM (13).

**Independent Test**: With approved dailies present, generate weekly report and open one figure’s source; attempt to change a final figure without audit and confirm block or history; generate monthly with a missing cost section showing “not recorded.”

**Acceptance Scenarios**:

1. **Given** approved daily reports for the week, **When** a weekly project report is generated, **Then** it includes critical-activity status, next-week plan, barriers/obstacles, and decisions required.
2. **Given** a generated report figure, **When** the user follows source / last-updated, **Then** they reach the underlying approved record and approval status in one step.
3. **Given** an attempt to change a final output number without leaving a trail, **When** save is attempted, **Then** the system blocks it or records the change in history (no silent overwrite).
4. **Given** monthly generation when cost (or another optional section) has no data, **When** the monthly report is shown, **Then** that section shows “not recorded” (or equivalent) rather than a misleading zero.
5. **Given** approved baseline and current progress data, **When** a monthly report is generated, **Then** it summarizes progress and baseline variance, and includes cost, commitments, payment certificates, key risks, and next-month forecast when those domains have data (otherwise “not recorded”).

---

### User Story 4 - Change measurement method with version and approval (Priority: P2)

As a project controls engineer, when I change an activity’s measurement method, the change is versioned and requires approval so historical progress remains interpretable under the method that produced it.

**Why this priority**: FR-PRG-011; method switches without versioning break auditability of prior percents.

**Independent Test**: Change method on an activity with existing progress; confirm prior records retain prior method version; new method applies only after approval.

**Acceptance Scenarios**:

1. **Given** an activity with an approved measurement method and existing progress, **When** a method change is submitted, **Then** it creates a new version pending approval and does not rewrite historical progress methods.
2. **Given** a pending method change, **When** it is approved by an authorized role, **Then** new progress uses the new method; prior cumulative history remains tied to the prior method version.
3. **Given** a rejected or draft method change, **When** progress is recorded, **Then** the currently approved method remains in force.

---

### Edge Cases

- Incomplete milestone weights → block reporting or show incomplete-data warning (never invent 100%).
- Activity without total quantity → quantity-based method disabled until total is set and approved.
- Missing cost/commitment/IPC/risk data on monthly → section labeled “not recorded,” not zero.
- Photo without technical approval → not treated as approved progress.
- Progress % > 100 without approved quantity change → rejected.
- Legacy department weekly PDF → must not be confused with or replace the project weekly report.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to select a measurement method per activity (or designated work package): quantity-based, weighted milestones, or evidence-backed percent.
- **FR-002**: Total quantity, unit, and weights for the chosen method MUST be approved before progress reporting is allowed for that activity under that method.
- **FR-003**: Progress percent greater than 100 MUST be rejected unless the activity has an approved quantity (or basis) change that permits it.
- **FR-004**: Period, cumulative, planned, and approved progress MUST be displayed as four separate, clearly labeled values.
- **FR-005**: A photo MUST NOT by itself substitute for technical approval of progress.
- **FR-006**: Each progress value MUST remain linked to its WBS package and measurement method (including method version when changed).
- **FR-007**: The system MUST generate a weekly project report from approved daily data covering critical-activity status, next-week plan, barriers/obstacles, and decisions required.
- **FR-008**: The system MUST generate a monthly project report summarizing progress, baseline variance, cost, commitments, payment certificates, key risks, and next-month forecast—using “not recorded” when a section has no data.
- **FR-009**: Automatically generated reports MUST show the source and last-updated time for each figure.
- **FR-010**: Manual correction of a final report figure MUST NOT be possible without leaving an auditable trail (block or recorded history).
- **FR-011**: Changing measurement method MUST create a version and require approval before it governs new progress.

### Key Entities

- **Activity measurement definition**: Chosen method, approved total/unit/weights or milestone set, approval state, version history.
- **Physical progress record**: Period and cumulative quantities/percents, planned and approved values, link to WBS/activity/method version, evidence references, technical-approval state.
- **Weekly project report**: Period coverage, generated sections from approved sources, per-figure provenance, optional audited overrides.
- **Monthly project report**: Month coverage, composed sections (progress, variance, cost, commitments, IPC, risks, forecast), provenance, “not recorded” placeholders.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In verification scenarios, every saved progress value is traceable to a WBS package and a measurement method (or method version).
- **SC-002**: Authorized users can produce both a weekly and a monthly project report from approved records in one generation action each.
- **SC-003**: In 100% of tested cases, progress that would exceed 100% without an approved basis change is rejected.
- **SC-004**: From any figure on a generated weekly or monthly report, a user reaches the source record and its approval status in one step (one click or equivalent).
- **SC-005**: Controllers can distinguish period vs cumulative vs planned vs approved on the progress view without training beyond labels (spot-check: four labels present and values not forced equal when states differ).

## Assumptions

- Approved daily site reports (FR-DR / 007) remain the primary operational feed for quantity-based period progress; manual entry stays available under the same validation and approval rules.
- Schedule baseline lock and forecast dates (005) feed planned progress and monthly baseline variance.
- Full EVM indices belong to implementation spec 13; this feature may show simple variance figures but does not redefine EVM.
- Cost, commitments, payment certificates, and risks for monthly sections may be optional in phase 1; absence is shown as “not recorded.”
- Technical approval of progress may reuse or align with existing daily-report approval roles where appropriate; photo remains evidence only.
- Existing S-curve and KPI dashboard remain; this feature extends semantics and adds period reports rather than replacing the dashboard.
- Project-scoped authorization (constitution I) applies to all progress mutations and report generation/export.
