# Feature Specification: Phase A.1 Daily Report Data Contract & Reference-Day Fixture (B01)

**Feature Branch**: `057-a1-b01-data-contract`

**Created**: 2026-11-19

**Status**: Clarified (Ready for Planning)

**Input**: User description: "Phase A.1 / B01 — Data contract and reference-day fixture (`01-b01-data-contract.md`, `granularity: single` inside `multi` sequence B01 → B02 → B03 → B04 → B05 → B06). Direct owners: H04, H05, D05, D07, D08, E17, X01–X10; shared with downstream owners: E02 (B03), Q01 (B05); formal items: A.1.01, A.1.02; Stage 1.2 QA findings: DEF-B01-01..DEF-B01-06; scope decisions: C01–C10; all 18 sections of `broader-daily-sections.md`."

## Clarifications

### Session 2026-11-19

- Q: What is the authoritative logical daily report unit, canonical mapping between header shifts and the three activity shifts, and authoritative source for actual shift working durations? (`C03`, `FR-011`) → A: One daily report per project per local calendar date; list only shifts that actually worked in the header; use the same shift identifiers (`1`, `2`, and `3`) in the header and in activity records; use the actual working duration recorded for each shift to calculate person-hours; if that duration is missing, treat it as unknown and do not assume planned or default hours. (Ratified 2026-11-19, actor `385da9f5-52d9-4f26-bb09-fc125283cf94`)
- Q: Is Phase A.1 acceptance scoped to a single representative daily sheet (Excel + PDF) plus discipline Excel exports only, or does it also require a multi-sheet date-range workbook and/or standalone PDFs per discipline? (`C05`, `C07`, `FR-016`) → A: Phase A.1 requires a representative single-day report in both Excel and PDF, discipline-specific Excel exports, a multi-sheet Excel workbook covering a date range, and standalone PDFs for each discipline. (Ratified 2026-11-19, actor `385da9f5-52d9-4f26-bb09-fc125283cf94`)
- Q: Which of (a) official report number & project day number, (b) wind & ground conditions from existing weather logs, and (c) 3-day weather forecast are mandatory for Phase A.1 acceptance, and what is the authoritative source or numbering rule for each? (`C08`, `FR-017`) → A: All three items are mandatory. Use the stable project ID from the project record; derive the actual project day number from the recorded actual start date (start date = day 1); format the official report number as `<projectID>-<projectDay>-<YYYY>-<MM>-<DD>` using the Solar Hijri project-local report date with two-digit months and days (e.g., `PRJ-012-12-1406-03-01` for project day 12 on 1 Khordad 1406); use existing weather logs for observed weather, wind, and ground conditions; use the free MET Norway Locationforecast 2.0 weather service for the next three days of forecasts at the project location. (Ratified 2026-11-19, actor `385da9f5-52d9-4f26-bb09-fc125283cf94`)
- Q: Do you ratify separating a versioned project job-title catalog from a selectable 34/32 Shiraz form profile, and what is the placement rule for custom, extra, and historical job titles? (`C04`, `FR-015`) → A: Approved. Keep the versioned, configurable project job-title catalog separate from the selectable Shiraz 34/32 reference-form profile, and list additional, custom, and historical job titles in an appendix. (Ratified 2026-11-19, actor `385da9f5-52d9-4f26-bb09-fc125283cf94`)
- Q: Does the current actor attribution block plus metadata fingerprint satisfy Phase A.1 (no PKI digital signature or whole-body tamper seal claimed), or is a separate cryptographic signature scope required? (`C06`, `FR-018`) → A: The existing actor attribution block and metadata fingerprint are sufficient for Phase A.1. A separate certificate-backed PKI signature or whole-report tamper-evidence mechanism is outside Phase A.1 scope. (Ratified 2026-11-19, actor `385da9f5-52d9-4f26-bb09-fc125283cf94`)
- Q: Which representative project day is designated as the A.1 reference-day fixture, and who are the named Decision Maker and Acceptance Owner? (`FR-001`, `FR-002`, `FR-005`) → A: No real project-day report is available; for Phase A.1, realistic, clearly labeled synthetic construction workday data is explicitly authorized as the reference fixture using synthetic project `SIM-A1-001` and `1406-03-01` Solar Hijri (project day 12) as the representative reference day. The designated AI workflow agent is responsible for creating and importing the fixture, recording the internal fixture decision on 2026-11-19, and verifying Phase A.1 against acceptance criteria. Once internal verification is complete, Phase A.1 is handed to the employer for independent acceptance testing; the employer retains final acceptance, with its named acceptance representative and acceptance date recorded during that handoff and review. (Ratified 2026-11-19, actor `385da9f5-52d9-4f26-bb09-fc125283cf94`)

### Session 2026-11-22

- Q: How do discipline, contractor, and block filters match activity sources within one daily summary? → A: When any discipline, contractor, or block filter is selected, a daily summary matches those filters only if one eligible activity source row satisfies them all. Exclude summaries whose matches are split across source rows. Return each matching logical daily report once. The Stage 3 Supervisor ratified this rule for B04 FR-001. [B01 data contract](contracts/daily-report-data-contract.v1.json)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Establish a Versioned Data Contract and Complete Reference-Day Fixture (Priority: P1)

The designated internal verification owner (AI workflow agent) and technical-office reviewers establish one complete, realistic, clearly labeled synthetic representative project day (`SIM-A1-001`, Solar Hijri `1406-03-01`, project day 12) and publish a versioned data contract for the official daily site report. For every field required by the agreed reference form and the daily report contract, the specification records the authoritative source document or cell, unit of measure, conversion rule, null-versus-zero semantics, print placement or explicit reason for omission from print, and the drill-down path for details not printed on the summary sheet. Every one of the 18 broader daily report sections has an explicit scope disposition (printed in Phase A.1, accessible via detail drill-down, or owned by a separate delivery phase) so that neither accidental omission nor silent scope creep occurs. Once internal verification is complete, the package is handed to the employer for independent acceptance testing, where the employer's named acceptance representative and acceptance date are recorded.

**Why this priority**: Downstream packages B02 through B06 cannot fix versioning, export parity, filtered totals, independent reconciliation, or employer acceptance without one unambiguous, versioned, auditable field contract and reference day.

**Independent Test**: Inspect the published contract and reference-day fixture independently of any product export builder and verify that 100% of required fields and all 18 broader daily sections have a recorded source, unit, empty/zero rule, print-or-drill-down disposition, version identifier, reference-day identifier (`SIM-A1-001` / `1406-03-01`, project day 12), clear synthetic-fixture labeling, internal decision/verification owner, and employer final-acceptance handoff fields.

