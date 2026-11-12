# Feature Specification: Schedule Import Experience

**Feature Branch**: `054-a7-p4-import-experience`

**Created**: 2026-11-12

**Status**: Draft

**Input**: User description: "A.7-P4 — complete the existing schedule import journey so an authorized planner can see what will be imported, what will change, and what must be corrected. Audit owners: I02, I10, I15, I16, I17. Source prompt: output/a7-requirements-2026-11-10/speckit-prompts/04-import-experience.md. Source requirement: specs/029-native-mpp-import FR-003, FR-007, FR-012, FR-015, FR-016, FR-017, and SC-008."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Confirm a file the planner can recognize (Priority: P1)

An authorized planner chooses one schedule file in the existing import journey, sees which accepted kind it is, sees the work packages and activities that would be stored, chooses add or replace, and confirms only when the file name, the kind, the mode, the structure, the warnings, and any blocking reason are visible. Changing the file throws away the previous preview. Leaving before confirmation does not change the project.

**Why this priority**: A planner who confirms the wrong file, the wrong mode, or a stale preview can replace or extend the live schedule without knowing what will change.

**Independent Test**: For one readable file of each accepted kind, walk from file choice through preview to the confirmation step without confirming. Check that the file name, kind, mode, and structure are visible, that a different file cannot reuse the previous preview, and that the project is unchanged after leaving.

**Acceptance Scenarios**:

1. **Given** an authorized planner on a project they may import into, **When** they choose a readable Microsoft Project file, Microsoft Project XML file, or Primavera schedule exchange file, **Then** the journey names that file, names the accepted kind it recognized, and prepares a preview before any confirmation.
2. **Given** a prepared preview, **When** the planner looks at the confirmation step, **Then** they see the file name, the chosen mode, the work packages and activities that would be stored, every warning, and any blocking reason. Confirmation is not available while a blocking reason is present.
3. **Given** a prepared preview, **When** the planner chooses a different file or goes back to change the file, **Then** the previous preview cannot be confirmed and a new preview is required before confirmation.
4. **Given** a preview that has not been confirmed, **When** the planner cancels or closes the journey, **Then** the project's work packages, activities, and relationships are unchanged.
5. **Given** add and replace, **When** the planner chooses a mode, **Then** the choice states whether the file will be added beside the current schedule, skipping duplicates, or will replace the current schedule when replacement is allowed.
6. **Given** this feature is in use, **When** the planner imports a schedule, **Then** they still use this same journey, the same permission, and the same replacement protection. The feature does not add a spreadsheet import, a new preview product, a live Primavera connection, or an earned-value or finance report.

---

### User Story 2 - Read a result that matches what was stored (Priority: P1)

After an informed confirmation, the planner sees that the save is in progress, then a result whose figures match the saved project and the hand-counted reference for that file. The result separates rows read, rows created, duplicates, rows skipped or rejected, work packages, activities, relationships actually kept, and rows removed by an allowed replacement. Each warning names its reason and the row it refers to. A number prepared before the rows are kept is not presented as the number stored.

**Why this priority**: A result that counts attempted relationships, or hides an omitted row, makes the stored schedule look complete when it is not. The planner cannot reconcile the file with the project.

**Independent Test**: Confirm one authored file with a known hand count, including at least one duplicate and one omitted relationship. Compare every displayed figure with the saved project and with the hand-counted reference. Repeat once where nothing new is stored.

**Acceptance Scenarios**:

1. **Given** a confirmed file, **When** the save finishes, **Then** the result shows rows read, rows created, duplicates, rows skipped or rejected, work packages, activities, relationships actually kept, and rows removed by an allowed replacement.
2. **Given** a relationship that was not kept, **When** the planner reads the result, **Then** that relationship is not included in the stored-relationship figure, and the warning names the reason and the row.
3. **Given** a preview and the finished result for the same file and mode, **When** the planner compares them with the saved project and the hand-counted reference, **Then** the figures and the warning reasons agree. A difference is visible and explained.
4. **Given** a file that contains something the product will not keep, such as an unsupported calendar or an omitted row, **When** the planner reads the preview and the result, **Then** that omission is visible. It does not need its own new field for every source column.
5. **Given** an add that stores nothing new, **When** the result is shown, **Then** it says the plan did not change. It does not say the import succeeded in changing the schedule.
6. **Given** a finished result that stored work, **When** the planner continues, **Then** they can open the work breakdown and the activities stored by that attempt without starting another import.
7. **Given** a finished result, **When** the planner reads it, **Then** every warning for that attempt is in the result and can be read in full. The result does not include wages, pay rates, or confidential contact details, and the planner does not need a separate discrepancy document.

