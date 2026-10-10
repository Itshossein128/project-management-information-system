# Spec Kit prompts — Decision Support (تصمیم‌یار)

Copy each phase prompt into a new chat (or the Spec Kit skill) as **`/speckit-specify`** arguments. Run phases **in order**. After each specify succeeds, continue that feature with the usual pipeline before starting the next phase:

```text
/speckit-plan
/speckit-tasks use TDD
/speckit-implement
/speckit-converge
```

(then implement any convergence tasks, then optionally converge again)

**Authoritative requirements (do not invent conflicting rules):**

- [decision-support/README.md](./decision-support/README.md) and docs `01`–`12`
- [decision-support-component-inventory.md](./decision-support-component-inventory.md) (reuse / extract-just-in-time)
- Acceptance IDs in [10-acceptance-checks.md](./decision-support/10-acceptance-checks.md)
- Open items stay open until decided: [11-source-review.md](./decision-support/11-source-review.md)

**Stack constraints:** Django 4.2 + DRF in `apps/api/core/`, React Router 7 + Vite in `apps/web/`, project tenancy + JWT permissions, pure calculation services (no math in views/React), bilingual `en.json` / `fa.json`, pytest for engines.

**Suggested feature short-name prefixes:** `018-decision-case-shell`, `019-decision-saw`, … (adjust to next free `specs/NNN-*` number when specify runs).

---

## Phase overview

| Phase | Focus | Primary docs | Acceptance focus |
| --- | --- | --- | --- |
| 1 | Case shell, shared inputs, immutable runs (no method engines yet) | 01, 02, 08 | AC05–AC12 (structure), AC23–AC24 (snapshot shape), AC26 |
| 2 | SAW ranking end-to-end | 03, 09, 02, 08 | AC01 (SAW-only), AC11, AC13–AC14, AC23–AC26 |
| 3 | Independent TOPSIS + shared ranking UI proof | 04, 01, 08 | AC01 (TOPSIS-only), AC15–AC16, AC03, AC25 |
| 4 | AHP weights + pairwise matrix | 05, 02 | AC02, AC17–AC18, AC04 (no auto-feed) |
| 5 | DEMATEL prominence / relation | 06, 02 | AC02, AC19–AC20, AC04 |
| 6 | ISM layers | 07, 02 | AC02, AC21–AC22 |
| 7 | Manual weight transfer, polish, full AC closure | 01, 08, 10, 11 | AC03–AC04, remaining AC*, open-item decisions |

---

## Phase 1 — Case shell, input contract, execution records

```text
/speckit-specify

Implement Velora Decision Support (تصمیم‌یار) Phase 1: project-scoped decision CASE shell, shared INPUT contract, and immutable EXECUTION RUN records — without implementing SAW/TOPSIS/AHP/DEMATEL/ISM calculation engines yet.

Authoritative sources (must follow; do not contradict):
- docs/decision-support/01-module-scope.md (method independence; multi-method = independent analyses on one case; no forced method chain)
- docs/decision-support/02-decision-inputs.md (criteria/alternatives naming, dims 1..10, weights/types/matrix rules, empty cell ≠ 0)
- docs/decision-support/08-execution-records.md (validate → run → store frozen input snapshot + method result; prior runs immutable)
- docs/decision-support/10-acceptance-checks.md (AC05–AC12 structural validation; AC23–AC24 snapshot immutability shape; AC26 field/cell-located errors)
- docs/decision-support-component-inventory.md (reuse PageHeader/form/ui/nav; extract NamedListEditor, ValidationIssueList, ExecutionHistoryList, InputSnapshotViewer only as needed; do NOT build five method UIs yet)
- docs/decision-support/11-source-review.md (leave unresolved open items as open; do not hard-code undecided policies)

In scope for this phase:
1. New Django app (e.g. decision_support) with DecisionCase + DecisionRun (or equivalent): case title, selected methods list, criteria/alternatives/weights/types/matrices as structured data; runs store method id, frozen input JSON, result JSON, extracted_at/actor; no in-place mutation of past runs.
2. Shared server-side validators for input contract (names unique/non-empty, dimensions, finite non-negative numbers, benefit|cost, empty≠zero) returning CodedValidationError with field/cell paths.
3. Thin DRF endpoints under /api/v1/projects/{id}/… with IsAuthenticated + project membership + appropriate permissions (define view/edit permission codes consistently with Velora).
4. Minimal web UI: one project route + nav entry; create/edit case; edit criteria and alternatives lists (max 10); method multi-select (store selection only); show empty/history placeholders; bilingual strings.
5. Pytest for validators and immutability of runs (AC05–AC12, AC23–AC24 as applicable without engines).

Out of scope for this phase:
- Any ranking or criteria-analysis calculations (SAW/TOPSIS/AHP/DEMATEL/ISM)
- Square/rectangular matrix editors beyond what is needed to persist stub/null matrices for later phases (prefer storing empty structures; full matrix UX can wait for Phase 2)
- Excel import, external compute services
- Merging or auto-chaining methods
- Overloading project-decisions-workflow (management rationale) as this UI

Success looks like: a member can create a case, select methods, define criteria/alternatives within contract limits, and the API rejects invalid inputs with locatable errors; run model exists and cannot overwrite a prior snapshot when a new run is added.
```

