# Validation Guide: Undo Project Status

**Status**: Implemented locally on 2026-10-17. Commands below target the implemented API/UI and disposable validation database. Actual outcomes, TDD history and proof limits are recorded in [verification.md](verification.md). [Contracts](contracts/status-undo-api.md), [UI](contracts/status-undo-ui.md), [data model](data-model.md) are normative for expected behavior.

## Prerequisites and proof categories

Use pinned Django 4.2.11 in the existing venv, real PostgreSQL and Redis. Do not install requirements-dev wholesale or upgrade Django. Use actual fresh lifecycle actions for event provenance; do not construct unknown-origin suspended/completed fixtures or write lifecycle metadata through an API. Keep all original dirty work and prior archive feature evidence.

Separate evidence: observed TDD RED/GREEN; normal pytest/API; independent-transaction PostgreSQL races; schema apply/reverse; intercepted browser UX; actual authenticated browser/API journeys; optional physical external-storage checks. A passing category is not proof of all the others. No production mutation, remote CI or deployment is authorized by this guide.

## Isolated database setup

The existing scoped runner can be reused unchanged with a new disposable database name. It replaces only the child database URL/name, sets synchronous general audit/eager tasks and runs in API core. It creates a database only on explicit --create-db and never drops a shared database or edits .env. Do not print tokens/credentials.

```bash
cd /home/hossein/Desktop/projects/building-management
set -a
source .env
set +a
export RESTORE_VALIDATION_DATABASE=velora_restore_undo_026
pg_isready -h 127.0.0.1 -p 5433
redis-cli ping
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py --create-db
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" manage.py migrate
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" "$PWD/e2e/helpers/seed-project-status-undo.py"
```

Current projects leaf is `0017_project_status_undo`, after unchanged `0016_bind_archive_remediation` (audit dependency `0003_initial`). Unknown-origin old development data requires explicit fresh preparation; do not infer destinations or add automatic cleanup. The seed enforces this disposable prefix, provides global group-admins, groupless superuser, ordinary editor, approval-only member/viewer/outsider and other approver, and saves private JWT fixtures to ignored `test-results/status-undo-actors.json` with mode 0600. Regenerate expired fixtures rather than publishing credentials. Fixtures create/submit/approve and then suspend/complete through real lifecycle actions.

## TDD and backend gates

Write a meaningful missing-behavior assertion before production changes and record actual RED → minimal fix → GREEN. Existing correct permission/gate/preservation behavior can stay GREEN; never break it to manufacture RED. No assertion that only mirrors implementation is required.

Complete scoped feature modules and affected regressions:

```bash
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" -m pytest \
  projects/tests/test_project_status_undo.py \
  projects/tests/test_project_status_undo_permissions.py \
  projects/tests/test_project_status_undo_remediation.py \
  projects/tests/test_project_status_undo_retries.py \
  projects/tests/test_project_status_undo_history.py \
  projects/tests/test_project_status_undo_localization.py \
  projects/tests/test_project_status_undo_preservation.py \
  projects/tests/test_project_status_undo_concurrency.py \
  projects/tests/test_project_status_undo_migrations.py \
  projects/tests/test_project_registration_lifecycle.py \
  projects/tests/test_project_registration_change_request.py \
  projects/tests/test_project_registration_gates.py \
  projects/tests/test_project_activation_feedback.py \
  projects/tests/test_project_archive_restore.py \
  projects/tests/test_project_archive_restore_permissions.py \
  projects/tests/test_project_archive_restore_remediation.py \
  projects/tests/test_project_archive_restore_retries.py \
  projects/tests/test_project_archive_restore_history.py \
  projects/tests/test_project_archive_restore_localization.py \
  projects/tests/test_project_archive_restore_preservation.py \
  projects/tests/test_project_archive_restore_concurrency.py \
  projects/tests/test_project_archive_restore_migrations.py \
  audit/tests.py permissions/tests/test_sod.py --create-db -q
```

