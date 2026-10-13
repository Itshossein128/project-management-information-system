# Quickstart and Validation: DEMATEL

**Feature**: `022-decision-dematel` | **Date**: 2026-10-11

References: [inputs/API](contracts/dematel-inputs-api.md), [calculation/result](contracts/dematel-result.md), [UI](contracts/dematel-ui.md), [data model](data-model.md).

This is a future validation guide. The new service and test files are planned, not implemented by speckit-plan. No application acceptance suites have run for DEMATEL at this phase. Numerical research reproduced only the small reference formula independently.

## Prerequisites

From `/home/hossein/Desktop/projects/building-management`, use existing root `.env`, API virtual environment and JS dependencies. Verify PostgreSQL/Redis availability and the configured DATABASE_URL without exposing secrets. Native dev examples use PostgreSQL port 5433:

```bash
sudo pg_ctlcluster 16 main start
sudo redis-server /etc/redis/redis.conf --daemonize yes
```

Do not reset an existing database or reinstall full API dev requirements. Django remains 4.2.11. NumPy is already a runtime dependency. For a genuinely fresh dev database only, use `pnpm db:migrate` and `pnpm db:seed`. If JS dependencies are missing, use `pnpm install --registry https://registry.npmjs.org/`.

Docker-less dev requires `AUDIT_LOG_ASYNC=false` and `CELERY_TASK_ALWAYS_EAGER=true`. DEMATEL needs no MinIO/RabbitMQ/worker. Start API and web separately rather than `pnpm dev`:

```bash
pnpm dev:api
```

```bash
pnpm dev:web
```

If an already running API uses `--noreload`, restart only the owned server after code/catalog changes; do not test stale code. Leave rate limiting enabled.

## TDD and backend verification

During implementation, add each regression and capture its real failing exit before the minimal fix; rerun focused tests green. New proposed files become runnable after tasks create them:

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
../.venv/bin/python -m pytest decision_support/tests/test_dematel_service.py decision_support/tests/test_dematel_api.py -q
```

After focused green, run existing regression and migration discovery:

```bash
../.venv/bin/python -m pytest decision_support/tests -q
../.venv/bin/python manage.py makemigrations --check --dry-run
```

| Scenario | Required evidence/outcome |
| --- | --- |
| Three-criterion directed chain | T/D/R/prominence/relation exactly match result contract within SC-002 tolerance; one 201 run |
| Decimal, tiny uniform scale, isolated criterion, n=10 | Accepted finite expected indicators, actual dimensions only |
| n=0/11; names; ragged/non-list inputs | Root/field/cell coded validation; zero successful runs |
| Blank/string/bool/nonfinite/range/diagonal | Correct paths/codes; no coercion to zero or successful record |
| All-zero n=1/n=3; singular loop | Matrix-level actionable error; no fabricated result |
| Accepted/rejected near-condition boundary | Independent high-precision expected accepted result; coded rejection beyond policy |
| Draft save and DEMATEL-only patch | Blanks persist; no nonfinite JSON; unrelated ranking drafts untouched |
| Stale instance/deselected/deleted case/concurrent edit | Authoritative locked input; coherent computation/snapshot; no invalid run |
| Edit and rerun | Distinct IDs; previous snapshot/result/actor/time unchanged |
| View-only and foreign project/case/run | Denied mutations/execution or scoped404; no disclosure |
| Mixed history and old DEMATEL stub | Correct filtering/pagination; immutable old payload; no fake numerical output |

Supply valid DEMATEL input or use ISM in the old AHP mixed-history fixture; retain its count/scoping assertions. Nonfinite inputs may need direct service tests when a JSON parser rejects them before validation. Test immutability by comparing persisted records before/after edits, not by depending on incidental JSON numeric formatting.

## Frontend checks

After planned helpers exist:

```bash
cd /home/hossein/Desktop/projects/building-management
node --experimental-strip-types --test \
  apps/web/src/components/decision-support/dematel-input-rules.test.ts \
  apps/web/src/components/decision-support/SquareMatrixEditor.test.ts \
  apps/web/src/components/decision-support/no-client-dematel-math.test.ts \
  apps/web/src/components/decision-support/i18n.keys.test.ts
pnpm typecheck
```

Record actual exit/output and distinguish unrelated existing type errors from new DEMATEL errors. Helper/source/key checks do not prove rendered UX or numerical correctness. Keep existing AHP helper/key/math-boundary regressions green.

## Browser acceptance

After the proposed suite exists, with actual API/web and PostgreSQL/Redis available:

```bash
pnpm exec playwright test \
  --config apps/web/e2e/playwright.config.ts \
  apps/web/e2e/tests/decision-dematel.spec.ts \
  --project chromium-desktop --trace on
```

Also run the existing `apps/web/e2e/tests/decision-ahp.spec.ts` browser suite affected by shared editor/route changes. No dedicated SAW/TOPSIS browser suites currently exist; add mixed-method ranking smoke scenarios where the shared adapters require coverage. Use isolated authorized test data and real persistence; do not mock successful calculation as numerical proof.

In EN and FA, verify independent chain entry/execution/result; directed opposite cells; fixed diagonal; explicit zero vs blank; decimals; keyboard focus/caret; rename/reorder/add/remove pair preservation; incomplete save/reload; named cell-error focus; all-zero/singular failure and retry; 403/404/429/non-JSON/network feedback; failed save prevents run; previous/current result distinction; delayed global save/run, an already-pending other-method save before DEMATEL/global save, and case-switch isolation; view-only mixed-method controls and real denied mutations; frozen history actor/time/labels and language switching, including a browser locale different from active app language. Preserve traces/screenshots and actual outcomes.

## Performance outcome SC-006

Measure request initiation to visible successful result under recorded normal operating conditions. Use at least 20 valid executions including n=10, with warm/cold state, locale, runtime, transport and machine context recorded. At least 95% must finish within two seconds. Exclude entry time and keep rate limiting enabled. A unit calculation benchmark does not establish user-visible timing. Space requests according to real application throttling and record errors separately.

## Evidence and handoff

Save red/green logs and final exits, numerical fixture provenance, PostgreSQL API/concurrency outcomes, migration result, typecheck scope, EN/FA traces and performance samples in the eventual validation record. Specification quality is 16/16; implementation acceptance remains unverified. Next step is speckit-tasks, followed by TDD implementation and convergence.
