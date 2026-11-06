# Quickstart: A6-P5 access history

From `apps/api/core`, with the repository `.env` loaded and the test database, not the development database:

```bash
../.venv/bin/python -m pytest \
  projects/tests/test_positions_and_history.py \
  projects/tests/test_team_lifecycle.py \
  permissions/tests/test_access_history.py \
  audit/tests.py
```

`permissions/tests/test_access_history.py` is the new module this phase adds. Do not drop or recreate the development database. Django stays on 4.2. Do not install the full development requirements file.

These tests prove the synchronous transaction used by the test settings. They do not prove a later asynchronous audit worker. If delivery is configured to write the trail out of band, that configuration needs its own failure test before durability is claimed.

## Scenarios

1. Change a member's roles, set and clear one exception, and change membership status. The project history shows actor, subject, project, time, before, and after. Exception rows are distinguishable from role rows.
2. Change a global role used by project A and project B. The organization history keeps a null project. The project A manager does not receive project B subjects. A direct request from a viewer is 403.
3. Filter by subject, actor, and time range, then open the next page. Rows stay inside the filter. Persian and English labels render.
4. Store a nested password and token. The saved JSON and the API response contain the redacted marker. Actor and the access difference remain.
5. Force the history insert to fail during a permission change. The change is not saved and the response is `audit_unavailable`. A failed change does not leave a success row.
6. Sign in successfully and request recovery. History shows `login_succeeded` and `recovery_requested` with requester and target separated. A wrong password adds no login row. The recovery token is absent.
7. Complete one final approval and one sensitive export that this phase wires. Each has its own history row. Request-write middleware coverage is not accepted as a substitute.
8. Remove a member and delete a custom role after its assignments are gone. Earlier rows remain readable.

## Browser

On the Persian project history screen, as the team manager, apply each filter and confirm the viewer never sees the screen or a successful direct response. Repeat the labels in English. The organization screen is visible to the system administrator and hidden from the project-only manager.

Details of the responses are in [contracts/access-history.md](./contracts/access-history.md). Fields are in [data-model.md](./data-model.md).
