# Data Model: Import Operations

Design proposal; no migration or product model has been written in this planning command.

## Existing concrete jobs

Extend abstract `BaseImportJob` in `schedule/models.py`; fields are added to both `MspImportJob` and `P6ImportJob`. Preserve UUID, project, nullable actor, task_id, status, progress, filename, replace flag, BinaryField file_data, JSON result and error fields. Do not move originals to a new storage service or delete history rows for retention.

### Proposed additive fields

- `source_sha256`: 64-character digest, computed from accepted source bytes, immutable. Indexed with project/actor/mode/status as needed for existing in-flight matching; digest alone is not cross-project deduplication or access authority.
- `source_size`: nonnegative original byte count, immutable after intake.
- `queued_at`, `dispatch_deadline_at`: timezone-aware intake and deadline; pending publish attempts must not extend the deadline.
- `last_dispatched_at`, `dispatch_count`: publication observations; broker task UUID stays in existing task_id and is persisted before publish.
- `started_at`, `execution_deadline_at`: claim time and absolute bounded deadline.
- `execution_token`: nullable random UUID fence. It is internal, never a user authorization token.
- `completed_at`: immutable terminal completion timestamp for new jobs; set in the same commit as DONE/result or terminal FAILED.
- `retention_anchor_at`, `retention_anchor_source`: immutable expiry anchor, equal to completed_at for new jobs; source is `terminal` or `legacy_backfill`. Allows honest handling of old terminal rows without inventing completion dates.
- `file_purged_at`: nullable timestamp; set atomically when file_data is cleared. Purging does not change source digest/size, completed_at or result.
- `retry_of`: nullable self-reference within the concrete job family; same project, confirming actor authorized now, immutable after intake. A retry is a new job with a new lifecycle; it does not reopen its predecessor. This field is nullable only for fresh imports/legacy rows: request intent=retry requires a visible same-family/project FAILED predecessor and a fresh upload; intent=new forbids retry_of. Request intent is not a new stored job-state field.

An optional `stage` value may be added only if needed internally; public status vocabulary stays pending/running/done/failed. Prefer existing progress_pct milestones rather than a second public state machine.

### Invariants and transitions

1. Intake: after current authorization, cheap bounded upload checks and digest/size, return any scoped matching in-flight job before reserving preparation capacity. Only genuinely new work enters preparation; recheck matching under the project lock before storing a new PENDING job with validated source identity, dispatch UUID and fixed dispatch deadline. Input-validation/capacity rejections have no business job; an existing safety refusal stored as FAILED receives its identifier and terminal/retention timestamps immediately.
2. Claim: lock project then job, re-read status; terminal → return recorded outcome. An unexpired RUNNING claim → no-op duplicate. PENDING with an unexpired dispatch deadline plus available slot → RUNNING with token/deadline; an expired PENDING job cannot be claimed and is failed under the same locks; commit the claim before preparation.
3. Preparation: helper has no database access. Preparation-stage progress may be persisted with token-conditional updates and is capped at 99. No schedule rows are changed.
4. Apply: lock project then job; verify token, running status, remaining deadline and current actor/safety rules. Apply prepared data using P2/P3 services, then store DONE/result/100% and immutable terminal/retention timestamps in the same transaction. Two job families serialize on the same project lock.
5. Failure: roll back all domain work first; reacquire project→job locks and fail only the still-owned RUNNING attempt. A fenced-out delivery cannot overwrite a new owner or terminal outcome. Errors are sanitized.
6. Terminal jobs never transition back to RUNNING. Duplicate deliveries neither change timestamps nor reset expiry.
7. Maintenance: try the same locks with bounded wait/skip-locked behavior. Expired PENDING/RUNNING becomes FAILED only if still nonterminal and safely acquired; an active apply is never failed from an unlocked stale snapshot. Hard execution/DB budgets prevent an apply holding locks indefinitely. Follow the runtime contract's stable oldest-first cohort cutoff, revisit skipped items, drain consecutive batches and record N/budget/elapsed/unfinished metadata without extending deadlines or letting later arrivals starve prior work.
8. Expiry: eligible only when terminal, anchor is present, anchor + 168 hours ≤ now, and bytes remain. Under lock, clear bytes and stamp file_purged_at; retain result and attributable history. Reads/redelivery do not renew retention.

## Processing capacity lease — proposed small model

`ImportProcessingSlot`: fixed seeded slots (initial profile: one), `slot_number` unique, nullable execution token, family/job UUID or preview request UUID, owner-host identifier, deadline, and containment-relative identifier. No source bytes/credentials are stored here. Only launcher/maintenance code can claim/release it.

Preview has no business job, so it uses a short-lived request execution identity. Global slots cover preview, start validation, and worker preparation rather than only one Celery queue. Claims are atomic; do not hold a capacity row lock while acquiring project/job locks. Release with a token condition. Reclaim only after the old containment is confirmed stopped, or mark it quarantined and reject further admission on that slot. A reused PID is never sufficient identity for killing work. Host reboot identifiers and execution-token cgroup names prevent PID-reuse mistakes.

## Derived workspace manifest

A small private manifest contains version, random execution token, owner-host/reboot identity, request/job identity, absolute deadline, fixed artifact names and configured resource profile identity. It contains no credentials or raw source content. Scratch input/output/manifest are held only under the configured dedicated bounded root with restrictive permissions; filenames from uploads are metadata, never path components. No symlink traversal or generic `/tmp` deletion.

Original DB bytes and durable results are separate: deleting temporary input/output cannot delete job.file_data before its agreed expiry. Detailed diagnostics are restricted and bounded; public history/results must not retain copied source text as a substitute for purged bytes.

## Migration and rollout

- Generate the next available schedule migration at implementation time; this plan does not reserve a number. Add nullable fields first and create the capacity table without changing existing business tables' meanings.
- Backfill digest/size in bounded batches while bytes exist. New intake must always populate them; historical rows already missing bytes retain nullable identity rather than a fabricated digest.
- For historical terminal jobs, keep completed_at unknown; set retention_anchor_at to a single recorded migration instant and source `legacy_backfill`. Do not claim updated_at is historical completion. Originals remain for a full seven days from that conservative anchor.
- Historical active jobs remain protected. Deployment must quiesce/drain old import execution before activating new fencing/maintenance; legacy RUNNING rows are then reconciled as interrupted and anchored at their actual recorded terminalization. No concurrent old worker may apply after the new ownership protocol starts.
- Preserve project, actor reference, filename/mode, results, audit records and bytes during schema migration. Index creation/backfill lock duration must be assessed on an isolated copy.
- Validate forward migration against terminal/active/empty-byte historical fixtures and then new jobs; prove no early purge and correct boundary behavior. Reverse-schema dry-run/isolated exercise must preserve old columns; dropping new expiry metadata cannot restore bytes already purged. Rollback requires suspending purge/new execution first and a documented backup/restore choice for genuinely lost bytes.