---

## Phase 2 — SAW ranking (MVP vertical slice)

```text
/speckit-specify

Implement Velora Decision Support Phase 2: independent SAW ranking end-to-end on top of the Phase 1 case/run shell.

Depends on: completed Phase 1 feature (case, validators, immutable runs, project UI shell).

Authoritative sources:
- docs/decision-support/03-saw.md (formulas, benefit/cost normalization, score + order)
- docs/decision-support/09-ranking-reference.md (port SAW behavior from the editable sample; product must allow SAW-only execution — do NOT require TOPSIS to run)
- docs/decision-support/02-decision-inputs.md and 08-execution-records.md
- docs/decision-support/10-acceptance-checks.md: AC01 (SAW-only), AC09–AC14, AC23–AC26, sample numeric case in that doc
- docs/decision-support-component-inventory.md: introduce RectangularMatrixEditor, WeightVectorEditor, CriterionTypeToggle, RankingResultTable, RunActionBar, SawMethodPanel as thin wrappers; pure saw_service — no math in views/React

In scope:
1. Pure Python SAW engine service + shared weight normalization; reject all-zero benefit columns and invalid cost zeros per docs/reference.
2. API: run SAW for a case → persist DecisionRun with frozen inputs + SAW scores/order (rank policy: if open in 11-source-review, document chosen interim policy explicitly in spec).
3. Web: ranking input UX (weights, types, m×n performance matrix) reused later by TOPSIS; SAW result table; validation issues with cell paths; i18n.
4. Pytest AC14 + structural guards; UI wired to project case page method panel.

Out of scope:
- TOPSIS/AHP/DEMATEL/ISM engines
- Auto weight import from AHP/DEMATEL
- Combined/blended ranking scores

Success looks like: user runs only SAW and gets scores/order matching the acceptance sample; invalid matrices never create a successful run; snapshot is immutable.
```

---

## Phase 3 — Independent TOPSIS + shared ranking proof

```text
/speckit-specify

Implement Velora Decision Support Phase 3: independent TOPSIS ranking that REUSES Phase 2 ranking input UI and result table patterns; prove method independence (AC01/AC03/AC25).

Depends on: Phase 1 case shell + Phase 2 SAW.

Authoritative sources:
- docs/decision-support/04-topsis.md
- docs/decision-support/01-module-scope.md (no forced SAW before TOPSIS; no merged ranks)
- docs/decision-support/09-ranking-reference.md (TOPSIS portion; split from combined sample function)
- docs/decision-support/10-acceptance-checks.md: AC01 (TOPSIS-only), AC15–AC16, AC03, AC25
- docs/decision-support/11-source-review.md (TOPSIS distance/rank display open items — pick explicit interim product contract in the spec and mark as interim if still open)
- docs/decision-support-component-inventory.md: TopsisMethodPanel reuses RectangularMatrixEditor + RankingResultTable (extraColumns for distances if in contract); topsis_service pure

In scope:
1. Pure TOPSIS engine; callable without invoking SAW.
2. API run endpoint/action for TOPSIS-only; separate DecisionRun rows from SAW.
3. UI: TOPSIS panel on same case; if both methods have runs, show two independent result tables (never one blended rank).
4. Pytest AC15–AC16 and independence tests (running TOPSIS does not require/create a SAW run).

Out of scope:
- AHP/DEMATEL/ISM
- Automatic alignment of ranks across methods
- Rewriting SAW formulas unless a shared helper for weight/matrix validation is extracted cleanly

Success looks like: TOPSIS-only run works; SAW+TOPSIS both runnable on one case with separate histories/results; acceptance sample order matches.
```

