# Feature Specification: Specialty Unit Daily Sections and Structured Aggregation

**Feature Branch**: `033-daily-sections-grid`

**Created**: 2026-10-23

**Status**: Draft

**Input**: User description: "Complete the specialty-unit daily-report sections and aggregate them as structured data in the project daily report: each unit records the data it is responsible for in its own daily report, the aggregation engine transfers structured data from submitted or approved unit reports into the project daily report without fabrication, premature flattening, or loss of provenance, and derived rows in the project report are read-only and correctable only in their source unit report."

**Reference artifacts**:

- `reports_gaps/02/GAP-SPEC-02-DAILY-SECTIONS-GRID.md` — verified gap analysis and target output contract
- `reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md` — historical section contracts; superseded wherever it conflicts with the gap report or this specification
- The sample workbook «گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز» is a structural and sample-data reference only; it MUST NOT be imported into the product or treated as an instruction or operational data source
- `specs/028-auto-daily-report-summary/` — historical baseline; superseded wherever it conflicts with this specification
- `specs/032-unit-report-source-truth/` — the unit source-of-truth feature this feature depends on and extends

**Feature boundary**: The canonical unit taxonomy, the unit-report authoring workflow on the Specialty Units pages, eligibility rules, and summary rebuild mechanics are already resolved by feature 032 and MUST NOT be reintroduced through a standalone route such as `/sub-reports`. Final page design, printable/PDF and Excel-equivalent output, report number, page number, header composition, and signature areas are specified in the third feature of this series and are out of scope here.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record executed-activity rows with the full site contract (Priority: P1)

An authorized Buildings, Electrical, or Mechanical unit user adds an executed-activity row to that unit's daily report for a date. Each row carries the approved active project WBS activity, an activity description, a shift, an active project contractor, headcount, parcel, block, floor, location, a completed quantity, a unit, and optional notes. All of these are validated at the point of entry so bad data never reaches the project daily report.

**Why this priority**: Executed activities are the backbone of the project daily report's main table; without the complete row contract, aggregation cannot reproduce the daily report the business recognizes, and every later section depends on the same validation pattern.

**Independent Test**: Save an activity row with every required field for an active project, then attempt to save rows with a zero quantity, a WBS activity from another project, and an unrecognized shift value; verify the valid row is stored completely and each invalid attempt is refused with an explicit, localized error.

**Acceptance Scenarios**:

1. **Given** an authorized Buildings user and an approved active WBS activity of the project, **When** the user saves an executed-activity row with description, shift, contractor of the same project, headcount, parcel, block, floor, location, a positive completed quantity, and a unit, **Then** the row is stored with every required value and no field is silently dropped or flattened.
2. **Given** a completed quantity of zero or a negative number is provided, **When** the row is saved, **Then** it is rejected with an explicit error and nothing is stored.
3. **Given** a WBS activity or a contractor that belongs to another project, **When** a row referencing it is saved or submitted, **Then** it is rejected with a permission or validation error and no reference to the foreign project is stored.
4. **Given** a shift value that is not a recognized project shift, **When** the row is saved, **Then** it is rejected or explicitly recorded as unknown, and it is never silently mapped to another shift.
5. **Given** a row records both a crew name and a contractor, **When** it later appears in the project daily report, **Then** both appear as separate concepts in their own columns and neither is substituted for the other during aggregation.

---

### User Story 2 - Record labor with a project-configurable job-title catalog (Priority: P1)

An authorized unit user records indirect and direct labor by job title, present count, leave/absence count, associated contractor, and overtime. Counts are non-negative integers, man-hours are reproducibly calculated by the project-approved rule stored with the project template, and category totals plus an overall total are always calculable for output. The job-title catalog itself is versioned and configurable at the project-template level, so no fixed number of titles is hard-coded as a universal truth.

**Why this priority**: Labor totals are contractually significant for cost and progress claims. Incorrect aggregation — especially attributing a shared job title to the last contributing unit — would corrupt totals and provenance that auditors rely on.

