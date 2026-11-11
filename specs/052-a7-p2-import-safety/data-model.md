# Data Model: Import Safety and History

No new table and no migration. The rules below bind existing records.

## Schedule import job

Existing `MspImportJob` and `P6ImportJob`.

| Fact | Rule |
| --- | --- |
| Identity | The job id is the import request. Reading it again returns the stored status, result, and error. |
| Project | Set at creation and never retargeted. Status lookup includes the project id. |
| Actor | `created_by` is the confirming member. If it is missing when the job is applied, the job fails with `import_actor_missing` and no domain rows are written. |
| Mode | `replace_existing` false means append. True means replacement, which still passes the safety gate. |
| File | Bytes stay on the job. An in-flight match uses a hash of those bytes plus project, actor, and mode. The hash is not stored. |
| Outcome | `pending`, `running`, `done`, or `failed`. `done` with nothing created is still a finished attempt, and its result says the plan did not change. |
| Error | `error_code` and `error_message` remain after refusal or failure. |

## Work-breakdown node, activity, and relationship

| Fact | Rule |
| --- | --- |
| Creation | New rows from a successful adding import set `created_by` and `updated_by` to the confirming member. |
| Duplicate code | An existing live code in the same project is left unchanged and listed as skipped. |
| Protected replacement | No row is soft-deleted or hard-deleted when progress, cost, a document, a live activity, or a locked or approved baseline is present. |
| Unprotected replacement | Live activities and live nodes are soft-deleted by the confirming member, deepest node first. Relationships on those activities go with the existing activity soft-delete behavior. Hard delete is not used. |
| Other projects | A job never reads or writes another project's nodes, activities, relationships, or baselines. |

## Baseline

Existing `BaselineSchedule` and `BaselineActivity`.

| Fact | Rule |
| --- | --- |
| Locked or approved | `is_locked` or a non-empty `approved_at` blocks replacement before any write. Header and activity rows stay. Import does not clear `is_current` on that baseline. |
| Working copy | Created only when the attempt adds at least one node, activity, or relationship. `is_locked` stays false and `approved_at` stays empty. |
| Current flag | The working copy becomes current only when the project has no locked or approved current baseline. Otherwise it is stored with `is_current` false. |
| Empty attempt | No baseline row is created. |
| Actor | `created_by` and `updated_by` are the confirming member. There is no fallback user. |

## Project operational state

The project row is locked at apply time. Archive, membership, and `edit_wbs` are read from that locked row and the current membership. A change made after queueing is visible to that check. Draft, suspended, and completed projects keep their existing baseline and commitment rules; this feature does not add a transition.

## Result object

Stored on the job when the attempt finishes without an exception. Field list and error codes are in [contracts/import-safety.md](contracts/import-safety.md).

## State of one confirmed import

1. Start validates the file and creates a job, or returns the in-flight job with the same hash.
2. Apply locks the project, rechecks the actor and archive, and either refuses or writes inside the existing transaction.
3. Refusal or a mid-write exception leaves domain rows as they were before that attempt and marks the job failed.
4. A later valid job for the same project can run. It does not reuse a failed or completed job.
