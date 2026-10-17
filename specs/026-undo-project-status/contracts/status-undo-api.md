# Contract: Project Status Undo API

**Status**: Proposed, not implemented. **Base**: `/api/v1/projects/{project_id}/`
**Model/transaction**: [data-model.md](../data-model.md) · **UI**: [status-undo-ui.md](status-undo-ui.md)

## Authority and compatibility

- `resume`: freshly active authenticated user with existing project `edit_project` via active membership/role/override, or existing global-admin bypass. Retain current `HasProjectPermission` and recheck the same rule in service with a freshly fetched user; approval alone or project-manager assignment alone is insufficient.
- `undo_completion`: freshly active system administrator (`is_superuser` or global admin group). Independent of membership; no project edit/approve grant substitutes for global authority.
- Resolve every project through existing authorized scope, including global-admin bypass. Do not query or disclose another project's source event, receipt or reason.
- Preview/mutation/owned-attempt lookup use operation authority. History uses existing `view_project`, with the existing global bypass. Inactive/anonymous/unauthorized callers receive existing 401/403 conventions; authenticated denial is 403 `permission_denied`. Recheck authority even when returning a historical exact replay.
- **Intentional resume contract change**: existing `POST resume/` becomes confirmed/reasoned and returns an undo result, not bare Project detail. Update all application/service/test callers in the same delivery. Empty-body/legacy reasonless calls return 400; no parallel permissive resume remains. Existing suspend/complete URLs, source states and edit permission remain; they additionally capture required original semantic events atomically and return Project detail as before.
- Existing archive preview/restore/result/history routes, receipt types, token salt, status rules and capability meanings remain compatible. Do not insert status-undo rows into archive history or expose them as archived-origin receipts.

Use existing structured errors `{error:{code,message,details}}`, gettext/fa backend messages and `Accept-Language: fa|en`. IDs/codes stay language-independent. Every interface here is `Cache-Control: no-store`, including conflict/error responses containing state. GETs make no business write or success audit.

## Project detail additions — server computed

Add read-only:

- `suspension_event_id`, `completion_event_id`, `completed_from_status` (nullable outside applicable contexts, never writable).
- `can_resume_with_confirmation`: current suspended + resume authority, independently of readiness so missing gates remain discoverable.
- `can_undo_completion`: current completed + global-admin authority.
- `can_view_status_undo_history`: existing view_project authority.
- `status_undo_remediation`: null or `{operation, source_event_id, can_edit_manager, can_create_change_request}` for a current undo-to-active context. It exposes current field permissions and missing/open-CR context; it grants nothing.

For suspended, manager/CR permissions are existing normal policies. For completed-origin-active, manager uses existing authorized PATCH and a narrow nonmember-admin UI capability; new CR creation requires admin + missing scope/amount + no open CR. Completed-origin-suspended has no activation repair requirement. Keep all archive capabilities as-is; do not infer any action from frontend roles or from the capability's client copy.

## Read-only previews

- `GET resume-preview/`: operation `resume`, current suspended, source `suspension_event_id`, target active.
- `GET undo-completion-preview/`: operation `undo_completion`, current completed, source `completion_event_id`, target `completed_from_status`.

Return 200 even if active-target readiness is incomplete; `can_confirm=false` and list every missing field. Return 409 `status_undo_context_changed` for an inapplicable current state/event; deleted project is 404. There is no arbitrary target selector or time cutoff.

Example completed-origin-active:

```json
{
  "project_id": "project-uuid",
  "project_name": "Tower A",
  "operation": "undo_completion",
  "source_event_id": "original-audit-uuid",
  "from_status": "completed",
  "to_status": "active",
  "lifecycle_version": 12,
  "confirmation_token": "opaque-signed-status-undo-context",
  "can_confirm": false,
  "missing": ["project_manager", "scope_description", "budget_approved"],
  "remediation": [
    {"field": "project_manager", "action": "project_settings", "can_perform": true},
    {"field": "scope_description", "action": "project_change_request", "can_perform": true},
    {"field": "budget_approved", "action": "project_change_request", "can_perform": true}
  ]
}
```