**Independent Test**: Save labor rows for one title from two different unit reports, rebuild the summary, and verify the aggregate total equals the sum of both and the drill-down lists every source; then attempt a negative count and an unknown title and verify both are refused.

**Acceptance Scenarios**:

1. **Given** a labor row with a catalog job title, present count, leave count, contractor, and overtime hours, **When** it is saved, **Then** its man-hours are reproducibly calculated using the project-approved rule for that project and stored with the row.
2. **Given** a negative present, leave, or other count, **When** the row is saved, **Then** it is rejected with an explicit error.
3. **Given** the same job title recorded in unit reports from two different units for the same date, **When** the project summary aggregates labor, **Then** the aggregate retains every contributing source in its drill-down and the last unit never displaces an earlier one.
4. **Given** two projects whose templates define different job-title catalogs, counts, and display orders, **When** each records labor, **Then** each project uses only its own effective catalog and display order.
5. **Given** a catalog revision that migrates legacy titles, reorders display, or adds project-specific titles, **When** historical rows are retrieved, **Then** they keep their original identity and history and no title evidence is lost.

---

### User Story 3 - Derive the machinery status table without double counting (Priority: P1)

The Machinery unit user records, for every equipment type or stable equipment identifier, the total, active, ready-to-work, inactive, and under-repair counts for the reporting day, plus — where operationally needed — operating, stoppage, and repair hours and the stoppage reason. The project daily report derives its machinery table from this data. A stoppage reason is mandatory whenever stoppage hours exceed zero, the total recorded time for one equipment item never exceeds 24 hours in a day, stoppage reasons are controlled and translatable values, and an equipment item with a stable identity is never counted twice in a day's aggregation.

**Why this priority**: The machinery table is one of the main tables of the real daily report and is currently absent from the summary; it also introduces the day-limit and controlled-vocabulary rules that protect data quality.

**Independent Test**: Record one equipment item's status with operating and stoppage hours and a reason, then record orphan rows that omit a reason for positive stoppage, exceed 24 total hours, use an uncontrolled reason, and duplicate the same stable equipment identity; verify the first is aggregated once and every orphan is rejected.

**Acceptance Scenarios**:

1. **Given** Machinery unit data for a date with per-item or per-type status counts, **When** the project daily report is produced, **Then** the machinery table shows the five statuses — total, active, ready-to-work, inactive, and under-repair — derived from that unit report, not entered at project level.
2. **Given** the same equipment item with a stable identity appears in more than one contributing row, **When** the day is aggregated, **Then** it is counted exactly once and no duplicate appears.
3. **Given** stoppage hours greater than zero with no stoppage reason, **When** the row is saved, **Then** it is rejected with an explicit error.
4. **Given** operating, stoppage, and repair hours for one equipment item whose recorded total exceeds 24 hours in a day, **When** the row is saved, **Then** it is rejected with an explicit error.
5. **Given** a stoppage reason that is not one of the project's controlled, translatable values, **When** the row is saved, **Then** it is rejected and no free-text reason bypasses the vocabulary.

---

### User Story 4 - Display only real receipts in the main materials table (Priority: P1)

The Warehouse unit user records material receipts, consumption and consumption location, units, supplier, and warehouse-document reference — each preserved independently. The main material table of the project daily report shows only real receipts. The aggregation engine displays an item as a receipt only when it is a real receipt; it never blindly converts all generic material rows into receipts. Consumption and reconciliation stay available in visible details or a drill-down, and reconciliation compares recorded quantities against a specific warehouse document — not merely the total historical inventory balance — producing explicit, traceable statuses: match, mismatch, and insufficient data.

**Why this priority**: The real daily report shows only received materials in its main table; showing consumption there or fabricating receipts from generic rows would misrepresent procurement reality and undermine trust in reconciliation.

