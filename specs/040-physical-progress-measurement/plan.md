# Implementation Plan: Physical Progress Measurement, Strict Financial Governance, and Technical Approval Workflow

**Branch**: `040-physical-progress-measurement` | **Date**: 2026-10-28 | **Spec**: [spec.md](file:///home/hossein/Desktop/projects/building-management/specs/040-physical-progress-measurement/spec.md)

**Input**: Feature specification from `specs/040-physical-progress-measurement/spec.md`

## Summary

This feature establishes end-to-end engineering and financial governance across the physical progress lifecycle:
1. **Synchronous Validation Gate**: Synchronously rejects progress entries or daily report activity rows for activities lacking an approved measurement method (`measurement_not_approved`).
2. **Hard 100% Progress Ceiling (No Clamping)**: Rejects progress entries that would push cumulative progress beyond 100% of approved total quantity (`progress_exceeds_100`) without silently truncating to 100%.
3. **Strict Financial Governance in IPC**: Replaces reliance on contractor-claimed actual progress in `contracts/services/ipc_service.py` with strictly supervisor-approved progress (`approved_progress`), blocking unverified payments.
4. **Technical Approval Workflow**: Provides backend enforcement (rejecting photo-only claims with `photo_not_technical_approval`) and frontend UI actions and modals for users with `approve_reports` permission.
5. **Four-Way Progress & Period Quantity**: Computes and exposes `period_quantity` alongside `period_progress_pct`, `cumulative_progress_pct`, `planned_progress_pct`, and `approved_progress_pct`.
6. **Frontend UI Upgrades**: Enhances `MeasurementEditor.tsx` with dynamic weighted milestone grid, unit selector, and evidence rules; integrates it into `activity-drawer.tsx`; adds `period_quantity` column and Technical Approve modal to `ActivityProgressTable.tsx`.

---

## Technical Context

**Language/Version**: Python 3.12 (Django 4.2.11 + Django REST Framework) for API; TypeScript 5 + React 18 / React Router 7 + Vite for Web.  
**Primary Dependencies**: Django, DRF, Celery, React Query (@tanstack/react-query), Tailwind CSS, Lucide React.  
**Storage**: PostgreSQL 16 (on port 5433), Redis (on port 6379 for caching & Celery broker).  
**Testing**: `pytest` + `pytest-django` for API tests; Vite build + Playwright for Web.  
**Target Platform**: Linux server, web browser (Chrome, Firefox, Safari).  
**Project Type**: Monorepo (`apps/api` and `apps/web`).  
**Performance Goals**: Sub-50ms API response for progress validation gates; O(1) synchronous check at serializer boundary; single chronological sweep for progress history and four-way breakdowns.  
**Constraints**: Pinned Django 4.2.11 line; zero data clamping; bilingual Persian/English localization; strict RBAC checks (`approve_reports`, `edit_activities`).  

---

## Constitution Check

*GATE: Checked against `.specify/memory/constitution.md`*

- **I. Server-Enforced Authorization**: PASS. Technical approval endpoint strictly enforces `IsProjectMember` and `approve_reports` permission server-side.
- **II. Data Integrity and End-to-End Consistency**: PASS. Models, serializers, services, and UI align on `approved_progress`, `period_quantity`, and unified enums (`quantity_based`, `weighted_milestones`, `evidence_based`).
- **III. Bilingual and Locale-Correct Experience**: PASS. All error messages have standardized Persian strings, and UI components support Persian RTL and English.
- **IV. Explicit, Safe Business Mutations**: PASS. Over-100% entries are rejected without silent clamping or database corruption; technical approvals leave an immutable audit trail.
- **V. Minimal Coherent Changes**: PASS. Extends established `measurement_service.py`, `ipc_service.py`, `DailyReportActivitySerializer`, `MeasurementEditor.tsx`, and `ActivityProgressTable.tsx`.
- **VI. Evidence-Based Verification**: PASS. Pytest suites with PostgreSQL and Redis, and frontend production build checks will be executed.
- **VII. Accessible Construction-Management UX**: PASS. Clear bilingual error toasts, table column additions, and modal dialogs.

---

## Project Structure

### Documentation (`specs/040-physical-progress-measurement/`)
```text
specs/040-physical-progress-measurement/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── technical-approval.md
│   ├── measurement-validation.md
│   ├── ipc-calculation.md
│   └── progress-rejection.md
└── tasks.md
```

### Source Code
```text
apps/api/core/
├── contracts/services/ipc_service.py          # IPC calculation based on approved_progress
├── contracts/tests/test_ipc_service.py        # IPC tests asserting approved progress monetization
├── schedule/models.py                         # MeasurementMethod choices and ActivityProgress
├── schedule/services/measurement_service.py   # Synchronous validation, 100% check, technical approval
├── schedule/services/progress_service.py      # period_quantity calculation in progress breakdown
├── schedule/measurement_views.py              # Technical approval endpoint enhancement
├── schedule/tests/test_measurement_methods.py # Measurement method unit & milestone tests
├── schedule/tests/test_progress_validation.py # Progress rejection tests
├── field_reports/serializers.py              # DailyReportActivity synchronous validation
└── master_data/ref_views.py                   # Measurement unit listing endpoint

apps/web/src/
├── app/lib/api/progress.ts                    # Updated types and API functions
├── components/progress/MeasurementEditor.tsx  # Dynamic milestones, unit selector, evidence rules
├── components/progress/ActivityProgressTable.tsx # Period quantity column, Technical Approve modal
└── components/activities/activity-drawer.tsx  # MeasurementEditor integration
```

---

## Implementation Strategy

1. **Phase 1: Backend Safety & Contracts**
   - Update `contracts/services/ipc_service.py` to calculate IPC item quantities strictly from `approved_progress` delta and issue warnings for unapproved claimed progress.
   - Update `schedule/models.py` enum definitions to standardize on `quantity_based`, `weighted_milestones`, `evidence_based` with backward-compatible normalization.
   - Enhance `schedule/services/measurement_service.py` with strict 100% validation (`progress_exceeds_100`), exact Persian messages, and technical approval percentage customization with photo-only rejection.
   - Add synchronous measurement and 100% checks in `field_reports/serializers.py` (`DailyReportActivitySerializer`).
   - Add `period_quantity` to `schedule/services/progress_service.py` (`get_activity_progress_breakdown`).
   - Provide unit listing in `master_data`.
   - Run backend test suites.

2. **Phase 2: Frontend Implementation**
   - Update `apps/web/src/app/lib/api/progress.ts` to include `period_quantity`, unified enums, and expanded `technicalApproveProgress` payload.
   - Upgrade `MeasurementEditor.tsx` with dynamic milestones grid (100% sum validation), unit selector, and evidence rules.
   - Integrate `MeasurementEditor` into `activity-drawer.tsx`.
   - Add `حجم دوره` column and Technical Approve action button + modal into `ActivityProgressTable.tsx`.
   - Run `pnpm --filter web build`.

3. **Phase 3: Verification & Polish**
   - Verify all acceptance scenarios and tests.
