# Tasks for A.1 / B04 Filters, Result Sets, and Totals

[Specification](spec.md) · [Plan](plan.md) · [Research](research.md) · [Data model](data-model.md) · [Interface contract](contracts/filters-and-totals.md) · [Verification guide](quickstart.md) · [Implementation evidence](implementation-evidence.md)

Tasks use repository-relative paths. `[P]` denotes a task that can run alongside the indicated work once its prerequisites are complete. Write the story regressions before changing the behavior and capture the failure for each observed gap. Each story is P1. US1 is the first reviewable increment.

## Phase 1 — Setup

- [x] T001 Confirm the isolated PostgreSQL/Redis, Django pytest and authenticated Playwright setup using `specs/060-a1-b04-filters-totals/quickstart.md`; record the candidate revision and test identities for two equivalent members, a member without report permission and an actor from another project.
- [x] T002 Run the activity cache and FILE1 baseline regressions in `apps/api/core/field_reports/tests/test_activity_log_sync.py` and `apps/api/core/field_reports/tests/test_shiraz_file1_excel.py`; record existing failures before changes.

## Phase 2 — Shared prerequisites

- [x] T003 Verify that source rows for unit and department activities project discipline, contractor and block onto one row of the selected summary version in `apps/api/core/field_reports/services/daily_report_aggregation.py` and `apps/api/core/field_reports/models.py`. Verify B01 and B02 invariants with `apps/api/core/field_reports/tests/test_a1_b01_data_contract.py` and `apps/api/core/field_reports/tests/test_a1_b02_version_integrity.py`. Preserve legacy rows and version-bound source evidence.
- [x] T004 Identify and reuse project-scoped reference checks and existing view/export permissions in `apps/api/core/field_reports/daily_report_views.py`, `apps/api/core/field_reports/report_views.py` and `apps/api/core/permissions/project.py`. All list, option, aggregate and file reads must validate access and scoped filter identities before cache lookup or query evaluation. Invalid or foreign references produce a localized validation error or empty selection, with zero disclosure and no broadened selection.

## Phase 3 — US1 Share and recover a filtered daily reports list (P1, MVP)

**Independent test** Apply date/status and CIVIL, Contractor A and Block 1. Verify one occurrence of the same-row summary even with two matching rows, zero split-row or ineligible matches and equivalent page and controls on a second authorized session after share, reload and Back/Forward.

- [x] T005 [P] [US1] Add FR-001/FR-003 regressions in `apps/api/core/field_reports/tests/test_a1_b04_filters_totals.py` for two qualifying rows in one summary, split-row exclusion, ineligible rows, historical versions, single and combined dimensions, date/status-only requests and a foreign contractor ID.
- [x] T006 [P] [US1] Add authenticated SC-001 daily-list scenarios in `e2e/tests/b04-filters-totals.spec.ts` for exact summary identities, paging and selection restoration in two equivalent sessions in FA/RTL and EN/LTR, including refresh and Back/Forward.
- [x] T007 [US1] Apply one correlated eligibility predicate to daily list queries only in `apps/api/core/field_reports/daily_report_views.py`. Date and status constrain the parent. All selected discipline, contractor and block values must match one eligible activity source row on that version. Resolve contractor identity in-project, preserve current-only defaults and existing history access, and use stable date/ID ordering. Verify existing individual exports and the separate B03 date-range workbook contract.
- [x] T008 [US1] Extend request parameters in `apps/web/src/app/lib/api/daily-reports.ts` and bind the daily list filters, page and scoped choices to canonical URL state in `apps/web/src/app/routes/daily-reports-list.tsx`. Reset page on a filter change, preserve useful history entries and keep any filtered-list download aligned. Use the existing distinct range workbook control and update accessible labels and feedback in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`.

## Phase 4 — US2 Review and export an operational activity selection (P1)

**Independent test** From two equivalent sessions, restore a multi-dimensional activity selection and page from one URL. Confirm the complete FILE1 row set from either page, exclusion of historical/deleted records, explicit current-only preview, and zero disclosure to unauthorized actors.

- [x] T009 [P] [US2] Add FR-002–FR-005 API and FILE1 regressions in `apps/api/core/field_reports/tests/test_a1_b04_filters_totals.py` for filter aliases, multi-select, exact contractor identity, the twelve FILE1 fields, status within the version policy, complete unpaginated export and direct authorization checks for list, both options paths and export. Include unauthorized and cross-project requests against warm cache.
- [x] T010 [P] [US2] Add activity URL, history and FILE1 browser cases to `e2e/tests/b04-filters-totals.spec.ts` for both languages and two project members. Verify filters and page across copied links, refresh and Back/Forward, and trigger FILE1 from each page.
- [x] T011 [US2] Extend the shared selection in `apps/api/core/field_reports/services/activity_log.py` for legacy aliases, exact contractor ID, status, location, description/WBS search, headcount, measured quantity, unit and report reference. Preserve existing date, discipline/parcel multi-select, zone, block, floor, shift, activity and subcontractor filters. Values within an existing multi-select dimension are alternatives. Across dimensions, all supplied predicates apply to the same row. Default official selection is current approved and non-deleted. Explicit preview remains current and non-deleted.
- [x] T012 [US2] Align list, both option routes, and FILE1 in `apps/api/core/field_reports/report_views.py` and `apps/api/core/field_reports/shiraz_file1_excel.py` with the shared authorized selection. Return scoped contractor IDs, preserve pagination defaults and FILE1 columns and ordering, and ignore page parameters for export. Normalize the cache fingerprint and verify the project version invalidates after committed approval and relevant correction/cancellation in `apps/api/core/field_reports/services/__init__.py` and `apps/api/core/field_reports/services/correction_service.py`.
- [x] T013 [US2] Share typed selection serialization between the list in `apps/web/src/app/lib/api/reports.ts` and FILE1 download in `apps/web/src/app/lib/api/daily-reports.ts`. Pass every selection filter to both and send paging only for list reads.
- [x] T014 [US2] Apply canonical URL filters, explicit date bounds, filter/page history, scope-safe choices and twelve-field display in `apps/web/src/app/routes/project-activity-log.tsx`. Prevent stale rows under a new selection and refetch stale client data after lifecycle changes. Add FA/EN accessible labels, loading, empty and error states in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`.

