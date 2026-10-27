# Feature Specification: Discipline Sub-Reports Lifecycle and Validation

**Feature Branch**: `038-discipline-sub-reports`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "یک feature منسجم برای «ثبت، اعتبارسنجی و چرخه حیات سابریپورتهای تخصصی واحدهای اجرایی و دیسیپلینها (ابنیه، تأسیسات مکانیکی، برق، لولهکشی، تهویه مطبوع و نازککاری) بر اساس استانداردهای اکسل شیراز و انطباق با معماری کانونیکال» در پروژه ساختمانی"

**Reference artifacts**:
- `reports_documentation/atomic-specs/SPEC-05-DISCIPLINE-SUB-REPORTS.md`
- `reports_gaps/05/GAP-SPEC-05-DISCIPLINE-SUB-REPORTS.md` (covering gaps G01 through G08)
- `reports_documentation/01-core-requirements-and-excel-blueprints/مستندات فرمهای اکسل شیراز (FILE 5 و FILE 6)`
- `specs/032-unit-report-source-truth/spec.md`
- `specs/033-daily-sections-grid/spec.md`
- `specs/034-daily-lifecycle-lock/spec.md`
- `.specify/memory/constitution.md`

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record Daily Activity Execution Percentage and Validate Range (Priority: P1)

As a site discipline supervisor (Civil, Electrical, Mechanical), I want to record the daily progress percentage (`daily_percent` / `execution_percentage`) for individual activity rows, so that physical execution velocity is accurately captured in daily reporting according to engineering standards (Shiraz FILE 5 / FILE 6).

**Why this priority**: Without daily execution percentage on activity rows, physical progress velocity cannot be measured or distinguished from raw quantity, and existing data integrity is compromised (resolves G01 and G02).

**Independent Test**: Open the activity section of a draft unit report, create an activity row with a valid execution percentage (e.g. 15.5%), and verify it saves with two decimal places. Then attempt to enter out-of-range values (-5% or 105%) and verify that the system rejects the input with error code `percent_must_be_between_0_and_100` and displays a localized Persian/English message.

**Acceptance Scenarios**:

1. **Given** an authorized supervisor is editing a draft unit report on a selected date, **When** the supervisor inputs activity description, crew (foreman/worker counts), measurement unit, physical quantity, and a daily execution percentage of `15.50`%, **Then** the activity row is successfully saved with the execution percentage stored at two decimal places of precision.
2. **Given** an authorized supervisor enters a negative percentage (e.g., `-5.00`%) or a percentage greater than 100 (e.g., `100.01`% or `120.00`%), **When** the save mutation is executed, **Then** the system rejects the operation, the row is not persisted, and the error code `percent_must_be_between_0_and_100` is returned with a bilingual user-facing message ("درصد پیشرفت باید بین ۰ تا ۱۰۰ باشد" / "Execution percentage must be between 0.00 and 100.00").
3. **Given** boundary percentages of exactly `0.00`% or `100.00`%, **When** the row is saved, **Then** the system accepts and persists the values without error.
4. **Given** an activity row where physical progress percentage is not applicable or not measured on that day, **When** the supervisor leaves the execution percentage blank (null/empty), **Then** the activity row is saved successfully with an unset percentage without blocking the physical quantity.

---

### User Story 2 - Prevent Submission of Empty Sub-Reports (Priority: P1)

As a project manager and quality inspector, I need the system to strictly prohibit submitting empty sub-reports that contain no work rows, so that project daily aggregation and site statistics remain truthful and uncorrupted by hollow submissions (resolves G03).

**Why this priority**: Allowing empty sub-reports to be submitted allows fraudulent or meaningless records into daily rollup summaries, corrupting executive dashboards and project audit logs.

**Independent Test**: Create a new draft sub-report without adding any activity rows, workforce attendance rows, or consumable materials rows. Attempt to execute the submit action; verify the request is blocked with error code `cannot_submit_empty_sub_report`, the report state remains draft, and daily rollup aggregation is not triggered. Then add one valid row and confirm submit succeeds.

