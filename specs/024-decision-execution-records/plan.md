# Implementation Plan: Traceable Decision Execution Records

**Branch**: `develop` (actual Git branch, unchanged) | **Date**: 2026-10-13 | **Spec**: [spec.md](spec.md)

**Feature Directory**: `specs/024-decision-execution-records`

**Input**: Feature specification from `specs/024-decision-execution-records/spec.md`, based on `docs/decision-support/08-execution-records.md`.

Setup used `.venv/bin/python .specify/scripts/python/setup_plan.py --json`. Its `BRANCH` value was the derived feature name `024-decision-execution-records`; `git branch --show-current` confirms `develop`. No branch hook is configured or branch change performed.

## Summary

Complete the shared execution-record lifecycle and readable historical review while preserving existing engines and saved analyses. Reuse `DecisionCase`/`DecisionRun`, their authorized routes and the established history components. Put all existing method dispatch, case PATCH and narrowly scoped soft deletion behind the same authoritative parent-row locking boundary; make fixed-set pagination deterministic. Extend the read-only viewer for ranking inputs/results and completed DEMATEL records, safely classify incomplete legacy data, and separate historical selection from current method output. Generalize ISM's validated save–execute–bounded-recovery behavior across the four live method panels using the existing per-case coordinator.

No schema migration, dependency installation, engine change, historical backfill, manual weight transfer, merged ranking or new navigation product is planned. DEMATEL remains a placeholder until feature 022; completed fixture review is not live engine acceptance. Source/design research is complete in [research.md](research.md).

## Technical Context

**Language/Version**: Verified API Python 3.12.3 / Django 4.2.11, Node 25.2.1; frontend TypeScript 5.9 dependency line.

**Primary Dependencies**: Existing Django 4.2/DRF, PostgreSQL, React 19, React Router 7.12/Vite, TanStack Query v5, existing i18next/Tailwind/table components. Keep installed dependency boundaries; no framework upgrade or new package.

**Storage**: Existing PostgreSQL JSON fields and UUID relations; Redis supports local authentication/rate limits. No new persisted entity or schema field. Actor identity is the existing protected user relation, display name is presentation.

**Testing**: pytest/pytest-django with real PostgreSQL transaction tests and existing RBAC catalog fixture; Node strip-types helper tests; Playwright's dedicated `apps/web/e2e/playwright.config.ts`, Chromium desktop, one worker, real backend fixtures and EN/FA interactions. Typecheck/migration/locale checks supplement behavioral proof.

**Target Platform**: Existing bilingual project web workspace and Django API; local Linux PostgreSQL/Redis setup. No external compute, file storage or worker dependency for this feature.

**Project Type**: pnpm monorepo web application with Django backend; extend the existing Decision Support domain only.

**Performance Goals**: SC-004: prepared fixed 100-record case, ten-row pages, at least 95% of history page/detail selections within two seconds per locale/category. Measure selection-to-readable-display with actual page/run identity, document fresh/cached samples and failures; no prior calculation timing substitutes for history review timing.

**Constraints**: Active project/case scoping; immutable existing runs; pure engine math stays in services; one consistent locked persisted input per POST; preserve raw recoverable unrelated drafts; response guards before callbacks/release; ten-second recovery read with no POST retry; captured case isolation; no exactly-once, revision or cross-request PATCH→POST atomicity promise.

**Scale/Scope**: Existing five method IDs, four live engines and one DEMATEL placeholder; at most ten criteria/alternatives; fixed 100-record acceptance fixture. All 19 FRs, eight SCs and 21 acceptance scenarios are within the bounded shared-record feature. Broader Phase 7/manual-transfer/module-wide sign-off is excluded.

## Constitution Check

*GATE: Passed before Phase 0 research and re-evaluated after Phase 1 design. No exceptions.*

| Principle | Pre-research gate | Post-design evidence / obligation |
| --- | --- | --- |
| I. Authorization/isolation | PASS: existing project view/edit access and parent scope retained | [API contract](contracts/execution-api.md) double-scopes record reads/mutations and locks active parent; real bypass/viewer tests required |
| II. Data integrity | PASS: reuse entities, no historical rewrite or migration | [Data model](data-model.md) consistent transaction/snapshot, targeted locked writes and immutable records; migration dry run required |
| III. Bilingual experience | PASS: reuse current locales and date formatting | [UI contract](contracts/history-ui.md) EN/FA named review, errors, recovery, dates and real switching/keyboard proof |
| IV. Safe mutations | PASS: only explicit authorized save/run and current deletion semantics | No automatic POST retry, no record overwrite/delete or new retention policy; local disposable tests, no production-like actions |
| V. Minimal coherent changes | PASS: extend current domain/UI/coordinator | One shared four-panel lifecycle, existing tables/guards; no second model, state framework, new math or unrelated cleanup |
| VI. Evidence-based verification | PASS: TDD and separate final-tree proof | [Quickstart](quickstart.md) behavioral red/green, PostgreSQL lock observation, final backend/helpers/browser/type/schema/locale evidence and raw timing |
| VII. Accessible practical UX | PASS: existing native controls/table patterns | Clear current/history separation, keyboard selection, named frozen axes, localized empty/unavailable/read-failure states |