**Acceptance Scenarios**:

1. **Given** the authorized representative reference day (`SIM-A1-001`, Solar Hijri `1406-03-01`, project day 12), **When** the versioned data contract is compiled, **Then** the contract records a version identifier, form version, reference-day identifier, internal decision/verification owner, employer acceptance handoff placeholders (representative and date filled during independent acceptance review), and an independent field-by-field mapping covering every required field of the reference form.
2. **Given** all 18 sections of the broader daily report blueprint, **When** the scope matrix is reviewed, **Then** every section has an explicit disposition identifying whether it is printed in Phase A.1, available only via drill-down, or deferred to its named owner phase (`A.3.C`, `A.4`, `A.7`, `A.8`, `A.9`, `A.10`, `A.12`) with no silent deletions.
3. **Given** a field that is excluded from the printed summary form, **When** a stakeholder inspects the contract, **Then** the contract states both the explicit reason for omission and the authoritative detail path or owner phase where that information lives.
4. **Given** the authorized synthetic construction workday fixture (`SIM-A1-001`, `1406-03-01`, project day 12) versus older unlabeled/placeholder synthetic audit samples, **When** the reference-day fixture is registered, **Then** the authorized fixture is explicitly labeled as synthetic Phase A.1 reference data, older ad-hoc audit samples remain excluded, and internal verification is clearly distinguished from final employer acceptance.

---

### User Story 2 - Govern Scope Decisions Without Fabrication or Silent Defaults (Priority: P1)

An employer representative and the internal verification owner review the complete register of scope decisions (`C01`–`C10`). Recorded baselines (`C01`, `C02`), preserved cross-phase boundaries (`C09`, `C10`), and ratified Phase A.1 decisions (`C03`–`C08`, plus synthetic reference-day governance) are clearly documented with decision text, authoritative reference, decision maker/actor, and ratification date (`2026-11-19`). Any future scope change or unratified proposal MUST remain explicitly separated from ratified decisions and never be silently defaulted.

**Why this priority**: Guessing shift durations, official report numbers, weather forecasts, workbook sheet scope, or signature guarantees would produce fabricated official output and break employer trust.

**Independent Test**: Audit the decision register against `C01`–`C10` and verify that every decision distinguishes observed current behavior, ratified decisions (with decision text, actor/maker, and date), and preserved cross-phase boundaries, with zero unresolved material output-affecting ambiguities remaining for Phase A.1.

**Acceptance Scenarios**:

1. **Given** the ten scope decisions `C01`–`C10`, **When** a reviewer inspects the contract decision register, **Then** `C01` and `C02` are recorded as current baselines, `C09` and `C10` are preserved verbatim in intent, and `C03`–`C08` record their ratified 2026-11-19 decisions with full provenance (response text, actor/reference, and date).
2. **Given** any future unratified change request or optional feature outside `C01`–`C10`, **When** no explicit ratification exists, **Then** it remains explicitly `OPEN` without fabricated defaults being substituted into official output rules.
3. **Given** the ratified `C04` decision, **When** displayed to stakeholders, **Then** it specifies separating the versioned project catalog from the selectable 34/32 Shiraz form profile with additional, custom, and historical titles listed in an appendix.
4. **Given** the ratified `C06` decision, **When** described in contract and delivery materials, **Then** the signing block is stated strictly as an actor attribution block plus metadata fingerprint, and certificate-backed PKI digital signatures or whole-report tamper-evidence mechanisms are explicitly outside Phase A.1 scope.

---

### User Story 3 - Enforce Unambiguous Zero, Unset, and Not-Measured Semantics (Priority: P1)

A site engineer or discipline reviewer records daily activity quantities where zero work occurred (`0` or `0.00`) separately from quantities that were not recorded (`null` / unset) or explicitly marked as not measured. Across all entry, summary, and export views, explicit measured zero stays zero, unset or not-measured values remain visibly marked as unknown/unrecorded rather than silently turning into `0`, and aggregates never silently coerce unknown quantities into zero. Historical contradictions in older specifications that forbade zero quantities are formally superseded by the measured-zero rule without blanket-allowing invalid zeros on fields where zero is domain-invalid (such as non-positive concrete/pressure test values).

**Why this priority**: Conflating "zero work performed" with "not reported" or "not measured" corrupts daily quantities, activity-log totals, and contractual claims.

**Independent Test**: Supply a controlled reference dataset containing explicit `0`, `0.00`, unset (`null`), and `not-measured` activity rows alongside a non-positive pressure/concrete check, and verify that the contract rules preserve `0`/`0.00` as numeric zero, label unset/not-measured as unknown without coercing them into totals, and reject domain-invalid non-positive measurements.

**Acceptance Scenarios**:

1. **Given** an activity row with an explicitly measured quantity of `0` or `0.00`, **When** validated and summarized under the contract, **Then** it is accepted as a valid measured zero and displayed as `0` / `0.00` without validation error.
2. **Given** an activity row whose quantity is unset or marked not-measured, **When** displayed or aggregated across daily summaries and activity logs, **Then** it is presented as unrecorded/unknown (never silently converted to `0`) and excluded from numeric sums rather than counted as zero.
3. **Given** legacy records with inconsistent unset states or older specification text forbidding zero, **When** reviewed under the contract, **Then** the measured-zero-vs-unknown rule supersedes the older "zero forbidden" rule while preserving strict positive-only validation where domain rules require it (such as concrete/pressure checks).

---

### User Story 4 - Define Shift Structure, Actual Working Duration, and Labor Counting Semantics (Priority: P1)

A site engineer, supervisor, and project manager rely on accurate shift working hours and unambiguous labor counts. Under the ratified `C03` rule, the contract defines one logical daily report per project per local calendar date, lists only shifts that actually worked in the header, and uses the exact same shift identifiers (`1`, `2`, and `3`) across the header, activity/labor rows, and date-based lookup views. Person-hours are derived solely from the actual working duration recorded for each shift; when that duration is missing, it is treated as unknown without assuming planned or default hours, and static placeholder text such as "shift working hours: not recorded" is eliminated. The contract also distinguishes unique headcount (persons), person-shifts, person-days, and person-hours so that a sum of row counts across activities or shifts is never mislabeled as unique persons or person-days without proof of unique attendance.

