# Implementation Plan: Automated Project Daily Report Summary

**Branch**: `develop` (actual Git branch; unchanged) | **Date**: 2026-10-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/028-auto-daily-report-summary/spec.md`  
**Feature Directory**: `specs/028-auto-daily-report-summary`  
**Spec Kit logical feature key**: `028-auto-daily-report-summary` (setup JSON `BRANCH`; no Git branch created/switched)

**Status**: Phase 0 research and Phase 1 design complete. Design artifacts only; no `tasks.md`, source edits, or migrations in this invocation.

## Summary

Make the project-level **گزارش روزانه** a **materialized, auto-rebuilt summary** of that day’s **specialty-unit / رشته** reports (`DisciplineSubReport` and related specialty contribution rows), presented in a sectional layout matching the reference Excel day sheet. Remove the project daily-report **«گزارش جدید»** create path. Specialty flows remain the authoring surface; project daily report is view + summary-level approvals/management notes. Derived labor/activity/material/concrete rows are read-only on the summary.

## Technical Context

**Language/Version**: Python 3.x / Django 4.2.11 (API); TypeScript + React 19 + React Router 7 + Vite (`apps/web`)

**Primary Dependencies**: Django REST Framework, PostgreSQL, TanStack Query, i18next, existing `field_reports` + `sub_reports` apps, Jalali display helpers

**Storage**: PostgreSQL — reuse `daily_reports` (+ child tables) as the summary shell; `discipline_sub_reports` (+ activities, and additive specialty contribution tables as needed); provenance FKs/flags on derived rows

**Testing**: pytest (`field_reports`, `sub_reports` aggregation + permissions); `pnpm typecheck`; browser check of list (no create), date open, Excel-like view, specialty submit → summary refresh (fa/en)

**Target Platform**: Bilingual web SPA + Django API (Linux-hosted)

**Project Type**: pnpm monorepo (`apps/api` + `apps/web`)

**Performance Goals**: Aggregation for one project-day completes well under interactive thresholds (target &lt; 2s for typical day with ≤10 specialty reports and hundreds of activity rows); list by date remains paginated

**Constraints**: Project tenancy / IDOR-safe queries; no Django upgrade; preserve existing DailyReport approval/PDF/progress hooks where possible; do not invent blank project daily reports via UI create; offline create-queue for project daily reports must not reintroduce blank create (see research)

**Scale/Scope**: One summary per project per calendar date (shift=`full`); N discipline sub-reports per day; Excel sectional UI parity (not pixel-perfect export in MVP)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-research and post-design: **PASS** (design gates only; not runtime proof).

| Principle | Gate |
|-----------|------|
| **I — Authorization / isolation** | PASS — Aggregation and summary reads stay project-scoped; existing report permissions; specialty entry permissions unchanged |
| **II — Data / domain integrity** | PASS — Single DailyReport shell per date; rebuild replaces derived rows with clear provenance; approvals/management notes not wiped by rebuild |
| **III — Bilingual** | PASS — Section labels and empty/incomplete banners in fa/en; stable API status/discipline codes |
| **IV — Safe mutations** | PASS — No blank create; derived child writes rejected; summary metadata patch explicit; rebuild idempotent |
| **V — Minimal coherent change** | PASS — Extend existing DailyReport + DisciplineSubReport rather than a parallel summary store |
| **VI — Evidence** | PASS — Plan requires pytest aggregation cases, typecheck, browser/locale checks |
| **VII — Accessible UX** | PASS — Date browse + read-only derived tables; clear incomplete-state messaging |

No unjustified violations → Complexity Tracking empty.

## Project Structure

### Documentation (this feature)

```text
specs/028-auto-daily-report-summary/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── daily-report-summary-api.md
│   └── daily-report-summary-ui.md
├── spec.md
└── checklists/requirements.md
```

`tasks.md` is **not** created here — use `/speckit-tasks` next.

### Source Code (repository root; proposed touchpoints, not edits)

```text
apps/api/core/
├── field_reports/
│   ├── models.py                 # provenance fields; management_opinion; optional flags
│   ├── services/
│   │   └── daily_report_aggregation.py   # ensure + rebuild summary from specialty sources
│   ├── daily_report_views.py     # disable/redirect create; by-date ensure; read-only child writes
│   ├── serializers.py            # summary payload + incompleteness + contribution meta
│   └── tests/                    # aggregation, permissions, no-create, rebuild
├── sub_reports/
│   ├── models.py                 # specialty contribution extensions if required
│   ├── services.py               # hook rebuild on submit/update/delete/reject
│   ├── serializers.py / views.py
│   └── tests/
└── locale/fa/LC_MESSAGES/        # messages as needed

apps/web/src/
├── app/routes/
│   ├── daily-reports-list.tsx      # remove Plus/create; open-by-date
│   ├── daily-report-view.tsx       # Excel-like sectional summary layout
│   ├── daily-report-form*.tsx      # retire blank create; edit → summary metadata only or redirect
│   └── project-sub-reports.tsx     # remain authoring surface
├── components/daily_reports/       # summary sections; incompleteness banner; hide derived editors
├── app/lib/api/daily-reports.ts    # by-date ensure; drop create from list UX
└── locales/fa.json / en.json
```

**Structure Decision**: Keep `DailyReport` as the persisted project-day summary; rebuild derived children from `DisciplineSubReport` (+ extended specialty contributions). Do not introduce a second summary table.

## Phase 0 — Research outcome

[research.md](./research.md) resolves: materialize-vs-virtual, specialty source of truth, Excel layout mapping, create-path removal, weather/site reconciliation, incompleteness, offline create, verification.

## Phase 1 — Design outcome

- [data-model.md](./data-model.md) — entities, rebuild rules, state  
- [contracts/daily-report-summary-api.md](./contracts/daily-report-summary-api.md) — ensure-by-date, rebuild triggers, read-only derived rows  
- [contracts/daily-report-summary-ui.md](./contracts/daily-report-summary-ui.md) — no create button, Excel sections, specialty entry unchanged  
- [quickstart.md](./quickstart.md) — end-to-end validation scenarios  

## Complexity Tracking

> None — no constitution violations requiring justification.