**Independent Test**: Record one receipt with a warehouse-document reference and one consumption row, rebuild the summary, and verify the main table shows only the receipt; open the drill-down and verify the consumption row and the reconciliation status against the referenced document are both traceable.

**Acceptance Scenarios**:

1. **Given** a real receipt recorded by the Warehouse unit, **When** the project daily report is produced, **Then** the receipt appears in the main materials table with its quantity, unit, and provenance.
2. **Given** a consumption row recorded by the Warehouse unit, **When** the project daily report is viewed, **Then** the main table does not show it, and the row remains discoverable and traceable in the visible details or drill-down.
3. **Given** a generic material row with no receipt evidence, **When** aggregation runs, **Then** the engine does not display it as a receipt in the main table.
4. **Given** a reconciliation request for a recorded receipt, **When** it is compared against the specific warehouse document it references, **Then** one of the explicit statuses — match, mismatch, or insufficient data — is returned and the comparison is traceable to that document reference.
5. **Given** only a historical total inventory balance and no specific warehouse document, **When** reconciliation runs, **Then** the result is insufficient data rather than a fabricated match.

---

### User Story 5 - Record concrete pours with traceable quality-control linkage (Priority: P2)

An authorized unit user records each concrete pour with its description or grade, a positive volume, the structural element or location, parcel, block, floor, the batching plant, the truck or delivery-note number, the laboratory sample code, the sampling state, and the test-sheet count. When sampling is declared, the required test information must be present and a traceable link to the corresponding quality-control work is created. Negative volumes and data belonging to another project are rejected.

**Why this priority**: Concrete traceability supports structural quality claims later; it is complete but less time-critical than the main execution tables.

**Independent Test**: Save a complete pour with sampling declared and its test information; then attempt rows with a negative volume, a declared sampling state but missing test information, and a batching-plant reference from another project; verify only the first is accepted and the link to quality control is findable from the record.

**Acceptance Scenarios**:

1. **Given** a complete pour record with a positive volume and all required identifiers, **When** it is saved, **Then** it is stored intact and appears in the project daily report with its provenance once its unit report is eligible.
2. **Given** a negative volume, **When** the record is saved, **Then** it is rejected with an explicit error.
3. **Given** data referencing a batching plant or any other identifier that belongs to another project, **When** saved or submitted, **Then** it is rejected with a permission or validation error.
4. **Given** sampling is declared on a pour, **When** the record is saved, **Then** the declaring row carries the required test information and a traceable link to the corresponding quality-control work; a declared sampling state without the required test information is not accepted as complete.

---

### User Story 6 - Keep general activities, issues, visits, and HSE incidents structured (Priority: P2)

General activities remain structured rows — description, location or building, quantity or volume, unit, and notes — and are never converted into formatted text for storage. Buffered issues or barriers and project visits are structured records with source unit, date, text, and display order. A barrier carries an owner and a due date, and an HSE incident carries a severity and an immediate action and creates the required notification or follow-up task. A general note is never automatically an issue unless it is explicitly typed as one.

**Why this priority**: These narrative-sounding sections are where aggregation historically flattened meaning into text blobs; keeping them structured preserves accountability and order across rebuilds.

**Independent Test**: Record one general activity, one barrier with owner and due date, one visit, and one HSE incident; rebuild the summary twice; verify all four remain structured records in stable order, an implicit notification/task exists for the incident, and an untyped note never appears as an issue.

**Acceptance Scenarios**:

1. **Given** a general activity row with description, location or building, quantity or volume, unit, and notes, **When** it is saved and later aggregated, **Then** every column remains independently addressable and none is stored as formatted text.
2. **Given** an issue or barrier recorded by a unit, **When** the project summary is rebuilt, **Then** it appears as a structured record with its source unit, date, text, and display order preserved.
3. **Given** a barrier, **When** it is saved, **Then** it carries an owner and a due date.
4. **Given** an HSE incident with a severity and an immediate action, **When** it is saved, **Then** the required notification or follow-up task is created in addition to the record itself.
5. **Given** a free-text general note without an explicit issue type, **When** aggregation runs, **Then** it is not silently promoted into an issue or barrier record.

