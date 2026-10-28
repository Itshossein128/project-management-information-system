# Implementation Plan: Automated Periodic Reports Rollup, Figure Provenance, and Controlled Override Audit

**Branch**: `041-periodic-reports-rollup` | **Date**: 2026-10-28 | **Spec**: [Feature Specification](spec.md)

**Input**: Feature specification from `specs/041-periodic-reports-rollup/spec.md`

## Summary

This feature extends the project periodic reporting system (`schedule.ProjectPeriodReport`, `PeriodReportFigure`) to:
1. Automatically aggregate labor man-hours, machinery operational/idle hours, material deliveries/consumption, and completed activities from approved daily site reports (`field_reports.DailyReport`) for Saturday–Friday Solar Hijri workweeks.
2. Strictly exclude draft/unapproved daily reports and output explicit localized Persian warnings in the report header for missing or unapproved dates.
3. Establish granular figure provenance (`PeriodReportFigureSourceItem`) protected by referential integrity (`on_delete=models.PROTECT`) preventing deletion of source daily reports or their items.
4. Enforce controlled figure overrides requiring authorization (`edit_reports` or `approve_reports`), mandatory $\ge 10$-character justification, preservation of original `calculated_value`, and audit logging (`PeriodReportFigureOverride`).
5. Support monthly comprehensive chapters (HSE incidents, QC summaries, EVM SPI/CPI) and official serialized release with unique serial numbers (e.g. `REP-PRJ01-140508-M01`).
6. Present structured, accessible Persian tables/cards and footnotes across the web dashboard, replacing raw JSON string dumps.

---

## Technical Context

**Language/Version**: Python 3.12 (pinned Django 4.2.11 backend) & TypeScript / React 18 / React Router 7 (frontend).  
**Primary Dependencies**: Django REST Framework, `jdatetime`, PostgreSQL (`psycopg2`), Redis, `@tanstack/react-query`, `react-date-object`, Tailwind CSS.  
**Storage**: PostgreSQL 16 on port 5433 with relational foreign key protection (`models.PROTECT`) and JSONField attributes.  
**Testing**: `pytest`, `pytest-django`, `@pytest.mark.django_db` on backend; Vite build & typechecking (`pnpm --filter web build`) on frontend.  
**Target Platform**: Linux web server (API on port 8000) and modern desktop/mobile web browsers (Vite dev on port 5173).  
**Project Type**: Monorepo web service (Django REST API in `apps/api/core` + React frontend in `apps/web`).  
**Performance Goals**: Rollup computation across 7–31 daily reports under 150ms; figure provenance breakdown retrieval under 50ms.  
**Constraints**: Zero silent data mutations, zero raw JSON string dumps in UI, strict `PROTECT` on daily source foreign keys, Solar Hijri workweek compliance (Saturday to Friday).  
**Scale/Scope**: Handles multi-contractor site daily reports with hundreds of labor and machinery rows per period.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Principle I: Server-Enforced Authorization and Tenant/Project Isolation**  
   - *Status*: PASS.  
   - All period report endpoints inherit from `ProgressDomainView` verifying project membership and role permissions (`view_dashboard`, `edit_reports`, `approve_reports`). Direct IDOR is prevented by scoping all queries to `project_pk`. Overrides strictly require `edit_reports` or `approve_reports`.

2. **Principle II: Data Integrity and End-to-End Domain Consistency**  
   - *Status*: PASS.  
   - Deletion of source daily records is blocked at the database level by `PeriodReportFigureSourceItem` using `on_delete=models.PROTECT`. Calculated values are permanently preserved in `calculated_value`. Direct mutation of figures via PUT/PATCH is rejected with `figure_immutable`.

3. **Principle III: Bilingual and Locale-Correct Experience**  
   - *Status*: PASS.  
   - Workweeks default to Solar Hijri (Jalali) Saturday to Friday (`شنبه` تا `جمعه`). Warnings are formatted in clear Persian: «گزارش روز [تاریخ شمسی] تأیید نشده است و احجام آن در این گزارش لحاظ نگردید». Dates display in Solar Hijri format.

4. **Principle IV: Explicit, Safe Business Mutations**  
   - *Status*: PASS.  
   - Figure overrides require an explicit non-empty justification of at least 10 characters. All overrides are recorded in `PeriodReportFigureOverride` with timestamp and user. Approved reports are immutable.

5. **Principle V: Minimal Coherent Changes**  
   - *Status*: PASS.  
   - Extends existing `schedule/models.py`, `period_report_service.py`, `period_report_views.py`, and `PeriodReportsPanel.tsx` without introducing parallel duplicate reporting systems.

6. **Principle VI: Evidence-Based Verification**  
   - *Status*: PASS.  
   - Verification will be conducted with pytest against PostgreSQL (`test_ipcas`) and Redis, along with a clean frontend build (`pnpm --filter web build`).

7. **Principle VII: Accessible, Practical Construction-Management UX**  
   - *Status*: PASS.  
   - Raw JSON string dumps in table cells are replaced with structured cards, responsive tables with Persian headers, asterisk indicators for overridden values, and itemized provenance breakdown dialogs.

---

## Project Structure

### Documentation (this feature)

```text
specs/041-periodic-reports-rollup/
├── plan.md              # Implementation plan (this file)
├── research.md          # Architectural research & decisions
├── data-model.md        # Relational schema & entity specifications
├── quickstart.md        # Verification commands & quickstart guide
├── contracts/           # API contracts
│   └── period-reports-api.yaml
└── tasks.md             # Implementation tasks (created in Stage 2)
```

### Source Code Paths

```text
apps/api/core/
├── schedule/
│   ├── models.py                          # ProjectPeriodReport, PeriodReportFigure, PeriodReportFigureSourceItem, PeriodReportFigureOverride
│   ├── migrations/                        # Migration for new fields and models
│   ├── period_report_views.py             # API views: list, create, detail, approve, figure sources, figure override
│   ├── services/
│   │   └── period_report_service.py       # Rollup engine, approval checks, daily report aggregation, overrides, serial number generator
│   └── tests/
│       └── test_period_reports.py         # Comprehensive unit & integration tests
apps/web/src/
├── app/lib/
│   ├── api/
│   │   └── progress.ts                    # API client methods for period reports, approve, provenance sources, overrides
│   └── jalali-utils.ts                    # Solar Hijri Saturday–Friday workweek and month boundary helpers
└── components/
    └── progress/
        └── PeriodReportsPanel.tsx         # Dashboard panel: warnings banner, structured section tables/cards, provenance dialog, override drawer
```

---

## Complexity Tracking

*No constitutional violations identified. Standard idiomatic Django + React architecture utilized throughout.*
