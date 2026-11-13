# Quickstart: isolated import operations

Run from `/home/hossein/Desktop/projects/building-management`. The executable guide is [ops/a7-p5/README.md](../../ops/a7-p5/README.md). These are implemented commands; evidence and remaining acceptance limits are in [evidence/verification.md](evidence/verification.md). Do not substitute host inline tests for worker evidence.

## Private environment

The Compose project is `a7p5-import`; services are `postgres`, `redis`, `api`, `import-worker`, `maintenance-worker`, `beat`. Database: `a7p5_import`; queues: `a7p5-import` and `a7p5-maintenance`; eager/inline preparation false; prefetch/concurrency one. Local ports: API18000, PostgreSQL55432, Redis56379, separate frontend15173. Shared services8000/5173/5433/6379 are untouched. The private env/auth fixture files are ignored and mode0600; never export resolved credentials.

Linux cgroup v2, Docker Compose and narrow sudo are required. `prepare-host.sh` creates only transient `a7p5-containment.service`, delegates memory/pids/cpu controllers and mounts a dedicated256MiB tmpfs at `/run/a7p5-scratch`. API/importer/maintenance bind only that delegated subtree at `/var/a7p5-cgroup`, using host cgroup namespace and private PID namespaces. No whole-host writable cgroup, privileged container or Docker socket is provided. A deployment must supply equivalent narrow delegation and bounded storage.

```bash
ops/a7-p5/prepare-host.sh
# Only when the private env does not exist:
cp ops/a7-p5/.env.acceptance.example ops/a7-p5/.env.acceptance
chmod 600 ops/a7-p5/.env.acceptance
ops/a7-p5/run-acceptance.sh
```

This workstation can build through its existing authorized local proxy without changing global network configuration:

```bash
A7P5_BUILD_NETWORK=host A7P5_BUILD_PROXY=http://127.0.0.1:2080 ops/a7-p5/run-acceptance.sh
```

One image is reused by API/import/maintenance/Beat; API alone performs migrations. Workers wait for API health. The API uses Gunicorn timeout90 seconds; any delivery upstream must exceed90 seconds. Disable entrypoint RabbitMQ waiting with empty RABBITMQ_URL. Keep Django4.2.11; do not install requirements-dev.txt wholesale because debug-toolbar can upgrade Django.

## Runtime checks

The script validates configuration without printing it, builds/starts the private stack, retries real preflight, runs the matrix and exports `preflight.json` / `manifest.json` even when matrix exits nonzero. Preflight refuses non-phase database/broker/queues, eager/inline mode, unattachable containment, unbounded scratch and absent independent import/maintenance workers. It records versions, source-tree identity and effective controls. Its status is readiness for matrix execution, not feature acceptance.

The ten matrix groups cover native MPP and P6 XER success; jobless unreadable/protected/corrupt/type rejection and maximum50MiB admission versus oversized refusal; a separately admitted native-file failure; repeated delivery and capacity precedence for both families; actual timeout; actual memory/output/disk exhaustion plus expansion rejection; worker death before/during/after commit and during failure recording; original expiry; scratch cleanup; healthy follow-up. Both import families participate in commit/rollback interruption checks. Named private file barriers are guarded by isolated database identity and `A7_P5_ISOLATED=1`; no HTTP fault switch exists.

JPype is the default native route. `MPP_MPXJ_JAR_DIR` explicitly configures the installed MPXJ jars. The native-success group also forces JPype unavailable inside one private fresh helper, exercising the actual Java CLI fallback and comparing stored figures. MPXJ's current `org.mpxj` and legacy `net.sf.mpxj` CLI entry classes are selected from the configured jars. Both routes share the same conversion deadline and cgroup/scratch budget; limit failures cannot launch fallback. This proves the tested file/version, not universal Microsoft Project year support.

After the matrix, run actual private broker loss/restoration:

```bash
python3 ops/a7-p5/check-broker-outage.py
```

This script pauses after durable intake, stops only Compose's private Redis, releases publication, observes the admitted response, restores Redis in a finally block, reconciles the fixed dispatch deadline and verifies DONE plus a later healthy import. Never stop a host/global broker for this check. Do not run it concurrently with matrix/browser seeding.