---

### User Story 3 - Recover in the active language (Priority: P1)

A warning looks different from a blocking failure. File-type, corrupt, password-protected, too-large, unsupported, timeout, permission, project-status, duplicate, and save-failure messages are written in the language the planner is using, Persian or English, and say what to do next. The planner can choose another file, go back and correct the choice, retry when a retry is allowed, or read the result. The planner does not see an internal error name or an untranslated failure text as the message.

**Why this priority**: A fixed Persian sentence, or a raw failure name, leaves an English-speaking planner without a next step and leaves a Persian-speaking planner unable to trust a mixed result.

**Independent Test**: In Persian and again in English, produce one warning, one blocking preview, one refused replacement, and one rejected file of each named kind that can be produced safely. Confirm the message, the distinction, and the offered next step. Confirm the project is unchanged after each rejection or refusal.

**Acceptance Scenarios**:

1. **Given** the journey in Persian, **When** a warning, a blocking reason, a result, or a rejection is shown, **Then** the planner can read it in Persian. **Given** the same case in English, **Then** the planner can read the same meaning in English.
2. **Given** a non-blocking warning, **When** it is shown beside a blocking failure, **Then** the two are visually distinct, and every final warning can be read in full with its row.
3. **Given** a file that is the wrong kind, corrupt, password-protected, too large, or unsupported, **When** it is rejected, **Then** the message names that situation and a next step, and the project is unchanged. A password-protected file is not opened by guessing or removing the password.
4. **Given** a timeout, a refused permission, a project that is not open for import, a duplicate, or a failed save, **When** the planner sees the message, **Then** it is specific to that situation and tells the planner what they can do next.
5. **Given** a rejected or refused attempt that did not change the project, **When** the planner continues, **Then** they can choose another file, return to correct the choice, and try again when a retry is allowed.
6. **Given** a replacement that the product refuses because the current schedule has history that must be kept, **When** the planner confirms replace, **Then** the journey says why the replacement was refused, stays on a recoverable step, and leaves the project unchanged.

---

### User Story 4 - One attempt stays one attempt (Priority: P2)

While a preview is being prepared or a save is starting, another click, another file choice, and a dropped file do not start a second attempt or replace the file of the attempt already underway. Closing the journey, or switching project or account after submission, does not display a success that did not happen and does not claim the attempt was cancelled. A lost connection is not shown as a finished failure. The planner can recover the real outcome of that same attempt, and a safe retry does not store the file twice.

**Why this priority**: A second drop during processing, or a late result attached to the next project, can import the wrong file or convince the planner that a failed save succeeded.

**Independent Test**: During preview and again during the start of a save, click again, choose a second file, and drop a second file. Separately, submit one file, switch project, and wait for the first attempt to finish. Separately, interrupt the connection and then recover the same attempt. Compare the stored project with one intended attempt.

**Acceptance Scenarios**:

1. **Given** a preview or a save that has started, **When** the planner clicks again, chooses a second file, or drops a second file, **Then** no second attempt starts and the file of the attempt already underway does not change.
2. **Given** a submitted attempt, **When** the planner closes the journey or switches project or account before the outcome is known, **Then** the screen does not show a success that has not happened and does not say the attempt was cancelled. The attempt remains the file, mode, and project that were confirmed.
3. **Given** a result that arrives after the planner has selected another file, project, or account, **When** it is shown, **Then** it is not presented as the outcome of that newer file, project, or account.
4. **Given** a lost connection while the attempt is unfinished, **When** the planner looks at the journey, **Then** the screen does not say the attempt has failed. The planner can recover the real outcome of that attempt.
5. **Given** an attempt that is still in progress for the same person, project, mode, and file, **When** the planner retries, **Then** the retry returns that same attempt and does not store the file a second time. A later, deliberate confirmation is judged again. Asking for the status of a finished attempt does not import the file again.