---

### User Story 7 - Attach field images with provenance and rejection rules (Priority: P2)

A unit user may attach JPEG or PNG images up to 10 MB to a related activity. Capture date, work front, source activity, source unit, and the file's project are preserved. Files that are not valid images are rejected with explicit errors, and files cannot be attached across projects. Because the reference daily report has no dedicated photo section, the project daily report shows an accessible count of images per section with links; a large gallery in the printable form is not required without an approved need.

**Why this priority**: Field evidence is valuable but secondary; the contract protects storage and cross-project isolation without expanding the printable report.

**Independent Test**: Attach a valid in-range image to an activity and retrieve its count and link from the summary; then attempt an oversized image, a non-image file, and an attachment referencing another project's activity; verify every invalid attempt is refused with a clear error.

**Acceptance Scenarios**:

1. **Given** a valid JPEG or PNG image within the size limit, **When** it is attached to a related activity, **Then** it is stored with capture date, work front, source activity, source unit, and project, and remains retrievable through its link.
2. **Given** a file that is not a valid JPEG or PNG, including compressed archives and executables, **When** the upload is attempted, **Then** it is rejected with an explicit localized error and nothing is stored.
3. **Given** an image exceeding the maximum size, **When** the upload is attempted, **Then** it is rejected with an explicit error.
4. **Given** an attachment whose referenced activity belongs to another project, **When** the upload or link is attempted, **Then** it is refused and no cross-project reference is created.
5. **Given** a section of the project daily report with attached images, **When** it is viewed, **Then** an accessible image count with links is available and no large gallery is required in the printable output.

---

### User Story 8 - Aggregate and correct without fabrication, duplication, or staleness (Priority: P1)

An authorized project user opens the project daily report and sees derived rows built only from current unit reports in the permitted workflow states for the same project and date. Rebuilding is atomic and idempotent. Every section preserves row-level or multi-source provenance. Empty data, an actual zero, and an unknown value remain distinct — missing data never becomes a fabricated zero. General activities, issues, and visits are transferred as structured project-report records, not as text derived from markup in free text. Project-level overrides and the management opinion survive every rebuild. When a unit report is rejected, replaced, or corrected, exactly that unit's previous contribution is removed or replaced in the current summary, and corrected values can be fixed only in the source unit report.

**Why this priority**: This is the engine contract that makes every preceding section trustworthy; without atomicity, provenance, and the zero/empty/unknown distinction, the summary cannot be relied on for contractual use.

**Independent Test**: Build a summary from two contributing units, rebuild it three consecutive times, reject one unit's report, and rebuild again; verify identical results while inputs hold, the rejected unit's rows vanish without touching the other unit's rows, every retained row keeps its source link, and overrides are untouched.

**Acceptance Scenarios**:

1. **Given** an approved unit activity row, **When** the project daily report is produced, **Then** the activity appears with all required columns and a source link back to the unit report row.
2. **Given** unchanged inputs, **When** the summary is rebuilt repeatedly, **Then** the result is identical every time with no duplicate rows.
3. **Given** a failure occurs partway through a rebuild, **When** the process ends, **Then** the previously valid summary remains intact and no partially rebuilt content is exposed.
4. **Given** a section holds no contributions, a genuine zero, and an unknown value in different rows, **When** the summary is viewed, **Then** the three conditions remain visibly distinct and missing data is never filled with a fabricated zero.
5. **Given** project-level management opinion and site-status or weather overrides exist, **When** any rebuild runs, **Then** they remain unchanged.
6. **Given** a current unit report is rejected or superseded after contributing, **When** the summary is rebuilt, **Then** only that unit's previous contribution is removed or replaced and every other unit's contribution is untouched.
7. **Given** a user identifies an error in a derived project-report row, **When** they seek to correct it, **Then** the correction can be made only in the source unit report, and the derived row becomes read-only in the project report.

