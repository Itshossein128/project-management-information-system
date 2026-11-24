# Feature Specification: A.1 / B04 — Filters, Result Sets, and Totals

**Feature directory** `specs/060-a1-b04-filters-totals`
**Created** 2026-11-21
**Status** Clarified and ready for planning after Supervisor review.
**Input** [B04 source prompt](../../output/a1-requirements-2026-11-18/speckit-prompts/04-b04-filters-totals.md). Delivery item A.1.03. B04 owns E11–E14 and consumes the B02 E15 and B01 D05/D07 rules.

## Clarifications

### Session 2026-11-22

- Q: How do discipline, contractor, and block filters match activity sources within one daily summary? → A: When any discipline, contractor, or block filter is selected, a daily summary matches those filters only if one eligible activity source row satisfies them all. Exclude summaries whose matches are split across source rows. Return each matching logical daily report once. [Ratified B01 data contract](../../apps/api/core/field_reports/contracts/daily_report_contract_v1.json)

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Share and recover a filtered daily reports list (P1)

A technical-office engineer shares a daily list with a resident supervisor so they can review the same reports without reconstructing the filters. Exercise the list independently with two authorized members and the two-summary fixture in scenario 3.

1. **Given** reports covering different dates, statuses, disciplines, contractors, and blocks, **when** a member applies those filters together and chooses a page, **then** the visible controls, list request, URL, and resulting page represent the same selection. A second authorized member with equivalent report access recovers the same selection, page, and report identities from the shared link.
2. **Given** two distinct filter states, **when** either member reloads or navigates back and forward, **then** the browser restores each recorded selection and page. Any download offered for that filtered daily list uses the same authorized report selection. Existing individual-report downloads retain the identity of their selected report.
3. **Given** two daily summaries in the selected date range and status, with two eligible activity source rows each, the first summary has two rows matching CIVIL, Contractor A, and Block 1. The second has a CIVIL row for Contractor A in Block 2 and a CIVIL row for Contractor B in Block 1. **When** a member selects CIVIL, Contractor A, and Block 1, **then** the first summary appears exactly once and the second is excluded. The shared URL and any offered filtered list download return the same summary selection.

### User Story 2 — Review and export an operational activity selection (P1)

A project controls engineer and auditor use a shared activity-log link to inspect evidence and reconcile the complete Shiraz FILE1 download. Exercise this flow independently with two authorized members, an outsider, and current, historical, and deleted records.

1. **Given** the same authorized project and unchanged data, **when** two members open the same link, reload, change page, and navigate back or forward, **then** both recover the recorded filters and page, and paging only changes the visible slice. Downloading FILE1 from either page yields the same complete set of filtered activity rows with the existing reference columns.
2. **Given** a foreign-project identifier in a direct request or shared URL, **when** a member opens the list, filter choices, totals, or download, **then** no foreign-project values, counts, or rows are disclosed and the selection cannot silently broaden to an unrestricted result.
3. **Given** two approved versions in one lineage, a deleted row, and a current draft, **when** the official log and FILE1 are opened, **then** they include eligible rows only from the current approved version. The existing preview may include current non-approved rows under B02, while historical records remain accessible through the separately authorized version history.
4. **Given** a newly approved report with multiple activities, **when** the user opens the matching operational log after approval, **then** all matching activities are individually queryable and visible within one second with their date, discipline, work front and quantity. Prior results must stop serving the old selection on approval.

### User Story 3 — Reconcile full totals from any page (P1)

A project manager compares the activity-log totals with FILE1 to certify the work reported within a selection. Exercise this independently with the 51-row fixture described below.

1. **Given** 51 eligible filtered rows with 50 per page and a control value of one per row for summed activity-row headcount, **when** the reviewer changes between the 50-row page and the one-row page, **then** the count and headcount sum both stay 51 and the complete download contains exactly 51 eligible activity rows.
2. **Given** measured m² and m³ rows, an explicit measured zero, an unset quantity, and an unmeasured legacy row, **when** the reviewer compares the row display, full totals, and FILE1, **then** totals are separate per measurement unit, valid measured zero is numeric, and unknown values remain distinguishable from zero and outside numeric sums.
3. **Given** two contractors reporting the same job title, **when** the reviewer selects either contractor and then both, **then** each selection retains the correct contractor identity and row counts. The combined labor figure is labeled as a sum of activity-row headcounts in Persian and English. Unique-attendance or person-day figures require their own evidence under D07.
4. **Given** the US-EX-04 case of CIVIL, «آرماتوربند الف», and the last month, **when** the auditor applies the combination, **then** matching rows and their separate measurement-unit totals appear in under one second on documented data and environment.