**Why this priority**: Mislabeling summed activity headcounts as "person-days" and printing hardcoded "shift hours not recorded" text directly caused QA failures `DEF-B01-02` and `DEF-B01-03`.

**Independent Test**: Verify the contract rules against a multi-shift day with overlapping workers across activities: confirm one daily report per project-date, only worked shifts listed in the header using shift IDs `1`/`2`/`3` consistently across header and rows, invalid shift codes rejected rather than silently coerced, person-hours derived strictly from recorded actual shift durations (or marked unknown when missing), and row sums labeled accurately rather than as unique person-days unless unique attendance is established.

**Acceptance Scenarios**:

1. **Given** daily work spanning one or more of the three reference shifts (`1`, `2`, `3`), **When** shift identifiers and actual durations are recorded under the ratified `C03` rule, **Then** one daily report exists per project per local calendar date, only shifts that actually worked appear in the header, header/activity/labor/date-lookup views all use shift identifiers `1`, `2`, and `3`, invalid shift codes are rejected without silent conversion, and actual working durations are shown instead of static placeholder text.
2. **Given** labor rows reported across multiple activities or shifts without unique-worker attendance deduplication, **When** totals are labeled in the user interface, activity log, or exports, **Then** the sum of row counts is NEVER labeled as unique persons or "person-days" (`نفرروز`); it uses the contract-approved count label (such as person-shifts or activity headcount sum).
3. **Given** a worked shift whose actual working duration is missing, **When** person-hours are calculated, **Then** the system does not assume planned or default hours and instead treats the duration and resulting person-hours as unknown/unrecorded per contract rules.

---

### User Story 5 - Separate Project Labor/Job Catalogs from Form-Specific Presentation Profiles (Priority: P2)

A project administrator maintains a versioned, project-specific catalog of job titles and display order that reflects real site operations without losing historical titles when templates change. Separately, under ratified `C04`, when generating an official reference form that expects a fixed positional layout (the selectable 34-row / 32-title Shiraz reference-form profile), project catalog titles map into that approved form profile while any additional, custom, or historical job titles not present in the fixed 34/32 positions are listed in an appendix without dropping or relabeling them.

**Why this priority**: Hardcoding a fixed 34/32 list as universal project truth breaks multi-project flexibility, while ignoring form-profile mapping breaks reference-form parity (`DEF-B01-04`).

**Independent Test**: Edit a project job-title template (reordering or adding a custom title) and verify under the contract that historical daily reports keep their original titles, form-specific ordering applies only through the selectable 34/32 Shiraz form profile, and extra/custom/historical titles appear in the appendix.

**Acceptance Scenarios**:

1. **Given** a project with an active versioned job-title catalog, **When** an administrator modifies the template for future days, **Then** historical records retain their original job titles and counts without deletion or retroactive relabeling.
2. **Given** a reference form using the selectable 34/32 Shiraz form presentation profile (`C04`), **When** the project contains additional, custom, or historical job titles outside the fixed 34/32 positions, **Then** the fixed layout is applied strictly as a form profile (without overwriting the project catalog) and all extra, custom, and historical job titles are listed in an appendix.

---

### User Story 6 - Define Official Reference-Form Header Fields, Weather Forecast, and Delivery Scope Boundaries (Priority: P2)

A resident supervisor and employer reviewer require complete Phase A.1 deliverables and authoritative header/weather fields. Under ratified `C05`, `C07`, and `C08`, Phase A.1 mandates: (1) a representative single-day report in both Excel and PDF, discipline-specific Excel exports, a multi-sheet Excel workbook covering a date range, and standalone PDFs for each discipline; (2) official report numbers formatted as `<projectID>-<projectDay>-<YYYY>-<MM>-<DD>` (Solar Hijri project-local date, two-digit month/day, project day derived from actual start date where start date = day 1, using the stable project ID); (3) observed weather, wind, and ground conditions from existing weather logs; and (4) 3-day weather forecasts at the project location sourced from the free MET Norway Locationforecast 2.0 service. Non-A.1 cross-phase capabilities (`X01`–`X06`, `X08`–`X10`) remain explicitly routed to their owner phases without silent deletion.

**Why this priority**: Ratifying `C05`, `C07`, and `C08` locks down the exact Phase A.1 deliverable set, header numbering rule, weather-log integration, and authoritative forecast source (`DEF-B01-01`, `DEF-B01-05`, `DEF-B01-06`).

**Independent Test**: Review the contract for `H05`, `E17`, `X07`, and `X01`–`X10` and verify that every mandatory A.1 field and export type has an approved source, formatting rule, and missing-data `"unknown"` rule, while out-of-scope cross-phase items retain their named owner phases.

**Acceptance Scenarios**:

1. **Given** a project with stable project ID (e.g., `PRJ-012` or `SIM-A1-001`), an actual start date, and a Solar Hijri project-local report date (`1406-03-01` on actual day 12), **When** the official report number and project day number are derived (`H05`, `C08`), **Then** project day counts the actual start date as day 1, the official report number formats as `<projectID>-<projectDay>-<YYYY>-<MM>-<DD>` (e.g., `PRJ-012-12-1406-03-01` / `SIM-A1-001-12-1406-03-01`) independent of internal database record IDs, and printed page numbers are valid.
2. **Given** observed weather, wind, and ground conditions in existing weather logs and a 3-day weather forecast from the free MET Norway Locationforecast 2.0 service at the project location (`X07`, `C08`), **When** rendered in A.1 official output, **Then** each field cites its authoritative source and date, displays `"unknown"` / unrecorded when a log reading, project location, or forecast response is unavailable, and never fabricates weather or forecast values.
3. **Given** the ratified A.1 output scope (`E17`, `C05`, `C07`), **When** deliverables are verified across downstream packages, **Then** Phase A.1 includes the representative single-day Excel and PDF reports, discipline-specific Excel exports, a multi-sheet date-range Excel workbook, and standalone PDFs for each discipline (while historical 367-sheet legacy ETL remains out of A.1 scope under `X08`).
4. **Given** cross-phase capabilities (`X01` offline sync, `X02` discipline QC/progress, `X03` physical progress weighting, `X04` weekly/monthly periodic reports, `X05` stakeholder/meeting/correspondence workflows, `X06` procurement/RFI/submittals, `X08` historical migration/rollback, `X09` full production rollout/training, `X10` standalone department/warehouse balance reports), **When** reviewed in the A.1 contract, **Then** each retains its named owner phase, preserves compatibility constraints with A.1, and is neither silently dropped from the product nor falsely claimed as accepted upon A.1 completion.

