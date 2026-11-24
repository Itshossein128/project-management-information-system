# Feature Specification: Phase A.1 Daily Report Version Integrity, Derived-Row Lock & Lineage Preservation (B02)

**Feature Branch**: `058-a1-b02-version-integrity`

**Created**: 2026-11-19

**Status**: Draft

**Input**: User description: "Phase A.1 / B02 — Revision integrity, derived-row lock, provenance preservation, and current-approved operational totals (`02-b02-version-integrity.md`, `granularity: single` inside `multi` sequence B01 → B02 → B03 → B04 → B05 → B06). Direct owners: H06, D01, D02, D03, W01, W02, W03, W04, W05, W06, E15; shared coordination with B01: X01; formal deliverable: A.1.03; Stage 1.2 QA findings: DEF-B02-01..DEF-B02-06; prerequisite handoff: B01 (`specs/057-a1-b01-data-contract`, `output/a1-b01-stage5-qa-verification-2026-11-19.md`)."

## Prerequisite Handoff (B01)

- **Upstream Package**: Phase A.1 / Package B01 (`specs/057-a1-b01-data-contract`), verified `qa_passed` in `output/a1-b01-stage5-qa-verification-2026-11-19.md` (2026-11-19).
- **Inherited Ratified Contract Rules**:
  - `C01` (Baseline): Operational daily data enters exclusively through unit-level sub-reports; the project daily report is a derived summary permitting only authorized project-level metadata, including during revisions.
  - `C02` (Baseline): Measured zero (`0`, `0.00`) is valid; unset (`null`) and not-measured values remain unknown and are never coerced to zero.
  - `C03` (Ratified 2026-11-19): One logical daily report per project per local calendar date; header lists only worked shifts using canonical identifiers `1`, `2`, and `3`; actual working durations are used (unknown if missing).
  - `C09` (Baseline Preserved): Unit-source `submitted`/`approved` states are independent of the daily summary's `approved` state; approving a summary does not assert that every contributing unit source was individually approved.
  - `C10` (Boundary Preserved): Communications (`A.3.C`) and periodic/general reports (`A.10`) remain in their owner phases without silent deletion or premature closure.
  - `GOV-01` (Ratified 2026-11-19): Authorized synthetic reference fixture `SIM-A1-001` (`1406-03-01` Solar Hijri, project day 12) supports internal verification; employer final acceptance remains pending independent review in `B06`.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preserve Derived-Summary Identity and Lock Derived Rows Across Revisions (Priority: P1)

A site engineer or technical-office specialist opens a formal correction on an approved project daily report that was aggregated from at least two site units. The newly created draft revision preserves its derived-summary identity so that operational rows (activities, labor, materials, concrete logs, machinery, general activities, visits, and derived incidents) remain strictly read-only across every user interface, single-row edit, bulk edit, offline sync, and legacy edit entry point. Any attempt to directly create, modify, or delete a derived row is rejected based on row ownership rather than relying solely on a single client assumption or report-level flag. To correct operational data, the authorized user updates the originating unit sub-report and triggers an authorized summary rebuild, while still being allowed to edit authorized project-level management metadata on the editable revision.

**Why this priority**: Opening a correction currently strips the derived-summary identity (`DEF-B02-01`) and allows direct mutation of derived rows (`DEF-B02-02`), directly breaking the core source-of-truth boundary (`C01`, `D01`, `W03`).

**Independent Test**: Start with an approved daily summary aggregated from two units, open a correction with a valid reason (at least 10 characters), verify the draft revision retains its derived-summary identity, attempt direct creation, modification, and deletion of derived rows through single-row, bulk, and legacy paths (all rejected), verify authorized project-level metadata remains editable, then update a source unit sub-report and run an authorized rebuild to confirm the derived row updates cleanly.

**Acceptance Scenarios**:

1. **Given** an approved derived daily summary generated from at least two unit sub-reports, **When** an authorized user opens a correction with a reason of at least 10 characters, **Then** the resulting draft revision retains its derived-summary identity and remains linked as the next version superseding the prior approved version.
2. **Given** an open draft revision of a derived daily summary, **When** any user attempts to directly create, update, or delete a derived operational row via single-row, bulk/batch, offline sync, or legacy mutation paths, **Then** the system rejects the mutation with a clear read-only ownership error and leaves the stored derived row unchanged.
3. **Given** an open draft revision of a derived daily summary, **When** an authorized user updates a contributing unit sub-report and triggers an authorized summary rebuild, **Then** the draft revision refreshes its derived rows from eligible unit sources without permitting manual authoring of derived rows.
4. **Given** an open draft revision of a derived daily summary, **When** an authorized user edits permitted project-level summary metadata (such as management opinion or authorized weather/site overrides), **Then** the edit succeeds without unlocking or altering derived operational rows.