### Edge Cases

- No matching rows produce count zero and no measured quantity totals. A unit with only unknown measurements remains distinguishable from a measured total of zero.
- A measured flag with no amount remains unknown in read-only reporting. A legacy amount on a row marked not measured is presented as unknown. B01 owns submission validation.
- A row matching multiple selected values appears once. Stable data yields consistent pagination without omissions or duplicate rows.
- When a selection changes, the new result opens on its first page; browser history preserves the prior selection and page. Shared-link equivalence assumes unchanged data and equivalent applicable permissions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001** — Daily reports MUST support start date, end date, report status, discipline, contractor, and block as in FR-016. The visible filters, URL, list requests, and filtered download where offered MUST use the same filter meanings. Date and status describe the daily report. When any discipline, contractor, or block filter is selected, a daily summary matches those filters only if one eligible activity source row satisfies them all. Exclude summaries whose matches are split across source rows. Return each matching logical daily report once. (Story 1)
- **FR-002** — Activity log MUST use the same filter meanings in controls, URLs, list requests, totals and FILE1. It MUST support date range, discipline, parcel, zone, block, subcontractor, and pagination, with multi-select for discipline and parcel. It MUST support filtering and display coverage for the twelve FILE1 fields identified by 039 SC-006, including floor, location detail, activity description, shift, headcount, quantity, unit and report reference as applicable to those fields. Activity descriptions and the recorded date, discipline, work front, and quantity MUST be discoverable through search or their filters. It MUST support the source's WBS/activity-code, approval-status and work-location selection in the activity-log context under FR-005. Selection by contractor identity MUST distinguish contractors with identical job titles. (Stories 2 and 3)
- **FR-003** — Both views MUST restore filters and pagination from shared or bookmarked URLs, reloads and back/forward navigation for members with equivalent access to the same unchanged data. Project authorization MUST apply to direct list, filter-option, aggregate, and export requests and to project-specific filter values. Invalid or foreign references MUST prevent unintended broadening. (Stories 1 and 2)
- **FR-004** — The activity log MUST preserve the flat ACTIVITY row representation and existing Shiraz FILE1 columns, including source discipline, parcel, block, floor, location detail, activity description, shift, subcontractor, headcount, quantity, unit and report reference. FILE1 MUST export every eligible filtered row independently of page or page size. Approval MUST immediately invalidate stale operational results for the project. (Story 2)
- **FR-005** — List, operational totals, and FILE1 MUST inherit the B02 current-approved policy and exclude deleted records. An existing explicitly selected preview remains current-only and may include non-approved data under B02. Historical versions MUST stay in the authorized history view and outside operational selections and totals. Status filtering MUST operate within the selected policy. (Story 2)
- **FR-006** — The service providing filtered results MUST supply the total eligible row count and summaries computed across the entire authorized filtered activity set before pagination. The log MUST prominently display those totals and separately identify quantities by recorded measurement unit and measurement state. Only measured values with a recorded amount and unit contribute to a unit total. UI and FILE1 MUST distinguish numeric zero from unset or not-measured values under B01, including legacy records. The UI MUST use the localized unset presentation where the B01 contract applies. (Story 3)
- **FR-007** — Display the raw sum with a bilingual label identifying it as the sum of activity-row headcounts. Preserve distinct contractor identities and the B01/D07 meanings of persons, person-shifts, person-days and person-hours. Report-derived person-hours depend on actual shift duration under B01. (Story 3)
- **FR-008** — On a documented dataset and environment, applying the US-EX-04 combined filter MUST show matching records and full measured totals per unit in under one second, measured from application to visible results. This is separate from the approval-to-visibility criterion in FR-004. (Story 3)

### Key Entities

