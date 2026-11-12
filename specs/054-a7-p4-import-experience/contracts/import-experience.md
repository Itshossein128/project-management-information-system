# Contract: Schedule import experience

This contract is the display vocabulary for the existing MSP/MPP and P6 preview, start, and status paths. It does not add a file type, a permission, a table, or a download. Field meaning, units, and safety refusals stay in [import-fidelity.md](../../053-a7-p3-import-fidelity/contracts/import-fidelity.md) and [import-safety.md](../../052-a7-p2-import-safety/contracts/import-safety.md).

Codes are language-independent. Persian and English text is presentation.

## Preview

Preview still accepts the file and writes nothing. It does not create a job.

The body adds:

| Field | Meaning |
| --- | --- |
| `recognized_kind` | `mpp`, `xml`, or `xer` for the parser that accepted the file |
| `counts.rows_read` | Source schedule rows |
| `counts.relationships_kept` | Links that are not already stored |
| `counts.duplicate_count` | Existing codes and already stored links |
| `counts.rows_omitted` | Omitted rows and links that are not duplicates. Same meaning as `omitted_count` |
| `replacement.blocked` | First protection code, or null |
| `replacement.wbs_nodes_removed` | Live packages replace would soft-delete, else 0 |
| `replacement.activities_removed` | Live activities replace would soft-delete, else 0 |
| `replacement.relations_removed` | Live relationships replace would soft-delete, else 0 |

`counts.created_links` remains the resolver link list. Clients must not present it as the number stored. Present `counts.relationships_kept` for that number.

`warning_items` and `blocking` stay `{code, row}`. A relationship that already exists is `duplicate_relation`. It is included in `duplicate_count` and excluded from `relationships_kept`.

While the planner selects add, the screen shows removed counts as zero. While the planner selects replace, the screen shows the `replacement` counts, or the translated `replacement.blocked` code with confirm disabled.

## Start and status

Start and the in-flight replay are unchanged. The same person, project, mode, and file bytes return the existing task. A finished task is not reused.

Status for a finished job returns the existing result plus `rows_read`, `relationships_kept`, `duplicate_count`, and `rows_omitted`. `relationships_kept` equals `relations_created`. `warning_items` includes every warning the planner must read, including `duplicate_relation`.

A failed job still returns `error_code`. The screen translates that code. It does not present `error_message` or an exception string as the planner's message.

P6 preview and start use the same error envelope as MSP: `{error: {code, message}}`. Known validator results use `invalid_file_type` and `file_too_large` rather than a generic validation code.

## Screen rules

- The file name, recognized kind, and selected mode are visible before confirm.
- Changing the file discards the preview. A preview response whose file is no longer selected is ignored.
- While preview or start is in flight, another click, file choice, or drop does not send another file.
- The screen remembers the task id with the user, project, file name, kind, and mode. It shows status only when all three of user, project, and task still match.
- Closing the screen does not show success and does not say the attempt was cancelled.
- A lost connection stays on an interrupted state for that task. Retry reads status. It does not call start.
- The finished result lists every figure in the table above, every warning item, and links to the work breakdown and the activities for that project.
- The result is the discrepancy record. There is no export.

## Out of this contract

Spreadsheet import, a new preview flow, a live Primavera connection, earned-value or finance reports, a date picker, a new permission, and cancellation after submit.
