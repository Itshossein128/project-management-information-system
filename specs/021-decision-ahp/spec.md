# Feature Specification: Decision Support AHP Criteria Weighting (Phase 4)

**Feature Branch**: `021-decision-ahp`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: Implement Velora Decision Support Phase 4 from [05-ahp.md](../../docs/decision-support/05-ahp.md) — AHP criteria weighting via pairwise comparison, independent of ranking methods; geometric mean weight extraction, Saaty 1–9 reciprocal matrix, inconsistency ratio (CR) reporting and alert policy, no auto-mutation of ranking weights.

**Authoritative sources** (do not contradict):
- [05-ahp.md](../../docs/decision-support/05-ahp.md) — 1–9 scale, reciprocal matrix, geometric-mean weights, CR reporting
- [02-decision-inputs.md](../../docs/decision-support/02-decision-inputs.md) — $n \times n$ criteria matrix ($1 \le n \le 10$); no alternatives required
- [01-module-scope.md](../../docs/decision-support/01-module-scope.md) — method independence; AHP is a criteria-weighting method, not an alternative ranking engine
- [08-execution-records.md](../../docs/decision-support/08-execution-records.md) — validate → run → frozen snapshot + method result
- [10-acceptance-checks.md](../../docs/decision-support/10-acceptance-checks.md) — AC02 (AHP-only), AC04 (no auto-feed), AC17 (consistent matrix weights), AC18 (CR > 0.1 alert), AC22 (actual dimensions), AC23–AC26 (immutability and locatable errors)
- [11-source-review.md](../../docs/decision-support/11-source-review.md) — O05 (CR formula, RI table, block vs warn policy) and O06 (pairwise reciprocal entry UX)
- [decision-support-component-inventory.md](../../docs/decision-support-component-inventory.md) — SquareMatrixEditor (pairwise mode: auto reciprocal, diagonal 1), AhpMethodPanel, CriteriaWeightTable, pure `ahp_service` (no math in views or React)

**Phase**: 4 of 7 (see [decision-support-speckit-prompts.md](../../docs/decision-support-speckit-prompts.md))

**Depends on**: [018-decision-case-shell](../018-decision-case-shell/spec.md) completed (case shell, criteria list, immutable runs). Phase 2 (SAW) and Phase 3 (TOPSIS) exist in the codebase but MUST NOT be required for AHP to run (AC02).

---

## Gap Analysis (current vs Phase 4)

Phases 1–3 delivered the case shell, shared validators, immutable runs, and independent SAW and TOPSIS ranking engines. Criteria weighting via AHP is listed as a method in `METHOD_IDS` and `CRITERIA_METHODS`, but executing AHP currently returns a stub record (`{'status': 'stub', 'engine': None}`) without mathematical computation. Users cannot enter a pairwise comparison matrix, compute geometric mean weights, or inspect inconsistency ratios.

| Concern | Intent | Current state (after Phase 3) | Gap (this feature) |
|---|---|---|---|
| AHP calculation engine | Geometric mean weight vector + normalized weights + $\lambda_{\max}$ + $CI$ + $CR$ | Stub execution (`status: 'stub'`) | Pure AHP service calculating weights and Saaty inconsistency report |
| AHP input validation | $n \times n$ matrix validation, strictly positive numbers, diagonal 1, reciprocal consistency | Only checks `validate_criteria_only` | Locatable validation for $n \times n$ pairwise comparison matrix |
| AHP-only run | Execute criteria weighting without alternatives or ranking methods | Stubs only; no real result | Real AHP run generating immutable `DecisionRun` with weights and CR |
| Pairwise matrix UX | Enter pairwise preferences with Saaty 1–9 scale and automatic reciprocal synchronization | Absent | `SquareMatrixEditor` in pairwise mode (diagonal 1, auto-reciprocal update) |
| Criteria weight presentation | Display derived weights and inconsistency ratio report | Absent | `CriteriaWeightTable` with weight percentages, bar/rank, and CR badge |
| Inconsistency handling | Alert users when $CR > 0.1$ | Not implemented | Interim policy: calculate $CR$, display advisory warning when $CR > 0.1$, preserve audit run |
| Independence / No auto-feed | AHP run does NOT mutate case ranking weights (AC04) | Manual rule | Guaranteed server/client isolation: AHP run leaves ranking `weights` intact |