Run a focused subset at each TDD slice before this broader gate. --create-db affects only pytest's dedicated test database; transactional flush can otherwise remove migration-seeded roles under --reuse-db. Never run two pytest processes on the same test database. Existing direct-state archive/registration fixtures must be adapted for the new strict provenance constraints while retaining their original behavior assertions. Their older 0014/0016 migration boundaries remain meaningful; the new migration suite separately tests 0016 ↔ new leaf. Reasonless resume expectations must adopt the intentional confirmed request shape; keep explicit tests proving empty-body/service bypass is rejected.

Important backend assertions:

- Original suspend/complete status, new event reference and semantic audit commit together; injected original audit failure rolls back all. Audit is synchronous and exactly once under either global async setting. New original events capture true source, performer/time and immutable association to suspension.
- Three reverse routes: suspended→active; completed-from-active→active; completed-from-suspended→suspended followed by separately confirmed resume. All seven missing-gate combinations, zero amount, revoked authority and readiness removed after preview; no new activation predicate.
- Signature/body validation, actor/project/operation/source/version binding, reason, old request after subsequent status/new occurrence, changed payload, no arbitrary time cutoff, known rollback versus uncertain outcome, and source audit belonging to another project/type.
- Complete→archive→restore-completed retains completion source; suspended→complete→undo-suspended retains suspension source. Old undo cannot affect a fresh event; exact replay returns original receipt with current state.
- Project-first locks: duplicate/same/different request/user, forward suspend/complete, archive/restore, PATCH name/manager/readiness, normal or bound CR approval, delete, and user/grant changes. Use true independent connections/transactions, bounded waits and direct observed PostgreSQL lock waits where appropriate; cover both competing-writer orders. Close every worker's connections explicitly.
- Completed-bound repair rejects unrelated/already-filled fields, stale event/status, revoked global authority and wrong binding. CR source binding is exclusive/read-only. Preserve ordinary suspended and preexisting unbound CR policy; prove self-approve prevention and permitted stale cancel. Compare full Project/CR/receipt/audit snapshots around rejection.
- Failure of required undo audit/receipt leaves zero partial success; forbid finance/approval/baseline calls; compare populated business rows, prior budget stamps, document restrictions/revisions and original audit snapshots. History safe projection/pagination with >100 tied-time results, stable order and bounded queries. Account deletion/project rename preserves attribution; Project hard-delete still works with protected audit references.
- MigrationExecutor applies/reverses only new schema around 0016, preserves valid earlier business data/archive receipts and rejects invalid new effective-state/binding/receipt combinations. Old data without provenance is not given an inferred source.

Schema/type checks (via the same isolated environment):

```bash
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" manage.py makemigrations --check --dry-run
pnpm typecheck
```

Fresh final typecheck exits 2 with the same three baseline diagnostics: `daily-report-view.tsx:198`, `ManualProgressDrawer.tsx:171`, `KickoffCharterPanel.tsx:78`. No new diagnostic was introduced; global typecheck is not green.

## Browser gates

Run PostgreSQL concurrency/migration gates before starting API/browser integration; do not overlap their connection load or transactional flush with browser fixtures. Start API in a separate terminal using the isolated environment above:

```bash
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" manage.py runserver 8000 --noreload --nothreading
```

Start frontend separately (do not pnpm dev if Docker-less):

```bash
pnpm dev:web --host 127.0.0.1 --port 5173
```

New configs match dedicated tests, fa/en × desktop/mobile (Desktop Chrome/Pixel 5), with separate ignored reports/JSON/traces. Use installed Chrome if the matching Playwright browser is unavailable; record browser version rather than changing packages:

```bash
STATUS_UNDO_BROWSER_CHANNEL=chrome pnpm exec playwright test -c e2e/playwright.status-undo.config.ts
STATUS_UNDO_BROWSER_CHANNEL=chrome pnpm exec playwright test -c e2e/playwright.status-undo.integration.config.ts
RESTORE_BROWSER_CHANNEL=chrome pnpm exec playwright test -c e2e/playwright.restore.config.ts
RESTORE_BROWSER_CHANNEL=chrome pnpm exec playwright test -c e2e/playwright.restore.integration.config.ts
```

