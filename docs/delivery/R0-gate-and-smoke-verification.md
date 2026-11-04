# R.0.04 — Gate failure/success control and smoke verification

Date: 2026-11-04 (Asia/Tehran). Task/WBS: `R.0.04`.

## Acceptance result

**R.0.04 implementation and local acceptance rehearsal passed.** Five
intentional failure scenarios returned gate exit code **1**; healthy checks
returned **0**. The unified rehearsal then passed **31/31 live smoke checks**
and exited **0**. An intentionally incorrect API base produced smoke exit **1**.

This is local process/HTTP/database/broker evidence against the changed working
tree, not a claim that a GitHub-hosted deployment ran. Gate API responses in
phases A/B are loopback fixtures; phase C uses real services without mocked
authentication, database, HTTP endpoints, or RabbitMQ. No production release
was performed.

## Reproduction

Run from the repository root. Python commands use `apps/api/.venv/bin/python`
(verified Django **4.2.11**). The existing `.env.test-env` must describe the same
database, signing key, Redis, and broker used by the API. Existing exported
environment values take precedence over env-file defaults, including in CI.

Prepare the isolated environment, if not already running:

```bash
cp -n .env.test-env.example .env.test-env
docker compose -f docker-compose.test-env.yml --env-file .env.test-env \
  up -d --wait postgres-test redis-test rabbitmq-test
set -a
source .env.test-env
set +a
apps/api/.venv/bin/python apps/api/core/manage.py migrate --noinput
apps/api/.venv/bin/python apps/api/core/manage.py seed_test_roles --skip-demo
apps/api/.venv/bin/python apps/api/core/manage.py setup_event_topology
apps/api/.venv/bin/python apps/api/core/manage.py runserver 127.0.0.1:8001 --noreload
```

Keep that server running and use another terminal for the drills:

```bash
# Harness exit 0 means the observed child gate exit was the expected 1.
apps/api/.venv/bin/python scripts/drill_gate_failure.py --scenario api-failure

# Both harness and child gate exit 0 for the healthy scenario.
apps/api/.venv/bin/python scripts/drill_gate_failure.py --scenario success

# Phases A/B/C; any unexpected drill result or smoke failure stops the runner.
scripts/rehearse_r0_gate_and_smoke.sh \
  --env-file .env.test-env --api-base http://localhost:8001
```

Each drill starts a temporary loopback GitHub API fixture and executes the real
`scripts/verify_ci_gate.py` in a child process. Tokens from the caller are
removed from that child's environment. The harness checks its actual exit
status, output, and API request count. A detected failure makes one runs request
and at most one jobs request, with no polling/retry after detection.

## Recorded gate evidence

The [complete successful rehearsal output](evidence/R0-gate-and-smoke.txt)
contains these observed results:

```text
PASS drill=workflow-failure gate_exit=1 requests=1
PASS drill=api-failure gate_exit=1 requests=2
PASS drill=web-failure gate_exit=1 requests=2
PASS drill=missing-api gate_exit=1 requests=2
PASS drill=cancelled gate_exit=1 requests=1
PASS drill=success gate_exit=0 requests=2
```

The failed API job prints:

```text
[ERROR] [CI-GATE] The following required jobs did not succeed: api (conclusion: failure). Deployment blocked!
```

The healthy gate prints:

```text
SUCCESS: [CI-GATE] All required CI checks passed for commit aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa! Proceeding to deployment.
```

The all-`a` SHA belongs only to the fixture. It is not a verified release SHA.
The final unified-runner exit code was **0**.

## Live smoke coverage

`scripts/run_smoke_test.py` replaces the permissive legacy smoke script for
R.0 acceptance. Review of `scripts/smoke-stack.sh` found suppressed progress/cost
errors and conditional skipping when no project exists; its success message is
not accepted as R.0.04 evidence. The new runner reuses environment, Django setup,
and blueprint-schema checks from `scripts/verify_test_env.py`.

The 31 required checks are:

- `GET /api/health/`: HTTP 200 and status `ok`.
- `GET /api/schema/`: HTTP 200 and a nonempty schema response.
- `verify_blueprint_schema`: successful management-command execution.
- All **11** catalog accounts log in via `/api/auth/login/` with `devpass123`.
  Access JWT signatures, expiry, token type, and database user identity are
  validated. Tokens are never printed. The API's 10/minute limit stays enabled;
  a 429 permits one retry after waiting 61 seconds.
- All **11** accounts list projects over HTTP. Every page is checked against
  the account's active database memberships (all projects for the superuser).
  Missing, extra, duplicate, empty, and looping results fail.
- A reference visitor without membership in the disposable project receives
  HTTP 403 for its cost summary.
- A site supervisor posts one report to `daily-reports/sync-batch/`; the runner
  requires exactly one created result with no conflicts/errors and verifies
  database persistence. HTTP 200 with per-item errors fails.
