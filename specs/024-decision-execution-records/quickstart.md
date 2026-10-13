# Validation Guide: Traceable Decision Execution Records

This guide describes implementation-time validation. Proposed feature-024 tests/helpers do not exist at planning completion. Commands below become evidence only when run on the implemented final tree. No application suite, live acceptance or new mutation is claimed by this plan.

## Preconditions and preservation

- Work from `/home/hossein/Desktop/projects/building-management`; confirm active feature `024-decision-execution-records`, branch and dirty work before editing. Preserve source documents, requirements/checklist and earlier 018–023 work. Save a hash/source baseline and retain meaningful red/green logs.
- Python API environment is `apps/api/.venv`, Django pinned to 4.2.11; Spec Kit uses root `.venv`. Do not install full `requirements-dev.txt`, upgrade Django or reset the development database.
- PostgreSQL must accept connections on the root `.env` configured port (local convention 5433), Redis must respond on 6379. Use existing native services; no Docker/RabbitMQ/MinIO is required for this feature.
- Local API flags: `AUDIT_LOG_ASYNC=false`, `CELERY_TASK_ALWAYS_EAGER=true`. Do not print `.env`, authorization tokens or passwords in retained logs. E2E uses its existing disposable role/project setup.
- Existing API/web servers may be reused. If needed, run `pnpm dev:api` and `pnpm dev:web` separately from the project root; `pnpm dev` requires Docker. The dedicated app Playwright config starts/reuses servers and has one worker. Do not run production-like mutations to obtain evidence.

```bash
cd /home/hossein/Desktop/projects/building-management
pg_isready -p 5433
redis-cli ping
apps/api/.venv/bin/python -c 'import sys,django; print(sys.version.split()[0], django.get_version())'
```

## TDD slices before implementation

1. Add parameterized stale-caller/selection/deletion and PostgreSQL lock-wait tests for all existing live engines, plus preserved DEMATEL placeholder compatibility. Observe actual lock wait using separate connections/synchronization; after holder release, assert authoritative snapshot/result or zero append on rejection. Reproduce the non-ISM gaps before the common transaction fix; correct existing ISM behavior is a regression.
2. Add targeted PATCH/delete contention and fixed-UUID equal-time pagination tests. Verify exact `(-extracted_at,-id)` order and every filtered/unfiltered ID once, rather than relying on nondeterministic natural ordering to happen to fail.
3. Add pure guard/classification cases for malformed new responses and partial historical content, preserving legacy AHP row order and raw malformed drafts. Client guards verify structure without recomputing scientific output.
4. Add real EN/FA browser historical ranking review after live edits; prove selection no longer injects historical rows into current panels. Add delayed detail then page/filter/case change and failed read after previous success before navigation fixes.
5. Add global-save and SAW/TOPSIS/AHP malformed 2xx and committed-POST lost-response red cases; retain ISM equivalents as regressions. Hold/fail/timeout recovery, filtered/page-two display and A→B→A tokens before shared orchestration changes. Forward POST to the real server, capture its 201 ID, then lose only its response; intercepted failure alone is not persistence proof.

Proposed focused tests:

```bash
cd /home/hossein/Desktop/projects/building-management
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
cd /home/hossein/Desktop/projects/building-management/apps/api/core
../.venv/bin/python -m pytest --reuse-db decision_support/tests/test_execution_records.py -q
```

New tests follow the existing transaction-test RBAC catalog fixture; do not flush/reset the development DB. A future transaction test must use pytest-django transaction support and restore migration-owned test catalog as required by `decision_support/tests/conftest.py`.

## Final backend and schema checks

```bash
cd /home/hossein/Desktop/projects/building-management
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
cd /home/hossein/Desktop/projects/building-management/apps/api/core
../.venv/bin/python -m pytest --reuse-db decision_support/tests -q
cd /home/hossein/Desktop/projects/building-management
bash apps/api/django.sh makemigrations --check --dry-run
```

Expected: independent SAW/TOPSIS/AHP/ISM outputs, raw/normalized input traceability, zero append on known rejection, repeated identical explicit runs remain distinct, old-run full equality, deterministic pagination, locked authoritative execution/PATCH/soft delete, existing access/isolation and immutable routes all pass. No schema change expected. `manage.py test` is not an adequate runner for these pytest fixtures.

## Frontend guards and type evidence

```bash
cd /home/hossein/Desktop/projects/building-management
node --experimental-strip-types --test apps/web/src/components/decision-support/*.test.ts apps/web/src/app/lib/api/decision-support.test.ts
pnpm typecheck
```

Expected: new `execution-record-rules.test.ts` and shared orchestration/recovery helper tests plus existing input/ISM/AHP guards pass. Test the real local API response boundary, not only a copied implementation. Structural/source checks supplement browser evidence; they do not establish persistence or access enforcement.

Prior feature 023 typecheck evidence reported five unrelated errors in four unchanged files. Record the new actual output and baseline hashes; do not assume that prior result proves the final feature-024 outcome. No Decision Support diagnostics should remain. If backend localized messages change, run existing Persian catalog compilation/check procedure and retain actual output; do not claim compilation merely from a prior feature's log.