### Edge Cases

- A labor job title exists in more than one unit report for the same day: the aggregate retains every contributor and the drill-down lists each, so no attribution is lost.
- An equipment item has no stable identifier but a known type: it is aggregated by type; double-count protection applies by row, and identity-based deduplication applies only where a stable identity is reliably declared.
- A machinery status row has counts but no hours: status counts still aggregate; absent hours remain absent rather than becoming fabricated zeros.
- A reconciliation is requested for a receipt whose referenced warehouse document no longer exists or lacks values: the result is insufficient data, never a silent match.
- Sampling is declared but test information is incomplete: the pour record is not accepted as complete and no misleading quality-control link is created; making it complete requires the missing test data.
- A note's free text mentions issues or barriers in narrative form: without an explicit type it remains a general note and is not classified as an issue.
- A preserved override and a unit contribution conflict (for example, a site-status override against unit-reported conditions): the explicit override wins for its scoped field and the conflict does not silently discard either record's provenance.
- Two rebuilds run concurrently or a source report changes mid-rebuild: the outcome converges to one valid summary with the same guarantees as a single atomic rebuild, with no duplicated or orphaned contributions.
- An image attachment's file is renamed or mis-declared: the validation decision is based on the actual file being a JPEG or PNG within the limit, not only on its declared name, so disguised invalid files are still refused.
- A job-title lookup during aggregation encounters a title retired by a newer catalog version: historical rows keep resolving their original title evidence while new entries must use the effective catalog.
- Zero is provided as a completed quantity for an executed activity: the row is rejected because a provided quantity must be positive, distinguishing "nothing to report" (omit the row) from a measurement of zero.

## Requirements *(mandatory)*

### Functional Requirements

#### Executed-activity contract (Buildings, Electrical, Mechanical)

- **FR-001**: Each executed-activity row MUST include an approved, active project WBS activity, an activity description, a shift, an active project contractor, headcount, parcel, block, floor, location, a completed quantity, a unit, and optional notes; aggregation MUST reproduce all of these columns.
- **FR-002**: When a completed quantity is provided, it MUST be positive; zero and negative quantities MUST be rejected with an explicit, localized error.
- **FR-003**: The submitted WBS activity and contractor MUST belong to the same project as the report; identifiers from another project MUST be rejected with a permission or validation error.
- **FR-004**: Crew name and contractor MUST be recorded and displayed as separate concepts, and aggregation MUST NOT substitute one for the other.
- **FR-005**: An unrecognized shift value MUST NOT be silently remapped to another shift; it MUST be rejected or clearly marked as unknown.

#### Labor contract

- **FR-006**: Labor rows MUST record, per job title, the category (indirect or direct), present count, leave/absence count, associated contractor, and overtime.
- **FR-007**: Labor counts MUST be non-negative integers; negative counts MUST be rejected with an explicit error.
- **FR-008**: Man-hours MUST be reproducibly calculated using the project-approved rule associated with the project's reporting template; the same inputs MUST always yield the same result.
- **FR-009**: Indirect category totals, direct category totals, and an overall total MUST be calculable for output at any time.
- **FR-010**: The job-title catalog MUST be versioned and configurable at the project-template level; no fixed title counts (such as 34/32, 33/32, or 32/36) MAY be hard-coded as universal truth.
- **FR-011**: The catalog MUST support migration of legacy titles, explicit display order, and project-specific titles without losing historical title evidence.
- **FR-012**: When one job title contributes from multiple unit reports, the aggregate MUST retain every contributing source and MUST NOT attribute the total solely to the last unit.

#### Machinery and equipment contract