---

### User Story 2 - Preserve Complete Multi-Source Provenance and Lineage Across Revisions (Priority: P1)

An auditor or project controller inspects a derived row (such as a combined activity or labor total contributed by two separate unit sub-reports) before opening a correction, during the open draft revision, after approving the revision, and in an independent branch after cancelling a correction. In every state, the full set of contributing source references for every derived row is preserved and accurately remapped to the target version's row identifiers so that multi-source drill-down never collapses to zero sources or to a single-source link.

**Why this priority**: Currently, opening a correction drops all multi-source provenance records (`DEF-B02-03`: 2 source records in the approved original drop to 0 in the draft revision), destroying auditability (`W04`).

**Independent Test**: Create an approved daily summary containing a derived row contributed by 2 distinct unit sources, verify 2 traceable provenance records exist, open a correction, verify the cloned row in the new revision has 2 provenance records remapped to the new row identifier (pointing to the same 2 original sources), approve the revision and verify both sources remain traceable, and in a separate branch cancel a correction and verify the restored approved version still shows both sources.

**Acceptance Scenarios**:

1. **Given** an approved daily summary where a derived row aggregates contributions from two or more unit sources, **When** a correction is opened, **Then** all child rows and the complete set of derived-source provenance records are cloned and remapped to the new revision's child row identifiers, preserving every contributing source and its contribution details.
2. **Given** an open draft revision with remapped provenance records, **When** an authorized user inspects provenance drill-down for any derived row, **Then** all contributing unit sources (e.g., 2 of 2) are returned with accurate source unit, version, row identity, and access-checked navigation.
3. **Given** an open draft revision that is subsequently approved, **When** an auditor inspects the version history and the newly approved revision, **Then** both the superseded version and the newly approved revision retain their own complete, independently auditable provenance records without cross-version corruption.
4. **Given** an open draft revision that is cancelled before approval, **When** cancellation completes, **Then** the prior approved version is restored as current with its exact original derived-summary identity, child rows, and complete multi-source provenance intact.

---

### User Story 3 - Preserve Management Opinion, Authorized Overrides, and Version-Bound Snapshots (Priority: P1)

A project manager or resident supervisor records a management opinion and an authorized weather or site-status override on a daily summary, then approves it. When a correction is later opened, rebuilt, approved, or cancelled, the management opinion, authorized weather/site overrides, and required configuration/aggregation/fingerprint metadata are preserved or regenerated according to explicit version rules. Meanwhile, historical approved snapshots and archived/non-current versions remain strictly immutable: any attempt to automatically rebuild a historical, superseded, or archived version is rejected, and modifying a source unit after approval never silently alters an approved snapshot.

**Why this priority**: Opening a correction currently erases management opinion and weather overrides (`DEF-B02-04`), and automatic rebuilds do not reject historical/non-current versions (`DEF-B02-06`), risking silent corruption of official project records (`W05`, `W06`).

**Independent Test**: Save a management opinion and weather/site override on an approved daily summary, open a correction, verify both values and effective configuration/aggregation metadata are preserved on the draft revision, trigger a rebuild and verify overrides and management opinion persist, attempt an automatic rebuild against the superseded historical version and verify it is rejected with zero changes to its snapshot or provenance, and modify a source unit after approval to confirm the approved snapshot stays unchanged while drift is surfaced.

**Acceptance Scenarios**:

1. **Given** an approved daily summary containing a management opinion, authorized weather/site overrides, and effective reporting configuration/aggregation metadata, **When** a correction is opened, **Then** the draft revision preserves the management opinion, authorized overrides, and version-appropriate configuration/aggregation metadata while keeping snapshots and approval fingerprints bound to their own version.
2. **Given** an open draft revision carrying preserved management opinion and weather/site overrides, **When** an authorized rebuild runs after a unit sub-report update, **Then** derived operational rows refresh from eligible unit sources while the management opinion and authorized overrides remain preserved unless explicitly changed by an authorized user.
3. **Given** a superseded, historical, or archived daily report version, **When** an automatic rebuild is invoked targeting that non-current version, **Then** the system rejects the rebuild and leaves that historical version's rows, provenance, fingerprint, and approved snapshot completely unchanged.
4. **Given** an approved daily summary whose contributing unit sub-report is later modified outside an approved correction cycle, **When** a user views the approved summary, **Then** the approved snapshot remains unchanged and the system surfaces a clear source-drift comparison/warning without silently rewriting approved data.

---

