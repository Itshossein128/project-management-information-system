# Implementation Plan: Decision Support AHP Criteria Weighting (Phase 4)

**Feature / Branch identifier**: `021-decision-ahp` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

**Input**: `specs/021-decision-ahp/spec.md`. Spec Kit setup resolves this feature; the actual Git checkout is `develop` at `c5328c4`. Planning does not switch branches.

## Summary

Complete AHP criteria weighting by correcting the existing implementation. The current tree already contains geometric-mean weighting, CI/CR, the AHP execution branch, pairwise editor, weight table, localized messages, and baseline tests. The spec gap table describes an earlier tree; current source evidence and explicit policy interpretations are recorded in [research.md](research.md).

Remaining work: strict input validation; criteria-order output with independent ordinal ranks; explicit matrix draft state; Saaty fraction entry; correct result lifecycle across cases; method-specific history; and authorization/API/browser verification. AHP remains independent of ranking inputs and appends an immutable API execution record even when CR exceeds 0.10. Existing endpoints and JSON fields suffice; no migration or dependency addition is planned.

## Technical Context

**Language/Version**: Python 3.12.3 in the current API environment; TypeScript 5.9.x, React 19.x and React Router 7.12.x from `apps/web/package.json`; Node 25.2.1 locally. Preserve supported project runtimes.

**Primary Dependencies**: Django 4.2.11 compatibility boundary, DRF, drf-spectacular, Python `math`; React Router/Vite, TanStack Query, react-i18next, existing form/table components and Tailwind. No NumPy/SciPy or new test framework.

**Storage**: Existing PostgreSQL `decision_cases` and `decision_runs` tables and JSON fields. Redis is required for normal development/auth. Use configured `DATABASE_URL`; documented native development PostgreSQL port is 5433. No production database changes during planning.

**Testing**: pytest/pytest-django for numerical, validation, API and authorization checks; Node test runner with TypeScript stripping for pure UI rules/source checks; Playwright with `apps/web/e2e/playwright.config.ts` for actual browser behavior; `pnpm typecheck`.

**Target Platform**: Linux-hosted API/browser application; English LTR and Persian RTL. Development ports: API 8000, web 5173.

**Project Type**: pnpm monorepo web application, backend `apps/api/core`, frontend `apps/web/src`, documented HTTP interfaces.

**Performance Goals**: O(n²) time/storage for at most ten criteria. SC-001: representative four-criterion interaction under 30 seconds, measured through a user exercise. No measured millisecond engine guarantee is claimed.

**Constraints**: FR-005 governs actual numeric inputs, exact diagonal 1 and reciprocal product residual <1e-4. Weighting, matrix-vector calculation, lambda, CI and CR stay in `ahp_service.py`; reciprocal form synchronization and formatting are permitted in the UI. Blank judgments remain null. No automatic weight transfer. Reuse actual `view_decision_support`/`edit_decision_support` permissions. All technical unknowns are resolved in research.

**Scale/Scope**: 1–10 criteria, up to 100 cells, four stories, existing project/case/run interfaces, AHP panel and method history. Alternative pairwise ranking, transfer action, DEMATEL/ISM engines, spreadsheets and permanent closure of governance items O05/O06 remain outside scope.

## Constitution Check

Pre-research and post-design assessments apply to the proposed design, not completed implementation proof.

| Principle / constraint | Before research | After Phase 1 design and required evidence |
|---|---|---|
| I — Server authorization/isolation | PASS: retain existing membership/RBAC | PASS: project-scoped case and case/project-scoped run queries; negative create/list/detail/filter tests |
| II — Domain integrity | PASS: existing JSON fields and coherent snapshot | PASS: preserve ranking inputs, independent deep copies, full snapshot/result immutability tests; no migration |
| III — Bilingual UX | PASS: existing i18n retained | PASS: English/Persian fractions, errors, warnings, history, RTL and persistence browser gates |
| IV — Safe mutations | PASS: mutable draft and append-only run API | PASS: invalid execution creates no run; inconsistent success retained; `run_immutable` for mutation actions |
| V — Minimal changes | PASS: reuse engine/components/endpoints | PASS: helper/state repairs, optional list filter; no parallel module/dependency |
| VI — Evidence-based verification | PASS: planning separated from runtime proof | PASS: numerical/API/RBAC/typecheck/source/browser evidence named in quickstart |
| VII — Accessible UX | PASS: existing form/table patterns | PASS: explicit blank input, criterion cell labels, associated errors, keyboard and read-only history |
| Runtime/architecture | PASS: Django 4.2 and pnpm boundaries | PASS: no dependency upgrade/schema alteration/optional integration needed |

**Post-design result**: all design gates pass; no exception required. Implementation and acceptance checks remain to run under [quickstart.md](quickstart.md).

## Phase 0 — Research

Backend/frontend research inspected current source and domain documents. [research.md](research.md) resolves strict types/tolerances, scale behavior, output order/ranks, snapshots, permissions, draft initialization, result lifecycle, history pagination and numerical safety. Existing tests provide only baseline evidence.

## Phase 1 — Design

- [data-model.md](data-model.md): existing entities, validation and draft/run transitions.
- [contracts/ahp-pairwise-matrix.md](contracts/ahp-pairwise-matrix.md): case/run/history interfaces, permissions, strict inputs and errors.
- [contracts/ahp-run-result.md](contracts/ahp-run-result.md): run envelope, compatible snapshot, ordering and numerical contract.
- [contracts/ahp-ui.md](contracts/ahp-ui.md): matrix ownership, entry/history and accessible bilingual behavior.
- [quickstart.md](quickstart.md): runnable commands and planned acceptance scenarios.

## Project Structure

### Documentation (this feature)

```text
specs/021-decision-ahp/
├── spec.md                    # existing input, unchanged
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── ahp-pairwise-matrix.md
│   ├── ahp-run-result.md
│   └── ahp-ui.md
└── tasks.md                   # existing Phase 2 artifact; regenerate separately
```

### Source Code (repository root)

```text
apps/api/core/decision_support/
├── models.py                  # existing schema; no planned change
├── views.py                   # method-filtered scoped history; descriptions
├── serializers.py             # existing envelopes/schema descriptions
├── services/
│   ├── validators.py          # strict AHP inputs
│   ├── ahp_service.py         # ordered results/numerical safety
│   ├── execution_service.py   # existing snapshot/run orchestration
│   └── case_service.py        # targeted saves preserve unrelated inputs
└── tests/
    ├── test_ahp_service.py
    ├── test_ahp_api.py
    └── test_runs_immutability.py
apps/web/src/
├── app/lib/api/decision-support.ts
├── app/routes/project-decision-support.tsx
├── app/locales/{en,fa}.json
└── components/decision-support/
    ├── AhpMethodPanel.tsx
    ├── SquareMatrixEditor.tsx
    ├── square-matrix-rules.ts
    ├── CriteriaWeightTable.tsx
    ├── criteria-weight-rules.ts
    ├── ExecutionHistoryList.tsx
    ├── InputSnapshotViewer.tsx
    ├── ValidationIssueList.tsx
    └── *.test.ts
apps/web/e2e/tests/decision-ahp.spec.ts # new browser acceptance suite
```

**Structure Decision**: extend the existing domain and workspace. Repair pairwise mode without implementing later engines. Existing `tasks.md` reflects older planning and is not completion evidence; regenerate it through the next phase.

## Complexity Tracking

No constitution violations or additional abstraction layers. API immutability is not a database-level append-only guarantee. Historic JSON records retain their original values/order.
