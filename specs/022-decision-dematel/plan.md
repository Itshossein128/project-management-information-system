# Implementation Plan: Independent DEMATEL Criterion Influence Analysis

**Git Branch**: `develop` (unchanged) | **Feature ID**: `022-decision-dematel` | **Date**: 2026-10-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/022-decision-dematel/spec.md`.

`setup_plan.py --json` resolves the persisted feature and reports `BRANCH: 022-decision-dematel` as its feature alias. The actual Git branch remains `develop`; no branch hook is configured. Feature resolution is anchored by `.specify/feature.json`.

## Summary

Deliver independent criterion influence analysis using a directed 0–4 matrix, zero self-influence, source-defined maximum-row normalization and total relations, followed by D/R/prominence/relation and server-assigned roles. Reject missing/invalid/all-zero/singular/unreliable input without a successful record. Preserve separate immutable runs, ranking inputs, bilingual usability, and project authorization.

Extend the existing Django domain and React workspace, using already-declared NumPy for a guarded right solve. No new models, migrations, endpoints, permissions or runtime dependencies are planned. Add explicit DEMATEL editor behavior and criterion-operation metadata while preserving AHP's existing reciprocal and rename rules. The implementation must use TDD; this plan does not implement application behavior.

The planning refresh also requires minimal permission/pending/coordinator adapters in existing AHP, SAW and TOPSIS panels. Their independent PATCH→POST actions must participate in the same-case mutation boundary; no calculation or method-input semantics change.

## Technical Context

**Language/Version**: Python 3.12.3 research runtime; pinned Django 4.2.11; TypeScript 5.9-compatible project; React 19 / React Router 7.

**Primary Dependencies**: Existing DRF, NumPy (`numpy>=1.26.0`, installed 1.26.4), React Query, i18next, shared form/table components. No dependency installation/upgrade required.

**Storage**: PostgreSQL existing `DecisionCase` JSON inputs and `DecisionRun` immutable JSON snapshots/results. Redis supports application cache/rate limits. DEMATEL does not require MinIO, RabbitMQ or a worker.

**Testing**: pytest/pytest-django against PostgreSQL; Node strip-types helper/key/source tests; TypeScript check; actual Playwright Chromium desktop scenarios in EN and FA. Independent rational/Decimal fixtures for numerical expectations.

**Target Platform**: Existing project-scoped browser application and Linux Django service; desktop keyboard usability in LTR/RTL.

**Project Type**: pnpm monorepo web application, Django API and React frontend.

**Performance Goals**: SC-006: at least 95% of valid n≤10 runs visible within two seconds under documented normal supported conditions; measured request-to-result, not entry speed. No timing success claimed from the small numerical research exercise.

**Constraints**: Preserve Django 4.2 compatibility, existing dirty AHP work, project isolation, append-only run history, method independence, recoverable drafts, server-only mathematics, active-language feedback/dates, no weight auto-feed or conversion action. Implement explicit numerical policy and no substitute result for undefined analysis.

**Scale/Scope**: 1–10 criteria and actual n×n matrix. One entered judgment set per run. No surveys, aggregation, causal diagrams, ISM integration, exports/imports or new optimistic revision protocol.

## Constitution Check

*Design gates assessed before research and rechecked after contracts. PASS here describes design compliance, not delivered behavior.*

| Principle/gate | Before research | After design | Required evidence during implementation |
| --- | --- | --- | --- |
| I. Authorization/project isolation | PASS: reuse existing scoped routes and permissions | PASS: all reads/writes/runs scoped; locked authoritative case | PostgreSQL permission, view-only and foreign case/run tests; browser control gates |
| II. Data integrity/end-to-end consistency | PASS: extend existing JSON field/run record | PASS: strict execution, finite JSON, draft isolation, immutable result contract | API round trips, stale/concurrent case tests, frozen history, migration dry-run |
| III. Bilingual locale correctness | PASS: existing translation systems | PASS: EN/FA cells/errors/roles/dates/RTL contracts | Locale key checks and real browser EN/FA plus language switching |
| IV. Safe mutations | PASS: existing editable drafts and append-only history | PASS: no new destructive action; explicit failure/retry and pending coordinator | Failed save/run appends no success; preserved draft; no duplicate click or stale result |
| V. Minimal coherent changes | PASS: no duplicate domain or permission | PASS: additive matrix mode/helpers, no AHP algorithm/rename change | Existing Decision Support/AHP regression; no unrelated edits |
| VI. Evidence-based verification | PASS: TDD and layered evidence planned | PASS: quickstart names each check and its proof limits | Real red/green logs, final suites, exits, browser traces, performance sample |
| VII. Accessible practical UX | PASS: shared editors and feedback | PASS: keyboard focus, named issue location, directed axes | Multi-character typing/caret, reorder/remap and error-focus browser cases |
| Runtime/dependency boundary | PASS: pinned Django; existing NumPy | PASS: no dependency or model change | Record versions; no dev-deps install; migration dry-run |

No constitutional exception is required. No unresolved design clarifications remain; O07–O09 working policies are recorded in the specification assumptions and numerical/result contract.

## Project Structure

### Documentation (this feature)

```text
specs/022-decision-dematel/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── dematel-inputs-api.md
    ├── dematel-result.md
    └── dematel-ui.md