### User Story 4 - Count Only the Current Approved Version in the Official Activity Master Log (Priority: P1)

A project controller or executive reviews the official project activity master log after a daily report has been approved, corrected, and re-approved. The official activity master log includes ONLY the current approved version of each daily report so that operational quantities and headcounts are never double-counted across superseded versions. Historical superseded versions remain accessible exclusively through dedicated version-history inspection views. Downstream filtering and aggregate totals (Package B04) consume this exact current-approved policy.

**Why this priority**: Currently, the official activity master log filters only for `approved` without requiring `current` (`DEF-B02-05`), causing two approved 5-unit versions of the same day's activity to double-count as 10 units and double headcount (`E15`).

**Independent Test**: Approve version 1 of a daily report containing an activity with quantity `5` and headcount `4`, open a correction to create version 2 with the same activity (quantity `5`, headcount `4`), approve version 2, then query the official activity master log and confirm it returns 1 row with official total quantity `5` and headcount `4` (not 2 rows / `10` / `8`), while version 1 remains viewable in version history. In an independent branch, open version 2 and cancel it, confirming version 1 returns as the single current approved version in the official log.

**Acceptance Scenarios**:

1. **Given** a daily report approved as version 1 (quantity `5`, headcount `4`) and subsequently corrected and approved as version 2 (quantity `5`, headcount `4`), **When** a user queries the official activity master log, **Then** only version 2 (current approved) is included, yielding 1 row, official quantity `5`, and headcount `4` (never 2 rows, `10`, and `8`).
2. **Given** a daily report with an approved version 1 and an open (unapproved draft) correction version 2, **When** a user queries the official activity master log, **Then** unapproved draft version 2 is never included in official approved totals, and historical versions remain inspectable through the dedicated version-history path.
3. **Given** a daily report where correction version 2 is cancelled before approval, **When** cancellation restores version 1 as the current approved version, **Then** the official activity master log reflects version 1 accurately with no duplicate or missing rows.

---

### User Story 5 - Enforce Logical Uniqueness, Effective Six-Unit Configuration, Eligible Sources, and Role-Safe Workflow (Priority: P2)

Site teams, viewers, reviewers, and approvers rely on predictable daily report initialization, accurate date-effective required units, strict source eligibility, and server-enforced workflow roles. Opening a project date repeatedly never creates duplicate parallel reports for the same logical day, and read-only viewers can open and inspect a date without edit permissions. Required units are determined from the project's effective reporting configuration on that report date across the six valid units (buildings, electrical, mechanical, machinery, warehouse, security) rather than a hardcoded three-discipline default. Only current `submitted` or `approved` unit sub-reports from the same project and same date contribute to aggregation and completeness, and workflow transitions enforce valid state order, mandatory rejection reasons (at least 10 characters), role permissions, project isolation, and separation of duties.

**Why this priority**: Preserving and proving these foundational behaviors (`H06`, `D02`, `D03`, `W01`, `W06`) alongside the six defect fixes ensures B02 delivers complete, regression-free version and workflow integrity without rewriting working core subsystems.

**Independent Test**: Repeatedly open the same project date as both an editor and a read-only viewer (no duplicate report created; viewer succeeds without edit permission); test two reporting-configuration template versions with different effective dates to verify required units follow the date-effective configuration; introduce draft, rejected, soft-deleted, superseded, other-date, and other-project unit sub-reports to verify zero contribution; and exercise submit/review/approve/reject transitions with valid roles, unauthorized roles, cross-project users, short rejection reasons, and same-user submitter/approver separation-of-duties checks.

**Acceptance Scenarios**:

1. **Given** a project and local calendar date under the ratified `C03` one-report-per-date rule, **When** multiple users or repeated date lookups open that date, **Then** no duplicate parallel daily report is created, and a read-only viewer can view the report without requiring edit permissions.
2. **Given** a project with two reporting-configuration template versions effective on different dates across the six valid units (buildings, electrical, mechanical, machinery, warehouse, security), **When** daily reports are evaluated on dates before and after the change, **Then** required units and completeness indicators follow the configuration effective on each report date rather than a fixed three-discipline default.
3. **Given** unit sub-reports in `draft`, `rejected`, `soft-deleted`, or `non-current` states, or belonging to another date or another project, **When** daily summary aggregation and completeness evaluation run, **Then** those ineligible sub-reports contribute zero rows, zero quantities, and zero completeness credit; only current same-project, same-date `submitted` or `approved` unit sources contribute (while keeping unit approval status independent of summary approval status per `C09`).
4. **Given** a daily report moving through `draft` → `submitted` → `approved` / `rejected`, **When** a user attempts an invalid state transition, submits a rejection reason shorter than 10 characters, lacks the required project role permission, belongs to another project, or violates separation of duties (e.g., approving their own submission where disallowed), **Then** the server rejects the action with a localized, explicit error and leaves the report state unchanged.

