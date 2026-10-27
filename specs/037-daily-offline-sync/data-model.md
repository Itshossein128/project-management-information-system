# Data model: offline operations and recovery

## Existing authoritative entities

- `DisciplineSubReport`: project, canonical unit, report_date, status, `lineage_id`, `version_number`, `is_current`, `supersedes`; unique current per project/date/unit and lineage/version constraints already exist. Child types and validation in `sub_reports` remain authoritative. New local draft is not a second server report.
- `DailyReport`: automatic summary; derived rows/provenance belong to aggregation. Existing metadata/override fields follow workflow and allowlist in [research](research.md). Existing attachment references and version history remain intact.

## Server additions (logical model; migration must expand safely)

### Operation receipt

Fields: actor identity, project identity, `operation_id` UUID, canonical immutable request fingerprint (contract version, actor, project, target, kind, base revision, payload and dependencies), terminal outcome, target identity, client/server row mapping, stable error/details where applicable, commit time. Unique `(project, actor, operation_id)`; enforce same fingerprint on replay. Never expose a receipt without current project membership and permission. Receipt and business change commit in the same transaction; no successful receipt for rolled-back mutation. Retention MUST cover all supported offline/retry and upgrade windows; do not purge while a supported client could replay. If a bounded policy is later introduced, reject expired identities rather than replaying them as new; no silent reuse. Retryable failures do not become irrevocable terminal receipts.

### Concurrency token

Each mutable row and editable header has a monotonically changing revision or equivalent opaque token. All online, batch, legacy, correction and delete writers update the token atomically; deletes leave a detectable tombstone/version. Base token is required for existing target changes; new row uses client ID and dependency on report creation. A mismatch yields conflict without business mutation. A report version/current/status token is also checked under parent lock. Scope and target membership must be verified server-side, including foreign references. Individual row token prevents a new unrelated row from causing conflict; aggregate invariants across rows still validate under parent lock.

### Correction transfer intent

A stable user-selected transfer identity references source conflict, approved version and explicit destination. Formal correction creation/reuse is authorized online and retains lineage/reason. A repeated intent returns the same authorized destination, or a clear conflict if the open correction is incompatible; no new correction or duplicate transfer. Individual operations still use receipt/idempotency; intent creation alone is not transfer success.

## Local entities

- **Local report snapshot**: actor, project, canonical unit or project-metadata scope, date, local_report_id, server report/version when known, base header and rows, local overlay including tombstones, cached effective config and reference identity, per-field/row status and error. Full values plus base and local versions remain recoverable; no cross-user display.
- **Operation**: `operation_id`, `client_id` where row target, local_report_id, actor/project/unit, operation kind, target server ID if known, base target revision, immutable payload, predecessor IDs and supersedes-operation ID, created timestamp, state, stable error. Same logical row retains client ID; different operations do not share operation IDs. Schema upgrade preserves raw legacy record and conversion provenance.
- **Claim**: actor/project scope, owner tab, expiry, fencing generation. Claim/update in local transaction; stale workers cannot acknowledge after another owner takes over. Server idempotency remains safety boundary if clocks/leases overlap.
- **Conflict**: source operation identities, scope, base/local/server full relevant snapshots, reason code, resolution intent and destination; retained until confirmed server reconciliation or committed destination receipts. Server choice only discards selected domain and associated operations, not other reports/sections.
- **Legacy quarantine**: raw prior record, cache/context evidence, owner if provable, reason and decision state; no automatic replay where identity, scope, target or operation is ambiguous. Unknown actor data is not shown to a different account; account recovery requires authenticated proof.

## State transitions and invariants

`pending → syncing → synced` only with valid matching receipt; `syncing → pending` after interrupted/expired claim; network/authorization failure retains retryable data; validation transitions to `failed`, conflict to `conflict`. Edit invalid payload creates new pending operation linked to failed predecessor, retaining history. Dependents remain blocked until predecessor confirmed; failed prerequisite never implies success. `synced` history is retained separately from active queue; a tombstone cannot resurrect after later hydration. Local transaction commits overlay and enqueue together before user success. A failed transaction leaves user input recoverable.

For existing targets, `base_revision` reflects the last server-confirmed version plus dependencies: successive operations on one target use the revision returned by predecessor, not an invented revision. Do not send a dependent operation before predecessor receipt; if response is lost, replay predecessor first. Independent operations can succeed individually. Same operation can never be reassigned to another actor/project/target or changed payload.

## Migration and rollback

Server: additive receipt/revision migration, backfill existing targets without changing business values, deploy revision-aware all-writer paths before accepting v2 updates, validate uniqueness/relations with production-like legacy fixtures; constraints after cleanup. Verify apply and rollback on copies; preserve receipt journal across application rollback, with backward-compatible schema until replay risk has elapsed. Restore/controlled replay rather than deleting receipts.

Browser: preserve IndexedDB name, upgrade in a transaction with failure abort; add new stores/version without deleting originals. Legacy records may lack actor or unit: do not infer these. Keep raw records and local decisions with provenance; enable conversion only when context unambiguously proves owner/project/unit/date/target. Test partial upgrade, storage-full abort, old data/readability and restart. IndexedDB version rollback cannot be assumed: provide export/backup plus compatible reader/recovery, validate on same profile before rollout; do not run old code against new schema unless demonstrated safe. Keep old records until explicit reconciliation and compatible retention policy.
