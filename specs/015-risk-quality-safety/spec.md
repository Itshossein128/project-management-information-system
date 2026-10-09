# Feature Specification: Risk, Quality & Safety

**Feature Branch**: `015-risk-quality-safety`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: Implementation Spec `14-ریسک کیفیت و ایمنی.md` (FR-RSK) — register and track risk and issue as separate entities, and make quality/safety data reportable including inspection, nonconformity, incident, and near miss.

**Source**: [14-ریسک کیفیت و ایمنی.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/14-ریسک%20کیفیت%20و%20ایمنی.md) (`FR-RSK`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [004-wbs-structure](../004-wbs-structure/spec.md), [008-project-registration](../008-project-registration/spec.md)

## Gap Analysis (current vs FR-RSK)

A project risk/barrier event register already exists (`RiskEvent` with probability, severity, owner, corrective action, activity link, matrix view, and status open / in progress / resolved). Daily-report incident rows capture safety/quality notes in the field-report surface. This feature closes **unmet** FR-RSK portions: true separation of **risk vs issue**, full risk scoring/status vocabulary, richer impact dimensions and links, and first-class quality/HSE records (inspection, nonconformity, corrective action, work permit, training, incident/near miss) with project-and-period reporting.

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-RSK-001 | Risk and issue are separate entities | Single `RiskEvent` mixes risk/barrier/delay/claim types | Distinct risk vs issue records (not interchangeable) |
| FR-RSK-002 | Risk fields: description, cause, consequence, probability, impact severity, composite score, owner, response, action, due date, status | Partial (description, probability, severity, owner, corrective action, dates); cause/consequence/response/composite incomplete | Complete risk register fields + composite score rules |
| FR-RSK-003 | Statuses: open, under review, mitigated, closed, residual | open / in_progress / resolved only | Align status set to FR vocabulary |
| FR-RSK-004 | Link risk to activity, cost, contract, or related decision | Activity (+ some doc/report links); no cost/contract/decision | Add optional links as specified |
| FR-RSK-005 | Inspection plan/request/result, NCR, corrective action, work permit, training, incident, near miss as reportable data | Daily-report incidents only; no inspection/NCR/permit/training register | Introduce quality/HSE entities and capture flows |
| FR-RSK-006 | Each inspection linked to WBS, responsible person, date | N/A | Enforce those links on inspections |
| FR-RSK-007 | Quality/safety reportable at project and time period | No period quality/safety report | Project + period report |
| SC-RSK-001 | Risk register + issue path workable | Partial risk register | Full risk + separate issue path |
| SC-RSK-002 | Quality/safety project & period report | Missing | Deliver report |
| SC-RSK-003 | 100% recorded inspections have date and responsible | N/A | Enforce + test |

**In scope**: Risk; issue; scoring; actions; inspection; nonconformity; corrective action; work permit; training; incident / near miss; project and period reporting.

**Out of scope**: General workflow engine (implementation spec 15); portfolio risk dashboard (16); replacing daily-report incident capture (may remain a feed or parallel note source).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Register and track risk (Priority: P1)

As a project manager, I register a risk with cause, consequence, probability, impact severity, owner, response, and status, and I can link it to an activity, cost item, contract, or related decision so the team can follow mitigation over time.

**Why this priority**: Without a complete, trackable risk register separate from issues, control and reporting of uncertain threats cannot start (FR-RSK-001–004, SC-RSK-001).

**Independent Test**: Create an open risk with required fields → change status to mitigated → link to an activity → risk remains findable and filterable by impact dimension.

**Acceptance Scenarios**:

1. **Given** an active project, **When** a risk is saved with description, cause, consequence, probability, impact severity, composite score (when inputs allow), owner, response, action, due date, and status, **Then** it is trackable in the project risk register.
2. **Given** impacts on schedule, cost, quality, safety, contract, and/or liquidity, **When** the register is filtered by impact dimension, **Then** matching risks are returned.
3. **Given** an event that has already occurred, **When** it is recorded as an issue, **Then** it is stored separately from uncertain risks (not as a “risk” of the same kind).
4. **Given** probability or impact severity is missing, **When** the risk is saved, **Then** composite score is not computed and status defaults to (or remains) under review unless the user sets another allowed status.

---

### User Story 2 - Inspection and nonconformity (Priority: P2)

As a supervisor / quality controller, I plan and record inspections (request and result), raise nonconformities, and assign corrective actions with due dates, all linked to WBS and a responsible person.

**Why this priority**: Quality control loop depends on inspection → NCR → corrective action traceability (FR-RSK-005–006, SC-RSK-003).

**Independent Test**: Record a failed inspection with a nonconformity and a corrective action that has a due date and responsible person → all appear linked to WBS and date.

**Acceptance Scenarios**:

1. **Given** a project WBS node and a responsible person, **When** an inspection is recorded with date and result, **Then** the inspection is stored with WBS, responsible person, and date.
2. **Given** a failed inspection, **When** a nonconformity and corrective action with due date are created, **Then** they remain linked to that inspection and are reportable.
3. **Given** an attempt to save an inspection without date or responsible person, **When** validation runs, **Then** the save is rejected.

---

### User Story 3 - Incident and near miss (Priority: P2)

As an HSE officer, I record incidents and near misses with date and project (and optionally WBS) linkage, and I produce a quality/safety report for a time period.

**Why this priority**: HSE reporting and period summaries are required for site control (FR-RSK-005, FR-RSK-007, SC-RSK-002).

**Independent Test**: Two events in the same month appear in the period quality/safety report for the project.

**Acceptance Scenarios**:

1. **Given** an active project, **When** an incident or near miss is saved with date and project link, **Then** it is stored; WBS is optional but recommended.
2. **Given** multiple quality/safety records in a date range, **When** a period report is requested for the project, **Then** inspections, nonconformities, incidents, and near misses in that range are included.
3. **Given** an incident without WBS, **When** it is saved with a project link, **Then** it is accepted; missing WBS does not block save.

---

### User Story 4 - Work permit and safety training (Priority: P3)

As an HSE officer, I record work permits and safety training events so they contribute to the same project quality/safety reporting surface.

**Why this priority**: Explicitly in FR-RSK-005; lower than core risk and inspection loops for MVP sequencing.

**Independent Test**: Save a work permit and a training record for a project → both appear in the project quality/safety period report when their dates fall in range.

**Acceptance Scenarios**:

1. **Given** a project, **When** a work permit is recorded with date (and responsible person when applicable), **Then** it is reportable for the project/period.
2. **Given** a safety training record with date, **When** the period report runs, **Then** the training appears in the quality/safety period output.

---

### Edge Cases

- **Risk without probability or impact severity**: Composite score is not calculated; status is under review (or remains under review if already set).
- **Closing a risk while an action is still open**: System warns (user may proceed only with explicit acknowledgment, or be blocked—default: warn + acknowledge).
- **Incident without WBS**: Allowed; project link required; WBS recommended in UI.
- **Issue vs risk**: Occurred events must not be filed only as open risks without an issue path.
- **Empty period**: Quality/safety period report returns empty sections with clear empty state, not fabricated zeros of “perfect safety.”

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Risk and issue MUST be separate entities (or clearly separated record types with distinct lifecycle), not a single interchangeable “event” for both uncertain risk and realized issue.
- **FR-002**: Each risk MUST support description, cause, consequence, probability, impact severity, composite score (when computable), owner, response, action, due date, and status.
- **FR-003**: Risk status MUST include at least: open, under review, mitigated, closed, residual.
- **FR-004**: Users MUST be able to link a risk to a related activity, cost item, contract, and/or related decision when those targets exist on the project.
- **FR-005**: The system MUST define reportable records for inspection plan/request/result, nonconformity, corrective action, work permit, training, incident, and near miss.
- **FR-006**: Each inspection MUST be linked to a WBS node, a responsible person, and a date; missing any of these MUST prevent a valid save.
- **FR-007**: Users MUST be able to produce quality and safety reports at project scope and for a selected time period.
- **FR-008**: Impact dimensions for risk (at least schedule, cost, quality, safety, contract, liquidity) MUST be filterable in the risk register.
- **FR-009**: Closing a risk while related actions remain open MUST produce a warning (acknowledge-to-proceed in v1).
- **FR-010**: Composite score MUST NOT be invented when probability or impact severity is missing.

### Key Entities

- **Project Risk**: Uncertain threat with scoring, owner, response, actions, due date, status, impact dimensions, and optional links to activity/cost/contract/decision.
- **Issue / Obstacle**: Realized problem tracked separately from risk.
- **Inspection & Result**: Planned or requested inspection with WBS, responsible person, date, and outcome.
- **Nonconformity & Corrective Action**: Finding from inspection (or related quality check) with due corrective action.
- **Incident / Near Miss**: HSE event with date and project link; optional WBS.
- **Work Permit / Safety Training**: Permit-to-work and training records included in quality/safety reporting.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A project manager can register a risk with the required fields, change its status through the allowed set, and filter by at least one impact dimension in under 3 minutes on a seeded project.
- **SC-002**: An issue recorded for an occurred event is distinguishable from an open risk in the same project register/views (no silent merge into one type).
- **SC-003**: Quality/safety period report for a project returns inspections, nonconformities, incidents, and near misses (and permits/training when present) for the selected range without requiring a spreadsheet export as the only path.
- **SC-004**: In 100% of tested cases, an inspection cannot be saved without date and responsible person (and WBS).
- **SC-005**: In 100% of tested cases with missing probability or impact severity, composite score is absent/not computed (not a fabricated number).

## Assumptions

- “Related decision” may later be supplied by the general workflow/decision feature (implementation spec 15); v1 may store an optional decision reference or note field until that feature lands.
- Monthly/periodic progress reports (009) MAY consume “top risks” later; this feature only needs the risk data to be queryable.
- Composite score default = probability × impact severity on a defined numeric scale (e.g. 1–5 each → product), documented in planning; not computed when either input is missing.
- Daily-report incident rows may continue to exist; quality/HSE incident/near-miss register is the FR-RSK system of record for period reporting (optional import/link from daily report is out of scope unless planning adds it).
- Work permit and training are P3 for delivery sequencing but remain in product scope for FR-RSK-005.
- Closing risk with open actions: **warn + acknowledge** in v1 (not hard-block).
- Bilingual (Persian/English) labels and project-scoped authorization follow the project constitution.
- Portfolio-level risk dashboards remain out of scope (spec 16).
