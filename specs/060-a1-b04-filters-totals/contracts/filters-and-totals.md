# B04 Reporting Interface Contract

All API paths are relative to `/api/v1/projects/{project_id}/`. Keep existing authentication and project permission dependencies, including additional export permission where already required. Apply project filtering to options and identifier resolution. Invalid or foreign scoped identifiers produce validation failure or an empty selection, with no foreign data or fallback to an unrestricted selection. Localize validation messages.

## Daily reports

- `GET daily-reports/` retains the pagination envelope and existing report filters. Add `discipline`, `contractor` (project contractor ID) and `block`. Apply date and status to the report and all selected activity dimensions to one eligible source row. Return exactly one result per matching logical summary.
- Daily list URL state mirrors its API filters and page. If a filtered-list download is exposed, it uses the same report selection. The existing separate B03 date-range workbook uses its explicit range. Preserve individual Excel/PDF report identity and access checks.

## Activity log

- `GET activity-log/` and `GET activity-log/excel/` accept identical selection criteria. Retain date range, `discipline` and its `source_discipline` alias, `parcel`, `zone`, `block`, legacy `subcontractor`, `floor`, `shift`, `activity_id` and `approved_only`. Continue accepting comma-separated discipline and parcel selections. Use deterministic alias precedence consistent with the existing API.
- Proposed additive filters are `contractor_id` for exact identity, `status` within the B02 visibility policy, `location` for location detail, `q` for description and WBS/activity-code search, `headcount`, `quantity`, `unit`, and `report_id`. Date and report reference are scoped to the project. Quantity filtering operates on measured values with recorded amount and unit. Display the twelve reference fields from the specification. Preserve established clients using legacy fields.
- `GET activity-log/filters/` and its existing `filter-options/` alias return options from the authorized project and applicable version policy. Preserve existing lists and add labeled contractor IDs for identity-safe selection.
- Default official selection requires current approved reports and non-deleted reports and rows. The existing explicit `approved_only=false` preview stays current and non-deleted. A status filter cannot expand the selected policy. Preserve separate authorized history.
- List accepts `page` and `page_size` using existing defaults and limits. FILE1 ignores pagination and emits one row per qualifying activity in the same order, with the established columns and quantity presentation. Compare row identity using an independent fixture mapping where the workbook does not expose an activity ID.

### Additive list response

- Preserve `count`, `next`, `previous` and `results`. `count` represents the full selection. Each result includes the existing quantities and fields plus explicit `quantity_measured` and contractor identity where recorded. Normalize inconsistent legacy quantity for display using B01 measurement semantics.
- Add `aggregates.headcount_sum` as the integer sum of recorded activity-row headcounts, with zero for an empty selection. Label it in FA/EN as an activity-row headcount sum.
- Add `aggregates.quantity_by_unit` as ordered records with `unit`, `total` (decimal string or null), `measured_count`, and `unknown_count`. Add `aggregates.unknown_quantity_without_unit_count`. Use an empty array when the selection has no known units.

## Browser behavior

Use the URL as filter and paging state. Serialize the actual date bounds when the view starts with a date default or the user selects a preset, so a shared link keeps the same date range. Filter changes reset page to one. Paging changes only the visible slice. Refresh, share, Back and Forward restore the selected filters and page. A second user with equivalent access and stable data sees the same identities. FILE1 downloads use the current URL selection without page parameters. Prevent stale query results being shown under newly applied criteria. Provide labeled keyboard-operable controls and localized loading, empty and error states.