**Acceptance Scenarios**:

1. **Given** a unit sub-report in `draft` status containing zero recorded activity rows, zero workforce attendance records, and zero material consumption rows, **When** any user attempts to submit the sub-report, **Then** the request is rejected with a validation error code `cannot_submit_empty_sub_report` and a clear localized message ("امکان ارسال گزارش خالی وجود ندارد؛ حداقل یک ردیف فعالیت یا کارکرد وارد نمایید" / "Cannot submit an empty sub-report; at least one activity or workforce row is required").
2. **Given** a rejected empty submission attempt, **When** inspecting the sub-report in the database, **Then** its status remains strictly `draft`, no submission timestamp is recorded, and no automatic daily summary roll-up recalculation is invoked.
3. **Given** a draft sub-report containing at least one valid activity row with a non-zero quantity OR at least one workforce attendance row with positive headcount, **When** an authorized user triggers the submit action, **Then** the status transitions to `SUBMITTED`, submission metadata is logged, and the daily workshop roll-up summary is refreshed.
4. **Given** a draft sub-report that contains only general narrative notes or header comments but zero operational rows, **When** the user attempts to submit, **Then** the submission is blocked under `cannot_submit_empty_sub_report` because narrative notes alone do not constitute site execution evidence.

---

### User Story 3 - Electrical Installations Sub-Report with Discipline Separation (Priority: P1)

As an electrical discipline supervisor, I want an electrical reporting view that exposes electrical-specific measurement units (meters, points/fixtures, branches) and hides irrelevant civil/structural fields (such as concrete grade, batching, rebar testing), so that daily electrical installation reporting conforms to Shiraz FILE 6 standards.

**Why this priority**: Presenting civil engineering fields (concrete class, slump, laboratory sampling) on an electrical panel clutters the interface and introduces erroneous data entry in electrical reporting (resolves Shiraz FILE 6 parity and G04).

**Independent Test**: Open the Electrical unit reporting screen, verify civil-specific widgets (concrete sampling, slump test, batching plant) are hidden, add electrical activity rows with electrical units ("متر طول", "شعله / نقطه", "شاخه", "دستگاه تابلو"), specify shift 1–3, and submit successfully.

**Acceptance Scenarios**:

1. **Given** an electrical supervisor opens the daily report for the `electrical` unit, **When** viewing the activity and execution panels, **Then** civil-specific forms (concrete sampling, slump tests, mix design, batching) are completely hidden from the workspace.
2. **Given** an electrical supervisor creates an activity row, **When** selecting units of measurement, **Then** standard electrical units (linear meters, points/outlets, units/panels, branches) are presented as first-class options.
3. **Given** an electrical activity row is recorded across different site shifts (Shift 1, Shift 2, or Shift 3), **When** saved, **Then** shift number, crew name, electrician counts, and location parameters (zone, block, floor, riser) are preserved.

---

### User Story 4 - Mechanical & Plumbing Consumables with Quick-Selection Templates (Priority: P2)

As a mechanical and plumbing supervisor, I want to access a consumable materials section in the mechanical unit report with quick-pick suggestions for high-frequency plumbing and HVAC items (5-layer pipes, PVC/Plica pipes, welding fittings, elastomeric insulation), so that daily material consumption is tracked directly at the discipline level without switching to the general warehouse module (resolves G05).

**Why this priority**: Currently, materials logging is restricted solely to the warehouse unit, leaving mechanical supervisors unable to document installed pipes, fittings, and daily material placement.

**Independent Test**: Navigate to the Mechanical unit report, verify that the Materials section is accessible and enabled, open the item selection picker, verify standard mechanical items appear as quick-pick suggestions, select "لوله ۵ لایه" and enter quantity/location, and verify the record is saved.

**Acceptance Scenarios**:

