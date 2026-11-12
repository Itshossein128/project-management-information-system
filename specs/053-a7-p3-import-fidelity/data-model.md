# Data Model: Import Fidelity

No new project, baseline, or relationship table. `Activity.wbs` stays required. Imported `working_calendar` stays null.

## Activity fields written by import

Existing columns:

| Field | Source | Rule |
| --- | --- | --- |
| `wbs` | Resolved parent package | Required. No parent means the activity is not inserted. |
| `activity_code` | WBS code, else task id | Unique with `project`. An in-file duplicate blocks the confirmation. |
| `activity_name` | Task name | Required by the current parser. |
| `planned_start`, `planned_finish` | MSP `Start`/`Finish` or P6 `target_start_date`/`target_end_date` | Finish before start blocks the confirmation. Actual dates are not copied here. |
| `actual_start`, `actual_finish` | MSP `ActualStart`/`ActualFinish` or P6 `act_start_date`/`act_end_date` | Set only on a newly created activity, and only when the file has that value. |
| `forecast_start`, `forecast_finish` | None | Remain null. |
| `duration_days` | Exact eight-hour conversion, including 0 | Null when the file's duration is not a whole number of days. |
| `is_milestone` | MSP `Milestone`, or P6 `task_type` `TT_Mile` / `TT_FinMile` | True only with duration 0. Zero duration alone does not set it. |
| `working_calendar` | None | Stays null. |
| `weight` | None | Not used for percent or file weight. |

New nullable columns on `activities`. Existing rows stay null. No backfill.

| Field | Source | Rule |
| --- | --- | --- |
| `planned_percent` | MSP `PercentComplete` or P6 `phys_complete_pct` | Stored when the number is from 0 through 100 inclusive. Otherwise null and `invalid_percent`. |
| `is_critical` | MSP `Critical` or the P6 critical flag when the file has one | Null when the file has no flag. |
| `total_slack_days` | MSP total slack or P6 total float | Whole days after the same exact conversion as lag. Otherwise null. |
| `free_slack_days` | MSP free slack or P6 free float | Same conversion rule. |

## Work package

A summary row, or a Primavera `PROJWBS` row, becomes a `WBS` node. The parent is the resolved parent identifier, or null for a root. `wbs_code` is the file code. A row deeper than `Project.max_depth` is not inserted. Descendants of an omitted row are not moved under an ancestor.

## Activity link

`ActivityRelation` stays the stored link. `relation_type` is only `FS`, `SS`, `FF`, or `SF`. `lag_days` is the exact whole-day delay, including 0. A delay that is not an exact number of days does not create the row.

A predecessor that is missing, a summary, an unsupported type, or part of a cycle does not create a row. A cycle or a self-link blocks the whole confirmation before any write.

## Working copy

`import_safety.open_working_copy` still decides whether an unapproved working copy is created and whether it is current. That copy is not locked and is not approved. Its `BaselineActivity` rows copy planned dates, duration, `planned_percent`, slack, and `is_critical` from the resolved task so the current Gantt and critical-path gate keep their existing read path. Those copies do not replace the activity fields above.

## Resolved plan

An in-memory result, not a table:

- Work packages to insert, with parent keys
- Activities to insert, with the fields above
- Links to insert
- Blocking codes, if any
- Warning codes with row identity
- Counts of created, omitted, and warned rows

Preview and confirm both display this result. Confirm writes it only when there is no blocking code and the existing safety gate allows the write.

## Validation states

| State | Stored project |
| --- | --- |
| Blocking classification | Unchanged. Replacement does not start. |
| Warnings only | Valid rows stored. Named rows or links omitted. |
| Empty result | Unchanged. `empty_import` warning. Not a successful plan change. |
| Append duplicate of an existing code | Existing row unchanged, including its actual dates. |
| Calendar present in the file | Activities stored with `working_calendar` null and `calendar_not_applied`. |
