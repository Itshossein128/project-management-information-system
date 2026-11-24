# Data Model: B03 Export Projections

This design extends version-owned report evidence only where needed. It reuses the [B01 field mapping](../057-a1-b01-data-contract/contracts/daily-report-data-contract.v1.json) and [B02 lineage rules](../058-a1-b02-version-integrity/contracts/version-integrity-api.md). Export projections and download requests are transient.

## Daily report version

- Identity is the exact `DailyReport.id`, with project, report date, lineage, version, status, deletion flag, and current flag. The one-project/one-local-date rule applies to B01 contract data. Legacy data can retain multiple shift-specific records for a date.
- Project identity, preparer, contract version, presentation profile and numbering come from the selected report and its authoritative B01 sources. Keep the synthetic fixture label visible in validation artifacts. A missing stable project ID or actual start date yields unknown official numbering.
- An open correction creates a new current draft. Clone version-owned shift evidence and row provenance under the same B02 correction operation. Never carry prior approval attribution onto the draft as a performed action. Cancellation restores prior eligibility without editing the original report. Authorized exact-version reads remain available within the visibility policy.
- Use version-owned observations, authorized overrides and frozen forecast evidence when available. Keep observation, forecast, and override semantically distinct. For current previews, use the bounded B01 forecast cache and service. A missing forecast stays unknown. If a version lacks frozen forecast evidence, capture available evidence through the existing approval/snapshot flow for future versions and leave approved history untouched. Workbook rendering uses version-owned evidence and makes no external fetch per sheet. An approved historical version without captured forecast evidence reports unknown, even if a newer cache entry exists.

## Worked shift and manpower

- `DailyReportWorkedShift` belongs to one report version and stores canonical ID `1`, `2`, or `3` plus independently recorded nullable actual duration. Add nullable observed start/end timestamps to the version-owned row only when an authoritative upstream source cannot supply them. Use timezone-aware timestamps with local display, allowing overnight work. When both timestamps are present, an end before start is invalid. Do not infer duration from wall-clock time or infer either endpoint from duration.
- Historical rows may have one or both endpoints unknown. An unknown duration gives unknown person-hours. Keep recorded headcount, shift count, leave, overtime, and person-hours distinct. Distinct attendance is required before applying a unique-person or person-day label.
- Project catalog and B01 form profile are independent axes. Use the version's profile and titles. Under Shiraz, preserve the 34 indirect and 32 direct form positions and place extra/custom/historical titles in a labeled appendix. Keep separate contractor identities in the underlying rows and case-specific source totals visible.

## Operational rows and source details

- Activities retain WBS, shift, distinct contractor and crew, location, unit, and quantity. Equipment identity and source hours remain separate from derived totals. Materials use a receipt-only main section with separate document-scoped reconciliation. Keep structured issues, visits, HSE and attachments bound to their source rows and permissions.
- Preserve measured numeric zero and unknown distinctly. Blank/dash can render an unknown without changing the stored value. HSE type and severity use their stable codes with localized labels. All user-entered spreadsheet text remains literal.
- Concrete rows retain versioned provenance, source unit/report references, concrete field values, `lab_sample_code`, `test_sheet_count`, and same-project `qc_inspection` when present. Read existing authorized detail/provenance paths first. If authoritative mixer identity, lab sheet number or verified 28-day result linkage is absent, show unknown or unavailable with an applicable omission rationale. Extend the least existing source or linkage only where actual required evidence exists to capture. Sheet count, sample code, and sheet number are separate values. A generic inspection link alone establishes no 28-day result.
- Persisted/API sampling identifiers remain `sampling_declared` and `not_sampled`. Map them to localized display labels for **taken** and **not taken**. The first label records a declared sample. A blank, absent, or unrecognized historical value displays **unknown**. Do not write these display labels back or change canonical validation.

## Workflow attribution and fingerprint

- One displayed slot per applicable preparation, review or approval event of the selected report version. Use daily workflow records and unit status events, with event-scoped actor, timestamp, and verified organizational/project position. Distinguish a position from a permission role and from the slot caption.
- Extend existing event metadata or use narrowly scoped nullable evidence if no action-time role snapshot exists. Capture it with the existing action transaction and only from the position actually held/recorded for that action. A skipped stage stays empty. Historical missing fields stay unknown. Convert timestamps to the project-local timezone before computing the local calendar date and display time.
- The fingerprint is a deterministic digest of defined report/version and approval metadata. It does not attest row content or substitute for certificate-backed signing.

## Workbook selection and compatibility

- A range request holds authorized project ID, inclusive parsed dates and locale. Select eligible version IDs once. A worksheet belongs to one eligible date, keyed by a unique slash-free Solar Hijri label. No dates, worksheets or counts are manufactured. [Download contract](contracts/exports.md).
- Any new stored fields are nullable and additive. Existing rows, canonical IDs and approval histories remain valid. Test forward migration, legacy rows, and rollback behavior. Roll back new fields only after confirming how to retain newly captured evidence. No inferred backfill is planned.
