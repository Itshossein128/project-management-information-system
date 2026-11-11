# Contract: Schedule import safety

This contract is the refusal and result vocabulary for the existing MSP/MPP and P6 confirm paths. It does not change file parsing or preview contents. A later stage can show these fields without inventing new outcomes.

Both families use the same codes and the same result fields. Preview does not create a job and does not write project data.

## Start

The confirm call keeps its current acceptance of the file and of `replace`.

Before a new job is queued, the server refuses when the caller cannot import into the project now. An archived project returns `project_archived` unless the caller is a system administrator with active membership and `edit_wbs`. Any other missing membership or permission stays the current permission refusal.

When a pending or running job already exists for the same project, user, mode, and file bytes, the response returns that job's id and does not queue another apply.

A new confirm after a completed job is a new job.

## Apply

The apply step repeats the archive, membership, permission, and actor checks. It then applies the replacement gate when the mode is replacement.

Failure before any domain write, and failure during the write, leaves the project as it was before that attempt. The job remains available to the same project's authorized reader with `failed`, `error_code`, and `error_message`.

Two applies for one project run one after the other. Neither writes to a different project. A late status response stays the body of the job that was requested.

## Error codes

| Code | When | Project data |
| --- | --- | --- |
| `project_archived` | The project is archived and the caller is not an active system-administrator member with `edit_wbs`. | Unchanged |
| `import_not_permitted` | At apply time the starter is no longer an active member or no longer has `edit_wbs`. | Unchanged |
| `import_actor_missing` | The job has no resolvable confirming user. | Unchanged |
| `wbs_has_progress` | Replacement would meet recorded progress. | Unchanged |
| `wbs_has_cost` | Replacement would meet cost records. | Unchanged |
| `wbs_has_documents` | Replacement would meet a linked document. | Unchanged |
| `wbs_has_activities` | Replacement would meet live activities. | Unchanged |
| `baseline_history_protected` | Replacement would meet a baseline with `is_locked` or `approved_at`. | Unchanged |

Existing file, size, password, and parse codes stay as they are. Messages for the codes in this table are available in Persian and English. The code itself does not change with language.

The first matching protection code is enough. The server does not need to list every blocker.

## Result fields

Present on a finished attempt that stored a result:

| Field | Meaning |
| --- | --- |
| `wbs_nodes_created` | Nodes actually created |
| `activities_created` | Activities actually created |
| `relations_created` | Relationships actually inserted |
| `wbs_nodes_removed` | Nodes soft-deleted by an allowed replacement. Zero for append and for a refusal |
| `activities_removed` | Activities soft-deleted by an allowed replacement. Zero for append and for a refusal |
| `duplicates` | Codes or relationship keys that were skipped because they already exist |
| `warnings` | Existing human-readable warnings, including duplicate skips |
| `schedule_version_changed` | True only when a new current working copy was stored |
| `baseline_id` | The working copy created by this attempt, or null |
| `nothing_changed` | True when no node, activity, or relationship was created or removed |

A refusal does not use this object as a success. It uses the error code. `nothing_changed` true must not be displayed as a changed plan.

## Visibility

A caller who is not an active member of the job's project, and who is not allowed the existing observation read, receives no file, preview, progress, or result for that job. A job id from another project is not a result for this project.

## Out of this contract

Field mapping, warning translation beyond these refusals, spreadsheet import, preview layout, and live Primavera sync.