---

### Edge Cases

- **Unworked shifts omitted from header (`C03`)**: On a project-date where only Shift 1 and Shift 3 actually worked, the report header MUST list only Shifts `1` and `3` (omitting unworked Shift `2`), and activity/labor rows MUST reject invalid shift identifiers without silent remapping.
- **Missing actual shift working duration (`C03`)**: When a shift worked on a day but its actual working duration is missing, the system MUST treat duration and person-hours as unknown/unrecorded and MUST NOT substitute planned or default shift hours.
- **Zero vs. unset vs. not-measured in mixed aggregates (`C02`)**: A day containing one activity with `0.00`, one with `12.50`, and one unset/not-measured MUST sum to `12.50` while preserving visibility that one row is unrecorded/unknown; the unset row MUST NOT be displayed as `0`.
- **Domain-invalid zero (`C02`)**: Allowing measured zero for general activity quantities MUST NOT weaken positive-only validation for measurements where zero or negative values are physically invalid (such as non-positive pressure tests or invalid concrete metrics).
- **Duplicate worker across activities/shifts (`D07`)**: When the same worker appears in two activity rows or two shifts without unique-person attendance tracking, summing the rows MUST NOT be labeled as unique persons or `نفرروز`.
- **Additional, custom, or historical job titles outside 34/32 profile (`C04`)**: Any custom, additional, or historical job title not in the fixed 34/32 Shiraz profile positions MUST NOT be dropped or merged into an unrelated title; it MUST be listed in the report appendix.
- **Missing actual start date for project day / official report number (`C08`)**: If a project's actual start date is absent or the report date precedes the actual start date, the project day and official report number MUST surface an explicit unrecorded/validation state rather than fabricating day `0`, negative days, or synthetic IDs.
- **Absent wind/ground log or unavailable MET Norway forecast (`C08`, `X07`)**: When weather-log wind/ground readings, project coordinates, or the MET Norway Locationforecast 2.0 response are unavailable (e.g., offline, timeout, or missing location), the output MUST display an explicit `"unknown"` / unrecorded indicator and MUST NEVER fabricate weather or forecast values.
- **Summary approved while a unit source is only submitted (`C09`)**: An approved daily summary MUST NOT be presented as proof that every contributing unit source was individually approved, unless a separate policy gate is explicitly ratified.
- **Authorized synthetic fixture vs. unlabeled legacy samples (Governance)**: The authorized synthetic reference fixture (`SIM-A1-001`, `1406-03-01` Solar Hijri, project day 12) MUST be clearly labeled as synthetic construction workday data; older unlabeled placeholder samples from earlier audits remain excluded, and internal AI verification MUST NOT be presented as final employer acceptance.
- **Cross-phase interference (`X01`–`X06`, `X08`–`X10`)**: Deferring non-A.1 capabilities to their owner phases MUST NOT permit regressions in A.1 official daily output or allow daily activity quantities to be mislabeled as cumulative official physical progress (`X03`) or free-text notes to be presented as formal procurement/correspondence logs (`X05`/`X06`).

## Requirements *(mandatory)*

### Functional Requirements

#### Contract Governance & Reference-Day Fixture (`Q01`, `E02`, `A.1.01`, `A.1.02`, `DEF-B01-06`)

- **FR-001**: The data contract MUST be a versioned, reviewable artifact recording: contract version, reference-form version, representative reference-day identifier (`SIM-A1-001`, Solar Hijri `1406-03-01`, project day 12), internal decision and verification owner (designated AI workflow agent, decision recorded `2026-11-19`), employer final-acceptance handoff fields (named employer acceptance representative and acceptance date recorded during independent acceptance review in `B06`), and revision history.
- **FR-002**: Because no real project-day report is available, the contract MUST explicitly authorize realistic, clearly labeled synthetic construction workday data as the Phase A.1 reference-day fixture—using synthetic project `SIM-A1-001` and Solar Hijri `1406-03-01` (project day 12) as the representative reference day. The designated AI workflow agent MUST create and import this fixture, label it unmistakably as synthetic reference data, exclude unlabeled legacy synthetic audit samples from acceptance evidence, verify Phase A.1 internally, and hand the verified package to the employer for independent final acceptance.
- **FR-003**: For every field required by the agreed reference form and Phase A.1 daily report specification, the contract MUST provide an independent field mapping specifying: authoritative source document/cell, measurement unit, conversion rule, null/not-measured versus zero semantics, print location (or explicit omission reason), and detail drill-down path. (Independent numeric/formula/print reconciliation proof remains owned by B05 under `Q01`; B01 owns the versioned contract and field mapping.)
- **FR-004**: The contract MUST assign an explicit scope disposition to all 18 sections of the broader daily report blueprint (`broader-daily-sections.md`), classifying each section as printed in A.1, accessible via drill-down, or owned by a named separate phase (`A.3.C`, `A.4`, `A.7`, `A.8`, `A.9`, `A.10`, `A.12`).

#### Scope Decision Register & Anti-Fabrication (`C01`–`C10`, `DEF-B01-06`)