- **Logical daily report** — One project-local day summary with independent status, versions, and eligible source evidence.
- **Activity row** — A recorded item of work associated with an eligible report version and with recorded filter dimensions, contractor identity, headcount and measurement state.
- **Filtered selection** — The project, access scope, version policy, and criteria that determine membership. Page determines the visible slice.
- **Full-result totals** — Row count, activity-row headcount sum, and measured quantity totals and unknown states by unit for the selection.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** — Two authorized members reproduce 100% of filter selections, report or row identities, and page state on both views across shared link, reload, and back/forward. The Story 1 fixture yields exactly one occurrence of the summary with an eligible row satisfying all selected dimensions and zero occurrences of the split-row summary. All project isolation attempts disclose zero foreign values or records. (FR-001–FR-003)
- **SC-002** — With 51 matching rows and 50 per page, the two pages contain 50 and one unique eligible rows. Count and control headcount sum are 51 on both pages. FILE1 contains exactly those 51 rows with the reference columns, and per-unit measured totals computed from the workbook agree with the result totals on both pages. The fixture includes m², m³, measured zero, unset and legacy not-measured quantities, two approved versions in one lineage, and two distinct contractors with a shared job title. (FR-004–FR-007)
- **SC-003** — Across the fixture, both languages distinguish every measured zero from every unknown quantity, no incompatible units are combined, no headcount sum is labeled as unique people or person-days, and no historical/deleted row contributes to the official list, FILE1 or totals. The B02 preview and history controls pass their separate eligibility expectations. (FR-005–FR-007)
- **SC-004** — Document the fixture size and data window, browser, environment and timing method. All eligible activities of the newly approved report are visible within one second of approval, and the US-EX-04 filter scenario displays matching rows and totals in under one second after applying the combination. An authoritative amendment is required to change either source criterion. (FR-004, FR-008)

## Assumptions

- Acceptance comparisons use a stable dataset between requests and members with equivalent project permissions. Expected identities and totals are computed from the fixture independently of the displayed page. The 51-row fixture is controlled evidence. B05 owns broader independent reconciliation and B06 owns employer final acceptance.
- B04 covers filtering and totals for the daily list and Activity Master Log, including the FILE1 selection. B03 owns FILE4 presentation and date-range workbook, discipline exports and PDFs. A.8 owns wider operations, offline and resources, A.3.C owns communications, A.10 owns general and periodic reporting, and A.12 owns comprehensive deployment and training. Any effect on this package's project isolation, source integrity or result parity remains in scope.
- [Constitution](../../.specify/memory/constitution.md) principles I–III and VI apply to authorization, consistent data and locale, and verification.

### Dependencies

