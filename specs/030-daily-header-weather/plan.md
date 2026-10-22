# Implementation Plan: Standardized Daily Weather and Temperature

**Branch**: `030-daily-header-weather` (Spec Kit logical branch; actual Git branch: `develop`) | **Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/030-daily-header-weather/spec.md`

**Feature Directory**: `specs/030-daily-header-weather`
**Status**: Phase 0 research and Phase 1 design complete. This command updates design artifacts only; it does not implement source changes, create migrations, or regenerate `tasks.md`.

## Summary

Converge the existing comprehensive 24-hour daily-report implementation on the narrowed specification: retain the five approved weather values and committed legacy normalization, enforce inclusive temperature bounds and effective-state min/max ordering at model, API, and every client write boundary, and preserve optional weather-impact notes through hydration, readback, summary rebuilds, corrections, sync, and the official PDF. The work closes observed gaps in aggregation edge cases, autosave/save blocking, structured error mapping, bilingual shared controls, and the PDF's exact unconditional row; it does not change report creation permissions, shift structure, inactivity behavior, or the broader aggregation lifecycle.

## Technical Context

**Language/Version**: Python 3.12 / Django 4.2.11; TypeScript 5.9 / React 19 / React Router 7

**Primary Dependencies**: Django REST Framework (repository pin 3.17.1; current root virtualenv reports 3.16.1), PostgreSQL, ReportLab 4.2.5, TanStack Query, i18next, IndexedDB via `idb`, Playwright 1.63

**Storage**: PostgreSQL tables for daily reports, weather logs, and specialty reports; browser IndexedDB for cached daily reports and pending offline mutations

**Testing**: pytest + pytest-django against PostgreSQL/Redis; Django migration executor and schema checks; TypeScript typecheck; Node tests for pure offline normalization; Playwright desktop/mobile flows; PDF text extraction plus visual rendering

**Target Platform**: Bilingual Persian/English web application and Django API on Linux; desktop and responsive mobile browsers

**Project Type**: pnpm monorepo with Django API (`apps/api`) and React web client (`apps/web`)

**Performance Goals**: Temperature feedback is produced locally during the edit interaction without an additional request; weather aggregation remains linear in the number of eligible specialty reports and stays within the existing daily-summary response target

**Constraints**: Preserve Django 4.2; use PostgreSQL and Redis for realistic tests; preserve one full-day materialized summary per project/date; keep existing project-level weather overrides authoritative; use stable language-independent values and error codes; preserve queued offline work; show the exact PDF label even when notes are empty; MinIO and RabbitMQ are not required for this feature

**Scale/Scope**: One project summary per project/date; five weather values; three existing server-side weather-bearing entities affected by the shared enum; two daily-report header editing surfaces; one offline report/queue representation; one official PDF header row

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

Pre-research: **PASS**. Post-design: **PASS**. These are design gates, not implementation evidence.

| Principle | Design gate and evidence obligation |
|-----------|-------------------------------------|
| **I — Authorization and isolation** | PASS — no authorization behavior changes. Existing project-scoped retrieval and edit permission checks remain the server boundary; regression tests cover an authorized editor and cross-project denial for modified header/PDF paths. |
| **II — End-to-end consistency** | PASS — the shared vocabulary is traced through database rows, migrations, model choices, serializers, aggregation, API types, daily-report UI, offline cache/queue, corrections, PDF output, docs, seeds/fixtures, and tests. Normalization precedes choice restriction. |
| **III — Bilingual experience** | PASS — machine values and codes remain stable English identifiers; labels, validation guidance, helper text, and accessibility descriptions are present in Persian and English and verified in both directions. |
| **IV — Safe mutations** | PASS — migration work requires backup and pre/post counts; semantic normalization is explicitly lossy and has a restore-based rollback; invalid temperature writes are rejected server-side even when the client is bypassed. |
| **V — Minimal coherent change** | PASS — extend the existing enum, models, serializers, aggregation service, header controls, offline representation, and PDF generator. No parallel weather subsystem or unrelated inactivity/security work is introduced. |
| **VI — Evidence-based verification** | PASS — final-tree evidence is separated into migration, model/API, aggregation, frontend typecheck, browser, offline, PDF extraction/rendering, localization, and relevant regression results. |
| **VII — Accessible operational UX** | PASS — weather buttons have textual names and radiogroup semantics; temperature errors are field-associated and actionable; the notes control is labelled, multiline, keyboard accessible, and usable in RTL/LTR layouts. |

No constitution violation requires a complexity exception.

## Project Structure

### Documentation (this feature)

```text
specs/030-daily-header-weather/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── daily-report-header-weather-api.md
│   └── daily-report-header-weather-ui.md
├── spec.md
└── checklists/requirements.md
```

The existing `tasks.md` was generated from the former broader specification and is intentionally not modified by `/speckit-plan`; it must be regenerated with `/speckit-tasks` before implementation work is scheduled.

### Source Code (repository root; planned touchpoints)

```text
apps/api/core/
├── field_reports/
│   ├── models.py
│   ├── serializers.py
│   ├── pdf.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── correction_service.py
│   │   └── daily_report_aggregation.py
│   ├── migrations/0018_daily_header_weather.py  # committed history; verify, do not edit
│   ├── tests/
│   │   ├── test_spec_01_daily_header_weather.py
│   │   ├── test_daily_report_weather_migration.py
│   │   ├── test_daily_report_summary_metadata.py
│   │   ├── test_daily_report_gaps_correction.py
│   │   ├── test_sync_batch.py
│   │   └── test_weather.py
│   └── ENDPOINTS.md
├── sub_reports/
│   ├── models.py
│   ├── migrations/0004_standardize_weather.py   # committed history; verify, do not edit
│   ├── tests/
│   └── ENDPOINTS.md
└── projects/seeds/full_project.py

