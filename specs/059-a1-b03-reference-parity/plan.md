# Implementation Plan: A.1 B03 Reference-Form Parity

**Feature** `059-a1-b03-reference-parity`  
**Date** 2026-11-20  
**Specification** [Approved B03 specification](spec.md)  
**Source** [B03 work-package prompt](../../output/a1-requirements-2026-11-18/speckit-prompts/03-b03-reference-parity.md)

## Summary

Repair reference-form parity in daily and discipline exports. Use one version-aware projection of persisted report data for the daily header and section values shared by the screen, FILE 4, and PDF. Extend the existing renderers for print and locale parity, preserve FILE 5 and FILE 6 column contracts, and add a date-range workbook and a standalone PDF for every supported discipline. B03 verifies export behavior using B01's labeled synthetic fixture and targeted variants. B05 owns independent reconciliation and B06 owns final employer acceptance.

## Technical Context

- **Runtime and dependencies** — Python 3.12 in the workspace, pinned Django 4.2.11, Django REST Framework, openpyxl, ReportLab, Arabic reshaping and bidi helpers. React Router 7, Vite, and TypeScript use the existing authenticated API clients and locale dictionaries.
- **Storage** — PostgreSQL report versions, unit reports, child rows, provenance, status events, and project permissions. Redis supports existing caches. Generate downloads on demand. Persist additional evidence only where an existing authoritative record cannot supply a required value.
- **Testing** — pytest with PostgreSQL and Redis, openpyxl inspection, PDF page rendering and visual print inspection, web typecheck, and bilingual authenticated browser checks. Attachment verification requires a working storage environment.
- **Target and scale** — Web and API on the existing Linux deployment. Plan for more than 50 rows, wide multilingual tables, and a bounded date-range workload. Proposed initial cap is 31 inclusive calendar days, configurable and subject to representative render checks. Resolve versions in one scoped selection and prefetch relations so lookups do not multiply with rows. Date-range rendering makes no per-sheet network calls.

## Constitution Check

| Principle | Pre-design gate | Post-design check |
| --- | --- | --- |
| I. Authorization and isolation | Resolve projects, reports, units, and source rows server-side. | [Contract](contracts/exports.md) specifies read permission, tenant and unit scope, observation limits, and behavior for hidden items. |
| II. Data integrity | Carry B01 semantics and B02 immutable versions through every output. | [Data model](data-model.md) preserves stable identifiers and source references and defines compatibility for any new evidence fields. |
| III. Bilingual experience | Keep permission codes and canonical values stable across locales. | Contract covers request locale and date formats. [Quickstart](quickstart.md) covers RTL and LTR presentation, Persian font, and local timestamps. |
| IV. Safe operations | Downloads must be authorized and read-only. | Contract specifies bounded and validated range selection, localized errors, and no export-driven report updates. |
| V. Minimal changes | Reuse exporters, clients, data contracts, and workflow. | [Research](research.md) records why shared sheet rendering and output projections fit the existing entry points. |
| VI. Verification | Define distinct evidence for code, runtime, output, and browser checks. | Quickstart maps all eight success criteria to checks on the final implementation. |
| VII. Accessible UX | Use existing controls and feedback patterns. | Daily list and unit panel designs include keyboard access, localized progress and errors, and visible version selection. |

Design gate passes for review across I–VII. No constitution exception is proposed.

## Project Structure

- `apps/api/core/field_reports/` — `daily_report_views.py`, `urls.py`, `services/data_contract.py`, `services/form_profiles.py`, `services/weather_forecast.py`, `shiraz_file4_excel.py`, `pdf.py`, `excel_safety.py`, and focused tests.
- `apps/api/core/sub_reports/` — `unit_report_views.py`, `urls.py`, `shiraz_subreport_excel.py`, existing unit and QC services, a unit PDF renderer, and focused tests.
- `apps/web/src/app/` — daily list and detail routes, existing daily and unit API clients, and FA/EN locale dictionaries. `apps/web/src/components/department/unit-daily-report-panel.tsx` hosts the discipline download action.
- `e2e/tests/` — authenticated, scoped export and print-readiness journeys. Existing B01 and B02 suites remain regression gates.

## Design sequence and traceability

| Design slice | Specification and evidence |
| --- | --- |
| Version-scoped headers and profile, DEL-01 | US1, FR-001–009, DEF-B03-01/02/08. Use B01 versioned numbering, worked shifts, weather and profile resolution. Add provenance-backed start and end evidence where the existing duration record cannot supply them. |
| Operational sections, DEL-01 | US2, FR-010–017, DEF-B03-05/06/07. Preserve measured zero, nullable values, structured rows, source identity and receipt boundaries. Expose authorized QC and attachment details, localize HSE at render time. |
| Print, signatures, and text fidelity | US3, FR-018–023, DEF-B03-03/04. Share sheet print settings, keep live workbook formulas and literal user text, render paginated PDFs and version-scoped actor attribution. |
| Discipline and range outputs, DEL-02–04 | US4, FR-024–027. Preserve FILE 5/6 schema and add unit PDF plus current-approved date-range workbook. Exercise the same read policy in every direct download and source drill-down. |
| Release evidence | SC-001–008. Record backend, binary output, visual, API, and browser evidence separately. Hand off parity artifacts to B05 and leave acceptance with B06. |

## Planning artifacts

- [Research and design decisions](research.md)
- [Data model and compatibility](data-model.md)
- [Download and presentation contract](contracts/exports.md)
- [Validation quickstart](quickstart.md)

## Dependencies

- [B01 contract v1.0.0](../057-a1-b01-data-contract/contracts/daily-report-data-contract.v1.json), [B01 T030 handoff](../057-a1-b01-data-contract/tasks.md#b03-handoff-from-convergence), and [B01 QA](../../output/a1-b01-stage5-qa-verification-2026-11-19.md).
- [B02 version and lineage contract](../058-a1-b02-version-integrity/contracts/version-integrity-api.md), [implementation evidence](../058-a1-b02-version-integrity/implementation-evidence.md), and [B02 QA](../../output/a1-b02-stage5-qa-verification-2026-11-19.md).