**In scope**:
1. Pure Python calculation service (`ahp_service.py`):
   - Geometric mean of rows: $g_j = (\prod_{k=1}^n a_{j,k})^{1/n}$
   - Normalized weights: $w_j = g_j / \sum_{k=1}^n g_k$
   - Eigenvalue approximation: $\lambda_{\max} = \frac{1}{n} \sum_{j=1}^n \frac{(A \cdot w)_j}{w_j}$
   - Consistency Index: $CI = (\lambda_{\max} - n) / (n - 1)$ for $n > 1$ ($CI = 0$ for $n=1$)
   - Consistency Ratio: $CR = CI / RI(n)$ using Saaty Random Index table
2. Pairwise matrix validator with locatable cell/path errors (`ahp_matrix.{j}.{k}`) checking dimensions ($n \times n$), strictly positive numbers ($a_{j,k} > 0$), diagonal equals $1.0$, and reciprocal consistency ($a_{k,j} = 1 / a_{j,k}$). Empty cells are never treated as zero (AC08).
3. API execution endpoint action for `ahp` that creates an immutable `DecisionRun` with frozen criteria + pairwise matrix snapshot and complete AHP result.
4. Web UI:
   - `SquareMatrixEditor` configured for pairwise comparisons (fixed diagonal of 1.0, auto reciprocal updating of upper/lower triangles, Saaty 1–9 and reciprocal fractions).
   - `CriteriaWeightTable` displaying criterion name, weight (decimal and percentage), ordinal rank, and visual indicator.
   - `AhpMethodPanel` integrating the pairwise editor, action bar, weight table, and inconsistency alert banner/badge.
5. Strict isolation: running AHP requires zero alternatives, zero performance matrix entries, and never modifies ranking weights on the case (AC02, AC04).
6. Automated pytest and frontend verification for AC02, AC04, AC17, AC18, AC22, AC23–AC26.

**Out of scope**:
- Pairwise alternative ranking (AHP in this system is strictly for criteria weighting per [05-ahp.md](../../docs/decision-support/05-ahp.md)).
- Automatic copying or pushing of AHP weights into ranking case `weights` or `weights_normalized` (manual transfer is deferred to Phase 7 per AC04).
- DEMATEL and ISM calculation engines (Phases 5 and 6).
- Excel import/export of matrices.
- Closing open items O01–O10 as permanent project-wide policy (interim AHP policy applied below).

---

### Interim policy: CR calculation, Random Index, and Inconsistency Handling (O05 / O06)

Open items O05 (CR formula, Random Index table, blocking vs warning behavior) and O06 (pairwise reciprocal entry UX) remain open as final product governance. For Phase 4 AHP delivery only, the following explicit **interim** policies apply:

1. **Random Index ($RI$) Table**: Standard Saaty Random Index values for $n \in [1, 10]$:
   - $n = 1: 0.0$
   - $n = 2: 0.0$
   - $n = 3: 0.58$
   - $n = 4: 0.90$
   - $n = 5: 1.12$
   - $n = 6: 1.24$
   - $n = 7: 1.32$
   - $n = 8: 1.41$
   - $n = 9: 1.45$
   - $n = 10: 1.49$
2. **Consistency Ratio ($CR$) Calculation**:
   - For $n \le 2$: $RI = 0.0 \implies CR = 0.0$ (by definition consistent).
   - For $n > 2$: $\lambda_{\max} = \frac{1}{n} \sum_{j=1}^n \frac{(A \cdot w)_j}{w_j}$. $CI = \max(0.0, \frac{\lambda_{\max} - n}{n - 1})$ (clamped to 0 against numerical floating-point errors). $CR = CI / RI$.
   - Inconsistency threshold: $CR \le 0.10$ is considered acceptable (`is_consistent: true`); $CR > 0.10$ is flagged as inconsistent (`is_consistent: false`).
