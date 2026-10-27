# Implementation Plan: Daily Report Auto-Rollup & Activity Master Log Sync

**Branch**: `039-auto-daily-rollup` | **Date**: 2026-10-28 | **Spec**: [specs/039-auto-daily-rollup/spec.md](specs/039-auto-daily-rollup/spec.md)

**Input**: Feature specification from `specs/039-auto-daily-rollup/spec.md`

## Summary

This feature unifies and solidifies the automated daily report rollup engine, guarantees date-mediated navigation without 404 errors via automatic draft shell provisioning, differentiates labor headcounts by contractor, locks derived collections with standardized error codes, aligns the Activity Master Log with the 12-column Shiraz Excel Sheet 1 format with real-time cache invalidation upon report approval, preserves site manager weather overrides with explicit audit metadata, provides clear visual feedback on reporting completeness, and formats localized Jalali timestamps with aggregated material sums.

## Technical Context

**Language/Version**: Python 3.12 (Django 4.2.11 + DRF 3.15 backend), TypeScript 5.6 + React 18 / React Router 7 frontend  
**Primary Dependencies**: Django, DRF, jdatetime, Redis (cache backend), TanStack React Query, Tailwind CSS, Lucide React  
**Storage**: PostgreSQL 16 (port 5433, UUID primary keys), Redis (port 6379, rate limiting & response caching)  
**Testing**: pytest + pytest-django (backend in `apps/api/core`), Vite build + Vitest / Playwright (frontend)  
**Target Platform**: Linux server, modern web browsers (Chrome/Firefox/Safari)  
**Project Type**: Full-stack web application (Monorepo with `apps/api` and `apps/web`)  
**Performance Goals**: `< 2s` rollup response time on calendar date navigation, `< 1s` Activity Master Log cache invalidation upon report approval  
**Constraints**: Server-enforced project authorization (`view_reports`, `edit_reports`, `approve_reports`), strict tenant isolation, bilingual UX (Persian default, English fallback), non-breaking migrations, pinned Django 4.2 boundary  
**Scale/Scope**: Construction projects with daily sub-reports across 3+ engineering disciplines and dozens of subcontractors  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principle I (Server-Enforced Authorization & Isolation)**: All `/by-date/`, child collection, and `/activity-log/` endpoints enforce project-scoped permission checks (`view_reports`, `edit_reports`, `approve_reports`). Auto-provisioning occurs strictly within the authorized project context.
- [x] **Principle II (Data Integrity & End-to-End Consistency)**: Contractor references and names are persisted in the database model `DailyReportLabor`, propagated through serializers, and validated in tests. Derived rows are protected from direct mutation drift.
- [x] **Principle III (Bilingual & Locale-Correct Experience)**: All error messages, status banners, table headers, and timestamps support localized Persian presentation (`aggregated_at_jalali`, bilingual error messages).
- [x] **Principle IV (Explicit, Safe Business Mutations)**: Derived rows cannot be mutated out-of-band; manager weather overrides require explicit flags and are tracked with `weather_source='overridden_by_manager'`.
- [x] **Principle V (Minimal Coherent Changes)**: Extends existing `DailyReportLabor`, `ensure_daily_report_summary`, `activity_log`, and `IncompletenessBanner` without introducing parallel duplicate architectures.
- [x] **Principle VI (Evidence-Based Verification)**: All changes verified by running pytest suites against PostgreSQL and Redis, and frontend production builds.
- [x] **Principle VII (Accessible, Practical Construction UX)**: Eliminates 404 date navigation traps; clearly presents missing vs. complete reporting states with color-coded banners.

## Project Structure

### Documentation (this feature)

```text
specs/039-auto-daily-rollup/
├── plan.md              # This file
├── research.md          # Technical decisions and alternatives
├── data-model.md        # Entities, constraints, and relationships
├── quickstart.md        # Verification commands and test procedures
├── contracts/           # API and behavior specifications
│   ├── by-date-api.md
│   ├── derived-collection-lock.md
│   └── activity-log-sync.md
└── tasks.md             # Implementation tasks
```

### Source Code

```text
apps/api/core/
├── field_reports/
│   ├── models.py                     # DailyReportLabor additions (contractor_ref, contractor_name)
│   ├── serializers.py                # Serializer updates (labor contractor fields, materials summary totals)
│   ├── daily_report_views.py         # by_date auto-provisioning, derived_collection_read_only code
│   ├── report_views.py               # ActivityLogView & ActivityLogFilterOptionsView updates
│   ├── services/
│   │   ├── __init__.py               # approve_report cache purge hook
│   │   ├── daily_report_aggregation.py # Bucketing by contractor, weather hierarchy & override, jalali timestamp
│   │   └── activity_log.py           # Activity log query filtering & serialization (discipline, parcel)
│   ├── migrations/                   # Migration for DailyReportLabor contractor fields
│   └── tests/                        # Pytest tests for all acceptance criteria

apps/web/src/
├── app/
│   ├── lib/api/
│   │   ├── reports.ts                # ActivityLog API client types (source_discipline, parcel)
│   │   └── daily-reports.ts          # DailyReport types
│   └── routes/
│       └── project-activity-log.tsx  # Activity Master Log table & filters (discipline, parcel)
└── components/
    └── daily_reports/
        ├── DailyReportForm.tsx       # Auto-summary lock / redirect
        └── summary/
            ├── IncompletenessBanner.tsx # Green complete banner & orange missing banner
            └── DailyReportSummaryView.tsx # Manager override indicator & contractor labor display
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
