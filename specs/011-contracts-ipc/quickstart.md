# Quickstart: Contracts & IPC Gap Closure

## Prerequisites

- Postgres + Redis running; API venv ready
- Migrated DB with seed project

## Backend verify

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest contracts/tests/test_payment_terms.py \
  contracts/tests/test_ipc_amounts.py \
  contracts/tests/test_collection_status_invariant.py \
  contracts/tests/test_receivables_report.py -q
```

## Manual API smoke

1. Create contract with `payment_terms`.
2. Create draft IPC → submit → approve with reduced `approved_amount` + note.
3. POST two collections; GET IPC — status still `approved`; amounts unchanged; remaining decreased.
4. GET `.../ipcs/receivables-report/?near_due_days=7`.

## UI

Open project → Contracts: payment terms on form; IPC detail shows submitted/approved; Receivables panel lists overdue/near-due.