---

### User Story 5 - Complete the journey by keyboard in both directions (Priority: P2)

The planner can complete a successful import and a recoverable failure with the keyboard only, in Persian right-to-left and English left-to-right, on a desktop screen and on a phone-width screen. File names, codes, dates, and long messages stay readable. Focus and labels identify the file choice, the mode, and the confirmation. This journey does not add a date picker. Any date control the journey does change reopens and keeps its value in both languages.

**Why this priority**: Office and field users switch language and screen size. A journey that can be completed only with a pointer, or only in one direction, blocks the same import the figures are meant to explain.

**Independent Test**: With a keyboard only, complete one success and one recoverable rejection in Persian and in English, on a desktop screen and on a phone-width screen. Read a long file name, a code, a date, and a long message in each combination.

**Acceptance Scenarios**:

1. **Given** Persian right-to-left and English left-to-right, **When** the planner uses only the keyboard, **Then** they can choose a file, reach the preview, choose a mode, confirm or recover from a rejection, and open the resulting work breakdown.
2. **Given** a desktop screen and a phone-width screen, **When** the same two journeys are repeated, **Then** the file name, codes, dates, and a long message remain readable and the primary actions remain reachable.
3. **Given** a step change, **When** the planner moves by keyboard, **Then** focus moves to the new step and each control has a name that says what it does.
4. **Given** a date shown by this journey, **When** the language is Persian or English, **Then** the date is shown in that language. **Given** a date control this journey changes, **When** the planner reopens it in each language, **Then** the chosen date is still the date that was saved.

---

### Edge Cases