apps/web/src/
├── app/
│   ├── lib/
│   │   ├── api/daily-reports.ts
│   │   ├── api/weather.ts
│   │   ├── offlineDB.ts
│   │   ├── offlineWrite.ts
│   │   └── syncService.ts
│   ├── locales/fa.json
│   ├── locales/en.json
│   └── routes/daily-report-view.tsx
├── components/
│   ├── daily_reports/
│   │   ├── DailyReportForm.tsx
│   │   └── ReportHeader.tsx
│   ├── sub_reports/SpecialtyContributionForm.tsx
│   └── weather/
│       ├── weather-icons.tsx
│       ├── weather-log-drawer.tsx
│       └── weather-log-grid.tsx
└── app/lib/__tests__/offlineDB.test.ts

e2e/tests/daily-report-header-weather.spec.ts
```

**Structure Decision**: Treat this as brownfield convergence. Keep `WeatherCondition` as the existing backend vocabulary imported by daily reports, standalone weather logs, and specialty reports. Store weather-impact notes directly on the existing full-day `DailyReport`; do not create another header or note entity. Reuse the established project-scoped API, custom error envelope, offline queue, correction copy, localization catalogs, and PDF generator. The standalone weather and specialty surfaces change only as required to remain compatible with the shared five-value vocabulary. Any migration correction is additive; committed migration history is immutable.

## Phase 0 — Research Outcome

[research.md](./research.md) resolves the shared-enum blast radius, ordered and semantically lossy data normalization, effective-state temperature validation, aggregation/override behavior, summary-owned note preservation, offline compatibility, shared header UX, and PDF proof strategy. No open clarification remains.

## Phase 1 — Design Outcome

- [data-model.md](./data-model.md) — affected entities, fields, invariants, normalization, preservation rules, and migration/rollback boundary
- [contracts/daily-report-header-weather-api.md](./contracts/daily-report-header-weather-api.md) — five-value weather contract, header read/update payloads, stable temperature errors, aggregation behavior, and PDF output
- [contracts/daily-report-header-weather-ui.md](./contracts/daily-report-header-weather-ui.md) — weather controls, immediate temperature validation, notes entry/readback, localization, accessibility, and offline behavior
- [quickstart.md](./quickstart.md) — runnable migration, backend, frontend, browser, offline, PDF, bilingual, and regression verification guide

## Complexity Tracking

> None — no constitution violation requires justification.
