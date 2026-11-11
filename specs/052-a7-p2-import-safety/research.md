# Research: A.7-P2 Import Safety

## Decision 1 — Refuse protected replacement before any delete

**Decision**: Before a replacement writes, refuse the whole operation when the project has live progress, cost, documents, or activities, or a baseline with `is_locked` or `approved_at`. Use the existing stable codes `wbs_has_progress`, `wbs_has_cost`, `wbs_has_documents`, and `wbs_has_activities`. Add `baseline_history_protected` for the baseline case. Do not delete first and repair later.

**Rationale**: `execute_msp_import` and `execute_p6_import` currently hard-delete relations, activities, and work-breakdown rows when `replace` is true. `BaselineActivity.activity` uses cascade delete, so those hard deletes empty a locked baseline while its header remains. Manual delete already refuses activities, progress, cost, and documents. Forced template replacement already refuses progress, cost, and documents. There is no existing path that can remove activities and still keep baseline rows.

**Alternatives considered**: A new baseline version that survives deletion. Rejected. The specification forbids a new versioning scheme and forbids deleting history to finish the phase. Soft-deleting activities under a locked baseline was also rejected, because the approved snapshot would no longer point at live schedule rows and the specification says that history must remain.

## Decision 2 — Unprotected replacement soft-deletes like a template

**Decision**: When the refusal check finds nothing, replacement soft-deletes live activities and then live work-breakdown nodes from the deepest node upward, with the acting user recorded. It does not call queryset `delete()`. A parent/child work-breakdown edge by itself is not a refusal. The result states how many nodes, activities, and relationships were removed and how many were added.

**Rationale**: Forced template replacement already treats a bare hierarchy as replaceable and soft-deletes it only after the dependency check passes. Treating every parent as `wbs_has_children` would make ordinary trees impossible to replace even when they hold no history. The specification's "child items" are the dependent records already named by the manual and template guards.

**Alternatives considered**: Hard delete of an empty tree. Rejected because the specification requires the same recoverable removal as template replacement.

## Decision 3 — A current baseline is published only when new schedule content is added and no approved baseline is current

**Decision**: Create the import baseline only when the attempt actually adds a work-breakdown node, activity, or relationship. Leave `is_locked` false and `approved_at` empty. Set `is_current` only when the project has no locked or approved current baseline. Otherwise create the copy with `is_current` false. An attempt that adds nothing creates no baseline and reports `schedule_version_changed: false`. The result must not be presented as a changed plan.

**Rationale**: Both executors currently create a current baseline on every success, including a repeat that skips every row. Saving that row also clears `is_current` on the previous baseline. A repeat must not do that. A first adding import may still record an unapproved working copy, which is the current product outcome, without taking the current flag from an approved baseline.

**Alternatives considered**: Never creating an import baseline. Rejected because a successful adding import is already specified to record an unapproved working copy. Always setting `is_current` true. Rejected because that demotes an approved baseline and creates the misleading empty current version.

## Decision 4 — Replay is the existing job; a new confirm is judged again

**Decision**: Reading a job by its id returns the stored outcome and does not run the import again. A new confirm creates a new job, even when the file bytes match a completed job. If the same user already has a pending or running job for the same project, mode, and file hash, the start call returns that job instead of queueing a second apply. The hash is computed in memory. No new column is added.

**Rationale**: The job id is the request the product already returns. Status retrieval is the existing replay. A later click is a new confirmation and must follow append or replacement rules. The in-flight match stops a double submit from applying replacement twice. Completed jobs are not reused, so a deliberate second import is not silently swallowed.

**Alternatives considered**: A client idempotency token and a migration. Rejected because the current confirm call has no token and the phase forbids a new versioning scheme. Treating every identical file as replay forever. Rejected because the specification separates a new confirmation of a similar file from replay of the same request.

## Decision 5 — Archive and authority are rechecked at apply time

**Decision**: Start and apply refuse an archived project unless the user is a system administrator (superuser or the `admin` group) and an active member with `edit_wbs`. Observation alone is not enough. Apply locks the project row and checks again that the user still exists, is an active member, still has `edit_wbs`, and still passes the archive rule. Failure uses `project_archived`, `import_not_permitted`, or `import_actor_missing` and writes no domain rows. Preview stays a read of the file only. It must not gain writes.

**Rationale**: Start currently checks `edit_wbs` through active membership, then the task later calls the executor with `job.created_by` and no fresh permission or archive check. `created_by` becomes null when that user is removed, and both executors then fall back to the oldest account. Membership plus `edit_wbs` does not override archive. The constitution's read exception does not grant this write. The existing archive exception remains only for a system administrator who also holds membership and permission.

**Alternatives considered**: Letting every system administrator import without membership. Rejected because that would widen the constitution's observation exception. Blocking system administrators who are active members. Rejected because the archive contract already excepts that role and this phase must not invent a tighter product rule.

## Decision 6 — One shared gate for both file families

**Decision**: Put the refusal, attribution requirement, replacement soft-delete, and baseline decision in one schedule service used by both executors. Keep parsing, preview, and field mapping where they are.

**Rationale**: MSP XML, MPP, and P6 currently duplicate the hard delete and the oldest-user fallback. A fix in only one family would leave the other file type unsafe.

**Alternatives considered**: Copying the guard into both modules. Rejected because the two copies already diverged once.

## Decision 7 — Overlapping codes stay skipped, and the counts must match what was stored

**Decision**: Append continues to skip an existing work-breakdown or activity code and to ignore a relationship that is already stored. The reported relationship count is the number inserted, not the number attempted. Skipped codes remain in the warning list. The wizard shows a no-change outcome when all created counts are zero.

**Rationale**: Duplicate activities are already skipped. Relationship creation uses `ignore_conflicts` but increments the count before insert, so a repeat can report new relationships that were not stored and can still publish a baseline. The specification requires an explicit duplicate result and no false success.

**Alternatives considered**: Rewriting preview or the warning catalog. Rejected. Those belong to later stages. This phase only stops false creation and false success.
