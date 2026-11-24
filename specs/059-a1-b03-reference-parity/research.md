# Research: B03 Reference-Form Parity

The approved B03 spec, B01/B02 contracts, and the existing workspace sources establish the planning baseline. The project's hybrid index is stale and its local embedding service was unavailable at specification review. The findings below use direct sources.

## R1. Version selection and authorization

**Decision.** Keep exact-version single-report downloads for authorized current, draft, and visible historical versions. Select one current, approved, non-deleted daily report per date for the official workbook. When a correction makes an older approval historical and leaves a current draft, that date has no eligible official sheet until approval or cancellation restores eligibility. Keep B02 provenance attached to the selected version.

**Rationale.** Daily downloads already use `get_object()`. B02's current-approved collection invariant is recorded for the activity log. The workbook adopts the same invariant as a B03 design decision. The current daily Excel action lacks the same explicit membership class as daily PDF. The unit resolver uses the all-objects manager, so both unit download actions need an explicit non-deleted guard. Sensitive exports and files require their existing specific permissions, including for observation accounts. [Daily views](../../apps/api/core/field_reports/daily_report_views.py), [unit views](../../apps/api/core/sub_reports/unit_report_views.py), [unit service](../../apps/api/core/sub_reports/unit_report_services.py), [B02 contract](../058-a1-b02-version-integrity/contracts/version-integrity-api.md).

**Alternatives.** Looking up the latest approval by date could select a superseded version. Applying collection policy to explicit UUID downloads would remove draft and visible history workflows. An export-specific permission hierarchy would duplicate the existing project policy.

## R2. One FILE 4 layout for one day and ranges

**Decision.** Separate sheet population and print settings from workbook serialization in the existing FILE 4 builder. The range action uses that sheet renderer once per selected day, names the sheet with its Solar Hijri date, and serializes the workbook once. A duplicate eligible legacy date produces a localized conflict. Use an initial configurable 31-day inclusive cap, checked before rendering.

**Rationale.** FILE 4 currently owns its workbook. Using a common sheet renderer keeps profile, wrapping, range, header repetition, formulas, and A4 fit aligned and avoids copying openpyxl objects from independently built files. A bounded, calendar-based range lets a full calendar month fit and avoids unexpectedly large synchronous downloads. Confirm representative performance before release. [FILE 4 builder](../../apps/api/core/field_reports/shiraz_file4_excel.py).

**Alternatives.** Copying complete workbooks can lose worksheet settings and links. A second range-only template duplicates corrections. Unbounded synchronous rendering has no predictable resource envelope.

## R3. Header and operational semantics

**Decision.** Use B01 contract/version/profile resolution and B02 version-bound metadata. Use recorded shift values, literal text, nullable quantities, and same-project source references. Turn stored QC codes into localized labels only at presentation. Read forecast evidence through the B01 service/cache with an unknown fallback. Keep approved artifacts tied to evidence captured for their own version.

**Rationale.** `DailyReportWorkedShift` stores canonical ID and nullable duration. No actual start/end source was found in the inspected daily, unit, or project models, so plan nullable version-bound observed start/end fields on that record if no authoritative upstream source is available. Capture them through the existing authorized worked-shift source flow or a narrowly scoped extension of that flow. Preserve overnight offsets and the independently recorded duration. The concrete model carries a lab sample code and a sheet count. A sheet number, mixer identity, or result must come from verified structured source or linked QC evidence. [Daily report models](../../apps/api/core/field_reports/models.py), [B01 contract](../057-a1-b01-data-contract/contracts/daily-report-data-contract.v1.json), [QC linkage](../../apps/api/core/sub_reports/services/qc_linkage.py).

**Alternatives.** Scheduled times, a zero default, matching a QC record by free text, and treating a sheet count as an identifier would invent evidence. Fetching live weather afresh during historical rendering could change an approved report.

## R4. Attribution and pagination

**Decision.** Use the daily workflow records and unit version status events for actor and timestamp; resolve the organizational title from authoritative evidence at the time of action. Capture any missing attribution for future actions on the existing transition path under its existing transaction. Use the report's project-local clock, with the B01 Iran local-time convention for applicable projects. Preserve unknown evidence on legacy versions. Reuse the daily PDF font, pagination and watermark primitives for unit PDF content, with per-version signature blocks.

**Rationale.** The existing daily signature renderer prints workflow captions and directly formats datetime values. Unit status events capture actor and time but do not snapshot a title. Reusing a current role as a historical title is inaccurate after a membership change. The current PDF uses A4 and per-page hooks, which can be reused for long discipline exports. [Daily PDF](../../apps/api/core/field_reports/pdf.py), [unit status history](../../apps/api/core/sub_reports/models.py), [B01 local-time convention](../../apps/api/core/field_reports/services/weather_forecast.py).

**Alternatives.** A fake reviewer, workflow caption as role, or inferred role would not satisfy FR-021. A separate document pipeline introduces duplicate bidi, layout, and watermark logic.

## R5. Discipline parity and workbook safety

**Decision.** Preserve FILE 5 numeric source values in the 0–100 range and write Excel fractions with percentage formatting. Preserve FILE 6's electrical schema. Share small print and literal-cell utilities across the existing builders. For unit PDFs, use each unit's own data and status.

**Rationale.** The existing FILE 5 writer already divides by 100 and leaves missing values blank. FILE 6 already excludes building-only fields. Row heights, page breaks, long bilingual text, and formula preservation need binary and visual evidence. [Discipline Excel builder](../../apps/api/core/sub_reports/shiraz_subreport_excel.py), [literal-cell helper](../../apps/api/core/field_reports/excel_safety.py).

**Alternatives.** Storing percent text breaks calculations. Applying text sanitation to internally authored formulas breaks totals. Rendering the project summary through the unit PDF endpoint would use the wrong data and approval state.
