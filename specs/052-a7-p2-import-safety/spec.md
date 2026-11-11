# Feature Specification: Import Safety and History

**Feature Branch**: `052-a7-p2-import-safety`

**Created**: 2026-11-11

**Status**: Draft

**Input**: User description: "A.7-P2 — make schedule import safe against data loss, unauthorized change, and misleading repeats. Audit owners: P08, W04, S05, I06, I07, I08, I11, I14, I18. Source prompt: output/a7-requirements-2026-11-10/speckit-prompts/02-import-safety.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Replacement keeps existing history (Priority: P1)

A planner who already has activities, recorded progress, cost, a linked document, and a locked approved baseline tries to replace the schedule from a Microsoft Project or Primavera file. The replacement does not erase that history. If the product cannot keep the history safely, the replacement is refused before anything changes, and the planner sees why.

**Why this priority**: A replacement that deletes activities and empties a locked baseline destroys the record the project uses to explain progress, cost, and deviation. Manual deletion and forced template replacement already stop for those dependencies. File replacement must stop for the same reasons.

**Independent Test**: On a project that already has an activity, progress, cost, a document, and a locked approved baseline, confirm replacement from each accepted schedule file type. Compare the project before and after. The history is still there, and the refusal names the reason. Repeat the comparison on a project with none of those dependencies, where replacement is allowed.

**Acceptance Scenarios**:

1. **Given** a project whose work breakdown has progress, cost, a document, child items, or activities, **When** a planner confirms replacement from an accepted schedule file, **Then** the operation is refused before any of those records change, and the reason matches the reason already given for a manual delete or a forced template replacement.
2. **Given** a locked or approved baseline and its activity rows, **When** replacement is confirmed, **Then** both the baseline and its activity rows remain, and the refusal states that approved history cannot be removed by import.
3. **Given** a project with no progress, cost, documents, activities, or locked or approved baseline, **When** an authorized planner confirms replacement, **Then** the unprotected structure may be replaced in the same recoverable way already used for a forced template replacement, and the result states what was removed and what was added.
4. **Given** the same dependent project, **When** replacement is attempted from each accepted file type, **Then** the outcome and the preserved history are the same.

---

### User Story 2 - Repeating a file does not pretend the plan changed (Priority: P1)

A planner adds a schedule, then submits the same file again, repeats the same request, or imports a file whose codes overlap what is already there. The project does not gain duplicate activities or relationships, does not gain a new empty current schedule version, and does not show a success that implies the plan changed when nothing new was added.

**Why this priority**: A second import that skips every row but publishes a new current baseline makes the current plan look replaced when it was not.

**Independent Test**: Import one file, then append it again and resubmit the completed request. Count activities, relationships, and the current schedule version before and after each action.

**Acceptance Scenarios**:

1. **Given** an existing schedule and append mode, **When** a file with overlapping activity or relationship codes is imported, **Then** those overlapping items are not created again, the result lists what was skipped, and the current schedule version stays as it was when nothing new was added.
2. **Given** a completed import request, **When** that same request is submitted again, **Then** the original outcome is shown again, the file is not applied a second time, and no second success is recorded.
3. **Given** a new confirmation of a similar file, **When** the file contains both new codes and overlapping codes, **Then** only the new codes are added, overlaps are listed as duplicates, and the result states whether the current schedule version changed.
4. **Given** a first successful import that adds schedule content, **When** it finishes, **Then** any schedule copy it records is an unapproved working copy and is not presented as the locked approved baseline.

---

### User Story 3 - An archived project stays unchanged (Priority: P1)

A project member who can edit the work breakdown opens an archived project and tries to preview, start, or confirm a schedule import. The archived project does not change. Membership and permission to edit the work breakdown do not override the archived state. A system administrator is not given any new exception.

**Why this priority**: The archive rule already makes the project read-only for everyone except the system administrator. Import was observed accepting work for a non-administrator, which bypasses that rule.

**Independent Test**: Archive a project that has schedule history. As a member with permission to edit the work breakdown, attempt preview, start, and confirm. Then repeat as a system administrator who lacks membership, and as a system administrator who is an active member with permission to import.