```

`tasks.md` belongs to the subsequent speckit-tasks phase and is not generated here.

### Source Code (repository root)

```text
apps/api/core/decision_support/
├── models.py                              # Existing fields; no planned edits
├── serializers.py                         # Existing generic field/run exposure
├── views.py                               # Existing scoped API; schema text update only
├── services/
│   ├── validators.py                      # New strict DEMATEL execution/draft guard
│   ├── case_service.py                    # DEMATEL draft isolation/recovery
│   ├── execution_service.py               # DEMATEL-only locked dispatch
│   └── dematel_service.py                 # New pure calculation service
├── ENDPOINTS.md                            # Existing docs; update engine support
└── tests/
    ├── test_dematel_service.py             # New independent references/guards
    ├── test_dematel_api.py                 # New persistence/auth/errors/concurrency
    ├── test_ahp_api.py                     # Mixed-history fixture compatibility
    ├── test_runs_immutability.py           # Extend frozen-run checks
    └── test_no_math_in_views.py            # Extend architectural guard
apps/api/core/locale/fa/LC_MESSAGES/
├── django.po
└── django.mo
apps/web/src/
├── app/lib/api/decision-support.ts         # DEMATEL result and draft types/guard
├── app/routes/project-decision-support.tsx # Draft/current-run/coordinator/permission state
├── app/locales/{en,fa}.json
└── components/decision-support/
    ├── DematelMethodPanel.tsx              # New isolated save/run/result flow
    ├── DematelResultTable.tsx              # New server-result presentation
    ├── AhpMethodPanel.tsx                  # Permission/pending/coordinator adapter only
    ├── SawMethodPanel.tsx                  # Permission/pending/coordinator adapter only
    ├── TopsisMethodPanel.tsx               # Permission/pending/coordinator adapter only
    ├── dematel-input-rules.ts              # New pure directed/remap helpers
    ├── dematel-input-rules.test.ts          # New helper regressions
    ├── no-client-dematel-math.test.ts       # New source boundary audit
    ├── NamedListEditor.tsx                 # Optional change metadata; focus preserved
    ├── SquareMatrixEditor.tsx             # Add explicit DEMATEL mode
    ├── square-matrix-rules.ts              # Retain AHP behavior; reuse where appropriate
    ├── ValidationIssueList.tsx             # DEMATEL named-cell focus support
    ├── validation-issues.ts                # Existing parser + DEMATEL codes
    ├── InputSnapshotViewer.tsx             # Frozen DEMATEL inputs/results
    ├── ExecutionHistoryList.tsx            # Reuse locale-aware generic history
    └── i18n.keys.test.ts                   # Include new components/dynamic keys
apps/web/e2e/tests/decision-dematel.spec.ts   # New bilingual real-browser scenarios
```

**Structure Decision**: Extend the existing Decision Support domain and route; place formulas in one backend service. Existing generic case/run storage and history remain the host. Optional named-list operation metadata avoids a global criterion-ID redesign and keeps AHP behavior independent.

## Delivery Sequence and TDD Boundaries

1. **Strict execution and draft contract**: Failing name/shape/type/scale/diagonal tests; minimal validator and draft finite-storage/isolation guards; green focused tests. Include malformed persisted draft recovery and ranking preservation.
2. **Pure calculation**: Failing independent chain/decimal/sparse/tiny-scale/n=10/balanced references and undefined/reliability cases; implement guarded NumPy solve and server role classification; green numerical tests. Do not derive test expectations by calling the production calculation.
3. **Authoritative persisted run**: Failing API tests; add DEMATEL-only atomic reload/row-lock helper before stale selected-method checks, then compute/snapshot/append. Include deselection, deletion, stale instances and controlled PostgreSQL concurrency. Preserve legacy stubs and other method paths.
4. **Directed editor and remapping**: Failing pure helper and actual EN/FA keyboard tests; add mode-specific zero diagonal, directed edit and operation-index remap. Existing AHP defaults/reciprocity/rename tests must stay green.
5. **Workspace/result integration**: Failing browser/API-type tests; add panel, server-result table, permissions, localized errors and same-case save/run coordinator. Adapt AHP/SAW/TOPSIS save/run controls to the shared permission and pending boundary without changing their calculations. Test a delayed other-method save followed by attempted DEMATEL/global save, plus view-only mixed-method controls. Snapshot-based display and pending/case-switch/stale-result tests precede fixes.
6. **Frozen review and final evidence**: Failing history/locale/legacy-stub scenarios; extend viewer and keys. Update endpoint docs. Run focused green tests, then full Decision Support backend/helper/browser regressions and migration/type checks. Record limitations and SC-006 timing distribution separately.

Task generation should preserve these red→green dependencies, concrete files/contracts and regression boundaries. Every task must have evidence appropriate to its behavior; source audits and checkbox completion do not replace numerical/API/browser proof.

**Planning refresh**: Re-ran feature resolution on 2026-10-11 and reviewed the existing design against the unchanged application worktree. Backend audit passed; frontend audit identified the shared-panel adapters above. Constitution design gates remain satisfied. Implementation and performance acceptance are still unverified.