1. **Given** an authorized user opens the report for the `mechanical` unit (or sub-disciplines `PLUMBING` / `HVAC`), **When** viewing the unit report sections, **Then** the Materials section is active, enabled, and editable in draft state (overriding the warehouse-only restriction).
2. **Given** a user is adding a material row in the mechanical report, **When** typing in the item name or clicking the quick-pick catalogue, **Then** high-frequency mechanical materials ("لوله ۵ لایه", "لوله پلیکا / فاضلابی", "اتصالات جوشی گاز", "عایق الاستومری حرارتی/برودتی", "لوله گالوانیزه") are presented for one-click selection.
3. **Given** a mechanical material item is selected from the quick list, **When** the supervisor inputs consumption quantity and installation zone, **Then** the row is persisted with reference to the project inventory catalog and linked to the daily discipline report.

---

### User Story 5 - Hydrostatic & Pressure Testing Integration with Quality Control (Priority: P2)

As a mechanical quality assurance engineer, I want to record hydrostatic pressure test results (test status, test pressure in Bar, duration, pipe segment) within the mechanical/plumbing sub-report, and have successful tests automatically create or link to a quality inspection record in the Quality/Risk management module, so that plumbing pressure certifications are auditable (resolves G06).

**Why this priority**: Plumbing and piping installations cannot be enclosed or commissioned without certified pressure test documentation. Automatically linking test evidence to quality inspection records prevents missing quality sign-offs.

**Independent Test**: In a mechanical sub-report, record a piping activity row, toggle "انجام تست هیدرواستاتیک / فشار", input test pressure (e.g. 6.50 Bar), specify holding duration and result "قبول / Passed", submit the report, and verify that a corresponding Quality Inspection record (`risk.Inspection`) is generated or linked with identical test metadata.

**Acceptance Scenarios**:

1. **Given** a mechanical or plumbing sub-report in draft state, **When** the supervisor documents piping installation and checks the "تست هیدرواستاتیک / فشار انجام شد" (Hydrostatic/Pressure Test Performed) toggle, **Then** the form requires input of test pressure in Bar (with decimal precision, e.g., 6.50 Bar), test duration (hours/minutes), tested segment/line, and test outcome (Passed / Failed).
2. **Given** a mechanical sub-report with a recorded successful hydrostatic test (`test_outcome = PASSED`), **When** the sub-report is submitted, **Then** the system automatically generates or links a Quality Inspection record in the quality management system (`risk.Inspection`) tagged with the discipline, tested zone, test pressure in Bar, and report date.
3. **Given** a hydrostatic test where the recorded pressure is zero or negative, **When** the user attempts to mark the test as performed, **Then** validation rejects the record with error code `invalid_test_pressure_value` ("فشار آزمون باید عددی مثبت باشد" / "Test pressure must be a positive number").
4. **Given** an approved report containing hydrostatic test records, **When** exported to PDF or reviewed in audit mode, **Then** the test pressure, holding time, and QA inspection linkage are prominently rendered in the technical section.

---

### User Story 6 - Subcontractor Crew Labor Hours Rollup (Priority: P2)

As a contracts and subcontractor manager, I want subcontractor crew allocations recorded in daily sub-reports to automatically compute and aggregate cumulative crew-hours (`(foreman_count + worker_count) * shift_hours`), so that daily labor billing, timesheets, and contractor claims can be cross-verified against site reports (resolves G07).

**Why this priority**: Subcontractor claims frequently dispute site presence and working hours. Deriving contractor labor directly from approved daily sub-reports provides tamper-evident evidence for interim payment certificates (IPCs).

**Independent Test**: Create an activity row, assign a recognized project subcontractor, input 2 foremen and 6 laborers on an 8-hour shift, submit and approve the report, and verify that the subcontractor's labor ledger reflects 64 person-hours for that date and project.

**Acceptance Scenarios**:

1. **Given** an activity row with an associated subcontractor reference (`contractor_ref`), **When** the supervisor inputs foreman count $F$ and worker count $W$ for an activity operating on shift duration $H$ hours (defaulting to 8 hours if unspecified), **Then** the system computes the activity labor effort as $(F + W) \times H$ person-hours.
2. **Given** a daily sub-report containing multiple subcontractor-executed rows is submitted and approved, **When** the contractor labor rollup is queried for that project and contractor, **Then** the cumulative person-hours are credited to the contractor's site attendance ledger.
3. **Given** an activity row is marked as direct labor ("نفر شرکت" / company staff), **When** saved, **Then** no external subcontractor labor credit is generated, and hours are routed to internal company headcount analytics.

