# Feature Specification: Decision Support SAW Ranking (Phase 2)

**Feature Branch**: `019-decision-saw`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: Implement Velora Decision Support Phase 2 — independent SAW ranking end-to-end on top of the Phase 1 case/run shell. Depends on completed Phase 1 (case, validators, immutable runs, project UI shell). Pure SAW engine + shared weight normalization; run SAW → persist immutable DecisionRun with frozen inputs and SAW scores/order; ranking input UX (weights, types, m×n matrix) reusable later by TOPSIS; SAW result table; validation with cell paths; i18n; AC14 + structural guards. Out of scope: TOPSIS/AHP/DEMATEL/ISM engines, auto weight import, blended ranking scores.

**Authoritative sources** (do not contradict):
- [03-saw.md](../../docs/decision-support/03-saw.md) — benefit/cost normalization, weighted sum, score + order
- [09-ranking-reference.md](../../docs/decision-support/09-ranking-reference.md) — port SAW behavior from the editable sample; product MUST allow SAW-only execution (do NOT require TOPSIS)
- [02-decision-inputs.md](../../docs/decision-support/02-decision-inputs.md) — shared ranking input contract
- [08-execution-records.md](../../docs/decision-support/08-execution-records.md) — validate → run → frozen snapshot + method result
- [10-acceptance-checks.md](../../docs/decision-support/10-acceptance-checks.md) — AC01 (SAW-only), AC09–AC14, AC23–AC26, sample numeric case
- [decision-support-component-inventory.md](../../docs/decision-support-component-inventory.md) — RectangularMatrixEditor, WeightVectorEditor, CriterionTypeToggle, RankingResultTable, RunActionBar, SawMethodPanel as thin wrappers; pure SAW calculation service — no math in views or client UI
- [11-source-review.md](../../docs/decision-support/11-source-review.md) — open items; interim policies documented explicitly below where needed

**Phase**: 2 of 7 (see [decision-support-speckit-prompts.md](../../docs/decision-support-speckit-prompts.md))

**Depends on**: [018-decision-case-shell](../018-decision-case-shell/spec.md) completed (case shell, shared validators, immutable runs, project UI shell).

## Gap Analysis (current vs Phase 2)

Phase 1 delivers the decision case, shared structural validators, immutable run records, and a bilingual project shell without ranking engines. Users cannot yet enter a full performance matrix, assign weights/types, or obtain SAW scores. The ranking reference sample always computes SAW and TOPSIS together; the product must diverge by offering SAW-only execution (AC01).

| Concern | Intent | Current state (after Phase 1) | Gap (this feature) |
|---------|--------|-------------------------------|--------------------|
| SAW engine | Pure benefit/cost normalize + weighted sum | Absent | Independent SAW calculation matching doc 03 / sample SAW path |
| Weight normalization | Shared `w = weights / sum` | Structural/helper only | Used by SAW; AC11 on scores |
| Ranking inputs UX | Weights, types, m×n matrix | Stub/empty structures | Shared editors for ranking; wired into SAW panel |
| SAW-only run | Execute SAW without TOPSIS | No run action for engines | Run SAW → new immutable run with SAW result |
| Result display | Name, score, order/rank for SAW | History placeholders | Ranking result table for SAW runs |
| Engine guards | Reject all-zero benefit columns; cost zeros | Partial structural AC09–AC10 | AC13 + engine-level rejects; never successful run on invalid input |

**In scope**: Pure SAW calculation service; shared weight normalization; SAW-only execution that persists an immutable run with frozen ranking inputs and SAW scores/order; ranking input editors (weights, criterion types, rectangular performance matrix) designed for later TOPSIS reuse; SAW method panel + run action + result table; locatable validation issues; bilingual strings; automated checks for AC14 and related structural/engine guards (AC01, AC09–AC13, AC23–AC26 as they apply to SAW).