---

### Edge Cases

- **Concurrent correction requests**: When two authorized users submit correction requests for the same approved daily report simultaneously, only one correction succeeds; the second request is rejected cleanly with an explicit "correction already open" error, and no duplicate draft revision is created.
- **Short or empty correction/rejection reasons**: Attempting to open a correction or reject a report with a missing or whitespace-trimmed reason shorter than 10 characters MUST be rejected with a localized validation error.
- **Cancellation of non-cancellable states**: Attempting to cancel a correction whose draft revision has already been submitted, approved, cancelled, or altered out of lineage MUST be rejected without disturbing the current report.
- **Direct edit bypass on legacy/bulk/offline paths (`DEF-B02-02`, `X01`)**: Even if a client sends a direct single-row, batch/bulk, legacy, or offline-sync mutation against a derived row (whether on version 1 or on a revision), server-side ownership enforcement MUST reject the mutation regardless of UI state.
- **Rebuild targeted at historical/archived/deleted version (`DEF-B02-06`)**: Invoking automatic aggregation/rebuild on a superseded (`not current`), approved, or soft-deleted version MUST be rejected so historical snapshots and provenance remain immutable.
- **Approved summary with subsequent unit edits (`W06`)**: Editing or creating a newer version of a unit sub-report after the project daily summary is approved MUST NOT silently modify the approved summary's rows or snapshot; instead, source-drift comparison surfaces the difference until an authorized correction cycle is opened and rebuilt.
- **Approved summary with submitted (unapproved) unit sources (`C09`)**: An approved daily summary built from `submitted` unit sources MUST remain valid under `C09` and MUST NOT falsely claim that every contributing unit source is individually approved.
- **Cross-project and unauthorized access**: A user from another project or a member lacking the required permission MUST be denied access to open corrections, cancel corrections, rebuild summaries, mutate metadata, inspect unauthorized source drill-downs, or approve/reject reports.
- **Read-only observation vs. mutation**: A system administrator observing a project without active project membership and mutation permissions MUST NOT be able to open corrections, edit metadata, rebuild, or approve/reject daily reports (Constitution Principle I).
- **Logical date and shift alignment (`C03`, `H06`)**: Revisions MUST preserve the logical project-date identity and ratified `C03` worked-shift/official-report contract metadata without creating parallel reports for the same project-date.

---

## Requirements *(mandatory)*

### Functional Requirements

#### Derived-Summary Identity & Row-Ownership Lock (`D01`, `W03`, `X01`, `DEF-B02-01`, `DEF-B02-02`)

- **FR-001**: When a correction revision is created from a derived daily summary, the resulting revision MUST preserve its derived-summary identity throughout the revision lifecycle and upon cancellation/restoration of the prior version (`DEF-B02-01`).
- **FR-002**: The system MUST enforce derived-row read-only protection based on row ownership and derived-summary identity across ALL mutation paths—including user interface, single-row child endpoints, bulk/batch endpoints, offline sync paths (`X01`), and legacy entry paths—rejecting any direct creation, update, or deletion of derived operational rows regardless of version number (`DEF-B02-02`, `C01`).
- **FR-003**: Raw manual creation of a standalone project daily report operational record MUST remain forbidden; operational data MUST enter only through authorized unit-level sub-reports and flow into the project daily summary via authorized aggregation (`D01`, `C01`).
- **FR-004**: Authorized project-level summary metadata (such as management opinion and authorized weather or site-status overrides) MUST remain distinct from derived operational rows and MUST remain editable by authorized users while a daily summary or correction revision is in an editable state (`W03`, `W05`).

#### Revision Lineage, Multi-Source Provenance & Metadata Preservation (`W02`, `W04`, `W05`, `DEF-B02-03`, `DEF-B02-04`)

