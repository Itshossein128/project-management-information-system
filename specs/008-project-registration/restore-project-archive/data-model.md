# Data Model: Restore Project from Archive

**Spec**: [spec.md](spec.md) · **Decisions**: [research.md](research.md)
**Status**: Proposed design; no models or migrations written.

## Project — extend the existing root

Keep identity and all business fields unchanged. Add:

- `archived_from_status`: nullable status value restricted to `active`, `suspended`, `completed`. Captured from the freshly locked row before each new archive. Retained after restoration until the next archive.
- `archive_cycle_id`: nullable UUID, generated anew for each successful archive. Retained after restoration so result context remains identifiable; previous successful cycles remain in receipts.
- `lifecycle_version`: non-negative big integer, default 0. Increment under the Project lock whenever supported writes change status, project name, project manager, scope description or contract amount. Also compare a canonical snapshot hash at confirmation; do not use timestamps as the sole revision.

Constraints:

1. Origin and cycle are either both absent or both present; a present origin is one of the three allowed destinations.
2. `status=archived` requires both a valid origin and cycle. Non-archived rows may retain their most recent cycle metadata.
3. New create ignores/rejects caller-supplied lifecycle metadata and starts with the current draft defaults. PATCH/import/template entry points cannot set cycle, origin, revision or restored status directly.
4. Only archive replaces origin/cycle. Restore changes current status and revision/timestamp; it does not rewrite budget approval fields or the captured destination.
5. Version increments reflect committed changes only; failed operations roll back metadata together with business fields.

No new index on a low-selectivity boolean is needed. Existing status index remains. Receipt lookup uses compound uniqueness below.

## ProjectArchiveRestore — immutable success receipt

A narrow project-domain model; no generic operation framework or separate preview entity.

- `id`: UUID primary key; the stable public receipt identity.
- `project`: foreign key to Project, indexed. Use existing hard-delete semantics (`CASCADE` for dependent receipt); this feature does not introduce project recovery or change delete authorization. Audit project snapshot survives separately under existing AuditLog SET_NULL behavior.
- `archive_cycle_id`: UUID captured from Project at successful restore.
- `request_id`: UUID supplied for the confirmed attempt, scoped to this project.
- `request_fingerprint`: canonical SHA-256 digest over actor ID, project ID, cycle, target, confirmed version/snapshot hash and trimmed reason. Compare on replay; raw token encoding/timestamp is not the fingerprint.
- `confirmation_version`: Project version shown in preview.
- `actor`: nullable user FK with SET_NULL; identity is also captured below so later account deletion does not erase provenance.
- `actor_snapshot`: minimal durable ID and display-name snapshot, without credentials or contact information.
- `project_snapshot`: project ID, code and name at the event, without copying all project data.
- `reason`: trimmed nonempty text. Restore does not inherit CR's ten-character minimum; normal request size limits still apply.
- `from_status`: fixed `archived`.
- `to_status`: one of the three allowed targets.
- `restored_at`: timezone-aware occurrence time; use the paired audit row's creation timestamp to keep one event time.
- `audit_log`: one-to-one FK to AuditLog, required; PROTECT deletion of that audit while its receipt exists.

Constraints:

- Unique `(project, archive_cycle_id)`: at most one business success per archive occurrence.
- Unique `(project, request_id)`: one immutable result per confirmed attempt.
- Unique audit reference; check from/to and trimmed reason nonempty.
- Receipts have no public create/update/delete endpoint and are never overwritten on replay. Order history by `-restored_at, -id`.

## AuditLog — reuse existing storage

No new generic audit schema. Persist exactly one semantic event synchronously inside the restore transaction, using existing actor/project/resource/time fields and `changes` with:

- `event=project.restored_from_archive`, `receipt_id`, `archive_cycle_id`, `request_id`;
- actor/project identity snapshots, normalized reason;
- `from_status=archived`, actual `to_status`.

The audit row's `created_at` is the event occurrence time and supplies receipt `restored_at`. Preserve all earlier audit rows. A narrow request marker skips the generic response-success middleware entry for initial restore success and exact replay; no second semantic or generic success is inserted for the replay.

## Read-only presentation capabilities

