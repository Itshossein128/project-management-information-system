# Quickstart and Verification: Daily Report Header and Weather Controls

This is the implementation verification guide. A green focused test is necessary but does not by itself prove migration safety, browser behavior, offline behavior, PDF content, or the full regression boundary.

## 1. Local prerequisites

From the repository root:

```bash
sudo pg_ctlcluster 16 main start
sudo redis-server /etc/redis/redis.conf --daemonize yes
```

Use the existing root `.env`. It must point to PostgreSQL on port `5433` and Redis on `6379`. Keep Django pinned to `4.2.11`; do not install `requirements-dev.txt` wholesale.

Start the services in separate terminals:

```bash
pnpm dev:api
```

```bash
pnpm dev:web
```

The current `playwright.config.ts` has no `webServer` block, so Playwright does not start either service automatically.

## 2. TDD order

Implement in red → minimal green → regression order:

1. Migration normalization and new model constraints/fields.
2. Serializer field placement and stable error codes, including partial PATCH.
3. GET/POST `by-date` permission and mutation behavior plus concurrent ensure.
4. Aggregation, rebuild, correction, lifecycle, and sync preservation.
5. PDF content.
6. Shared frontend types/metadata/validation and actual summary editor.
7. Activity confirmation before online/offline writes.
8. IndexedDB upgrade/replay compatibility.
9. Bilingual desktop/mobile/offline E2E.

Record the failing assertion before each minimal implementation change. After code changes, rerun against the final tree; a historical green run is not final evidence.

## 3. Migration safety

Before applying the migration outside disposable development data:

```bash
pg_dump -h 127.0.0.1 -p 5433 -U ipcas -d ipcas \
  --format=custom --file=/tmp/velora-before-daily-header-weather.dump
```

Capture pre-migration counts for `sunny`, `partly_cloudy`, and `foggy` in daily reports, weather logs, and specialty reports. Then inspect and apply the plan:

```bash
cd apps/api/core
set -a
source ../../../.env
set +a
../.venv/bin/python manage.py makemigrations --check --dry-run
../.venv/bin/python manage.py migrate --plan
../.venv/bin/python manage.py migrate
```

Post-migration assertions:

- no server row contains a retired weather value;
- `sunny` counts moved to `clear`;
- `partly_cloudy` and `foggy` counts moved to `cloudy`;
- report identity, project/date/shift, and unrelated fields did not change;
- new text/reason fields have non-destructive blank defaults;
- schema verification still passes:

```bash
../.venv/bin/python manage.py verify_blueprint_schema
```

Exact legacy categories cannot be reconstructed from the reverse migration; use the backup when exact semantic rollback is required.

## 4. Focused backend tests

From `apps/api/core` with `.env` exported:

```bash
../.venv/bin/python -m pytest \
  field_reports/tests/test_spec_01_daily_header_weather.py \
  field_reports/tests/test_daily_report_by_date.py \
  field_reports/tests/test_daily_report_summary_permissions.py \
  field_reports/tests/test_daily_report_summary_metadata.py \
  field_reports/tests/test_daily_report_gaps_correction.py \
  field_reports/tests/test_sync_batch.py \
  field_reports/tests/test_weather.py \
  sub_reports/tests \
  -q
```

`test_spec_01_daily_header_weather.py` is the planned focused feature suite. It should cover:

- the five weather choices on all three persisted entities;
- data-migration outcomes;
- inclusive `-40` and `60` boundaries and out-of-range rejection;
- partial-update min/max comparison and error attachment to `temp_max`;
- required inactivity reason, active-state clearing, and lifecycle rejection;
- weather-impact/reason preservation in rebuild, correction, and sync;
- deterministic severity;
- PDF content;
- raw-create blocking and the by-date permission matrix;
- one logical report under concurrent PostgreSQL POSTs.

Relevant regression suite:

```bash
../.venv/bin/python -m pytest field_reports/tests sub_reports/tests -q
```

Do not substitute `manage.py test`; this repository's suites use pytest fixtures and markers.

## 5. API permission and mutation matrix

Verify using distinct active project members:

| Actor/action | Expected result | Database effect |
|--------------|-----------------|-----------------|
| viewer GET existing date | `200` | none |
| viewer GET missing date | `404` | none |
| viewer POST by-date | `403` | none |
| editor POST missing date | `200`/`201` per existing convention | one full-day summary |
| editor POST same date again | `200` | still one current summary |
| editor raw collection POST | `400 auto_summary_only` | none |
| member of another project | `403`/scoped `404` per existing convention | none |

For the two viewer cases, compare row counts and timestamps before/after to prove GET is read-only. For concurrency, use real PostgreSQL transactions/workers rather than mocks and assert the current-row count is one.

## 6. Validation probes

Exercise both full and partial header updates:

- `temp_min=-40`, `temp_max=60` succeeds;
- values below/above the bounds fail on their own fields;
- update only `temp_max` below stored `temp_min` and receive `temp_max_must_be_gte_temp_min` on `temp_max`;
- update only `temp_min` above stored `temp_max` and receive the same code on `temp_max`;
- inactive without a reason receives `inactivity_reason_required` on `inactivity_reason`;
- inactive with each allowed reason succeeds;
- changing to active clears the stored reason;
- retired weather strings are rejected as new input.

Repeat the weather/range probes for standalone weather logs and the vocabulary probes for specialty reports.

## 7. PDF proof

Generate the official PDF through the real endpoint using a report with a distinctive impact note and inactive reason. Preserve the file, then inspect text:

```bash
pdftotext /tmp/daily-report-header-weather.pdf - | \
  rg 'گرد و غبار دید ماشین‌آلات را محدود کرد|حادثه ایمنی'
```

Also render/open the output and visually inspect the header table for RTL shaping, wrapping, non-overlap, and page boundaries. `%PDF` plus extracted text proves format/content presence; the visual review covers layout quality.

## 8. Frontend static checks

From the repository root:

```bash
pnpm typecheck
```

Record unrelated pre-existing failures separately if still present; do not report a non-zero baseline as feature success. Search the final client tree for retired values and confirm any remaining matches are migration compatibility code or explicit rejection tests:

```bash
rg -n 'sunny|partly_cloudy|foggy' apps/web/src e2e
```

## 9. Browser verification

With API and web servers already running:

```bash
pnpm exec playwright test \
  e2e/tests/daily-report-header-weather.spec.ts \
  --project=chromium-desktop

pnpm exec playwright test \
  e2e/tests/daily-report-header-weather.spec.ts \
  --project=mobile-chrome
```

Required scenarios:

1. No new-report button or editable header shift is present.
2. Editor and viewer date-opening behavior matches the permission matrix.
3. Exactly five weather options appear on every relevant UI.
4. Range and order errors prevent the request and identify the right field.
5. Inactive reveals a required reason; active hides and clears it.
6. Impact notes survive save/refetch and are visible in the downloaded PDF.
7. Positive activity create/edit on an inactive date opens the exact Persian warning.
8. Cancel causes no network write and does not loop under autosave; editing/retrying can prompt again.
9. Confirm issues one write and keeps the site status unchanged.
10. Keyboard focus enters the dialog, Escape/cancel is safe, and focus returns to the initiating row.
11. Repeat locale-sensitive assertions in Persian RTL and English LTR.

## 10. Offline verification

Use a prepared browser database at the pre-upgrade version containing:

- a cached report with `sunny`;
- pending queue payloads with `partly_cloudy` and `foggy`;
- queue retry metadata and unrelated fields.

Load the new client and verify the IndexedDB upgrade maps values to `clear`/`cloudy` without losing records or metadata. Then test a positive activity edit on an inactive report:

- cancel creates no queue entry;
- confirm creates exactly one queue entry;
- reconnect replays it once;
- new header fields survive replay/conflict handling.

The configured `pwa-offline` Playwright project starts the context offline, which may prevent initial app navigation unless the service worker/cache is pre-seeded. Use a scenario that loads and seeds online first and then toggles the context offline, or a dedicated fixture that installs the cached app state; record which method was used.

## 11. Final evidence report

Report these separately:

- migration backup, plan, applied version, and pre/post normalization counts;
- focused backend and regression test totals;
- permission and concurrent-ensure proof;
- typecheck status, including any baseline failures;
- desktop/mobile/offline Playwright results;
- PDF extraction and visual review;
- Persian/English and accessibility checks;
- unavailable infrastructure or scenarios not exercised.

Do not equate checked tasks, serializer unit tests, or a PDF signature with end-to-end delivery.
