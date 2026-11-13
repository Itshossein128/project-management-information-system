# Research: Import Operations

**Date**: 2026-11-12. Research/design only; decisions below are not current implementation claims.

## R1 — Durable business outcome and delivery repeats

**Decision**: Extend existing jobs with bounded fenced ownership. Claim before preparation; use a consistent project→job lock order for final application. Re-read terminal status/ownership under lock. Apply domain writes and DONE/result/100%/completed_at in one transaction. On rollback, write a sanitized terminal failure in a separate transaction only if the same execution token still owns the attempt. Terminal deliveries are read-only no-ops, including FAILED.

**Rationale**: `schedule/tasks.py:46–77` checks DONE outside locking and records DONE after the domain transaction commits. This creates duplicate-delivery and commit/reporting windows to verify. Stage progress written on the transaction's own connection is not visibly incremental until commit; persist preparation-stage progress beforehand, not via a second connection blocked on the same locked job.

**Alternatives considered**: Separate result/domain commits; treating Celery SUCCESS as the authoritative schedule outcome; promises of exactly-once message delivery. All rejected: the required guarantee is at-most-one committed application per durable job.

**Primary references**: [Django 4.2 transactions](https://docs.djangoproject.com/en/4.2/topics/db/transactions/), [row locking](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#select-for-update), [Celery tasks/late acknowledgment](https://docs.celeryq.dev/en/v5.6.3/userguide/tasks.html). Late acknowledgment follows idempotency; worker loss does not guarantee redelivery, and unrestricted worker-loss rejection risks poison loops.

## R2 — Dispatch, lost workers and retry

**Decision**: Pending jobs are durable dispatch intent, published after commit with a persisted delivery UUID. A 60-second maintenance trigger republishes unclaimed pending work within a 300-second dispatch window; afterward it records failure. Stable oldest-first cohorts drain consecutive batches without waiting another full interval. The runtime contract specifies N-dependent bounds with per-item C=10 seconds, B=100 and G≤1 second, fair deferred-row handling and failed/blocked outcomes on maintenance-budget violations; startup admission stays closed until catch-up completes. A claim establishes an immutable 180-second execution deadline and token. Expired claims become FAILED under locks; no automatic business retry. A deliberate user retry is a newly authorized same-family job with mandatory failed-predecessor retry_of linkage and a fresh upload. Multipart intent=retry requires that linkage; intent=new (default for old clients) forbids it. The wizard/API client must propagate explicit retry context; polling status again is not a business retry. Redis broker visibility timeout is 600 seconds in the isolated profile; it does not replace reconciliation.

**Rationale**: `schedule/views.py:178–188` commits the job before `.delay`; `on_commit()` alone cannot close crash-before-publish. Source settings use Redis by default; RabbitMQ elsewhere serves events and is not a reason to migrate import broker. Existing Beat can maintain jobs without a new scheduler family. An authorized matching in-flight confirmation is resolved before capacity admission, with a locked post-preparation match recheck for a genuinely new request; this preserves P2 during sole-slot saturation.

**Alternatives considered**: Infinite retry/requeue; requiring broker result state to prove death; global worker-loss policy changes. Rejected in favor of bounded, observable failure and explicit retry.

**Primary references**: [Celery configuration](https://docs.celeryq.dev/en/v5.6.3/userguide/configuration.html#task-reject-on-worker-lost), [Redis visibility timeout](https://docs.celeryq.dev/en/v5.6.3/getting-started/backends-and-brokers/redis.html#visibility-timeout). Profile values are engineering choices requiring acceptance evidence, not a new customer SLA.

## R3 — Killable conversion across every entry path

**Decision**: Use a fresh exec/spawn Python helper with JPype/JVM initialized only inside it. Share the bounded preparation adapter between preview, genuinely new start validation and worker, including XML/XER parsing and serialized prepared-result limits. Pre-admission input failures return actionable errors without a business job; failures after durable admission update that job, while existing stored safety refusals retain their FAILED history. Retain JPype-first and configured CLI fallback inside one monotonic conversion deadline. Never fallback after timeout or resource exhaustion. Return validated bounded prepared data to existing P2/P3 application code; do not accept executable pickles or caller-supplied prepared plans.

**Rationale**: `mpp_convert.py:62–114` starts a JVM in the caller and leaves a daemon thread alive after timeout. Lines 167–190 limit the immediate CLI child but capture unbounded output. `views.py:88–108,136–148` also converts in API requests, so worker-only controls miss preview/start.

**Alternatives considered**: Thread join timeout; forking an initialized JVM; worker-only hard limits; silent unbounded fallback. Rejected because they fail real termination or miss synchronous paths.

**Primary references**: [JPype multiprocessing](https://jpype.readthedocs.io/en/latest/userguide.html#multiprocessing), [JPype API](https://jpype.readthedocs.io/en/latest/api.html), [Python 3.12 subprocess](https://docs.python.org/3.12/library/subprocess.html). Use `start_new_session`, explicit group termination/reaping, and no threaded-parent `preexec_fn`.

## R4 — Effective containment and deadlines

**Decision**: Require a delegated cgroup-v2 subtree and dedicated bounded scratch filesystem for the helper, fail closed when unavailable, and verify actual effective limits before admitting input. Initial isolated profile: one preparation slot; 1 GiB whole-helper memory with swap disabled, JVM heap 512 MiB, 32 processes/threads maximum, one CPU quota, 256 MiB scratch, 128 MiB converted/prepared output and 64 KiB diagnostic output. Conversion default remains 60 seconds total across startup/routes; preparation deadline 75 seconds; process-kill grace 2 seconds included in it. Preview/start request timeout 90 seconds, with gateway timeout greater than that. Import soft/hard execution bounds 170/180 seconds include preparation, lock wait and application. Application statement budget 90 seconds and lock wait 3 seconds must also fit the remaining absolute attempt budget; abort rather than reset its clock per statement.

**Rationale**: Upload size and JVM heap do not bound native/helper memory or decompression/output. Production Gunicorn timeout is currently 60 seconds, equal to conversion default (`docker-compose.production.yml:28`); it must permit controlled failure response within the request budget. Production concurrency two is not measured import capacity. Docker has no default memory cap.

**Alternatives considered**: RLIMIT_RSS or Xmx alone; arbitrary API-wide memory caps; spawning Docker containers through a privileged socket from request code. Rejected. Use host-provisioned narrow containment delegation; no unrestricted Docker socket or root API. If the delivery platform cannot delegate containment, record an operational gate rather than run unbounded.

**Primary references**: [Linux cgroup v2 interface](https://docs.kernel.org/admin-guide/cgroup-v2.html) and [Docker resource constraints](https://docs.docker.com/engine/containers/resource_constraints/). Numbers are explicit safety settings for empirical calibration; require actual reference-file success and measured memory/output before release. Legitimate inputs exceeding them require a recorded configuration revision and full bound/failure recheck, not silent bypass.

## R5 — File lifecycle and historical rows

**Decision**: User-approved original-file retention is 168 elapsed hours after immutable completion, then byte-only purge on an hourly-triggered oldest-first cohort drain. The runtime contract's W_purge(N) includes all cohort work ahead of the item; hourly triggering alone is not a completion guarantee. Store digest/size separately; retain job/result/audit metadata. Temporary artifacts are removed immediately after process termination and reconciled after restart every 60 seconds. New directories are private (0700), owned by random execution token, and never use source filenames. No new raw-file download endpoint is introduced.

**Rationale**: Original bytes are currently stored in `BaseImportJob.file_data` (`models.py:623–665`); tasks read them at line 54 without a reviewed purge rule. Persisted digest avoids dependence on expired bytes. `import_safety.py:160–171` currently hashes retained candidates during in-flight matching.

**Alternatives considered**: Deleting whole job rows; using mutable updated_at as a genuine historical completion time; purging active input; preserving raw bytes indefinitely. Rejected. Historical terminal rows receive a labeled migration-time retention anchor; active legacy rows remain protected until reconciliation. Cleanup and retry never reset a terminal deadline.

## R6 — Actual environment and evidence

**Decision**: Reuse PostgreSQL, Redis and Celery in an isolated phase-specific configuration. Keep API/event worker/import Celery/Beat roles distinct, with maintenance independently available while conversion work is blocked. Require real `plan.mpp` preview/import, crash windows, output/memory/time/temp-limit checks, cleanup/expiry and healthy follow-up. Capture dependency versions from the tested image.

**Observed inventory**: Local Python 3.12.3, Django 4.2.11, Celery 5.6.3, MPXJ 16.10.0, JPype 1.7.1, Redis client 8.0.1, OpenJDK 21.0.12.1; Docker/Java/Redis executables exist. Daemons, delegation and permissions were not assessed. No RabbitMQ executable was found; Redis is already the import broker.

**Alternatives considered**: Eager tests as deployment proof; assuming installed Java proves conversion; reusing shared database/Redis/queues. Rejected. Two read-only research agents reviewed runtime lifecycle and conversion containment; no services/tests were run by them.

## Resolved unknowns and remaining gates

All product/design choices needed for Phase 1 are resolved, including seven-day retention. P4 handoff/integrated predecessor readiness was subsequently verified through the user-authorized 93-test local integrated recheck and actual P4 handoff; see the current P5 handoff. This resolves that local prerequisite only. Delegated helper containment, bounded scratch, actual delivery services and profile calibration remain deployment/acceptance gates. These have explicit required behavior; none is reported verified. The latest invocation authorizes independent design without waiving those gates.
