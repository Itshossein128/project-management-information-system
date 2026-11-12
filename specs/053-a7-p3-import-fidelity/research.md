# Research: Import Fidelity

## Parent identity

**Decision**: Resolve parents from the file's own parent identifier, then let preview and both executors consume that resolved plan.

Microsoft Project XML uses `OutlineNumber`. The parent of `1.2.3` is the task whose outline number is `1.2`. The WBS code is the stored code, not the parent lookup. Row order and the last node at the previous level are not parents. A missing outline number means the row has no parent identity.

Primavera uses `PROJWBS.parent_wbs_id` for a work package and `TASK.wbs_id` for an activity. Both must exist in that file. Prefix matching on codes is not a parent lookup.

**Rationale**: The current executors remember the last node at the previous level after sorting. That chooses a different parent when the file order or the code sort changes. `build_preview` already walks an outline stack, so preview and confirm can disagree. One resolver removes that split.

**Alternatives considered**: Keep the outline stack. Rejected because a reordered file would change parents. Parse dots in the WBS code. Rejected because the spec treats those dots as a code, not as a parent link.

## Rows with no parent

**Decision**: A summary with no parent identifier is a root work package. A leaf or milestone with no parent identifier is not stored. The result uses `activity_without_parent` and names the row. It is not attached to the first or last package, and no container package is created for it.

A named parent that is not in the file is the same warning, not a root.

The reference `relation.xml` and `relation.xer` files are this case: their leaves have no resolvable work-package parent. They prove the warning. Stored finish-to-start coverage comes from a test file that puts two leaves under a real parent. The reference files are not edited.

**Rationale**: `Activity.wbs` is required, so a parentless activity cannot be inserted without inventing a package. The spec forbids that invention.

**Alternatives considered**: Current fallback that treats every row as a summary and then attaches orphans to the first or last package. Rejected. One synthetic file-level package. Rejected for the same reason.

## Summary predecessors

**Decision**: A predecessor that is a summary work package produces `predecessor_is_summary` and no activity link. The summary stays a work package. This covers employer predecessor identifiers 8055, 8084, 8102, and 8120 on successor پایان. A test XML with that shape is the deterministic check. The unchanged `real-data/plan.mpp` is imported only on the pytest database when the MPP converter runs. Counts 83 and 79 stay historical.

**Rationale**: Activity links exist between activities. Turning the summary into an activity would break the summary-to-package rule.

**Alternatives considered**: Expand the summary link onto every child leaf. Rejected because that invents links the file does not name.

## Duration, lag, and slack units

**Decision**: An agreed day is 8 hours. Microsoft Project `Duration` of `P{n}D` is `n` days. `PT{n}H` and `PT0H0M0S` convert only when the hours divide by 8, including zero. `PT0H0M0S` is 0 days. A remainder sets `duration_days` null and adds `duration_not_whole_days`.

`LinkLag` and Microsoft Project slack are tenths of a minute. 4800 is 1 day. The value is stored only when it divides evenly by 4800. Otherwise the link is omitted with `lag_not_whole_days`, or the slack field stays null with `slack_not_whole_days`.

Primavera `target_drtn_hr_cnt` and `lag_hr_cnt` are hours. They convert only when they divide evenly by 8. Zero stays zero. Floor division and `max(1, round(...))` are not used.

**Rationale**: The current duration helper rounds hours up to at least one day and does not accept the zero form. The current lag path stores the raw `LinkLag` integer and floors Primavera hours. Both contradict the spec.

**Alternatives considered**: Store fractional days. Rejected because `duration_days` and `lag_days` are whole-day integers and the existing schedule rule keeps lag in whole days. Add a migration to store minutes. Rejected as a new unit the support contract does not ask for.

## Milestone and calendar

**Decision**: Microsoft Project `Milestone` of true sets `is_milestone` only when the stored duration is zero. A milestone flag with a non-zero duration warns `milestone_duration_conflict`, keeps the duration, and leaves `is_milestone` false. Primavera sets the milestone mark only when `task_type` is `TT_Mile` or `TT_FinMile`. Zero hours alone are not a milestone, so `milestone.xer` stores duration 0 and `is_milestone` false. `milestone.xml` stores both.

If the XML contains a `Calendar` element or the XER contains a `CALENDAR` table, add one `calendar_not_applied` warning. `working_calendar` stays null. The import path does not call the project default calendar.

**Rationale**: The activity rule already rejects a milestone whose duration is not zero. The phase 1 contract left calendars outside support. Assigning a default would hide that.

**Alternatives considered**: Import the Shamsi calendar from the employer file. Deferred. The spec records that as a contract change for the next phase.

## Dates and consuming fields

**Decision**: Planned dates come only from Microsoft Project `Start` and `Finish`, or Primavera `target_start_date` and `target_end_date`. Actual dates on a newly created activity come only from `ActualStart` and `ActualFinish`, or Primavera `act_start_date` and `act_end_date`. An actual date is never copied into a planned date. Forecast dates stay null. An append that skips an existing code does not update that row.

`duration_days`, `is_milestone`, planned dates, `planned_percent`, `is_critical`, `total_slack_days`, and `free_slack_days` are written on `Activity`. The same critical, slack, percent, and duration values are still copied onto the unapproved working-copy `BaselineActivity` rows so the current Gantt and critical-path gate keep reading them. `Activity.weight` is not used for percent. No WBS weight is invented. A percent outside 0 through 100 warns `invalid_percent` and is not stored.

A new migration adds the four activity columns as nullable, with `is_critical` nullable too. Existing rows stay null.

**Rationale**: Today `extract_activities_from_tasks` writes only planned dates. Percent, slack, and critical exist only on `BaselineActivity`, and the activity model has no columns for them. The spec says a snapshot-only value does not satisfy the requirement. Nullable columns preserve existing rows.

**Alternatives considered**: Leave critical and slack only on the working copy. Rejected because the spec names the activity as the consuming record. Reuse `Activity.weight` for percent. Rejected because weight is a share of a parent, not percent complete.

## Blocking and warnings

**Decision**: The resolver classifies the file before `guard_and_maybe_replace`. Blocking results raise a coded error and leave the project unchanged, including replacement mode. Warning rows are omitted or stored under the contract, and the other valid rows may be written.

Blocking: finish before start, a parent cycle, an activity-link cycle, a self-link, and a duplicate identifier or code inside the file.

Warnings: missing predecessor, unsupported relationship type, depth past `project.max_depth` (that row and its descendants, with no reparenting), empty result, invalid percent, summary predecessor, calendar not applied, non-whole duration, lag, or slack, milestone conflict, and activity without a parent.

A duplicate against data already in the project stays the existing append skip. It is not the in-file blocking rule.

**Rationale**: Replacement currently deletes before the file is judged. A blocking file must not reach that delete. Manual cycle checks run only after a link is posted, so import bypasses them today.

**Alternatives considered**: Write the valid rows and skip the blocking rows. Rejected for the four blocking cases. The spec says those confirmations write nothing.

## Downstream screens

**Decision**: The status report already lists `Activity.is_milestone`. The Gantt payload gains `is_milestone` and the Gantt shows it. The critical-path gate stays the current validity check: incomplete duration means not calculable, and stored critical flags do not override that. No earned-value formula changes.

Wizard text for the new codes is localized. Stable codes stay in the API result.

**Rationale**: A milestone stored only on the activity is invisible on the Gantt today. The status report will show it once `is_milestone` is set.

**Alternatives considered**: A new milestone report. Rejected. The existing report is the consumer.
