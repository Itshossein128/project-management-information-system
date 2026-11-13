# A.7-P5 isolated import runtime

The stack owns only database `a7p5_import`, private Redis and queues `a7p5-import` / `a7p5-maintenance`. API: `127.0.0.1:18000`; PostgreSQL: `55432`; Redis: `56379`; separate browser frontend: `15173`. Existing services on 8000/5173/5433/6379 are not changed.

## Host preparation and build

Linux/systemd, Docker Compose, the repository dependencies and narrowly scoped sudo are required. From repository root:

```bash
ops/a7-p5/prepare-host.sh
cp ops/a7-p5/.env.acceptance.example ops/a7-p5/.env.acceptance
chmod 600 ops/a7-p5/.env.acceptance
ops/a7-p5/run-acceptance.sh
```

Do not overwrite an existing private env file just to rerun. `prepare-host.sh` creates only transient unit `a7p5-containment.service`, its delegated subtree and a dedicated 256 MiB tmpfs at `/run/a7p5-scratch`. The sleeping manager is moved into a child before enabling memory/pids/cpu controllers. Containers bind only that subtree at `/var/a7p5-cgroup`, using the host cgroup namespace and private PID namespaces; no whole-host cgroup write mount, Docker socket or privileged container is used. Shared scratch lets maintenance see the importer/API artifacts. A common runtime host identity plus boot ID scopes recovery.

If the local build network cannot reach package downloads, use an already authorized local HTTP proxy for the build only, for example on this workstation:

```bash
A7P5_BUILD_NETWORK=host A7P5_BUILD_PROXY=http://127.0.0.1:2080 ops/a7-p5/run-acceptance.sh
```

This changes neither system DNS nor daemon/proxy configuration. Build proxy arguments do not persist in the image. The regular API Dockerfile and pinned Django 4.2.11 are preserved; actual image/dependency versions are recorded by preflight. The acceptance configuration builds one tagged API image and reuses it for workers/Beat. Only API runs initial migrations; workers wait for API health and skip migration startup races.

## Real execution and evidence

Preflight requires a writable, actually attachable helper cgroup, bounded scratch, eager/inline modes off, private DB/broker identity and separate responding workers. Mere presence of Java/packages is insufficient. `run-acceptance.sh` runs the actual native MPP, XML/P6 and adverse-path matrix and exports `preflight.json` / `manifest.json` under `specs/055-a7-p5-import-operations/evidence/runtime/`.

The private fault directory is available only when `A7_P5_ISOLATED=1` and the selected database contains `a7p5`. Test barriers kill actual worker children before apply, after domain writes before commit and after commit before acknowledgment. Helper probes exercise actual timeout, memory/output/scratch limits and parent death. Explicitly aged disposable timestamps accelerate deadline/expiry cases; the report labels that fixture technique. Kernel controls, worker termination, DB rollback/one-time commit and maintenance processing remain real. No fault control is a public HTTP input.

After the matrix, run `python3 ops/a7-p5/check-broker-outage.py` for an actual private Redis outage between durable intake and publication, restoration and reconciliation. The matrix also forces JPype unavailable in one fresh helper and exercises the explicitly configured MPXJ Java CLI fallback, comparing stored results. See the feature quickstart for rollback and cohort-check details.

Do not run two acceptance/browser seed operations concurrently: they share private fault controls. Report failures/non-run scenarios as such; a passing preflight alone is not a passing matrix. Missing containment fails closed. API feedback retains stable localized codes and excludes raw source/exception details. Test output includes no credentials.

## Real browser retry

After the runtime matrix completes, prepare new private UI subjects:

```bash
python3 ops/a7-p5/seed-browser.py
VITE_API_BASE_URL=http://127.0.0.1:18000/api pnpm --filter web exec vite --host 127.0.0.1 --port 15173 --strictPort
```

In another terminal:

```bash
A7P5_BROWSER_FIXTURES="$PWD/ops/a7-p5/.runtime-auth.json" pnpm exec playwright test --config=e2e/playwright.a7-p5.config.ts
```

The ignored fixture file is mode 0600 and contains local test tokens; never paste/commit it. Four real browser cases use Persian/English and desktop/phone widths, a seeded FAILED predecessor, a fresh-file business retry processed by the actual worker, an interrupted status request followed by status refresh without another start, and cleared retry state for a fresh import. Native OS file-picker behavior is not claimed; automation attaches the file. Screenshots are saved under runtime evidence; failure traces stay in ignored test-results.

## Maintenance and teardown

Use this exact private Compose invocation:

```bash
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec api python manage.py maintain_import_jobs --dry-run
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec api python manage.py maintain_import_jobs --operation recovery
```

Recovery runs every 60 seconds; original-byte purge hourly after immutable terminal anchor +168 hours. Queue separation keeps maintenance available during importer loss. Cleanup verifies owned groups are empty, kills expired owned descendants when necessary and removes only owned artifacts. Dry-run preserves bytes and workspaces. Never infer whole-job deletion from byte expiry.

To remove only this disposable stack, inspect its `ps` output and then use the same file/env/project identity with `down -v`. After all its containers stop, `/run/a7p5-scratch` can be unmounted and only `a7p5-containment.service` stopped. These steps are not production deployment or shared-service cleanup. Preserve exported evidence before resetting the private database.

A genuinely independent operator still needs to repeat this guide from a clean isolated environment before T049 can be marked complete. Installed Java, host unit tests or the implementer's own second run cannot substitute for that criterion.

Maintenance completion exits nonzero when blocked/failed, including a competing leader; retry after the owning pass completes. Invalid batch arguments are command errors. Scratch uses a finite snapshot, pages of at most100, bounded manifest reads and per-item budgets; recovery admission opens only after both job recovery and owned scratch verification succeed. Dry-run does not reopen admission.

After matrix/broker checks, run `python3 ops/a7-p5/check-concurrent-delivery.py`. It temporarily starts a second private importer, confirms a live duplicate returns before the paused original resumes for both MSP/P6, verifies one commit and terminal replay, then removes only its created container in finally. The preparation-slot profile stays one. Do not run concurrently with matrix/browser seeding.

Application uses a cumulative90-second deadline bounded by the remaining180-second job execution deadline. Each SQL statement receives only the remaining application budget; final DONE and transaction cleanup respect the same boundary. SQL budget exhaustion rolls back before a sanitized failure is recorded.
