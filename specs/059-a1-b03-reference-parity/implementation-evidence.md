# B03 Implementation Evidence

## Execution status

B03 Stage 4.2 implemented and checked all four download families against isolated synthetic data. The [B05 handoff index](evidence/README.md) links the files, fixture sources, and exact report versions.

## Initial baseline attempts (2026-11-20)

- Workspace: `/home/hossein/Desktop/projects/building-management`.
- PostgreSQL on port 5433 responded as accepting connections; Redis returned `PONG`.
- B01 fixture seed command exists at `apps/api/core/field_reports/management/commands/seed_a1_reference_fixture.py`.
- Existing workspace contains B01/B02 modifications and artifacts. They were preserved.
- Command: `cd apps/api/core && ../.venv/bin/python -m pytest field_reports/tests/test_a1_b01_data_contract.py field_reports/tests/test_a1_b02_version_integrity.py -q`.
- Result: **2 passed, 35 errors**. The test database `test_ipcas` already existed and was being accessed by another session; pytest could not safely recreate it.
- Isolation retry with `TEST_DATABASE_NAME=test_ipcas_b03_20261120` did not reach test execution after approximately 65 seconds and was interrupted. No tests ran in that retry. No shared database was dropped or modified.
- Knowledge index status was stale with a recorded failed embedding job. No indexing job was started.

## Stage 4.2 execution

- Spec Kit resolved this feature and its plan and tasks. The requirements checklist passed 16/16. No implementation extension hooks are registered.
- Django 4.2.11, PostgreSQL on 5433 and Redis were verified. A fresh `velora_b03_s42_20261120` database migrated forward and the B01 seed command imported `SIM-A1-001-12-1406-03-01`. `prepare-fixtures.py` populates the following cases in that isolated database.
- Normal, 2027-05-22, `fb9bcd42-a786-4b19-ba7b-1548c9526393`. B01 source with five activity rows and observed shift durations 8.50 and unknown.
- Inactive, 2027-05-23, `84b5f113-d71f-5ac8-a194-5759e9052047`. Holiday with no operational rows.
- Measured zero, 2027-05-24, `a7051254-2a55-5675-9386-3acdf09c7cb5`. Productive and idle hours and FILE 5 source progress are zero.
- Unknown, 2027-05-25, `e2bbd5dc-ac69-5c69-8afd-2e87fd43db58`. Productive and idle hours and FILE 5 source progress are null.
- Three shifts, 2027-05-26, `b21661df-88e7-59f9-befc-718e1ab746fa`. Recorded durations are 8.50, 7.25, and 6.00 hours.
- Long bilingual, 2027-05-27, `49248f37-a9a5-5db4-9d73-6c1f8b54091d`. 56 activity descriptions with Persian and English on separate lines.
- The configured local MinIO endpoint returned connection refused. The final browser run used a local S3 HTTP emulator.
- The earlier baseline failure was resolved using `TEST_DATABASE_NAME=test_ipcas_b03_s42_1795162559`. From `apps/api/core`, `../.venv/bin/python -m pytest field_reports/tests/test_a1_b01_data_contract.py field_reports/tests/test_a1_b02_version_integrity.py --reuse-db -x -vv` passed **37 tests** in 184.55 seconds. Shared databases were left intact.
- The refreshed hybrid knowledge index was usable during this run. A separate pre-change migration drift check reported an existing change to `storage.StoredFile.source`. B03 owns no change to that field.

### Foundation and US1

- Red tests reproduced export access by unscoped observation accounts and spreadsheet export of a deleted unit version. After the changes, both permission modules passed **27 tests**. Established report downloads accept an active member with `view_reports`, or a named observer whose persisted active organization unit exactly matches the project's owning unit. File authorization continues to require separate active membership and the file's source and allowlist permissions.
- Red tests reproduced absent editable shift timestamps, mutable observed weather on approved reports, vertically stacked Shiraz slots and fixed placeholders on unprofiled projects. New observed timestamps are nullable, independently validated and carried into a correction. Approval records observed weather and available cached forecast evidence. A current preview can refresh the bounded weather cache.
- The header/weather, FILE 4, daily PDF, PDF summary and watermark regression modules passed **55 tests**. The B01 observed-header and the B02 correction-copy checks passed in the focused run. `pnpm typecheck` passed. The existing Chromium inactivity spec passed **5 tests** with mocked API responses, including Persian confirm/cancel and English copy.

### US2

- The focused operational/export suite passed **92 tests**. Regression coverage includes legacy zero/unknown machinery, receipt versus non-receipt sections, localized severity, exact-version provenance, canonical QC IDs, sample code and sheet-count separation, and actual image validation and attachment scope through a mocked S3 client.
- The inspection schema has no verified mixer identifier, lab sheet number, slump or 28-day result relation. The concrete detail returns unknown evidence for these fields and keeps the generic inspection link separate. A conflicting equipment state contributes one machine without assigning a status category.
- The Docker daemon denied both attempted MinIO image pulls. A temporary Moto server on loopback provided real HTTP upload and download for the browser test. Production MinIO remains outside this evidence.

### US3 and US4

