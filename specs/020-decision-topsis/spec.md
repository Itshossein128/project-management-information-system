# Feature Specification: Decision Support TOPSIS Ranking (Phase 3)

**Feature Branch**: `020-decision-topsis`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: Implement Velora Decision Support Phase 3 from [04-topsis.md](../../docs/decision-support/04-topsis.md) — independent TOPSIS ranking (relative closeness to ideal solutions) that reuses Phase 2 ranking inputs and result-table patterns; prove method independence (TOPSIS-only and SAW+TOPSIS side-by-side without merged ranks).

**Authoritative sources** (do not contradict):
- [04-topsis.md](../../docs/decision-support/04-topsis.md) — vector normalization, ideal best/worst, distances, closeness; independence from SAW
- [01-module-scope.md](../../docs/decision-support/01-module-scope.md) — no forced SAW before TOPSIS; no merged ranks
- [09-ranking-reference.md](../../docs/decision-support/09-ranking-reference.md) — TOPSIS portion of sample; product MUST split so TOPSIS runs without SAW
- [02-decision-inputs.md](../../docs/decision-support/02-decision-inputs.md) — shared ranking input contract
- [08-execution-records.md](../../docs/decision-support/08-execution-records.md) — validate → run → frozen snapshot + method result
- [10-acceptance-checks.md](../../docs/decision-support/10-acceptance-checks.md) — AC01 (TOPSIS-only), AC15–AC16, AC03, AC25; sample numeric case
- [11-source-review.md](../../docs/decision-support/11-source-review.md) — O01/O02 open; interim TOPSIS output contract documented below
- [decision-support-component-inventory.md](../../docs/decision-support-component-inventory.md) — TopsisMethodPanel reuses shared ranking editors + RankingResultTable (extra columns for distances); pure TOPSIS calculation service — no math in views or client UI

**Phase**: 3 of 7 (see [decision-support-speckit-prompts.md](../../docs/decision-support-speckit-prompts.md))

**Depends on**: [018-decision-case-shell](../018-decision-case-shell/spec.md) and [019-decision-saw](../019-decision-saw/spec.md) (case shell, validators, ranking UI, SAW engine, immutable runs).

## Gap Analysis (current vs Phase 3)

Phase 2 delivers SAW-only ranking, shared ranking editors, and immutable runs. TOPSIS remains stubbed or absent. The ranking sample always runs SAW and TOPSIS together; the product must offer TOPSIS-only execution and keep SAW and TOPSIS results as separate histories (AC01, AC03, AC25). Doc 04’s analytical output includes distances to ideal solutions, while the sample returns only score/order — this phase picks an explicit interim product contract (below).

| Concern | Intent | Current state (after Phase 2) | Gap (this feature) |
|---------|--------|-------------------------------|--------------------|
| TOPSIS engine | Vector normalize, ideal best/worst, distances, closeness | Absent / stub | Independent pure TOPSIS matching doc 04 / sample TOPSIS path |
| TOPSIS-only run | Execute without SAW | SAW path exists; TOPSIS stub or missing | Real TOPSIS run; no SAW required or auto-created |
| Shared ranking UX | Reuse weights/types/matrix editors | Built for SAW | TopsisMethodPanel reuses same editors |
| Independence proof | Separate results when both methods run | SAW results only | Two independent result tables / run histories (AC03, AC25) |
| Distances in output | Analytical display vs sample omission | Open (O02) | Interim: store and show distances (see policy) |
| Zero-distance score | Closeness `0.5` when d_best+d_worst=0 | Not implemented | AC16 behavior |

**In scope**: Pure TOPSIS calculation service; TOPSIS-only execution appending immutable Decision Runs; reuse of Phase 2 ranking input editors and result-table patterns via TopsisMethodPanel; optional simultaneous SAW+TOPSIS selection showing separate results (never blended); locatable validation (including all-zero matrix columns for vector normalization); bilingual strings; automated checks for AC15–AC16, AC01 (TOPSIS-only), AC03/AC25 independence, and immutability/locatable errors on the TOPSIS path.

