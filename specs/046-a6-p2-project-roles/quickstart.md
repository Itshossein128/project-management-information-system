# Quickstart: A6-P2

From `apps/api/core`, with the repository `.env` loaded and the test database, not the development database:

```bash
../.venv/bin/python -m pytest \
  projects/tests/test_local_roles.py \
  permissions/tests/test_permission_origin.py \
  projects/tests/test_positions_and_history.py
```

Do not drop or recreate the development database. Django stays on 4.2.

## Scenarios

1. The manager of project A creates a local role and assigns it. It is absent from project B. Project B's manager cannot change it or assign it in B.
2. An ordinary user cannot edit a global custom role. A built-in role cannot be deleted.
3. A custom role assigned to an inactive or suspended member is not deleted, and the assignment remains. After that assignment is replaced, the authorized actor can delete the custom role. A global role is not deleted by project member-management authority.
4. Two roles combine. Deny overrides the combination. Clearing the deny returns inheritance. Removing one role leaves the other role's permission.
5. The member form shows inherit, grant, and deny from the origin. A public active title and a local title can be selected. Another project's title cannot.
6. A role or override change leaves a record with the person, project, actor, time, and difference.

The browser check opens the member screen, creates or selects a local role, sets deny, clears it, and confirms the origin returns to inherit.
