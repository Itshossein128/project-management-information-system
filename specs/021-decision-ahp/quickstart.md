# Quickstart & Verification Guide: Decision Support AHP Criteria Weighting (Phase 4)

**Branch**: `021-decision-ahp` | **Spec**: [spec.md](./spec.md)

This guide documents runnable validation scenarios that verify Phase 4 AHP criteria weighting end-to-end.

---

## Prerequisites
- PostgreSQL running on port 5433: `sudo pg_ctlcluster 16 main start`
- Redis running on port 6379: `sudo redis-server /etc/redis/redis.conf --daemonize yes`
- Python virtual environment: `apps/api/.venv`
- Frontend dependencies installed: `pnpm install`

---

## Validation Scenarios

### Scenario A: AHP-Only Execution (AC02, AC17)
- **Goal**: Execute AHP weighting on 3 criteria without providing alternatives or ranking matrices.
- **Inputs**:
  - `criteria`: `["Quality", "Cost", "Schedule"]`
  - `ahp_matrix`:
    ```json
    [
      [1.0, 2.0, 6.0],
      [0.5, 1.0, 3.0],
      [0.1666667, 0.3333333, 1.0]
    ]
    ```
- **Execution**: `POST /api/v1/projects/{p_id}/decision-cases/{c_id}/runs/` with `{"method": "ahp"}`
- **Expected Outcome**:
  - HTTP 201 Created
  - `status: "ok"`, `engine: "ahp"`
  - `weights`: Quality $\approx 0.60$, Cost $\approx 0.30$, Schedule $\approx 0.10$ ($\sum w_j = 1.0$)
  - `cr`: $\approx 0.0$ ($< 0.10$), `is_consistent: true`
  - No SAW or TOPSIS run created or required (AC02).

---

### Scenario B: Inconsistency Alert ($CR > 0.10$) (AC18)
- **Goal**: Provide intransitive judgments and verify the advisory warning is reported without crashing.
- **Inputs**:
  - `criteria`: `["A", "B", "C"]`
  - `ahp_matrix`:
    ```json
    [
      [1.0, 5.0, 0.2],
      [0.2, 1.0, 5.0],
      [5.0, 0.2, 1.0]
    ]
    ```
- **Expected Outcome**:
  - HTTP 201 Created
  - `is_consistent: false`, `cr > 0.10`
  - In web UI: Warning banner alert rendered advising pairwise comparison revision (AC18).

---

### Scenario C: Boundary Conditions ($n = 1$ and $n = 2$)
- **$n = 1$**: `criteria = ["SoleCriterion"]`, `matrix = [[1.0]]` $\implies$ weight $= 1.0$, $CR = 0.0$, $is\_consistent = true$.
- **$n = 2$**: `criteria = ["A", "B"]`, `matrix = [[1.0, 3.0], [0.3333333, 1.0]]` $\implies$ $w_A = 0.75, w_B = 0.25$, $CR = 0.0$.

---

### Scenario D: Input Validation Guards (AC26)
- **Non-positive cell**: cell value $\le 0 \implies$ rejected with `cell_non_positive`.
- **Diagonal $\ne 1$**: cell $(j, j) \ne 1.0 \implies$ rejected with `ahp_diagonal_invalid`.
- **Reciprocal mismatch**: $a_{k,j} \ne 1 / a_{j,k} \implies$ rejected with `ahp_reciprocal_mismatch`.
- **Dimension mismatch**: $n \times m$ where $m \ne n \implies$ rejected with `dimension_invalid`.
- **Empty cell**: cell is `null` $\implies$ rejected with `cell_empty`.

---

### Scenario E: Isolation and Immutability (AC04, AC23, AC24)
- Case has manual ranking weights `[10, 20]`, alternatives, and performance matrix.
- Execute AHP $\implies$ case's `weights` remain `[10, 20]`; zero modification to ranking inputs (AC04).
- Change a pairwise comparison and run AHP again $\implies$ second independent `DecisionRun` created; prior run snapshot and result unchanged (AC24).

---

## Automated Test Suites

### Backend Pytest Suite
```bash
cd apps/api/core
set -a && source /home/hossein/Desktop/projects/building-management/.env && set +a
../.venv/bin/python -m pytest decision_support/tests/test_ahp_service.py decision_support/tests/test_ahp_api.py -v
```

### Frontend Test Suite
```bash
node --test apps/web/src/components/decision-support/*.test.ts
```