- A second file is dropped, chosen, or clicked while a preview is being prepared or a save is starting. The file already underway stays the file of that attempt.
- The planner changes the file after a preview. The old preview cannot be confirmed, and a late result from the old file is not shown as the new file's result.
- The planner confirms replace on a project whose history must be kept. The replacement is refused, the reason is readable, and the project is unchanged.
- The planner adds a file whose codes are already stored. Duplicates are counted as duplicates, relationships that were not kept are not counted as stored, and an unchanged plan is not called a successful change.
- The file is empty, corrupt, password-protected, too large, the wrong kind, or not a genuine schedule file despite its name. The message names the situation. The project is unchanged. A later valid file can still be imported.
- The save takes too long, the planner no longer has permission, or the project is archived or otherwise not open for import. Each case has its own message and a next step. None of these is shown as a successful import.
- The connection drops before the outcome is known. The journey does not call that a finished failure. When the connection returns, the planner sees the real outcome of the same attempt.
- The planner closes the journey or switches project or account after submission. The attempt is not described as cancelled, and its result is not attached to the new project or account.
- A warning list or file name is very long. The planner can read the whole warning and identify the file. Latin codes and file names remain readable in right-to-left layout.
- The planner uses only the keyboard on a phone-width screen, in each language, for both a success and a recoverable rejection.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The product MUST complete the existing schedule import journey for a readable Microsoft Project file, Microsoft Project XML file, and Primavera schedule exchange file. The journey MUST cover file choice, recognized kind, preview, structure, add or replace, informed confirmation, progress, result, and a way to open the stored work breakdown and the activities stored by that attempt. The product MUST NOT add a second import journey.
- **FR-002**: Before confirmation, the planner MUST see the file name, the recognized kind, the chosen mode, the work packages and activities that would be stored, every warning, and any blocking reason. Confirmation MUST be unavailable while a blocking reason is present. Add MUST be described as keeping the current schedule and skipping duplicates. Replace MUST be described as replacing the current schedule only when replacement is allowed.
- **FR-003**: Changing the selected file, or going back to change it, MUST invalidate the previous preview. That previous preview MUST NOT be confirmable. A result that finishes after the planner has changed file, project, or account MUST NOT be presented as the outcome of the newer file, project, or account.
- **FR-004**: Leaving the journey before confirmation MUST leave the project's work packages, activities, and relationships unchanged.
- **FR-005**: The preview and the finished result MUST show rows read, rows created, duplicates, rows skipped or rejected, work packages, activities, relationships actually kept, and rows removed by an allowed replacement. A figure prepared before those rows are kept MUST NOT be shown as the number stored. A relationship that was not kept MUST NOT be included in the stored-relationship figure.
- **FR-006**: For the same file and mode, the preview figures, the finished result, the saved project, and the hand-counted reference for that file MUST agree. A difference MUST be visible and MUST name its reason. Data the product will not keep MUST be visible as an omission or warning. The product MUST NOT add a separate control for every source column.
- **FR-007**: A finished attempt that stores nothing new MUST say the plan did not change. A refused replacement MUST NOT be shown as a successful replacement. From a result that stored work, the planner MUST be able to open the work breakdown and the activities stored by that attempt without starting another import.
- **FR-008**: A warning MUST be visually distinct from a blocking failure. Every final warning MUST be fully readable and MUST name its reason and the row it refers to when a row is known. A blocking failure MUST stop confirmation or end as a failed result, and MUST name a next step.
- **FR-009**: The on-screen result MUST be the discrepancy record for the attempt. Every warning in that result MUST be readable there. The result MUST NOT add wages, pay rates, confidential contact details, or other sensitive fields. This feature MUST NOT add a separate discrepancy export.
- **FR-010**: Messages for the wrong file kind, a corrupt file, a password-protected file, a file that is too large, an unsupported file, a timeout, a refused permission, a project that is not open for import, a duplicate, and a failed save MUST follow the active Persian or English language, name that situation, and name a next step. The message the planner reads MUST NOT be an internal error name or an untranslated failure text. A password-protected file MUST NOT be decrypted.
- **FR-011**: After a rejection or a refusal that left the project unchanged, the planner MUST be able to choose another file, return to correct the choice, and retry when a retry is allowed. After success, the planner MUST be able to read the result.
- **FR-012**: While a preview is being prepared or a save is starting, another click, another file choice, and a dropped file MUST NOT start a second attempt and MUST NOT replace the file of the attempt already underway. The file name of the attempt underway MUST stay visible.
- **FR-013**: Closing the journey, or switching project or account, after the planner has submitted MUST NOT display a success that has not happened and MUST NOT say the attempt was cancelled. The attempt MUST keep the file, mode, and project that were confirmed.
- **FR-014**: A lost connection during an unfinished attempt MUST NOT be shown as a finished failure. The planner MUST be able to recover the real outcome of that same attempt. A retry while that attempt is still in progress for the same person, project, mode, and file MUST return that attempt and MUST NOT store the file twice. A new confirmation after the attempt is finished MUST be judged again. Reading the status of a finished attempt MUST NOT import the file again.
- **FR-015**: The planner MUST be able to complete a successful import and a recoverable rejection with the keyboard only, in Persian right-to-left and English left-to-right, on a desktop screen and on a phone-width screen. Focus MUST move to the active step, and the file choice, mode, and confirmation MUST have names that say what they do. File names, codes, dates, and long messages MUST stay readable.
- **FR-016**: Dates shown in this journey MUST follow the active language. This feature MUST NOT add a date picker. If this journey changes a date control, that control MUST reopen and keep the chosen date in both Persian and English.
- **FR-017**: Who may import, which history blocks replacement, the meaning of each imported row, and the rule that a preview writes nothing MUST stay as already decided. This feature MUST NOT add a spreadsheet import for the work breakdown, a new preview product, a live Primavera connection, an earned-value or finance report, or a weaker access rule.

### Key Entities

