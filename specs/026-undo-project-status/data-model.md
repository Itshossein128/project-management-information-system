# Data Model: Undo Project Status

**Spec**: [spec.md](spec.md) · **Decisions**: [research.md](research.md)
**Status**: Proposed; no schema or migration has been written/applied.

## Project — exact source references

Extend the existing root with three server-only fields:

- `suspension_event`: nullable FK to AuditLog, `PROTECT`, no reverse accessor needed. Its UUID (`suspension_event_id`) identifies the current/most recent actual suspend occurrence, whose semantic event is `project.suspended`.
- `completion_event`: nullable FK to AuditLog, `PROTECT`; UUID exposed read-only as `completion_event_id`. Identifies the current/most recent actual complete occurrence, semantic event `project.completed`.
- `completed_from_status`: nullable status, restricted to `active` or `suspended`, captured from the freshly locked row before a successful complete.

Retain existing `lifecycle_version`, `archive_cycle_id` and `archived_from_status` without repurposing them. Only actual suspend rotates the suspension reference; only actual complete rotates completion reference/origin. Failed actions rotate nothing. Undo, archive and archive restore leave these fields intact. Returning from completion to suspended retains the original suspension reference; resuming that suspension remains separate.

### Database invariants

1. completion reference and completion origin are both absent or both present; present origin is explicitly non-null and active/suspended. Express null branches explicitly so SQL NULL cannot make an invalid check pass.
2. Effective completed state requires a completion reference/origin: current `status=completed`, or current `status=archived` and `archived_from_status=completed`.
3. Suspension reference is required for current suspended, archived-with-origin-suspended, and effective-completed-with-completion-origin-suspended.
4. Outside those effective states, retained historical references are allowed. Do not require a suspension reference just because `archived_from_status` retains suspended while current status is active/draft/etc.
5. All references have real audit FK integrity. Same-project, expected semantic type, allowed original transition, source version and completion-to-suspension association are application validations under the root lock, not cross-table SQL CHECKs.
6. Existing create/template/import paths remain draft and do not copy event references, origin or receipts. Reject submitted metadata through create/update guards, including FK field and `_id` aliases; no normal status PATCH bypass.

`lifecycle_version` advances once per successful status transition through existing `save_project`, and on existing supported name/manager/scope/amount writes. Membership or FK deletion is also checked through fresh authority/readiness/snapshot even if it does not advance this version.

## AuditLog — typed original event, not a new ledger

Reuse AuditLog UUID/time/project/actor/resource fields; no generic audit-schema migration. On suspend or complete persist synchronously in the same transaction as Project status/reference:

- `changes.schema_version=1`;
- `changes.event=project.suspended|project.completed`;
- actual `from_status`/`to_status`;
- `version_before`/`version_after`;
- minimal actor `{id, display_name}` and project `{id, project_code, project_name}` snapshots;
- for complete-from-suspended, the associated `suspension_event_id`; otherwise null.

The row's actual primary key is its event identity; do not search arbitrary audit rows or derive origin from a translated message. `persist_audit_log` returns the created UUID; assign that row to the Project reference before transaction completion. The helper need not be changed to accept a caller-chosen UUID. Timestamp is the audit's own timezone-aware `created_at`.

These semantic payloads are immutable through application services and have no public mutation endpoint. PROTECT prevents deletion while the current Project or a receipt/CR references the source audit. Later account/project deletion may null audit FK references under existing policy; immutable snapshot attribution survives. A narrow success marker suppresses the otherwise duplicate generic middleware row only after committed suspend/complete/undo or exact undo replay. General audit behavior and the existing archive marker remain unchanged.

## ProjectStatusUndo — durable immutable committed result

A new narrow model for these two reverse operations only:

- `id`: UUID primary key, stable public receipt ID.
- `project`: Project FK, CASCADE, indexed, related name `status_undos`.
- `operation`: `resume` or `undo_completion`.
- `source_audit_log`: required AuditLog FK, PROTECT; its ID is public `source_event_id`.
- `source_snapshot`: immutable safe original-event projection: ID, kind, original from/to, original occurrence time, original actor and original project name. Internal extra audit fields are not copied into the public projection.
- `request_id`: client UUID scoped to project, across both new operations.
- `request_fingerprint`: canonical SHA-256 of decoded actor/project/operation/event/from/to/version/snapshot context plus trimmed reason; not raw token bytes/signing timestamp.
- `confirmation_version`: Project version shown at preview.
- `actor`: nullable user FK with SET_NULL; `actor_snapshot`: durable minimal ID/display name.
- `project_snapshot`: durable ID/code/name at undo time, distinct from the original event's project snapshot.
- `reason`: trimmed, nonempty text; no new ten-character minimum (that minimum belongs to CR reasons).
- `from_status`, `to_status`: actual reverse transition.
- `performed_at`: paired undo success audit's timezone-aware creation timestamp.
- `audit_log`: required distinct one-to-one AuditLog FK, PROTECT, semantic success event `project.resumed` or `project.completion_undone`.

Constraints/indexes:

- Unique `(project, request_id)`.
- Unique `(project, operation, source_audit_log)` — one reverse success per original event, even for competing users/request IDs.
- One-to-one success audit; source and success audit cannot be the same row.
- Check operation/from/to tuples: `resume, suspended, active`; `undo_completion, completed, active|suspended`.
- Check reason trimmed and nonempty, following existing archive receipt semantics.
- History index/order `project, -performed_at, -id`; default page 50/max 100; no unbounded aggregate/history traversal.

