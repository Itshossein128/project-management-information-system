# Research & Decisions: Decision Support AHP Criteria Weighting (Phase 4)

**Branch**: `021-decision-ahp` | **Spec**: [spec.md](./spec.md)

This document records architectural, mathematical, and user experience decisions for Phase 4 AHP criteria weighting.

---

## 1. Mathematical Weight Extraction Method

### Decision
Use the **Geometric Mean Method** (Logarithmic Least Squares) to extract normalized weights:
$$g_j = \left( \prod_{k=1}^n a_{j,k} \right)^{1/n}$$
$$w_j = \frac{g_j}{\sum_{k=1}^n g_k}$$

### Rationale
- Mandated directly by [05-ahp.md](../../docs/decision-support/05-ahp.md) lines 23–28.
- Closed-form, exact, non-iterative, and mathematically robust against rank reversal.
- Does not require iterative numerical eigenvalue approximation solvers or external linear algebra libraries (like NumPy/SciPy), preserving zero-dependency pure Python runtime.

### Alternatives Considered
- *Power Method / Exact Eigenvector Solver*: Requires matrix power iterations until convergence. Adds unnecessary complexity and floating-point iteration thresholds without practical accuracy improvement for $n \le 10$.
- *Row Sum Normalization (Arithmetic Mean)*: Less accurate and does not satisfy the reciprocal matrix group property.

---

## 2. Inconsistency Index & Ratio ($CI$ and $CR$)

### Decision
Calculate the principal eigenvalue approximation $\lambda_{\max}$ and Consistency Index $CI$:
$$v_j = (A \cdot w)_j = \sum_{k=1}^n a_{j,k} \cdot w_k$$
$$\lambda_{\max} = \frac{1}{n} \sum_{j=1}^n \frac{v_j}{w_j}$$
$$CI = \begin{cases} 0.0 & \text{if } n \le 1 \\ \max\left(0.0, \frac{\lambda_{\max} - n}{n - 1}\right) & \text{if } n > 1 \end{cases}$$

Use Saaty's standard Random Index ($RI$) table for $n \in [1, 10]$:
| $n$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| $RI(n)$ | 0.00 | 0.00 | 0.58 | 0.90 | 1.12 | 1.24 | 1.32 | 1.41 | 1.45 | 1.49 |

$$CR = \begin{cases} 0.0 & \text{if } n \le 2 \\ \frac{CI}{RI(n)} & \text{if } n > 2 \end{cases}$$

Consistency threshold: $is\_consistent = (CR \le 0.10)$.

### Rationale
- Standard Saaty formulation referenced in operational research literature.
- Clamping $CI \ge 0$ prevents negative $CI$ due to minute floating-point rounding errors on perfectly consistent matrices.
- For $n=1$ and $n=2$, $RI=0$, so $CR=0.0$ by definition.

### Alternatives Considered
- *Golden-Wang or Alonso-Lamata RI tables*: Less widespread than Saaty's original baseline; Saaty values are standard in civil engineering and construction management.

---

## 3. Inconsistency Handling Policy (Warn vs Block)

### Decision
When $CR > 0.10$:
- The backend calculation completes successfully and saves the `DecisionRun` with `status: "ok"`, `is_consistent: false`, and the exact $CR$ value.
- The web UI renders a prominent **advisory warning banner** stating that comparisons are inconsistent ($CR > 0.10$) and suggesting pairwise judgment review.
- The execution is **not** aborted or discarded.

### Rationale
- Resolves open item O05 as an explicit interim policy.
- Enables decision-makers to save exploratory or draft comparisons during collaborative sessions without losing input data.
- Ensures complete audit trails in `DecisionRun` records.

### Alternatives Considered
- *Hard HTTP 400 rejection on $CR > 0.10$*: Prevents users from seeing derived weights and makes iterative adjustment frustrating, especially in multi-stakeholder workshops.

---

## 4. Pairwise Matrix UX and Reciprocal Synchronization

### Decision
Implement `SquareMatrixEditor` in pairwise reciprocal mode:
- The diagonal cells $a_{j,j}$ are locked to `1.0` (read-only, visually dimmed).
- The matrix is symmetrical reciprocal: editing $a_{j,k}$ automatically updates $a_{k,j}$ to $1 / a_{j,k}$ in real time (and vice versa).
- Inputs support Saaty scale integers ($1, 2, \dots, 9$) and reciprocal fractions ($1/2, 1/3, \dots, 1/9$).
- Backend validation checks $|a_{k,j} \cdot a_{j,k} - 1.0| < 10^{-4}$ to allow standard floating-point representation.

### Rationale
- Resolves open item O06 as an explicit interim UX policy.
- Drastically reduces cognitive load and data entry effort: users only need to fill $n(n-1)/2$ judgments instead of $n^2$.

### Alternatives Considered
- *Manual two-way entry*: Users must manually calculate and enter fractions for the lower triangle; highly error-prone and violates UX Principle VII.

---

## 5. Independence and Weight Isolation (AC02, AC04)

### Decision
- AHP executes without needing alternatives or performance matrices.
- Executing AHP generates an immutable `DecisionRun` containing `{weights: [...], lambda_max, ci, cr, is_consistent}`.
- It does **not** update or mutate `case.weights` or `case.weights_normalized`.
- Voluntary manual transfer of weights into ranking inputs is reserved for Phase 7 (`ManualWeightTransferAction`).

### Rationale
- Strict compliance with AC02 and AC04.
- Prevents accidental side effects on SAW or TOPSIS ranking setups.
