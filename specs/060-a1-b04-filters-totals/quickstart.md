# B04 Verification Quickstart

Run after implementation against an isolated development or test project with PostgreSQL and Redis. Use the workspace API virtual environment and the existing authenticated Playwright setup. Provide authorized accounts with equivalent project access, a member without report permission, and a user belonging only to another project. Keep credentials outside evidence files.

## Browser fixture

Point `DATABASE_URL` at an empty migrated database whose name begins with `velora_b04_` and use a dedicated Redis instance. Set `B04_TEST_PASSWORD` through the environment and run the seed from the repository root. The returned JSON contains fixture IDs and dates for the browser run.

```bash
(cd apps/api/core && ../.venv/bin/python manage.py shell < ../../../e2e/fixtures/seed_b04.py) > /tmp/b04-fixture.json
eval "$(python3 - <<'PY'
import json
import shlex
for key, value in json.load(open('/tmp/b04-fixture.json')).items():
    print(f'export {key}={shlex.quote(value)}')
PY
)"
```

Use `B04_TEST_API_URL` for the API base, including `/api`, and `B04_TEST_WEB_URL` for the interface origin. Set `VITE_API_BASE_URL` and `CORS_ALLOWED_ORIGINS` for those services. Enable eager tasks and synchronous audit logging when running without workers. Viewer accounts `b04-viewer-1` and `b04-viewer-2` have equivalent permissions. `b04-no-reports` has project membership with no report permission. `b04-other-project` belongs to the second project.

## Automated checks

From the repository root, run the existing B01/B02 and FILE1 regressions plus the planned B04 suites once those files exist:

```bash
set -a
source .env
set +a
(cd apps/api/core && ../.venv/bin/python -m pytest \
  field_reports/tests/test_a1_b01_data_contract.py \
  field_reports/tests/test_a1_b02_version_integrity.py \
  field_reports/tests/test_activity_log_sync.py \
  field_reports/tests/test_shiraz_file1_excel.py \
  field_reports/tests/test_a1_b04_filters_totals.py)
pnpm typecheck
pnpm e2e e2e/tests/b04-filters-totals.spec.ts --project=chromium-desktop --workers=1 --grep-invert SC-004
pnpm e2e e2e/tests/b04-filters-totals.spec.ts --project=chromium-desktop --workers=1 --grep SC-004
```

Run SC-004 on its own after the regression and acceptance runs finish. It consumes the submitted timing fixture by approving it. Use a fresh isolated fixture for a repeat measurement. The verifier brackets approval commit visibility with read-only PostgreSQL queries and records the next browser paint and approval response on the same host clock.

For manual browser verification, start `pnpm dev:api` and `pnpm dev:web` in separate terminals after starting Postgres and Redis. Use the [interface contract](contracts/filters-and-totals.md) against the same build as the browser.

## Acceptance runs

1. **FR-001 and SC-001** Seed Story 1 scenario 3. With CIVIL, Contractor A and Block 1, expect exactly the first summary once, even though it has two matching rows. The split-row summary is excluded. Check single-dimension, combined and date/status-only selections. Test an ineligible source and foreign contractor ID. Compare API identities with the visible list and any offered filtered-list export.
2. **FR-002 through FR-007 and SC-001, SC-002 and SC-003** Seed 51 eligible activity rows with headcount one per row, quantities in m² and m³, measured zero, unset and legacy unmeasured values, two contractors with the same job title and two approved revisions in a lineage. Add excluded historical and deleted control records outside the 51 expected rows. Use `page_size=50`, fetch both pages and download FILE1 from both selections. Compare each export's 51 row identities and per-unit totals to an independent fixture manifest. Expect count and headcount 51 on both pages, no extra or missing identities, and numeric zero distinct from unknown. Test explicit preview, history separation, negative project access, and filter option scope.
3. **SC-001 and SC-003** In FA/RTL and EN/LTR, apply combined filters, copy the URL to the second authorized session, reload, page, then use Back and Forward. Compare controls, page, row identities, totals and FILE1 selection. Verify localized unknown and headcount labels. Repeat direct API list, option and export requests as each unauthorized actor.
4. **SC-004** Document dataset size and date window, environment, browser version, network, and cache state. With independent sessions and synchronized timing, measure from the committed approval timestamp to all expected activities visible in the matching log. Record the approval response timestamp separately. Require visibility within one second, including cache invalidation. Separately measure from applying CIVIL, «آرماتوربند الف» and last month to rendering matching rows and whole-result totals. Require under one second. Record cold and warm conditions and retain elapsed times and browser/network evidence.

Record the tested commit, fixture identity, executed commands, pass/fail results, and paths to API responses, browser evidence, workbook checksums and independent expected values. Supply these to B05 and B06. Employer disposition belongs to B06.