- **FR-005**: The contract MUST maintain a formal decision register for `C01`–`C10` (plus synthetic reference-day governance) preserving source wording and separating (a) observed current behavior, (b) ratified decisions, (c) preserved cross-phase boundaries, and (d) any future unresolved items. Every ratified decision MUST record response text, reference, decision maker/actor, and date (`2026-11-19` for `C03`–`C08` and synthetic fixture governance).
- **FR-006**: The contract MUST preserve `C01` (operational data enters through unit-level sources; the project daily report is a derived summary permitting only authorized project-level metadata, including during revisions) and MUST NOT re-open raw project-level operational entry.
- For B04 daily summary filtering, the B01 contract MUST record that all selected discipline, contractor, and block filters match one eligible activity source row. A split-row match excludes the summary. B04 FR-001 owns delivery and verification of this behavior.
- **FR-007**: The contract MUST preserve `C09` (unit-source `submitted`/`approved` states are independent of the daily summary's `approved` state unless an explicit stricter approval gate is ratified) and `C10` (stakeholder/meeting/correspondence workflows belong to `A.3.C`, general/periodic reporting belongs to `A.10`, and neither is deleted nor falsely marked complete by A.1 acceptance).
- **FR-008**: The contract MUST NOT fabricate values, silent defaults, or unratified employer rulings for any missing operational reading (such as missing shift durations, missing actual start dates, or unavailable weather/forecast readings) or any future open scope item.

#### Measured Zero vs. Unset / Not-Measured Semantics (`D05`, `C02`)

- **FR-009**: The contract MUST enforce `C02`: explicitly measured `0` and `0.00` quantities MUST be accepted as valid numeric zero, while unset (`null`) and explicitly `not-measured` quantities MUST remain distinct as unknown/unrecorded and MUST NEVER be silently coerced to `0` in displays, exports, or aggregations.
- **FR-010**: The contract MUST formally supersede older conflicting text that rejected zero activity quantities (`033` `FR-002`/`SC-004`) while preserving positive-only validation where domain rules forbid zero or negative values (e.g., pressure tests or concrete parameters) and defining consistent handling for legacy inconsistent records across all views and activity logs.

#### Shift Model, Actual Durations & Labor Counting (`H04`, `D07`, `C03`, `DEF-B01-02`, `DEF-B01-03`)

- **FR-011**: Under ratified `C03`, the contract MUST enforce one logical daily report per project per local calendar date, list ONLY shifts that actually worked in the report header, use the exact same canonical shift identifiers (`1`, `2`, and `3`) across the header, activity/labor records, and date-lookup views, and reject invalid shift identifiers without silent conversion.
- **FR-012**: Under ratified `C03`, official daily outputs MUST calculate person-hours exclusively from the actual working duration recorded for each worked shift and MUST eliminate static placeholder text ("shift working hours: not recorded"). When a shift's actual working duration is missing, the system MUST treat the duration and resulting person-hours as unknown/unrecorded and MUST NOT assume planned or default hours.
- **FR-013**: The contract MUST define unambiguous definitions and bilingual (Persian and English) labels for headcount, person-shifts, person-days, and person-hours. Any sum of labor rows across activities or shifts without unique-worker attendance proof MUST NOT be labeled as unique persons or "person-days" (`نفرروز`), and person-hours MUST be calculated exclusively from valid actual shift durations (or shown as unknown when duration is unavailable).

#### Job-Title Catalog & Form Presentation Profile (`D08`, `C04`, `DEF-B01-04`)

- **FR-014**: Under ratified `C04`, the contract MUST separate the project's versioned, configurable job-title catalog and ordering from the selectable 34-row / 32-title Shiraz reference-form presentation profile. Editing a project catalog or template MUST NOT delete or retroactively alter historical titles or counts.
- **FR-015**: Under ratified `C04`, when the selectable 34/32 Shiraz reference-form profile is used, any additional, custom, or historical job titles not present in the fixed 34/32 positions MUST be listed in an appendix rather than dropped or merged into unrelated titles.

#### Official Header Numbers, Weather Attributes, Delivery Scope & Signature Meaning (`H05`, `E17`, `X07`, `C05`, `C06`, `C07`, `C08`, `DEF-B01-01`, `DEF-B01-05`)

- **FR-016**: Under ratified `C05` and `C07`, Phase A.1 delivery scope MUST include all four official output deliverables: (1) a representative single-day report in both Excel and PDF, (2) discipline-specific Excel exports, (3) a multi-sheet Excel workbook covering a date range, and (4) standalone PDFs for each discipline. (Historical 367-sheet legacy ETL remains outside Phase A.1 under `X08`.)
- **FR-017**: Under ratified `C08`, Phase A.1 official output MUST include all three mandatory header/weather items with their authoritative sources:
  - **(a) Project Day & Official Report Number (`H05`)**: Use the stable project ID from the project record; derive the actual project day number from the project's recorded actual start date with the start date counted as day `1`; format the official report number as `<projectID>-<projectDay>-<YYYY>-<MM>-<DD>` using the Solar Hijri project-local report date with two-digit months and days (e.g., `PRJ-012-12-1406-03-01` for project day 12 on 1 Khordad 1406, and `SIM-A1-001-12-1406-03-01` for the reference fixture), independent of internal record IDs; printed page numbers MUST remain valid.
  - **(b) Observed Weather, Wind & Ground Conditions (`X07`)**: Source observed weather, wind, and ground conditions from existing weather logs.
  - **(c) 3-Day Weather Forecast (`X07`)**: Source the next three days of weather forecasts at the project location from the free MET Norway Locationforecast 2.0 weather service.
  - **Missing-Data Rule**: Whenever actual start date, weather-log readings, project location, or forecast data are unavailable, the output MUST display an explicit `"unknown"` / unrecorded state and MUST NEVER fabricate numbers or weather forecasts.
- **FR-018**: Under ratified `C06`, the existing actor attribution block plus metadata fingerprint is sufficient for Phase A.1. Official documentation and outputs MUST describe it strictly as actor attribution plus metadata fingerprint; certificate-backed PKI digital signatures and whole-report tamper-evidence mechanisms are explicitly outside Phase A.1 scope.

#### Cross-Phase Compatibility & Boundary Preservation (`X01`–`X06`, `X08`–`X10`)

- **FR-019**: The contract MUST explicitly route `X01` (offline sync, `A.8`), `X02` (discipline QC/progress/contractor hours, `A.8`), `X03` (physical progress weighting, `A.7`/`A.8`), `X04` (weekly/monthly periodic reports & general catalog, `A.10`), `X05` (stakeholders, meetings, correspondence, `A.3.C`/`A.10`), `X06` (daily procurement, RFI/submittals, `A.4`/`A.9`/`A.10`), `X08` (historical migration/taxonomy/rollback, `A.8`/`A.12`), `X09` (full product rollout & training, `A.12`), and `X10` (standalone department/warehouse balance reports, `A.8`/`A.10`) to their named owner phases while preserving non-regression and semantic boundaries with A.1 (e.g., daily quantities are never labeled as official cumulative physical progress; free-text daily notes are never labeled as official procurement or correspondence logs; derived project summaries remain read-only during offline sync).

### Key Entities

- **Daily Report Data Contract**: A versioned governance artifact binding the reference-form version, representative reference day (`SIM-A1-001` / `1406-03-01`), 18-section scope matrix, independent field mapping, semantic rules, and ratified `C01`–`C10` decision register.
- **Reference-Day Fixture**: The explicitly authorized, realistic, clearly labeled synthetic construction workday dataset for project `SIM-A1-001` on Solar Hijri `1406-03-01` (project day 12; official report number `SIM-A1-001-12-1406-03-01`), created and imported by the designated AI workflow agent for internal verification and subsequent employer handoff, serving as the shared baseline dataset for downstream packages `B02`–`B06`.
- **Field Mapping Entry**: A structured mapping record for one official report field specifying its identifier, source document/cell, measurement unit, conversion formula, zero/unset/not-measured rule, print placement or omission reason, and detail drill-down path.
- **Scope Decision Entry (`C01`–`C10`)**: A governed decision record distinguishing observed current behavior, ratified decision text, authoritative reference, decision maker/actor, ratification date, and preserved cross-phase boundaries.
- **Shift Definition**: A canonical shift identifier (`1`, `2`, or `3`) listed in the daily report header only when that shift actually worked on the project-date, paired with its recorded actual working duration (treated as unknown if missing; never defaulted).
- **Labor Counting Metric**: A distinct, bilingually labeled quantity class separating unique persons (headcount), person-shifts, person-days (requiring unique attendance proof), and person-hours (requiring valid actual shift durations).
- **Job-Title Catalog & Form Profile**: A versioned, project-configurable list of job titles separated from the selectable 34/32 Shiraz reference-form presentation profile, with additional, custom, and historical job titles placed in an appendix.
- **Official Report Identifier & Weather Forecast Record**: A deterministic official report identifier (`<projectID>-<projectDay>-<YYYY>-<MM>-<DD>` in Solar Hijri) paired with observed weather/wind/ground log readings and 3-day project-location forecasts sourced from MET Norway Locationforecast 2.0 (displaying `"unknown"` when unavailable).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of fields required by the agreed reference form and Phase A.1 daily report specification have an independent, reviewable mapping entry specifying source, unit, conversion, zero/unset rule, and print-or-drill-down disposition.
- **SC-002**: 100% of the 18 sections in `broader-daily-sections.md` have an explicit, non-contradictory scope disposition naming either Phase A.1 print/drill-down coverage or the exact owner phase.
- **SC-003**: 100% of scope decisions `C01`–`C10` (plus synthetic reference-day governance) are recorded in the contract decision register with complete provenance (response text, actor/reference, and date `2026-11-19`); 0 unresolved material decisions affecting official A.1 output remain.
- **SC-004**: 100% of Stage 1.2 QA findings for B01 (`DEF-B01-01` through `DEF-B01-06`) map to explicit, testable requirements and acceptance scenarios with zero unaddressed defects.
- **SC-005**: In contract review walkthroughs using controlled edge cases (measured `0`/`0.00`, unset, not-measured, multi-shift labor rows with missing durations, custom/historical job titles in the appendix, missing actual start date, and unavailable weather/forecast readings), 0 cases produce silent coercion to zero, mislabeled "person-days" (`نفرروز`), fabricated shift hours, or synthetic official numbers/forecasts.
- **SC-006**: Downstream packages `B02`–`B06` receive a complete, ratified B01 data contract and handoff specification naming `SIM-A1-001` (`1406-03-01`, project day 12) as the synthetic reference-day fixture and clearly distinguishing internal AI verification from final employer acceptance sign-off during `B06` handoff.

## Assumptions

- **Existing Core Preserved**: The existing daily report core, aggregation engine, unit pages, approval workflow, and current Excel/PDF exporters are the baseline; B01 closes the data contract and fixture gaps rather than redefining or rebuilding working subsystems.
- **Bilingual Presentation**: All user-facing field labels, unknown/unrecorded indicators, appendix headings, and labor counting terms defined by the contract will be presented accurately in both Persian and English while keeping underlying identifiers language-independent.
- **Historical Audit Evidence**: The 2026-11-18 audit baseline (162 passing tests, 2 independent checks, and 6 strict XFAIL defect reproductions) is historical evidence of observed gaps at that point in time, not proof of today's runtime state or employer acceptance.
- **External Forecast Service Dependency**: The ratified 3-day weather forecast depends on the free MET Norway Locationforecast 2.0 service and a valid project geographic location; when offline, rate-limited, or missing coordinates, the system MUST degrade gracefully to `"unknown"` / unrecorded without fabricating forecasts.
- **Synthetic Fixture vs. Employer Acceptance Boundary**: Internal creation, import, and verification of the clearly labeled synthetic reference fixture (`SIM-A1-001`, `1406-03-01`, project day 12) by the designated AI workflow agent establishes internal readiness. Under the `GOV-01` handoff policy, B01 planning, implementation, and internal verification may proceed while the employer's named acceptance representative is pending. Record the representative's name and the acceptance date during the employer's independent review in `B06`, where the employer retains final acceptance authority.
- **A.1 Acceptance Boundary**: Completing B01 (or all of Phase A.1) does not constitute acceptance of `A.3.C` (communications), `A.4`/`A.9` (procurement/document control), `A.7` (schedule/progress), `A.8` (full unit operations & offline sync), `A.10` (periodic/general reporting), or `A.12` (full production rollout & training).

---

## Scope Decisions & Clarifications Register (`C01`–`C10` + Fixture Governance)

| ID | Topic | Status | Recorded Baseline / Ratified Decision | Decision Maker & Date | Linked Requirements |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **C01** | Raw daily entry vs. derived summary | **Baseline Recorded** | Current baseline: operational entry occurs only on unit pages; project daily report is a derived summary with authorized project-level metadata only (including revisions). Older raw-form text is aligned to this baseline. | Recorded baseline (prior specs 028/032/037/039) | FR-005, FR-006 |
| **C02** | Valid measured zero vs. positive-only | **Baseline Recorded** | Current baseline: measured `0`/`0.00` is valid; `null`/`not-measured` is unknown. Supersedes older `033` zero-forbidden text without blanket-allowing domain-invalid zeros (e.g., pressure/concrete). | Recorded baseline (prior specs 034/036) | FR-009, FR-010 |
| **C03** | Header shift, activity shift & working duration | **Ratified** | One daily report per project per local calendar date; list only shifts that actually worked in the header; use identical shift identifiers (`1`, `2`, `3`) in header and activity records; compute person-hours from recorded actual working duration per shift; treat missing duration as unknown without assuming planned or default hours. | Clarification Session `2026-11-19` (actor `385da9f5-52d9-4f26-bb09-fc125283cf94`) | FR-011, FR-012, FR-013 |
| **C04** | Configurable catalog vs. fixed 34/32 count | **Ratified** | Keep the versioned, configurable project job-title catalog separate from the selectable Shiraz 34/32 reference-form profile; list additional, custom, and historical job titles in an appendix. | Clarification Session `2026-11-19` (actor `385da9f5-52d9-4f26-bb09-fc125283cf94`) | FR-014, FR-015 |
| **C05** | Single daily sheet vs. multi-sheet workbook | **Ratified** | Phase A.1 requires both a representative single-day report (Excel and PDF) AND a multi-sheet Excel workbook covering a date range. (Legacy 367-sheet historical ETL remains outside A.1 under `X08`.) | Clarification Session `2026-11-19` (actor `385da9f5-52d9-4f26-bb09-fc125283cf94`) | FR-016 |
| **C06** | Meaning of "digital signature" | **Ratified** | Existing actor attribution block and metadata fingerprint are sufficient for Phase A.1. Certificate-backed PKI digital signatures and whole-report tamper-evidence mechanisms are outside Phase A.1 scope. | Clarification Session `2026-11-19` (actor `385da9f5-52d9-4f26-bb09-fc125283cf94`) | FR-018 |
| **C07** | Standalone discipline sub-report PDF | **Ratified** | Phase A.1 requires standalone PDFs for each discipline in addition to discipline-specific Excel exports. | Clarification Session `2026-11-19` (actor `385da9f5-52d9-4f26-bb09-fc125283cf94`) | FR-016 |
| **C08** | Reference-form extra header/weather fields | **Ratified** | All three are mandatory in A.1: (a) stable project ID + actual project day (actual start date = day 1) + official report number `<projectID>-<projectDay>-<YYYY>-<MM>-<DD>` in Solar Hijri project-local date with 2-digit month/day (e.g., `PRJ-012-12-1406-03-01`), (b) observed weather/wind/ground from existing weather logs, (c) 3-day weather forecast at project location from free MET Norway Locationforecast 2.0 service. Missing readings display `"unknown"`; never fabricated. | Clarification Session `2026-11-19` (actor `385da9f5-52d9-4f26-bb09-fc125283cf94`) | FR-017 |
| **C09** | Summary approval vs. individual source approvals | **Baseline Preserved** | Unit source `submitted`/`approved` states are independent of daily summary `approved` state. Any stricter gate requiring all sources to be approved before official summary approval requires explicit policy ratification. | Recorded baseline (prior specs 032/039) | FR-007 |
| **C10** | Communications & general/periodic reports | **Boundary Preserved** | Stakeholder/meeting/correspondence workflows remain in `A.3.C`; weekly/monthly/general catalog reports remain in `A.10`. Preserved in total product scope; neither deleted nor closed by A.1. | Recorded boundary (R0) | FR-007, FR-019 |
| **GOV-01** | Reference-day fixture & acceptance governance | **Ratified (Internal Scope)** | No real project-day report is available. Explicitly allow realistic, clearly labeled synthetic construction workday data: synthetic project `SIM-A1-001`, representative day `1406-03-01` Solar Hijri (project day 12, official report `SIM-A1-001-12-1406-03-01`). Designated AI workflow agent creates/imports fixture, records internal fixture decision (`2026-11-19`), and verifies A.1 internally; employer retains final acceptance with named representative & date recorded during `B06` handoff/review. | Internal scope decision `2026-11-19` (actor `385da9f5-52d9-4f26-bb09-fc125283cf94`); Employer final acceptance pending `B06` handoff | FR-001, FR-002, FR-005 |

---

## 18 Broader Daily Sections Disposition Matrix (`broader-daily-sections.md`)

| # | Section | Audit Groups | B01 Contract Disposition | Owner / Downstream Package |
| :---: | :--- | :--- | :--- | :--- |
| 1 | General Information (اطلاعات عمومی) | H01, H04, H05, H06 | Printed in A.1; worked-shifts-only header with IDs `1`/`2`/`3` & actual durations (`C03`) and official report/project-day numbering (`C08`) mandatory | B01 (contract) → B03 (parity) |
| 2 | Weather, Wind & Ground (شرایط جوی، باد، زمین) | H02, X07 | Printed in A.1; observed weather/wind/ground from weather logs + 3-day forecast from MET Norway Locationforecast 2.0 (`C08`, `"unknown"` when absent) | B01 (`C08`) → B03 |
| 3 | Civil Activities (فعالیت‌های ابنیه) | D04, D05, E10 | Unit entry in A.8; display/export, standalone discipline PDF (`C07`), & measured-zero rule in A.1 | B01 (`D05`, `C07`) → B03, B04 |
| 4 | Mechanical Activities (فعالیت‌های مکانیکی) | D04, X02 | Unit entry & specialized QC in A.8; summary display, discipline Excel, & standalone discipline PDF (`C07`) in A.1 | A.8 (`X02`) / B01 (`C07`) → B03 |
| 5 | Electrical Activities (فعالیت‌های برقی) | D04, X02, E10 | Unit entry in A.8; summary, discipline Excel, & standalone discipline PDF (`C07`) in A.1 | A.8 (`X02`) / B01 (`C07`) → B03 |
| 6 | Manpower / Labor (نیروی انسانی) | D06, D07, D08 | Printed in A.1; counting labels (`D07`) & separate project catalog + selectable 34/32 Shiraz profile with appendix (`D08`, `C04`) governed by B01; source rules in A.8 | B01 → B03, B04 / A.8 |
| 7 | Machinery / Equipment (ماشین‌آلات) | D09, D10 | Printed in A.1 (null-hour fix in B03); operational entry in A.8 | B03 / A.8 |
| 8 | Materials (مصالح) | D11, D12 | Daily receipts printed in A.1; warehouse balance & detail in A.8/A.10 | B03 / A.8, A.10 |
| 9 | Planned & Actual Progress (پیشرفت برنامه‌ای و واقعی) | X03 | Out of A.1 print truth; daily quantities MUST NOT replace official cumulative physical progress | A.7 / A.8 (`X03`) |
| 10 | Blockers & Issues (موانع و مسائل) | D14 | Printed in A.1; formatting & parity verified in B03 | B03 |
| 11 | Safety & HSE (ایمنی و HSE) | D15 | Print localization & fields in B03; ongoing tracking in A.8 | B03 / A.8 |
| 12 | Quality Control & Tests (کنترل کیفیت و آزمایش‌ها) | D13, X02 | Print vs. detail drill-down boundary governed in B01/B03; specialized QC in A.8 | B01, B03 / A.8 (`X02`) |
| 13 | Daily Procurement (تدارکات روز) | X06 | Not a full procurement report in A.1; any print snapshot requires authoritative source link | A.4 / A.10 (`X06`) |
| 14 | Correspondence, RFI, Submittal | X05, X06 | Out of A.1 formal workflow; free-text daily notes MUST NOT substitute official workflows | A.3.C / A.9 (`X05`, `X06`) |
| 15 | Visits, Meetings & Decisions (بازدید و جلسه و تصمیم) | D16, X05 | Daily site visits in A.1; formal meetings & decisions in A.3.C | B03 / A.3.C (`X05`) |
| 16 | Site Photos (عکس‌های کارگاه) | D17 | Section/source link in A.1; real upload verification in B03/B06 | B03, B06 |
| 17 | Project Manager Comments (نظر مدیر پروژه) | W05 | Present in A.1 summary; preservation across revisions fixed in B02 | B02 |
| 18 | Unit Entry, Approval, Lock & Offline | D01, W01–W04, X01 | Derived summary & lock rules directly govern A.1 (B02); full offline acceptance in A.8 | B02 / A.8 (`X01`) |

---

## Traceability & Disposition Matrix

### Owned & Shared Requirement Groups, QA Findings, and Atomic Stories

| Identifier | Ownership / Source | Disposition | Mapped Spec Items |
| :--- | :--- | :--- | :--- |
| **H04** | Direct owner (B01); `033:190`, `039:181`, `044:181`, `US-DR-02` | Close gap (`C03` ratified: 1 report/project-date, worked shifts only, IDs `1`/`2`/`3`, actual duration or unknown) | US4, FR-011, FR-012, SC-005 |
| **H05** | Direct owner (B01); `R0:30` | Close gap (`C08` ratified: `<projectID>-<projectDay>-<YYYY>-<MM>-<DD>` Solar Hijri) | US6, FR-017, SC-003 |
| **D05** | Direct owner (B01); `007:129,152`, `033:187,272`, `034:97-99,118`, `036:84-90,109-110`, `07-گزارش:63`, `US-DR-04`, `US-DR-14` | Preserve behavior & close legacy/text conflict (`C02`) | US3, FR-009, FR-010, SC-005 |
| **D07** | Direct owner (B01); `033:196`, `US-DR-05` | Close gap (consumed by B03/B04) | US4, FR-013, SC-005 |
| **D08** | Direct owner (B01); `033:198-199`, `044:182-183`, `US-DR-05` | Close gap (`C04` ratified: separate catalog + 34/32 Shiraz profile + appendix for extra/custom/historical) | US5, FR-014, FR-015, SC-005 |
| **E17** | Direct owner (B01); `R0:46`, `delivery-plan:107` | Close gap (`C05` & `C07` ratified: single-day Excel/PDF + date-range multi-sheet Excel + discipline Excel & PDFs) | US6, FR-016, SC-003 |
| **X07** | Direct owner (B01); `R0:30` | Close gap (`C08` ratified: weather logs for wind/ground + MET Norway Locationforecast 2.0 for 3-day forecast) | US6, FR-017, SC-003 |
| **X01** | Direct owner (B01); `037:104-116,120-131,155-161`, `US-DR-15`, `US-DR-16` | Defer to owner phase (`A.8`) with A.1 readonly-sync compatibility | US1, US6, FR-004, FR-019 |
| **X02** | Direct owner (B01); `038:156-165,171,176-179,181,218-223`, `US-SR-01..04` | Defer to owner phase (`A.8`) with A.1 summary/export compatibility | US1, US6, FR-004, FR-019 |
| **X03** | Direct owner (B01); `SPEC-07`, `US-PR-01..03` | Defer to owner phase (`A.7`/`A.8`); daily volume ≠ cumulative progress | US1, US6, FR-004, FR-019 |
| **X04** | Direct owner (B01); `R0:51`, `US-PR-04..07` | Defer to owner phase (`A.10`, `C10`) | US1, US6, FR-007, FR-019 |
| **X05** | Direct owner (B01); `R0:19` | Defer to owner phase (`A.3.C`/`A.10`, `C10`) | US1, US6, FR-007, FR-019 |
| **X06** | Direct owner (B01); `R0:12,55` | Defer to owner phase (`A.4`/`A.9`/`A.10`); snapshot conditional on contract | US1, US6, FR-004, FR-019 |
| **X08** | Direct owner (B01); `032:157,195-200,225-226` | Defer to owner phase (`A.8`/`A.12`); no automatic 367-sheet ETL | US1, US6, FR-016, FR-019 |
| **X09** | Direct owner (B01); `R0:20` | Defer full rollout/training to `A.12`; A.1 scoped release in B06 | US1, US6, FR-019 |
| **X10** | Direct owner (B01); `SPEC-09`, `SPEC-10`, `US-DP-01..03`, `US-WH-01..02` | Defer to owner phase (`A.8`/`A.10`); preserve six-unit source ownership | US1, US6, FR-004, FR-019 |
| **E02** | Shared (primary owner: B03) | Contract field & layout mapping only (no re-owning B03 parity) | US1, FR-003, SC-001 |
| **Q01** | Shared (primary owner: B05) | Versioned contract & independent field mapping only (B05 owns final proof) | US1, FR-001, FR-002, FR-003, SC-001 |
| **DEF-B01-01** | Stage 1.2 QA (`H05`, `C08`) | Resolved in contract (`C08` ratified: deterministic Solar Hijri official report & project day numbering) | US6, FR-017, SC-004 |
| **DEF-B01-02** | Stage 1.2 QA (`H04`, `C03`) | Resolved in contract (`C03` ratified: worked shifts `1`/`2`/`3` & actual durations, no static placeholder) | US4, FR-011, FR-012, SC-004 |
| **DEF-B01-03** | Stage 1.2 QA (`D07`) | Close gap in contract counting semantics (consumed by B03/B04) | US4, FR-013, SC-004, SC-005 |
| **DEF-B01-04** | Stage 1.2 QA (`D08`, `C04`) | Resolved in contract (`C04` ratified: separate catalog + 34/32 Shiraz profile + appendix) | US5, FR-014, FR-015, SC-004 |
| **DEF-B01-05** | Stage 1.2 QA (`X07`, `C08`) | Resolved in contract (`C08` ratified: weather logs for wind/ground + MET Norway Locationforecast 2.0) | US6, FR-017, SC-004 |
| **DEF-B01-06** | Stage 1.2 QA (`C01`–`C10`, 18 sections) | Resolved in contract (`C01`–`C10` + `GOV-01` recorded with provenance; 18-section matrix complete) | US1, US2, FR-001..FR-008, SC-002..SC-004 |
