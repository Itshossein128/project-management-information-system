# Quickstart & Validation: AHP Criteria Weighting

**Feature**: `021-decision-ahp` | **Date**: 2026-10-11

Acceptance contracts: [inputs/API](contracts/ahp-pairwise-matrix.md), [result](contracts/ahp-run-result.md), [UI](contracts/ahp-ui.md), [data model](data-model.md). This is a validation/run guide, not implementation code.

## Prerequisites

Use existing `apps/api/.venv`, Django 4.2.11 compatibility, root `.env`, JS dependencies and configured PostgreSQL/Redis. Never install `requirements-dev.txt` as-is. Verify `DATABASE_URL`; documented native development PostgreSQL port is 5433. Start existing native services if needed:

```bash
sudo pg_ctlcluster 16 main start
sudo redis-server /etc/redis/redis.conf --daemonize yes
```

Missing JS deps: `pnpm install --registry https://registry.npmjs.org/`. Use isolated dev/test data. For a fresh dev DB only, `pnpm db:migrate` and `pnpm db:seed`; never reset an existing DB for validation. Docker-less development uses `AUDIT_LOG_ASYNC=false`, `CELERY_TASK_ALWAYS_EAGER=true`. AHP needs no RabbitMQ/MinIO. Existing seed credentials: admin phone `+10000000001`, password `devpass123`; verify current seeding if unavailable.

## Existing numerical baseline

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
../.venv/bin/python -m pytest decision_support/tests/test_ahp_service.py -q
```

Planning baseline: **8 passed**, 2026-10-11. Basic formulas/guards only; no DB records, strict-type fixes or output-order proof.

## Existing frontend helper baseline

```bash
cd /home/hossein/Desktop/projects/building-management
node --experimental-strip-types --test \
  apps/web/src/components/decision-support/SquareMatrixEditor.test.ts \
  apps/web/src/components/decision-support/CriteriaWeightTable.test.ts \
  apps/web/src/components/decision-support/no-client-ahp-math.test.ts \
  apps/web/src/components/decision-support/i18n.keys.test.ts
```

Planning baseline: **12 passed**, 2026-10-11. Helper/key/limited source checks, not rendered UI/state proof. At that baseline, matrix tests still expected all-ones defaults. Current tests enforce blank unjudged pairs and owned diagonal values.

## Backend acceptance/regression

Run the implemented regressions with PostgreSQL/Redis:

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
../.venv/bin/python -m pytest decision_support/tests -q
```

| Scenario | Required outcome |
|---|---|
| AHP only, no ranking inputs | 201; one run; weights 0.6/0.3/0.1, CI/CR≈0 |
| n=1, n=2 ratio 3, n=10 | Weight 1; weights 0.75/0.25; ten finite normalized rows |
| n=0/11, ragged/wrong rows | Coded dimension error; no run |
| Null/blank/string/bool/zero/negative/non-finite | Contract codes/paths; no run |
| Diagonal 1.00005, reciprocal boundary | Exact diagonal rejected; symmetric product residual rule |
| Lower/Higher with ratio 0.25 | Input order, weights 0.2/0.8, ranks 2/1 |
| Equal weights | Stable unique ordinal ranks, sum within 1e-6 |
| Circular inconsistency | 201, CR≈2.75862, false consistency, persisted record |
| Out-of-scale/custom/extreme values | Scale alone does not reject; no non-finite JSON/unhandled overflow |
| Ranking fields around run and matrix-only patch | Raw weights/types/alternatives/performance/other inputs identical |
| Two runs separated by case edit | New ID; entire previous snapshot/result/actor/time unchanged |
| Missing membership/read-only/no permission; foreign IDs | 403 or scoped 404; no disclosure/unauthorized run |
| Method history, interleaved/multiple pages | Filter before pagination, correct count/order, scoped access |
| Run PUT/PATCH/DELETE | 400 `run_immutable`, persisted data unchanged |

Cover non-finite values directly in validator/service tests if JSON parser rejects them first. Compare numerical fixtures at 1e-6 or tighter, rather than existing broad 1e-2 checks. Verify no input-list mutation and no run on invalid execution.

## Frontend gates

Extend helper tests for null defaults, pair clearing, retained/reordered/new criteria, reciprocal precision and missing-source failures, then run the helper command and:

```bash
cd /home/hossein/Desktop/projects/building-management
pnpm typecheck
```

Record unrelated errors by file/exit status; do not assume historic failures remain current.

