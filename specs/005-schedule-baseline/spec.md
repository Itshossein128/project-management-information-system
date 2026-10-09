# Feature Specification: Schedule & Baseline Gap Closure

**Feature Branch**: `005-schedule-baseline`

**Created**: 2026-10-08

**Status**: Draft

**Input**: User description: "Read Implementation Spec `05-برنامه زمان‌بندی و خط مبنا.md` (FR-SCH), define gaps versus the current application, and write new Spec Kit specs that completely cover and resolve those gaps."

**Source**: [05-برنامه زمان‌بندی و خط مبنا.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/05-برنامه%20زمان‌بندی%20و%20خط%20مبنا.md) (`FR-SCH`)  
**Depends on**: [004-wbs-structure](../004-wbs-structure/spec.md), [002-core-domain-principles](../002-core-domain-principles/spec.md), Implementation Specs 01 and 04

## Gap Analysis (current vs FR-SCH)

This feature closes **only the unmet** portions of FR-SCH. Capabilities already delivered remain in place and are **out of scope** for new work except where a gap explicitly extends them.

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-SCH-001 | Activity on WBS with duration, dates, calendar, predecessors, owner, planned %, status | Activity requires WBS; planned/actual dates, responsible, status, quantity/weight, FS–SF relations exist; duration is derived from planned dates | Working calendar; explicit duration (incl. zero for milestones); milestone type |
| FR-SCH-002 | Predecessor relations (FS min.; others allowed) | FS/SS/FF/SF + lag + cycle reject | None (keep; relation notes optional) |
| FR-SCH-003 | Warn/reject impossible dates, cycles, scope-orphans | Cycles rejected; WBS FK required (no orphan); weak/no impossible-date rules | Impossible-date and calendar-aware date validation; clear warnings |
| FR-SCH-004 | Planned, actual, and **forecast** dates stored separately | Planned + actual only | Forecast start/finish (and display vs planned/actual) |
| FR-SCH-005 | Approved baseline locked; current updates do not erase deviation history | `BaselineSchedule` + snapshot activities + `is_current`; Gantt compare | Formal **lock** of approved baseline; forbid silent overwrite of locked snapshot |
| FR-SCH-006 | Schedule change request with cause, impacts, approver, new baseline version | Absent | Full change-request lifecycle |
| FR-SCH-007 | Milestone / critical / near-critical / delay / forecast-finish report | Critical flags from import/store only; no dedicated delay/milestone report | Milestone & delay report with forecast finish |
| FR-SCH-008 / SC-SCH-004 | Critical-path result invalid when durations/relations incomplete | Stored `is_critical` used without validity gate | Validity gate: show “not calculable / not valid” instead of misleading critical flags |
| SC-SCH-001 | Link activity to WBS + predecessors | Done | Regression only |
| SC-SCH-002 | Lock baseline; keep prior versions | Partial (`is_current` only) | Lock + version retention via change request |
| SC-SCH-003 | Report shows approved, current, actual, forecast separately | Partial (Gantt baseline vs current; no forecast) | Four-way date clarity in report/views |

**Out of scope**: Complex CPM algorithms beyond validity + existing critical flags; daily reports (07); physical progress measurement methods (08); WBS tree gaps (004); ERP/P6 live sync beyond existing MSP/XER import.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete activity definition with calendar, duration, and forecast (Priority: P1)

As a project controls engineer, I define a schedule activity on a WBS package with working calendar, duration (including milestone = zero), planned dates, forecast dates, predecessors, responsible person, and status—so planned, actual, and forecast stay distinct.

**Why this priority**: Closes FR-SCH-001 and FR-SCH-004; without calendar/duration/forecast, SC-SCH-003 cannot be met.

**Independent Test**: Create two linked activities with calendars and forecast dates; create a zero-duration milestone; confirm planned/actual/forecast remain separate fields and impossible finish-before-start is rejected.

**Acceptance Scenarios**:

1. **Given** a WBS work package, **When** an activity is saved with title, duration, planned start/finish, working calendar, predecessor (FS), responsible, planned quantity or weight, and status, **Then** it is linked to that package and all fields persist.
2. **Given** forecast start and/or finish entered separately from planned and actual dates, **When** the activity is viewed, **Then** planned, actual, and forecast dates are shown as distinct values (none silently overwrites another).
3. **Given** finish date before start (planned or forecast) or a date that violates the activity’s working calendar rules, **When** the user saves, **Then** the system rejects or warns with a clear reason (impossible date).
4. **Given** a milestone activity (duration zero / milestone type), **When** it is saved, **Then** it is allowed and identifiable as a milestone in lists and reports.

---

### User Story 2 - Lock approved baseline and protect deviation history (Priority: P1)

As a project manager, after I approve a baseline I expect it to be locked. Updating the live schedule must not rewrite the locked snapshot; I can still compare approved vs current.

**Why this priority**: FR-SCH-005 / SC-SCH-002; without lock, “baseline” is only a mutable label and deviation history is unreliable.

**Independent Test**: Approve and lock a baseline; change a live activity’s planned dates; confirm locked baseline activity dates unchanged and comparison still shows variance.

**Acceptance Scenarios**:

1. **Given** a baseline marked approved/current and locked, **When** a user updates live activity planned dates, **Then** the locked baseline snapshot dates remain unchanged.
2. **Given** a locked baseline, **When** a user attempts to edit that baseline’s snapshot dates directly, **Then** the change is rejected unless done through an approved schedule change request that creates a **new** version.
3. **Given** a previous baseline version that is no longer current, **When** the user opens baseline history or comparison, **Then** the prior version remains available (not deleted by making another current).

---

### User Story 3 - Schedule change request with impact and new baseline version (Priority: P1)

As a project controls engineer, I submit a schedule change request with reason, impacts on milestones/cost/contract, and an approver path. On approval, a new locked baseline version is created without erasing the prior locked version.

**Why this priority**: FR-SCH-006 is entirely missing; it is the only compliant path to change an approved program.

**Independent Test**: Open a change request against a locked baseline; fill cause and impacts; approve; assert a new baseline version exists, prior remains, and live/current program reflects the approved change.

**Acceptance Scenarios**:

1. **Given** a locked current baseline, **When** a change request is created, **Then** it records reason, milestone impact, cost impact, contract impact, requester, and required approver(s).
2. **Given** a submitted change request, **When** an authorized approver approves it, **Then** a new baseline version is created, becomes the current locked baseline, and the previous version stays retained.
3. **Given** a rejected or draft change request, **When** viewing baselines, **Then** no new locked baseline version has been published from that request.

---

### User Story 4 - Milestone, delay, and critical-path validity report (Priority: P2)

As a project manager, I open a schedule status report that lists milestones, critical and near-critical activities, delays, and forecast project finish—and if durations or relations are incomplete, critical path is labeled not valid / not calculable instead of showing a false path.

**Why this priority**: FR-SCH-007 / FR-SCH-008 / SC-SCH-004; misleading critical flags undermine control decisions.

**Independent Test**: (A) Complete network → report shows milestones, critical/near-critical, delay, forecast finish. (B) Remove a duration or break relations → critical path marked invalid, not a fabricated path.

**Acceptance Scenarios**:

1. **Given** activities with complete durations and relations, **When** the delay/milestone report is opened, **Then** it shows milestones, critical and near-critical activities, delay versus planned/baseline, and a forecast finish date where forecast data exists.
2. **Given** incomplete durations or incomplete relation coverage for the network, **When** critical-path information is requested, **Then** the system displays “not calculable / not valid” (or equivalent localized wording) and does not present a misleading critical path as authoritative.
3. **Given** the report view, **When** the user compares date sets, **Then** approved (baseline), current planned, actual, and forecast values are distinguishable (SC-SCH-003).

---

### Edge Cases

