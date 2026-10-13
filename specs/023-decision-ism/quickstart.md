# Quickstart: Validate Independent ISM

This guide specifies future implementation validation. New ISM tests/components do not exist at planning completion. Commands become evidence only when run against the final implemented tree; reference checks, source audits and task checkboxes do not establish application acceptance.

## Prerequisites

- Confirm intended worktree and preserve unrelated changes; planning Git branch is `develop`, feature alias `023-decision-ism`.
- Use existing API venv/pinned Django 4.2. Do not install full `requirements-dev.txt` or upgrade dependencies.
- PostgreSQL/Redis must be available at actual root `.env` addresses (normally PostgreSQL port 5433); no SQLite fallback or database reset for validation.
- Core ISM needs no worker/RabbitMQ/MinIO. Local overrides `AUDIT_LOG_ASYNC=false`, `CELERY_TASK_ALWAYS_EAGER=true` should already be configured; never print secrets.
- Use disposable authorized test cases plus view-only and other-project members; do not destroy production-like data.

For the native cloud environment, start services if needed:

```bash
sudo pg_ctlcluster 16 main start
sudo redis-server /etc/redis/redis.conf --daemonize yes
```

Run API/web separately from repository root, not Docker-dependent `pnpm dev`:

```bash
pnpm dev:api
```

```bash
pnpm dev:web
```

## TDD and backend proof