- **FR-005**: Opening a correction on a current approved daily report MUST require an explicit reason of at least 10 non-whitespace characters, atomically mark the prior approved version as non-current, create a new current draft revision linked to the same lineage and incremented version number, and prevent concurrent duplicate open corrections for the same lineage (`W02`).
- **FR-006**: Cloning a daily report into a correction revision MUST copy all active child rows AND clone and remap the complete set of multi-source provenance records (`DailyReportDerivedSource`) to the exact newly created child row identifiers in the target revision, preserving every contributing source (not merely a single source reference) (`W04`, `DEF-B02-03`).
- **FR-007**: A derived row contributed by `N` unit sources (e.g., `N >= 2`) MUST continue to expose all `N` traceable sources with accurate source identity, version, and contribution values after correction creation, after approval, and after cancellation/restoration (`W04`, `DEF-B02-03`).
- **FR-008**: Opening a correction MUST preserve authorized summary-owner metadata—including management opinion, weather/site overrides, effective reporting configuration binding, aggregation metadata, completeness state, and ratified B01 contract header metadata—according to explicit version rules, while keeping approval snapshots and metadata fingerprints strictly bound to each individual version (`W05`, `DEF-B02-04`).
- **FR-009**: Running an authorized rebuild on an editable draft revision MUST refresh derived operational rows and their multi-source provenance from eligible current unit sources while preserving management opinion and authorized weather/site overrides unless explicitly modified by an authorized user (`W05`).
- **FR-010**: Cancelling an open draft correction revision MUST atomically retire/soft-delete the draft revision, mark the correction request cancelled with actor and timestamp, and restore the exact prior approved version as current with its original derived-summary identity, child rows, complete multi-source provenance, management opinion, overrides, and approved snapshot unchanged (`W02`).

#### Official Snapshot Immutability & Historical Rebuild Protection (`W06`, `DEF-B02-06`)

- **FR-011**: Automatic aggregation or summary rebuild MUST reject any target daily report version that is approved, historical/non-current, or archived/deleted, guaranteeing that historical snapshots, rows, fingerprints, and provenance records remain completely immutable (`W06`, `DEF-B02-06`).
- **FR-012**: Modifying a contributing unit sub-report after a project daily summary has been approved MUST NOT silently alter the approved summary's stored rows or snapshot; the system MUST preserve the approved snapshot with separate submission and approval timestamps and surface source-drift differences until an authorized correction cycle is performed (`W06`).

#### Official Activity Master Log Current-Version Policy (`E15`, `DEF-B02-05`)

- **FR-013**: The official operational activity master log MUST include ONLY rows belonging to daily reports that are both `approved` AND `current` (excluding draft, rejected, soft-deleted, and superseded historical approved versions) so that corrected reports are never double-counted in operational totals or headcounts (`E15`, `DEF-B02-05`).
- **FR-014**: Historical superseded versions of daily reports MUST remain viewable through dedicated version-history inspection paths separate from official operational activity-log totals (`E15`).
- **FR-015**: The current-approved operational policy established by `FR-013` MUST be exposed consistently so downstream Package B04 can apply the identical policy across filtered activity-log queries, server-side aggregates, and `FILE1` exports (`E15`, `DEF-B02-05`).

#### Logical Uniqueness, Six-Unit Effective Configuration, Source Eligibility & Workflow Integrity (`H06`, `D02`, `D03`, `W01`)

- **FR-016**: Under ratified `C03` and `H06`, opening or looking up a project daily report by date MUST enforce logical uniqueness per project and local calendar date without creating duplicate parallel reports, and MUST allow authorized read-only viewers to open and view reports without edit permissions.
- **FR-017**: Required reporting units and completeness evaluation MUST use the project's effective reporting configuration for the report's calendar date across the six valid units (buildings, electrical, mechanical, machinery, warehouse, security) rather than a hardcoded three-discipline default (`D02`).
- **FR-018**: Daily summary aggregation and completeness calculation MUST include ONLY current, non-deleted unit sub-reports belonging to the same project and same report date in `submitted` or `approved` status; `draft`, `rejected`, `soft-deleted`, `superseded`, other-date, and other-project sub-reports MUST contribute zero rows and zero completeness credit (`D03`). Consistent with `C09`, summary approval status MUST remain explicitly distinct from individual unit-source approval status.
- **FR-019**: Daily report workflow transitions (`draft`, `submitted`/in-review, `approved`, `rejected`) MUST enforce valid transition order, mandatory rejection reasons of at least 10 characters, server-side project membership and role permissions, cross-project isolation, and separation of duties between preparer/submitter and approver (`W01`, Constitution Principle I).
- **FR-020**: All validation, permission, lock, and lifecycle errors in B02 MUST return clear, localized messages in both Persian and English while keeping machine-readable error codes language-independent (Constitution Principle III).

### Key Entities