3. **Execution & Alert Policy (Warn vs Block)**:
   - When $CR > 0.10$, execution **succeeds** and records the `DecisionRun` with `is_consistent: false` and the calculated $CR$ value. It does **not** abort or discard the calculation, ensuring users can audit their preliminary judgments and review history.
   - The UI surfaces a prominent **warning alert banner** and badge informing the user: *"Judgments are inconsistent (CR = X.XX > 0.10). Please review and revise pairwise comparisons."*
   - The run record clearly identifies inconsistency so downstream manual usage can flag or review the source.
4. **Pairwise Entry UX (O06)**:
   - The diagonal $a_{j,j}$ is fixed to $1.0$ and read-only.
   - When the user sets $a_{j,k}$ in the upper triangle ($j < k$), the reciprocal cell $a_{k,j}$ is automatically set to $1 / a_{j,k}$ in the form state (and vice versa).
   - Inputs support standard Saaty values: integers $1$ through $9$ and reciprocals ($1/2, 1/3, \dots, 1/9$, represented numerically with standard floating precision).
   - On server validation, reciprocal values must satisfy $|a_{k,j} - 1/a_{j,k}| < 10^{-4}$ to accommodate standard JSON serialization.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enter pairwise comparisons and run AHP weighting (Priority: P1)

As a project member with edit access, I open a decision case with AHP selected, enter pairwise comparisons for my criteria on a 1–9 scale without needing to define alternatives or performance matrices, run AHP, and view the derived criteria weights and consistency status.

**Why this priority**: Core value of Phase 4 (AC02, AC17). Provides independent criteria weighting based on relative user judgments.

**Independent Test**: Define 3 criteria → enter consistent pairwise comparisons → run AHP alone → receive normalized weights summing to 1.0, $\lambda_{\max} \approx 3.0$, $CR = 0.0$, and verify no ranking run is created or required.

**Acceptance Scenarios**:
1. **Given** a case with AHP selected and $n$ defined criteria ($1 \le n \le 10$) and zero alternatives, **When** the user provides a valid reciprocal pairwise matrix and executes AHP, **Then** a successful `DecisionRun` is created with method `ahp`, containing normalized criteria weights ($w_j > 0, \sum w_j = 1.0$) and an inconsistency report, without requiring alternatives or performance data (AC02).
2. **Given** a 3-criteria consistent comparison matrix where Criterion A is 2x Criterion B, and Criterion B is 3x Criterion C (so A is 6x C), **When** AHP is executed, **Then** weights match geometric mean normalization ($w_A \approx 0.60$, $w_B \approx 0.30$, $w_C \approx 0.10$), $CI \approx 0.0$, and $CR \approx 0.0$ (AC17).
3. **Given** a case with only 1 criterion ($n=1$), **When** AHP is executed, **Then** the weight is $1.0$ and $CR = 0.0$.
4. **Given** a case with 2 criteria ($n=2$) and comparison ratio $a_{1,2} = 3$ (and $a_{2,1} = 1/3$), **When** AHP is executed, **Then** weights are $w_1 = 0.75, w_2 = 0.25$, and $CR = 0.0$.

---

### User Story 2 - Inconsistency detection and advisory alert (Priority: P1)

As a project member, when my pairwise judgments contain circular or severe inconsistencies exceeding $CR > 0.10$, the system successfully calculates and saves the run, but clearly warns me that my judgments are inconsistent and provides the exact $CR$ value so I can revise them.

**Why this priority**: Inconsistency detection is the foundational quality check of AHP (AC18, O05 interim). Prevents users from blindly trusting contradictory judgments.

**Independent Test**: Provide an intransitive comparison matrix (e.g., A > B, B > C, but C > A) → execute AHP → verify run record created with `is_consistent: false` → verify UI displays warning banner with $CR > 0.10$.

