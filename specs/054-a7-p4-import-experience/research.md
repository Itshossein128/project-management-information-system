# Research: Schedule Import Experience

## One journey

**Decision**: Extend `MspImportWizard` and the current MSP/MPP and P6 preview, start, and status responses. Do not add a route, a wizard, or a parser.

**Rationale**: The screen already chooses a file, previews, offers add or replace, confirms, polls, and links to the work breakdown. The gap is what that screen says and how it behaves while a request is open. A parallel flow would leave the old one in place.

**Alternatives considered**: A new import page. Rejected because the delivery boundary says to complete the existing preview, not replace it.

## Figures the planner sees

**Decision**: Show one set of figures on the preview and on the finished result:

| Figure | Preview | Finished result |
| --- | --- | --- |
| Rows read | Source rows in the file, including rows later omitted | Same number |
| Work packages | Packages that would be created | `wbs_nodes_created` |
| Activities | Activities that would be created | `activities_created` |
| Relationships kept | Links that are not already stored | `relations_created` |
| Duplicates | Existing codes, plus links already stored | Same events |
| Skipped or rejected | Warning rows and links that are omitted and are not duplicates | Same events |
| Removed | Zero while add is selected. While replace is selected, the live rows the current soft-delete would remove, or zero when replacement is refused | `wbs_nodes_removed`, `activities_removed`, `relations_removed` |

`created_links` stays the resolver's link list and is not the number shown as stored. `relationships_kept` is that list minus links whose predecessor and successor are already stored as a pair. The result already sets `relations_created` from the rows `bulk_create` inserts. A test must show those two numbers equal for the same file and mode.

`rows_read` is `len(parsed.tasks)` at resolve time. It is stored on the plan counts so preview and the job result carry it. An unchanged result still includes it.

**Rationale**: The wizard currently copies only work packages created, activities created, and warning lines into the result. Preview already returns `counts`, and the screen does not render them. `created_links` counts every resolved link, including a link that insert will skip. Showing that number as stored would repeat the defect this feature closes.

**Alternatives considered**: Count relationships in the browser from the preview tree. Rejected because the tree does not list links and the browser cannot know which pairs are already stored. A new summary endpoint. Rejected because preview and the job result already travel with the journey.

## Replacement before confirm

**Decision**: Every preview includes a read-only `replacement` object from the existing protection check. `blocked` is the first current code, or null. When `blocked` is null, the removed counts are the live work packages, activities, and relationships the current replace path would soft-delete. When `blocked` is set, those counts are zero. Preview does not write and does not create a job. The confirm call still runs the same gate. Choosing add shows removed counts as zero. Choosing replace shows the projection, or the refusal, and disables confirm while it is refused or the file itself is blocking.

**Rationale**: The mode is chosen after the file is previewed. The planner must see the effect of replace before pressing Import. Re-sending the file for a second preview would repeat the parse. The protection check is already a read.

**Alternatives considered**: Show the refusal only after Import is pressed. Rejected because the specification requires the removal figures on the preview when replace is the chosen mode. Trust the browser to count live rows. Rejected because the server decides which rows are protected.

## Recognized kind

**Decision**: Preview adds `recognized_kind` with `mpp`, `xml`, or `xer`, chosen by the parser that accepted the file. The screen translates those three codes. A rejected file does not receive a kind.

**Rationale**: The client currently chooses the P6 call from the extension, then the server validates the bytes. The label the planner trusts is the kind the accepted preview used, not the extension alone.

**Alternatives considered**: Infer the kind only from the extension. Rejected because a renamed file is rejected by content and must not be labeled as a successful kind.

## Language

**Decision**: The wizard translates `error.code` and warning `code` through `scheduleImport.codes` in `en.json` and `fa.json`. A known code never falls back to the server sentence or the code string. An unknown code uses one generic localized sentence, not the exception text. File and safety codes that the journey can already return are added to that catalog: `invalid_file_type`, `file_too_large`, `mpp_corrupt`, `mpp_password_protected`, `mpp_unsupported`, `msp_invalid_xml`, `processing_timeout`, `conversion_failed`, `import_failed`, `project_archived`, `import_not_permitted`, `import_actor_missing`, `wbs_has_progress`, `wbs_has_cost`, `wbs_has_documents`, `wbs_has_activities`, `baseline_history_protected`, and `duplicate_relation`.

