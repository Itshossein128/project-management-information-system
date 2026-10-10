# Research: Decision Support SAW Ranking (Phase 2)

**Date**: 2026-10-10

## Findings

### Existing coverage (Phase 1) to reuse

- App `decision_support` with `DecisionCase` / `DecisionRun`, permissions, project-nested URLs.
- Pure `validators.validate_ranking_inputs` (AC05–AC12 structural) + `CodedValidationError` issue paths.
- `weights.normalize_weights` already exists (AC11 structural).
- `execution_service.create_stub_run` freezes snapshot and appends runs; rejects `method_not_selected`.
- Web: case page, NamedListEditor, ValidationIssueList, ExecutionHistoryList, InputSnapshotViewer, API client.
- Component inventory names shared ranking editors and `SawMethodPanel` / `saw_service.py`.

### Gaps

1. No `saw_service` / SAW scores; runs for `saw` still store stub results.
2. Case UI does not edit weights / types / performance matrix (fields exist on model/API).
3. Sample `rank_options` always runs SAW+TOPSIS — product must split for AC01.
4. AC13 (all-zero benefit column) not enforced as engine/product gate yet.
5. Result display table and validate→run UX for SAW missing.
6. Interim ordinal rank policy from spec not implemented (O01/O02 still open as final policy).

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Engine placement | Pure `services/saw_service.py` with `compute_saw(criteria, alternatives, weights, types, matrix) -> SawResult` | Inventory + FR-007; no HTTP |
| Port source | SAW loop from [09-ranking-reference.md](../../docs/decision-support/09-ranking-reference.md); formulas from [03-saw.md](../../docs/decision-support/03-saw.md) | Authoritative; do not port TOPSIS |
| Independence | Execution path for `method=saw` never imports/calls TOPSIS | AC01 |
| Weight helper | Reuse `normalize_weights`; engine receives raw weights and normalizes internally (or accepts pre-validated raw and calls helper) | AC11; DRY |
| Validation order | Structural `validate_ranking_inputs` first, then engine guards (benefit all-zero AC13 — may overlap structural cost zeros AC09) | Fail locatable; no successful run |
| AC13 error | Issue code `benefit_column_all_zero`, `path` = `criteria.{j}` (criterion / column index j) | Column-level failure; clear locatable path for AC26 |
| Snapshot | Keep Phase 1 deep-copy fields; **add** optional `weights_normalized: number[]` for audit (doc 08) | Spec FR-009 |
| Result shape | `{ "status": "ok", "engine": "saw", "ranking": [ { "option", "score", "rank" }, … ] }` ordered by score desc, stable on ties; `rank` = 1-based ordinal after sort | Spec interim O01/O02; no TOPSIS keys |
| Stub retention | Non-SAW methods still use Phase 1 stub (or reject real ranking for topsis until Phase 3) | Minimal scope; topsis stub OK if selected |
| Run API | Same `POST …/runs/` with `{ "method": "saw" }` — behavior upgrades from stub to real when method is `saw` | No parallel endpoint; Principle V |
| Case PATCH | Persist weights/types/performance_matrix via existing case serializer; UI hydrates all ranking fields | Already in data model |
| UI composition | Shared editors + `SawMethodPanel` on existing route; math only server-side | Inventory |
| Client | Sends live case PATCH then POST run; displays `result.ranking` from run response/history | No SAW formulas in TS |
| Structural guard | Test or lint that `views.py` / React panels do not contain SAW normalize formulas (string/AST check optional but FR-020) | Spec |
| Open O01/O02 | Interim ordinal ranks only; document in result; do not claim final tie policy | Spec FR-018 |
| Auto weights | Not implemented | AC04 / out of scope |

## Alternatives considered

- **Keep combined `rank_options` and discard TOPSIS half** — rejected; risks accidental TOPSIS coupling and fails AC01 clarity.
- **New `POST …/saw/` endpoint** — rejected; Phase 1 run resource already models method execution.
- **Compute SAW in the browser for preview** — rejected (FR-007 / inventory); server is source of truth.
- **Competition/dense tied ranks now** — deferred; interim ordinals match sample stable sort + display need without closing O01.
- **Separate NormalizedWeight table** — rejected; JSON on snapshot sufficient for ≤10.
- **Block TOPSIS stub runs in Phase 2** — optional; allowing stub for other methods keeps Phase 1 behavior; SAW is the only real engine.

## NEEDS CLARIFICATION

None remaining — Technical Context unknowns resolved. Product open items O01–O02 stay **open** with interim SAW policy documented in [spec.md](./spec.md) and [contracts/saw-engine.md](./contracts/saw-engine.md).
