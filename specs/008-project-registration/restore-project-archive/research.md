# Research: Restore Project from Archive

**Date**: 2026-10-16
**Spec**: [spec.md](spec.md)
**Status**: Complete — all design questions resolved; implementation has not started.

## Evidence boundary

Research used the current working tree, including pre-existing uncommitted activation-feedback changes, and two read-only research agents for concurrency/audit and UI/contracts. Findings were verified against source; no runtime, database, browser or migration behavior was tested in this phase. Historical parent research is not evidence of current implementation.

## D1 — Keep the existing lifecycle and global administrator authority

**Decision**: Extend the existing `projects/lifecycle_service.py`, ViewSet and explicit URL patterns. Restore authority uses `_is_global_admin` from `permissions/project.py`: authenticated superuser or global `admin` group, independently of project membership/edit/approve permissions. Enforce in view and service, with a fresh authority check before mutation. Detail returns server-derived restoration/support capability booleans using request context; UI does not infer them from project permissions or roles. Include manager remediation, scoped CR creation and restoration-history access. CR serialization supplies contextual `restore_remediation_actions` for existing records, including the current SoD decision. Nonmember admins must not depend on a successful membership-permissions lookup for these surfaces.

**Rationale**: Current frontend profile exposes group roles but no superuser flag; a group-less superuser must still see the action. Current project queryset already grants global administrators project access without membership.

**Alternatives considered**: `edit_project` or `approve_project` grants too much; `hasRole(ADMIN)` misses some superusers; a new global permission system is unnecessary.

**Evidence**: `apps/api/core/permissions/project.py`, `projects/views.py`, `authentication/serializers.py`; `apps/web/src/app/lib/auth-types.ts`, `contexts/auth-context.tsx`, `components/projects/ProjectLifecycleBar.tsx`. Paths in this research section are repository-relative.

## D2 — Separate archive occurrence, confirmation freshness and successful retry identity

**Decision**: Add `archived_from_status`, fresh `archive_cycle_id` and monotonic `lifecycle_version` to Project. Each successful archive records its locked current origin and generates a new cycle UUID. Increment the version on supported changes to status, project name, manager, scope or amount. A signed preview token binds actor, project, cycle, target, version and a canonical hash of these displayed/readiness values. The token has no time-based expiry; it becomes unusable for a new write when this context changes. A client-generated `request_id` identifies one confirmed submission and is preserved through refresh-token retry, transport retry and result lookup.

**Rationale**: A status or timestamp alone cannot distinguish successive archives or a value changed and later changed back. The project-level cycle is small; the version makes stale confirmation deterministic. Preview performs no mutation.

**Alternatives considered**: Client-selected destination is forbidden; `updated_at` alone depends on every writer and clock granularity; a generic workflow engine or persisted preview table adds unnecessary machinery.

## D3 — Durable immutable receipt for every successful archive cycle

**Decision**: Add `ProjectArchiveRestore` as a narrow success receipt, unique by `(project, archive_cycle_id)` and `(project, request_id)`. Store normalized reason, actor identity snapshot, target, completion time, request fingerprint and one-to-one AuditLog reference. Preserve receipts across later transitions and archives. Store no success receipt for failed attempts.

**Rationale**: Project “last restored” fields alone lose retry evidence when another archive occurs. A receipt allows a retry to report its original result and the current project state separately without repeating an old transition.

**Alternatives considered**: Redis deduplication loses durable business evidence; request payload logs cannot prove the committed transition; one receipt per HTTP response duplicates success.

## D4 — Serialize all participating Project writers, not only restore

**Decision**: Inside `transaction.atomic`, fetch the authoritative bare Project row with `select_for_update()` before state checks and writes. Integrate this convention into archive/restore, all existing lifecycle transitions, Project PATCH, Project delete and change-request operations that write Project. For operations touching a CR use Project → CR lock order and revalidate both rows. Save only intended business fields plus revision/timestamp. Never persist a full stale `cr.project` or serializer instance. Public services accept identity or re-fetch by identity, so direct callers receive the same guarantees.

**Rationale**: Existing lifecycle methods use `atomic` without locks. PATCH validation uses a preloaded instance; CR approval does `project.save()` on `cr.project`. These writers can overwrite a newly restored status or gate information even if restore itself locks. Preserve their existing business authorization and allowed transitions; the change is ordering and freshness.

**Alternatives considered**: Lock only restore fails against stale writers. A lock on the annotated list queryset can combine aggregation and nullable joins; use a separate Project query instead. Network work while holding the lock increases contention and is unnecessary.