## Real browser scenarios

Proposed suite `apps/web/e2e/tests/decision-execution-records.spec.ts` uses existing authentication/setup utilities and API routes:

```bash
cd /home/hossein/Desktop/projects/building-management
pnpm exec playwright test --config apps/web/e2e/playwright.config.ts apps/web/e2e/tests/decision-execution-records.spec.ts --project chromium-desktop --trace on
pnpm exec playwright test --config apps/web/e2e/playwright.config.ts apps/web/e2e/tests/decision-execution-records.spec.ts apps/web/e2e/tests/decision-ahp.spec.ts apps/web/e2e/tests/decision-ism.spec.ts --project chromium-desktop --trace on
```

Validate [API](contracts/execution-api.md), [stored review](contracts/result-review.md) and [UI states](contracts/history-ui.md) in each language:

- Persist successful live-method runs, capture IDs, edit names/order/inputs, run again and re-read old detail. Verify stored payload and visible frozen named axes/results; compare full old payload equality separately from mutable actor display-name presentation.
- Inspect distinct SAW/TOPSIS disagreement results and tie fixtures; each keeps stored name/score/rank/order and TOPSIS distances. Selecting history performs zero mutations and leaves current result/draft untouched.
- Browse AHP sorted legacy rows/inconsistency and ISM cycles with existing presenters. Test completed DEMATEL presentation with explicitly labeled test-only persisted examples from feature 022; preserve stub display. These examples are not live DEMATEL engine evidence.
- Inspect partial/null/missing snapshots, missing normalized weights and unusable output without crashes or invented values; available provenance and raw inputs remain readable.
- Intercept successful save/POST bodies with empty, HTML, truncated, null, object, wrong ID/method, missing snapshot and invalid result. Unconfirmed saves send no POST. A real committed run with unconfirmed response produces one initial POST and no automatic repeat; history GET remains held while same-case controls are disabled. Recovery success exposes the captured committed ID/count and visible all-method page one; failure/malformed GET/ten-second timeout reports uncertainty.
- Reselect or navigate A→B→A while PATCH/POST/recovery is pending. Another case remains independent; old response cannot change its filter/page/result or release its token. Historical details stay accessible without overlapping same-case mutations.
- Delay detail, then select another row, filter, page or case; verify stale detail cannot become selected. Fail a new selection after prior success; show read failure rather than the prior analysis as the requested result.
- Real view-only, no-view, nonmember and foreign-project/case requests and UI; native keyboard history selection/tables, EN/FA labels/dates/direction and switched-language payload equality.

## SC-004: prepared 100-record history performance

Create one disposable fixed case with 100 records distributed over the four live methods and existing DEMATEL placeholders, plus appropriate completed-DEMATEL review fixtures in a separate case. Record actual method counts and keep the timed 100-record set unchanged during measurement. Equal-time ordering is separately covered by controlled backend fixtures; never mutate production timestamps.

For each locale measure at least 40 history-page selections and 40 detail selections with ten-row pages. Time from browser user selection event immediately before dispatch/state transition to the matching complete readable page/detail. Include request, render and visibility polling; exclude case preparation. Identify each selected page/run so a cached old view cannot end a measurement. Document which samples are cold versus cached; include forced-fresh selections sufficient to demonstrate network-backed review, not cached navigation alone.

At least 95% of samples in each locale/category must complete within 2000 ms. Include all failures/timeouts as failed trials, not excluded samples. Retain raw durations, page/run IDs, method distribution, sample counts, failures, median/p95, cache conditions, boundary and OS/CPU/memory/Node/Python/Django/PostgreSQL/Chromium/server-mode/worker metadata in feature-local `validation-performance.json` during implementation.

This is history-review latency, not feature 023's POST-to-layer calculation timing. Prior feature timings cannot substitute for it. Local normal conditions mean no artificial latency/throttling, one Playwright worker and documented local API/web processes. No production or all-network guarantee follows.

## Completion evidence

During implementation create feature-local validation/evidence artifacts retaining exact commands/exits, meaningful red → minimal fix → green, final changed-tree identity, backend/helper/type/migration/locale/browser categories, traces and SC-004 raw timing. Reconcile every FR, SC and acceptance scenario; distinguish regression/source review from actual new behavior proof. Preserve original 018–023 artifacts and reviewer checklist markers. Task counts and requirements-quality checklist passes alone do not establish application acceptance. No automatic commit, push, deployment or human sign-off is part of this workflow.

## Implemented lifecycle

The common parent lock, deterministic queryset order, unknown-safe history
boundary, named snapshot tables and shared four-panel recovery are implemented.
Use the commands above; feature-local [validation.md](validation.md) retains
actual focused/final output. New pure guards validate structure and frozen
membership; they contain no scientific derivation. Local historical fixture ORM
inserts in the browser helper verify compatibility/presentation only.

Mutation retries are disabled. After an unconfirmed POST, inspect the refreshed
all-method first page (or normal history if refresh failed) before manual retry.
A retry can append another run. There is no cross-request revision guarantee.
DEMATEL is still a placeholder engine. Existing O01/O02 policies remain open.