Both new configs support `STATUS_UNDO_BROWSER_CHANNEL`; omit it to use the installed Playwright Chromium. The UI config uses intercepted responses and proves only UX; integration config uses actual API/PostgreSQL and all real actors. Existing archive suites must remain green; their mocks/types/endpoints are not replaced. Capture real command exit status; redirecting output is fine if `$?` is saved before tail and returned. Reports/traces are private local evidence because they can contain disposable credentials.

Real journeys create ready projects through existing create→submit→approve, then valid suspend/complete. For partial completed-active setup, remove scope/amount through an actually approved existing CR before completion, and manager through authorized PATCH, rather than spoofing metadata. Validate both manager and CR links, saving reason before leaving; another approver acts through existing approval controls. Completion undo to suspended must work even with missing activation fields and must not implicitly resume.

After-commit response-loss test forwards the real POST and verifies its committed success before dropping only response delivery; separately abort before forwarding and safely retry the exact body. Reload and auth refresh must retain body/operation/event. Test late responses across cached project, operation and account changes; preserve any existing shell protections. Warm actual singleton QueryClient summary/dashboard caches and count actual refetch after applied/replay/completed lookup, versus unchanged caches after cancel/not_recorded. Ensure preview initial/cached failure retry never posts or enables stale confirmation.

## Acceptance coverage — no checklist markers are execution evidence

- **US1/1–7**: three destinations, blank reason, cancel before dispatch, repeated completion with new source, completion→suspended then separate resume; API and real browser in both locales/devices. FR-001/002/004, SC-001/002.
- **US2/1–7**: actual project editor can resume, group-less/nonmember system admin can undo completion, editor/approver/manager/outsider cannot undo completion, all missing combinations, executable repair with draft retention/SoD, suspended target bypasses active gates, revoked authority/readiness rechecked. FR-003/005/006, SC-003/004.
- **US3/1–7**: atomic rollback/audit failure, distinct preview errors, actual before/after-commit loss and owned lookup, independent-connection contention, stale/tampered context, old event/replay after newer event, inapplicable/deleted state and late view/account callbacks. FR-008–014, SC-004/007.
- **US4/1–4**: populated documents/financial/approval/history snapshots, immutable original and undo attribution/time/from/to, actual detail/list/portfolio/history refresh and safe recovery, fa/en desktop/mobile keyboard/empty/error/pagination/draft cleanup. FR-007/008/014/015, SC-005–007.

These groups enumerate all 25 acceptance scenarios and all 15 FR/seven SC. Individual executed evidence mappings, exact run counts and limitations are in verification.md. Measure SC-002 as three business steps for ready users; no infrastructure latency SLA or arbitrary throughput target is invented. History boundedness/query shape is the technical performance gate.

## Storage and environment limits

When MinIO/object store is unavailable, report DB document/file URL/revision/restriction preservation separately from physical file download/hash retrieval. Do not assert external storage availability from fixture metadata. Existing RabbitMQ/worker are unnecessary with the isolated eager/synchronous overrides; required semantic audits still use direct synchronous persistence regardless of general settings. No local test proves remote CI/deployment/production behavior. Do not reset original development data or change credentials/config to make validation convenient.

## Local evidence and repeatability

Ignored private logs, scripts and preserved reports are under `test-results/status-undo-evidence/` (directory mode 0700). Browser actor fixtures are mode 0600. Save the real exit before displaying log tails:

```bash
STATUS_UNDO_BROWSER_CHANNEL=chrome pnpm exec playwright test -c e2e/playwright.status-undo.config.ts > test-results/status-undo-evidence/repeat-ui.log 2>&1
result=$?
tail -30 test-results/status-undo-evidence/repeat-ui.log
exit "$result"
```

Run suites sequentially and copy their JSON/report/output directories before rerunning the same config. The existing activation config has no channel override; this machine uses a private config wrapper that imports `e2e/playwright.activation.config.ts`, sets its absolute testDir and `use.channel="chrome"`. No change to the original activation config is needed. With Playwright's matching bundled Chromium installed, run the original config directly. Seed prior archive actors before the real archive regression suite as well:

```bash
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" "$PWD/e2e/helpers/seed-project-archive-restore.py"
```

