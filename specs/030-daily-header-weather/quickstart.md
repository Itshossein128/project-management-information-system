# Quickstart and Verification: Standardized Daily Weather and Temperature

This is a brownfield convergence guide. Much of the feature already exists on `develop`; verification must prove the narrowed specification and close observed gaps rather than treating committed code or checked tasks as completion evidence.

## 1. Local prerequisites

From the repository root, start the native services required by the cloud/dev environment:

```bash
sudo pg_ctlcluster 16 main start
sudo redis-server /etc/redis/redis.conf --daemonize yes
```

Use the existing root `.env`, PostgreSQL on port `5433`, and Redis on `6379`. Keep Django pinned to `4.2.11`; do not install `apps/api/requirements-dev.txt` wholesale because its debug-toolbar constraint can upgrade Django.

Start the application in separate terminals when browser/API proof is needed:

```bash
pnpm dev:api
```

```bash
pnpm dev:web
```

The root `playwright.config.ts` does not start these services automatically.

## 2. Brownfield baseline and TDD order

Before editing, confirm that the committed baseline contains the shared enum, migrations, serializers, aggregation, UI controls, and PDF path described in [research.md](./research.md). Then use red → minimal green → regression order:

1. Add strict migration-executor tests for all three legacy mappings and unrelated-data preservation.
2. Add strict model/API tests for bounds, effective-state partial updates, and both the exact top-level code and `temp_max` detail placement.
3. Add aggregation tests for the full five-level order, blanks, unknown stored values, no-valid-contributor clearing, and approved override preservation.
4. Add notes tests for header/detail hydration, rebuild, correction, sync, and offline replay.
5. Add PDF tests for the exact unconditional label, empty cell, mixed-language/multiline content, markup-significant characters, and valid output.
6. Add client tests/E2E proving shared five-choice controls, save/autosave/offline blocking, structured server-error mapping, and note hydration.
7. Implement only the smallest changes needed to make each red test pass.
8. Rerun focused and relevant regression suites on the final tree.

Do not add or modify inactivity reasons, daily-report creation permissions, shift behavior, or inactive-day activity warnings under this feature.

## 3. Migration safety and evidence

The existing migration files are committed history. Inspect their state; do not edit them:

```bash
cd apps/api/core
set -a
source ../../../.env
set +a

../.venv/bin/python manage.py showmigrations field_reports sub_reports
../.venv/bin/python manage.py migrate --plan
../.venv/bin/python manage.py makemigrations --check --dry-run
```

For a production-like database, create a recoverable backup before any forward corrective migration:

```bash
pg_dump -h 127.0.0.1 -p 5433 -U ipcas -d ipcas \
  --format=custom --file=/tmp/velora-before-weather-standardization.dump
```

Capture pre/post counts for `sunny`, `partly_cloudy`, `foggy`, approved values, and unexpected nonblank values in:

- `daily_reports`
- `weather_logs`
- `discipline_sub_reports`

Post-migration assertions:

- `sunny` moved to `clear`;
- `partly_cloudy` and `foggy` moved to `cloudy`;
- zero retired or unexpected nonblank weather values remain;
- row identity, project/date links, note text, and unrelated fields did not change;
- exact legacy categories are recoverable only from the backup because normalization is lossy.

Run the migration-executor test directly once created:

```bash
../.venv/bin/python -m pytest \
  field_reports/tests/test_daily_report_weather_migration.py -q
```

## 4. Focused backend tests

From `apps/api/core` with `.env` still exported:

```bash
../.venv/bin/python -m pytest \
  field_reports/tests/test_spec_01_daily_header_weather.py \
  field_reports/tests/test_weather.py \
  field_reports/tests/test_daily_report_summary_metadata.py \
  field_reports/tests/test_daily_report_gaps_correction.py \
  field_reports/tests/test_sync_batch.py \
  sub_reports/tests \
  -q
```

The focused evidence must prove:

- all five approved values are accepted and retired/unknown values are rejected;
- model `full_clean()` enforces inclusive bounds;
- API PATCH merges omitted fields with stored values;
- reversed ranges produce exactly `error.code=temp_max_must_be_gte_temp_min` and `error.details.temp_max`;
- all five severity levels order correctly;
- blank/invalid contributors do not win aggregation;
- no valid contributor clears derived weather unless an approved override exists;
- impact notes survive detail readback, rebuild, correction, and sync;
- project scoping/authorization on the touched header and PDF paths has not regressed.

Relevant regression suite:

```bash
../.venv/bin/python -m pytest field_reports/tests sub_reports/tests -q
../.venv/bin/python manage.py verify_blueprint_schema
```

Do not use `manage.py test`; these suites use pytest fixtures and markers.

## 5. Direct API validation probes

Using an authorized project editor and an existing daily report, exercise the real PATCH endpoint from [the API contract](./contracts/daily-report-header-weather-api.md):

