# Implementation Plan: Independent ISM Criterion Layering

**Git Branch**: `develop` (unchanged) | **Feature ID**: `023-decision-ism` | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

**Input**: `specs/023-decision-ism/spec.md`, derived from `docs/decision-support/07-ism.md`.

`setup_plan.py --json` resolves `.specify/feature.json` and reports `BRANCH: 023-decision-ism` as the feature alias; the actual Git branch is `develop`. No branch-creation hook is configured.

## Summary

Deliver independent ISM from 1–10 ordered criteria and an explicit directed binary matrix. Compute Boolean identity inclusion, full transitive closure, active-set reachable/intersection layer extraction and maximal non-singleton mutual groups on the server. Accept all-zero, single-criterion and cyclic networks; preserve direct judgments and append immutable runs. Present numbered layers/groups, not weights, ranking or deletion advice.

Extend existing Decision Support storage, APIs, permissions, localization and history. Add a dedicated binary editor and operation-aware ISM remapping while preserving AHP rename/reciprocal rules. Supply minimal permission/pending/coordinator adapters in AHP, SAW and TOPSIS for all same-case saves/runs. DEMATEL is unimplemented and is not a dependency. No new models, migrations, endpoints, permissions or runtime dependencies are planned.

Use TDD during implementation. This phase delivers design only and claims no implementation acceptance.

## Technical Context

**Language/Version**: Python 3.12.3 current API runtime; pinned Django 4.2.11; TypeScript 5.9; React 19 / React Router 7.

**Primary Dependencies**: Existing DRF, React Query, i18next and shared form/table components. Pure Python binary calculation; no NumPy/graph dependency or upgrade.

**Storage**: Existing PostgreSQL `DecisionCase.ism_matrix` and immutable `DecisionRun.input_snapshot/result`; Redis for normal cache/rate limits. No worker, RabbitMQ or MinIO requirement for ISM.

**Testing**: PostgreSQL pytest/pytest-django, literal exact references and independent traversal oracle, controlled row-lock tests, Node strip-types helper/key/source checks, TypeScript checks, real Playwright Chromium EN/FA flows.

**Target Platform**: Existing project browser workspace and Linux Django service; keyboard interaction in LTR/RTL.

**Project Type**: pnpm monorepo web application (`apps/api`, `apps/web`).

**Performance Goals**: SC-008: ≥95% of valid n≤10 requests show completed layers within two seconds under documented supported normal conditions. O(n³) work/O(n²) storage does not establish request/API/render latency; measure it separately.

**Constraints**: Stable row→column identity; zero distinct from missing; direct diagonal 0/1 valid; server-only analysis; immutable provenance; method-specific validation; recoverable drafts; project access; EN/FA text/dates/focus; pending/case-switch isolation; preserve existing dirty AHP work and DEMATEL artifacts.

**Scale/Scope**: Maximum ten criteria, actual n×n matrix and one judgment set per run. No diagram/graph editing, method chaining, DEMATEL conversion, weights/transfer, ranking changes, surveys, import/export or optimistic revision protocol.

## Constitution Check

*Evaluated before research and rechecked after design. PASS means design compliance; implementation evidence remains outstanding.*

| Principle/gate | Before research | After design | Required implementation evidence |
| --- | --- | --- | --- |
| I. Authorization/isolation | PASS: reuse scoped access | PASS: view/edit permissions and project/case lock | Real denied/view-only/cross-project API/browser checks |
| II. Integrity/consistency | PASS: existing JSON/run entities | PASS: finite drafts, strict execution, aligned axes, frozen snapshot | API round trips, stale/concurrent cases, frozen history, migration dry-run |
| III. Bilingual experience | PASS: existing EN/FA systems | PASS: states/errors/layers/groups/dates/direction contract | Key coverage and real EN/FA keyboard/language-switch flows |
| IV. Safe mutations | PASS: additive analysis | PASS: no destructive action; coordinator/failure recovery | Failed PATCH prevents POST; zero partial runs, no overlap/late case results |
| V. Minimal changes | PASS: reuse domain/routes | PASS: one service, binary editor, narrow adapters | AHP/SAW/TOPSIS regression; no DEMATEL dependency/algorithm change |
| VI. Evidence | PASS: TDD/layered checks | PASS: categories and SC coverage explicit | Meaningful red/green, final exits/traces and timing distribution |
| VII. Accessible UX | PASS: standard controls | PASS: native selects, named focus, operation remap | Typing/caret, pairs/remap/error focus in both locales |
| Runtime boundary | PASS: pinned Django/PostgreSQL | PASS: no new dependency/model | Versions, migration dry-run, no full dev-deps upgrade |