- **Daily Report Version & Lineage**: A versioned project-level daily summary uniquely identified per project and local calendar date (with a single `current` version per lineage), linked to its superseded predecessor and carrying workflow status, derived-summary identity, and version-bound snapshot/fingerprint metadata.
- **Correction Request**: A governed lifecycle record authorizing a new draft revision from a current approved daily report, capturing mandatory reason (≥10 characters), requester, timestamps, source version, result version, and terminal outcome (`approved` or `cancelled`).
- **Derived Operational Row & Ownership Lock**: Any child operational record (activity, labor, material, concrete, machinery, general activity, visit, or derived incident) produced from unit sub-reports whose read-only protection is enforced by data ownership across all edit channels.
- **Multi-Source Provenance Record (`DailyReportDerivedSource`)**: An audit mapping linking one derived row in a specific daily report version to each contributing unit sub-report, source version, source row, and contribution value (supporting many-to-one aggregation).
- **Authorized Project-Level Summary Metadata**: Project-level fields owned directly by the daily summary (management opinion, authorized weather/site overrides, effective configuration binding, and aggregation metadata) that remain editable on editable versions without unlocking derived operational rows.
- **Official Activity Master Log Entry**: An operational activity record drawn strictly from `current` + `approved` daily report versions, separated from historical version archives.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In end-to-end verification of the primary B02 lifecycle (approved summary from ≥2 units and multiple sources → correction opened with reason → direct create/edit/delete of derived rows rejected → unit source updated and authorized rebuild executed → new version approved → totals and multi-source lineage verified → independent branch correction cancelled and prior version restored), 100% of steps pass with zero data loss and zero unauthorized derived-row mutations.
- **SC-002**: 100% of Stage 1.2 QA defects (`DEF-B02-01` through `DEF-B02-06`) are resolved and verified by passing automated and scenario checks with **0** expected-failure (`XFAIL`) markers remaining for B02 defects.
- **SC-003**: A derived row aggregated from 2 distinct unit sources retains 2 of 2 (100%) traceable provenance records remapped to the target revision's row identifier after correction creation, after approval, and after cancellation/restoration.
- **SC-004**: When an activity with quantity `5` and headcount `4` exists across two approved versions of the same project-date (version 1 superseded, version 2 current approved), the official activity master log reports exactly **1** row with quantity `5` and headcount `4` (0% double-counting), while version 1 remains accessible in version history.
- **SC-005**: 100% of attempted direct mutations on derived rows across single-row, bulk/batch, offline, and legacy entry paths are rejected on both original summaries and correction revisions, while 100% of permitted project-level metadata edits (management opinion and authorized overrides) succeed on editable revisions and persist across rebuilds.
- **SC-006**: 100% of automatic rebuild attempts targeting historical, superseded, approved, or soft-deleted report versions are rejected with 0 changes to historical rows, provenance, or snapshots.
- **SC-007**: Under concurrent correction requests, invalid workflow transitions, short reasons (<10 characters), ineligible sources (draft/rejected/deleted/historical/other-date/other-project), read-only viewer access, cross-project access, unauthorized roles, and separation-of-duties checks, 100% of security and integrity invariants hold without duplicate reports or privilege escalation.
- **SC-008**: Technical verification readiness for B02 (`A.1.03`) is documented separately from final employer acceptance, which remains explicitly gated on independent review in Package `B06`.

---

## Assumptions

- **Existing Core Preserved**: The existing daily report core, aggregation engine, six unit sub-report pages, workflow engine, and correction infrastructure are extended rather than rewritten; B02 fixes verified gaps and proves preserved behaviors.
- **B01 Handoff Stability**: Package B01 (`specs/057-a1-b01-data-contract`) is complete and verified (`qa_passed`); B02 honors all ratified `C01`–`C10` and `GOV-01` rules, including one report per project-date (`C03`), valid measured zero (`C02`), and independent unit-vs-summary approval status (`C09`).
- **Cross-Phase Ownership**: Full offline sync (`X01` / `A.8`), full six-unit operational workflows (`A.8`), communications (`A.3.C`), periodic reports (`A.10`), and production rollout (`A.12`) remain owned by their respective phases; B02 enforces non-regression and read-only derived-row boundaries where those paths intersect A.1 daily reports.
- **Downstream Handoff to B03 & B04**: Stabilized revision identity, provenance, snapshot immutability, and current-approved activity-log policy from B02 will be consumed directly by B03 (reference-form export parity) and B04 (filters, full-queryset aggregates, and `FILE1` export).
- **Technical Gate vs. Employer Acceptance**: Passing all B02 automated and live QA checks establishes technical readiness for `A.1.03` and unlocks B03/B04, but does NOT constitute employer final acceptance (which is formally recorded in `B06`).

---

## Traceability & Disposition Matrix

### 1. Stage 1.2 QA Findings & Formal Deliverable (`A.1.03`)

