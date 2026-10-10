# Implementation Plan: Decision Support Case Shell (Phase 1)

**Branch**: `018-decision-case-shell` | **Date**: 2026-10-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/018-decision-case-shell/spec.md`

## Summary

Add Velora Decision Support (تصمیم‌یار) **Phase 1 shell only**: a new project-scoped `decision_support` Django app with editable **DecisionCase** (title, method multi-select, criteria/alternatives, stub ranking inputs) and append-only **DecisionRun** history (frozen input snapshot + result JSON, actor, time). Shared pure validators enforce the doc-02 input contract with field/cell-located `CodedValidationError`s (AC05–AC12, AC26). Thin DRF endpoints under `/api/v1/projects/{id}/…` with membership + `view_decision_support` / `edit_decision_support`. Minimal bilingual web route + nav entry; reuse PageHeader/form/empty chrome; extract `NamedListEditor` / `ValidationIssueList` / `ExecutionHistoryList` / `InputSnapshotViewer` only as needed. **No** SAW/TOPSIS/AHP/DEMATEL/ISM engines or full matrix UIs.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2), TypeScript (React Router 7 + Vite)  
**Primary Dependencies**: DRF, drf-spectacular, `permissions.project` (`IsProjectMember`, `HasProjectPermission`), TanStack Query; reuse `CodedValidationError` + custom exception envelope; web form/ui/layout kits  
**Storage**: PostgreSQL UUID models; case live JSON fields + immutable run rows (`input_snapshot`, `result`); no Excel / external compute  
**Testing**: pytest (validators AC05–AC12, run immutability AC23–AC24, permission IDOR); UI smoke optional after API green  
**Target Platform**: Velora monorepo (`apps/api/core`, `apps/web`)  
**Project Type**: Web + API monorepo  
**Performance Goals**: Case/run CRUD interactive; validation on ≤10×10 structures is trivial; no async workers required for Phase 1  
**Constraints**: Server-side project authz; empty cell ≠ 0; prior runs immutable; method independence (selection only); leave O01–O10 open; do not overload `project-decisions-workflow`  
**Scale/Scope**: One new Django app; one project nav entry + case workspace; stub “record run” for history proofs before engines

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status |
|-----------|--------|
| I. Server-enforced authz / project isolation | Pass — all case/run routes: `IsAuthenticated` + `IsProjectMember` + `HasProjectPermission` (`view_decision_support` / `edit_decision_support`); queryset scoped by `project_pk` |
| II. Data integrity end-to-end | Pass — models → serializers → validators → API → UI named lists; migrations for new tables; live case edits never rewrite run snapshots |
| III. Bilingual UX | Pass — shell labels + validation messages in `en.json` / `fa.json`; codes language-independent |
| IV. Explicit safe mutations | Pass — runs create-only; PATCH/PUT/DELETE on run snapshot rejected with stable code; case delete policy documented (runs cascade or protect — see research) |
| V. Minimal coherent changes | Pass — new domain app only where no SoR exists; reuse chrome/nav/form; no five method UIs; no workflow overload |
| VI. Evidence-based verification | Pass — pytest suites in quickstart; distinguish API tests vs UI smoke |
| VII. Accessible practical UX | Pass — locatable validation issues; empty/history states; max-10 named lists |

**Post-Phase 1 re-check**: Pass — contracts define field/cell `path` issues without claiming O03 final envelope; stub run endpoint proves AC23–AC24; permissions follow existing catalog pattern; open items remain open in research.

## Project Structure

### Documentation (this feature)

```text
specs/018-decision-case-shell/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── decision-cases.md
│   ├── decision-runs.md
│   └── input-validation.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks — NOT created here
```

### Source Code (touched)

```text
apps/api/core/decision_support/          # NEW Django app
  models.py                              # DecisionCase, DecisionRun
  services/
    validators.py                        # shared input contract (pure)
    weights.py                           # normalize weights helper (AC11)
    case_service.py                      # create/update case
    execution_service.py                 # freeze snapshot + append run (stub result OK)
  serializers.py
  views.py                               # thin ViewSets
  urls.py
  apps.py
  migrations/0001_initial.py
  tests/
    test_validators.py                   # AC05–AC12, AC26 paths
    test_runs_immutability.py            # AC23–AC24
    test_case_api.py                     # authz + CRUD smoke
  ENDPOINTS.md                           # optional short index

apps/api/core/permissions/constants.py   # view_decision_support, edit_decision_support + role grants
apps/api/core/config/settings.py         # INSTALLED_APPS
apps/api/core/projects/urls.py           # include decision_support.urls under project_pk

apps/web/src/
  app/lib/api/decision-support.ts
  app/routes/project-decision-support.tsx
  app/routeVars.ts / routes registration
  config/project-navigation.config.ts    # one nav child (not decisions-workflow)
  components/decision-support/
    NamedListEditor.tsx                  # as needed
    ValidationIssueList.tsx
    ExecutionHistoryList.tsx
    InputSnapshotViewer.tsx              # read-only; optional if history detail deferred
  locales/en.json, fa.json
```

**Structure Decision**: New **`decision_support`** app (Principle V — no existing MCDM SoR to extend). Mirror `risk` nesting: mount under `projects.urls` at `<uuid:project_pk>/`. Engines stay future pure modules under `services/`; Phase 1 only validators + case/execution orchestration. UI: single project route + `components/decision-support/*` shared shell pieces from inventory; keep `project-decisions-workflow` untouched.

## Complexity Tracking

None — new app is justified (greenfield domain). Stub run endpoint is justified so AC23–AC24 are testable before Phase 2 engines.

## Implementation Phases

1. **App + models + permissions** — `DecisionCase` / `DecisionRun`; `view_decision_support` / `edit_decision_support`; register URLs.
2. **Validators + weight normalize** — pure services; pytest AC05–AC12 / AC26.
3. **Case + stub-run API** — CRUD case; POST run freezes snapshot; reject run mutation; pytest AC23–AC24 + IDOR.
4. **Web shell** — nav, route, case form, named lists, method multi-select, validation list, history/empty placeholders, i18n.
5. **Polish** — ENDPOINTS.md / spectacular tags; quickstart verification pass.