Schema reversal `0017 → 0016` deliberately removes new undo receipts/references/completion binding, preserves original audits, old archive receipts and business records, and does not change business status. Reapplying 0017 does not fabricate dropped history or unknown origins. Dedicated tests cover valid old active/draft/archived data plus real applied undos and approved bound repair. Unknown effective suspended/completed development rows must be prepared explicitly outside this migration; no compatibility/backfill is claimed.

## Convergence follow-up T088–T092

Run these checks against the final working tree, with the isolated environment above. Private fresh evidence belongs under `test-results/status-undo-convergence/`; retain the earlier evidence rather than overwriting its claims. The actual commit-ack test calls PostgreSQL's commit and then raises an acknowledgment error; keep API/browser fixtures stopped during this transactional gate. The final affected backend gate is:

```bash
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" -m pytest \
  projects/tests/test_project_status_undo.py \
  projects/tests/test_project_status_undo_permissions.py \
  projects/tests/test_project_status_undo_remediation.py \
  projects/tests/test_project_status_undo_retries.py \
  projects/tests/test_project_status_undo_history.py \
  projects/tests/test_project_status_undo_localization.py \
  projects/tests/test_project_status_undo_preservation.py \
  projects/tests/test_project_registration_lifecycle.py \
  projects/tests/test_project_registration_change_request.py \
  projects/tests/test_project_registration_gates.py \
  projects/tests/test_project_activation_feedback.py \
  projects/tests/test_project_archive_restore.py \
  projects/tests/test_project_archive_restore_permissions.py \
  projects/tests/test_project_archive_restore_remediation.py \
  projects/tests/test_project_archive_restore_retries.py \
  projects/tests/test_project_archive_restore_history.py \
  projects/tests/test_project_archive_restore_localization.py \
  projects/tests/test_project_archive_restore_preservation.py \
  audit/tests.py permissions/tests/test_sod.py --create-db -x -q
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" manage.py makemigrations --check --dry-run
```

`--create-db` recreates only the dedicated pytest database and restores migration-seeded roles after transactional fixture flushes. It does not reset the original database or the separate browser fixture database. This affected gate excludes unchanged concurrency/migration modules; their previous full-gate result remains historical, and a future change to their services/models/migrations requires rerunning them. Migration drift alone does not replace their behavioral checks.

After backend completion, reseed both sets of browser actors, start the isolated API and a stable frontend, and run all five browser configs above sequentially, including activation. Do not change frontend source between starting the server and running the account/operation isolation cases: those cases intentionally use the mounted singleton QueryClient, and Vite HMR module versions can invalidate the test's unversioned dynamic-import fixture. If frontend source changes, restart the owned frontend before the final gate.

New coverage includes same-document account replacement inside cache freshness (cached and late history), fa/en completion-bound CR errors, actual database commit-ack loss on all three paths, sent known rollback/competing/gate outcomes with frozen retry bodies and narrow invalidation, fa/en auth/operation ownership, anonymous HTTP denial, and actual JWT membership with exactly `view_project`. The latter creates real history, then makes the status applicable again before proving readable history, absent controls and direct preview/write/result denial. No new permissions, fake mutation success or shell bypass are used.

Keep the global typecheck's three existing diagnostics and storage/remote-CI/deployment boundaries above explicit. Record each command's exit and JSON statistics; earlier focused GREEN runs are not substitutes for the combined final runs.

In actual response-loss journeys, await the route fixture's `deliveryLost` signal after its verified real commit/abort before asserting the unknown-result UI. The normal UI assertion timeout measures rendering after the fault; it must not also impose an unstated5s database-commit SLA. Keep the original request body, actual200 assertion and result/receipt checks intact, and retain a failed run separately before repeating a corrected gate.

The T088–T092 final working-tree run recorded299 affected backend passes and five complete browser gates:156 status-undo UI,126 archive UI,94 activation UI,68 actual status-undo and46 actual archive. Browser total490, including114 actual API journeys, with no skips/flaky/unexpected results. See verification.md for the preserved earlier failed fixture run, its synchronization correction, exact source manifests and limitations. These are local results; global typecheck still exits2 on the three baseline errors. Stop only test servers you started and retain native services/original data.