- Project controls reads `progress/s-curve/`: seeded planned **60%**, actual
  **40%**, variance **-20** must match the returned series.
- Finance reads `costs/summary/`: seeded budget **1,000**, approved actual cost
  **250**, committed **0**, and consumption **25%** must match. The actual cost
  creator and approver are different users.
- RabbitMQ's existing exchange and every catalog queue pass passive declaration;
  a uniquely routed message is confirmed, received, compared, and acknowledged
  through a temporary exclusive queue. No production topic receives a fake
  business event. This checks broker dispatch/topology, not background-worker
  business processing.
- The disposable project and its report are deleted and their absence verified
  even after a failed core check. Related fixture rows cascade with the project.

Writes are restricted to database names with a separate `test` component, such
as `ipcas_test_env`, `ipcas_test`, or `test_ipcas`. The runner creates its own
project, memberships, WBS, activity/progress, budget, and cost. It does not reset
existing reference users or mutate their reference projects.

Observed final output:

```text
PASS progress S-curve
PASS cost control summary
PASS RabbitMQ topology and confirmed event round-trip
PASS disposable project cleanup
SMOKE 31/31 passed; 0 failed (100% pass)
PASS R.0 gate and integration smoke rehearsal
```

Negative live verification:

```bash
apps/api/.venv/bin/python scripts/run_smoke_test.py \
  --env-file .env.test-env --api-base http://localhost:8001/r0-intentional-missing
```

This deliberately targets nonexistent endpoints; it performs no fixture writes
because authentication fails. [Recorded output](evidence/R0-smoke-intentional-failure.txt):

```text
FAIL API health: RuntimeError: GET /api/health/: expected HTTP 200, got 404
SMOKE 1/15 passed; 14 failed
```

Observed smoke process exit code: **1**. No `100% pass` message was printed.

## Automated checks and CI enforcement

```bash
apps/api/.venv/bin/python -m pytest scripts/tests -q

(
  set -e
  set -a
  source .env.test-env
  set +a
  cd apps/api/core
  ../.venv/bin/python -m pytest \
    permissions/tests/test_role_accounts_auth.py \
    field_reports/tests/test_sync_batch.py \
    schedule/tests/test_progress.py \
    cost_control/tests/test_cost_control.py \
    events authentication audit storage --reuse-db -q
)
```

Observed results: **37 script tests passed** and **89 selected backend tests
passed**, exit **0** for each command. These include all 14 reference-account
tests. Existing dependency deprecation notices and the short non-secret test
signing-key warning remain; Django was not upgraded. Two stale tests were
corrected: progress-cache invalidation now uses a separate cost approver, and
the rate-limit test explicitly requests English with the documented login field.

The regression tests also inspect the actual workflow definitions:

- `.github/workflows/deploy.yml`: `deploy.needs` is `[verify-ci-gate]`, the
  default success condition is retained, and neither the gate job nor its command
  allows errors to continue. A failing gate therefore skips `deploy` under
  Actions dependency semantics. This is verified configuration, not an observed
  hosted skipped job.
- `.github/workflows/ci.yml`: the required `api` job runs script regression
  tests and the unified live rehearsal. Smoke failures propagate as job failures;
  the deploy gate requires successful `web` and `api` jobs for its target SHA.
  Deployment-workflow edits now also trigger CI. Redis is supplied for live
  health/login, and eager tasks avoid requiring a Celery worker.
- CI creates the API virtualenv and installs the pinned runtime plus compatible
  pytest/PyYAML dependencies, avoiding the debug-toolbar dependency that would
  upgrade Django. The former `manage.py test` step uses pytest.

## Formal R.0 disposition and handoff

- **R.0.01 — Complete**, carried forward from the accepted scope/report contract
  in [R0-scope-and-reports-contract.md](R0-scope-and-reports-contract.md).
- **R.0.02 — Complete for implementation and local gate rehearsal**, with
  required workflow/job outcomes, actual process exits, and deployment dependency
  protected by the regression tests above.
- **R.0.03 — Complete per the accepted task baseline supplied with this request**.
  This run additionally reconfirmed isolated PostgreSQL/Redis/RabbitMQ, blueprint
  schema, and all reference accounts. MinIO/file-storage acceptance from that
  prior task was not re-audited here.
- **R.0.04 — Complete for local acceptance**, based on the recorded blocked and
  healthy gate exits, 31/31 live checks, negative smoke exit, and selected tests.

**Phase R.0 is closed for this local implementation/rehearsal scope and ready to
transition to Phase A.6 — Users & Access Boundaries.** This does not attest full
product acceptance or authorize a production release. A release must still pass
the actual required hosted CI jobs on the exact SHA being deployed.

Evidence limits: no GitHub Actions run was dispatched, no production job was
executed, and the full repository/backend suite, frontend checks, browser E2E,
MinIO uploads, and background-worker processing were not run in this task.
