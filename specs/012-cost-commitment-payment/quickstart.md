# Quickstart: Cost Commitment & Payment Gap Closure

## Prerequisites

- Postgres + Redis running; API venv ready; root `.env` sourced
- Migrated DB with seed project (`pnpm db:migrate` / seed as needed)

## TDD workflow (mandatory)

For each gap slice:

1. Add the failing pytest named below (**red**).
2. Implement the minimal fix (**green**).
3. Re-run the focused pytest (**still green**), then continue.

Do **not** implement production code for a slice before its failing test exists.

## Backend verify (after green)

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  cost_control/tests/test_remaining_no_double_count.py \
  cost_control/tests/test_commitment_payment_terms.py \
  cost_control/tests/test_actual_cost_lifecycle.py \
  cost_control/tests/test_payment_duplicate_guard.py \
  cost_control/tests/test_contract_order_remaining.py \
  cost_control/tests/test_ledger_report.py \
  cost_control/tests/test_commitment_payment.py \
  procurement/tests/test_requisition_create_commitment.py \
  -q
```

(Adjust procurement test path if the suite lands under `cost_control/tests/`.)

## Manual API smoke

1. Create commitment with `payment_terms` + CBS → approve → `budgets/remaining/` shows open committed.
2. Create actual linked to that commitment → approve → remaining **does not** drop by commitment+actual sum.
3. POST payment with `document_ref`; second identical ref → 400; with exception ack → 201.
4. GET `costs/ledger-report/` — commitment, actual, payment rows with documents.
5. (P2) Approved requisition → `create-commitment` → origin set; draft requisition blocked.

## UI

Open project → Costs: payment terms on commitment; Payments panel; ledger report with three row types (fa/en).

## Expected outcomes

| Check | Pass criteria |
|-------|----------------|
| SC-001 / SC-006 | Remaining tests match open-commitment formula |
| SC-002 | Duplicate payment tests 100% block without exception |
| SC-003 | Ledger report returns separate traceable rows |
| SC-004 | Contract remaining = approved − posted payments on linked commitments |
| SC-005 | Actual approve without classification rejected |