---

## Phase 4 — AHP criteria weighting

```text
/speckit-specify

Implement Velora Decision Support Phase 4: AHP criteria weighting via pairwise comparison — independent of ranking methods.

Depends on: Phase 1 case shell (criteria list). Ranking phases may exist but MUST NOT be required to run AHP.

Authoritative sources:
- docs/decision-support/05-ahp.md (1–9 scale, reciprocal matrix, geometric-mean weights, CR reporting)
- docs/decision-support/02-decision-inputs.md (n×n criteria matrix; no alternatives required)
- docs/decision-support/01-module-scope.md and AC02/AC04/AC17/AC18 in 10-acceptance-checks.md
- docs/decision-support/11-source-review.md (CR formula / RI table / block-vs-warn on CR>0.1 — choose explicit interim policy in spec, document as interim if source still open)
- docs/decision-support-component-inventory.md: introduce SquareMatrixEditor (pairwise mode: auto reciprocal, diagonal 1); AhpMethodPanel; CriteriaWeightTable; pure ahp_service; ManualWeightTransferAction is OUT of this phase (Phase 7) — only ensure AHP does not auto-mutate SAW/TOPSIS inputs (AC04)

In scope:
1. Pure AHP engine: weights + inconsistency report (CR).
2. API run for AHP-only without alternatives/performance matrix.
3. UI pairwise matrix + weights + CR warning/alert per chosen policy; bilingual.
4. Pytest AC17–AC18 (and AC02 independence).

Out of scope:
- Pairwise ranking of alternatives (criteria weights only per doc 05)
- DEMATEL/ISM
- Auto-copy weights into ranking case fields

Success looks like: AHP runs with only criteria + pairwise matrix; CR>0.1 surfaces per policy; SAW/TOPSIS inputs unchanged unless user later transfers manually.
```

---

## Phase 5 — DEMATEL influence analysis

```text
/speckit-specify

Implement Velora Decision Support Phase 5: DEMATEL direct-effect analysis producing prominence and relation per criterion — independent of other methods.

Depends on: Phase 1 case shell; Phase 4 SquareMatrixEditor should be REUSED (intensity 0–4 mode), not forked.

Authoritative sources:
- docs/decision-support/06-dematel.md
- docs/decision-support/02-decision-inputs.md (0 is valid judgment ≠ empty)
- docs/decision-support/10-acceptance-checks.md: AC02, AC19–AC20, AC04, AC22
- docs/decision-support/11-source-review.md (singular I-N / all-zero policy — explicit interim in spec)
- docs/decision-support-component-inventory.md: DematelMethodPanel + CriteriaMetricsTable; dematel_service pure; no auto weight feed to ranking

In scope:
1. Pure DEMATEL engine (normalize by max row sum, T = N (I-N)^-1, D/R, prominence, relation); reject non-computable cases without fabricating numbers.
2. API + immutable DecisionRun for DEMATEL.
3. UI: n×n intensity matrix (0–4), results table; reuse square matrix shell.
4. Pytest AC19–AC20, AC22.

Out of scope:
- Survey aggregation / multi-expert fusion
- Auto conversion of prominence to SAW weights
- ISM

Success looks like: DEMATEL-only analysis works without alternatives; invalid invertibility does not yield fake scores; ranking inputs unchanged automatically.
```

---

## Phase 6 — ISM structural layering