For each slice in [plan.md](plan.md), retain meaningful failing behavior assertions, apply minimal fixes, then focused green. Import failures prove scaffolding only; existing correct behavior needs regression, not fabricated red.

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
../.venv/bin/python -m pytest decision_support/tests/test_ism_service.py decision_support/tests/test_ism_api.py -q
```

Required coverage:

- Literal networks in [ism-result.md](contracts/ism-result.md), both single diagonal values, all-zero, ten-chain/ten-cycle and independent traversal closure expectations.
- Exact binary matrices, stable simultaneous active-set layers, maximal groups, zero false self/same-level groups, every criterion once, ≤n levels.
- Zero/eleven criteria, blank/duplicate names, wrong root/rows, missing/text/bool/nonfinite/overflow/fraction/negative/>1 cells: locatable issues and zero runs.
- Incomplete save/reload, explicit zero success, finite-invalid recovery, nonfinite persistence rejection, isolated matrix PATCH and genuine shared ranking-dimension rules. Preserve AHP's unrelated invalid ISM draft fixture.
- Distinct immutable records and unchanged earlier names/direct/derived/groups/actor/time/unrelated fields after edit/rerun.
- Locked authoritative selection, stale/deleted instances and controlled concurrent PostgreSQL save/run. Use transaction-capable tests, separate connections and synchronization, not arbitrary sleep timing as lock proof.
- Actual denied view-only mutations, foreign project/case/run reads, immutable run/filter-before-pagination and localized backend issues.

Then verify full domain and migration status in the same environment:

```bash
../.venv/bin/python -m pytest --reuse-db decision_support/tests -q
../.venv/bin/python manage.py makemigrations --check --dry-run
```

No migration expected. Whole-domain green includes AHP/SAW/TOPSIS and DEMATEL-stub compatibility, not browser/timing proof.

## Frontend helper/source/type proof

From repository root once the planned files exist:

```bash
node --experimental-strip-types --test apps/web/src/components/decision-support/*.test.ts apps/web/src/app/lib/api/decision-support.test.ts
pnpm typecheck
```

Also run existing Decision Support helper/source regressions after shared editor/coordinator changes. Check defaults, exact option mapping, independent cells, two-axis operation remap and structural result guards; never compute closure/layers/groups on the client. Record final typecheck output and attribute failures; prior unrelated failures do not establish the current outcome. Helper/source/key checks supplement actual UI proof.

## Real browser proof

Use the actual existing config/project:

```bash
pnpm exec playwright test --config apps/web/e2e/playwright.config.ts apps/web/e2e/tests/decision-ism.spec.ts --project chromium-desktop --trace on
```

Run existing `decision-ahp.spec.ts` and SAW/TOPSIS mixed-method smoke flows after adapters change. Retain exits, traces/report paths and locale outcomes. Exercise real API persistence; deterministic delay/error interception supplements actual backend checks.

1. **Independent analysis**: Create ISM-only A/B/C without ranking inputs. Keyboard-enter all nine cells (A→B/B→C one, others zero). Inspect exact closure/layers C/B/A and no groups. Reopen frozen direct/derived/layers/actor/date.
2. **Draft/correction**: Save/reopen unanswered A→C; execute, focus named pair, choose zero, rerun. Direct diagonal one remains one in snapshot; derived one. Reverse cells independent. Invalid persisted text/bool/finite number/shape stays visibly invalid until deliberate correction; nonfinite requests rejected before storage.
3. **Identity/focus**: Multi-character typing/caret stays stable. Rename/move/add/remove and assert surviving directed pairs, new diagonal zero/cross-pairs null, removed pairs gone. Existing AHP rename/reciprocity stays correct.
4. **Cycles/explanation**: A↔B with B→C, full three-cycle, same-layer isolated nodes, multiple distinct cycle groups. Match literal layers/groups; confirm top/lower explanation and no weights/ranking/removal control.
5. **History**: Capture input/result/actor/time; edit/reorder/rerun/switch locale; reopen first run and compare unchanged stored values. Legacy ISM stub is unavailable computation.
6. **Failure/pending**: Failed PATCH prevents POST. 403/404/429/non-JSON/network feedback preserves draft. Duplicate clicks acquire one local operation. Delay each AHP/SAW/TOPSIS save and attempt ISM/global save, then reverse; conflicts blocked. Switch case before response, no late new-case draft/result. Prior success remains history, never failed-run outcome.
7. **Access**: View-only mixed-method workspace has no create/edit/save/run controls but readable history. Actual bypass requests denied with zero runs; foreign case/nested run reveals no data.
8. **EN/FA**: Repeat entry/correction/remap/results/groups/history with keyboard. Assert logical row→column identity under RTL, translated states/errors/layer numbers/dates, and frozen data unchanged by language switch.

## SC-008 timing

Measure monotonic browser time from execution POST dispatch until completed layers for that returned run are visible. Exclude relationship-entry and preparatory PATCH time, matching the execution-request boundary. Include real network/API/render and count failed/time-out trials as failures.

Use ≥40 valid trials per documented locale/environment condition, distributed across single, sparse/chain, branching and dense cycles including n=10. Record OS/browser/server/database versions, network latency, worker count, warm/cold conditions, project data scale, locale, sample count, individual durations and failure count. Require ≥95% trials≤2000 ms (≥38/40), with median/p95 supporting statistics. Separate artificial slow-network/failure scenarios from normal trials. Service-only benchmarks do not prove visible latency or universal production performance.

## Evidence and handoff

During implementation keep feature-local validation notes with final-tree identity/status, meaningful red/green slices, exact commands/exits, backend/helper/type/migration/browser categories, traces and timing. Distinguish automated proof, source review and remaining human checks. Quality checklist completion alone is not acceptance.

Implementation evidence is recorded in [validation.md](validation.md), with raw visible-result timing in [validation-performance.json](validation-performance.json). Backend tests reseed the existing Decision Support permission catalog before and after transaction-capable tests, whose database flush removes migration-seeded role permissions. This affects test infrastructure only and does not reset the development database.

The browser suite includes 40 timing trials per locale. It collects actual OS/CPU/memory, Node, Python/Django, PostgreSQL server version and current Decision Support data counts through the existing local `django.sh` entrypoint. It records Chromium's own version and browser resource dispatch timestamps, includes all failures, and writes both locale results to the feature-local JSON. The documented measurement assumes a single-process `runserver --nothreading` local API and one Playwright worker; confirm or update that server configuration for another environment. Use `--grep SC-008` to run this measurement alone.