Runtime retention/recovery uses explicitly aged disposable timestamps rather than waiting seven days or changing system time. Actual queues, kernel OOM, SIGKILL, PostgreSQL rollback/commit and maintenance remain real. At least201 rows across both families drain in consecutive pages; a real locked row, later arrival and competing maintainer verify cohort fairness. Deterministic tests separately exercise exact168-hour boundaries and budget failure. W_recovery(N)=60+480+10*N+ceil(N/100); W_purge(N)=3600+480+10*N+ceil(N/100) seconds, with zero detection delay during startup catch-up. B=100, C=10 seconds/item, G≤1 second. These conservative engineering budgets assume healthy services; unavailable services/budget exhaustion remain blocked/failed, never a passing deadline claim.

## Browser

After all runtime fault checks finish:

```bash
python3 ops/a7-p5/seed-browser.py
VITE_API_BASE_URL=http://127.0.0.1:18000/api pnpm --filter web exec vite --host 127.0.0.1 --port 15173 --strictPort
```

In another terminal:

```bash
A7P5_BROWSER_FIXTURES="$PWD/ops/a7-p5/.runtime-auth.json" pnpm exec playwright test --config=e2e/playwright.a7-p5.config.ts
pnpm typecheck
```

Four tests cover Persian/English at1280/390px, keyboard operation, remembered FAILED attempt, fresh upload, actual multipart intent=retry/retry_of, new attempt, interrupted status request and same-job status refresh without another start. The real API/worker must finish it. Screenshots are exported; private tokens stay out of evidence. The automation attaches files; native OS picker behavior is not claimed. API regression tests cover invalid/cross-project/missing retry linkage.

## Regression and maintenance

Use pytest, not manage.py test. Host regressions need a new phase-specific PostgreSQL test DB and explicitly label eager/inline/cache overrides. Run `ops/a7-p5/check-host.sh` after host preparation for the exact regression selection and JUnit export. It creates a new phase-specific test database and uses narrow delegated kernel probes via sudo; it does not use the private Docker database. The final result and JUnit are linked in verification.md. Migration tests exercise forward preservation/backfill and reverse-schema awareness in a disposable database. A preflight guard test is not proof of actual kernel limits.

```bash
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec api python manage.py maintain_import_jobs --dry-run
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec api python manage.py maintain_import_jobs --operation recovery
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec api python manage.py makemigrations schedule --check --dry-run
```

Recovery/abandoned scratch:60 seconds; original-byte purge:hourly after terminal anchor+168 hours. Dry-run preserves files/bytes. Cleanup kills only verified expired owned containment, quarantines unverifiable work, preserves active/unexpired/unrelated artifacts, and never deletes action history. No raw-file download right is added.

## Rollout, rollback and independent reproduction

This bundle does not deploy. Before enabling lifecycle/late-ack/maintenance in a delivery environment, stop admission and drain old import workers, back up DB, apply additive schedule migrations0016/0017, validate containment/settings, run startup catch-up, start separate workers/Beat and reopen admission only after success. Review actual migration names in traceability.md. Rollback requires drained workers and the recorded reverse-schema procedure; already purged original bytes require backup restore and cannot be recreated by reversing schema. Do not delete historical jobs/results.

For a clean independent repeat, export evidence, inspect the exact Compose project's `ps`, then use the same env/file identity with `down -v`; rerun this guide from new private DB/broker state. Preserve source fixture SHA256 and record actual image/source versions. Clean only this disposable stack. After its containers stop, the dedicated tmpfs may be unmounted and only `a7p5-containment.service` stopped. A second operator records their own observations in reproduction.md; the implementer's repeated run is insufficient. Every failure/not-run scenario must remain explicit and prevents full acceptance.

Maintenance completion exits nonzero when blocked/failed, including a competing leader; retry after the owning pass completes. Invalid batch arguments are command errors. Scratch uses a finite snapshot, pages of at most100, bounded manifest reads and per-item budgets; recovery admission opens only after both job recovery and owned scratch verification succeed. Dry-run does not reopen admission.

After matrix/broker checks, run `python3 ops/a7-p5/check-concurrent-delivery.py`. It temporarily starts a second private importer, confirms a live duplicate returns before the paused original resumes for both MSP/P6, verifies one commit and terminal replay, then removes only its created container in finally. The preparation-slot profile stays one. Do not run concurrently with matrix/browser seeding.

Application uses a cumulative90-second deadline bounded by the remaining180-second job execution deadline. Each SQL statement receives only the remaining application budget; final DONE and transaction cleanup respect the same boundary. SQL budget exhaustion rolls back before a sanitized failure is recorded.
