# Quickstart: Verify B03 after implementation

Use an isolated development database named with the `velora_b03_` prefix and the labeled B01 reference fixture. [Implementation evidence](implementation-evidence.md) records executed checks.

## 1. Prepare the environment

Use the repository's pinned dependencies and configured development PostgreSQL and Redis. Start both before Django. Use a developer database and authorized test accounts. Keep the attachment checks on an environment with working object storage. Load the root `.env` into the API shell first, then export `DATABASE_URL` pointing to the isolated database. Set `B03_TEST_PASSWORD` before preparing the fixture to create the browser accounts. For the attachment check, configure the storage endpoint and bucket first and set `B03_TEST_ATTACHMENTS=1`.

Run the Django commands directly in the API shell so the exported database and storage settings take effect. The pnpm Django wrapper sources the root `.env` on each invocation.

```bash
cd apps/api/core
../.venv/bin/python manage.py migrate --noinput
../.venv/bin/python manage.py seed_a1_reference_fixture
../.venv/bin/python manage.py shell < ../../../specs/059-a1-b03-reference-parity/prepare-fixtures.py
../.venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload
```

In a separate terminal at the repository root, run `pnpm dev:web`.

Prepare reports that represent a normal day, inactive day, real zero, unknown hour and progress percentage, all three worked shifts, and a report with more than 50 rows and multiline FA/EN text. Include the selectable Shiraz profile and one project with a different catalog. Use recorded actor and role evidence, including a timestamp near local midnight. Prepare a draft, direct approval without review, a fully reviewed approved report, and an open correction with preserved overrides and provenance. Include current, historical and soft-deleted records and a legacy date with multiple eligible shifts.

## 2. Run focused regressions

From `apps/api/core`, load the repository's development environment using the standard local setup, then run:

```bash
../.venv/bin/python -m pytest \
  field_reports/tests/test_a1_b01_data_contract.py \
  field_reports/tests/test_a1_b02_version_integrity.py \
  field_reports/tests/test_shiraz_file4_excel.py \
  field_reports/tests/test_daily_report_pdf.py \
  field_reports/tests/test_pdf_summary_parity.py \
  field_reports/tests/test_pdf_signatures_watermark.py \
  field_reports/tests/test_daily_report_aggregation_sections.py \
  sub_reports/tests/test_concrete_qc_link.py \
  sub_reports/tests/test_shiraz_subreport_excel.py
```

Run `field_reports/tests/test_b03_workbook_range.py`, `field_reports/tests/test_daily_report_summary_permissions.py`, `sub_reports/tests/test_b03_unit_report_pdf.py`, `sub_reports/tests/test_b03_report_attachments.py`, and `sub_reports/tests/test_unit_report_permissions.py` for range limits, exact versions, and attachment scope. Verify forward migration and preservation of legacy values and B02 clone evidence. Run `pnpm typecheck` from the repository root.

For real downloads, export the same `B03_TEST_PASSWORD` in the Playwright shell. Set `B03_TEST_ATTACHMENTS=1` there if storage and the attachment fixture were prepared. Run `pnpm exec playwright test --project=chromium-desktop e2e/tests/b03-reference-parity.spec.ts` with the API and web servers running. The browser suite signs in through the backend and saves the downloaded files in the Playwright output directory.

## 3. Download through the actual UI and API

1. Sign in as an authorized project member and use the daily detail page to download FILE 4 and PDF for the selected exact version. Use the daily list's range action for the workbook. Use the unit panel for FILE 5, FILE 6 and standalone PDFs from all supported units. Repeat in FA and EN, using keyboard access and checking feedback.
2. Verify headers, filenames, MIME types, locale, and authorization against the [download contract](contracts/exports.md). Repeat with an unauthenticated session, member lacking permission, authorized scoped observation account, same-organization nonmember, HR-only and cross-tenant accounts. Check direct URLs, alternate UUIDs, wrong unit, deleted rows, and protected drill-downs. Testing an attachment denial uses an isolated synthetic file.
3. Test valid Jalali and Gregorian endpoints, a reversed range, no eligible reports, the configured maximum and one day over, and a legacy ambiguity. Inspect order and membership across a sparse range, an open correction, cancellation and a newly approved version. For an authorized explicit historical ID, verify the retained snapshot. Confirm API and browser downloads do not change business data.
4. Inspect XLSX cells with openpyxl and render print preview in a spreadsheet application. Confirm A4, one page wide, correct print area, repeated headings, wrapping and row heights. Verify numeric cells and live formulas separately from formatted display, including FILE 5 values `0`, `0.455`, `1`, and blank. Check that only FILE 6 electrical columns are present and literal user text stays intact. Independently sum the fixture columns and confirm rendered totals.
5. Render and visually inspect every page of the long daily and unit PDFs. Compare the expected version and source facts to both export formats, including legacy null vs zero, adjacent manpower tables, appendix titles, localized HSE terms, QC link visibility, and Persian glyphs. Verify the final signature block, exact role and local date/time, skipped stage, metadata fingerprint terminology and all-page watermark policy.

## 4. Record evidence

| Criterion | Evidence to retain |
| --- | --- |
| SC-001 | Results for DEF-B03-01 through DEF-B03-08 and removal of the historical expected failure after the fix is proven. |
| SC-002 | Values and layout for all six fixture scenarios. Record any fabricated values, mislabeled actors, clipping, total differences or formula errors. |
| SC-003 | Profile and custom-catalog output with intact extra titles and checked manpower totals. |
| SC-004 | Workbook property inspection, independent expected totals and visual print previews. |
| SC-005 | Annotated PDF page images and event evidence for watermarks and attribution in daily and discipline outputs. |
| SC-006 | Four deliverable families, locale and permission matrix, version IDs and applied range bounds. |
| SC-007 | Negative role, scope, attachment and fingerprint-label checks. |
| SC-008 | B03 technical readiness report and artifacts for B05. Employer sign-off remains pending B06 review. |