- Milestone with duration zero is allowed; non-milestone with finish before start is rejected.
- Activity with no predecessors at project start is allowed.
- Different working calendars on linked activities: each activity’s dates validate against its own calendar; cross-calendar lag remains in whole days unless a finer rule is later defined.
- Near-critical threshold defaults to total float ≤ 5 working days (or equivalent project setting) when float is available; if float is unavailable and path validity fails, near-critical is not invented.
- Soft-deleted activities do not participate in cycle checks or critical-path validity.
- Concurrent change requests: at most one **submitted** change request against the current locked baseline may be in flight (or later requests warn of conflict); approved requests serialize into successive baseline versions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A schedule activity MUST remain linked to exactly one WBS package and MUST support title, duration (including zero for milestones), planned start/finish, working calendar reference, predecessors, responsible person, planned quantity or weight, and status.
- **FR-002**: Predecessor relations MUST continue to support at least finish-to-start; SS/FF/SF remain allowed with lag; cycle creation MUST be rejected.
- **FR-003**: The system MUST detect and reject or clearly warn on impossible dates (finish before start; dates inconsistent with the activity’s working calendar) and MUST continue to reject dependency cycles; activities without WBS MUST not be publishable (WBS remains mandatory).
- **FR-004**: Planned dates, actual dates, and forecast dates MUST be stored and presented as separate values; updating one MUST NOT overwrite another.
- **FR-005**: An approved schedule baseline MUST be lockable; locked baseline snapshot data MUST NOT be rewritten by live schedule edits; prior baseline versions MUST remain for deviation history.
- **FR-006**: A schedule change request MUST capture reason, impacts on milestones, cost, and contract, requester, and approver outcome; approval MUST create a new baseline version without destroying the previous locked version.
- **FR-007**: A schedule status report MUST present milestones, critical and near-critical activities (when path is valid), delays, and forecast finish, and MUST show approved / current / actual / forecast distinctly where data exists.
- **FR-008**: Critical-path results MUST be marked not calculable / not valid when required durations or relations are incomplete; the product MUST NOT present an authoritative critical path from incomplete data.
- **FR-009**: Soft-delete and audit expectations from core principles MUST apply to activities, relations, baselines, and change requests (who/when; no silent hard-delete of approved baseline history).

### Key Entities

- **Schedule Activity**: Time-bounded work item on a WBS package; holds planned, actual, and forecast dates; duration; optional milestone marker; calendar; owner; status.
- **Working Calendar**: Project (or shared) definition of working/non-working days used to validate activity dates.
- **Activity Relation**: Predecessor/successor link with type and lag.
- **Schedule Baseline**: Named, approvable, lockable snapshot of activity dates/quantities for deviation history; one current locked baseline per project at a time after approval.
- **Schedule Change Request**: Controlled proposal to alter the approved program; on approval produces a new baseline version.
- **Schedule Status Report**: Read model listing milestones, critical/near-critical (if valid), delays, and forecast finish with four-way date clarity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A controls user can create two FS-linked activities with calendar, duration, and distinct forecast dates, and a zero-duration milestone, in one session without losing separation of planned/actual/forecast.
- **SC-002**: In 100% of automated checks, editing live planned dates after baseline lock leaves locked baseline snapshot dates unchanged.
- **SC-003**: Approving a schedule change request always yields a new baseline version while retaining the previous version in 100% of automated checks.
- **SC-004**: When durations or relations are incomplete, critical-path output is labeled not valid / not calculable in 100% of automated checks (no authoritative false path).
- **SC-005**: The milestone/delay report distinguishes approved, current, actual, and forecast date sets whenever each set has data (verified in acceptance tests).

## Assumptions

- Existing activity CRUD, relation cycle detection, MSP/P6 import, Gantt baseline comparison, and progress modules remain the foundation; this feature extends them rather than replacing them.
- WBS packages exist before detailed scheduling (004 / Implementation Spec 04).
- Actual progress continues to be fed primarily from daily reports and progress (07, 08); this feature only ensures actual **dates** on activities remain distinct from planned and forecast.
- “Near-critical” default float threshold is 5 working days unless project settings later override it.
- Working calendar v1 is sufficient as project-level calendars with optional activity assignment; organization-wide calendar libraries can follow later.
- Complex resource-leveled CPM and automatic forecast recalculation from progress are out of scope for this feature; forecast dates may be entered or updated manually (and later automation can write the same fields).
- Relation “explanation” for non-FS types may be a free-text note on the relation if product UX needs it; not a blocker for approval of FS networks.
- Localization (Persian/English) and Jalali display follow existing product rules; stored dates remain sortable standard dates.