`budget_approved` is the existing missing-amount identifier, not a new budget-stamp predicate. Target suspended returns `missing=[]`. `can_perform=false` means explain the needed authorized editor/approver and available review path rather than showing a dead control. Fixed action identifiers build local authorized settings links; no arbitrary returned URL is executed. An open CR suppresses new create capability but remains reviewable under its actual per-record actions. The opaque token contains the exact context defined in the data model, including actor/operation/source binding.

## Confirmed mutations

- `POST resume/` — sole suspended→active transition.
- `POST undo-completion/` — completed→original active or suspended.

Both require exactly:

```json
{
  "request_id": "client-uuid",
  "confirmation_token": "opaque-signed-status-undo-context",
  "reason": "The status was selected by mistake."
}
```

Reason is trimmed/nonempty. Reject missing required body fields and any extra supplied operation/target/status/origin/event/actor/approval fields instead of silently treating extras as writable. Route supplies operation, token binds it, server determines target. No elapsed max-age. Refresh/auth retry must send the identical three fields with the same request UUID; editing reason or changing token/context creates a new explicit confirmation and a new attempt only after the old result is resolved or definitively rejected.

Use the data model's Project-first transaction/replay ordering. A fresh success returns 200:

```json
{
  "outcome": "applied",
  "receipt": {
    "id": "undo-receipt-uuid",
    "project_id": "project-uuid",
    "project_name": "Tower A",
    "operation": "undo_completion",
    "source_event_id": "original-audit-uuid",
    "request_id": "client-uuid",
    "actor": {"id": "actor-uuid", "display_name": "Administrator"},
    "performed_at": "2026-10-17T08:00:00Z",
    "reason": "The status was selected by mistake.",
    "from_status": "completed",
    "to_status": "active",
    "source_event": {
      "id": "original-audit-uuid",
      "kind": "complete",
      "from_status": "active",
      "to_status": "completed",
      "occurred_at": "2026-10-17T07:00:00Z",
      "actor": {"id": "original-actor-uuid", "display_name": "Project editor"},
      "project_name": "Tower A"
    }
  },
  "current_project": {
    "project_id": "project-uuid",
    "project_name": "Tower A",
    "status": "active",
    "lifecycle_version": 13,
    "suspension_event_id": null,
    "completion_event_id": "original-audit-uuid",
    "completed_from_status": "active",
    "archive_cycle_id": null
  }
}
```

A resume receipt instead has `operation=resume`, source kind `suspend`, from suspended/to active. Completion undo to suspended has from completed/to suspended and current Project retains its associated original suspension reference.

Exact replay returns `outcome=replayed` with byte-equivalent public original receipt and fresh current_project; status may already be archived or in a later cycle. Replay does not change status, audit, timestamps or receipt and is allowed only under current operation authority. A *new* request for an already consumed source event conflicts; it never applies to the current event just because status matches. Success/replay uses a narrow semantic-audit marker to suppress generic success middleware logging, without changing archive/unrelated auditing.

## Owned attempt lookup

`GET status-undo-attempts/{operation}/{request_id}/`, operation is `resume|undo_completion`.

- Apply current operation authority and project scope first, independently of current state.
- Look up by project/request/operation and original actor snapshot ID. Another actor's attempt is not returned through this recovery route; authorized history is the separate way to see shared provenance.
- 200 `{outcome:"completed",receipt:<safe receipt>,current_project:<fresh state>}` when owned receipt exists.
- Otherwise 200 `{outcome:"not_recorded",receipt:null,current_project:<fresh state>}`. This is inconclusive, not proof of rollback or permission to invent a new request.
- Deleted project: 404; invalid operation/UUID: existing validation/route error conventions. Lost authority: 403, stop automatic retry and clear private client attempt state.

