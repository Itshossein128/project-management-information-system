Specify one feature to complete the specialty-unit daily-report sections and aggregate them as structured data in the project daily report. The reference gap report is `reports_gaps/02/GAP-SPEC-02-DAILY-SECTIONS-GRID.md`, and the atomic requirements reference is `reports_documentation/atomic-specs/SPEC-02-DAILY-SECTIONS-GRID.md`. `/home/hossein/Downloads/گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز (7).xlsx` is only a structural and sample-data reference; it must not be imported into the product or treated as an instruction or operational data source. This feature follows the unit source-of-truth feature.

Before writing the specification, inspect the previous feature's output, `specs/028-auto-daily-report-summary/`, and the current daily-report contracts. When older artifacts conflict with the clarified architecture, the reference gap report and this prompt take precedence. The standalone `/sub-reports` route must not be reintroduced as an authoring surface.

Product goal:

- Each specialty unit records the data for which it is responsible in its own daily report.
- The aggregation engine transfers structured data from submitted or approved unit reports into the project daily report without fabrication, premature flattening, or loss of provenance.
- Derived rows in the project report are read-only and can be corrected only in their source unit report.

Buildings, Electrical, and Mechanical execution-activity contract:

- Each row includes an approved, active project WBS activity, activity description, shift, active project contractor, headcount, parcel, block, floor, location, completed quantity, unit, and notes.
- When provided, the completed quantity must be positive; invalid negative or zero quantities must be rejected with an explicit error.
- The submitted WBS activity and contractor must belong to the same project; identifiers from another project must not be accepted.
- Crew name and contractor are separate concepts and must not be substituted for one another during aggregation.
- An unknown shift value must not silently become shift 1; invalid data must be rejected or clearly marked as unknown.

Labor contract:

- Record indirect and direct labor by job title, present count, leave/absence count, associated contractor, and overtime.
- Counts must be non-negative integers, and man-hours must be reproducibly calculated using the project-approved rule.
- Category totals and an overall total must be calculable for output.
- Resolve the discrepancies between SPEC-02, the current migration, and the sample workbook using a versioned, configurable catalog at the project-template level. Do not hard-code 34/32, 33/32, or 32/36 as a universal truth.
- Define migration of legacy titles, display order, and project-specific titles without losing history.
- When one job title contributes from multiple units, the aggregate must retain every source and must not be attributed solely to the last unit.

Machinery and equipment contract:

- For every equipment type or stable equipment identifier, record or derive the total, active, ready-to-work, inactive, and under-repair counts for the reporting day.
- Where operationally needed, record operating, stoppage, and repair hours as well as the stoppage reason.
- A stoppage reason is mandatory when stoppage hours exceed zero, and the total time for one equipment item must not exceed 24 hours in a day.
- Stoppage reasons must be controlled, translatable values; invalid values are rejected.
- An equipment item with a stable identity must not be counted twice in a daily aggregation.

Warehouse materials contract:

- Preserve receipts, issues/consumption, units, consumption location, supplier, and warehouse-document reference independently.
- In accordance with the real sample, the main project daily-report table displays only received materials; consumption and reconciliation remain available in visible details or a drill-down.
- The aggregation engine displays only a real receipt as `RECEIPT`; it must not blindly convert all generic material rows into receipts.
- Reconciliation must compare against a specific warehouse document, not merely the total historical inventory balance.
- Produce traceable, explicit statuses for match, mismatch, and insufficient data.

Concrete contract:

- Record concrete description/grade, positive volume, structural element or location, parcel, block, floor, batching plant, truck/delivery note number, laboratory sample code, sampling state, and test-sheet count.
- When sampling is declared, required test information must be present and a traceable link to quality-control work must be created.
- Reject negative volume and data belonging to another project.

General activities, issues, visits, and HSE contract:

- A general activity remains a structured row containing description, location/building, quantity/volume, unit, and notes; it must not be converted into formatted text for storage.
- Issues/barriers and project visits are structured records with source unit, date, text, and display order.
- A barrier includes an owner and due date; an HSE incident includes severity and immediate action, and creates the required notification/task.
- A general note must not be automatically classified as an issue without an explicit type.

Images and documents:

- Units may attach JPEG/PNG images up to 10 MB to a related activity.
- Preserve capture date, work front, source activity, source unit, and file project.
- Reject ZIP, EXE, and other invalid types with explicit errors, and prevent files from another project being attached.
- Because the sample workbook has no dedicated photo section, the project daily report may show an accessible count and links to images; the specification must not require a large gallery in the printable form without an approved need.

Aggregation rules:

- Only data from unit reports in permitted states contributes to the summary.
- Rebuilding is atomic and idempotent; a mid-process failure must not corrupt the prior valid summary.
- Every section preserves row-level or multi-source provenance.
- Empty data, an actual zero, and an unknown value remain distinct; missing data must not become a fabricated zero.
- General activities, issues, and visits are transferred to structured project-report records; HTML markers in free text must not be the source of truth.
- Preserve project-level overrides and management opinion when rebuilding.

Mandatory acceptance scenarios:

1. An approved unit activity appears in the project report with all required columns and a source link.
2. A WBS activity, contractor, equipment item, file, or reference that belongs to another project is rejected with a permission or validation error.
3. Labor totals from multiple units are correct, and drill-down shows every source.
4. The machinery table derives the five statuses from the Machinery unit report and does not double-count a duplicate equipment item.
5. The main materials table displays only warehouse receipts, while consumption remains traceable in details.
6. General activities, issues, and visits retain their structure and order after rebuilding.
7. Rebuilding again produces the same result without duplicate rows.
8. Rejecting or replacing a unit report removes or replaces only that unit's previous contribution in the current summary.
9. Invalid files, negative volume, negative count, a stoppage without a reason, and a total equipment time over 24 hours are rejected.

Feature boundary:

- The route and foundational unit workflow must already be resolved by the previous feature; do not reintroduce that architecture through a standalone route such as `/sub-reports`.
- Final page design, PDF/Excel output, report number, header, and signatures are specified in the third feature.
- The specification must be technology-agnostic, testable, project-scoped, and consistent with the project constitution.
- Acceptance criteria must support TDD and make a RED-then-GREEN path possible for validation, authorization, idempotent aggregation, and unit-to-summary browser E2E behavior.