- **FR-013**: For every equipment type or stable equipment identifier, the product MUST record or derive total, active, ready-to-work, inactive, and under-repair counts for the reporting day.
- **FR-014**: Where operationally needed, operating, stoppage, and repair hours and the stoppage reason MUST be recorded with the equipment row.
- **FR-015**: A stoppage reason MUST be provided whenever stoppage hours exceed zero; rows without it MUST be rejected with an explicit error.
- **FR-016**: The total recorded time for one equipment item MUST NOT exceed 24 hours in a single day.
- **FR-017**: Stoppage reasons MUST be controlled, translatable values; values outside the controlled vocabulary MUST be rejected.
- **FR-018**: An equipment item with a stable identity MUST NOT be counted twice in one day's aggregation.

#### Materials contract

- **FR-019**: Material records MUST preserve receipts, issues/consumption, units, consumption location, supplier, and warehouse-document reference independently and simultaneously.
- **FR-020**: The main project daily-report materials table MUST display only real receipts, matching the reference output form.
- **FR-021**: The aggregation engine MUST mark an item as received only when it is a real receipt and MUST NOT blindly convert generic material rows into receipts.
- **FR-022**: Consumption and reconciliation MUST remain available in visible details or a drill-down from the daily report.
- **FR-023**: Reconciliation MUST compare against the specific warehouse document a record references, not merely the total historical inventory balance.
- **FR-024**: Reconciliation MUST produce explicit, traceable statuses — match, mismatch, and insufficient data — with the comparison anchored to the referenced document.

#### Concrete contract

- **FR-025**: Each concrete record MUST include description or grade, a positive volume, structural element or location, parcel, block, floor, batching plant, truck or delivery-note number, laboratory sample code, sampling state, and test-sheet count.
- **FR-026**: When sampling is declared, the required test information MUST be present and a traceable link to the corresponding quality-control work MUST be created.
- **FR-027**: Negative volumes and references to data belonging to another project MUST be rejected.

#### General activities, issues, visits, and HSE contract

- **FR-028**: A general activity MUST remain a structured row — description, location/building, quantity/volume, unit, and notes — and MUST NOT be converted into formatted text for storage.
- **FR-029**: Issues/barriers and project visits MUST be structured records with source unit, date, text, and display order.
- **FR-030**: A barrier MUST include an owner and a due date.
- **FR-031**: An HSE incident MUST include a severity and an immediate action and MUST create the required notification or follow-up task.
- **FR-032**: A general note MUST NOT be automatically classified as an issue unless it is explicitly typed as one.

#### Images and documents

- **FR-033**: Units MAY attach JPEG/PNG images up to 10 MB to a related activity.
- **FR-034**: Each attachment MUST preserve capture date, work front, source activity, source unit, and the file's project.
- **FR-035**: Files that are not valid JPEG/PNG within the size limit — including ZIP, EXE, and other invalid types or mis-declared types — MUST be rejected with explicit errors, and files MUST NOT be attached across projects.
- **FR-036**: The project daily report MUST offer an accessible image count with links per relevant section; the specification MUST NOT require a large gallery in the printable form without an approved need.

#### Aggregation rules

- **FR-037**: Only data from unit reports in the permitted workflow states for the same project and date — as established by the unit source-of-truth feature — MAY contribute to the summary; draft, rejected, superseded, other-project, and other-date data MUST contribute nothing.
- **FR-038**: Rebuilding MUST be atomic and idempotent: a mid-process failure MUST leave the prior valid summary intact, and repeated rebuilds with unchanged inputs MUST produce identical results without duplicate rows.
- **FR-039**: Every section MUST preserve row-level provenance, and every total or combined value from more than one source MUST preserve the complete multi-source provenance set.
- **FR-040**: Empty data, an actual zero, and an unknown value MUST remain distinct everywhere in the summary; missing data MUST NOT become a fabricated zero.
- **FR-041**: General activities, issues, and visits MUST be transferred into structured project-report records; markup or markers embedded in free text MUST NOT be the source of truth for structure.
- **FR-042**: Rebuilding MUST preserve project-level overrides and the management opinion.
- **FR-043**: Derived rows in the project report MUST be read-only to product users; content corrections MUST be made only in the source unit report and then flow through rebuild.
- **FR-044**: Rejecting or replacing a unit report MUST remove or replace only that unit's previous contribution in the current summary, leaving other units' contributions untouched.
- **FR-045**: Structure and display order of transferred general activities, issues, and visits MUST be preserved across rebuilds, including when multiple units contribute.

