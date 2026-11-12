# Feature Specification: Import Fidelity for WBS, Activities, and Schedule

**Feature Branch**: `053-a7-p3-import-fidelity`

**Created**: 2026-11-11

**Status**: Draft

**Input**: User description: "A.7-P3 — import a supported schedule file with the correct meaning for work-breakdown parents, activities, durations, relationships, and dates. Audit owners: W07, S01, S02, S03, S04, S06, S07, S08, I01, I03, I04, I05, I12, I13, I21, I22. Source prompt: output/a7-requirements-2026-11-10/speckit-prompts/03-import-fidelity.md."

## Clarifications

### Session 2026-11-12

- Q: Should the parentless employer-file activities شروع and پایان be stored? → A: Keep omitting them with row warnings; store zero duration only for activities with a valid parent. FR-015 and US6/AC5 below reflect this decision; the required-parent rule stays in force.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The file's parent is the stored parent (Priority: P1)

A planner imports a schedule that has more than one root, more than one branch, codes with and without dots, a deep outline, and rows that are not in parent-before-child order. Each summary row becomes a work package. Each leaf and each milestone becomes an activity under the parent the file names. Preview and the saved schedule show the same parents, the same identifiers, and the same warnings.

**Why this priority**: A parent chosen from the last sibling or from code order puts activities on the wrong package. Later progress, cost, and the Gantt then describe the wrong scope.

**Independent Test**: Import authored branch examples for both accepted schedule families, including a reordered copy of the same file. Compare each child's parent in the preview and in the saved schedule with the parent named in the file.

**Acceptance Scenarios**:

1. **Given** a file with two roots and two branches, **When** the planner previews and then confirms the import, **Then** each child is under the parent the file names, in both the preview and the saved schedule.
2. **Given** the same relationships written in a different row order, and codes that mix dotted and undotted forms, **When** the file is imported, **Then** the parents match the file and do not follow row order or code sort order.
3. **Given** a summary row, **When** it is imported, **Then** it is a work package. **Given** a leaf or a milestone, **When** it is imported, **Then** it is an activity under that file's parent package.
4. **Given** an activity whose file names no parent, **When** the planner previews and confirms, **Then** that activity is listed with its row identity and is left unattached. It is not placed on the first or last package.
5. **Given** a file with no summary rows, **When** it is imported, **Then** each row is placed only by the parent identity in the file. A row with no parent identity is reported and is left without a parent.

---

### User Story 2 - Unsafe structure is stopped before the project changes (Priority: P1)

A planner submits a file with an impossible date, a loop in the work tree or in the activity links, a row that names itself, a repeated identifier or code, a missing predecessor, a level deeper than the project allows, or a relationship type the product does not recognize. The product classifies each case before it changes the project. A blocking case writes nothing. A warning names the row and applies only the stated omission.

**Why this priority**: The same checks already protect manual edits. A file that bypasses them can store a loop, a finish before its start, or two rows with one code.

**Independent Test**: For each case, compare the project before and after confirm. Blocking cases match the earlier project. Warning cases name the row and omit only the stated row or link.

**Acceptance Scenarios**:

1. **Given** a finish date before its start, a loop, a self-reference, or two rows in one file with the same identifier or code, **When** the planner confirms, **Then** the project is unchanged and the result names the blocking reason and the row identities.
2. **Given** a predecessor that is not in the file, a relationship type outside finish-to-start, start-to-start, finish-to-finish, and start-to-finish, or a row deeper than the project allows, **When** the planner confirms, **Then** that link or row is omitted, the warning names it, and the other valid rows may be stored.
3. **Given** any of these cases, **When** the planner sees the preview and the saved result, **Then** the classification, the row identity, and the counts agree.
4. **Given** an empty imported structure, or a weight that is not a valid share of its parent, **When** the import finishes, **Then** the planner sees a warning. An empty structure is not presented as a successful plan change. An invalid weight is not replaced with a guessed weight.

---

### User Story 3 - Supported facts arrive on the activity (Priority: P1)

A planner opens an imported activity and finds the duration, the duration unit, a zero duration, the milestone mark, the planned dates, the planned quantity or percent, the critical mark, and the slack that the file supplied and the support contract accepts. Those values are on the activity the planner and the schedule views use. A copy kept only on an import snapshot does not satisfy this.

