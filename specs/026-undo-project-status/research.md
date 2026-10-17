# Research: Undo Project Suspension and Completion

**Date**: 2026-10-17 · **Spec**: [spec.md](spec.md)
**Status**: Phase 0 complete; decisions below are proposed design, not implemented behavior.

## Evidence and boundaries

Read the current shared checkout on actual Git branch `main`, including uncommitted archive-restoration implementation. The setup script reports logical `BRANCH=026-undo-project-status` from feature configuration; it did not switch Git branches. Python 3.12.3 and Django 4.2.11 were verified by importing the existing API venv. React/React Router/Vite/TypeScript versions come from current manifests. No database, migration, service or test was run for this planning invocation.

Two read-only research agents examined backend state/audit/concurrency and frontend authorization/remediation/history. They made no edits. The main agent checked their source findings and consolidated these decisions. A preservation snapshot covers all 2,936 files present before setup, including spec/checklist and existing dirty/untracked work.

Primary local evidence:

- [Lifecycle service](../../apps/api/core/projects/lifecycle_service.py): `lock_project`, `save_project`, `activation_missing`, suspend/resume/complete/archive, signed archive context and immutable replay.
- [Project models](../../apps/api/core/projects/models.py), [serializers](../../apps/api/core/projects/serializers.py), [views](../../apps/api/core/projects/views.py), [permissions](../../apps/api/core/permissions/project.py).
- [Change-request service](../../apps/api/core/projects/change_request_service.py), [SoD](../../apps/api/core/permissions/sod.py).
- [Audit persistence](../../apps/api/core/audit/service.py), [middleware](../../apps/api/core/audit/middleware.py), [AuditLog](../../apps/api/core/audit/models.py).
- [Lifecycle bar](../../apps/web/src/components/projects/ProjectLifecycleBar.tsx), [archive dialog](../../apps/web/src/components/projects/ProjectArchiveRestoreDialog.tsx), [pending/drafts](../../apps/web/src/app/lib/project-archive-restore-pending.ts), [auth](../../apps/web/src/app/contexts/auth-context.tsx), [CR panel](../../apps/web/src/components/projects/ProjectChangeRequestPanel.tsx).
- [Existing archive design](../008-project-registration/restore-project-archive/plan.md) is historical design; actual source, not its older “proposed” labels, determines current availability. Its verification report is prior evidence, not tests rerun here.

## D1 — Preserve asymmetric authority

**Decision**: Resume keeps `member_has_codename(user, project, 'edit_project')`, including active membership and the existing global-admin bypass. Undo-completion requires a freshly active `_is_global_admin` user (superuser or global admin group), without separate project membership. Preview, mutation and owned attempt lookup apply the corresponding operation authority; history uses existing `view_project`.

**Rationale**: `views.py:79–101` assigns resume to edit_project; `permissions/project.py` includes the global-admin bypass. The spec deliberately preserves this while restricting completion correction. Fresh service checks must re-fetch user and grants; cached UI capabilities are not authority.

**Alternatives considered**: admin-only resume would revoke an existing permission; allowing project editors to undo completion contradicts the accepted specification; frontend group inference misses group-less superusers/nonmember administrators.

## D2 — Keep one resume mutation

**Decision**: Upgrade existing `POST resume/` and `lifecycle_service.resume` to require request ID, signed preview context and trimmed reason. Add preview/result/history support and a distinct undo-completion action. Replace every bare resume caller, including tests; do not retain an empty-body compatibility path. Suspend and complete retain their existing source-state/authorization rules.

**Rationale**: Current resume is an immediate empty-body call returning Project detail; it has neither confirmation nor durable replay. Its intentional request/response contract change must be delivered across server, typed client, UI and fixtures together.

**Alternatives considered**: adding a parallel safe resume would leave the original bypass; treating completion undo as resume would lose its distinct authority and original destination.

## D3 — Typed original events in existing audit storage

**Decision**: Add Project nullable protected audit references `suspension_event`, `completion_event`, plus nullable `completed_from_status`. A successful suspend/complete creates a synchronous semantic AuditLog inside the same Project transaction; the audit UUID is the source-event identity. Capture actual from/to, actor/project snapshots, version before/after and, for completion from suspension, that suspension event ID. Persist the reference and status together. No new general event table is needed.

**Rationale**: AuditLog already has UUID identity, occurrence time and JSON snapshots. Forward middleware runs after the response, may enqueue asynchronously and swallows failures; it cannot alone guarantee an origin record. A direct protected FK identifies an exact typed source row rather than searching for the latest arbitrary audit. Required audit failure must also roll back the forward transition, with no new event reference.

**Alternatives considered**: bare origin fields plus unlinked middleware logs lose durable provenance; inferring origin from archive metadata is incorrect; a separate ProjectStatusOccurrence table duplicates an already sufficient immutable semantic audit projection; a generic lifecycle ledger exceeds this two-action feature.

## D4 — Preserve independent event identities through round trips