No capability is stored as a Project field. With request context, detail computes `can_restore_from_archive`, `can_edit_manager_for_restore`, `can_create_restore_remediation` and `can_view_restore_history` from fresh server authority/context. The remediation flags are limited to global admin, archived origin active and the relevant missing field/open-CR state. History follows existing view authority. CR serialization adds `restore_remediation_actions` for that record/context, checking status, global-admin authority and existing SoD. These values drive otherwise membership-gated controls for nonmember admins; they confer no server bypass or invented membership.

## Confirmation context — signed, not persisted

Preview returns an opaque signed token containing actor/project/cycle/target, current version and snapshot hash. Snapshot covers project name, status, cycle/origin and activation inputs (manager ID, trimmed scope, normalized amount). Both signature and project/actor scope are checked server-side. The client cannot select destination or inject completion metadata.

Token validity is context-based, with no elapsed-time cutoff. A completed exact retry may return its stored receipt even after later project changes; a new write always requires the current version and snapshot. A changed-and-restored value still changes the version. Role authority is freshly checked regardless of token/receipt age.

## Transitions and transaction order

Existing draft/approval/suspend/resume/complete rules remain. New edges only:

- `active → archive → archived(origin=active, cycle=A) → restore → active`, subject to current activation gates;
- corresponding suspended/completed archive/restore pairs, with no activation gate on their restore;
- a later archive creates cycle B and records its immediately previous state.

For restore:

1. Validate body shape, reason, token signature and actor/project binding; re-fetch bare Project with `select_for_update()` in `atomic` and freshly verify global-admin authority.
2. Look up receipt by project/request ID. A matching fingerprint returns its immutable receipt plus current Project state. A changed fingerprint conflicts; no write.
3. For another request with an already-restored cycle, return `archive_already_restored` with original receipt and current state. Never apply it to another current cycle.
4. Otherwise require current `archived`, matching cycle/origin/version/snapshot. Recheck `activation_missing` only for active.
5. Change only status, increment version and update timestamp. Insert synchronous semantic audit and required receipt in the same transaction. No call to approve/resume, finance or baseline creation.
6. Return only after transaction exit. Any required insert failure rolls back the complete change. If communication/commit acknowledgement is uncertain, use result lookup or exact retry; never infer a definitive rollback from a broken connection.

Project PATCH locks before instance-dependent validation and writes only submitted allowed fields. All lifecycle actions, delete and CR writers follow the same fresh Project lock. CR operations use Project → CR ordering and fresh validation. Readiness changes from user-FK deletion are caught by the fresh activation check and snapshot comparison; there is no promise that a project can never become incomplete after a later independently authorized edit.

## Narrow archived remediation integration

Manager remains an ordinary authorized Project setting. Scope and amount remain protected and cannot be directly patched. Allow existing CR creation for global admin only when archived origin is active and proposed keys are a nonempty subset of currently missing `scope_description`/`contract_amount`, with replacement values satisfying existing activation predicates. On submit/approve recheck this restricted context under the same Project/CR locks; completion from the normal non-archived CR flow keeps its existing rules. Existing open-CR uniqueness, reason minimum and SoD remain. An existing CR with otherwise legitimate protected changes keeps its current policy; the new create exception cannot be used to propose unrelated changes. Metadata does not automatically complete or approve a CR.

## Bound remediation request context

Implementation refinement: ProjectChangeRequest gains `restore_archive_cycle_id`, nullable read-only UUID, set only by server for a request created while repairing this archived active-origin cycle. This distinguishes the new narrowly bound remediation flow from legitimate normal CRs created before archival. Recheck it on update/submit/approve; delayed remediation must not apply to another cycle. Normal CRs retain null and their existing policy. This adds no new lifecycle state or legacy-data behavior.

## Migration and rollback boundary

Add fields, receipt model, constraints and indexes in a new migration; never edit the historical project-registration migration. No old-origin backfill, guessed destination, legacy runtime handler or automatic data deletion. Existing disposable archived rows without origin may make the constraint migration fail: prepare an explicit fresh development database or replace fixtures before applying. Do not silently choose a status to make migration pass.

Verify forward and schema reversal on isolated disposable databases, recording that reverse removes feature metadata/receipts and does not perform a reverse business restore. Snapshot any needed test evidence before rollback. Fresh valid project documents/finance must be preserved across forward migration and every valid restore. No reset or migration is executed during planning.