No constitutional exception or unresolved design clarification remains. O10 is bounded by the specification's working presentation policy. Browser/API/performance acceptance remains unverified.

## Project Structure

### Documentation

```text
specs/023-decision-ism/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── ism-inputs-api.md
    ├── ism-result.md
    └── ism-ui.md
```

`tasks.md` is produced by speckit-tasks, not this phase.

### Source Code (planned changes, repository root)

```text
apps/api/core/decision_support/
├── models.py, serializers.py              # Existing storage/exposure, no new fields
├── views.py, ENDPOINTS.md                  # Preserve scope; truthful engine/schema docs
├── services/
│   ├── validators.py                      # ISM strict/draft guards
│   ├── case_service.py                    # Matrix-only isolation/raw recovery
│   ├── execution_service.py               # ISM-only atomic scoped reload/dispatch
│   └── ism_service.py                     # New pure closure/layer/group service
└── tests/
    ├── test_ism_service.py                 # New independent references/invalid inputs
    ├── test_ism_api.py                     # New persistence/access/stale/concurrency
    ├── test_runs_immutability.py           # Frozen-run regression
    └── test_no_math_in_views.py            # ISM architecture boundary
apps/api/core/locale/fa/LC_MESSAGES/{django.po,django.mo}
apps/web/src/
├── app/lib/api/decision-support.ts         # Draft hydration/result types and guard
├── app/routes/project-decision-support.tsx # ISM state/remap/access/shared operations
├── app/locales/{en,fa}.json
└── components/decision-support/
    ├── BinaryRelationEditor.tsx            # New explicit directed select editor
    ├── IsmMethodPanel.tsx                  # New independent save/run
    ├── IsmLayerList.tsx                    # New server layer/group presentation
    ├── ism-input-rules.ts                  # New defaults/edit/remap/local validation
    ├── ism-input-rules.test.ts             # New independent helper regressions
    ├── no-client-ism-math.test.ts           # New boundary supplement
    ├── NamedListEditor.tsx                 # Optional operation metadata/stable typing
    ├── AhpMethodPanel.tsx                  # Access/pending/coordinator adapter only
    ├── SawMethodPanel.tsx                  # Adapter and late-response isolation only
    ├── TopsisMethodPanel.tsx               # Adapter and late-response isolation only
    ├── ValidationIssueList.tsx             # ISM named-cell focus
    ├── validation-issues.ts                # Binary/derivation codes
    ├── InputSnapshotViewer.tsx             # Frozen ISM inputs/layers/groups
    ├── ExecutionHistoryList.tsx            # Reuse generic filter/locale dates
    └── i18n.keys.test.ts                   # New components/dynamic keys
apps/web/e2e/tests/decision-ism.spec.ts       # New real bilingual browser checks
```

**Structure Decision**: Extend existing domain/route with one pure service and a binary editor instead of expanding AHP's numerical editor. Optional operation metadata avoids persistent criterion IDs. A small host coordinator satisfies concrete mixed-method acceptance. If another feature has implemented compatible host support by implementation time, reuse it; do not assume DEMATEL design delivered it.

## Delivery Sequence and TDD Boundaries