No public create/update/delete for receipts or original semantic audits. Exact replay never rewrites snapshots/reason/time or inserts another audit. Database referential changes to actor FK do not rewrite immutable attribution. Project hard-delete keeps existing semantics: receipts/CRs cascade; their audit rows remain with project FK SET_NULL and snapshots; deletion is not project recovery. Test this collector path with the new protected references.

## ProjectChangeRequest — narrowly bind completed remediation

Add nullable, server-only `restore_completion_event`: protected FK to the exact completion AuditLog. Preserve existing nullable `restore_archive_cycle_id` unchanged. DB check: at most one binding is present. Normal active/suspended CRs remain unbound with their existing rules.

A new completion-bound CR may be created only when:

- actor is currently a global admin;
- project is currently completed, with active completion origin and matching valid completion event;
- no other open CR exists under current uniqueness policy;
- proposed changes are a nonempty subset of currently missing `scope_description` and `contract_amount`;
- supplied replacement values satisfy existing activation predicates and existing field validation (finite amount, including valid zero).

Keep CR's existing reason minimum, protected-field approval and SoD; group admin requester cannot self-final-approve, existing superuser exception unchanged. Update/submit/approve check binding, current state, current missing fields and fresh authority again under Project→CR locks. A completion-bound CR cannot be transplanted to an archive cycle, another completion, or active/suspended normal editing. While archived it is invalid for update/submit/approve even for an admin; archive round-trip back to the *same* completion may permit fresh current-context actions if all predicates still hold. An old signed undo preview is still invalid because version changed.

Stale bound draft/submitted CRs retain cancel for current global admins; submitted rejection keeps existing eligible authority. No stale approved-data application. Earlier legitimate unbound CRs retain their existing update/submit/approval/cancel policy and are never silently bound; an unbound open CR can block a new repair and must be shown with its actual permitted review/cancel actions. Do not add completed to general new-CR statuses. Manager remains existing authorized normal PATCH; undo does not confer new field permissions.

## Ephemeral confirmation and client state

Preview is not a database entity. Dedicated signed context contains exact keys: `project_id`, `actor_id`, `operation`, `source_event_id`, `from_status`, `to_status`, `lifecycle_version`, `snapshot_hash`. Salt: `projects.status-undo.v1`. Signature validates structure/actor/project/operation; no elapsed-time expiry is imposed.

Snapshot covers current project name/status, current source event/reference identities and completion origin, associated suspension event, archive metadata, manager ID, trimmed scope and normalized amount. A new write requires exact fresh equality; receipt replay compares its original decoded context/fingerprint before current status checks.

Client draft: actor/project/operation + unsent reason only. Client pending attempt: actor/project/operation/source-event ID + frozen `{request_id, confirmation_token, reason}`; no inferred destination. Namespaces are distinct from each other and from archive state. Nothing is persisted until deliberate remediation navigation (draft) or POST dispatch (pending). Explicit abandonment clears unsent text; logout clears both kinds; originating late callbacks must not clear a newer matching-key request with a different request ID.

## Transition and transaction rules

Forward capture: fresh Project lock → existing source-state/authority checks → synchronous original semantic audit → set new reference/origin and status → targeted save/version → return only after atomic completion. Any audit/save failure rolls back everything; failed suspend/complete creates no occurrence.

Undo: fresh operation authority → Project lock → fresh operation authority again → validate body/signature/scope → exact request lookup → already-consumed source lookup → current state/source/snapshot/associated-event validation → current activation gate if active target → targeted status/version save → synchronous success audit + immutable receipt → commit. Require the currently referenced source audit to be the same project's typed event; complete-from-suspended also requires the retained suspension ID to match the original completion's recorded association and remain eligible for its eventual separate resume.

Current operation authority is checked even on historical replay. A valid exact replay is read-only even if the current project is now archived or in a later cycle; it cannot bypass the current-state checks for a *new* write. Another request for an already handled event conflicts; a different fingerprint under the same request ID conflicts. Do not call approval, finance, baseline, generic resume-without-context or archive restore during the reverse transition.

All existing competing writers remain root-lock participants: every lifecycle action including archive/restore, Project PATCH/delete and CR mutation. Use Project→CR order; source audits/receipts are immutable and need no broad joined relation lock. Signature/no-store reads do not hold database locks across HTTP or external storage.

## Migration and reversal

Current projects leaf is `0016_bind_archive_remediation`; expected next migration is 0017, but recheck at implementation. Existing audit leaf is `0003_initial`; a new projects migration can depend on it without modifying earlier audit/project migrations. Add three Project fields, ProjectStatusUndo, completion-CR FK and constraints/indexes in an additive migration or dependency-ordered new migrations if generation requires it.

No legacy origin inference or automatic data deletion. Strict constraints can reject old suspended/completed/archived-effective rows lacking new event provenance; explicitly prepare a dedicated fresh development database rather than silently selecting active. Planning performs no reset. Adapt new fixtures to actual suspend/complete and known event captures; caller-written metadata is never an application input.

MigrationExecutor validation: forward from 0016 with valid unaffected active/draft/archived-active business rows and existing archive receipts; apply constraints, exercise all new event/undo/CR data, reverse only the new migrations to 0016, and compare earlier business rows/archive receipts/audit snapshots. Reverse drops new receipts/fields/constraints/binding but neither changes project business status nor deletes original AuditLog history. Old code/fixtures restored at that boundary do not promise new reasoned-undo behavior. Keep data-preservation and schema-reversal claims separate.