**Acceptance Scenarios**:

1. **Given** an archived project and a member who may edit the work breakdown, **When** that person previews, starts, or confirms an import, **Then** the project data is unchanged. Start and confirm are refused with the archived-project reason. Preview adds no schedule, progress, cost, document, or baseline data.
2. **Given** an archived project and a system administrator who is not an active member of that project, **When** that person tries to import, **Then** the import is refused. Being able to observe the project does not authorize the change.
3. **Given** an archived project and a system administrator who is an active member and has permission to import, **When** that person confirms an import, **Then** the existing archive exception applies, and the history rules in User Story 1 still apply.
4. **Given** a refusal, **When** the person reads it in Persian and in English, **Then** the reason is understandable in the active language.

---

### User Story 4 - Authority is checked again when the import is applied (Priority: P2)

A person starts an import while they are allowed to, and before it is applied they lose membership, lose permission, or the project becomes archived. The import does not continue. A person from another project cannot see the file, the preview, the import progress, or the result.

**Why this priority**: A check only at the start would let a queued import finish after access was removed, and a project identifier alone must not reveal another project's file or result.

**Independent Test**: Queue an import, remove the person's permission or archive the project, and let the import reach its apply step. Separately, sign in as a member of another project and request this project's preview, progress, and result.

**Acceptance Scenarios**:

1. **Given** a queued import, **When** the starter's active membership or import permission is gone at apply time, **Then** the import is refused, project data is unchanged, and the outcome is traceable.
2. **Given** a queued import for a project that is archived before apply time, **When** the starter is not allowed to change an archived project, **Then** the apply step is refused and project data is unchanged.
3. **Given** a person who is not a member of the project, **When** they request the file, preview, progress, or result, **Then** they receive nothing from that project.
4. **Given** an active member with permission on one project, **When** they submit a file for a different project, **Then** the other project is unchanged.

---

### User Story 5 - Preview, failure, and overlap leave one consistent project (Priority: P2)

A planner can preview and cancel without leaving any schedule data behind. If import fails before or during recording, the project returns to its previous state, the failure can be followed up, and a later valid file can be imported. Two overlapping confirmations, or a late reply, do not delete or replace the schedule twice and do not write into another project.

**Why this priority**: A partial schedule, a second replacement, or a result applied to the wrong project is as damaging as an unauthorized import.

**Independent Test**: Preview and cancel on a populated project and compare record counts. Force a failure before recording and a failure during recording, then import a valid file. Start two replacements together and delay one reply.

**Acceptance Scenarios**:

1. **Given** a populated project, **When** the planner previews a file and then cancels before confirming, **Then** activities, relationships, progress, cost, documents, baselines, and work-breakdown records are unchanged.
2. **Given** a failure before any recording, or a failure in the middle of recording, **When** the attempt ends, **Then** the project matches its pre-attempt state, the failure remains visible for follow-up, and a later valid import can succeed.
3. **Given** two confirmations that would replace the same project at the same time, **When** both are processed, **Then** the schedule is not removed twice and the other project is untouched.
4. **Given** a reply that arrives after the planner has moved to another project, **When** the result is shown, **Then** it remains the result of the original project and request.

---

### User Story 6 - Imported records name the person who made them (Priority: P2)

After a successful import, the planner can see who created or updated the imported work-breakdown items, activities, relationships, and schedule copy, and can see the import's project, file, mode, time, and outcome. The product does not assign that work to some other account when the real person is missing.

**Why this priority**: History that names the wrong person, or names nobody, cannot be used to answer who changed the plan.

**Independent Test**: Import as a known member and read the author on each new record and on the import history. Queue an import, remove that account before apply, and confirm no other account is written as the author.

**Acceptance Scenarios**:

1. **Given** a successful import by an active member, **When** the new work-breakdown items, activities, relationships, and schedule copy are inspected, **Then** each one names that member as creator or editor, and the import history names the member, time, project, file, mode, and outcome.
2. **Given** a queued import whose starter no longer exists when it is applied, **When** the apply step runs, **Then** the import is refused, no domain records are written, and no other account is substituted as the author.
3. **Given** an import that was refused or failed, **When** someone reviews the import history, **Then** the attempt is still identifiable without attributing project changes to an unrelated person.