- **Import journey**: The existing path from file choice through preview, mode, confirmation, progress, and result. This feature completes that path.
- **Selected schedule file**: One file the planner chose, identified by its name and recognized kind, whose preview belongs only to that file.
- **Preview**: What would be stored if the planner confirms this file and mode, including structure, warnings, blocking reasons, and control figures. It does not itself change the project.
- **Import mode**: Add, which keeps the current schedule and skips duplicates, or replace, which replaces the current schedule only when the existing protection allows it.
- **Import attempt**: One confirmed save for one file, one mode, and one project. A later result belongs to that attempt only.
- **Control figures**: Rows read, rows created, duplicates, rows skipped or rejected, work packages, activities, relationships actually kept, and rows removed by an allowed replacement.
- **Warning**: A non-blocking explanation of a row or fact that was omitted or not applied, distinct from a blocking failure.
- **Blocking outcome**: A reason that prevents confirmation or ends the attempt without the offered change, including a refused replacement and a rejected file.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For each accepted schedule file kind, a planner completes one real journey from file choice to the stored work breakdown, and every displayed control figure matches the saved project and the hand-counted reference for that file.
- **SC-002**: In 100% of compared trials, the stored-relationship figure equals the relationships actually kept. A figure prepared before the save is not presented as the stored figure.
- **SC-003**: In 100% of warning trials, every warning text and its row are fully readable and visually distinct from a blocking failure. In 100% of blocking, rejection, and refused-replacement trials, the project is unchanged and the message names a next step in the active language.
- **SC-004**: In 100% of trials during preview preparation or save start, a second click, a second file choice, or a second drop does not create a second attempt or change the file of the attempt underway.
- **SC-005**: In 100% of trials where the file, project, or account changes before a late result arrives, that result is not shown as the outcome of the newer file, project, or account.
- **SC-006**: In the interrupted-connection trial, the journey does not label the unfinished attempt as a finished failure. The planner can see the real outcome of that attempt, and a retry does not store the file twice.
- **SC-007**: A keyboard-only success and a keyboard-only recoverable rejection both succeed in Persian and in English, on a desktop screen and on a phone-width screen.
- **SC-008**: An employer reviewer, using one short illustrated guide and no developer present, can judge one success, one warning, one recoverable rejection, one refused replacement, one interrupted response, and one prevented double submit, in Persian and in English.

## Assumptions

- The accepted schedule files remain the Microsoft Project file, the Microsoft Project XML file, and the Primavera schedule exchange file already accepted by the import journey. Excel and CSV import of the work breakdown stay outside the approved delivery boundary unless a later scope decision adds them.
- This feature extends the existing import journey and its preview. It does not replace that preview with a new product, and it does not open a live Primavera connection.
- The on-screen result is enough as the discrepancy record. A separate download is not required, because every warning is readable in the result. That avoids a new report. If a warning cannot be read in full on screen, the result itself must be extended until it can. No sensitive fields are added.
- The phase-1 reference is ready for review. Its hand-counted examples, and the unchanged employer schedule file identified by the recorded fingerprint, are the comparison baseline. The 2026-11-10 audit, including the historical observation of 83 source links and 79 stored relationships, is history. It is not the pass target. Phase 3 already decided that the four summary predecessors are reported and are not stored as activity links, and that a file calendar is reported as not applied.
- Phase 2 and phase 3 now have explicit [safety](../052-a7-p2-import-safety/handoff.md) and [fidelity](../053-a7-p3-import-fidelity/handoff.md) handoffs declaring the integrated local baseline ready, with verification limits (2026-11-12). Their safety and fidelity outcomes remain the baseline: protected history is not replaced, a preview and a cancel write nothing, an unchanged repeat is not a new current plan, an archived project stays closed to import except for the already decided administrator case, and preview figures mean the same outcome as the saved result. The user confirmed omission of parentless employer rows with row warnings; zero duration is stored only for activities with valid source parents. Checkmarks and verification notes alone do not replace those handoffs. T002 verifies both handoffs before this feature's implementation continues.
- Safe retry is the rule already accepted for an import attempt: the same person, project, mode, and file still in progress return that attempt; a finished attempt is not silently reused; a new confirmation is judged again.
- A lost connection means the outcome is not yet known. This feature does not add a new way to cancel an attempt after it has been submitted.
- Who may import stays active project membership plus permission to edit the work breakdown. Seeing a project is not permission to import it. This feature does not weaken that rule.
- The journey shows dates in the active language. It does not add or change a date picker. The constitution's reopen-and-persist check applies only if a date control is actually changed.
- A short illustrated guide is a delivery aid for the employer review of this journey. It is not a new in-product tour.
- The November 10 audit describes the journey as it was then. It is not evidence of the journey on the day this specification was written. Today's journey still needs this specification because the result the planner sees does not yet present every control figure required above, and a second file can still be dropped while a preview or save is underway.