**Out of scope**: TOPSIS, AHP, DEMATEL, and ISM engines; auto-import of weights from AHP/DEMATEL (AC04 remains “no auto-feed”); combined or blended ranking scores across methods; Excel import; final closure of all open items O01–O10 (only an explicit interim rank/display policy for SAW is set below).

### Interim policy: rank ties and score display (O01 / O02 — SAW only)

Open items O01 (tie ranks / score display precision) and O02 (independent engine output contract, numeric rank field) remain **open as final product policy**. For Phase 2 SAW delivery only, the following **interim** contract applies and MUST be documented on the run result so it can be revised later without rewriting history semantics:

1. **Ordering**: Alternatives are ordered by SAW score descending. When scores are equal, relative order of those alternatives as listed on the case (input order) is preserved — matching the sample’s stable sort behavior in [09-ranking-reference.md](../../docs/decision-support/09-ranking-reference.md).
2. **Display rank**: Each ordered row receives a 1-based **ordinal position** after that sort (1, 2, 3, …). Equal scores do **not** share a tied rank in this interim; competition/dense shared ranks remain undecided under O01.
3. **Score values**: Results store the computed SAW scores used for ordering. The acceptance sample MUST match exactly: scores `1.0` and `0.5` with order الف then ب. Broader floating-point display rounding remains under O01 and MUST NOT change the acceptance fixture’s expected values.
4. **Result payload shape (interim)**: For each alternative in ordered form: option name (user’s name), SAW score, and interim ordinal rank. No TOPSIS fields. Normalized weights MAY be stored alongside raw weights in the frozen snapshot for audit (doc 08 clarification).

This interim MUST NOT be presented as the closed decision for O01/O02; later phases may adopt shared ranks or a revised output contract via an explicit product decision.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enter ranking inputs and run SAW only (Priority: P1)

As a project member with edit access, I open a decision case that includes SAW, enter criteria weights, benefit/cost types, and an m×n performance matrix, then run SAW alone — without being required to run TOPSIS or any other method — and see scores and order for that run.

**Why this priority**: This is the Phase 2 vertical slice (AC01, AC14) and the first real method execution on the Phase 1 shell.

**Independent Test**: Configure the acceptance sample inputs → run SAW only → observe scores الف=`1.0`, ب=`0.5`, order الف then ب; confirm no TOPSIS execution was required or produced.

**Acceptance Scenarios**:

1. **Given** a case with SAW selected and valid ranking inputs (criteria, alternatives, weights, types, complete m×n matrix), **When** the user runs SAW, **Then** a successful execution record is created with method SAW, a frozen input snapshot, and SAW scores/order — and TOPSIS is neither required nor executed (AC01).
2. **Given** the acceptance sample from [10-acceptance-checks.md](../../docs/decision-support/10-acceptance-checks.md) (`criteria` تجربه/قیمت, `alternatives` پیمانکار الف/ب, `weights` [1,1], `types` benefit/cost, `matrix` [[10,100],[5,200]]), **When** SAW is run, **Then** scores are `1.0` for الف and `0.5` for ب and order is الف then ب (AC14).
3. **Given** weight vectors `[2, 3]` and `[20, 30]` on otherwise identical valid ranking inputs, **When** SAW is run for each, **Then** SAW scores match after weight normalization (AC11).
4. **Given** a case with only SAW selected (TOPSIS not selected), **When** the user uses the run action for SAW, **Then** the product does not force selection or execution of TOPSIS (AC01; contrast with combined sample `rank_options`).

---

### User Story 2 - Reject invalid ranking inputs before any successful SAW run (Priority: P1)

As a project member, when ranking inputs violate the contract or SAW engine guards (including all-zero benefit columns and invalid cost zeros), the system stops calculation, shows the field or cell path, and does not create a successful run.

**Why this priority**: Invalid matrices must never produce a successful run (AC09–AC13, AC26); engine guards from the sample are product requirements.

**Independent Test**: Submit each invalid fixture → coded locatable error → zero new successful SAW runs for that attempt.

