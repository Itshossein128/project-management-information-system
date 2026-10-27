# Contract: versioned targeted synchronization

## Endpoint and compatibility

Design target: `POST /api/v1/projects/{project_id}/daily-reports/sync-operations/v2/` with a versioned operation envelope, under current project access policy. Final route naming must be documented in endpoint inventory when implemented. Existing `POST .../sync-batch/` retains its request and `results/summary` shape/status meaning, including `conflict`; it MUST reject unsafe derived writes, avoid partial effects and honor current lock/authorization. Do not silently reinterpret `local_id` as `operation_id`. Document security refusal of formerly accepted destructive writes; tests verify existing safe consumers and versioned v2. No v2 fallback to legacy snapshot mutation.

Authentication, current project membership/permission (including existing global-admin policy), ownership and target scoping apply at request, receipt read and mutation; stale cached grants do not authorize writes. Each mutation rechecks scope and current editable state in its transaction. Cross-project references are rejected. Workflow decisions are not operation kinds.

## Request envelope

```json
{
  "contract_version": 2,
  "operations": [
    {"operation_id":"UUID", "local_report_id":"UUID", "scope":{"kind":"unit", "unit":"electrical", "report_date":"2026-10-27", "report_id":null}, "action":"create_report", "target":{"kind":"header"}, "base_revision":null, "depends_on":[], "payload":{"form_code":"A"}},
    {"operation_id":"UUID", "local_report_id":"UUID", "scope":{"kind":"unit", "unit":"electrical", "report_date":"2026-10-27", "report_id":null}, "action":"create", "target":{"kind":"activity", "client_id":"UUID", "server_id":null}, "base_revision":null, "depends_on":["UUID-of-create-report"], "payload":{"activity_ref":"UUID"}}
  ]
}
```

UUID examples are placeholders, not literal valid values. Client-generated row `client_id` is UUIDv4; `operation_id` and local report ID are independent stable UUIDs. A create-report operation resolves existing current unit report without overwriting it; if local and server draft data disagree, return conflict for explicit choice. Header validation and creation are one operation: failure leaves no shell. A child create may depend on successful creation/resolve; no dependency is inferred from request order. `scope.kind=project_metadata` addresses existing summary identity only, never creates raw project reports or targets derived sections. `target.kind` enumerates only existing active section types, e.g. activity/labor/material/machinery/concrete/general activity/issue/visit/incident/note, subject to effective config and server validation. Unsupported target returns stable per-operation error, not skip. Binary upload/file conflict are excluded; existing attachments are preserved.

Existing row update/delete supplies client_id when known, server_id, current base_revision and explicit payload for update or explicit delete. Header operations use a distinct target revision. Dependencies form an acyclic graph in the same batch or previously acknowledged receipt; missing, failed, conflicted, unauthorized or cyclic dependencies return `blocked_dependency` without mutation or success. Send sequential changes on same target after predecessor receipt so its returned revision can be used; batch may contain independent operations. Omission or empty list never means replace/delete. Server verifies duplicate operation ID, payload fingerprint, correct identity and target. An unknown or malformed operation is never treated as successful.

## Response semantics

```json
{
  "contract_version": 2,
  "synced_ids": ["operation-uuid"],
  "results": [
    {"operation_id":"operation-uuid", "outcome":"success", "target":{"client_id":"row-uuid", "server_id":"server-row-uuid", "report_id":"report-uuid", "revision":"opaque-token"}},
    {"operation_id":"another-operation-uuid", "outcome":"validation_error", "error":{"code":"stable_code", "field":"quantity", "message":"localized message"}},
    {"operation_id":"third-operation-uuid", "outcome":"conflict", "status":"sync_conflict", "error":{"code":"conflict_report_approved", "message":"localized message"}},
    {"operation_id":"fourth-operation-uuid", "outcome":"retryable_failure", "error":{"code":"temporarily_unavailable", "message":"localized message"}}
  ]
}
```

Results may be reordered. `synced_ids` contains only operation IDs with valid committed success results, not row or local report IDs. Success includes operation and target identifiers and new revision where relevant; create row maps `client_id` to server ID. Client verifies request membership, unique result per operation, target mapping and consistent `synced_ids`; missing, duplicate, unknown, inconsistent or malformed results do not clear affected operations. An authenticated replay of same identity and fingerprint returns the recorded outcome/mapping even after response loss; same ID with changed payload gives `operation_id_reused` and no mutation. A response-level HTTP success does not imply every operation succeeded. Authorization/session failure may reject request as a whole; no unconfirmed operation is cleared.

Each operation has its own atomic transaction and outcome; invalid header/create leaves no shell, child or other business side effect. Independent valid operations in batch can commit, dependent operations cannot commit early. Validation errors carry code, field and target scope; errors retained locally; edited payload uses new operation ID with `supersedes_operation_id`. Conflict response references authoritative version and provides or allows an authorized read of complete relevant server header and sections; deleted/non-current versions are not silently retargeted. `conflict_report_approved` and `sync_conflict` remain stable across locales. Other conflicts (stale target, non-current, locked, competing draft) have distinct stable codes and actionable state.

## Correction and protected data

Selection of server version needs explicit confirmation and local scoped reconciliation. Selection of correction first performs explicit online authorized formal correction using stable transfer intent, with reason and user preview; unit data targets unit correction draft, project-owned metadata follows project correction workflow. Retries reuse intent and operations; no direct mutation of approved version, no implicit workflow decision and no duplicate correction/row. No local deletion until corresponding destination receipt; partial destination success keeps unresolved remainder and makes already acknowledged operations non-replayable.

Derived rows, aggregated totals and provenance cannot be authored, replaced or deleted via any route; `derived_readonly` for authored/empty-array attempts on auto-summary including legacy PATCH/create/batch. Existing permitted metadata retains workflow controls and validation. Ledger/revision and mutation are committed together, and all writers use same concurrency discipline. See [data model](../data-model.md).