---

### User Story 7 - Taxonomy Bridge: Sub-Discipline Tags within Canonical Units (Priority: P2)

As a site supervisor for specialized trades (Plumbing, HVAC, Finishing), I want to tag reports and activity rows with my specific sub-discipline (`PLUMBING`, `HVAC`, `FINISHING`, `STRUCTURE`) under the canonical 6-unit architecture (`mechanical`, `buildings`, etc.), and access these authoring workflows from both the Specialty Units menu and the Project Reports navigation, so that legacy sub-report capabilities are fully realized without fragmenting the single source of truth (resolves G04 and G08).

**Why this priority**: Resolves the architectural tension between the 6 canonical specialty units (`buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, `security`) and specialized sub-disciplines without creating orphaned routes or parallel data stores.

**Independent Test**: Open the Mechanical unit, select sub-discipline tag `PLUMBING`, record plumbing rows, verify that the report belongs to the canonical `mechanical` unit while carrying `sub_discipline = 'PLUMBING'`, and confirm it is visible and navigable both from `/projects/:id/units/mechanical/` and the project reports tab.

**Acceptance Scenarios**:

1. **Given** a user creating or filtering reports within the `mechanical` unit, **When** selecting sub-discipline, **Then** options `MECHANICAL` (General), `PLUMBING`, and `HVAC` are available.
2. **Given** a user working within the `buildings` unit, **When** classifying activities, **Then** sub-disciplines `CIVIL` (Structural/Concrete) and `FINISHING` (Architecture/Joinery/Gypsum) are selectable.
3. **Given** any sub-discipline report is saved and submitted, **When** project summary rollups occur, **Then** all rows roll up under their parent canonical unit without duplicating daily master report headers.
4. **Given** an end user navigating the web application, **When** accessing specialty reports, **Then** navigation paths from the Project Overview / Daily Reports tabs and the Specialty Units sidebar lead to the same canonical report workspace without dead links or orphaned components.

---

### Edge Cases

- **Zero vs. Unset Daily Percentage**: A daily percentage of `0.00`% means zero progress was achieved on an ongoing activity; leaving the field empty/null means progress percentage was not measured or tracked for that activity. The system MUST NOT coerce null to `0.00`%.
- **Multiple Contractors on Single Row**: If an activity is shared across teams, each distinct subcontractor crew MUST be recorded on a separate row to prevent ambiguous person-hour distribution.
- **Extreme Range Boundary Tests**: Values such as `0.001`% must round to `0.00`% or `0.01`% based on standard decimal rules, but values such as `-0.001`% or `100.001`% must trigger `percent_must_be_between_0_and_100`.
- **Sub-Report with Zero Rows on Re-Submit**: If a user submits a valid report, has it rejected, deletes all rows in draft mode, and tries to resubmit, the system MUST block submission with `cannot_submit_empty_sub_report`.
- **Concurrent Submissions**: If two supervisors simultaneously attempt to submit the same sub-report, the first transaction transitions the status to `SUBMITTED`, and the second attempt is safely rejected with `report_already_submitted` or invalid state transition error without duplicating summary rollups.
- **Hydrostatic Test Without Pressure Value**: If "Hydrostatic Test Performed" is toggled on, but the pressure value is left empty, submission of that row must fail with a validation message requiring the test pressure.
- **Sub-Discipline Filter Invariance**: Filtering by a sub-discipline tag must never omit shared workforce or weather conditions recorded at the parent canonical unit level.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support entering a daily execution percentage (`execution_percentage` / `daily_percent`) on activity rows for all discipline sub-reports.
- **FR-002**: The system MUST enforce that `execution_percentage` is within the closed interval `[0.00, 100.00]`. Any value outside this range MUST be rejected with error code `percent_must_be_between_0_and_100`.
- **FR-003**: The system MUST allow `execution_percentage` to be null/empty, treating it as unmeasured progress without blocking physical quantity or description.
- **FR-004**: When submitting a sub-report (transitioning from `DRAFT` to `SUBMITTED`), the system MUST verify that the report contains at least one active row in activities, workforce, or materials.
- **FR-005**: If a sub-report contains zero active rows, the submission request MUST fail with HTTP status 400 and error code `cannot_submit_empty_sub_report`, leaving the report in `DRAFT` status and preventing daily summary rollup execution.
- **FR-006**: Sub-report submission rejection for empty content MUST return bilingual error messages ("امکان ارسال گزارش خالی وجود ندارد" / "Cannot submit an empty sub-report").
- **FR-007**: The system MUST provide discipline-specific UI layouts where civil-specific sections (concrete grades, slump test, batching) are hidden from the electrical (`electrical`) reporting panel.
- **FR-008**: The electrical reporting view MUST offer electrical-appropriate units of measurement (linear meter, point/outlet, panel unit, branch) in quick selectors.
- **FR-009**: The system MUST enable the consumable materials section for the `mechanical` unit, allowing mechanical and plumbing supervisors to record daily installed and consumed materials.
- **FR-010**: The mechanical materials interface MUST supply quick-selection items for high-frequency mechanical materials, including:
  - لوله ۵ لایه (5-layer composite pipe)
  - لوله پلیکا / فاضلابی (PVC pipe)
  - اتصالات جوشی (Welding fittings)
  - عایق الاستومری حرارتی و برودتی (Elastomeric insulation)
  - لوله گالوانیزه (Galvanized pipe)
- **FR-011**: The system MUST support recording hydrostatic and pressure test data on mechanical and plumbing activity rows, including:
  - Test performed toggle (`is_hydrostatic_tested`)
  - Test pressure in Bar (`test_pressure_bar`) with at least one decimal digit precision
  - Test duration / holding period
  - Test outcome (`PASSED`, `FAILED`)
- **FR-012**: When a sub-report containing a successful hydrostatic test (`PASSED`) is submitted, the system MUST create or link a Quality Inspection record in the quality management module (`risk.Inspection`) with reference to the sub-report, date, zone, and test pressure.
- **FR-013**: The system MUST reject any hydrostatic test record where the entered pressure is less than or equal to zero Bar with error code `invalid_test_pressure_value`.
- **FR-014**: When an activity row specifies a referenced subcontractor (`contractor_ref`), the system MUST compute the total crew person-hours as `(foreman_count + worker_count) * shift_duration_hours`.
- **FR-015**: Upon sub-report approval, computed subcontractor person-hours MUST be logged to the contractor daily labor ledger for billing and audit verification.
- **FR-016**: The system MUST maintain the 6 canonical reporting units (`buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, `security`) as the primary architectural boundary.
- **FR-017**: The system MUST allow tagging activities and sub-reports with granular sub-disciplines:
  - Under `mechanical`: `MECHANICAL`, `PLUMBING`, `HVAC`
  - Under `buildings`: `CIVIL`, `FINISHING`