**Out of scope**: AHP/DEMATEL/ISM engines; automatic alignment or merging of ranks across methods; rewriting SAW formulas except extracting shared weight/matrix validation helpers if already shared; Excel import; closing O01–O10 as final product policy (interim TOPSIS contract only).

### Interim policy: TOPSIS output, distances, and ties (O01 / O02 — TOPSIS)

Open items O01 and O02 remain **open as final product policy**. For Phase 3 TOPSIS delivery only:

1. **Ordering**: Alternatives ordered by TOPSIS closeness score descending. Equal scores preserve case alternative input order (stable), matching the sample’s sort behavior.
2. **Display rank**: 1-based **ordinal position** after that sort (same interim style as Phase 2 SAW). Shared/tied ranks remain undecided under O01.
3. **Distances (interim product choice for O02)**: Each result row includes **distance to ideal best**, **distance to ideal worst**, and **closeness score**, plus option name and interim ordinal rank. This follows the analytical output in [04-topsis.md](../../docs/decision-support/04-topsis.md) and enables RankingResultTable `extraColumns`; it deliberately exceeds the sample’s score-only return shape.
4. **Zero total distance (AC16)**: If `d_best + d_worst == 0`, closeness is `0.5` (sample contract for indistinguishable alternatives).
5. **All-zero column**: A performance column with Euclidean denominator zero is rejected before scoring (sample / doc 04).
6. **Acceptance sample**: For the doc-10 fixture, TOPSIS scores MUST be `1.0` (الف) and `0.0` (ب) with order الف then ب (AC15).
7. **Independence**: Running TOPSIS MUST NOT invoke SAW or create a SAW run; running both on one case yields separate Decision Runs and separate result tables (AC01, AC03, AC25).

This interim MUST NOT be presented as the closed decision for O01/O02.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run TOPSIS only on ranking inputs (Priority: P1)

As a project member with edit access, I configure ranking inputs on a case that includes TOPSIS (without requiring SAW), run TOPSIS alone, and see closeness scores, distances, and order for that run.

**Why this priority**: Vertical slice for AC01 (TOPSIS-only) and AC15; proves independence from the combined sample.

**Independent Test**: Acceptance sample → run TOPSIS only → scores الف=`1.0`, ب=`0.0`, order الف then ب; no SAW run created.

**Acceptance Scenarios**:

1. **Given** a case with TOPSIS selected and valid ranking inputs, **When** the user runs TOPSIS, **Then** a successful Decision Run is stored with method TOPSIS, frozen inputs, and TOPSIS ranking (option, distances, closeness, interim rank) — and SAW is neither required nor executed (AC01).
2. **Given** the acceptance sample in [10-acceptance-checks.md](../../docs/decision-support/10-acceptance-checks.md), **When** TOPSIS is run, **Then** closeness scores are `1.0` for الف and `0.0` for ب and order is الف then ب (AC15).
3. **Given** a case with only TOPSIS selected (SAW not selected), **When** the user runs TOPSIS, **Then** the product does not force SAW selection or execution (AC01).

---

### User Story 2 - Reject invalid TOPSIS inputs; AC16 edge scores (Priority: P1)

As a project member, invalid matrices (including all-zero columns that break vector normalization) never create a successful TOPSIS run; when distances sum to zero, closeness is `0.5`.

**Why this priority**: Engine safety (doc 04 / sample) and AC16; locatable errors (AC26).

**Independent Test**: All-zero column → reject, no run; single alternative / identical rows yielding zero total distance → closeness `0.5`.

**Acceptance Scenarios**:

1. **Given** a performance column that is entirely zeros (normalization denominator zero), **When** the user attempts to run TOPSIS, **Then** the input is rejected with a locatable error and no successful run is stored.
2. **Given** shared ranking contract violations (empty cells, cost zeros, bad weights, etc.), **When** TOPSIS run is attempted, **Then** acceptance stops with field/cell paths and no successful run (AC26 shape).
3. **Given** a valid case where `d_best + d_worst == 0` for an alternative (e.g. single alternative or indistinguishable options per sample), **When** TOPSIS is run, **Then** that alternative’s closeness is `0.5` (AC16).

---

### User Story 3 - SAW and TOPSIS side-by-side without blending (Priority: P1)

