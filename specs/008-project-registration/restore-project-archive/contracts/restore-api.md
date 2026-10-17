# Contract: Project Archive Restoration API

**Status**: Proposed; interfaces do not exist yet.
**Base**: `/api/v1/projects/{project_id}/`
**Data**: [data-model.md](../data-model.md)

## Authority and shared conventions

Preview, restore and request-result lookup require authenticated `_is_global_admin`, even for project members/editors/approvers. Apply view and service checks, with fresh mutation-time authority. Resolve project through the existing global-admin-aware scope; a nonmember global admin is allowed. Authorization is checked before returning preview or receipt information. History requires existing `view_project` through authorized project scope, with the current global-admin bypass.

Use existing authentication and `Accept-Language: fa|en`. Keep machine identifiers stable; messages use backend gettext/fa catalog and frontend locale strings. Error shape remains `{ "error": { "code": "...", "message": "localized explanation", "details": {} } }`. Do not parse translated text to identify failure. Omitted authentication follows the existing authentication stack's 401/403 behavior; authenticated non-admin gets 403 `permission_denied`.

Add `can_restore_from_archive: boolean` to Project detail, computed using request context and archived status, never inferred from submitted data. Ensure detail/action serializers receive the request. `archive_cycle_id`, `archived_from_status`, `lifecycle_version` may be read-only for authorized detail; no serializer accepts them for creation/PATCH. Also return read-only `can_edit_manager_for_restore`, `can_create_restore_remediation` and `can_view_restore_history`. The first two are narrowly computed for global admin + archived origin active + the applicable missing field; create is false when an open CR already exists. History capability follows existing view authority. Current membership-permissions lookup can 404 for a nonmember administrator, so these capabilities must independently drive the relevant settings/CR/history controls. Existing CR responses gain `restore_remediation_actions` (subset of `update`, `submit`, `approve`, `reject`, `cancel`) computed with actor, current record status/context and existing SoD; same-author group-admin gets no approve action. Ensure CR serializers also receive request context. Other current API fields remain backward compatible.

## GET restore-preview/

Admin only, no write, no success audit, `Cache-Control: no-store`.

200 example:

```json
{
  "project_id": "uuid",
  "project_name": "Tower A",
  "from_status": "archived",
  "to_status": "active",
  "archive_cycle_id": "uuid",
  "lifecycle_version": 8,
  "confirmation_token": "opaque-signed-context",
  "can_confirm": false,
  "missing": ["project_manager", "scope_description", "budget_approved"],
  "remediation": [
    {"field": "project_manager", "action": "project_settings"},
    {"field": "scope_description", "action": "project_change_request"},
    {"field": "budget_approved", "action": "project_change_request"}
  ]
}
```

`budget_approved` preserves the existing gate identifier and means missing current amount, not a new stamp requirement. Return all currently missing gates only for active target; suspended/completed return `missing=[]`. Remediation uses fixed action identifiers, not arbitrary untrusted URLs. UI builds authorized local routes and explains existing open CR / SoD requirements. No free target selector. A valid preview may be incomplete (`200, can_confirm=false`) so the user can see all gaps. GET on a non-archived project returns 409 `restore_context_changed` with current state.

## POST restore/

Admin only. Body is exactly the confirmation context plus reason and stable submission identity:

```json
{
  "request_id": "uuid",
  "confirmation_token": "opaque-signed-context",
  "reason": "Project was archived by mistake."
}
```

Reject writable target/status/cycle/actor/approval fields rather than silently using them. Trim reason; empty/whitespace fails. Validate signature and actor/project scope, then apply the locked flow in the data model. No token expiry clock is introduced; context invalidation governs new writes. No proxy, client, refresh-token handler or UI retry may replace the request ID or confirmed body during automatic retry.

200 for first success or exact committed replay:

```json
{
  "outcome": "restored",
  "receipt": {
    "id": "uuid",
    "project_id": "uuid",
    "project_name": "Tower A",
    "archive_cycle_id": "uuid",
    "request_id": "uuid",
    "actor": {"id": "uuid", "display_name": "Administrator"},
    "restored_at": "2026-10-16T08:00:00Z",
    "reason": "Project was archived by mistake.",
    "from_status": "archived",
    "to_status": "active"
  },
  "current_project": {
    "project_id": "uuid",
    "project_name": "Tower A",
    "status": "active",
    "archive_cycle_id": "uuid",
    "lifecycle_version": 9
  }
}
```

Exact replay changes only `outcome` to `replayed`; it returns original actor/reason/time/target and a fresh `current_project`. Current status may now be suspended, completed or archived in a newer cycle. Never present receipt `to_status` as current status without comparing the current state. First success and replay suppress middleware's generic success row through the explicitly-audited request marker. Replay creates no audit, receipt, timestamp or version change.

Known domain errors:

- 400 `reason_required`: empty trimmed reason; `details.fields.reason` contains localized guidance.
- 400 `invalid_restore_request`: malformed UUID/body/token, invalid signature or unexpected writable fields. Token bound to another actor is 403 `permission_denied`.
- 400 `activation_gates_failed`: current complete `details.missing` array and remediation actions; archived state remains.
- 409 `restore_context_changed`: non-archived/stale project, cycle, target, revision or snapshot; include authorized `current_project` and require fresh preview/confirmation.
- 409 `archive_already_restored`: a different request already succeeded for this cycle; include original receipt and current state, with no independent success.
- 409 `restore_request_conflict`: the same project/request ID is reused with a different fingerprint; do not overwrite its receipt.
- 404 `not_found`: absent/deleted project. No recreation.
- 503 `restore_not_applied`: only when rollback is positively established, including a forced synchronous audit failure; localized retry instruction. Translate errors outside the atomic block.
- Unstructured 5xx, connection failure or lost commit acknowledgement: outcome is unknown to the client; check result/exact retry. Do not promise rollback without evidence.

State/permission revalidation precedes fresh writes. A matching historical retry can return its receipt before checking current archived state/version, but never bypasses fresh global authority or actor/project/token binding. Another admin competing with another request receives original result as conflict, not a second successful restore.

## GET restore-attempts/{request_id}/

Admin only; project-scoped, no write, no success audit, `Cache-Control: no-store`.

- 200 `{ "outcome": "completed", "receipt": {...}, "current_project": {...} }` when a durable committed receipt exists for that project/request ID.
- 200 `{ "outcome": "not_recorded", "receipt": null, "current_project": {...} }` otherwise. This is not proof a still-running POST failed. Retry the identical confirmed POST to serialize safely with it; if context changed, show conflict/fresh preview.
- 403 for non-admin; 404 for absent project. A result from another project is never resolved by a global request-ID-only lookup.

## GET restore-history/?page=1&page_size=50

Read-only project restoration events under current `view_project`/global-admin authority. Use `DefaultPageNumberPagination` (default 50, maximum 100): `{ "count": 1, "next": null, "previous": null, "results": [receipt] }`. Return safe immutable receipt fields and actor/project snapshots, not confirmation tokens, hashes or arbitrary audit payloads. Empty history returns an empty page. Order by newest event then ID. This endpoint is a narrow success history, not a list of failed requests or an unrestricted audit browser.

## Existing archive, PATCH and CR integration

- Existing `POST archive/` authorization and allowed origins remain unchanged. Under the shared row lock it captures origin/new cycle and advances revision. Existing response gains read-only context fields; failed/repeated archives do not rotate cycle.
- Existing lifecycle/PATCH/delete/CR writers join Project-first locking and targeted saves; stale objects cannot overwrite restoration state. No new lifecycle transitions or generic status PATCH.
- Existing manager PATCH becomes reachable in settings using existing user lookup. It retains `edit_project` plus current global-admin bypass and FK validation.
- Existing CR create/submit/approve gains only the narrow archived-active-origin missing-scope/amount remediation availability described in [data model](../data-model.md). Existing permissions, ten-character CR reason, one-open rule, approval/SoD and protected PATCH rejection remain. Non-admin archived creation and unrelated archived protected changes remain rejected.