```text
/speckit-specify

Implement Velora Decision Support Phase 6: ISM binary relation matrix → reachability closure → hierarchical layers — independent of other methods.

Depends on: Phase 1 case shell; reuse SquareMatrixEditor in binary 0/1 mode (from Phase 4/5), not a third grid implementation.

Authoritative sources:
- docs/decision-support/07-ism.md (self-reach via OR I, transitive closure, layering rule Reach = Intersection)
- docs/decision-support/02-decision-inputs.md
- docs/decision-support/10-acceptance-checks.md: AC02, AC21–AC22
- docs/decision-support/11-source-review.md (cycles / mutual reach display — interim policy in spec if still open)
- docs/decision-support-component-inventory.md: IsmMethodPanel + HierarchyLayerBoard; ism_service pure

In scope:
1. Pure ISM engine with tests for chain A→B→C ⇒ layers C, then B, then A (AC21).
2. API + immutable run records.
3. UI binary matrix + layer board; no fake weights/ranks.
4. Pytest AC21–AC22.

Out of scope:
- Using ISM output to auto-delete “irrelevant” criteria
- Graph library / fancy network viz unless needed for basic layer readability
- Auto pipeline into AHP/DEMATEL/SAW

Success looks like: ISM-only run produces correct layers for the acceptance chain; works without alternatives; other method inputs untouched.
```

---

## Phase 7 — Manual transfer, polish, acceptance closure

```text
/speckit-specify

Implement Velora Decision Support Phase 7: cross-cutting completion — manual weight transfer, UX polish, and closure of acceptance checks AC01–AC26 against the implemented product; resolve or explicitly defer remaining open items from source review.

Depends on: Phases 1–6 delivered (case shell, SAW, TOPSIS, AHP, DEMATEL, ISM).

Authoritative sources:
- docs/decision-support/01-module-scope.md (optional multi-step scenario; transfer ONLY manual)
- docs/decision-support/08-execution-records.md and 10-acceptance-checks.md (full AC matrix)
- docs/decision-support/11-source-review.md (close or document deferrals with product decisions)
- docs/decision-support-component-inventory.md: ManualWeightTransferAction; MethodComparisonNote; ValidationIssueList completeness; no new parallel matrix widgets
- Constitution / Velora bilingual + permission norms

In scope:
1. Explicit UI actions to copy AHP weights (and/or DEMATEL-derived weights IF a conversion formula is decided in this spec) into ranking weight fields — never automatic on run (AC04).
2. MethodComparisonNote when SAW and TOPSIS both have results; ensure AC03/AC25 presentation.
3. Fill gaps vs AC01–AC26: missing tests, locatable errors, inactive/unavailable empty states, i18n, ENDPOINTS.md, nav/permissions polish.
4. Record product decisions for previously open items (CR blocking, TOPSIS distance columns, rank ties, name normalization) in the feature spec / update decision-support docs only if the user asks — prefer feature spec + checklist evidence.
5. UAT-oriented checklist under the feature checklists/ for PM-style walkthrough of independence + one full optional ISM→AHP→SAW/TOPSIS manual path.

Out of scope:
- Excel import / external solvers
- New MCDM methods beyond the five
- Silent score fusion

Success looks like: all buildable AC checks have automated and/or checklist evidence; weight transfer is opt-in; no method is a hard prerequisite for another; converge finds no CRITICAL gaps against phases 1–6 specs.
```

---

## How to run a phase (cheat sheet)

1. Paste the phase block starting with `/speckit-specify` (include the blank line after the command if your runner expects arguments on following lines; otherwise put the whole description after `/speckit-specify` in one message).
2. Attach or `@`-mention the listed `docs/decision-support/*.md` files for that phase.
3. After specify finishes: `/speckit-plan` → `/speckit-tasks use TDD` → `/speckit-implement` → `/speckit-converge`.
4. Do not start Phase N+1 until Phase N’s implement (+ converge remediation) is done, so each specify can treat prior code as a dependency rather than re-specifying it.

## Notes

- Prefer **one Spec Kit feature directory per phase** (clearer plan/tasks/converge) over one giant feature for all five methods.
- If specify proposes overlapping models, keep a single `decision_support` app evolved across phases rather than five apps.
- Component inventory is guidance for plan/tasks; specify should stay outcome-focused (user value + FR/SC), while plan.md should name the shared components to extract.