**Why this priority**: A duration or milestone that exists only on a snapshot leaves the Gantt, the milestone list, and the critical-path check without the fact they need.

**Independent Test**: Import the authored milestone and relationship examples. Read the saved activity and its links. Compare each supported value with the hand-counted example. Repeat for a paired native schedule file and its XML twin.

**Acceptance Scenarios**:

1. **Given** a duration in days or in hours, **When** it is imported, **Then** the activity stores it in whole days using the agreed eight-hour day. A zero duration is stored as zero days.
2. **Given** a milestone mark in the file, **When** the activity is saved, **Then** the activity is identifiable as a milestone. A zero duration does not become a milestone unless the file marks it as one.
3. **Given** planned start, planned finish, planned quantity or percent, a critical mark, and slack in the file, **When** they are supported values, **Then** the activity stores them. The same values may also sit on the import snapshot.
4. **Given** a Microsoft Project link delay written as 4800 in that format's unit of tenths of a minute, **When** the link is stored, **Then** the delay is 1 day under the agreed eight-hour day.
5. **Given** a Primavera delay stated in hours, **When** the hours divide evenly into the agreed eight-hour day, **Then** the stored delay is that whole number of days. **When** they do not divide evenly, **Then** the link is reported and no rounded delay is stored.
6. **Given** a relationship type of finish-to-start, start-to-start, finish-to-finish, or start-to-finish, **When** the link is stored, **Then** the stored type is that type.
7. **Given** a working calendar and exceptions in the file, **When** the calendar is outside the current support contract, **Then** the result says the calendar was not applied, and no substitute calendar is assigned.

---

### User Story 4 - Planned, approved, actual, and forecast stay separate (Priority: P1)

A planner imports a file into a project that already has actual dates and a locked approved baseline. The import fills planned dates from the file. It leaves actual dates and forecast dates empty when the file does not contain them. It does not overwrite actual dates already stored on an activity that remains. The imported schedule copy stays an unapproved working copy.

**Why this priority**: Mixing these dates, or promoting an import into the locked baseline, makes progress and deviation look approved when they were only imported.

**Independent Test**: On a project with an actual date and a locked approved baseline, import a file that has planned dates only. Read the four date kinds and the baseline state before and after.

**Acceptance Scenarios**:

1. **Given** a file with planned start and finish only, **When** import succeeds, **Then** those dates are the activity's planned dates, and actual and forecast dates are not created.
2. **Given** an activity that already has an actual date and that remains after import, **When** the file has no actual date, **Then** the stored actual date is unchanged.
3. **Given** a successful import that adds schedule content, **When** the planner inspects the schedule copy, **Then** it is an unapproved working copy and the locked approved baseline is unchanged.
4. **Given** a later approved schedule change, **When** it is approved, **Then** the previous locked version remains, and the change still records its effect on milestones, cost, and contract. Import itself is not that approval.

---

### User Story 5 - Imported facts show up where the schedule is used (Priority: P2)

After a successful import, the planner sees the same milestones and planned dates on the Gantt and on the milestone report, sees the stored relationships, and sees a critical-path result only when durations and relationships are complete enough to calculate. An incomplete import is labeled not calculable.

**Why this priority**: A correct stored activity that the Gantt or the milestone report ignores is still a wrong schedule for the planner.

**Independent Test**: Import one authored file with a milestone and one finish-to-start link, and one file that omits a duration. Open the Gantt, the milestone report, and the critical-path gate in Persian and in English.

**Acceptance Scenarios**:

1. **Given** a successful import of a milestone and a planned date, **When** the planner opens the Gantt and the milestone report, **Then** both show that milestone and those planned dates, distinct from approved, actual, and forecast dates.
2. **Given** an import whose durations or relationships are incomplete, **When** the planner opens the critical-path gate, **Then** the result is not calculable. Stored critical marks do not make that network look valid.
3. **Given** the same screens in Persian and in English, **When** the planner compares them, **Then** the dates, the milestone marks, and any calendar warning have the same meaning.
4. **Given** the existing earned-value and period reports, **When** this import is used, **Then** those reports keep their current formulas and catalog. This feature only requires that they read the imported dates and milestones they already know how to read.

---

### User Story 6 - A bad file is still rejected, and twins match after save (Priority: P1)