**Decision**: Only actual suspend replaces `suspension_event`; only actual complete replaces `completion_event`/origin. Completion from suspended retains the exact suspension reference. Undo-completion to suspended restores no new suspension event and does not consume/resume it. Archive and archive restore leave all three fields unchanged. A subsequent real suspend/complete creates a new source-event identity.

**Rationale**: Completed→archived→completed must still undo to the original pre-completion status. Suspended→completed→undo-to-suspended→resume must consume the original suspension exactly once. Retained archive metadata is not the effective current state when the project is no longer archived.

**Alternatives considered**: one “previous status” field is overwritten by archive; rotating suspension on undo-completion fabricates an original event; clearing history on reverse loses retry/provenance.

## D5 — One narrow immutable undo receipt

**Decision**: Add `ProjectStatusUndo` for `resume` and `undo_completion`. It references the protected original audit and a distinct required one-to-one success audit, stores source/performer snapshots, reason and canonical request fingerprint, and is unique by project/request and project/operation/source event. Archive receipts remain separate and unchanged.

**Rationale**: A durable committed result is needed after response loss, later status changes and later cycles; a boolean or transport retry alone cannot prove which operation succeeded. Reuse the proven archive pattern without pretending its archived-only receipt type fits suspended/completed.

**Alternatives considered**: unique status updates without receipts cannot explain historical replay; putting the new operations into ProjectArchiveRestore breaks its constraints and existing consumers; sharing an ephemeral cache for idempotency loses results.

## D6 — Project-first atomic boundary and replay ordering

**Decision**: For a new or repeated undo: fresh authority → bare Project row lock → fresh authority again → validate actor/project/operation-bound signed payload → exact request lookup → source-event success lookup → fresh context/readiness → targeted status/version save + direct success audit + receipt. Exact committed replay precedes current-status checks and returns original receipt separately from fresh current state. New writes never adapt stale context to another event. The source row must match project, kind and fixed original fields; no caller-supplied destination is accepted.

