# Contract: Schedule import fidelity

This contract is the shared preview and confirm vocabulary for Microsoft Project XML, native MPP, and Primavera XER. It does not add a file type, a permission, or a calendar import.

Preview and confirm resolve the same file through one plan. Counts, parents, row identities, blocking codes, and warnings match. Preview writes nothing.

Confirm runs this classification before the import-safety replacement gate. A blocking code writes nothing and does not remove existing work. When there is no blocking code, replacement, append, attribution, and the unapproved working copy stay on the import-safety contract.

## Codes

Codes are language-independent. Persian and English text is presentation.

### Blocking

The confirmation is refused. Project data is unchanged.

| Code | When |
| --- | --- |
| `finish_before_start` | A row has both planned dates and the finish is before the start. |
| `structure_cycle` | A parent chain or an activity-link chain loops, including a row that names itself. |
| `duplicate_in_file` | Two rows in the same file share an identifier or a code. |

### Warnings

Other valid rows may be stored. The named row or link is omitted, except where the table says the row is stored with a null field.

| Code | When | What is stored |
| --- | --- | --- |
| `activity_without_parent` | A leaf has no parent identifier, or the named parent is not in the file. | That activity is omitted. |
| `predecessor_missing` | The predecessor identifier is not in the file. | That link is omitted. |
| `predecessor_is_summary` | The predecessor is a summary work package. | That link is omitted. The summary stays a work package. |
| `relation_type_invalid` | The type is not finish-to-start, start-to-start, finish-to-finish, or start-to-finish. | That link is omitted. |
| `lag_not_whole_days` | The delay is not an exact number of eight-hour days. | That link is omitted. |
| `depth_exceeded` | The row is deeper than the project's maximum depth. | That row and its descendants are omitted. |
| `duration_not_whole_days` | The duration is not an exact number of eight-hour days. | The activity is stored with `duration_days` null. |
| `slack_not_whole_days` | Slack is not an exact number of eight-hour days. | The activity is stored with that slack field null. |
| `invalid_percent` | Percent is outside 0 through 100. | The activity is stored with `planned_percent` null. |
| `milestone_duration_conflict` | The file marks a milestone and the duration is not zero. | Duration is stored. `is_milestone` stays false. |
| `calendar_not_applied` | The file contains a calendar. | No calendar is assigned. One warning for the file. |
| `empty_import` | The resolved plan would store nothing and nothing was blocking. | No rows. The result is not a successful plan change. Existing project rows stay. |
| `duplicate_existing` | The code already exists in the project. | That existing row stays unchanged. |
| `invalid_weight` | Microsoft Project `Weight`, or Primavera `weight`, is present and is not a share from 0 through 1. | `Activity.weight` stays empty. Percent complete is not used as a weight. |

## Units

- One day is 8 hours.
- Microsoft Project duration `P{n}D` is `n` days. `PT{n}H` and `PT0H0M0S` are days only when the hours divide by 8. Zero is 0 days.
- Microsoft Project `LinkLag` and slack are tenths of a minute. 4800 is 1 day. Any other multiple of 4800 is that many days. Any other value is not stored as a day count.
- Primavera duration and lag hours convert only when they divide by 8. Zero is 0 days. Values are not rounded and are not forced up to 1.

## Parents and mapping

- Microsoft Project parent key is the outline number without its last segment, matched to another row's outline number.
- Primavera work-package parent is `parent_wbs_id`. An activity's package is `wbs_id`.
- Summary rows and `PROJWBS` rows become work packages. Leaves become activities. A milestone flag becomes `is_milestone` only when duration is zero.
- A root summary has no parent. A leaf with no resolvable parent is `activity_without_parent`.

## Dates

Planned dates and actual dates stay on their own fields. Forecast dates are not filled. An existing activity skipped as an append duplicate keeps its actual dates.

## Employer-file decisions handed to the next phase

- Calendars, including the Shamsi calendar in the employer file, are `calendar_not_applied`. No substitute is assigned.
- Predecessor identifiers 8055, 8084, 8102, and 8120 are `predecessor_is_summary`. They are not activity links, and the summaries are not turned into activities.
- The historical observation of 83 source links and 79 stored relationships is not a pass count.
- The known zero-duration form parses as 0 days and is stored as 0 days only for activities with a valid source parent. The actual employer-file rows شروع and پایان have no parent: both preview and the saved result report row-identified `activity_without_parent` warnings, and neither activity is stored. No parent is invented. A milestone mark is stored only when the file sets it.

**Scope decision (2026-11-12)**: The user confirmed: “Keep omitting them with row warnings; store zero duration only for activities with a valid parent.” This resolves T034 and supersedes the earlier unconditional employer-row storage wording in FR-015 and US6/AC5.

Existing file-size, password, corrupt, renamed, and unsupported rejections stay on their current contract. This contract does not weaken them.
