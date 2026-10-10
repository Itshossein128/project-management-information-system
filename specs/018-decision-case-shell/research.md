# Research: Decision Support Case Shell (Phase 1)

**Date**: 2026-10-10

## Findings

### Existing coverage to reuse

- Project nesting: `projects/urls.py` includes domain apps at `<uuid:project_pk>/` (same pattern as `risk`, `economic`, …).
- AuthZ: `IsAuthenticated` + `IsProjectMember` + `HasProjectPermission` with `required_permission` / action maps (`risk/views.py`).
- Permission catalog: `permissions/constants.py` `view_*` / `edit_*` pairs + `DEFAULT_ROLE_PERMISSIONS`.
- Errors: `config.exceptions.CodedValidationError` → envelope `{ error: { code, message, details } }` via `custom_exception_handler`.
- Immutability precedent: period-report figures reject PATCH with `figure_immutable`; `ReportExportVersion` stores extraction metadata + payload JSON (append-oriented).
- UI chrome: `PageHeader`, `EmptyState`, `QueryErrorState`, form kit, project nav config; workflow decisions route is a **different** product surface.
- Component inventory explicitly lists Phase-1 extractables and forbids five method UIs / workflow overload.

### Gaps

1. No `decision_support` app, models, validators, or APIs.
2. No `view_decision_support` / `edit_decision_support` permissions.
3. No project nav / route for تصمیم‌یار (must not reuse `decisions-workflow`).
4. No shared MCDM input validators or run history.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Bounded context | New Django app `decision_support` | Greenfield domain; Principle V says extend when SoR exists — it does not |
| Case storage | `DecisionCase` with JSON fields for `selected_methods`, `criteria`, `alternatives`, `weights`, `types`, `performance_matrix`, plus stub square matrices (`ahp_matrix`, `dematel_matrix`, `ism_matrix`) default empty lists | Matches doc 02 shapes; avoids premature normalized child tables for ≤10 names |
| Run storage | `DecisionRun` FK → case; `method`, `input_snapshot` JSON, `result` JSON, `extracted_at`, `extracted_by`; no update API for snapshot/result | Doc 08 / AC23–AC24; mirrors export-version immutability idea |
| Case delete | Soft-delete or hard-delete case **cascades** runs (history owned by case); runs themselves have no PATCH | Simple Phase 1; audit via existing middleware on delete if needed |
| Method IDs | Stable strings: `saw`, `topsis`, `ahp`, `dematel`, `ism` | Language-independent; store on case as list; independence = no execution order |
| Permissions | Add `view_decision_support`, `edit_decision_support`; grant both to `project_manager`; view+edit to `planning_engineer`; view to `viewer` | Matches Velora view/edit pairing; PM owns decision analysis |
| Validation placement | Pure `services/validators.py` called from case_service and execution_service (and serializers thin) | Inventory + no math in views |
| Ranking validation trigger | On case PATCH when ranking fields present **or** when creating a run for a ranking method; criteria-only methods may omit alternatives | Spec edge case AC02 readiness |
| Empty cell | Represent missing cells as JSON `null` or omit key; **never** coerce to `0` in validators or serializers | AC08 |
| Weight normalize | Pure helper `normalize_weights(weights) -> list[float]`; used for AC11 tests; not a scoring engine | Spec assumption |
| Stub run (Phase 1) | `POST …/decision-cases/{id}/runs/` with `{ "method": "saw" }` validates inputs required for that method family, freezes snapshot, stores `result: { "status": "stub", "engine": null }` | Proves AC23–AC24 without engines; real engines replace stub in later phases |
| Run mutation | Detail endpoint GET only; PATCH/PUT/DELETE → 400/405 with code `run_immutable` | AC24 |
| Error location (O03 interim) | `CodedValidationError(code='decision_input_invalid', detail={'issues':[{'code','path','message'},…]})` where `path` is dotted (`criteria.0`, `matrix.1.2`, `weights.1`, `types.0`) | Satisfies AC26; does **not** claim final cross-app envelope (O03 open) |
| Name policy (O04 interim) | Trim ends; reject empty; uniqueness is exact string equality; no Persian-digit / fuzzy fold | Leave O04 open |
| AC11 without scores | Assert `normalize_weights([2,3]) == normalize_weights([20,30])` | Engines out of scope |
| AC13 | Defer to Phase 2 engine (document only); optional structural note if full matrix present | Spec |
| UI composition | One route `project-decision-support`; MethodPicker as multi-select checkboxes; NamedListEditor×2; history list; no RectangularMatrixEditor yet | Inventory Phase 1 |
| Nav placement | New child under Planning or Commercial **separate** from `decisions-workflow`; path e.g. `decision-support` | Spec FR-015 |
| Capability key | Optional `decision_support` capability later; Phase 1 always show nav if permission allows (no capability gate required) | Avoid inventing capability product policy |
| Open items O01–O02, O05–O10 | Explicitly unresolved; no rank-tie, CR-block, DEMATEL/ISM viz policies in code | Doc 11 |

## Alternatives considered

- **Store cases inside `workflow` / decisions-workflow** — rejected (different domain; inventory anti-pattern).
- **Normalized Criterion / Alternative tables** — deferred; JSON lists sufficient for n,m ≤ 10 and snapshot freeze.
- **Client-only validation** — rejected (constitution I; AC must hold server-side).
- **Skip stub run until Phase 2** — rejected; AC23–AC24 need an append path in Phase 1.
- **Reuse `view_reports` / `edit_reports`** — rejected; distinct product surface deserves distinct codes for least privilege.
- **Full matrix editors in Phase 1** — rejected by spec/out-of-scope; empty stubs only.

## NEEDS CLARIFICATION

None remaining — Technical Context unknowns resolved by decisions above. Open product items O01–O10 stay **open** (not Phase-1 blockers).