**Acceptance Scenarios**:

1. **Given** a cost-type criterion with a zero (or non-positive) performance value, **When** the user attempts to run SAW, **Then** the input is rejected with a locatable error and no successful run is stored (AC09, AC26).
2. **Given** a negative weight or an all-zero weight vector, **When** the user attempts to run SAW, **Then** the input is rejected and no successful run is stored (AC10, AC26).
3. **Given** a benefit column that is entirely zeros (even if that criterion’s weight is zero), **When** the user attempts to run SAW, **Then** the input is rejected and no successful run is stored (AC13).
4. **Given** empty cells, non-numeric text, negatives, NaN, or infinity in the performance matrix, **When** validation or run is attempted, **Then** acceptance stops; empty cells are never treated as zero (AC08 shape; AC26).
5. **Given** any of the above failures, **When** the error is shown, **Then** the user can identify the field or cell path to fix (AC26).

---

### User Story 3 - Immutable SAW run history after re-run (Priority: P1)

As a project member, after a successful SAW run, changing a weight or matrix cell and running SAW again creates a new independent history entry; the prior run’s frozen inputs and SAW result remain unchanged.

**Why this priority**: Traceability (doc 08) and AC23–AC24 must hold for real engine results, not only Phase 1 stubs.

**Independent Test**: Run SAW → mutate one weight or cell → run SAW again → prior snapshot and scores unchanged; new run reflects new inputs.

**Acceptance Scenarios**:

1. **Given** a successful SAW run with named alternatives, **When** the run is inspected, **Then** alternative/criterion names, frozen ranking inputs, and SAW scores/order for that run are preserved with method identity, time, and actor (AC23).
2. **Given** an existing SAW run, **When** the user changes a weight or matrix cell and runs SAW again, **Then** a new history entry is created and the prior run’s input snapshot and result remain exactly as stored (AC24).
3. **Given** an existing SAW run, **When** a client attempts to overwrite that run’s snapshot or result in place, **Then** the mutation is rejected.

---

### User Story 4 - Ranking input and SAW result UI on the case page (Priority: P2)

As a project member, on the project decision case page I use shared ranking editors (weights, types, m×n matrix), a SAW method panel with validate/run actions, a SAW result table, and locatable validation issues — in Persian and English — without client-side SAW math.

**Why this priority**: Completes the end-to-end product surface; shared editors are the reuse foundation for Phase 3 TOPSIS.

**Independent Test**: Open case with SAW selected → edit weights/types/matrix → run SAW → see result table and history; switch locale and confirm critical labels; confirm calculation is not performed in the browser UI layer (server/engine owns math).

**Acceptance Scenarios**:

1. **Given** edit permission and SAW on the case, **When** the user opens the case workspace, **Then** they can edit weights, criterion types, and the rectangular performance matrix via shared ranking editors (inventory: WeightVectorEditor, CriterionTypeToggle, RectangularMatrixEditor).
2. **Given** valid inputs, **When** the user validates and runs SAW from the method panel, **Then** RunActionBar-style validate→run flow shows blocking errors or succeeds; SawMethodPanel shows RankingResultTable with option name, score, and interim ordinal rank for that SAW run.
3. **Given** validation or engine errors, **When** they are returned, **Then** ValidationIssueList (or equivalent) shows issues with field/cell paths.
4. **Given** locale `fa` or `en`, **When** the SAW ranking surface is shown, **Then** user-facing labels and validation messages are localized; permission and method codes remain language-independent.
5. **Given** the component inventory, **When** ranking UI is built, **Then** editors are thin shared wrappers reusable by a future TOPSIS panel; SAW-specific UI is limited to SawMethodPanel composition, not a duplicate matrix/weight stack.

---

### Edge Cases