---

### Edge Cases

- A successful import of an empty project does not prove that a project with history is safe.
- Replacement is all or nothing. A mix of protected and unprotected items does not leave part of the schedule deleted.
- An unapproved working copy created by an earlier import is not treated as a locked approved baseline. Replacing a project that has only that unprotected working copy follows the unprotected replacement rule and states the effect on the current schedule version.
- A suspended, draft, or completed project keeps its existing baseline and commitment rules. This feature does not relax them.
- Overlapping codes inside one file are skipped and listed. They do not create a second activity or relationship.
- A refused replacement still lets the planner import later by appending, or by replacing only after the blocking history is no longer at risk under the existing rules.
- Confirmation of a destructive replacement shows the refusal reason in the import journey before data changes.
- A person who loses access after preview, but before confirm, cannot confirm that preview into the project.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Replacement from every accepted schedule file type MUST preserve activities, progress, cost, documents, and locked or approved baseline rows. If that preservation cannot be guaranteed by the protection already used for manual work-breakdown deletion and forced template replacement, the replacement MUST be refused before any project data changes, with a specific reason.
- **FR-002**: The refusal reason for a protected replacement MUST be the same kind of reason already shown when a manual delete or a forced template replacement is blocked by children, activities, progress, cost, or documents, plus a distinct reason when a locked or approved baseline would be lost.
- **FR-003**: A project with no blocking dependency and no locked or approved baseline MAY be replaced. Removal of that unprotected structure MUST be recoverable in the same way as a forced template replacement, and the result MUST state what was removed and what was added.
- **FR-004**: Append, a repeated file, a repeated request, and overlapping codes MUST NOT create duplicate activities or relationships, MUST NOT publish a new current schedule version when nothing new was added, and MUST NOT record a success that implies the plan changed when it did not.
- **FR-005**: Submitting the same completed import request again MUST return the original outcome and MUST NOT apply the file again. A newly confirmed import of a similar file is a separate action and follows append or replacement rules.
- **FR-006**: The result of every completed or refused import MUST state the duplicate or skipped items and the effect on the current schedule version.
- **FR-007**: A schedule copy created by a successful import MUST be an unapproved working copy. It MUST NOT be presented as a locked approved baseline, and it MUST NOT erase an existing locked or approved baseline.
- **FR-008**: An archived project MUST NOT be changed by preview, start, confirm, or later application when the actor is not allowed to change archived projects. Active membership and permission to edit the work breakdown MUST NOT override the archived state.
- **FR-009**: A system administrator MUST NOT gain a new archive exception. Observation of a project MUST NOT authorize import. Import into an archived project remains available only to a system administrator who already has active membership and permission to import, and the history rules still apply.
- **FR-010**: Active membership, permission to import, project scope, and the project's operational status MUST be checked again when the import is applied. A change after the import was queued MUST be honored.
- **FR-011**: A person outside the project MUST NOT see that project's import file, preview, progress, or result, and MUST NOT change that project by submitting a file.
- **FR-012**: Preview and cancel before confirm MUST create no work-breakdown, activity, relationship, progress, cost, document, or baseline data.
- **FR-013**: Failure before recording and failure during recording MUST restore the project to its pre-attempt state, leave a followable failure outcome, and leave a later valid import possible.
- **FR-014**: Concurrent confirmations and a late reply MUST NOT apply replacement twice and MUST NOT change a different project. The visible result stays bound to the original project and request.
- **FR-015**: Imported work-breakdown items, activities, relationships, and schedule copies MUST name the member who confirmed the import. If that member cannot be resolved when the import is applied, the import MUST be refused with no domain records written and no substitute account.
- **FR-016**: Import history MUST show the acting member when known, the time, project, file, mode, and outcome, including refusal and failure, without attributing a change to an unrelated person.
- **FR-017**: User-facing refusal and result text MUST be understandable in Persian and in English, following the active language. The stable meaning of each outcome MUST stay the same in both languages.
- **FR-018**: Field-by-field schedule fidelity, a new schedule-versioning scheme, an independent spreadsheet importer, a rewritten preview, a live Primavera connection, and any weakening of the current access policy are outside this feature.