**Acceptance Scenarios**:
1. **Given** a pairwise matrix with severe inconsistency where $CR > 0.10$, **When** AHP is executed, **Then** the execution succeeds with `status: "ok"`, records `is_consistent: false` alongside the computed $CR$ and $\lambda_{\max}$ in the run result, and the UI displays a warning banner advising the user to revise their comparisons (AC18).
2. **Given** a pairwise matrix with acceptable consistency ($CR \le 0.10$), **When** AHP is executed, **Then** the run result records `is_consistent: true` and the UI shows a success/consistent indicator without a warning banner.

---

### User Story 3 - Reject invalid pairwise comparison inputs (Priority: P1)

As a project member, if the pairwise matrix has invalid dimensions, non-positive numbers, empty cells, non-reciprocal values, or a diagonal not equal to 1, the system rejects the input with locatable field and cell errors and creates no successful run record.

**Why this priority**: Robust input validation prevents numerical crashes and ensures mathematical integrity (AC08, AC26).

**Independent Test**: Submit matrices with zero, negative numbers, empty cells, diagonal $\ne 1$, or dimension mismatches → receive HTTP 400 with coded errors pointing to exact `ahp_matrix.{j}.{k}` paths → verify zero runs created.

**Acceptance Scenarios**:
1. **Given** a pairwise matrix with a diagonal cell $a_{j,j} \ne 1.0$, **When** execution is attempted, **Then** the input is rejected with error code `ahp_diagonal_invalid` locating `ahp_matrix.{j}.{j}` (AC26).
2. **Given** a pairwise matrix with a cell $a_{j,k} \le 0$ or non-numeric/empty value, **When** execution is attempted, **Then** the input is rejected with error code `cell_non_positive` or `cell_empty` locating `ahp_matrix.{j}.{k}` (AC08, AC26).
3. **Given** a pairwise matrix where $a_{k,j}$ does not equal $1 / a_{j,k}$ within tolerance ($10^{-4}$), **When** execution is attempted, **Then** the input is rejected with error code `ahp_reciprocal_mismatch` locating `ahp_matrix.{k}.{j}`.
4. **Given** a criteria list of length $n$, but a pairwise matrix whose dimensions are not $n \times n$, **When** execution is attempted, **Then** the input is rejected with error code `dimension_invalid` locating `ahp_matrix`.

---

### User Story 4 - Strict isolation from ranking inputs and immutable run history (Priority: P2)

As a project member, running AHP generates an independent immutable execution history without altering the case's manual ranking weights, alternatives, or performance matrix, preserving complete auditability.

**Why this priority**: Upholds method independence (AC02, AC04) and run immutability (AC23, AC24).

**Independent Test**: Configure a case with manual ranking weights $[1, 2]$, alternatives, and performance matrix → run AHP yielding weights $[0.8, 0.2]$ → verify case's `weights` and `weights_normalized` remain unchanged $[1, 2]$ → verify past AHP runs remain immutable after revising comparisons.

**Acceptance Scenarios**:
1. **Given** a decision case with manual ranking weights, alternatives, and performance matrix configured, **When** AHP is executed, **Then** the case's `weights`, `types`, and `performance_matrix` fields remain completely unchanged; AHP weights are NOT automatically copied into ranking inputs (AC04).
2. **Given** a completed AHP run, **When** the user changes a pairwise cell in the UI and runs AHP again, **Then** a new independent `DecisionRun` is created; the previous run's frozen snapshot (criteria and pairwise matrix) and calculated weights remain unchanged (AC24).
3. **Given** a case with SAW, TOPSIS, and AHP all selected, **When** viewing the case workspace, **Then** AHP has its own dedicated method panel and independent execution history tab/view (AC03).

---

### Edge Cases

