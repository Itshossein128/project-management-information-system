# Implementation Plan: Daily Report Header and Weather Controls

**Branch**: `030-daily-header-weather` (Spec Kit logical branch; actual Git branch remains `develop`) | **Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/030-daily-header-weather/spec.md`

**Feature Directory**: `specs/030-daily-header-weather`
**Status**: Phase 0 research and Phase 1 design complete. This command created design artifacts only; it did not create `tasks.md`, source changes, or migrations.

## Summary

Standardize the shared daily-weather vocabulary to the five Shiraz-form values, safely normalize legacy rows, add bounded/cross-field temperature validation, persist weather-impact notes and conditional inactive-site reasons, and carry both fields through correction, aggregation, offline sync, detail UI, and official PDF output. Keep the project daily report as one full-day auto-summary: a read-only `GET by-date` remains available to viewers, while only `POST by-date` with `edit_reports` may ensure/rebuild the shell; raw collection creation stays blocked. Add an accessible pre-save confirmation for positive activity quantities on inactive days before either online mutation or offline queueing.

## Technical Context

**Language/Version**: Python 3.12 / Django 4.2.11; TypeScript 5.9 / React 19 / React Router 7

**Primary Dependencies**: Django REST Framework (requirements pin 3.17.1; current local venv reports 3.16.1), PostgreSQL, ReportLab, TanStack Query, i18next, Radix UI dialogs, IndexedDB via `idb`

**Storage**: PostgreSQL (`daily_reports`, `weather_logs`, `discipline_sub_reports`); browser IndexedDB (`offline_daily_reports`, `offline_queue`) for supported offline writes

**Testing**: pytest + pytest-django against PostgreSQL/Redis; Django migration executor/checks; TypeScript typecheck; Playwright desktop/mobile/offline interaction tests; PDF text extraction with Poppler for content assertions

**Target Platform**: Bilingual Persian/English web application and Django API on Linux; desktop and responsive mobile browsers

**Project Type**: pnpm monorepo with Django API (`apps/api`) and React web client (`apps/web`)

**Performance Goals**: Header validation remains interactive; date ensure/rebuild remains within the existing target of under 2 seconds for a typical project-day (up to 10 specialty reports and hundreds of rows); no additional request is required merely to display validation choices

**Constraints**: Preserve Django 4.2; PostgreSQL and Redis are required for realistic tests; no blank project-report creation; one `shift=full` summary per project/date; derived rows remain protected; stable error codes and machine values remain language-independent; legacy and pending offline weather values must be normalized before rejection rules take effect; MinIO/RabbitMQ are not required for this feature

**Scale/Scope**: Three persisted weather-bearing entities, two API/UI weather surfaces, one project summary per project/date, five allowed weather values, five inactivity reasons, and one guarded execution-activity mutation path

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

Pre-research: **PASS**. Post-design: **PASS**. These are design gates, not implementation evidence.

| Principle | Design gate and evidence obligation |
|-----------|-------------------------------------|
| **I — Authorization and isolation** | PASS — `GET by-date` is project-scoped/read-only; `POST by-date` requires `edit_reports`; raw create remains blocked; permission and cross-project tests are mandatory. |
| **II — End-to-end consistency** | PASS — shared weather changes cover database rows, serializers, aggregation, standalone weather logs, summary UI, specialty UI, offline cache, correction copies, PDF, seed data, documentation, and tests. Data normalization precedes choice restriction. |
| **III — Bilingual experience** | PASS — stable values/codes remain English identifiers while all new labels, errors, warning text, and recovery guidance use `fa`/`en` locale keys and `Accept-Language`. |
| **IV — Safe mutations** | PASS — migration requires backup/count verification; inactive activity confirmation happens before online/offline persistence; cancellation is mutation-free; viewer ensure is denied before any write. |
| **V — Minimal coherent change** | PASS — extend the existing shared enum, models, serializers, aggregation service, `ReportHeader`, grid save pipeline, and PDF generator; no parallel report or weather subsystem. |
| **VI — Evidence-based verification** | PASS — final-tree migration, focused pytest, regression pytest, typecheck, PDF extraction, Playwright, locale, permission, concurrency, and offline evidence are separated in quickstart. |
| **VII — Accessible operational UX** | PASS — field-level errors, fixed full-day header, conditionally revealed reason selector, keyboard/focus-safe dialog, and cancel/confirm recovery path are contract requirements. |

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

`tasks.md` is intentionally not created by `/speckit-plan`; use `/speckit-tasks` after reviewing this design.

### Source Code (repository root; planned touchpoints)

```text
apps/api/core/
├── field_reports/
│   ├── models.py
│   ├── serializers.py
│   ├── daily_report_views.py
│   ├── pdf.py
│   ├── views.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── correction_service.py
│   │   └── daily_report_aggregation.py
│   ├── migrations/0018_daily_header_weather.py
│   ├── tests/
│   │   ├── test_spec_01_daily_header_weather.py
│   │   ├── test_daily_report_by_date.py
│   │   ├── test_daily_report_summary_permissions.py
│   │   ├── test_daily_report_summary_metadata.py
│   │   ├── test_sync_batch.py
│   │   └── test_weather.py
│   └── ENDPOINTS.md
├── sub_reports/
│   ├── models.py
│   ├── serializers.py
│   ├── migrations/0004_standardize_weather.py
│   ├── tests/
│   └── ENDPOINTS.md
└── projects/seeds/full_project.py

apps/web/src/
├── app/
│   ├── lib/api/daily-reports.ts
│   ├── lib/api/weather.ts
│   ├── lib/offlineDB.ts
│   ├── lib/offlineWrite.ts
│   ├── lib/syncService.ts
│   ├── locales/fa.json
│   ├── locales/en.json
│   └── routes/
│       ├── daily-reports-list.tsx
│       └── daily-report-view.tsx
└── components/
    ├── daily_reports/
    │   ├── ReportHeader.tsx
    │   ├── DailyReportForm.tsx
    │   ├── ActivityTab.tsx
    │   ├── InlineGridTab.tsx
    │   └── EditableGrid.tsx
    ├── sub_reports/SpecialtyContributionForm.tsx
    └── weather/
        ├── weather-icons.tsx
        └── weather-log-drawer.tsx

e2e/tests/daily-report-header-weather.spec.ts
```

**Structure Decision**: Keep `WeatherCondition` as the single backend vocabulary shared by daily reports, standalone weather logs, and specialty reports. Keep `DailyReport` as the persisted full-day summary and extend its existing header metadata rather than creating another header table. Reuse the existing API error envelope, permission classes, PDF generator, localization files, and grid mutation pipeline.

## Phase 0 — Research Outcome

[research.md](./research.md) resolves the shared-enum blast radius, migration ordering and rollback boundary, partial-update validation, derived-inactive transitional state, permission/mutation split, concurrent ensure locking, shared header UI, activity confirmation with autosave/offline semantics, PDF verification, and offline cache compatibility. No open clarification remains.

## Phase 1 — Design Outcome

- [data-model.md](./data-model.md) — fields, allowed values, invariants, normalization, state transitions, and offline representation
- [contracts/daily-report-header-weather-api.md](./contracts/daily-report-header-weather-api.md) — date access, header payloads, errors, summary aggregation, weather surfaces, and PDF contract
- [contracts/daily-report-header-weather-ui.md](./contracts/daily-report-header-weather-ui.md) — full-day header, conditional reason, validation, warning dialog, localization, and offline behavior
- [quickstart.md](./quickstart.md) — migration, API, PDF, browser, permission, concurrency, offline, and bilingual validation guide

## Complexity Tracking

> None — no constitution violation requires justification.
