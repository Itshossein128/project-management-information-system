# Contract: Schedule Import Operations

Proposed extension of existing MSP/MPP and P6 interfaces. P2 safety/P3 fidelity/P4 UX remain authoritative. See [runtime containment](runtime-containment.md).

## Existing interface compatibility

Under `/api/v1/projects/<project-id>/` (config/urls.py and projects/urls.py:295), retain:

- POST `import/msp/preview/`, POST `import/p6/preview/`: same synchronous preview bodies, recognized kind, warnings, replacement figures and no persistent schedule mutation or business job. Shared bounded preparation is mandatory even here.
- POST `import/msp/`, POST `import/p6/`: multipart `file` plus `replace`; response 202 with `task_id` equal to the durable job UUID and status `queued` for admitted work. Before durable admission, input validation failures return their existing 4xx error envelope, while capacity/dependency refusals retain their defined operational errors; no business job is created for these rejections. Existing safety refusals that already persist a FAILED history job retain that behavior, include its identifier and set terminal/retention timestamps. After durable admission, a background failure updates that job to FAILED; it is never reported as an unadmitted rejection.
- GET `import/msp/status/<task_id>/`, GET `import/p6/status/<task_id>/`: same project-bound status, progress_pct, DONE result, FAILED error/error_code/blocking. Status reads never queue or restart work.

Start ordering is normative: authorize the current actor/project and perform cheap bounded upload checks, compute the accepted upload digest/size, then find the same actor/project/family/mode/file in-flight job under the existing project lock. If found, return its existing 202 identifier immediately without reserving a preparation slot, rerunning conversion, or returning processing_busy, even when the sole slot is occupied. Only a genuinely new submission proceeds to capacity reservation and contained validation; release capacity-row locks before taking project/job locks. Recheck for an in-flight match under the project lock after preparation before creating a job, closing the concurrent-start race. Persisted digest/size is not cross-project authority. A fresh confirmation after completion remains a new job; idempotence is per durable job, not global same-file suppression.

Start accepts multipart `intent` with values `new` or `retry`; omitted intent means `new` for existing clients. For `intent=new`, retry_of must be absent. For `intent=retry`, retry_of is required and identifies a FAILED predecessor in the same family/project; validate current actor permission and predecessor visibility without requiring that the original actor still has access. Missing/invalid/cross-project linkage is rejected before admission without disclosing the target. The existing wizard's explicit Retry flow captures the failed job identity, requests a fresh file, and sends both intent=retry and retry_of through the MSP/P6 API client; a fresh-import action clears that context and sends intent=new. Status-refresh retry only rereads the existing attempt. New business retries always require an upload, including after expiry, preserve the predecessor deadline, and get their own job identity/lifecycle. No raw-file download/replay endpoint or auto-guessed predecessor is added.

## Dispatch and execution

1. Commit intake and delivery identity before publish. Publish after commit with a bounded connection/retry budget (initial profile: five seconds total); a failure to publish does not discard the durable PENDING job. Once durably admitted, return its 202 identity; reconciler later publishes or records an actionable terminal dispatch failure.
2. Per-import late acknowledgments are enabled only after atomic outcome/idempotence exists. Do not change global worker-loss rejection or unrelated tasks. Redis visibility timeout is configured above the 180-second maximum attempt duration (profile: 600 seconds).
3. Project→job lock order applies to claim, application, failure and maintenance. Concurrent delivery with live token returns without applying. A PENDING job past dispatch_deadline_at cannot be claimed even if the maintenance scan has not reached it; it is terminalized under the same locks. Expired execution is terminalized rather than silently taking over; a deliberate retry is a fresh job.
4. Background preparation is untrusted/read-only. Before apply, validate bounded prepared data and token, recheck P2 actor/membership/state/protected-history rules, and resolve against the current project with P3 semantics. A client cannot supply its own prepared plan.
5. Domain mutation, result, DONE, terminal timestamps and 100% are committed atomically. A late acknowledgment failure is recovered by reading that outcome. A pre-commit crash rolls back and later reconciles as failure.
6. Progress uses committed milestones during preparation; 100 only inside final success. Application progress may remain at its last committed stage until final commit; no false precision or separate connection writes to a locked row.

## Failure vocabulary and privacy

Retain existing `processing_timeout`, `conversion_failed`, file/parse, safety and fidelity codes. Add only where no existing meaning suffices: `processing_resource_limit`, `processing_interrupted`, `processing_busy`, `input_expired`; provide matching Persian/English messages. Generic unknown failures use `import_failed`, never raw `str(exc)` in public job errors. Dispatch expiry uses sanitized `import_failed` with an actionable retry message.

Capacity exhaustion for preview or a genuinely new start returns 503 with `processing_busy` and a retry hint, without creating a job. An authorized matching in-flight start takes precedence and returns its existing job without capacity admission; an already-queued background attempt waits within its fixed dispatch window. A missing containment prerequisite returns existing `conversion_failed`. Job status GET retains its current successful HTTP read shape even when the business attempt failed.

Stable user-facing error identifiers are not translated. No token, credentials, helper command environment, raw Java exception, source excerpt or unrestricted disk location appears in public status/logs. Authorized diagnostics remain subject to existing sensitive-file policy and organization/project isolation. Seven-day retention does not itself authorize any file access.

## Maintenance and seven-day retention

Proposed `maintain_import_jobs` command and equivalent existing Beat tasks expose independent operations: reconcile dispatch/execution, reclaim expired scratch/containment, and purge expired originals. Support dry-run, bounded batch size, a deterministic test clock in isolated tests, and nonzero exit on failed mandatory cleanup; never log contents/secrets. Production clock cannot be changed by an unauthenticated API parameter.

- Reconcile every 60 seconds; dispatch expiry 300 seconds; execution expiry 180 seconds from claim. Use the runtime contract's oldest-first finite-cohort protocol, per-item/batch budgets and computable recovery/expiry bounds. Drain successive batches immediately rather than waiting another full scan interval; new work cannot starve the existing cohort.
- Reconciliation is independent of the import execution queue so a stuck converter cannot block it. It uses a narrow delegated containment root and database leases, never arbitrary OS PIDs.
- Original-byte purge every hour; delete at first eligible successful run after terminal anchor + 168 hours. With maintenance healthy, lateness follows the finite-cohort bound in the runtime contract; the hourly interval alone is not a completion bound. Record cohort size, duration and actual lag/failures. After service restoration, run a catch-up scan before admitting fresh processing, then continue periodically.
- Temporary artifacts are removed after process termination; after restart, reclaim expired containment/workspaces on the first maintenance scan. Active inputs, unexpired originals and unrelated files remain protected. Never remove a workspace until its owning process group/cgroup is confirmed empty.
- Purge clears file_data only, sets file_purged_at, and preserves digest/size, actor/project/mode/file identity, terminal timestamps and sanitized result/history. Repeated purge is a no-op. Retry/redelivery/status reads cannot extend expiry.

Acceptance tests must cover each transition and fault window, all three input paths, both job families, cleanup boundaries and a subsequent healthy native import. None of this contract is reported implemented by planning.