**Rationale**: Existing Project PATCH/delete, lifecycle and CR writers already share the root lock and targeted-save/version convention; extend that convention. Django requires transaction boundaries for [select_for_update](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#select-for-update), and transaction-level tests avoid misleading TestCase wrapping. Keep locks short and perform no external I/O while holding them.

**Alternatives considered**: atomic without a common root lock allows stale checks; checking current status before exact receipt rejects safe historical retries; locking nullable joined relations is unnecessary and fragile.

## D7 — Context freshness without a clock cutoff

**Decision**: Sign project/actor/operation/source-event/from/to/version/snapshot with a dedicated status-undo salt. Snapshot includes current name/status, all relevant event/origin/archive identifiers and activation inputs. No max-age cutoff; successful exact replay compares canonical decoded context + trimmed reason, not token encoding or signing timestamp.

**Rationale**: Existing lifecycle_version detects changed-and-changed-back supported writes; the snapshot also catches current FK/readiness changes. [Django signing](https://docs.djangoproject.com/en/4.2/topics/signing/) supports salted structured values; actor/operation scoping and current authorization remain application responsibilities. Secrets and decoded payloads are not client authority.

**Alternatives considered**: fixed undo windows contradict the spec; timestamps alone miss some changes; token-only replay equality makes harmless signature timestamps significant.

## D8 — Exact activation predicate, no financial re-execution

**Decision**: Reuse `activation_missing` unchanged only when target is active: manager exists, trimmed scope nonblank, amount is not null. Zero remains valid. Never call approve, payment/collection, commitment approval, budget restamping or baseline creation. Undo to suspended skips activation gating and preserves existing suspended restrictions.

**Rationale**: Current resume already uses this predicate. Correction grants normal future active-state operations; it does not replay prior decisions or roll unrelated data back.

**Alternatives considered**: forcing all targets through activation blocks valid suspension; invoking approval creates side effects and falsely renews approval metadata.

## D9 — Narrow completed remediation, preserve normal suspended policy

**Decision**: Keep normal active/suspended CR rules unchanged. Add only a global-admin, completed-origin-active exception for currently missing scope/amount. Add nullable server-only `restore_completion_event` protected audit FK to CR, mutually exclusive with existing `restore_archive_cycle_id`. Create/update/submit/approve recheck event, current completed state/origin, still-missing keys, authority, open-CR uniqueness and existing SoD under Project→CR locks. Invalid/stale bound CRs allow only appropriately authorized cancel (and existing eligible submitted rejection), never stale edits/approval. Earlier unbound CRs keep their existing policy and are never silently rebound.

**Rationale**: `CR_ALLOWED_PROJECT_STATUSES` currently excludes completed; merely linking settings would be a dead end. Settings already renders its CR panel, but that panel restricts only archived requests and can display a form the server rejects. Manager is not protected and keeps existing authorized PATCH; a narrow server capability exposes the existing manager control to nonmember admins.

**Alternatives considered**: adding completed to general CR creation permits unrelated changes; direct scope/amount PATCH bypasses approvals; auto-approving remediation violates SoD; binding only to project lets a delayed CR repair the wrong completion event.

## D10 — Capabilities and UI reuse without changing archive contracts

**Decision**: Add fresh server capabilities for confirmed resume, completion undo, safe history and a typed operation/event remediation context. Mount a focused status-undo controller independently of membership-only early returns. Route the existing resume button through it and remove its immediate mutation. Add a small feature-specific history projection/component showing actual from/to and original event. Reuse dialog/button/manager controls and exact session-safety patterns; share only small presentation helpers when necessary.

**Rationale**: Archive preview/receipt types and history renderer hardcode archived as source. The actual AppShell already keys route content by pathname, but keyed user/project/operation controllers and mounted/auth/request ownership remain explicit defense if shell reuse changes.

**Alternatives considered**: rewriting all archive APIs/history would expand scope; copying the archive source label would lie; relying only on client role arrays or shell unmounts leaves independent capability/session gaps.

## D11 — Scoped drafts, frozen sent body and evidenced refresh

**Decision**: Use separate token-free draft and sent-pending namespaces keyed by actor/project/operation; sent work retains its source event and exact three-field POST body. Retain unsent reason only for remediation navigation; clear on explicit abandonment/send/logout. Extend existing auth cleanup, respecting initial session-validation timing. Prevent late callbacks from clearing a different request or disclosing an old account. Confirmed success/replay/completed lookup invalidates detail/projects/status-undo history and both actual portfolio query keys; unknown/not_recorded/cancel does not.

**Rationale**: The current archive implementation already proves these boundaries. Operation identity prevents a completion-undo request colliding with a later resume or an archive attempt. Fresh preview is required after remediation; filling information alone does not undo.

**Alternatives considered**: one actor/project key mixes actions; overwriting a frozen pending reason changes request identity; optimistic status on unknown transport result lies about success.

## D12 — Atomic semantic auditing and error taxonomy

**Decision**: Persist initial suspend/complete semantic events and undo success audits synchronously, regardless of global async setting. Mark only those committed actions/replays to suppress their duplicate generic middleware audit; archive behavior keeps its current marker. Catch an IntegrityError outside the service atomic boundary only when rollback is known; report a stable known-failure code. Connection/commit-acknowledgment loss remains uncertain and requires lookup/exact retry. Preview failures have separate actionable localized messages.

**Rationale**: [Django transactions](https://docs.djangoproject.com/en/4.2/topics/db/transactions/) requires database exception handling around atomic boundaries. An on-commit callback cannot provide all-or-nothing required audit persistence because it runs after the business transaction. General middleware auditing for unrelated actions is unchanged.

**Alternatives considered**: async required audit can be lost; success middleware duplicates replay; describing every 5xx or broken connection as rollback creates unsafe retries/new operations.

## D13 — Additive migration and explicit development-data boundary

**Decision**: Generate new migrations after current projects leaf `0016_bind_archive_remediation`, depending on the existing audit leaf (`0003_initial`) as needed for FKs. Add strict effective-state constraints, receipt uniqueness/status/reason checks and CR binding exclusion. Preserve historical migrations and all valid project/business/archive receipts. No guessed origin/backfill or automatic delete; implementation prepares a dedicated fresh development database for unknown-origin old fixtures. Reverse only this feature schema after 0016, preserving prior archive schema/receipts and business data; schema reversal is not a business undo.

**Rationale**: The user waived compatibility with unknown-origin development data, not the integrity of correctly formed business data or historical specs. Snapshot-based MigrationExecutor forward/reverse tests are required later. Current-status/effective-archived-state predicates avoid imposing requirements based on irrelevant retained archive origin.

**Alternatives considered**: editing 0015/0016 invalidates previous delivery; fabricating an active origin violates the core requirement; a blanket constraint on retained archived_from_status rejects valid later states.

## D14 — Evidence design and gates

**Decision**: Plan observed RED→minimal implementation→GREEN for missing behavior; retain already-correct behavior as GREEN without manufacturing failure. Use real PostgreSQL independent-connection lock contention, migration/reversal and domain-data snapshots; separate intercepted UI from actual authenticated browser/API proof. Test all 25 acceptance scenarios, 15 FR and 7 SC. Existing runner can safely target a new `velora_restore_undo_026` disposable database; no runner changes required. Keep backend concurrency/migration and API/browser runs sequential to avoid test flush/connection interference.

**Rationale**: Existing archive evidence distinguishes all these categories and records seeded-role loss under transactional flush. New schema means archive fixtures that directly construct effective suspended/completed states must be adapted through valid real lifecycle actions; reasonless resume assertions must adopt the intentional new contract.

**Alternatives considered**: checked tasks or one mocked suite do not prove delivery; SQLite cannot prove PostgreSQL contention; a full database reset or a dependency upgrade is unnecessary.

All technical questions are resolved by these decisions. No product clarification, new role, new activation condition or constitution amendment is needed for planning. Runtime assertions remain future implementation gates.