- **B01 (hard dependency)** — The B01 baseline establishes C02/D05 and D07 semantics. The ratified `daily_summary_activity_filter` contract entry governs FR-001. B04 acceptance verifies the same-row match and split-row exclusion. [B01 specification](../057-a1-b01-data-contract/spec.md), [data contract](../../apps/api/core/field_reports/contracts/daily_report_contract_v1.json), and [historical Stage 5 QA](../../output/a1-b01-stage5-qa-verification-2026-11-19.md).
- **B02 (hard dependency)** — [Version contract §5](../058-a1-b02-version-integrity/contracts/version-integrity-api.md#5-official-activity-master-log-contract-def-b02-05-e15-b04-handoff) and [Stage 5 QA §3](../../output/a1-b02-stage5-qa-verification-2026-11-19.md) record current-approved eligibility, current-only preview and history separation. B04 re-verifies E15 after its filters and totals extend that behavior.
- **B03 (sequence predecessor)** — [Specification](../059-a1-b03-reference-parity/spec.md), [export contract](../059-a1-b03-reference-parity/contracts/exports.md), [implementation evidence](../059-a1-b03-reference-parity/implementation-evidence.md) and [Stage 5 QA](../../output/a1-b03-stage5-qa-verification-2026-11-21.md) record DEL-01 through DEL-04 verification and closure of the eight B03 defects. Read these as predecessor evidence. FILE1 result parity belongs to B04.

### Scope decisions carried forward

Read the original wording for all ten decisions in the [Stage 1 register](../../output/a1-requirements-2026-11-18/scope-decisions.md) and their later B01 dispositions in the [B01 contract](../../apps/api/core/field_reports/contracts/daily_report_contract_v1.json). B04 applies these dispositions:

- **C01** preserves the derived project summary and unit-source ownership. **C02** resolves the historical positive-only wording for measured activity zero, applied by FR-006. **C03** preserves one report per local project day and canonical worked shifts with actual duration, applied by FR-001, FR-004 and FR-007.
- **C04** preserves contractor and catalog identity alongside B03's selectable 34/32 profile and appendix. **C05** preserves B03's single-day formats and date-range workbook scope. **C06** preserves attribution and metadata fingerprint under B03. **C07** preserves discipline PDFs under B03. **C08** preserves B03's official numbering, observed weather sources and forecasts. None introduces a new FILE1 presentation requirement.
- **C09** preserves independent source and summary approval states. FR-005 applies the B02 report-version rule. **C10** preserves the A.3.C and A.10 ownership boundaries.

### Traceability and disposition

Source line references use the Stage 1 audit manifest at `f41fc378ebfe8a5d227b1e4b34dc85de5aaf3d8a` (2026-11-18). The 162 tests, two passing controls and six strict XFAIL results are historical evidence. [Stage 1 audit](../../output/a1-requirements-2026-11-18/requirements-and-delivery.md), [clause catalog](../../output/a1-requirements-2026-11-18/source-clauses.md), [atomic coverage](../../output/a1-requirements-2026-11-18/atomic-coverage.md) and [ownership map](../../output/a1-requirements-2026-11-18/speckit-prompts/coverage.json) supply provenance.

- **E11** — `specs/039-auto-daily-rollup/spec.md:187` FR-009 preserves ACTIVITY fields and rows, and `:189` FR-011 and `:215` SC-005 preserve approval freshness. Story 2, FR-004, SC-002 and SC-004. `specs/044-shiraz-excel-parity-pdf/spec.md:199` FR-018 preserves full FILE1 output and requires filter and total parity in evidence. Stories 2–3, FR-004, SC-002.
- **E12** — `specs/044-shiraz-excel-parity-pdf/spec.md:197` FR-016 closes the filter and URL coverage gap using the ratified B01 rule for matching one eligible source row. Story 1, FR-001/003, SC-001.
- **E13** — `specs/039-auto-daily-rollup/spec.md:188` FR-010 preserves discipline/parcel multi-select and `:216` SC-006 requires complete FILE1 filter and display coverage. `specs/044-shiraz-excel-parity-pdf/spec.md:198` FR-017 preserves persisted dimensions and `:222` SC-004 verifies same-member and second-member recovery and fills any navigation gaps. Story 2, FR-002/003, SC-001.
- **E14** — `specs/044-shiraz-excel-parity-pdf/spec.md:200` FR-019 closes the full-selection aggregation gap and applies the B01 D07 label in place of the source's parenthetical man-days wording. Story 3, FR-006/007, SC-002/003.
- **E15** — [Stage 1 E15](../../output/a1-requirements-2026-11-18/requirements-and-delivery.md) and `specs/058-a1-b02-version-integrity/contracts/version-integrity-api.md:107` preserve B02 ownership and version eligibility. Story 2, FR-005, SC-003.
- **D05** — Preserve zero/unknown in activity results and FILE1 (Story 3, FR-006, SC-003) from `specs/007-daily-report-gaps/spec.md:129,152` FR-010/SC-004 and `reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:63` FR-DR-010. Save/submit and material semantics stay with source owners. `specs/033-daily-sections-grid/spec.md:187,272` FR-002/SC-004 yield to C02 for measured activity zero, with other source validation retained by its owner. `specs/034-daily-lifecycle-lock/spec.md:97–99,118` FR-011–013/SC-004 and `specs/036-validation-codes-unset-semantics/spec.md:84–90,109–110` FR-006–012/SC-002–003 preserve read-only zero and bilingual unset presentation, including inconsistent legacy quantities. B01 retains submission validation and editable views.
- **D07** — `specs/033-daily-sections-grid/spec.md:196` FR-008 preserves the B01 reproducible person-hour rule. B04 applies the row-sum label, with actual-duration calculations and unique-attendance policy retained by B01. Story 3, FR-007, SC-003.
- **US-AG-06** — `reports_documentation/atomic-specs/SPEC-06-AUTO-DAILY-ROLLUP.md:129` preserves each eligible activity as a searchable, filterable independent row after approval, including date, discipline, work front and quantity. FR-002/004, Story 2, SC-004. B02 retains version/history policy. B04 specifies the observable projection and approval visibility.
- **US-EX-04** — `reports_documentation/atomic-specs/SPEC-11-SHIRAZ-EXCEL-PARITY-PDF.md:79` preserves the combined CIVIL, named contractor and last-month scenario with the sub-second threshold and unit-specific totals (Story 3, FR-002/006/008, SC-004), and exact link recovery for another authorized member (Stories 1–2, FR-003, SC-001). WBS, status and location apply within the activity reporting scope under FR-002/005. The generic all-reporting-pages scope belongs to the owner of each reporting surface.

### Historical QA and current evidence

Use the [local defect register](../../output/a1-requirements-2026-11-19-stage1-b04-qa-findings.md) and [machine-readable findings](../../output/a1-requirements-2026-11-19-stage1-b04-qa-findings.json). The detailed prose in the report labels some issues differently from its register. Use the local table and JSON for DEF-B04-02/04/05 and record both meanings of DEF-B04-06.

- **DEF-B04-01** — Compare totals across the 50/1 pages (FR-006, SC-002). Historical reproduction recorded count 51 and page size 50.
- **DEF-B04-02** — Verify the service supplies whole-selection totals including unit boundaries and unknown-versus-zero cases (FR-006, SC-002/003).
- **DEF-B04-03** — Verify both filter coverage and link, reload, paging, and back/forward navigation across views (FR-001–FR-003, SC-001). This also covers the delivery note's navigation meaning for DEF-B04-06.
- **DEF-B04-04** — Verify the D07 row-sum label in both languages (FR-007, SC-003).
- **DEF-B04-05** — Verify that authorized visible selection and complete FILE1 agree by row identity and totals (FR-004/006, SC-002).
- **DEF-B04-06** — Verify historical-version exclusion with the B02 gate even after filters are applied. The local report classifies it as a regression risk. The B02 evidence closes its original gate and the B04 fixture rechecks it (FR-005, SC-003).
- Current source inspection found that activity list and FILE1 already share the activity selection and B02 version gate at `apps/api/core/field_reports/report_views.py:100,136` and `apps/api/core/field_reports/services/activity_log.py:11`. The list produces a page response, the activity UI sums displayed rows at `apps/web/src/app/routes/project-activity-log.tsx:129`, and the daily list request filters date/status at `apps/api/core/field_reports/daily_report_views.py:175`. Preserve proven shared behavior and verify the listed gaps at B04 acceptance. The activity URL history risk appears at `apps/web/src/app/routes/project-activity-log.tsx:87` and still requires browser verification.

### November 21 QA findings

The November 21 B04 report records `qa_failed`. Use the report date with each defect ID because the November 19 register uses DEF-B04-04 and DEF-B04-05 for different findings. [November 21 QA report](../../output/a1-requirements-2026-11-21-stage1-b04-qa-findings.md) and [defect data](../../output/a1-requirements-2026-11-21-stage1-b04-qa-findings.json).

- **DEF-B04-01 and DEF-B04-02** — Page totals changed from 50 to 1, and the list response lacked whole-selection totals. FR-006 and SC-002 require the count and control headcount sum to stay 51 on both pages and the full FILE1 export to reconcile.
- **DEF-B04-03** — The daily list lacked discipline, block, and contractor filters. FR-001, FR-003 and SC-001 require shared behavior across the controls, list, and URL, with the multi-source matching outcome governed by B01.
- **DEF-B04-04** — The activity display reduced unset or unmeasured values to zero. FR-006 and SC-002/003 require those values to remain distinct in the result and FILE1.
- **DEF-B04-05** — The activity display labeled the row headcount sum as man-days. FR-007 and SC-003 require the bilingual row-sum label and preserve B01 labor semantics.

Both November QA registers remain acceptance inputs. The Stage 3.1 review checks specification traceability only.