| Probe | Expected result |
|-------|-----------------|
| Each approved weather value | `200`, same stable value in response |
| `sunny`, `partly_cloudy`, `foggy`, unknown value | `400`, details under `weather_condition` |
| `temp_min=-40`, `temp_max=60` | `200` |
| Equal minimum and maximum | `200` |
| Value immediately outside a bound | `400`, corresponding field in details |
| PATCH only `temp_max` below stored `temp_min` | `400`, exact stable code and `temp_max` details |
| PATCH only `temp_min` above stored `temp_max` | Same reversed-range contract on `temp_max` |
| Clear one temperature with `null` | `200`, cleared field returned as `null` |
| Multi-line Persian/English note | `200`, exact text returned on PATCH and GET |

Compare row contents before and after rejected requests to prove no invalid mutation persisted.

## 6. Aggregation verification

Build eligible specialty-report sets that cover:

- every adjacent severity pair;
- all five values together;
- blank plus approved values;
- an unexpected stored value plus approved values;
- only blank/unknown values;
- removal of all previously contributing valid values;
- an approved project override.

Expected results follow [data-model.md](./data-model.md): approved maximum severity wins, no valid contribution yields `null`, and an approved override is preserved. Verify `weather_impact_notes` is byte-for-byte unchanged across every rebuild case.

## 7. PDF proof

Generate the official PDF through the real endpoint for two reports:

1. a distinctive multi-line Persian/English note containing `&` and `<`;
2. an empty note.

Automated assertions must cover:

- valid `%PDF` output and endpoint content type;
- exact required row label in the generator/header-row contract;
- exact distinctive note after text extraction where the embedded font permits reliable extraction;
- the same labelled row with an empty value for the empty-note report;
- no parse/layout failure from line breaks or markup-significant characters.

Preserve and inspect the artifact:

```bash
pdftotext /tmp/daily-report-weather.pdf - | rg 'اثر آزمایشی|Weather impact'
pdftoppm -png -f 1 -singlefile \
  /tmp/daily-report-weather.pdf /tmp/daily-report-weather-page
```

Open the rendered PNG and verify Persian shaping, the exact label, wrapping, line breaks, and absence of overlap. Text extraction and visual inspection prove different boundaries; record both.

## 8. Frontend static and offline checks

From the repository root:

```bash
pnpm typecheck
```

If the documented pre-existing `DailyReportForm.tsx` TypeScript baseline error remains, report it separately and show whether changed files introduce any additional errors. Do not describe a non-zero baseline as a green feature check.

Search for retired values:

```bash
rg -n 'sunny|partly_cloudy|foggy' apps/web/src e2e
```

Every remaining match must be migration compatibility code or an explicit rejection/normalization test—not an option, default, label, icon mapping, or newly emitted payload.

Run the existing pure normalization test:

```bash
node --test --experimental-strip-types \
  apps/web/src/app/lib/__tests__/offlineDB.test.ts
```

Add focused validation-helper coverage or prove the same behavior through Playwright if no general frontend unit-test runner is introduced. The repository currently has no generic frontend unit-test script, so do not invent a passing command.

## 9. Browser verification

With API/web services running, execute the focused root Playwright spec:

```bash
pnpm exec playwright test \
  e2e/tests/daily-report-header-weather.spec.ts \
  --project=chromium-desktop

pnpm exec playwright test \
  e2e/tests/daily-report-header-weather.spec.ts \
  --project=mobile-chrome
```

Required scenarios on both editable header surfaces:

1. Exactly five localized weather choices appear in the required order; no retired value appears.
2. Keyboard selection updates checked state and visible text/icon remain redundant.
3. Boundary and equal temperatures save once with the expected payload.
4. Out-of-range and reversed values show associated inline errors and cause zero API requests/queue writes.
5. Slowly typing an incomplete negative/decimal token causes no autosave or accidental null write.
6. A mocked structured API error maps by `code/details` to `temp_max`.
7. Saving a multi-line mixed-language note, refetching, and reopening preserves the exact value.
8. Reopening the legacy form does not blank notes before its autosave timer runs.
9. Persian uses RTL labels/messages and English uses LTR localized labels/messages.
10. Desktop and mobile layouts keep controls, errors, and note text readable.

For offline proof, load and seed the application online, switch the context offline, attempt valid and invalid edits, then reconnect. Invalid input creates no queue entry; valid weather/temperature/note data replays once and survives refetch.

For the usability outcome in SC-007, run a short moderated task with at least 10 representative editors across Persian and English. Each participant must select weather, enter valid temperatures, encounter and correct one invalid temperature, and add an impact note without coaching. Record completion and first-attempt correction rates; at least 9 of 10 must complete the flow without external assistance.

## 10. Final evidence report

Report these categories separately:

- migration state, backup, pre/post counts, and migration-executor result;
- focused model/API/aggregation/correction/sync test totals;
- full field-report/sub-report regression totals;
- typecheck status and any independently identified baseline failures;
- offline normalization and replay evidence;
- desktop/mobile Persian/English Playwright results;
- PDF generator/endpoint, extraction, and visual-render evidence;
- infrastructure or scenarios not exercised.

A checked task list, committed migration, source inspection, or PDF signature alone is not end-to-end delivery proof.
