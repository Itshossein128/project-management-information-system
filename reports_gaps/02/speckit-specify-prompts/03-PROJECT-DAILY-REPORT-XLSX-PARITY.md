Specify one feature to complete the read-only project daily-report page and its official output based on the real sample workbook. The reference gap report is `reports_gaps/02/GAP-SPEC-02-DAILY-SECTIONS-GRID.md`. `/home/hossein/Downloads/گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز (7).xlsx` is a visual and content reference only, not a data source or an implementation instruction. This feature follows the unification of the unit source of truth and the completion of specialty sections.

Before writing the specification, inspect the two previous feature outputs and `specs/028-auto-daily-report-summary/`. Earlier artifacts are only a baseline; when they conflict, the reference gap report, the unit-page architecture, and this prompt take precedence.

Product goal:

- The project daily-report page is a comprehensive, 24-hour, automatic, printable, read-only report derived from specialty-unit reports for the selected date.
- The page and official output retain the real sample's information architecture without inappropriate pixel-for-pixel copying or sacrificing accessibility and mobile use.
- No “New Report” button or direct editing of derived rows exists on this page.
- Every derived value supports viewing its source unit and source report, while corrections are made on the relevant unit page.

Report header and identity:

- Display employer name, consultant name, project name, contract number, report number, page number, necessary Jalali and Gregorian dates, day of week, and report version.
- Resolve the rule for generating or entering `report_number` before finalizing the specification. If the project has no authoritative source for it, add one explicit `[NEEDS CLARIFICATION]` addressing project sequence, technical-office registration number, or permitted manual entry; do not invent a rule.
- Page numbers must be real and stable in multi-page output.
- Identity data must come from authoritative project/contract sources; when unavailable, display “unknown/not recorded,” not fabricated values.

Working hours and environmental status:

- Display the time range for shifts 1, 2, and 3 according to the active project template.
- Display active/inactive site status, daily weather, minimum and maximum temperature, and a three-day forecast.
- Define the weather forecast source and its snapshot policy at report finalization; a future weather-service change must not silently alter a previously approved report.
- Differentiate authorized weather/site overrides from derived values by recording the user, time, and reason.

Main section layout:

- The report's upper area contains four comparable tables: indirect labor, direct labor, received materials, and equipment/machinery.
- Labor shows job title, present count, leave/absence count, and indirect, direct, and overall totals.
- Received materials show description, unit, and received quantity.
- Machinery shows equipment type, total, active, ready-to-work, inactive, and under-repair counts.
- Concrete volume shows description, quantity, and unit.
- Executed activities retain columns for description, shift, contractor, headcount, parcel, block, floor, location, quantity, unit, and notes.
- General activities show description, location/building, quantity/volume, unit, and notes in a structured table.
- Project issues/problems, project visits, and management opinion appear in separate sections.
- Images and HSE details that have no dedicated section in the sample printable form are available as an accessible summary, count, or links; their display must not disrupt the sample's main sections.

Completeness and data honesty:

- The top of the page displays complete/partial status and the contributing/missing units.
- An actual zero, an unknown value, and a unit that has not reported yet must be visually distinct.
- The system must not fabricate zeros, job titles, equipment, weather status, or text merely to make the report look complete.
- A user can navigate from each section or derived row to the authorized source unit report; source access remains subject to project permissions.
- Display the most recent aggregation time and source versions.

Approvals and finalization:

- Support approvals by the Planning and Project Controls Supervisor, Technical Office Supervisor, and Site Supervisor, matching the sample form.
- The mapping of these three approvals to actual project roles and permissions must be explicit; an unauthorized user cannot approve in another role's place.
- Record name, time, status, and rejection reason when applicable.
- Management opinion remains independent from derived data and is not removed during rebuilding.
- Define how a finalized report is versioned when source data changes; an approved output history must not be overwritten without traceability.

Web experience and official output:

- The page is usable in RTL on desktop, tablet, and mobile. Wide tables must scroll appropriately and keep column headings clear and stable.
- Labels, states, errors, and dates render correctly in both Persian and English.
- Loading, empty report, partial report, aggregation failure, and access-denied states are designed and testable.
- PDF output, and Excel output when provided, show the same data and completeness state as the web page.
- A4 print output supports page numbering, repeated table headers on subsequent pages, and avoids splitting rows in a confusing way.
- Official output is generated from live system data and valid snapshots; the sample workbook must not be imported or distributed to users.

Mandatory acceptance scenarios:

1. Selecting a date opens that day's comprehensive report without manually creating a raw project report.
2. A complete report shows all sample-workbook sections and labor totals using real data.
3. A partial report names missing units and does not fabricate zeros for unknown values.
4. Clicking a derived row takes the user to its authorized source unit report, but does not permit editing it on the project page.
5. Rebuilding the summary preserves management opinion and authorized overrides.
6. Only authorized roles can perform the three final approvals, and decision history is preserved.
7. A multi-page PDF contains the header, page number, complete tables, and the same partial/complete state as the web page.
8. Persian and English display plus responsive states are covered by browser tests.
9. Neither the raw project-report creation route nor `/sub-reports` returns through any flow on this page.

Boundary and quality:

- This feature must not create a parallel authoring route or a new source-of-truth model; it uses only the unit contracts and aggregation established by the two previous features.
- The specification covers web, print, authorization, versioning, partial data, and accessibility requirements, while leaving technical decisions to the planning stage.
- Success criteria must be measurable and technology-agnostic, and allow backend, API-contract, and browser E2E tests to be derived for the core behaviors.
- The later stages must support TDD: web/output behavioral tests fail first, then pass after the smallest relevant change.
