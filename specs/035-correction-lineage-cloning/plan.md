# Implementation Plan: Daily Report Correction Lineage and Lossless Cloning

**Branch**: `035-correction-lineage-cloning` | **Date**: 2026-10-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/035-correction-lineage-cloning/spec.md`

## Summary

Implement the approved daily report correction workflow, lossless child-row cloning, cancellation flow, and enriched version lineage. When an approved report is corrected, 100% of its active child rows—including contractor references, crew names, headcount breakdowns, parcels, machinery summaries, general tasks, visits, and incident severities—are duplicated into the new draft version without data loss. Concurrent correction requests are deterministically blocked with HTTP 400 (`correction_already_open`). A safe, two-step cancellation flow allows authorized editors to discard unwanted correction drafts and immediately restore the predecessor approved version as active. The version history panel is enriched with modifier attribution, version-bound correction justifications, and localized Jalali approval timestamps.

## Technical Context

**Language/Version**: Python 3.12 (Django 4.2.11 backend) & TypeScript 5.x / React 18 / React Router 7 (Vite web frontend).

**Primary Dependencies**: Django REST Framework, django-treebeard, pydantic, Lucide React, TanStack Query, Tailwind CSS.

**Storage**: PostgreSQL 16 (port 5433) for primary persistence; Redis (port 6379) for caching and rate-limiting.

**Testing**: pytest (`pytest-django`) for backend service and endpoint tests; Playwright for browser E2E workflows; `pnpm typecheck` (`react-router typegen && tsc`) for frontend type safety.

**Target Platform**: Linux dev environment / web client (desktop/tablet responsive, RTL Persian primary, LTR English secondary).

**Project Type**: Monorepo web service (`apps/api` Django REST backend, `apps/web` React Router frontend).

**Performance Goals**: Cloning and cancellation operations complete under 500ms; version history panel renders in under 200ms.

**Constraints**: Monorepo dependency boundaries; pinned Django 4.2.11; zero schema drift / no extra migrations; server-enforced tenant/project authorization; bilingual Persian/English localization.

**Scale/Scope**: Per-project daily operational records spanning multiple disciplines and report versions.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Evaluation |
|---|---|:---:|
| **I. Server-Enforced Authorization** | All endpoints verify project membership and `edit_reports` / `view_reports` codenames; cross-project cancellation attempts rejected with 403/404. | **PASS** |
| **II. Data Integrity & Domain Consistency** | Declarative `CHILD_CLONE_SPECS` prevents silent column dropping; soft-deleted records excluded; atomic transaction preserves exact state. | **PASS** |
| **III. Bilingual & Locale-Correct Experience** | Approval timestamps formatted via Jalali calendar in Persian locale; dialog and button copy localized; stable error codes. | **PASS** |
| **IV. Explicit, Safe Business Mutations** | Two-step confirmation modal before cancellation; temporary draft soft-deleted; predecessor cleanly restored as `is_current = True`. | **PASS** |
| **V. Minimal Coherent Changes** | Extends existing `correction_service.py`, `daily_report_views.py`, and `ApprovalStatusBar.tsx` without creating parallel models or workflows. | **PASS** |
| **VI. Evidence-Based Verification** | Validation strategy combines schema-drift check, pytest suite, Playwright browser lifecycle run, and typecheck. | **PASS** |
| **VII. Accessible Construction UX** | Cancellation button styled with clear destructive intent; keyboard-accessible confirmation dialog; clear status badges. | **PASS** |

## Project Structure

### Documentation (this feature)

```text
specs/035-correction-lineage-cloning/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Architectural research & decisions
├── data-model.md        # Lineage state machine & clone specifications
├── quickstart.md        # Runnable verification guide
├── contracts/           # Interface contracts
│   └── daily-report-correction-lineage-api.md
├── checklists/          # Quality assurance checklist
│   └── requirements.md
└── tasks.md             # Implementation tasks (/speckit-tasks output)
```

### Source Code Layout

```text
apps/api/core/field_reports/
├── models.py                     # DailyReport, DailyReportCorrectionRequest, child row models
├── serializers.py                # DailyReportVersionSerializer, DailyReportHeaderSerializer
├── daily_report_views.py         # DailyReportCorrectionCancelView, corrections viewset actions
├── urls.py                       # Endpoint routing for correction requests and cancellation
├── services/
│   └── correction_service.py     # CHILD_CLONE_SPECS, open_correction, cancel_correction, list_versions
└── tests/
    ├── test_daily_report_gaps_correction.py  # Lossless clone, concurrency, and cancellation tests
    └── test_daily_report_summary_permissions.py # Authorization and cross-project isolation tests

apps/web/src/
├── app/lib/api/
│   └── daily-reports.ts          # cancelCorrectionRequest API client, fetchReportVersions
└── components/daily_reports/
    └── ApprovalStatusBar.tsx    # Cancel correction button, confirmation modal, enriched version history
```

**Structure Decision**: Monorepo modular extension. All backend logic resides in the established `field_reports` domain and its `correction_service.py`. All frontend workflow logic resides in the established `daily-reports.ts` API module and `ApprovalStatusBar.tsx` component.

## Complexity Tracking

> **No Constitution violations identified. No unnecessary abstractions or extra tables introduced.**

| Component | Standard Approach | Justification |
|---|---|---|
| Child cloning | Declarative `CHILD_CLONE_SPECS` tuple | Avoids brittle ad-hoc attribute assignments while preventing circular foreign-key overhead. |
| Cancellation routing | Dual route registration (canonical + alias) | Ensures both `/correction-requests/...` and `/daily-reports/correction-requests/...` succeed transparently across diverse client integrations. |