### Key Entities

- **Schedule import attempt**: One preview or confirmed import of an accepted schedule file into one project, with a mode of append or replacement, a starter, a file identity, a project, a status, and an outcome.
- **Work-breakdown item**: A scope node that may block replacement when it has children, activities, progress, cost, or documents.
- **Activity and relationship**: Schedule items that must not be duplicated by append or repeat, and must not be destroyed when progress, cost, documents, or a locked baseline depend on them.
- **Approved baseline**: The locked approved snapshot and its activity rows. Import must not empty or replace it.
- **Working schedule copy**: An unapproved copy that a successful adding import may record. It is not the approved baseline.
- **Import attribution**: The member responsible for created or updated imported records, distinct from any other account in the organization.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100% of trials on a project that has activities, progress, cost, a document, and a locked approved baseline, confirmed replacement leaves every one of those records in place and shows a specific refusal reason before any change.
- **SC-002**: The same protected project produces the same preserved outcome for every accepted schedule file type.
- **SC-003**: In 100% of repeat and overlap trials, no duplicate activity or relationship is created, and a run that adds nothing does not publish a new current schedule version or a success that claims the plan changed.
- **SC-004**: In 100% of archived-project trials, a member who is not a system administrator sees no change in project data after preview, start, and confirm.
- **SC-005**: In 100% of trials where membership, permission, or archived status changes after the import is queued, the applied result leaves project data unchanged.
- **SC-006**: In 100% of cross-project trials, the other person sees no file, preview, progress, or result, and the other project is unchanged.
- **SC-007**: In 100% of preview-and-cancel, pre-recording failure, and mid-recording failure trials, project record counts match the pre-attempt state and a later valid import can finish.
- **SC-008**: In 100% of overlapping confirmation trials, the schedule is removed at most once and no other project changes.
- **SC-009**: In 100% of successful imports, every new imported record names the confirming member, and in 100% of missing-member trials no substitute account is written.
- **SC-010**: A planner can see the replacement refusal, in Persian and in English, during the import confirmation journey, before project data changes.
- **SC-011**: A passing import on an empty project is not accepted as evidence that a project with history is safe.

## Assumptions

- Phase 1 (`specs/051-a7-p1-project-reference`) is ready for review. Its handoff says the importer was not changed. Its remaining limits are outside this feature, so this specification proceeds on that integrated work. The 2026-11-10 audit is historical evidence of the risk, not proof of today's behavior.
- The safe path already approved for dependent work breakdowns is refusal, as specified for manual deletion and for forced template replacement. This feature uses that path for file replacement. It does not add a new schedule-versioning scheme and does not delete history in order to finish the import.
- A locked or approved baseline has no existing import path that can remove activities while keeping the baseline rows. Replacement is therefore refused before any change when that history would be lost. A new approved baseline still comes only from the existing schedule change process.
- Exact replay of one completed request is distinct from a new confirmation of a similar file. That distinction already exists for confirmed project actions: replay returns the original outcome, and a new confirmation is judged again.
- The archive contract makes an archived project read-only for anyone who is not a system administrator. The constitution still requires active membership and the operation's permission before a change. Those two rules together are the administrator boundary. No additional exception is created.
- Accepted schedule files remain the file types the product already accepts for this import journey. How fields inside those files are mapped belongs to the next stage.
- Preview behavior stays as it is: opening and cancelling it must not write domain data. This feature does not replace the preview itself.
- An import that adds real new schedule content may still record an unapproved working copy, because that is the current product outcome of a successful adding import. A repeated or empty result must not add another current copy.
- Refusal and result wording must be stable enough for a later stage to show them. This specification defines the outcomes; it does not define field-mapping fidelity or a new importer.
- Tests that prove this feature must include a project that already has history. An empty project is only the unprotected replacement case.
- `SPECIFY_FEATURE_DIRECTORY`, SpecKit, and embedding job are process words in the stage prompt. They are not product records.