## Phase 5 — US3 Reconcile full totals from any page (P1)

**Independent test** Use 51 eligible rows at page size 50. The pages contain 50 and one row, each displays count and headcount sum 51, and FILE1 contains the same 51 identities with matching per-unit totals. Both languages distinguish measured zero from unknown.

- [x] T015 [P] [US3] Add SC-002/SC-003 cases in `apps/api/core/field_reports/tests/test_a1_b04_filters_totals.py` with independently calculated expected values for both pages and both workbook downloads. Include m² and m³, measured zero, unset, legacy unmeasured, missing unit, entirely unknown unit, empty selection, excluded historical/deleted controls and two contractors reporting the same job title.
- [x] T016 [P] [US3] Add authenticated FA/EN total and label assertions to `e2e/tests/b04-filters-totals.spec.ts`. Compare both pages and both downloaded workbooks against independent expected row identities and totals. Verify the row headcount label and distinct measured-zero and unknown displays.
- [x] T017 [US3] Compute row count, activity-row headcount sum and per-unit decimal summaries from the whole authorized activity selection before pagination in `apps/api/core/field_reports/services/activity_log.py` and `apps/api/core/field_reports/report_views.py`. An amount contributes when the row is measured and has both amount and unit. Use a null total for an all-unknown unit, count measured and unknown rows per unit, and count unknowns with missing units separately. Use an empty array when there are no known units and zero headcount for an empty selection. Return additive aggregate fields and explicit measurement state consistent with the page and authorized cache scope.
- [x] T018 [US3] Align normalized row values and numeric workbook cells in `apps/api/core/field_reports/services/activity_log.py` and `apps/api/core/field_reports/shiraz_file1_excel.py`. Preserve numeric measured zero, the workbook unknown marker and its reference columns. Keep report version eligibility and decimal totals consistent across both outputs.
- [x] T019 [US3] Type the aggregate response in `apps/web/src/app/lib/api/reports.ts` and render page-independent counts, per-unit totals and unknown states in `apps/web/src/app/routes/project-activity-log.tsx`. Replace page reductions and use the B01/D07 FA/EN label for the sum of activity-row headcounts in `apps/web/src/app/locales/fa.json` and `apps/web/src/app/locales/en.json`.

## Phase 6 — Cross-cutting verification and handoff

- [x] T020 [P] Run the B01/B02, B04 API and FILE1 regressions and a read-only migration impact check against the final candidate using `specs/060-a1-b04-filters-totals/quickstart.md` and `apps/api/core/manage.py`. Record results, applicable query counts, and authorization evidence.
- [x] T021 [P] Run frontend typecheck and authenticated bilingual acceptance, including both stories’ URL recovery and the 51-row parity workflow in `e2e/tests/b04-filters-totals.spec.ts`. Retain browser logs and workbook checksums and compare output against independent fixture values.
- [x] T022 Measure SC-004 separately in `e2e/tests/b04-filters-totals.spec.ts` using `specs/060-a1-b04-filters-totals/quickstart.md`. Require all eligible activities visible within one second of committed approval, and CIVIL/«آرماتوربند الف»/last-month rows and full totals visible in under one second from applying the filters. Record build, dataset, date window, browser, network and cold/warm cache conditions.
- [x] T023 Create `specs/060-a1-b04-filters-totals/implementation-evidence.md` with the candidate revision, executed commands, results, timings and evidence locations. Map outcomes to SC-001–SC-004 and the dated QA findings. Hand off workbook and fixture evidence to B05 and release verification inputs to B06. Keep delivery status pending where required evidence is missing.

## Dependencies and parallel examples

- Setup T001–T002 precedes shared checks T003–T004. Complete both phases before the stories.
- US1 and US2 have independent product scope. Their shared test, client and locale files require the execution order below. US3 depends on US2’s shared activity selection and typed client work.
- Within each story, run the paired API and browser test-authoring tasks in parallel after prerequisites. Complete T005 and T006 before T007–T008, T009 and T010 after the US1 test edits and before T011–T014, and T015 and T016 after the US2 test edits and before T017–T019. Run each implementation sequence in ID order. This avoids concurrent edits to the same files.
- T020 and T021 can run together after the stories when their test environments are isolated. Run timing on an uncontended candidate environment after those checks, then complete T023.

## Implementation strategy

Validate US1 as the first independently demonstrable slice. Add US2’s authorized activity selection, URL recovery and FILE1 export. Complete US3 with whole-result totals, unit and measurement semantics, and the independent 51-row comparison. Close technical verification only after the runtime, bilingual browser, workbook and timing checks have recorded results. Employer disposition follows the B06 acceptance workflow.