**Primary references**: [Django 4.2 select_for_update](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#select-for-update) and [transactions](https://docs.djangoproject.com/en/4.2/topics/db/transactions/). Lock tests need real separate transactions; ordinary TestCase wrapping can hide missing transaction boundaries. Keep exceptions outside the atomic block when translating database failures.

## D5 — Make semantic audit synchronous and inseparable from success

**Decision**: Reuse `build_audit_payload` and direct `persist_audit_log` inside the same database transaction as status change and receipt insertion. Use event `project.restored_from_archive` in audit changes, recording project/actor snapshots, cycle, request, reason, from/to and occurrence time. Propagate audit failures to roll back everything. Mark successful restore and replay requests as explicitly audited on the underlying Django request; `AuditLogMiddleware` skips its generic success entry only for these marked requests. No global async audit setting change.

**Rationale**: Existing middleware runs after the response, swallows failure and may publish asynchronously. It logs repeated successful HTTP responses, which would falsely look like repeated business success. An after-commit callback cannot undo a committed transition if its audit insert fails.

**Alternatives considered**: Existing `record_audit_log` is unsuitable for mandatory synchronous evidence; after-commit publishing is suitable for optional notifications, not this required success record. Do not introduce new financial or approval events during restore.

**Primary reference**: [Django on_commit timing](https://docs.djangoproject.com/en/4.2/topics/db/transactions/#performing-actions-after-commit).

## D6 — Make missing-information guidance executable through existing controls

**Decision**: Reuse `activation_missing` only for target `active`, preserving its exact current manager/scope/non-null amount predicates and preserving budget approval metadata. Add the missing manager selector to project settings using existing user lookup and existing authorized PATCH. For missing protected scope/amount, make the existing project change-request path available narrowly to global administrators while Project is archived, its known origin is active, and proposed keys only repair currently missing scope/amount. Preserve existing reason length, open-request rule, submit/approve/reject/cancel, permissions and segregation of duties. A group-admin cannot approve their own material CR; the existing superuser exception remains unchanged. Restore itself performs no CR or approval.

**Rationale**: Current settings locks protected fields, protected PATCH rejects administrators too, and CR creation currently allows only active/suspended. Linking to settings alone is a dead end. Current settings/CR controls also depend on membership-derived `usePermission`, whose endpoint requires membership even for a global admin. Server-derived support capabilities and per-record remediation actions therefore explicitly enable only these remediation controls; do not fabricate membership or broadly alter the global permission hook. This is a scoped availability extension of the existing approved-field flow needed by FR-RPA-006; it changes no lifecycle transition and bypasses no protected-field approval. Existing general CR behavior outside this narrowly defined case remains unchanged. An existing open CR is reviewed/completed through its current workflow instead of creating a second one.

**Alternatives considered**: Direct protected admin PATCH would bypass approved-field rules; restore to suspended would choose the wrong destination; asking users to alter the database would not satisfy an actionable completion flow. Broadly allowing all archived field changes or all archived CR creators is unnecessary.

**Evidence**: `projects/serializers.py` protected validation, `projects/change_request_service.py` current CR status restriction and approval, `permissions/sod.py`; `project-settings.tsx` protected controls, `project-create-wizard.tsx` existing `lookupUsers` flow.

## D7 — Narrow history and safe result recovery

**Decision**: Add admin-only preview, restore and request-result interfaces, plus read-only paginated restoration history using existing `view_project`/global-admin authority and authorized project scope. Display a small restoration history section in project overview; do not build a generic audit browser. Keep current status distinct from historical target in every restore/replay result. A result lookup with no committed receipt is `not_recorded`, not proof that an in-flight request failed; retrying the exact confirmed POST safely serializes with it.

**Rationale**: No general audit read endpoint or overview history surface exists in the inspected code. Current project status alone cannot identify who performed the restore or whether this request committed.

**Alternatives considered**: Guessing success because the project is no longer archived is unsafe. Exposing arbitrary audit log content would broaden data access. See [API contract](contracts/restore-api.md) and [UI contract](contracts/restore-ui.md).

## D8 — No old-data restoration compatibility

**Decision**: Schema migration is additive and reversible at the schema level; no destination inference/backfill or legacy-specific runtime path. Require a known origin/cycle for archived data under the new schema. If disposable development data violates the new invariant, document explicit database recreation or fixture replacement as a separately executed development preparation step. Do not run a reset during planning and do not embed silent deletion in the migration.

**Rationale**: The user explicitly waived preservation/compatibility for old development data. This waiver does not permit deleting valid business data during a restore.

**Alternatives considered**: Default active, mapping unknown origin, manual destination selection and legacy migration heuristics violate the bounded scope. Existing historic migration files remain untouched.

## D9 — Evidence must cover UI, actual transactions and preservation separately

**Decision**: Plan red → green pytest coverage, true PostgreSQL concurrency tests, frontend typecheck, isolated intercepted browser tests in both locales, and real API/browser integration. Verify schema forward/rollback in disposable databases and compare pre/post domain data. Do not treat existing intercepted activation UI checks as backend or financial proof.

**Rationale**: Current root Playwright config has no `webServer`; the dirty activation config starts only frontend with intercepted API. Earlier AGENTS startup claims are stale relative to these files. Verification commands must start the actual services and explicitly name mocked versus real boundaries.

**Remaining unknowns**: None. Endpoint names, failure codes, state/receipt constraints, narrow remediation access and validation evidence are fixed in Phase 1 contracts. No package upgrade or new external service is required.