### Key Entities *(include if feature involves data)*

- **Executed-Activity Row**: A unit-owned, project-scoped activity record carrying the full site contract of FR-001 with its own stable identity for provenance.
- **Labor Row and Job-Title Catalog**: A per-title labor record (category, present, leave, contractor, overtime, computed man-hours) resolved against a versioned, project-template-level catalog that also carries display order and project-specific and migrated legacy titles.
- **Equipment Status Row and Equipment Identity**: Per-type or per-item daily status counts, optional operating/stoppage/repair hours, a controlled stoppage reason, and a stable identity used to prevent double counting.
- **Material Record and Warehouse-Document Reference**: Receipt and consumption data preserved independently with supplier, consumption location, unit, and the specific warehouse-document reference that anchors reconciliation.
- **Concrete Pour Record**: Grade/description, positive volume, structural location fields, batching plant, truck/delivery note, laboratory sample code, sampling state, and test-sheet count, with a traceable linkage to quality-control work when sampling is declared.
- **General Activity, Issue/Barrier, Visit, and HSE Incident Records**: Structured, ordered, source-attributed records; barriers additionally carry owner and due date; HSE incidents carry severity, immediate action, and generated notification/task linkage.
- **Field Image Attachment**: A validated JPEG/PNG file within the size limit, anchored to a source activity, unit, and project with capture date and work front.
- **Derived Summary Item**: A project-report row, counter, total, or structured record copied or computed from eligible unit-report rows, carrying complete provenance, distinct empty/zero/unknown semantics, and read-only presentation in the project report.
- **Project Reporting Configuration Extensions**: The versioned, effective-dated project-template data that supplies the job-title catalog (titles, order, migration mapping), the man-hour computation rule, the controlled stoppage-reason vocabulary, and any project-specific section defaults; existing required-unit configuration continues to govern completeness and remains governed by the unit source-of-truth feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every mandatory acceptance scenario of this feature passes end to end — from unit-page entry through aggregation to project-report viewing — with zero undocumented extrapolations.
- **SC-002**: Rebuilding the same summary at least three consecutive times with unchanged inputs yields identical content, row counts, ordering of structured records, provenance sets, and project-level overrides, with zero duplicate or stale derived items.
- **SC-003**: Across the permission and validation matrix, 100% of identifiers, rows, and attachments that belong to another project — activities, contractors, equipment, concrete references, and files — are rejected without storing any cross-project reference.
- **SC-004**: 100% of contractually invalid inputs — zero or negative completed quantities, negative counts, negative volumes, a stoppage without a reason, equipment time exceeding 24 hours, uncontrolled stoppage reasons, unrecognized shifts, unknown job titles, and invalid or oversized files — are rejected with explicit, localized errors and leave no partial data.
- **SC-005**: For every combined total with more than one contributing source, the drill-down lists 100% of contributing rows and reports; no total is ever attributed solely to its most recent source.
- **SC-006**: In machinery aggregation, every equipment item with a stable identity appears exactly once, and the five-status table values match the Machinery unit report for the day in 100% of acceptance cases.
- **SC-007**: The main materials table contains only confirmed real receipts; 100% of consumption records remain retrievable through visible details or drill-down, and every reconciliation result is anchored to a specific referenced warehouse document with a match, mismatch, or insufficient-data status.
- **SC-008**: After any rebuild, 100% of transferred general activities, issues, and visits retain their fieldwise structure, source attribution, and display order, with zero conversions to formatted text for storage.
- **SC-009**: In usability checks, a user who spots an error in a derived project-report row can reach the responsible source unit report through provenance in a single attempt, and every derived row is confirmed read-only in the project report.
- **SC-010**: Acceptance criteria are executed in a test-first manner: for each mandatory scenario, a failing behavioral check exists before the smallest production change that makes it pass, covering validation, authorization, idempotent aggregation, and the unit-to-summary browser end-to-end path.