As a project member, I can run SAW and TOPSIS on the same case (in either order) and see two independent result tables and history entries; ranks are never merged into one blended score.

**Why this priority**: AC03 and AC25 method independence; core product promise of doc 01 / 04.

**Independent Test**: Run SAW then TOPSIS (or reverse) on the same case → two runs; each result table shows only its method’s scores/ranks; no combined rank UI.

**Acceptance Scenarios**:

1. **Given** a case with both SAW and TOPSIS selected and valid ranking inputs, **When** the user runs each method, **Then** two independent Decision Runs exist and each result display is method-specific (AC03, AC25).
2. **Given** SAW and TOPSIS results that differ in rank order, **When** both are shown, **Then** the product presents the difference for review and does **not** produce a single blended ranking (doc 04 / AC25).
3. **Given** an existing TOPSIS run, **When** the user changes a weight or cell and runs TOPSIS again, **Then** a new run is appended and the prior TOPSIS snapshot/result remain unchanged (AC23–AC24 on TOPSIS path).

---

### User Story 4 - TOPSIS panel reusing shared ranking UI (Priority: P2)

As a project member, on the case page I use TopsisMethodPanel with the same ranking editors (weights, types, matrix), validate/run actions, a TOPSIS result table (including distance columns), and bilingual labels — without client-side TOPSIS math.

**Why this priority**: Completes the product surface and proves inventory reuse without duplicating editors.

**Independent Test**: Open case with TOPSIS → edit shared ranking inputs → run TOPSIS → see result table with scores and distances; switch locale; no TOPSIS formulas in the UI layer.

**Acceptance Scenarios**:

1. **Given** TOPSIS on the case, **When** the user opens the workspace, **Then** TopsisMethodPanel reuses WeightVectorEditor, CriterionTypeToggle, RectangularMatrixEditor, and RunActionBar (no second matrix/weight stack).
2. **Given** a successful TOPSIS run, **When** results are shown, **Then** RankingResultTable displays option, closeness score, interim rank, and distance-to-best / distance-to-worst (interim O02 contract) for that TOPSIS run only.
3. **Given** both SAW and TOPSIS have successful runs, **When** the case page shows results, **Then** two separate result tables (or clearly separated method panels) appear — never one blended table (AC25).
4. **Given** locale `fa` or `en`, **When** the TOPSIS surface is shown, **Then** labels and validation messages are localized.

---

### Edge Cases

- **TOPSIS-only vs sample**: Product path runs only TOPSIS when requested; sample’s combined return is a math reference, not orchestration.
- **All-zero column**: Rejected (denom = 0).
- **AC16**: Closeness `0.5` when total distance is zero.
- **Equal closeness scores**: Stable input order; interim ordinal ranks (not shared ties).
- **SAW already run**: TOPSIS run does not mutate prior SAW runs.
- **Empty cell ≠ 0**: Unchanged from shared contract.
- **Open O01/O02 final policies**: Only interim TOPSIS contract above; do not claim closed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide an independent TOPSIS calculation that, given valid ranking inputs and normalized weights, applies column vector normalization `v[i,j] = w[j] * x[i,j] / sqrt(sum_i(x[i,j]^2))`, identifies ideal best/worst by benefit/cost, computes Euclidean distances `d_best` and `d_worst`, and closeness `d_worst / (d_best + d_worst)` (doc 04).
- **FR-002**: TOPSIS execution MUST NOT require or invoke SAW or any other method (AC01).
- **FR-003**: When `d_best + d_worst == 0`, closeness MUST be `0.5` (AC16 / sample).
- **FR-004**: A performance column whose vector-normalization denominator is zero MUST be rejected with a locatable error; no successful run (doc 04 / sample).
- **FR-005**: TOPSIS calculation MUST live in a pure domain service; views and client UI MUST NOT implement TOPSIS math (inventory / constitution V).
- **FR-006**: Running TOPSIS MUST validate ranking inputs first; on success, append an immutable Decision Run with method TOPSIS, frozen input snapshot (including normalized weights when stored for audit), and TOPSIS result per interim policy (option, d_best, d_worst, score/closeness, interim ordinal rank) (doc 08; AC23).
- **FR-007**: Invalid validation or engine rejection MUST NOT create a successful run (AC26).
- **FR-008**: For the acceptance sample in doc 10, TOPSIS MUST produce closeness `1.0` and `0.0` with order الف then ب (AC15).
- **FR-009**: Users MUST be able to run SAW and TOPSIS independently on the same case; results MUST remain separate Decision Runs and separate displays with no blended cross-method rank (AC03, AC25; doc 01 / 04).
- **FR-010**: Changing live inputs and re-running TOPSIS MUST append a new run; prior TOPSIS (and SAW) runs MUST remain unchanged (AC24).
- **FR-011**: The product UI MUST introduce TopsisMethodPanel that reuses Phase 2 shared ranking editors and RunActionBar, and RankingResultTable with extra columns for distances per interim contract (component inventory).
- **FR-012**: User-facing TOPSIS labels and validation messages MUST work in Persian and English (constitution III).
- **FR-013**: All TOPSIS operations MUST require authenticated project membership and existing Decision Support view/edit permissions (constitution I).
- **FR-014**: Final O01/O02 policies remain open; Phase 3 MUST implement only the interim TOPSIS contract in this spec and MUST NOT claim those items closed.
- **FR-015**: AHP/DEMATEL/ISM engines and auto weight import MUST NOT be implemented in this phase.
- **FR-016**: Automated checks MUST cover AC15–AC16, TOPSIS-only AC01, independence AC03/AC25 (no SAW side-effect when running TOPSIS; separate displays when both exist), and AC23–AC24/AC26 on the TOPSIS path.