A planner submits a file that is too large, empty, corrupt, password-protected, renamed to a schedule extension, unsupported, or otherwise not a genuine schedule. The project does not change, and the message distinguishes the problem. For a genuine pair made of a native schedule file and the same schedule in XML, the saved hierarchy, dates, durations, milestones, relationships, and warnings match. The four known links on the employer file are explained.

**Why this priority**: Fidelity work must not weaken the existing rejection of unsafe files. A preview-only comparison can hide a parent, a duration, or a link that the saved project got wrong.

**Independent Test**: Reject one file of each unsafe kind and confirm the project is unchanged. Import a paired native file and XML file and compare stored rows. Import the unchanged employer file and read the classification of predecessor identifiers 8055, 8084, 8102, and 8120.

**Acceptance Scenarios**:

1. **Given** an oversized, empty, corrupt, password-protected, renamed, or unsupported file, **When** the planner previews or confirms, **Then** the project is unchanged and the message names that kind of problem. A password-protected file is not opened by guessing.
2. **Given** a paired native schedule file and XML file with the same supported content, **When** both are imported on separate trial projects, **Then** the saved hierarchy, dates, durations, milestones, relationships, and warnings have no unexplained difference.
3. **Given** the unchanged employer schedule file, **When** it is imported on a trial project, **Then** each of predecessor identifiers 8055, 8084, 8102, and 8120 is reported as a present summary work package on the successor پایان. The summary stays a work package. No activity relationship is created for that link.
4. **Given** the historical observation of 83 source links and 79 stored relationships, **When** the result is judged, **Then** those historical counts are evidence of the old mismatch. They are not the pass target. The pass target is the independent schedule reference and the decision in scenario 3.
5. **Given** the parentless tasks شروع and پایان on the unchanged employer file, **When** the file is previewed and imported, **Then** each row is omitted with its row identity and `activity_without_parent`. No parent is invented. Their known duration parses as zero, not as an unparsed duration. A zero-duration activity is stored as zero days only when its source parent resolves to a valid work package.

---

### Edge Cases

- Several roots are all roots. None of them is placed under another root because it appears later in the file.
- A dotted code and an undotted code can both be valid. The dots are not parsed as a substitute for the file's parent identity.
- A file with no summary rows does not gain a parent that the file does not name.
- A duplicate identifier inside one file blocks the whole confirmation. A duplicate against data already in the project follows the existing append and replacement rules from the import-safety feature.
- A missing predecessor omits that link and names the row. It does not invent a predecessor.
- A delay that is not a whole number of agreed days is reported and left unset. It is not rounded to a nearby day.
- A calendar named in the file is not replaced with the project's calendar or with a guessed calendar.
- An imported working copy is not treated as the locked approved baseline, including when the import is otherwise correct.
- Replacement of a project that already has history still follows the import-safety rules. This feature does not weaken them in order to store a more faithful tree.
- Preview and cancel still leave the project unchanged.
- The employer schedule file stays byte-for-byte unchanged.
- An empty project that imports cleanly does not prove a file with loops, duplicate codes, or summary links.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The parent of every imported work package and activity MUST be the parent identified in the file. Row order, code sort order, the last sibling at a level, and the first or last package already created MUST NOT choose the parent. Preview and the saved schedule MUST show the same parent.
- **FR-002**: A summary row MUST become a work package. A leaf and a milestone MUST become an activity under the work package the file names. This mapping MUST be the same for every accepted schedule file type.
- **FR-003**: An activity whose file names no parent MUST be reported with its row identity and MUST remain unattached. A file with no summary rows MUST place each row only by the parent identity in that file. A row with no parent identity MUST be reported and MUST remain without a parent.
- **FR-004**: The product MUST classify the following before any project change. Blocking cases MUST leave the project unchanged. Warning cases MUST name the row and MUST omit only the stated row or link.

  | Condition | Class | Stored result |
  | --- | --- | --- |
  | Finish before start | Blocking | No change from this confirmation |
  | Loop in the work tree or in activity links, including a row that names itself | Blocking | No change from this confirmation |
  | Two rows in one file with the same identifier or the same code | Blocking | No change from this confirmation |
  | Predecessor identifier that is not in the file | Warning | That link is omitted |
  | Relationship type other than finish-to-start, start-to-start, finish-to-finish, or start-to-finish | Warning | That link is omitted |
  | Row deeper than the project's allowed depth | Warning | That row is omitted and counted |
  | Empty imported structure | Warning | No successful plan-change message |
  | Weight that is not a valid share of its parent | Warning | No guessed weight is stored |
  | Predecessor is a summary work package | Warning | No activity relationship is stored, and the summary stays a work package |
  | Working calendar outside the support contract | Warning | No calendar is assigned |

