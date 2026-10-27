# Implementation Plan: Daily Report Lifecycle Lock

**Branch**: `034-daily-lifecycle-lock` | **Date**: 2026-10-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/034-daily-lifecycle-lock/spec.md`

## Summary

Close the identified daily-report lifecycle gaps without changing the established approval model: make correction copies lossless for the in-scope rows, make correction cancellation safe and usable, expose complete version lineage, normalize workflow error contracts, and keep unset quantities visually and semantically distinct from explicit zero. Extend existing correction, workflow, serializer, client, and daily-report UI paths; introduce no parallel reporting subsystem and no persistence schema.

## Technical Context

**Language/Version**: Python 3.12 host runtime with Django 4.2.11 and Django REST Framework 3.17.1; TypeScript 5.9, React 19, and React Router 7.12

**Primary Dependencies**: Django REST Framework, PostgreSQL driver, pytest/pytest-django; React Query, i18next, Tailwind/shadcn UI primitives, Playwright

**Storage**: PostgreSQL daily-report, correction-request, and child-row records; Redis is required by normal API/test configuration. No migration is expected because the required rows and persisted fields already exist.

**Testing**: Focused Django pytest API/service tests, Playwright daily-report browser checks, TypeScript typecheck, migration-drift check, and manual bilingual/Jalali verification

**Target Platform**: Browser-based construction-management web application with Django API on Linux deployment/runtime environments

**Project Type**: pnpm monorepo web application (`apps/api` + `apps/web`)

**Performance Goals**: Preserve current daily-report interaction responsiveness; version history must load its lineage metadata without one additional database query per version.

**Constraints**: Server-side project authorization is the authority; correction/open/cancel transitions must be transactionally serialized; approved records remain immutable; API codes stay language-independent while messages and dates are localized; explicit zero must never be converted to unset or vice versa.

**Scale/Scope**: One report-lineage lifecycle across the existing daily-report API and screens: correction cloning/cancellation, version metadata, three workflow error cases, one submit-readiness validation, and quantity presentation in activity editing, read-only, and summary surfaces.

## Constitution Check

### Pre-design gate — PASS

| Principle / gate | Plan response |
|---|---|
| I. Authorization and project isolation | Reuse project-scoped paths and server `edit_reports`/`view_reports` checks. Cancellation lookup remains project-scoped; tests cover cross-project and view-only refusal. |
| II. Data integrity and end-to-end consistency | Clone behavior, serializers, client types, screens, error contracts, and browser/API tests change together. No model field is needed; run migration-drift verification to prove that boundary. |
| III. Bilingual and locale-correct UX | Keep stable error codes separate from localized messages; use the established Jalali formatter and test Persian presentation. |
| IV. Safe mutations | Open/cancel actions are server-authorized, confirmed in UI where destructive, and guarded/locked against stale or concurrent lifecycle transitions. |
| V. Minimal coherent changes | Extend current correction service, viewset/serializers, client, status bar, activity grid, and summary. No new workflow, route family, or duplicate quantity model. |
| VI. Evidence-based verification | Require focused backend contracts, browser behavior, migration-drift, and static checks. Record the known unrelated frontend typecheck baseline separately. |
| VII. Accessible practical UX | Use labelled confirmation controls, non-colour-only unset text, existing date/localization utilities, and stable browser test identifiers. |

**Gate result**: PASS. The material lifecycle risk is concurrent state transition handling; the design requires locking the authoritative report/lineage before checking or changing current-state flags.

## Project Structure

### Documentation (this feature)

```text
specs/034-daily-lifecycle-lock/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── daily-report-lifecycle-api.md
│   └── daily-report-lifecycle-ui.md
└── tasks.md                 # Generated later by /speckit-tasks
```

### Source Code (repository root)

```text
apps/
├── api/core/field_reports/
│   ├── models.py
│   ├── serializers.py
│   ├── daily_report_views.py
│   ├── services/correction_service.py
│   └── tests/
│       ├── test_daily_report_gaps_correction.py
│       ├── test_approval_workflow.py
│       ├── test_daily_report_gaps_status_unset.py
│       └── test_daily_report_summary_permissions.py
└── web/
    ├── src/app/lib/api/daily-reports.ts
    ├── src/components/daily_reports/
    │   ├── ApprovalStatusBar.tsx
    │   ├── DailyReportForm.tsx
    │   ├── ActivityTab.tsx
    │   ├── EditableGrid.tsx
    │   └── summary/DailyReportSummaryView.tsx
    ├── src/app/routes/daily-report-view.tsx
    └── e2e/tests/daily-report.spec.ts
```

**Structure Decision**: Use the existing Django `field_reports` domain and React daily-report feature surfaces. The server remains the source of lifecycle truth; the client composes existing project-scoped endpoints and reflects returned state.

## Implementation Approach

1. Harden correction-service invariants: lock/reload the authoritative current report, preserve in-scope semantic child-row fields, emit a coded 400 for an already-open correction, and verify/lock cancellation participants before restoration.
2. Extend lineage reads efficiently: return modifier name, result-bound correction reason, and approval time in a bounded lineage query; never attribute a correction reason to the predecessor version.
3. Normalize submit/reject validation at the workflow boundary. Permit a measured activity with blank quantity during editing, but enforce measured-without-quantity on submit with the approved code/message; preserve numeric zero.
4. Extend the typed client and existing status bar: discover the open correction request for the current draft, confirm cancellation, invalidate dependent views, and navigate to the returned predecessor id. Render lineage metadata through the shared Jalali date-time formatter.
5. Add one reusable activity quantity display rule for read-only/editable display and summary rendering: unset/not-measured shows a labelled muted warning state, while explicit zero remains numeric.
6. Prove authorization, lineage, lifecycle, zero/unset, UI navigation, and localization behavior with the validation matrix in `quickstart.md`.

## Complexity Tracking

No constitution violations or additional architectural complexity require justification.

## Constitution Check — Post-design

**Result: PASS.** The Phase 1 artifacts retain server-enforced authorization, model-aware cloning without a speculative migration, bounded lineage retrieval, bilingual/Jalali presentation, confirmed recoverable cancellation, and a verification ladder that distinguishes API, browser, schema, and static evidence.