1. **Input/draft**: Failing name/shape/type/binary/diagonal and draft persistence/isolation/recovery tests → minimal method-specific validators/finite guard → focused green. Preserve AHP's unrelated `ism_matrix:[[9]]` fixture and shared ranking-dimension boundaries.
2. **Calculation**: Failing literal chain/diamond/disconnected/all-zero/single/cyclic/multiple-group/n=10 references → copied Boolean closure, simultaneous active-set extraction and maximal groups → green. Independently establish exact expectations, stable order, every criterion once and ≤n levels; test defensive invariant failure separately from valid cycles.
3. **Persisted execution**: Failing API selection/scoping/stale/deleted/frozen and synchronized PostgreSQL concurrency tests → early ISM dispatch/scoped atomic reload/lock/compute/snapshot/append → green. Leave DEMATEL stub/other engines unchanged; update truthful API docs.
4. **Entry/remap**: Failing helpers and rendered EN/FA keyboard tests → binary editor, guarded invalid hydration and optional operation metadata → green. Verify zero/blank, independent directions, editable diagonal, rename/move/add/remove and AHP typing/rename/reciprocity regression.
5. **Workspace**: Failing permission/failure/duplicate/pending/case-switch browser cases → ISM panel and small shared coordinator with AHP/SAW/TOPSIS adapters → green. Delay each other-method save and attempt ISM/global save in both directions; test view-only all-panel controls and returned frozen snapshot display.
6. **History/evidence**: Failing frozen/locale/legacy-stub cases → viewer/layer list/keys/error focus → green. Run focused then full Decision Support backend/helper/browser regression, typecheck/migration checks, and separate SC-008 timing. Record evidence/limits; source checks/tasks alone cannot complete behavioral gates.

Tasks must preserve meaningful red→minimal fix→green dependencies. Already-correct behavior needs regression evidence, not fabricated red. No production-like destructive validation is required.

## Requirement and Outcome Coverage

| Requirement/outcome | Design | Planned proof |
| --- | --- | --- |
| FR-001, SC-001 | API independence | ISM-only API/browser without ranking/other methods |
| FR-002 | Name/shape contract | Invalid counts/names/root/rows; n=1/10 |
| FR-003, SC-003 | Strict binary execution | Null/text/bool/nonfinite/overflow/finite invalid rejection; zero-run counts; zero/cycle success |
| FR-004 | Draft/remap UI contract | Save/reload, independent cells, two-axis operations |
| FR-005 | Binary identity | Both direct diagonal values; unchanged snapshot; integer output |
| FR-006 | Complete closure | Literal and independent traversal references |
| FR-007, FR-008, SC-002 | Active sets/reachable-intersection | Chain/diamond/cyclic/ten-node exact levels; full assignment/≤n rounds |
| FR-009 | Ordered interpretation | Deterministic levels/order and browser explanation |
| FR-010, SC-004 | Maximal groups | Two/long/multiple cycles; no self/same-level false groups; explanation |
| FR-011 | Visible direct/derived/layers/groups | Browser presentation alongside frozen input |
| FR-012 | Immutable append/provenance | Distinct run IDs and actor/time/snapshot |
| FR-013, SC-005 | Frozen review | Edit/rerun/locale before-after equality |
| FR-014 | Method isolation | Unrelated inputs/results equal, no auto-chain/weights/removal |
| FR-015 | Locatable/recoverable failure | Named cell focus; no partial success; denial/network draft recovery |
| FR-016, SC-007 | Authorization | Actual denial/no disclosure plus view-only mixed workspace |
| FR-017 | EN/FA presentation | Keys, labels/dates/direction/language-switch browser proof |
| FR-018, SC-006 | Keyboard/shared coordinator | Caret/remap and delayed mixed-method/case-switch EN/FA flows |
| SC-008 | Two-second result target | Documented request-to-visible duration distribution |

## Complexity Tracking

No violations require justification. No general graph platform, new domain entities or method-chaining framework is planned.