Existing unrelated type errors do not justify unrelated source edits or a green typecheck claim. Requirements/checklist files are protected; planning/design quality is not application acceptance. Preserve Django 4.2 and pnpm/API boundaries. No code gate violation was introduced by design.

## Project Structure

### Documentation (this feature)

```text
specs/024-decision-execution-records/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── execution-api.md
│   ├── result-review.md
│   └── history-ui.md
└── tasks.md                         # Future speckit-tasks output; not created here
```

### Source Code (repository root; proposed edit/test paths)

```text
apps/api/core/decision_support/
├── models.py                        # Existing entities; no schema edit planned
├── serializers.py                   # Existing envelope/provenance; preserve shape
├── services/
│   ├── execution_service.py          # Common authoritative lock/reload/append
│   └── case_service.py               # Locked targeted merge/validation/update
├── views.py                         # Stable ordering and case-specific locked delete
├── ENDPOINTS.md                      # Lifecycle/history/compatibility guidance
└── tests/
    ├── conftest.py                   # Existing reused transaction RBAC fixture
    ├── test_execution_records.py     # New behavior/concurrency/pagination coverage
    └── test_runs_immutability.py     # Extend full equality and zero-append proof
apps/web/src/
├── app/lib/api/
│   ├── decision-support.ts           # Local safe transport/record guard integration
│   └── decision-support.test.ts      # Existing actual response boundary tests
├── app/routes/project-decision-support.tsx
├── app/locales/{en,fa}.json
└── components/decision-support/
    ├── execution-record-rules.ts     # New pure guards and historical classifiers
    ├── execution-record-rules.test.ts
    ├── execution-recovery.ts         # New bounded read helper extracted from ISM
    ├── execution-recovery.test.ts    # Actual async/cache/error ownership tests
    ├── useDecisionExecution.ts       # New thin shared lifecycle; no math
    ├── InputSnapshotViewer.tsx       # Named frozen review and safe legacy states
    ├── RankingSnapshotTable.tsx     # New read-only named ranking inputs if needed
    ├── CriteriaMetricsTable.tsx      # New completed DEMATEL presentation if needed
    ├── ExecutionHistoryList.tsx      # Existing accessible selection/provenance
    ├── {Saw,Topsis,Ahp,Ism}MethodPanel.tsx
    └── RankingResultTable.tsx / CriteriaWeightTable.tsx / IsmLayerList.tsx
apps/web/e2e/tests/
├── decision-execution-records.spec.ts # New shared-record EN/FA scenarios/timing
├── decision-ahp.spec.ts               # Retained regression suite
└── decision-ism.spec.ts               # Retained recovery/pending regression suite
```

**Structure Decision**: Keep persisted changes in the existing backend domain and user state in the existing route. Pure unknown-safe structural rules and bounded recovery helpers are separate only to permit reuse and direct behavior tests. New presenters are small read-only views of stored data, not duplicate input widgets. File names above are proposed implementation targets, not claims that unbuilt files exist. Do not edit engine formulas, common project-delete behavior or source decision-support documents.

## Phase 0 — Research Completed

[Research decisions R1–R11](research.md) resolve storage, locking, pagination, new-response versus legacy handling, four-panel recovery reuse, frozen presentation, request ownership and evidence boundaries. Read-only research agents independently checked backend/frontend source. Graph discovery was verified against current files; primary Django and TanStack references support transaction/cache decisions. All technical questions are resolved; no clarification marker or constitution exception remains.

## Phase 1 — Design Completed

- [Data model](data-model.md): reused entities, snapshot/output invariants, transaction and frontend states, compatibility and migration boundaries.
- [Execution API](contracts/execution-api.md): existing routes/permissions/envelope, authoritative execute/PATCH/delete, ordering, strict response/read guards and uncertainty.
- [Stored result review](contracts/result-review.md): readable named ranking/criteria inputs and stored outputs, partial legacy classification, independent methods and no derivation.
- [History UI](contracts/history-ui.md): navigation generations, historical/current separation, per-case lifecycle and visible bounded recovery.
- [Quickstart](quickstart.md): runnable future validation commands, TDD slices, access/locale/legacy scenarios and SC-004 measurement.

