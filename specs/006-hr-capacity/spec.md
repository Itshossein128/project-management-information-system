# Feature Specification: HR & Capacity Gap Closure

**Feature Branch**: `006-hr-capacity`

**Created**: 2026-10-08

**Status**: Draft

**Input**: User description: "Read Implementation Spec `06-منابع انسانی و ظرفیت.md` (FR-HR) and write Spec Kit specs that resolve gaps versus the current application."

**Source**: [06-منابع انسانی و ظرفیت.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/06-منابع%20انسانی%20و%20ظرفیت.md) (`FR-HR`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [004-wbs-structure](../004-wbs-structure/spec.md), [005-schedule-baseline](../005-schedule-baseline/spec.md), Implementation Specs 01 / 03 / 04

## Gap Analysis (current vs FR-HR)

This feature closes **only the unmet** portions of FR-HR. Leave, overtime, manpower headcount grids, and progress isolation from labor already exist and are **out of scope** except where a gap explicitly extends them.

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-HR-001 | Person dossier: id, name, unit, position, skills, qualifications, supervisor, status, contact | User has name/contact/status/org text; project position via membership | Skills, qualifications, org unit, dossier supervisor |
| FR-HR-002 / SC-HR-003 | Sensitive employee data restricted | Project membership RBAC; wage often visible to any member | Field-level ACL for wage / approved rates (and similar sensitive fields) |
| FR-HR-003 | Assignment to project + WBS/activity with range, role, hours or % capacity, location, supervisor | `ProjectMember` = access membership only (optional dates/wage) | Resource **allocation** entity distinct from membership |
| FR-HR-004 / SC-HR-001 | Available capacity after overlapping allocations; over-capacity warning | Absent | Capacity calculation + conflict warning |
| FR-HR-005 / SC-HR-001 | Over-capacity exception with reason + manager approval | Absent | Exception workflow + flag on allocation |
| FR-HR-006 | Shift plan, attendance, approved hours, OT, absence separated | OT + leave done; manpower = headcount; no per-person attendance / shift schedule / general approved-hours ledger | Minimal: keep leave/OT; add **named** separation rules + optional thin attendance/shift stubs only if needed for SC clarity (prefer assume leave/OT suffice for P2 time types already shipped) |
| FR-HR-007 / SC-HR-002 | Allocation ≠ attendance; attendance ≠ progress proof | Progress already from measured activity qty only; no allocation layer | Preserve progress isolation; ensure allocation never feeds attendance or progress |
| FR-HR-008 | Labor cost from approved rate × approved hours; confidential rates | Auto cost from daily_rate on report; member wage unused; no rate ACL | Prefer approved rate when estimating; warn if missing; redact rates without permission |

**Out of scope**: Legal payroll; treating attendance as progress proof; re-building leave/OT/manpower UIs; full HRIS; organization-wide calendar libraries.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extend person dossier (Priority: P1)

As an HR or project resource manager, I maintain a person’s dossier with unit, skills, qualifications, supervisor, status, and contact so assignments have a valid active person.

**Why this priority**: FR-HR-001; allocations and capacity make no sense without an identifiable person profile.

**Independent Test**: Open/update a person dossier with skills and qualifications and a supervisor; inactive person cannot receive a **new** allocation; historical allocations remain readable.

**Acceptance Scenarios**:

1. **Given** an authorized user, **When** they save skills, qualifications, organizational unit, supervisor, status, and contact on a person, **Then** those fields persist and appear on the dossier view.
2. **Given** a person marked inactive, **When** a new project allocation is attempted, **Then** the system rejects it; existing historical allocations remain viewable.
3. **Given** a user without HR/person-edit permission, **When** they attempt to edit dossier fields, **Then** the change is denied.

---

### User Story 2 - Allocate a person to project / WBS / activity (Priority: P1)

As a project or resource manager, I allocate an active person to a project (and optionally a WBS package and/or activity) with date range, role, capacity as percent or hours, work location, and supervisor—separately from project membership/access.

**Why this priority**: FR-HR-003; membership today is not resource allocation.

**Independent Test**: Create a valid allocation; see it on the project allocation list; confirm membership can exist without allocation and vice versa (membership still required for app access as today).

**Acceptance Scenarios**:

1. **Given** an active person and an active project with WBS/activity available, **When** an allocation is saved with date range, role, capacity (% or hours), optional WBS/activity, location, and supervisor, **Then** it appears in the project’s allocation list.
2. **Given** an allocation to a WBS or activity, **When** viewed, **Then** the linked scope (project / WBS / activity) is explicit and navigable.
3. **Given** overlapping date validation needs, **When** end date is before start date, **Then** the system rejects the allocation.

---

### User Story 3 - Capacity conflict warning and approved exception (Priority: P1)

As a resource controller, when overlapping allocations exceed 100% (or the person’s available capacity), I receive a clear conflict warning. Recording an over-capacity allocation requires a reason and manager approval, stored as an exception.

**Why this priority**: FR-HR-004/005 and SC-HR-001 are the acceptance bar for capacity control.

**Independent Test**: With capacity 100% and an existing 80% allocation, a new 50% overlapping allocation warns; completing it only after exception reason + authorized approval stores the allocation with an exception flag.

**Acceptance Scenarios**:

1. **Given** a person with available capacity 100% and an existing 80% allocation in a date range, **When** a new 50% allocation overlapping that range is submitted without exception, **Then** the system warns (or rejects until exception path is used)—capacity conflict is visible to the user.
2. **Given** a capacity conflict, **When** an authorized manager approves an exception with a written reason, **Then** the allocation is saved with an exception flag, approver, reason, and decision time.
3. **Given** a rejected or draft exception, **When** viewing allocations, **Then** the over-capacity allocation is not treated as fully approved without the exception decision.

---

### User Story 4 - Sensitive rates and approved-rate cost estimate (Priority: P2)

As a finance or HR policy owner, wage and approved labor rates are hidden from users without sensitive-HR permission. Cost estimates may use approved rate × approved hours when available; if no approved rate exists, the system warns and does not invent a number.

**Why this priority**: FR-HR-002/008 and SC-HR-003; wage leakage and fake rates undermine trust.

**Independent Test**: User without sensitive permission cannot see wage/rate fields; estimate path with missing approved rate yields warning/optional blank, never a fabricated amount; attendance/labor entry alone still does not change activity progress (SC-HR-002 regression).

**Acceptance Scenarios**:

1. **Given** a user without sensitive wage/rate permission, **When** they view member or allocation financial fields, **Then** wage/approved rates are hidden or inaccessible.
2. **Given** an authorized user and an approved rate plus approved hours, **When** a labor cost estimate is requested, **Then** the estimate uses those approved inputs (not an invented rate).
3. **Given** no approved rate, **When** an estimate is requested, **Then** the system warns and does not fabricate a cost figure.
4. **Given** attendance or daily-report labor headcount only, **When** progress is recalculated, **Then** activity physical progress is unchanged (allocation/attendance are not progress proof).

---

### Edge Cases

- Part-time allocations across multiple projects: sum overlapping % (or equivalent hours converted to %) against available capacity.
- Inactive person: no new allocations; history readable.
- Missing approved rate: warn / optional estimate, never invent.
- Project membership without allocation (and allocation records that do not by themselves grant app login) remain distinct concepts.
- Soft-delete/audit on allocations and exceptions; approved exception history retained.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A person dossier MUST support identity, name, organizational unit, position/title context, skills, qualifications, supervisor, status, and necessary contact fields.
- **FR-002**: Sensitive employee fields (at minimum wage and approved labor rates) MUST be readable only by users with an explicit sensitive-HR (or equivalent) permission; others MUST NOT receive those values.
- **FR-003**: A resource allocation MUST capture person, project, optional WBS and/or activity, date range, role, capacity as percent and/or hours, work location, and allocation supervisor—and MUST be distinct from project membership/access.
- **FR-004**: Available capacity MUST be computed after subtracting overlapping allocations in the same period; over-capacity MUST produce a user-visible conflict warning.
- **FR-005**: Recording an over-capacity allocation MUST require a capacity exception with reason and authorized manager approval; the allocation MUST retain an exception flag and decision audit.
- **FR-006**: Shift plan, attendance, approved hours, overtime, and absence remain conceptually separate; existing leave and overtime flows MUST continue to represent their types without being conflated with allocation or attendance.
- **FR-007**: Allocation MUST NOT count as attendance; attendance or labor headcount alone MUST NOT prove or update activity physical progress.
- **FR-008**: Labor cost estimates MAY use approved rate × approved hours when both exist; missing approved rate MUST warn and MUST NOT invent a rate; rate visibility follows FR-002.
- **FR-009**: Soft-delete and audit expectations from core principles MUST apply to allocations and capacity exceptions (who/when; no silent hard-delete of approved exception history).

### Key Entities

- **Person dossier**: Extended human resource profile (skills, qualifications, unit, supervisor, status).
- **Resource allocation**: Planned assignment of a person to project scope with capacity and dates (not app membership).
- **Capacity exception**: Approved over-capacity decision with reason, approver, and link to allocation.
- **Approved labor rate**: Policy rate used for estimates (confidential per FR-002).
- **Time record types** (conceptual): shift plan, attendance, approved hours, overtime, absence—kept separate from allocation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100% of automated conflict tests, overlapping allocations that exceed available capacity produce a visible conflict before or instead of a silent save.
- **SC-002**: In 100% of automated exception tests, an over-capacity allocation is persisted with exception flag only after reason + authorized approval.
- **SC-003**: In 100% of automated ACL tests, a user without sensitive-HR permission does not receive wage or approved-rate values.
- **SC-004**: In 100% of automated regression tests, recording attendance/labor headcount alone does not change activity physical progress.
- **SC-005**: A resource manager can create a person dossier update and a project allocation with % capacity in one uninterrupted session and see both on their respective lists.

## Assumptions

- Leave requests and overtime (including manager-adjusted approved hours) remain the shipped implementations of those FR-HR-006 types; this feature does not rebuild them.
- Daily-report manpower/labor grids remain headcount tools; a full per-person attendance clock and shift-schedule planner can follow later as an additive module without blocking SC-001–SC-005.
- Default available capacity is 100% unless a dossier or policy sets otherwise.
- Capacity comparison uses percent; when only hours are entered, convert using a documented standard day length (e.g. 8 hours = 100%) stated in plan/tasks.
- Project membership continues to control application access; allocation alone does not grant login or project permissions.
- WBS/activity targets come from existing project structure (004/005).
- Localization (Persian/English) and Jalali dates follow existing product rules.
