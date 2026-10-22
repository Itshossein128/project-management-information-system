Specify one feature to correct the architecture for specialty-unit daily reporting and establish the project daily report's source of truth. The reference document is `reports_gaps/02/GAP-SPEC-02-DAILY-SECTIONS-GRID.md`. This feature must be completed before the next two features in this directory.

Before writing the specification, inspect `specs/028-auto-daily-report-summary/` and the related active artifacts. They are historical context and a baseline, but whenever they conflict, the explicit decisions in the reference gap report and this prompt take precedence—especially the removal of the standalone page and moving authoring into unit pages. The new feature must not preserve an obsolete architecture merely because it exists in an earlier spec.

Product goal:

- Each unit's specialty report must be created, edited, submitted, approved, or rejected only on that unit's page under the “Specialty Units” top-level menu.
- The standalone `/projects/{projectId}/sub-reports` page must not exist in the product.
- The project daily report must be an automatic, read-only summary of submitted or approved unit reports for the same date.
- No parallel workflows may remain for recording the same business concept.

Specialty-unit scope:

- The base set of units is Buildings, Electrical, Mechanical, Machinery, Warehouse, and Security/HSE.
- Define one official, canonical taxonomy for unit identifiers so that navigation, permissions, unit reporting, completeness calculations, and the project daily report use the same shared set.
- Legacy disciplines such as `civil`, `plumbing`, `hvac`, and `finishing` must not appear as new parallel units without an explicit migration decision. Mapping legacy data to official units must be explicit, testable, and preserve history.
- Each project must be able to declare, through its active template, which units are required for its daily report; completeness must not be hard-coded to three disciplines.

Unit daily-report workflow:

- On each unit page, an authorized user can select a date and open the report for that unit and date, or create its draft when it does not exist.
- For each project, date, and unit, only one current active version may exist, while version history is preserved.
- Support `draft`, `submitted`, `approved`, and `rejected` states.
- Only draft and rejected reports are editable.
- Submitting, approving, and rejecting require the corresponding project permissions, and an approver cannot bypass project segregation-of-duties rules.
- Record the rejection reason, and allow the unit user to correct and resubmit a rejected report.
- The unit page clearly shows report state, last-change time, preparer, submitter, approver, and rejection reason.

Source of truth and aggregation:

- Data entered on specialty-unit pages must be the sole source of truth for the project daily summary.
- Draft, rejected, deleted, or different-date unit reports must not contribute to aggregation.
- Summary rebuilding must be repeatable and idempotent; rerunning it must not create duplicate rows.
- Every derived row must retain the source unit report ID, source unit, and source row ID. Multi-source totals must retain all sources; the last source must not replace the complete provenance set.
- The daily summary must state the expected, contributing, and missing units according to the project template and truthfully show partial status.
- If a unit report is approved again after rejection or correction, rebuild the summary without retaining stale data.
- Authorized project-level overrides, such as management opinion, site status, or weather, must not be unintentionally removed during rebuilding.

Retire the obsolete user experience:

- Remove or update routes, navigation entries, CTAs, empty states, translations, and tests that make `/sub-reports` accessible.
- Opening the legacy URL directly must not display a report-creation page or data-entry form.
- The daily-reports page must not direct users to `/sub-reports`; specialty authoring is accessible only through the “Specialty Units” menu and the corresponding unit pages.
- Do not add a “New Report” button for the project daily report; direct creation of a raw project-level daily report remains prohibited.
- A legacy API or model may be retained temporarily only as an internal detail if it creates no parallel user workflow and has a clear migration/removal plan.

Migration and compatibility:

- Existing valid specialty-report data must not be lost. The specification must define mapping, backfill, duplicate-resolution, and rollback strategies.
- Preserve stable identifiers and links to existing daily reports wherever possible.
- No migration may apply a new constraint before inconsistent existing data is normalized.

Mandatory acceptance scenarios:

1. A user records and submits a Buildings report for a date on the Buildings page; after approval, the same data appears in that date's daily summary with correct provenance.
2. A draft or rejected report from a unit does not contribute to the summary, and that unit remains listed as missing.
3. After all template-required units are approved, the report is no longer partial.
4. Correcting and resubmitting a unit report replaces its contribution to the summary without duplicates or stale data.
5. A user without permission, and a user who belongs to another project, cannot view, create, submit, or approve a unit report.
6. `/sub-reports` is absent from navigation and UI, and opening it directly displays no specialty-report form.
7. Legacy data remains readable and traceable after migration.

Feature boundary:

- Do not complete the detailed contracts for specialty sections such as equipment, materials, concrete, and labor in this feature. Specify only the unit framework, workflow, taxonomy, migration, provenance, completeness, and source-of-truth integration.
- The full project daily-report page and printable output are specified in the third feature.
- The specification must be technology-agnostic, scenario-driven, testable, and consistent with the project constitution.
- Write scenarios so that the later tasks and implementation can follow TDD: first a failing behavioral test, then the smallest necessary change to make it pass.
