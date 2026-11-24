# B04 Data Model

## Existing records

- **DailyReport** carries project, date, status, lineage, current and deletion flags. Date and status constrain the parent. Current reports are the list default. B02 maintains lifecycle and history.
- **DailyReportActivity** belongs to one report version. It carries source discipline, contractor identity, location dimensions, description, shift, headcount, quantity, recorded unit, measured flag and optional WBS/activity reference. Legacy records may lack normalized references.
- **DailyReportDerivedSource** binds a projected activity to its source row kind, row identity and source report/version. For derived summaries, match the projected activity as evidence of one eligible source row and keep version-bound provenance. A missing value cannot satisfy a selected dimension. Verify the projection against the sources used by the existing rollup.

## Derived selections and summaries

- **Daily-list selection** is project scope, report-level filters, and an optional one-row predicate for selected discipline, contractor and block. The predicate applies only when one or more of these dimensions is selected. Separate rows cannot collectively satisfy it. Each parent appears once. Use date descending and a unique tie-breaker for stable pages.
- **Activity selection** is project scope, B02 current/non-deleted records, official or explicit preview policy, and activity predicates. Values within an existing multi-select dimension are alternatives. Across dimensions, all supplied predicates apply to the same row. Page state selects a slice of the ordered result.
- **Full-result summaries** contain eligible row count, sum of recorded activity headcounts, and per-unit measured totals and counts. An amount contributes when the row is measured and has both amount and unit. An all-unknown unit group has a null total and a measured zero has a numeric zero. Count unknowns with missing units separately. Keep incompatible units separate.
- **Cache identity** uses authorized project, selection, page and server version. Approval invalidates older activity results and totals through the existing version mechanism. Avoid mixing results from different database snapshots within one response.

No persistent entities are added by the design. B01 and B02 continue to own source eligibility, lifecycle and retention.