## Browser acceptance

The implemented suite is `apps/web/e2e/tests/decision-ahp.spec.ts`:

```bash
cd /home/hossein/Desktop/projects/building-management
pnpm exec playwright test \
  --config apps/web/e2e/playwright.config.ts \
  apps/web/e2e/tests/decision-ahp.spec.ts \
  --project chromium-desktop --trace on
```

For repeated local runs, start the API and web in separate terminals before the browser command:

```bash
# API terminal
bash apps/api/django.sh runserver 127.0.0.1:8000 --noreload --nothreading
```

```bash
# Web terminal
pnpm --filter web dev --host 127.0.0.1 --port 5173
```

This prevents the local threaded runserver from retaining enough PostgreSQL connections to exhaust its development limit. App-level config starts/reuses API/web; global setup migrates/seeds the configured dev database, so inspect its target first. Root `pnpm e2e` config does not supply server startup. For manual exploration, start `pnpm dev:api` and `pnpm dev:web` separately, avoiding Docker-dependent `pnpm dev` when Docker is unavailable. Install Chromium only if missing.

Run in both English/Persian with RTL and keyboard-only operation:

1. New AHP-only case: fresh n=1 runs from owned `[[1]]`; n≥2 visibly blank pairs block execution until entered, no alternatives required.
2. Fraction presets including `1/3`, full-precision opposite value, clearing both sides, custom out-of-scale advice, reload/reopen persistence.
3. Consistent 2/3/6 fixture: weights/ranks/CR and success status. Circular preferences: successful audit run and announced localized warning.
4. Criteria add/remove/reorder/rename: named pairs retained, new pairs blank, no implicit equality. Ten-criterion horizontal keyboard navigation.
5. Mixed-method independent history across pages, older frozen matrix/result, unchanged editable draft/ranking values.
6. Subsequent run preserves old record. Switch cases after a result and during delayed fetch/run responses: no old-case result/errors in new case.
7. Cell names/header scopes, error association/navigation, pending/history/scale copy, warning announcements, locale switching and absence of untranslated keys.

SC-001 additionally requires a timed four-criterion user exercise from an open configured case through judgment entry to visible result, under 30 seconds. Scripted typing or engine latency does not prove this user metric.

## Verification boundary

Record final-tree command exits/counts, API/RBAC/history assertions, typecheck, both-language browser traces and user timing. No migration expected; verify model changes remain absent. Planning ran the two baseline suites and read-only probes. Implementation evidence is in [validation.md](validation.md): API/DB, authorization, numerical, helper/source/locale and real browser checks are exercised. No production or human timing acceptance is inferred from those checks.

## Implementation result (2026-10-11)

The corrected engine uses log-domain geometric means and stores result rows in input order with independent ordinal ranks. Matrix drafts own blank pairs/diagonal values; presets/custom entry, reciprocal precision, cell error focus and separate frozen history are implemented. Matrix-only saves preserve raw ranking drafts. Existing model schema and permission codes are preserved.

Final backend: 115 passed, exit 0. Frontend Node helper/source/locale checks: 40 passed, exit 0. Typecheck: exit 2, five errors outside decision support in unchanged daily-report-view, project-list (two errors), ManualProgressDrawer and KickoffCharterPanel. Final real browser suite: 26 passed (13 scenarios per language), exit 0. See validation.md for retained logs/screenshots/traces and requirement coverage.

T041 remains pending until an observed four-criterion human exercise demonstrates SC-001. O05 advisory policy and O06 reciprocal entry remain the documented interim decisions. No commit/push/deployment is included.


## Convergence implementation result (2026-10-11)

T043–T048 correct missing Persian structural/method errors, general request-failure feedback, history date locale, criterion typing focus/caret, representable numerical overflow and root dimension diagnostics. Each fix has red/green regression evidence in [validation.md](validation.md).

Final gates after these fixes: 145 decision_support pytest tests, 50 Node checks and 32 browser scenarios passed (16 per language), all exit 0. Migration dry-run detects no change. pnpm typecheck exits 2 on the same five unrelated errors outside AHP, with no decision-support errors. Logs and 32 browser traces are retained at /tmp/ahp-convergence-20261011-124lk_fl.

Human SC-001 acceptance remains unavailable: the user could not perform the observed four-criterion exercise. T041/T049 remain unchecked; 47/49 tasks complete. The spec/plan/checklist/model are preserved. No commit/push or deployment.
