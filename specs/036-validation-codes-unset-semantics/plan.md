# Implementation Plan: Daily Report Validation Codes and Unset Semantics

**Branch**: `036-validation-codes-unset-semantics` (Spec Kit feature identifier; actual checkout: `develop`) | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: `specs/036-validation-codes-unset-semantics/spec.md`

## Summary

Complete the existing daily-report validation and quantity-presentation paths. Retain the four implemented backend error codes, nullable decimal quantities, workflow authorization, and successful transitions. Fix the existing reason-prefixed rejection error.message locally so it matches the spec's exact message. Close the English-label, localized client-feedback, caution-border, general-activity summary, and regression-coverage gaps. Extend existing components and tests rather than introduce another workflow, schema, or quantity model.

Source inspection establishes a partial implementation, not passing behavior. Phase 0 findings are in [research.md](research.md); Phase 1 contracts define the remaining delivery requirements.

## Technical Context

**Language/Version**: Python 3.12 observed in the planning environment; Python 3 project, TypeScript ~5.9, React 19.

**Primary Dependencies**: Django pinned 4.2.11, DRF pinned 3.17.1 in requirements; React Router 7.12, Vite 7, react-i18next/i18next, existing Badge and EditableGrid, Tailwind CSS 4. Declared dependencies are not a claim about installed runtime versions; no dependency upgrades planned.

**Storage**: Existing PostgreSQL DailyReport and DailyReportActivity; Redis required by application/cache/auth. No schema migration, backfill, or data conversion expected.

**Testing**: Existing pytest/pytest-django approval-workflow and activity tests; Playwright via apps/web/e2e/playwright.config.ts; pnpm typecheck. No new frontend test framework.

**Target Platform**: Linux Django service and desktop/mobile web browser, Persian RTL and English LTR, light/dark themes.

**Project Type**: Existing pnpm monorepo web application plus project-scoped REST API.

**Performance Goals**: Preserve existing request/query behavior; badge decisions are constant-time per cell and add no network requests. No new numeric latency target is specified or inferred.

**Constraints**: Explicit zero must survive validation/display; no null-to-zero conversion, permission expansion, lifecycle redesign, calculation change, or global Badge/error-handler restyling. Exact Persian feedback and English `Unset`. Unknown-code fallback retained.

**Scale/Scope**: Four validation identifiers; two workflow actions; activity quantity cells in read-only grids and the daily summary, including general activities' nullable quantity column. Existing editable quantity input remains usable. All FR-001–FR-016 covered by the acceptance matrix in quickstart.md.

## Constitution Check

Pre-research assessment: PASS for bounded extension of existing paths. Post-design assessment: PASS at design level; runtime quality gates remain pending implementation.

- I Authorization/isolation: preserve authenticated project-scoped resolution and existing edit_reports / approve_reports requirements; add denial and cross-project no-mutation checks.
- II Integrity: reuse nullable DecimalField and quantity_measured; preserve zeros, nulls, legacy flags, provenance, imports, exports, PDF, sync and aggregation semantics. No field shape or storage change; no migration needed. Trace those dependent paths during review to ensure presentation changes do not reach calculations or serialization.
- III Bilingual: retain stable error identifiers; add both locale keys for the four codes, exact labels, Accept-Language and browser locale-switch evidence.
- IV Safe mutations: rejected validations must leave status, timestamps, reason and quantities unchanged; preserve existing successful transitions. Use disposable test records only.
- V Minimal changes: reuse lifecycle_errors, API envelope, UnsetQuantityBadge, EditableGrid and existing suites; keep correction/cloning/cancellation/locking outside scope.
- VI Evidence: implement red → minimal fix → green for uncovered acceptance cases; report pytest, typecheck, real API and browser evidence separately. Existing passing cases become retained regression evidence, not artificial red tests.
- VII Accessible UX: compact neutral background with local caution-colored outline, readable text, keyboard-safe editable grid, light/dark and RTL/LTR review. Text conveys meaning independently of color.

No constitutional exceptions or unresolved research questions remain. PASS here approves the design only.

## Project Structure

### Documentation (this feature)

```text
specs/036-validation-codes-unset-semantics/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── workflow-api.md
    └── quantity-ui.md
```

`tasks.md` belongs to the subsequent speckit-tasks phase and is not generated here.

### Source Code (repository root)

```text
apps/api/core/
├── field_reports/
│   ├── models.py
│   ├── serializers.py
│   ├── daily_report_views.py
│   ├── services/lifecycle_errors.py
│   └── tests/test_approval_workflow.py
├── common/mixins.py
└── config/exceptions.py
apps/web/
├── src/app/
│   ├── lib/api-client.ts
│   ├── lib/api/daily-reports.ts
│   ├── locales/{fa,en}.json
│   └── routes/daily-report-view.tsx
├── src/components/daily_reports/
│   ├── ActivityTab.tsx
│   ├── EditableGrid.tsx
│   ├── DailyReportForm.tsx
│   ├── ApprovalStatusBar.tsx
│   ├── UnsetQuantityBadge.tsx
│   └── summary/DailyReportSummaryView.tsx
└── e2e/
    ├── playwright.config.ts
    └── tests/daily-report.spec.ts
```

**Structure Decision**: Keep backend validation in existing request/view paths and lifecycle message catalog. Keep display semantics in the shared quantity badge. Add a narrowly scoped daily-report workflow error-message helper near existing daily-report UI if required to share the four-code translation map across form and view callbacks; avoid changing the global API client's fallback contract. Apply caution styling to UnsetQuantityBadge only, leaving other neutral badges intact.

## Phase 0: Research

Completed in research.md: backend contract and locale behavior, persisted quantity semantics, exact display surfaces, shared localization integration, regression setup and compatibility boundaries. Existing graph used for navigation; source files verified directly because graph output was broad and may be stale. Two economic-model research agents inspected backend/frontend independently.

## Phase 1: Design and Contracts

1. Preserve data shapes and specify the quantity/reason state rules in data-model.md.
2. Preserve HTTP envelope/status/authorization and document exact messages plus client localization in contracts/workflow-api.md. In `_reject`, supply both detail and reason ErrorDetail entries so the existing handler emits the exact message while retaining field errors; leave the global handler unchanged.
3. Reuse the badge in all scoped read-only activity quantity cells, including general activities with no measured flag; change its English label and local caution outline per contracts/quantity-ui.md.
4. Translate only the four scoped workflow codes at both existing daily-report submit/reject error callbacks. Preserve server/generic fallback for unknown codes. Keep any existing client reason-length guard consistent with trimmed backend rules.
5. Extend canonical regression suites for uncovered cases, then validate real API workflow and bilingual browser states per quickstart.md. Do not remove assertions or bypass auto-summary creation to make older E2E fixtures pass.

## Complexity Tracking

No violations or additional architectural layers. No migration, new service, dependency, route, persisted field, or alternate source of truth.

## Planning Verification

Active feature pointer, clean initial worktree, setup_plan JSON, spec, constitution, source files and existing test/config paths inspected. Extension configuration parses successfully and registers no before_plan or after_plan hooks. This run generates design artifacts only; no application tests, database migrations, or browser acceptance runs are claimed.
