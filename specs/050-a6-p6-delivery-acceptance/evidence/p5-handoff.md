# A6-P5 handoff

Command, from `apps/api/core`, with the repository `.env` loaded and the isolated test database:

```bash
../.venv/bin/python -m pytest \
  projects/tests/test_positions_and_history.py \
  projects/tests/test_team_lifecycle.py \
  permissions/tests/test_access_history.py \
  audit/tests.py \
  -q --tb=line
```

Result on `a46161d3530edfb78c8ebf94b4786d991bea0ba7` (dirty tree): **25 passed**, 8 warnings, 92.26s.

The same four files were included again in the later combined run recorded in `evidence/channels.md`: 59 passed.

The history feature was not rebuilt. Synchronous test settings do not prove a later asynchronous worker. `AUDIT_LOG_ASYNC=false` and `CELERY_TASK_ALWAYS_EAGER=true` in the local `.env`.