After an initial unknown transport result, retry sends the frozen POST to its original operation route even if current status changed. The service can safely return its earlier owned receipt before current-context rejection. The UI must not switch to another operation based on current status.

## Bounded history

`GET status-undo-history/?page=1&page_size=50` under existing view_project authority.

Return existing pagination envelope `{count,next,previous,results}`; default 50/max 100, ordered `-performed_at,-id`. Results use the same fixed safe receipt projection above, including a safe original-event projection; never serialize arbitrary AuditLog changes, token, fingerprint, email/phone or financial fields. Store snapshots and avoid per-row user/source lookups; validate bounded queries on a >100-row history. No generic audit browsing or merged archive-history endpoint is introduced.

## Completed remediation through existing CR interfaces

Keep existing CR list/create/detail/actions routes. Add server-only `restore_completion_event_id` to the read-only shape and reject writable binding aliases. At most one archive/completion binding may exist. For completed-origin-active create, server assigns the current completion audit; proposed keys must be a nonempty subset of currently missing scope/amount, replacement values valid, existing reason length and open-CR constraints satisfied. All subsequent update/submit/approve decisions recheck current completion context under Project→CR locks; archive binding keeps its existing checks/codes.

Extend existing `restore_remediation_actions` response field for the completed context, preserving all archived-case meanings. For bound CRs derive actions from fresh binding/status/authority/SoD; invalid bound drafts/submitted rows expose only permitted cancel and existing eligible submitted rejection. For earlier unbound CRs, derive their actual existing permissions without silently binding or broadening creation. In ordinary suspended context keep current edit/approve/SoD behavior; do not force its normal CRs into completion-only rules.

Blocked open CRs are visible with real permitted review/cancel guidance; a fresh missing-field CR may be created only after the existing open request is resolved under current policy. Same-author group admin still cannot approve; current superuser exception remains. Existing manager-only PATCH/lookup is reused where actor already has field authority; direct scope/amount PATCH stays prohibited. Filling data does not submit undo and does not restamp prior budget approval.

## Stable errors

- 400 `reason_required`: required reason absent/blank; show field guidance.
- 400 `invalid_status_undo_request`: malformed body/signature/context; load fresh preview.
- 400 `activation_gates_failed`: all missing fields + actionable remediation; no state/receipt success.
- 403 `permission_denied`: no current operation authority, wrong actor/project/operation-bound confirmation; do not expose unavailable source details.
- 404: project unavailable/deleted; never recreate it.
- 409 `status_undo_context_changed`: fresh write no longer matches state/event/version/snapshot; obtain fresh detail/preview and explicit confirmation.
- 409 `status_undo_request_conflict`: same request UUID with different operation/context/reason.
- 409 `status_undo_already_applied`: source event already handled by another request; return current state and source-event identity, explain existing outcome. Do not include another actor's private reason through an operation-only recovery path; users with view_project can inspect safe shared history.
- 503 `status_undo_not_applied`: only after the service atomic boundary has provably rolled back the complete undo; preserve frozen retry identity. Underlying connection/commit acknowledgment uncertainty is not mapped to this code.
- Existing CR codes (`reason_required`, `invalid_proposed_keys`, `invalid_change_request_status`, `change_request_already_open`, `sod_self_approve`) retain their meanings; new completion binding context conflicts use `status_undo_context_changed`, old archive binding keeps `restore_context_changed`.

Required forward suspend/complete audit failure similarly leaves the original state/reference unchanged; use a localized known-rollback lifecycle error, not an undo-success receipt. Generic unclassified server/network errors after POST remain unknown to the client. Preview GET failures never use mutation-unknown/not-applied wording. Definitively rejected or fully rolled-back operations leave no partial transition/receipt/success audit. Ambiguous delivery may follow a committed success; only lookup/exact retry determines that outcome. Neither case may create duplicate success.