The P6 preview error path returns the same `{error: {code, message}}` envelope as the MSP path, using those existing codes when the shared validators already classify the file. The form helper keeps `error.code` on the thrown error so the wizard can select the translation. Callers that only read `message` are unchanged.

Hardcoded Persian in the wizard title, the extension toast, and the status-poll failure string moves into the same catalog. The title, steps, mode, buttons, and result lines use the active language.

**Rationale**: Django messages follow the API locale, and several wizard strings do not. Phase 3 already translates failed-job codes in the browser from the stable code. File rejections still show the server sentence because the form helper drops the code. Missing catalog entries currently display the raw code.

**Alternatives considered**: Translate only on the server and render `message`. Rejected because a worker message and a fixed Persian string would still bypass the active language. A second message catalog. Rejected because `scheduleImport.codes` is the catalog this screen already uses.

## Duplicate relationships

**Decision**: When insert skips a relationship that is already stored, add warning code `duplicate_relation` with the successor code as the row. Count it as a duplicate, not as a relationship kept. Do not add an English "Duplicate" substring filter for display.

**Rationale**: `duplicate_messages` keeps human strings that contain "Duplicate" or "skipped". Those strings are not the warning items the screen translates. A skipped relationship would otherwise disappear from the result or appear only in English.

**Alternatives considered**: Reuse `duplicate_existing`. Rejected because that code means an existing work-package or activity code, and the row would be ambiguous. Leave the English string in `warnings`. Rejected because the screen must not prefer that string over the translated item.

## One attempt

**Decision**: While a preview or confirm request is in flight, ignore further clicks, file selections, and drops, and keep the file name of the request that started. A preview response is applied only when the file identity still matches the file that was sent. Confirm submits that same file and the selected mode.

The screen remembers `{user_id, project_id, task_id, file_name, recognized_kind, replace}` in `sessionStorage`. It reads that record only when the signed-in user and the open project match. A status payload is painted only for that task, user, and project. Closing the dialog does not delete the record, does not show success, and does not say the attempt was cancelled. Opening the dialog again resumes that task. A finished status can be read again and does not call start. The existing in-flight replay still returns the same task when the same person, project, mode, and bytes are submitted twice.

A network failure or an unreachable status call sets an interrupted state and keeps the file name. It does not use the fatal-error panel. Retry calls status for the remembered task. HTTP 401, 403, and a failed job with `error_code` remain real refusals.

**Rationale**: The poll treats every thrown error, including a lost connection, as a Persian failure string. Closing the dialog clears the task id, so the planner cannot resume it. The status-undo screen already binds a pending attempt to user and project in `sessionStorage` and ignores a response after the account changes. Import should follow that pattern. The server already deduplicates an in-flight start; the screen must still not swap the file under that request.

**Alternatives considered**: A new list-jobs endpoint. Rejected because status by the known task id is enough to recover the outcome. Cancel the job on dialog close. Rejected because this feature does not add cancellation after submit. Keep polling forever in a hidden global query. Rejected because the remembered task id and an explicit retry match the specification with a smaller change.

## Navigation, keyboard, and layout

**Decision**: The finished result links to the project's work breakdown and to its activities. The step heading receives focus when the step changes. The file input, mode radios, and actions stay native controls with names from the catalog. The panel uses the full width on a narrow screen, wraps the file name, and scrolls the warning list. No date control is added. The preview tree is not given new date fields.

**Rationale**: The result currently links only to the work breakdown. The file input is already keyboard reachable; the gap is focus on step change, the unguarded drop target, and a fixed dialog width. Dates are not edited in this journey.

**Alternatives considered**: Add a date picker for planned dates inside the preview. Rejected because the specification does not ask for one and a date-control change would require its own reopen and persistence proof.

## Discrepancy record

**Decision**: The on-screen result is the discrepancy record. Every warning item is rendered there, with its row, inside a scrollable list. No download and no new report type.

**Rationale**: The specification says a separate export is out of scope and that sensitive fields must not be added. The warning items are already the list.

**Alternatives considered**: A CSV of the result. Rejected as a new export.

## Handoffs

**Decision**: This design assumes the phase 2 safety result and the phase 3 fidelity plan remain the behavior being displayed. Implementation does not start until each of those features has a handoff. Their verification notes and checked tasks are not that handoff.

**Rationale**: The phase prompt requires the integrated baseline. Phase 1 has a handoff. Phases 2 and 3 do not.

**Alternatives considered**: Treat the verification notes as handoffs. Rejected because the specification says they are not.