### Key Entities

- **Decision Case (shared)**: Same live ranking inputs as Phase 2; method selection may include TOPSIS and/or SAW.
- **Decision Run (TOPSIS)**: Immutable execution record with method TOPSIS, frozen ranking snapshot, and TOPSIS result rows (option, distances, closeness, interim rank).
- **TOPSIS Result Row**: User-facing alternative name, distance to ideal best, distance to ideal worst, closeness score, interim ordinal rank.
- **TopsisMethodPanel**: Product surface composing shared ranking editors + TOPSIS run/result display.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Using the documented acceptance sample, 100% of automated TOPSIS checks report closeness `1.0` / `0.0` and order الف then ب (AC15).
- **SC-002**: An authorized user can complete a TOPSIS-only run on a prepared case in under 5 minutes without being prompted to run SAW (AC01).
- **SC-003**: Automated checks show that running TOPSIS creates zero SAW runs in TOPSIS-only fixtures (AC01).
- **SC-004**: For AC16 fixtures where total distance is zero, closeness is `0.5` in 100% of tested cases.
- **SC-005**: When both SAW and TOPSIS are run on one case, 100% of tested scenarios show two independent result presentations with no blended rank field (AC03, AC25).
- **SC-006**: In 100% of tested re-run scenarios, a prior TOPSIS run’s frozen input and result remain unchanged after a new TOPSIS run (AC24).
- **SC-007**: Users can complete the TOPSIS ranking flow in both Persian and English without untranslated critical labels on the TOPSIS panel, shared editors, result table, or validation issues.

## Assumptions

- Phase 1–2 case shell, shared validators, ranking editors, SAW engine, permissions, and project Decision Support route remain the host surface; TopsisMethodPanel is added alongside SawMethodPanel.
- TOPSIS math is ported from the TOPSIS path of [09-ranking-reference.md](../../docs/decision-support/09-ranking-reference.md) and [04-topsis.md](../../docs/decision-support/04-topsis.md), as an independent callable (AC01).
- Shared ranking validation from Phase 2 remains the first gate; TOPSIS adds all-zero column (denom) rejection and AC16 closeness rule.
- Including distances in the interim result is the product choice for Phase 3 despite sample omission; revising later is an O02 decision.
- Ordinal ranks for TOPSIS match Phase 2 SAW interim style for consistency until O01 closes.
- Weight normalization reuses the existing shared helper.
- Automated verification emphasizes domain/API checks for AC15–AC16 and independence; full browser E2E is not required to close Phase 3 acceptance IDs if API and UI wiring evidence is otherwise sufficient.
- Open items O03–O10 stay open except the TOPSIS interim for O01/O02 documented here.