- Worksheet print properties survive serialization. User strings remain literal and the fixture grand total retains a live formula. LibreOffice recalculated `=SUM(G49,P47,G54)` to **24 person-shifts**, identical to the independent sum from the B01 fixture JSON. The reference and long workbooks exported to landscape A4 in LibreOffice.
- The long daily PDF rendered **9 pages per locale** and the long buildings PDF rendered **8 pages per locale**. Visual inspection showed the watermark over the table on every draft page and the signature block at the end. The approved reference PDF rendered **4 pages** without a draft mark. Poppler text extraction confirmed the EN page counts and marks. Automated checks cover direct approval, unknown legacy position, action-time role and Iran-local midnight, all non-approved statuses, and metadata-fingerprint scope.
- The range API accepted 31 inclusive days, rejected 32 at the default, accepted 32 with the test override, and selected the current approved non-deleted versions across correction open, cancel, and replacement approval. The 31-sheet sample with 12 activity rows per day was **204,237 bytes** and took **3.237 seconds** for a local HTTP request. The earlier run of an equivalent input took 2.082 seconds.
- Real browser downloads exposed a conflicting legacy discipline label on an electrical version. The canonical unit now controls the workbook schema, including the filename and exclusion of building-only columns. FILE 5 independently verified numeric values of 0, 0.455, and 1 and an empty unknown cell.

### Verification gates and evidence

- **Backend**. The integrated isolated PostgreSQL suite recorded **206 passed** across B01/B02, headers, exports, permissions, aggregation, QC, and attachments. The expanded watermark module passed **12 tests**. After the final machinery change, the affected export, attachment and machinery modules passed **52 tests**, and the B03 schema drift check found no changes in field_reports or sub_reports.
- **Migrations**. Field reports 0027–0028 and unit reports 0015–0016 applied on `velora_b03_s42_20261120`. On a separate `velora_b03_rollback_20261120` database, the four migrations were reversed and reapplied. B01's reference report, five activity rows, 68 labor rows, and worked shifts 1 and 3 survived. Legacy timestamp, forecast and actor evidence remained null. Production rollback would require retaining newly captured evidence separately before reversing the additive fields.
- **Frontend and browser**. `pnpm typecheck` passed. Chromium passed **8 checks** with one worker. Two used real authenticated FA/EN downloads of FILE 4, the daily PDF, FILE 5 and 6, the range workbook, and all six unit PDFs. Both entered dates by keyboard, downloaded using Enter, and checked localized reversed-range errors. The attachment check used a scoped editor upload and a scoped viewer download with byte-for-byte comparison against the submitted PNG. Five inactivity guards used mocked API responses.
- **DEF-B03-01**. The three-shift API and export fixtures list recorded shifts and 8.50, 7.25, and 6.00 hours. The API regression covers an overnight end timestamp and independent duration. The reference contains one unknown duration.
- **DEF-B03-02 and DEF-B03-08**. The selected Shiraz profile places its two blocks on the same starting row, preserves 34 and 32 standard positions and separate contractor rows in the appendix, and excludes fixed placeholders for the custom case.
- **DEF-B03-03 and DEF-B03-04**. The [A4 previews and long PDFs](evidence/README.md) show repeat print titles, wrapped content, the all-page draft mark and final attribution. Automated checks cover safe text, real action-time position and local time, direct approval, and the C06 fingerprint.
- **DEF-B03-05**. The legacy zero and unknown workbook samples contained numeric 0 and a blank, respectively. The active regression also verifies the equivalent PDF values. The historical XFAIL is recorded in the archived QA findings.
- **DEF-B03-06 and DEF-B03-07**. Concrete export columns include the delivery note, sample code and localized sampling state. The exact-version detail shows separately scoped QC evidence. Persian HSE severity uses localized terms, including `شدید`.
- **Remaining release scope**. The storage check used Moto over HTTP and the output checks used synthetic reports. Independent reconciliation belongs to B05 and employer acceptance remains pending B06. Existing uncommitted B01/B02 and unrelated files were preserved. The shared worktree includes same-file changes from the earlier packages, so this stage remains uncommitted.

### Stage 4.2 recheck (2026-11-21)

- Spec Kit resolved the B03 plan and tasks. The requirements checklist had 16 of 16 checks, and T001–T037 were marked complete. All 65 local links checked across the plan, tasks, quickstart and two evidence indexes resolved.
- The focused B01/B02/B03 suite passed **184 tests** across 17 pytest modules using isolated PostgreSQL. `pnpm typecheck` and `git diff --check` passed. A fresh disposable development database applied field reports 0027–0028, sub-reports 0015–0016 and projects 0022 before importing the B01 reference and B03 variants. The quickstart now runs Django directly because the pnpm wrapper reloads the root `.env`.
- Openpyxl verified A4, one-page-wide fit, print area and repeat titles on **41 sheets across 11 saved workbooks**. The range workbook had 31 chronologically ordered sheets. Poppler found draft marks on **9 of 9** long daily PDF pages and **8 of 8** long unit PDF pages, and on **0 of 4** approved reference pages. The three saved LibreOffice previews report landscape A4.
- The first FA/EN browser pass exposed a 404 in the machinery tab's reporting configuration request. The shared unit-report client now uses the API-relative path and converts the report's Solar Hijri date to ISO Gregorian. The B03 browser tests check for HTTP 200 and the exact date in both locales.
- After that fix, Chromium passed **8 checks** in 45 seconds. The authenticated FA/EN journeys downloaded **22 files** across DEL-01–04, including every unit PDF in each locale. The authenticated attachment check compared the downloaded PNG byte for byte using Moto over HTTP. Five inactivity tests used API mocks.
- The local semantic index was stale and the refresh failed to connect to the configured embedding service. The recheck used the B03 source artifacts and the running workspace directly.