- **FR-005**: The same classification, row identity, created counts, omitted counts, and warnings MUST appear in the preview and in the saved result.
- **FR-006**: Where the support contract includes the value, the activity MUST store duration in whole days, a zero duration as zero days, the milestone mark, planned start, planned finish, planned quantity or percent, the critical mark, and slack. Hour-based duration MUST convert with the agreed eight-hour day. A value that exists only on the import snapshot MUST NOT satisfy this requirement.
- **FR-007**: A Microsoft Project link delay MUST be read in tenths of a minute. A value of 4800 MUST be stored as 1 day under the agreed eight-hour day. A Primavera delay MUST be read in the unit the file states. A conversion that is not an exact whole number of agreed days MUST be reported, and no rounded delay MUST be stored. The stored relationship type MUST be the type stated by the file when that type is one of the four supported types.
- **FR-008**: A working calendar and its exceptions that are outside the current support contract MUST be reported as not applied. The import MUST leave the activity without an assigned calendar. It MUST NOT assign a project default or any other substitute.
- **FR-009**: Planned dates, approved baseline dates, actual dates, and forecast dates MUST remain distinct. Import MUST fill planned dates from the file's planned dates. It MUST leave actual and forecast empty when the file does not contain them. It MUST leave an existing actual date unchanged on an activity that remains.
- **FR-010**: A schedule copy created by import MUST remain an unapproved working copy. It MUST NOT become the locked approved baseline. A later approved schedule change MUST keep the previous locked version and MUST remain a different action from import.
- **FR-011**: After import, the Gantt and the milestone report MUST show the imported milestones and planned dates, distinct from approved, actual, and forecast dates. The critical-path gate MUST say the result is not calculable when durations or relationships are incomplete. This feature MUST NOT add or change earned-value formulas or the period-report catalog.
- **FR-012**: Oversized, empty, corrupt, password-protected, renamed, unsupported, and non-genuine files MUST be rejected with a distinct actionable message and with no project change. Password-protected files MUST NOT be decrypted. Readable samples of each accepted file type MUST still be accepted. The product MUST NOT claim that every Microsoft Project year is supported.
- **FR-013**: A paired native schedule file and XML file with the same supported content MUST produce the same stored hierarchy, dates, durations, milestones, relationships, and warnings. Comparison of the preview alone MUST NOT satisfy this requirement.
- **FR-014**: On the unchanged employer schedule file, predecessor identifiers 8055, 8084, 8102, and 8120 MUST each be reported, in preview and in the saved result, as a present summary work package on the successor پایان. The summary MUST remain a work package. No activity relationship MUST be created for that link. The historical counts of 83 source links and 79 stored relationships MUST remain historical evidence and MUST NOT be the pass target.
- **FR-015**: The known zero-duration form MUST parse as zero days. An activity with a valid source parent MUST store that duration as zero days. The parentless employer-file tasks شروع and پایان MUST instead be omitted with row-identified `activity_without_parent` warnings in preview and the saved result, per FR-003; no parent MUST be invented to store them.
- **FR-016**: The employer schedule file MUST remain byte-for-byte unchanged.
- **FR-017**: User-facing dates, milestone marks, warnings, and blocking reasons MUST be understandable in Persian and in English, with the same meaning in the active language.
- **FR-018**: An independent spreadsheet import, a rewritten preview, a live Primavera connection, a new earned-value or finance report, and any weakening of the current access policy or of the import-safety rules are outside this feature.

### Key Entities