## Assumptions

- The unit source-of-truth feature (032) already provides the canonical unit taxonomy, the unit page as the only authoring surface, report states and eligibility, current-version rules, the rebuild fingerprint and provenance foundations, and summary override preservation; this feature extends content contracts and aggregation of those contents, and does not reintroduce any standalone `/sub-reports` experience.
- The project-approved man-hour rule defaults to per-title standard shift hours for the present count plus overtime contribution, stored with the project's reporting configuration so each project can override it; the exact default formula is finalized during planning against the legacy catalog evidence.
- The initial job-title catalog content is seeded from the existing legacy title sets (including the 34/32, 33/32, and 32/36 variants as historical evidence) into versioned per-project catalogs; none of these counts remains a hard-coded constant.
- The controlled stoppage-reason vocabulary defaults to the five standard causes already documented — breakdown, lack of fuel, weather, no operator, and site obstruction — and project templates MAY extend it; all values remain controlled and translatable.
- A material row is a real receipt only when its warehouse-document reference or equivalent receipt evidence ties it to a warehouse receipt; generic rows remain non-receipt until they are classified, preserving the distinction between entered data and derived meaning.
- A stable equipment identity is declared explicitly (for example, a registered item or identifier); deduplication by identity applies only where such identity exists, and typed-only equipment aggregates by type.
- Sampling linkage reuses the existing quality-control work records rather than introducing a parallel QC store; the linkage requirement is traceability, not a new workflow definition.
- Image validation is content-based in addition to name-based: a mis-declared file is identified by its actual content, which makes disguised executables and archives rejectable regardless of filename.
- Missing concrete test-sheet counts or sample codes are defaults of "not provided" only when sampling is not declared; a declared sampling state makes them required.
- A barrier's due date may fall in the past at entry time (back-dated reality); the specification requires the fields' presence, not date-sequence validation, which can be added later without breaking the contract.
- Report header composition (employer, consultant, contract, report and page numbers, three work-shift clock hours, forecast and temperature display), final page design, printable/PDF and Excel-equivalent output, and signature areas are the third feature's scope and are intentionally not covered here.

## Dependencies

- The unit source-of-truth feature must be delivered first: canonical units, unit-page authoring, states, eligibility, current versions, and summary rebuild mechanics are its inputs and must not be re-created here.
- Project reporting configuration must be extendable to versioned catalogs and rules (job titles, man-hour rule, stoppage vocabulary) at the project-template level without breaking the existing required-unit configuration.
- Authoritative WBS activities, contractors, warehouse documents and references, quality-control work records, equipment registration with stable identities where applicable, and the notification/task infrastructure must be available and project-scoped.
- Attachment capability depends on the environment-dependent file storage service; verification must state explicitly what local tests do and do not prove when that service is unavailable.

## Out of Scope

- Reintroducing or retaining the standalone specialty-report route or any second authoring surface; the Specialty Units pages remain the only entry point.
- Final daily-report page design, printable/PDF and Excel-equivalent output, report numbering rules, page numbers, header field composition (including three work-shift clock hours, three-day weather forecast, and temperature display), and signature areas — the third feature's domain.
- Redefining unit-report states, permissions, segregation-of-duties, legacy report migration, or the required-units completeness model; those belong to the unit source-of-truth feature.
- Importing the sample workbook or adopting its data as operational content; it is a structural and sample-data reference only.
- New raw project-level daily-report authoring or editing flows; derived content remains read-only and correctable only via its source unit report.