| Finding ID | Deliverable | Disposition | Linked Requirements | Linked User Stories & Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **DEF-B02-01** | `A.1.03` | **Gap Fix** — Preserve derived-summary identity in correction revision and on cancellation | FR-001, FR-010 | US1, SC-001, SC-002 |
| **DEF-B02-02** | `A.1.03` | **Gap Fix** — Enforce derived-row ownership lock across UI, child, batch, offline, and legacy paths | FR-002, FR-003, FR-004 | US1, SC-001, SC-002, SC-005 |
| **DEF-B02-03** | `A.1.03` | **Gap Fix** — Clone and remap complete multi-source `DailyReportDerivedSource` set to target row IDs | FR-006, FR-007, FR-010 | US2, SC-001, SC-002, SC-003 |
| **DEF-B02-04** | `A.1.03` | **Gap Fix** — Preserve management opinion, authorized overrides, and version-bound config/aggregation metadata | FR-004, FR-008, FR-009 | US3, SC-001, SC-002, SC-005 |
| **DEF-B02-05** | `A.1.03` | **Gap Fix** — Filter official activity log to `approved` + `current` only; keep history separate (consumed by B04) | FR-013, FR-014, FR-015 | US4, SC-002, SC-004 |
| **DEF-B02-06** | `A.1.03` | **Gap Fix** — Reject automatic rebuild targeting historical/non-current/archived/deleted versions | FR-011, FR-012 | US3, SC-002, SC-006 |

### 2. Owned Requirement Groups & Shared Coordination

| Group ID | Title | Disposition | Linked Requirements | Historical Audit Basis (2026-11-18) |
| :--- | :--- | :--- | :--- | :--- |
| **H06** | Logical daily report uniqueness, date shell, no raw entry | **Behavior Preservation & Proof** (align with `C03`, concurrency & viewer proof) | FR-003, FR-016 | Existing implementation; acceptance proof pending |
| **D01** | Project report derived-only; data entry via unit pages | **Gap Fix** (close correction bypass & all child/batch/legacy paths) | FR-001, FR-002, FR-003 | Confirmed gap (`DEF-B02-01`, `DEF-B02-02`) |
| **D02** | Six valid units & date-effective reporting configuration | **Behavior Preservation & Proof** (verify 2 effective template versions) | FR-017 | Existing implementation; two-version date proof pending |
| **D03** | Eligible sources: current, same project/date, submitted/approved | **Behavior Preservation & Proof** (preserve `C09` boundary & exclusions) | FR-018 | Existing implementation; full negative-source proof pending |
| **W01** | Draft, submit/review, approve/reject workflow & official lock | **Behavior Preservation & Proof** (role matrix, SoD, ≥10-char rejection) | FR-019, FR-020 | Existing implementation; full role/SoD matrix pending |
| **W02** | Correction, versioning, reason, cancellation & restoration | **Gap Fix** (complete identity, provenance & metadata transfer + concurrency) | FR-001, FR-005, FR-006, FR-008, FR-010 | Confirmed gap (`DEF-B02-01`, `DEF-B02-03`, `DEF-B02-04`) |
| **W03** | Derived-data lock after correction & no direct editing | **Gap Fix** (ownership-based lock across all edit paths; keep allowed metadata editable) | FR-001, FR-002, FR-004 | Confirmed gap (`DEF-B02-01`, `DEF-B02-02`) |
| **W04** | Row provenance & complete multi-source set | **Gap Fix** (remap complete `DailyReportDerivedSource` set to target row IDs) | FR-006, FR-007, FR-010 | Confirmed gap (`DEF-B02-03`) |
| **W05** | Management opinion, weather/site overrides & summary metadata | **Gap Fix** (preserve opinion, overrides, config/aggregation/fingerprint metadata) | FR-004, FR-008, FR-009 | Confirmed gap (`DEF-B02-04`) |
| **W06** | Immutable approved snapshot & source-drift detection | **Gap Fix & Proof** (block historical rebuilds; keep snapshot stable on source edits) | FR-011, FR-012 | Existing snapshot comparison; historical rebuild gap (`DEF-B02-06`) |
| **E15** | Current approved version in official log; history separate | **Gap Fix** (enforce `is_current` alongside `approved` in official log) | FR-013, FR-014, FR-015 | Confirmed gap (`DEF-B02-05`) |
| **X01** *(Shared)* | Offline sync compatibility with derived-row read-only lock | **Shared Coordination** (primary owner `B01`/`A.8`; B02 enforces derived-row lock on offline sync paths without redefining `A.8`) | FR-002 | Boundary preserved with `B01`/`A.8` |

### 3. Atomic Stories & Source-Clause Traceability

