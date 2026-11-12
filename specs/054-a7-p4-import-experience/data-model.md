# Data Model: Schedule Import Experience

No new table and no migration. Preview writes nothing. The import job already stores status, progress, file name, mode, result, and error code.

## Display figures

These fields are added to the preview body and to the finished job result. They do not replace `wbs_nodes_created`, `activities_created`, or `relations_created`.

| Field | Meaning | When it is zero |
| --- | --- | --- |
| `rows_read` | Schedule rows in the file before omission | An empty file is rejected before a preview |
| `relationships_kept` | Links that will be inserted, or that were inserted | Every link was omitted or already stored |
| `duplicate_count` | Existing codes and already stored links | Nothing in the file matches the project |
| `rows_omitted` | Omitted rows and links that are not duplicates | Every accepted row is kept |

`rows_omitted` is the current `omitted_count`. The screen uses that meaning and does not show a second number.

Removed figures already exist on the finished result: `wbs_nodes_removed`, `activities_removed`, `relations_removed`. Add stays at zero. Replace uses the projection below, then the result after the write.

## Replacement projection

Present on every preview. Not stored as a job.

| Field | Meaning |
| --- | --- |
| `replacement.blocked` | The first existing protection code, or null when replace is allowed |
| `replacement.wbs_nodes_removed` | Live work packages the current replace path would soft-delete. Zero when blocked or when the planner chooses add |
| `replacement.activities_removed` | Live activities in that same case |
| `replacement.relations_removed` | Live relationships in that same case |

The screen shows the removed numbers only while replace is selected. Confirm stays disabled when `replacement.blocked` is set or the file preview has `blocking` entries. The start call still enforces the gate.

## Recognized kind

| Code | Shown after a preview the server accepted |
| --- | --- |
| `mpp` | Native Microsoft Project file |
| `xml` | Microsoft Project XML |
| `xer` | Primavera schedule exchange |

A rejected upload has no `recognized_kind`.

## Warning and error codes

Warning items stay `{code, row}`. Codes already defined for fidelity and safety keep their meaning. This feature adds one warning code:

| Code | When | What is stored |
| --- | --- | --- |
| `duplicate_relation` | The predecessor and successor pair is already stored | The existing relationship stays. It is not counted in `relations_created` |

File, timeout, permission, archive, and replacement codes stay the codes already returned by preview and start. The screen's catalog gains translations for the codes listed in [research.md](research.md). The code string remains language-independent.

## Import attempt

One confirmed save is one job. The client remembers the open attempt so the screen can resume it. This record is not a server entity.

| Field | Rule |
| --- | --- |
| `user_id` | The account that confirmed. A different signed-in account does not read the record |
| `project_id` | The project in the confirm request. Another project does not show the result |
| `task_id` | The id returned by start, including an in-flight replay |
| `file_name` | The name of the file that was sent |
| `recognized_kind` | The kind from the preview that was confirmed |
| `replace` | The mode that was confirmed |

The record does not contain the file bytes, counts, wages, or contact details. Closing the dialog leaves the record in place. A status response is shown only when the user, project, and task id still match. Reading a finished job does not create another job.

## State of the screen

| State | What the planner sees | Project data |
| --- | --- | --- |
| Choosing a file | File name once chosen. No preview from an older file | Unchanged |
| Preparing preview | The file name and a working state. Further files are ignored | Unchanged |
| Preview | Kind, structure, figures, warnings, and blocking reasons. Add or replace | Unchanged |
| Replace refused | The protection reason. Confirm unavailable | Unchanged |
| Saving | Progress and the confirmed file name. Further files are ignored | The job is the only writer |
| Interrupted | The same file name and a way to read status again. Not a failed import | Unknown until status returns |
| Finished | Figures, full warnings, and links to the work breakdown and the activities | The job result |
| Failed | A translated code and a way to choose another file or go back | Unchanged when the job failed before or during the write |

A preview response for a file that is no longer the selected file is discarded. A status response for another task, project, or account is discarded.