- **Single Criterion ($n = 1$)**: Pairwise matrix is $[[1.0]]$. Geometric mean is $1.0$, normalized weight is $1.0$, $\lambda_{\max} = 1.0$, $CI = 0.0$, $CR = 0.0$.
- **Two Criteria ($n = 2$)**: Pairwise matrix has $[[1, a], [1/a, 1]]$. Since $RI(2) = 0.0$, $CR$ is defined as $0.0$ regardless of $a$.
- **Intransitive Judgments**: If Criterion 1 > Criterion 2 ($a_{1,2} = 5$), Criterion 2 > Criterion 3 ($a_{2,3} = 5$), but Criterion 3 > Criterion 1 ($a_{3,1} = 5$), the geometric mean still produces a valid positive normalized weight vector, but $CR$ will be high ($> 0.1$), triggering the advisory warning.
- **Empty cells**: Empty cells must never default to zero or one silently. Any unfilled cell triggers a validation error before run.
- **Scale Bounds**: Standard Saaty comparisons range between $1/9$ and $9$. Values outside $(0, 10]$ are rejected or warned depending on configured boundary constraints.
- **Precision and Inversion in UI**: Entering $3$ in cell $(j, k)$ sets cell $(k, j)$ to $1/3 \approx 0.333333$. In the UI, the cell can display as `1/3` or `0.33` with tooltip.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a pure Python calculation service (`compute_ahp`) in `ahp_service.py` that computes criteria weights using the geometric mean method and returns normalized weights summing to $1.0$.
- **FR-002**: System MUST calculate the principal eigenvalue approximation $\lambda_{\max}$, Consistency Index $CI$, and Consistency Ratio $CR$ in `compute_ahp` using the standard Saaty Random Index table for $n \in [1, 10]$.
- **FR-003**: System MUST set $CR = 0.0$ and $is\_consistent = true$ when $n \le 2$.
- **FR-004**: System MUST evaluate $is\_consistent = (CR \le 0.10)$ when $n > 2$.
- **FR-005**: System MUST validate the $n \times n$ pairwise comparison matrix (`validate_ahp_inputs`), enforcing:
  - Matrix is a list of $n$ rows, each containing $n$ numeric values matching the criteria count $n$ ($1 \le n \le 10$).
  - Every cell $a_{j,k}$ is a finite, strictly positive number ($a_{j,k} > 0$).
  - Every diagonal cell $a_{j,j}$ equals $1.0$ (error code `ahp_diagonal_invalid`).
  - Reciprocal symmetry holds: $|a_{k,j} \cdot a_{j,k} - 1.0| < 10^{-4}$ (error code `ahp_reciprocal_mismatch`).
  - Empty cells, strings, negative numbers, zeros, NaN, or infinity are rejected with coded, locatable issues (`path: "ahp_matrix.{j}.{k}"`).
- **FR-006**: System MUST allow executing AHP on any case with AHP selected, requiring ONLY `criteria` and `ahp_matrix`; neither `alternatives` nor `performance_matrix` shall be required (AC02).
- **FR-007**: System MUST append an immutable `DecisionRun` on successful AHP execution, storing:
  - `method: "ahp"`
  - `input_snapshot`: frozen copy of `criteria` and `ahp_matrix`
  - `result`: `{ status: "ok", engine: "ahp", weights: [{ criterion, weight, rank }], lambda_max, ci, cr, is_consistent }`
  - timestamp and extracting user identity.
- **FR-008**: System MUST NOT modify case-level ranking weights (`weights`), normalized weights, alternatives, or performance matrix upon executing AHP (AC04).
- **FR-009**: System MUST support cases where $CR > 0.10$ by successfully persisting the run and returning $CR$, while flagging `is_consistent: false`.
- **FR-010**: System MUST render a dedicated `AhpMethodPanel` when AHP is selected on a decision case.
- **FR-011**: System MUST provide a `SquareMatrixEditor` in pairwise mode:
  - Renders an $n \times n$ grid labeled by criteria names.
  - Fixes diagonal cells $a_{j,j}$ to $1.0$ (disabled/read-only).
  - Automatically synchronizes reciprocal cells: editing $a_{j,k}$ updates $a_{k,j}$ to $1 / a_{j,k}$.
  - Supports Saaty scale values (1 through 9, and reciprocal fractions 1/2 through 1/9).