| Atomic Story | Source Path & Line | B02 Share / Disposition | Out-of-Scope Share (Routed Owner) |
| :--- | :--- | :--- | :--- |
| **US-DR-03** | `reports_documentation/atomic-specs/SPEC-01-DAILY-HEADER-WEATHER.md:67` | `H06` — Logical uniqueness, viewer read access, no parallel duplicates (FR-016) | None |
| **US-DR-11** | `reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md:26` | `W01` — Workflow transitions, rejection reason ≥10 chars, official lock (FR-019, FR-020) | None |
| **US-DR-12** | `reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md:53` | `W03` — Derived-row lock across revisions & all edit paths (FR-001, FR-002, FR-004) | None |
| **US-DR-13** | `reports_documentation/atomic-specs/SPEC-03-DAILY-LIFECYCLE-LOCK.md:74` | `W02, W04, W05` — Correction creation/cancel, full provenance remap, opinion/override preservation (FR-005–FR-010) | None |
| **US-SR-01..04** | `reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md:30,53,70,87` | `D01` — Unit-page source-of-truth boundary & no raw project operational authoring (FR-002, FR-003) | `X02` (`A.8`), `E10` (`B03`/discipline exports) |
| **US-AG-01** | `reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:34` | `D01, H06` — Auto-summary shell uniqueness & derived-only identity (FR-001, FR-003, FR-016) | None |
| **US-AG-02** | `reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:55` | `D03, W04` — Eligible-source selection & multi-source provenance (FR-006, FR-007, FR-018) | `D04, D06, D11` (other A.1 packages) |
| **US-AG-03** | `reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:78` | `W03` — Derived-row read-only enforcement across all edit paths (FR-002) | None |
| **US-AG-04** | `reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:95` | `W05` — Management opinion & authorized overrides preserved across revision/rebuild (FR-004, FR-008, FR-009) | `H02` (weather/site baseline) |
| **US-AG-05** | `reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:112` | `D02` — Date-effective six-unit reporting configuration (FR-017) | None |
| **US-AG-06** | `reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:129` | `E15` — Current-approved-only official activity log; separate history (FR-013–FR-015) | `E11, E13, E14` (`B04` filters & full-queryset aggregates) |

**Mapped Source Clause Clusters** (full line-level inventory verified from `02-b02-version-integrity.md` and `output/a1-requirements-2026-11-18/source-clauses.json`):
- `specs/007-daily-report-gaps/spec.md:126-132,150` (`FR-007..009`, `FR-013`, `SC-002`) → `W01, W02, W03, W06` (FR-001, FR-002, FR-005, FR-011, FR-012, FR-019)
- `specs/028-auto-daily-report-summary/spec.md:92-94,109-116,134-140` (`FR-001..003,005,006,009,011,012`, `SC-001,002,005,007`) → `D01, D02, D03, H06, W05` (FR-001..004, FR-008, FR-016..018)
- `specs/031-site-inactivity-security/spec.md:93-94,117` (`FR-011,012`, `SC-005`) → `H06` (FR-016)
- `specs/032-unit-report-source-truth/spec.md:144-194,218-224` (`FR-001,003,005..013,017..032`, `SC-001,003..007`) → `D01, D02, D03, H06, W01..W05` (FR-001..010, FR-016..019)
- `specs/033-daily-sections-grid/spec.md:200,243-250,270-277` (`FR-012,037..039,042..044`, `SC-002,005,009`) → `D03, W03, W04, W05` (FR-002, FR-006..009, FR-018)
- `specs/034-daily-lifecycle-lock/spec.md:87-96,115-119` (`FR-001..010`, `SC-001..003,005`) → `W01, W02` (FR-005, FR-010, FR-019, FR-020)
- `specs/035-correction-lineage-cloning/spec.md:89-104,118-121` (`FR-001..011`, `SC-001..004`) → `W02` (FR-001, FR-005..010)
- `specs/036-validation-codes-unset-semantics/spec.md:79-83,108` (`FR-001..005`, `SC-001`) → `W01` (FR-019, FR-020)
- `specs/037-daily-offline-sync/spec.md:117-119` (`FR-014..016`) → `W03, W04, W05` & shared `X01` (FR-002, FR-006, FR-008)
- `specs/038-discipline-sub-reports/spec.md:180,184,186,224` (`FR-016,018,020`, `SC-007`) → `D01, D02, W03` (FR-002, FR-003, FR-017)
- `specs/039-auto-daily-rollup/spec.md:179-194,211-218` (`FR-001,002,004,007,008,013..016`, `SC-001,002,004,007,008`) → `H06, D01, D02, W03, W05` (FR-001..004, FR-008, FR-009, FR-016, FR-017)
- `reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:60-62` (`FR-DR-007..009`) → `W01, W02, W06` (FR-005, FR-011, FR-012, FR-019)