- **FR-018**: All sub-report views and actions MUST be consistently discoverable and navigable from both the Project Overview / Daily Reports section and the Specialty Units navigation sidebar, ensuring no orphaned routes or disconnected components exist.
- **FR-019**: All user-visible validation errors, table headers, quick-pick labels, and status badges MUST be localized in Persian and English in compliance with the system Constitution.
- **FR-020**: Sub-reports in `SUBMITTED` or `APPROVED` status MUST be immutable to standard edits; modifications MUST require reopening a tracked correction lineage per Feature 034 specifications.

---

### Key Entities *(data involved)*

- **Discipline Sub-Report (`SpecialtyUnitReport`)**:
  - Represents the daily reporting document authored by a specific discipline/unit for a given project and date.
  - Attributes: Project reference, Date, Canonical Unit (`buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, `security`), Sub-Discipline tag (`CIVIL`, `FINISHING`, `ELECTRICAL`, `MECHANICAL`, `PLUMBING`, `HVAC`), Status (`DRAFT`, `SUBMITTED`, `APPROVED`, `REJECTED`), Version, Lock status, Created/Submitted/Approved metadata.

- **Sub-Report Activity Row (`DisciplineSubReportActivity`)**:
  - Represents an individual work item executed during a work shift.
  - Attributes: Sub-report reference, Row number, Shift (1/2/3), Crew name, Foreman count, Worker count, Contractor reference (`contractor_ref`), Activity reference / WBS code, Location attributes (Parcel, Zone, Block, Floor), Measured quantity, Unit of measurement, Daily execution percentage (`execution_percentage`, range 0.00–100.00), Notes.

- **Hydrostatic & Pressure Test Record**:
  - Technical inspection metadata attached to plumbing/piping activities.
  - Attributes: Activity row reference, Pipe line/circuit identification, Test pressure in Bar (`test_pressure_bar`), Test medium (Water / Air / Nitrogen), Holding duration in minutes, Test outcome (`PASSED`, `FAILED`), Quality inspection linkage ID (`qc_inspection_id`), Technician / Inspector sign-off.

- **Consumable Material Row (`DisciplineSubReportMaterial`)**:
  - Details materials consumed or installed by the discipline during the reporting day.
  - Attributes: Sub-report reference, Material item reference / catalog code, Item description, Quantity consumed, Unit of measurement, Destination location / front, Origin warehouse / delivery reference.

- **Subcontractor Labor Ledger Entry**:
  - Derived labor hours credited to a subcontractor from daily site reporting.
  - Attributes: Project reference, Subcontractor reference, Date, Discipline, Source sub-report activity reference, Foreman hours, Worker hours, Total person-hours, Approval status.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of activity row inputs with execution percentages outside `[0.00, 100.00]` are rejected at API and UI boundaries with error code `percent_must_be_between_0_and_100`.
- **SC-002**: 100% of attempts to submit an empty sub-report (zero activity, workforce, or material rows) are blocked with error code `cannot_submit_empty_sub_report`, achieving zero empty-report pollution in daily master summaries.
- **SC-003**: 100% of submitted sub-reports containing valid hydrostatic test certificates automatically link or generate a valid Quality Inspection entry in `risk.Inspection`.
- **SC-004**: Mechanical and plumbing supervisors can locate, select, and record standard plumbing materials (e.g. 5-layer pipe, PVC) in under 15 seconds using quick-pick suggestions.
- **SC-005**: 100% of activity rows associated with a subcontractor automatically yield verifiable person-hour labor records calculated from crew headcount and shift duration upon sub-report approval.
- **SC-006**: Electrical supervisors report zero civil/concrete noise or extraneous fields when filling out the electrical daily report.
- **SC-007**: 100% of sub-report authoring screens are reachable within 2 clicks from either the Project Reports menu or the Specialty Units workspace navigation.
- **SC-008**: All user-facing error messages, field labels, and action notifications maintain 100% Persian and English bilingual coverage.

---

## Assumptions

- **Canonical 6-Unit Anchor**: The 6 canonical reporting units (`buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, `security`) defined in Feature 032 remain the top-level architectural grouping. Sub-disciplines (`PLUMBING`, `HVAC`, `FINISHING`, `CIVIL`) are modelled as secondary taxonomy tags rather than creating new top-level database tables.
- **Shift Duration Standard**: When shift duration is not explicitly specified on an activity row, standard site shift duration is assumed to be 8 hours.
- **Inspection Module Availability**: The Quality/Risk module (`risk.Inspection`) exists in the domain and accepts programmatic inspection creation or linkage from sub-reports.
- **Authentication and Isolation**: Tenant and project isolation rules specified in Constitution Principle I are strictly enforced on all sub-report and labor endpoints.
- **Offline / Sync Compatibility**: Data structures and error responses conform to Feature 036 and Feature 037 offline sync and validation conventions.
- **Subcontractor Master Data**: Project subcontractors referenced in activity rows exist in the project stakeholders or subcontractors registry (`projects.Stakeholder` / `subcontractors.Subcontractor`).
