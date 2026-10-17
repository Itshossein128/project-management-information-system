# Validation: Restore Project from Archive

Implemented validation guide. Results, failures, recovery and boundaries are recorded in [verification.md](verification.md); checked tasks are not deployment or CI evidence. Parent registration documents and this feature's requirements checklist are preserved.

## Runtime and isolated data

Use PostgreSQL/Redis with Django 4.2.11 and the existing venv. Do not install requirements-dev wholesale, reset a shared database or use an unknown-origin legacy fixture. New migrations are `0015_project_archive_restore` and `0016_bind_archive_remediation`, following `0014_reportexportversion`. Old unknown-origin development rows have no compatibility/backfill requirement; prepare known-origin fixtures instead. Reversal removes feature receipts/metadata and is not a business undo.

From the repository root, load your configured credentials without printing them:

```bash
cd /home/hossein/Desktop/projects/building-management
set -a
source .env
set +a
export RESTORE_VALIDATION_DATABASE=velora_restore_validation
pg_isready -h 127.0.0.1 -p 5433
redis-cli ping
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py --create-db
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" manage.py migrate
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" "$PWD/e2e/helpers/seed-project-archive-restore.py"
```

The runner replaces only the child process database URL's name, enforces a `velora_restore_*` name, sets synchronous general audit/eager tasks and changes cwd to the API core. It never changes `.env` or drops a database. The browser seed writes private JWT fixtures to ignored `test-results/archive-restore-actors.json` with mode 0600, only on a disposable database. Refresh those fixtures when tokens expire; never publish them or print Authorization headers. The implementation session used `velora_restore_01a14457` and its separate pytest database.

The original wrapper reloads `.env`. Its read-only schema check is safe against that configured database; do not use it for an isolated migration unless `.env` deliberately selects that database:

```bash
apps/api/django.sh makemigrations --check --dry-run
pnpm typecheck
```

Observed schema check: no changes. Global typecheck retains three baseline errors outside this feature; see verification for exact locations.

## Backend, migrations and real contention

Run through the isolated runner. This combined command names the feature and existing regressions actually exercised:

```bash
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" -m pytest \
  projects/tests/test_project_archive_restore.py \
  projects/tests/test_project_archive_restore_permissions.py \
  projects/tests/test_project_archive_restore_remediation.py \
  projects/tests/test_project_archive_restore_retries.py \
  projects/tests/test_project_archive_restore_preservation.py \
  projects/tests/test_project_archive_restore_history.py \
  projects/tests/test_project_archive_restore_localization.py \
  projects/tests/test_project_archive_restore_concurrency.py \
  projects/tests/test_project_archive_restore_migrations.py \
  projects/tests/test_project_registration_lifecycle.py \
  projects/tests/test_project_registration_change_request.py \
  projects/tests/test_project_registration_gates.py \
  projects/tests/test_project_activation_feedback.py \
  audit/tests.py permissions/tests/test_sod.py --create-db -q
```

Use `--create-db` for a complete fixture-based session: transactional flushes can remove migration-seeded roles when subsequently reusing a database. It affects only pytest's dedicated test database. Do not run two pytest processes against the same test database.

Targeted follow-up commands used `--reuse-db` for the concurrency/migration pair and the new `-k reports_real` cases. Worker `finally` blocks explicitly close healthy connections; arrival barriers and independently observed PostgreSQL `pg_stat_activity.wait_event_type = Lock` distinguish actual row-lock contention from sequential HTTP calls. All competing writers re-read the same Project root before validation/write. Both writer orders, same/different admins/request IDs, name/manager PATCH, protected CR, lifecycle and deletion are exercised.

Preservation tests populate real production models, compare full persisted records and restricted-document links, forbid money/approval/event/baseline operations during restore, and verify one required audit/receipt after exact replay. Independent audit/receipt insert failures under both async settings prove rollback; no OperationalError is assumed to mean rollback. MigrationExecutor reverses to 0014 and reapplies 0015/0016 while preserving valid business rows and original audit.

## Browser categories

Run these **after** the PostgreSQL concurrency/migration run, avoiding combined development-server/test connection pressure. Start API and frontend in separate terminals using the same isolated environment:

```bash
apps/api/.venv/bin/python e2e/helpers/run-project-archive-restore.py "$PWD/apps/api/.venv/bin/python" manage.py runserver 8000 --noreload --nothreading
```

```bash
pnpm dev:web --host 127.0.0.1 --port 5173
```

Then run from the root (install the matching Chromium runtime with `pnpm exec playwright install chromium` if absent):

```bash
pnpm exec playwright test -c e2e/playwright.restore.config.ts
pnpm exec playwright test -c e2e/playwright.restore.integration.config.ts
```

- `restore.config.ts`: frontend-only intercepted API, desktop/mobile fa/en. Proves dialog/cancel/reason/gaps, independently computed capabilities, history pagination/empty state, fixed request body under auth refresh, logout/account isolation, uncertain and known-result recovery, stale confirmation and localized messages. It does not prove database/authorization behavior.
- `restore.integration.config.ts`: actual authenticated API/PostgreSQL/Redis and frontend. Projects are created/submitted/approved/archived through existing APIs. Tests cover all targets/locales/devices, nonmember administration, real approved remediation, document/contract equality and visible durable history. Response-loss interception forwards and verifies a real POST before aborting only delivery; a separate test aborts before forwarding. No successful restore response is fabricated. Exact retry/result checks compare actual receipts, and a new archive captures the latest origin.
- The bounded performance case collects six preview/restore/history samples per browser project, attaches raw timings and prints p95; it has no brittle latency assertion. The 2-second target is a local planning comparison, not a production SLA.

If the Playwright browser cache is absent but Google Chrome is installed, the configs also support `RESTORE_BROWSER_CHANNEL=chrome` before either command. This selects the installed Chrome executable for both desktop and mobile emulation; record its actual version with the result. It does not change application behavior or bypass assertions.

Reports: `playwright-report/project-archive-restore-{ui,integration}/`; JSON and screenshots/traces: `test-results/project-archive-restore-{ui,integration}*`. Passing history cases save screenshots, failing cases retain traces. Request traces may contain disposable credentials and are private local evidence. Shell test commands return the real process code; when redirecting a log, capture `$?` before displaying `tail` and return that code.

## Acceptance boundaries

All 25 scenarios, 14 functional requirements and seven success criteria have individual evidence mappings in verification. Test fixtures always archive from active/suspended/completed; there is no guessed destination, draft/pending/deleted recovery, new global role or activation predicate. Zero contract amount remains valid; completion uses existing approved-field CR and SoD, with no budget restamp.

An external object store was unavailable. Database file URLs/name/revision/access links are preserved; physical attachment bytes, download and object hash retrieval remain unverified. No local result proves remote CI, deployment, production connectivity or storage availability. Global English locale persistence on reload is an existing separate issue; recovery tests reselect the language and retain the original operation identity.