- **Schedule file**: One accepted native schedule file, XML schedule, or Primavera exchange file, judged against the schedule reference contract.
- **Work package**: The stored parent created from a summary row, or from a root when the file names no parent.
- **Activity**: The stored leaf or milestone, with duration, milestone mark, planned dates, planned quantity or percent, critical mark, slack, and an optional calendar only when the support contract includes that calendar.
- **Activity link**: A predecessor relationship with one of the four supported types and a whole-day delay after an exact unit conversion.
- **Import outcome**: The shared preview and saved result: created rows, omitted rows, blocking errors, warnings, and row identities.
- **Schedule copy**: The unapproved working copy an adding import may record. It is distinct from the locked approved baseline.
- **Date set**: Planned, approved, actual, and forecast dates, kept as separate facts.
- **Employer schedule file**: The unchanged customer file identified by the schedule reference contract, including the four summary-predecessor links and the two known zero durations.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100% of authored branch trials, including reordered rows, dotted and undotted codes, several roots, and several branches, every child is under the parent named in the file in both the preview and the saved schedule.
- **SC-002**: In 100% of blocking trials, the project matches its pre-confirm state. In 100% of warning trials, the named row or link is omitted and every other accepted row matches the file.
- **SC-003**: For every supported field present in an authored example, the saved activity shows that value. A field present only on the import snapshot fails the trial.
- **SC-004**: A Microsoft Project delay of 4800 in the file's own unit is stored as 1 day. In 100% of trials where a delay is not an exact whole number of agreed days, the delay is reported and no rounded value is stored.
- **SC-005**: In 100% of trials, absent actual and forecast dates stay empty, an existing actual date on a surviving activity is unchanged, and the imported copy is not the locked approved baseline.
- **SC-006**: After one successful authored import, the Gantt and the milestone report show the same milestones and planned dates. An incomplete network is labeled not calculable in the same trial set.
- **SC-007**: In 100% of oversized, empty, corrupt, password-protected, renamed, and unsupported trials, the project is unchanged. Every paired native-file and XML trial has zero unexplained differences in stored hierarchy, dates, durations, milestones, relationships, and warnings.
- **SC-008**: All four employer-file summary links are classified alike in the preview and in the saved result. The historical 83-versus-79 observation is not used as a pass or fail count.
- **SC-009**: For every trial in this feature, preview counts, saved counts, and warnings describe the same outcome.
- **SC-010**: A planner can read the imported dates, milestone marks, and calendar warning in Persian and in English with the same meaning.
- **SC-011**: A reviewer can read the support decisions that differ from the previous field-support contract, including calendar non-support and the summary-link decision, without reading implementation notes.

## Assumptions

- The schedule reference contract from the reference phase is the field, unit, and control-figure baseline. Its hand-counted examples are the expected rows. The 2026-11-10 audit and its importer counts are historical evidence, not approved targets.
- The agreed day is the eight-hour day already recorded for hour-based duration. Stored relationship delay remains a whole number of those days, which is the existing schedule rule. A conversion that does not land on a whole day is reported.
- Microsoft Project link delay is tenths of a minute in that format. 4800 tenths of a minute are 480 minutes, which are one agreed day. Primavera delay uses the unit stated on the link.
- Working calendars and their exceptions stay outside the current support contract. This feature reports that fact and assigns no substitute. Transferring a file calendar, including the Shamsi calendar in the employer file, is a contract change for the next phase if the employer requires it. Dates already in the file are still stored as planned dates.
- A predecessor that is a summary work package cannot become an activity relationship, because a summary is a work package and a link exists between activities. The four employer links are that case. They are reported and omitted. Turning every summary into an activity, or omitting the link with no reason, is not the decision.
- The known zero form on شروع and پایان is a duration of zero. Those employer-file rows have no parent and are omitted with row warnings. Zero is stored only for an activity with a valid source parent. The milestone mark is stored only when the file marks the row as a milestone.
- A file with no summary rows keeps the summary-versus-activity presentation: the file's own parent identity places each row, and a missing parent does not borrow another row.
- Import safety remains in force: protected history is not replaced, preview and cancel write nothing, a repeated empty result is not a new current plan, and an archived project stays unchanged. This feature does not restate those rules as new behavior.
- The reference phase is ready for review and did not change import behavior. The import-safety phase's integrated baseline and verification limits are recorded in [its handoff](../052-a7-p2-import-safety/handoff.md). This feature preserves that safety baseline.
- Who may import stays the current membership and work-breakdown edit permission. This feature does not change access.
- An independent spreadsheet path for the work breakdown, a new preview flow, a live Primavera connection, and full earned-value or financial reporting stay outside the approved delivery boundary.
- Contract decisions made here, especially calendar non-support and the summary-link decision, are handed to the next phase as contract changes. They are not silent importer behavior.
- The employer file fingerprint recorded by the reference phase remains the identity of that file. This feature does not edit the file to make counts match.