- **SAW-only vs sample**: Product execution path runs only SAW when requested; the sample’s combined SAW+TOPSIS return shape is a reference for SAW math, not for product orchestration.
- **All-zero benefit column with zero weight**: Still rejected (AC13 / sample).
- **Cost zeros**: Rejected before division (AC09 / sample).
- **Single alternative (1×n)**: Valid dimensions; SAW scores computed per formulas; interim ordinal rank is 1 for that sole row.
- **Equal SAW scores**: Ordered with input-order stability; interim ranks are distinct ordinals after sort (see interim policy); shared ties remain open under O01.
- **Criteria-only methods on same case**: Running SAW still requires full ranking inputs; presence of AHP/DEMATEL/ISM selection does not auto-supply weights.
- **Empty cell vs explicit zero**: Empty is invalid and never coerced to 0; explicit 0 on benefit may be valid unless the whole benefit column is zero; explicit 0 on cost is always invalid.
- **Open naming (O04)**: Exact string uniqueness as in Phase 1; no new name-normalization policy.
- **Open error envelope (O03)**: Locatable coded errors remain required; envelope may evolve without removing cell/field paths.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an independent SAW calculation capability that, given valid ranking inputs, applies benefit normalization `r[i,j] = x[i,j] / max_i(x[i,j])`, cost normalization `r[i,j] = min_i(x[i,j]) / x[i,j]`, and `score[i] = sum_j(w[j] * r[i,j])` with normalized weights `w[j] = weights[j] / sum(weights)` (doc 03, 02).
- **FR-002**: SAW execution MUST NOT require execution of TOPSIS or any other method (AC01; doc 01 / 09 product divergence from combined sample).
- **FR-003**: Weight normalization MUST be a shared pure helper usable by SAW (and later TOPSIS); proportional weight vectors that normalize identically MUST yield identical SAW scores (AC11).
- **FR-004**: The SAW engine MUST reject an all-zero benefit column even when that criterion’s weight is zero (AC13; sample).
- **FR-005**: The SAW engine MUST reject non-positive values in cost columns (AC09; sample).
- **FR-006**: The SAW engine MUST reject negative weights and all-zero weight vectors (AC10).
- **FR-007**: SAW calculation MUST live in a pure domain service with no presentation or HTTP concerns; views and client UI MUST NOT implement SAW math (component inventory / constitution V).
- **FR-008**: Users MUST be able to persist and edit live ranking inputs on the case: weights, criterion types (`benefit` | `cost`), and an m×n performance matrix aligned to alternatives × criteria (doc 02).
- **FR-009**: Running SAW MUST validate inputs first; on success, append an immutable Decision Run with method identity SAW, frozen input snapshot (criteria order, alternatives, raw weights, types, matrix; normalized weights MAY be included for audit), SAW result (ordered option name, score, interim ordinal rank per interim policy), extraction time, and actor (doc 08; AC23).
- **FR-010**: Invalid validation or engine rejection MUST NOT create a successful run (AC26).
- **FR-011**: Changing live case inputs and running SAW again MUST create a new run; prior runs’ snapshots and results MUST remain unchanged; in-place overwrite of a run MUST be rejected (AC24).
- **FR-012**: For the acceptance sample in doc 10, SAW MUST produce scores `1.0` and `0.5` with order الف then ب (AC14).
- **FR-013**: Validation and engine errors MUST identify field or cell paths usable in the UI (AC26); Phase 1 coded-error approach continues unless a later O03 decision replaces the envelope without losing locatability.
- **FR-014**: The product UI MUST introduce shared ranking editors — WeightVectorEditor, CriterionTypeToggle, RectangularMatrixEditor — and compose them in SawMethodPanel with RunActionBar and RankingResultTable; these editors MUST be structured for reuse by a future TOPSIS panel without a second copy of the matrix/weight stack (component inventory).
- **FR-015**: RankingResultTable for SAW MUST show option name, score, and interim ordinal rank for the selected/latest successful SAW run without blending any other method’s scores (doc 08; AC25 shape for SAW-only; no combined rank).
- **FR-016**: User-facing SAW ranking labels and validation messages MUST work in Persian and English (constitution III).
- **FR-017**: All SAW run and ranking-input mutations MUST require authenticated project membership and appropriate view/edit Decision Support permissions already established in Phase 1 (constitution I).
- **FR-018**: Final policies for shared tie ranks and general score-display precision (O01) and the long-term independent engine output contract (O02) remain open; Phase 2 MUST implement only the interim policy documented in this spec and MUST NOT claim O01/O02 closed.
- **FR-019**: Auto-transfer of weights from AHP or DEMATEL into SAW MUST NOT be implemented (out of scope; AC04).
- **FR-020**: Automated checks MUST cover AC14 (sample scores/order) and structural/engine guards for AC09–AC13 as they apply to SAW runs, plus immutability AC23–AC24 and locatable failures AC26 for the SAW path; structural “no math in presentation layer” guards SHOULD be included where practical.