Post-design constitution gate: PASS for all seven principles; no new storage dependency, destructive policy, engine coupling or unapproved scope.

## Planned TDD Delivery Sequence

1. **Authoritative recording foundation (US1)**: Add stale-instance, method-removal/deletion, synchronized PostgreSQL wait and targeted PATCH/delete tests before common locking changes. Retain already-correct ISM and engine tests as regressions. Verify required input validation, one append, full frozen input/output equality and raw/normalized weights. No scientific formula refactor.
2. **Deterministic history and safe record boundary (US2)**: Add fixed-ID equal-time pagination and malformed/partial record tests before ordering/guards. New mutation guards remain stricter than legacy classification. Reuse existing actor metadata and permissions; no migration.
3. **Readable frozen review (US2/US3)**: Add EN/FA ranking history and disagreement/tie/legacy tests before viewers. Remove historical injection into current results. Keep AHP stored row order and ISM interpretation; DEMATEL fixed fixtures prove presentation only. Then add delayed detail after page/filter/case transition tests before unified generation transitions and read-error state.
4. **Shared guarded operation (US4)**: Add meaningful global-save and SAW/TOPSIS/AHP malformed-success/lost-POST red cases before extraction/adapters. Reuse existing ISM behavior; all four panels keep captured payload, active callback guards and per-case tokens. Await validated visible history recovery through success/failure/timeout; never automatic POST retry. Expand mixed-method reselect/A→B→A and case B isolation before considering the slice complete.
5. **Final proof**: Relevant full Decision Support backend/helper suites, migration dry run, typecheck attribution, locale checks if changed, new records plus existing AHP/ISM browser suites, real access/keyboard/locales and fresh SC-004 timing. Retain red/green logs and final requirements/scenario reconciliation in implementation-time evidence. Preserve requirements/design/checklist and earlier dirty work; no commit/push/deploy is implied.

Tests precede the associated implementation. Keep shared-file changes sequential; independently authored backend and pure-rule tests can be prepared separately during the tasks phase. Record genuine regressions rather than manufacturing red for currently correct code. Full detailed task decomposition belongs to the next command.

## Requirement and Outcome Mapping

| Spec coverage | Planned design and proof |
| --- | --- |
| FR-001–FR-004 / SC-001 / US1 | Existing independent engines inside common active-parent lock; strict method selection, rejection/append and concurrent persisted-state proof |
| FR-005–FR-007 / SC-002 / US1–US2 | Deep-copy snapshots, normalized ranking weights, repeated explicit distinct append, full earlier-record equality and immutable routes |
| FR-008 / SC-004 / US2 | Scoped `(-time,-id)` fixed-set pages/filter counts and 100-record browser page/detail timing |
| FR-009–FR-011 / SC-003 / US2 | Read-only named snapshot/output presenters and safe selected detail ownership |
| FR-012 / SC-008 / US3 | Separately labeled stored SAW/TOPSIS disagreement/ties, no blending or automatic weight transfer |
| FR-013 / SC-003 / US2 | Unknown-safe partial legacy states, missing normalized weights, placeholders, AHP stored rows and DEMATEL future shape |
| FR-014–FR-016 / SC-005–SC-006 / US4 | Case/save/completed guards, shared bounded recovery, current output clearing, held-response/no-repeat/visible-filter/page/case-isolation proof |
| FR-017 / SC-007 / US4 | Real membership/view/edit/admin and project/parent/record scoped access; zero prohibited mutations/disclosures |
| FR-018 / SC-007 / US4 | EN/FA keyboard selection/axes/dates/errors and stored-value equality after locale switches |
| FR-019 / US3 + edge cases | Existing interim ranking precision/order/ranks, AHP/DEMATEL/ISM interpretations and no historical rewrite |

## Risks and Verification Limits

- Row locks protect one server POST's persisted input/eligibility, not browser revision intent across PATCH/POST. Explicit retry after uncertainty may append another result; absence on page one never proves no commit.
- Fixed-set page completeness does not freeze pages during concurrent new appends. UUID tie order is deterministic only, not time chronology.
- Shared adapters touch existing AHP/ISM pending/failure behavior; retain their complete suites and meaningful late-case/timeout/malformed-response regressions after the final change.
- Completed DEMATEL history examples cannot close feature 022 engine acceptance. Incomplete older history stays visible with unavailable sections; no backfill.
- Planning performed source/runtime/document checks only. Previously retained test counts/type errors/timings are baseline context. This feature's application and timing acceptance remain unexecuted.

No complexity exception is needed. Mandatory before/after-plan hook checks find `.specify/extensions.yml` absent. Planning ends with design artifacts; `tasks.md` and implementation evidence are intentionally future phase outputs.
