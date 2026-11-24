# Implementation Plan: A.1 / B04 Filters, Result Sets, and Totals

**Spec Kit feature** `060-a1-b04-filters-totals` | **Date** 2026-11-22 | [Specification](spec.md)

## Summary

Complete daily-report filters and make the Activity Master Log, whole-result totals, and Shiraz FILE1 use the same authorized selection. Apply B01's same-row rule through a correlated existence check against eligible activity rows attached to the summary version. Keep date and status on the report. Extend the existing B02 activity selection, calculate totals in PostgreSQL before slicing the page, and drive navigation and export from the same filter state.

## Technical Context

- **Stack** Python 3.12 workspace, Django 4.2.11, DRF, PostgreSQL, Redis, openpyxl, React Router 7, TypeScript, Vite and React Query.
- **Verification** Django pytest, frontend typecheck and authenticated Playwright. Read-only schema impact review and targeted query/timing evidence.
- **Platform** Existing web and API services with browser support in Persian RTL and English LTR. Keep project-local date semantics.
- **Performance** SC-004 requires visibility within one second of approval and visible filtered rows and totals in under one second. Record both measurements independently. Use at least 51 eligible rows with explicit page size 50 for pagination parity.
- **Scope** Existing report and activity rows, project dimensions, API, URLs, FILE1 and bilingual reporting. B05 owns wider independent reconciliation. B06 owns same-release employer acceptance.

## Constitution Check

- **I** Retain server-side project membership and report/read-export policies on all entry points. Resolve references within the authorized project before serving options, cache entries, totals or files.
- **II** Preserve B01 source/measurement semantics and B02 version eligibility across both views and relevant exports. Use additive response fields and avoid a schema migration in the planned design.
- **III** Use existing calendar utilities and bilingual labels/errors. Verify RTL/LTR, restored dates and localized unset values.
- **IV** Use authorized read and download actions. Exercise approval and correction against isolated test data.
- **V** Extend existing queryset, rollup representations, workbook builder, routes and typed clients.
- **VI** Collect backend, browser, workbook parity and timing evidence independently. Keep results tied to the tested revision.
- **VII** Use accessible existing filter controls, clear loading/error states and a visible summary that stays consistent across pages.

**Pre-design and post-design result** All seven principles are satisfied by the design. Implementation and runtime evidence gates remain open. No complexity exception is required.

## Project Structure

- **Backend** `apps/api/core/field_reports/daily_report_views.py`, `report_views.py`, `services/activity_log.py`, `shiraz_file1_excel.py`, existing model/provenance queries and `field_reports/tests/`.
- **Frontend** `apps/web/src/app/routes/{daily-reports-list,project-activity-log}.tsx`, `app/lib/api/{reports,daily-reports}.ts`, and existing FA/EN locale files.
- **Browser verification** `e2e/tests/` using project-backed fixtures and existing authentication setup.

## Design Sequence

1. Freeze the filter and response semantics in the [interface contract](contracts/filters-and-totals.md). Add independent fixtures for same-row and split-row matching, project isolation, current/preview/history policies and page-invariant totals.
2. Extend the daily list with the one-row existence predicate. Extend the activity selection with required dimensions and preserve existing aliases. Return server-computed aggregates, with one measurement rule for row serialization, grouping and FILE1. Reuse the project cache version and verify its invalidation follows committed approval and relevant correction or cancellation changes. Refetch stale client results for those changes.
3. Connect both views to canonical URL state. Preserve browser history, reset paging on filter changes, and share activity filter serialization between list and download. Render server totals and localized measurement/headcount labels.
4. Execute the [verification guide](quickstart.md), including authenticated navigation, FILE1 row identities and separate timing checks. Hand off dataset identifiers, build identity and evidence paths for B05/B06.

## Planning Artifacts

- [Research and design decisions](research.md)
- [Data model and selection rules](data-model.md)
- [API, export and browser contract](contracts/filters-and-totals.md)
- [Verification quickstart](quickstart.md)