- **FR-012**: System MUST render a `CriteriaWeightTable` displaying the resulting weights for each criterion with percentage representation and ordinal rank.
- **FR-013**: System MUST display an advisory warning banner in the UI whenever an AHP result has $CR > 0.10$, explaining that judgments are inconsistent and suggesting revision (AC18).
- **FR-014**: System MUST NOT perform mathematical calculations (geometric mean, matrix multiplication, eigenvalue, CR) in the client UI or views; all mathematical derivations must occur in `ahp_service.py`.
- **FR-015**: System MUST provide complete bilingual localization in Persian (`fa.json`) and English (`en.json`) for all AHP labels, table headers, validation errors, and consistency warnings.
- **FR-016**: System MUST display past AHP runs in `ExecutionHistoryList`, allowing users to inspect frozen pairwise inputs and resulting weights without in-place mutation.

---

### Key Entities *(include if feature involves data)*

- **`DecisionCase` (Criteria weighting fields)**:
  - `criteria`: List of $n$ unique non-empty string names ($1 \le n \le 10$).
  - `ahp_matrix`: $n \times n$ list of lists of positive floats representing the pairwise comparison judgments.
- **`DecisionRun` (AHP execution record)**:
  - `case`: Foreign key to `DecisionCase`.
  - `method`: Literal `"ahp"`.
  - `input_snapshot`: JSON object containing frozen `criteria` and `ahp_matrix`.
  - `result`: JSON object containing:
    - `status`: Literal `"ok"`.
    - `engine`: Literal `"ahp"`.
    - `weights`: Array of objects: `{ criterion: string, weight: float, rank: int }`.
    - `lambda_max`: float (principal eigenvalue estimate).
    - `ci`: float (Consistency Index).
    - `cr`: float (Consistency Ratio).
    - `is_consistent`: boolean ($CR \le 0.10$).
  - `extracted_at`: DateTime of execution.
  - `extracted_by`: User who initiated the run.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A project member can enter a pairwise comparison matrix and execute AHP in under 30 seconds for a typical 4-criterion case.
- **SC-002**: 100% of valid pairwise matrices produce normalized weights summing to $1.0 \pm 10^{-6}$ and an accurate Consistency Ratio matching standard Saaty AHP.
- **SC-003**: 100% of invalid matrices (diagonal $\ne 1$, non-positive numbers, empty cells, dimension mismatch) are rejected before execution with locatable cell paths (`ahp_matrix.{j}.{k}`), resulting in 0 false-positive runs.
- **SC-004**: 100% of AHP executions leave ranking weights, alternatives, and performance matrices completely untouched on the case.
- **SC-005**: 100% of inconsistent runs with $CR > 0.10$ display an advisory warning banner in the user interface.
- **SC-006**: 100% of user-facing strings, headers, error messages, and consistency states render correctly in both English and Persian without untranslated keys.
- **SC-007**: Zero calculation formulas or eigenvalue estimations are executed on the client side; verified by automated client-side math audit tests.

---

## Assumptions

- **Saaty Scale Limits**: Comparisons are entered using the Saaty 1–9 preference scale and reciprocal fractions ($1/2 \dots 1/9$). Custom decimal inputs within $(0, 10)$ are supported for flexibility.
- **CR Threshold**: The standard Saaty threshold $CR \le 0.10$ is accepted across construction and engineering management domains as the benchmark for acceptable consistency.
- **Interim Warning Policy**: An inconsistent matrix ($CR > 0.10$) generates a valid run with `is_consistent: false` and a prominent UI warning rather than blocking the user from saving, allowing iterative exploration and history auditing.
- **Manual Weight Transfer Deferred**: Automatic transfer of AHP weights into ranking inputs is explicitly forbidden (AC04); voluntary manual transfer via UI button is planned for Phase 7.
- **Tenancy and Permissions**: Follows existing Velora project tenancy (`HasProjectPermission`) and permissions catalog established in Phase 1 (`view_decision_case`, `edit_decision_case`, `run_decision_method`).