### Key Entities

- **Decision Case (extended)**: Phase 1 case plus editable live ranking inputs — weights, criterion types, and m×n performance matrix — used as the source for the next SAW run.
- **Decision Run (SAW)**: Immutable execution record with method SAW, frozen ranking input snapshot, and SAW result (ordered alternatives with scores and interim ordinal ranks).
- **Normalized Weight Vector**: Derived from raw weights by dividing by their positive sum; used inside SAW; may be stored in the snapshot for audit.
- **SAW Result Row**: One alternative’s user-facing name, SAW score, and interim ordinal rank after score-descending stable sort.
- **Shared Ranking Editors**: Product surfaces for weights, types, and rectangular matrix, reused conceptually by SAW now and TOPSIS later.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Using the documented acceptance sample, 100% of automated SAW checks report scores `1.0` / `0.5` and order الف then ب (AC14).
- **SC-002**: An authorized user can enter ranking inputs and complete a SAW-only run on a prepared case in under 5 minutes without being prompted to run TOPSIS (AC01).
- **SC-003**: For AC09, AC10, and AC13 fixtures, attempts to run SAW fail 100% of the time in automated checks and create no successful run (AC26).
- **SC-004**: In 100% of tested re-run scenarios, changing a weight or cell and running SAW again leaves the prior run’s frozen input and SAW result unchanged (AC24).
- **SC-005**: Weight vectors that differ only by a positive scale factor produce identical SAW scores in 100% of AC11 fixtures tested.
- **SC-006**: Users with access can complete the SAW ranking flow in both Persian and English without untranslated critical labels on the SAW panel, editors, result table, or validation issues.
- **SC-007**: No accepted Phase 2 outcome requires TOPSIS, AHP, DEMATEL, or ISM calculation, auto weight import, or a blended cross-method score.

## Assumptions

- Phase 1 case shell, shared validators, run immutability, permissions, and project Decision Support route/nav are available and remain the host surface for SawMethodPanel.
- SAW math is ported from the SAW path of [09-ranking-reference.md](../../docs/decision-support/09-ranking-reference.md) and [03-saw.md](../../docs/decision-support/03-saw.md), split into an independent callable so AC01 holds.
- Shared structural validation from Phase 1 remains the first gate; SAW engine adds benefit-column and cost-zero guards as specified.
- Interim ordinal rank policy above is sufficient for Phase 2 display and AC14 (which cares about scores and order); revising to shared ranks later is a product decision under O01, not a silent change.
- Score equality for the acceptance fixture uses exact expected values `1.0` and `0.5`; general UI rounding is not finalized (O01).
- TOPSIS panel may reuse the same ranking editors in Phase 3; this phase does not build TopsisMethodPanel.
- Name uniqueness and empty≠zero rules unchanged from Phase 1 / doc 02.
- Automated verification emphasizes domain/API pytest-style checks for AC14 and guards; full browser E2E is not required to close Phase 2 acceptance IDs if API and UI wiring evidence is otherwise sufficient.
- Open items O03–O10 (except the SAW interim for O01/O02 documented here) stay open and are not decided by this feature.
