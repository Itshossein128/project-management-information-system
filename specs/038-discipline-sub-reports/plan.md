# Implementation Plan: Discipline Sub-Reports Lifecycle and Validation

**Branch**: `038-discipline-sub-reports` | **Date**: 2026-10-28 | **Spec**: [specs/038-discipline-sub-reports/spec.md](specs/038-discipline-sub-reports/spec.md)

**Input**: Feature specification for discipline daily sub-reports lifecycle, execution percentage validation, empty submission guard, electrical UI separation, mechanical materials, hydrostatic testing QC linkage, contractor labor ledger rollup, and sub-discipline taxonomy bridge.

---

## Summary

This feature closes engineering reporting gaps (G01 through G08) by implementing:
1. Two-decimal `execution_percentage` on activity rows with range enforcement `[0.00, 100.00]` returning code `percent_must_be_between_0_and_100`.
2. Guard blocking submission of empty sub-reports returning `cannot_submit_empty_sub_report`.
3. Discipline-specific layout separation hiding civil/concrete elements from electrical reports, and providing specialized measurement units.
4. Enabling consumable materials for the mechanical unit with quick-pick plumbing/HVAC catalogs.
5. Hydrostatic testing tracking on piping activities with automated linkage to `risk.Inspection`.
6. Automatic rollup of contractor crew person-hours `(foreman + worker) * shift_hours` into `SubcontractorLaborLedgerEntry`.
7. Sub-discipline taxonomy tags (`CIVIL`, `FINISHING`, `PLUMBING`, `HVAC`, `MECHANICAL`) under canonical 6-unit reports.

---

## Technical Context

**Language/Version**: Python 3.12 (Django 4.2.11 pinned runtime) + TypeScript 5.8 (React 19 / React Router 7 / Vite).
**Primary Dependencies**: Django REST Framework, pytest-django, React Router 7, @tanstack/react-query, lucide-react, i18next.
**Storage**: PostgreSQL 16 (port 5433), Redis 7 (port 6379, cache & rate-limiting).
**Testing**: pytest (backend) with `--reuse-db`; Vitest & Playwright (frontend).
**Target Platform**: Linux server, modern web browsers (desktop/tablet site supervisors).
**Project Type**: Full-stack web application (monorepo: `apps/api` and `apps/web`).
**Performance Goals**: Sub-report submit/approve mutation < 250ms p95; material quick-pick selection < 1s.
**Constraints**: Pinned Django 4.2 boundary, bilingual Persian/English error messages and labels, tenant and project IDOR isolation.

---

## Constitution Check

- **I. Server-Enforced Authorization & Isolation**: PASSED. All mutations and queries verify project membership and permissions (`edit_reports`, `approve_reports`, `view_reports`) server-side via `HasProjectPermission` and scoped queries.
- **II. Data Integrity & Domain Consistency**: PASSED. Range validations enforced in DB schema, serializers, and frontend forms. Migrations preserve existing data.
- **III. Bilingual Experience**: PASSED. All new error codes (`percent_must_be_between_0_and_100`, `cannot_submit_empty_sub_report`, `invalid_test_pressure_value`) provide English and Persian translations.
- **IV. Explicit, Safe Business Mutations**: PASSED. Draft -> Submitted -> Approved lifecycle with immutable lock on submitted/approved reports, SoD enforcement, and empty-submission rejection.
- **V. Minimal Coherent Changes**: PASSED. Extends existing `DisciplineSubReportActivity` and `DisciplineSubReport` rather than creating parallel tables. Reuses `risk.Inspection`.
- **VI. Evidence-Based Verification**: PASSED. Test execution with pytest on Postgres/Redis and Vite build typechecks.
- **VII. Accessible Construction-Management UX**: PASSED. Quick-pick palettes and clear input masks for field engineers.

---

## Project Structure

### Documentation (this feature)
```text
specs/038-discipline-sub-reports/
├── plan.md              # Implementation architecture & decisions
├── research.md          # Technical analysis & alternatives
├── data-model.md        # Entities, fields & constraints
├── quickstart.md        # Verification commands
├── contracts/           # API contracts & schemas
│   ├── sub-report-activity-contract.md
│   ├── sub-report-submission-contract.md
│   ├── sub-report-materials-contract.md
│   └── subcontractor-labor-rollup-contract.md
└── tasks.md             # Task breakdown for implementation
```

### Source Code Impact
```text
apps/api/core/
├── sub_reports/
│   ├── models.py                     # Add fields to DisciplineSubReport, DisciplineSubReportActivity, add SubcontractorLaborLedgerEntry
│   ├── migrations/0011_*.py          # Django migration for new fields and model
│   ├── serializers.py                # Serializer validation for execution_percentage, hydrostatic test fields, shift_hours
│   ├── unit_report_serializers.py   # Serializers for unit report views
│   ├── unit_report_services.py      # Empty submit guard, QC linkage call, labor ledger calculation on approval
│   ├── services/
│   │   ├── qc_linkage.py             # Hydrostatic test linkage to risk.Inspection
│   │   └── labor_ledger.py           # Subcontractor labor ledger calculation & queries
│   └── tests/
│       └── test_discipline_sub_reports_lifecycle.py # Comprehensive pytest suite
apps/web/src/
├── app/lib/api/
│   └── unit-reports.ts               # Enable materials for mechanical, payload interfaces, error codes
├── components/department/
│   ├── unit-daily-report-panel.tsx   # Electrical civil filtering, sub-discipline tag display
│   ├── section-activities.tsx        # execution_percentage input, hydrostatic testing toggle & inputs
│   └── section-materials.tsx         # Mechanical materials quick-pick suggestions
└── locales/
    ├── fa.json                       # Persian translations for messages & labels
    └── en.json                       # English translations
```

---

## Complexity Tracking

No constitution violations detected; no complex abstractions required.
