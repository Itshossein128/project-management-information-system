# Session channel

version_id: `a46161d3530edfb78c8ebf94b4786d991bea0ba7`

Command from `apps/api/core`:

```bash
../.venv/bin/python -m pytest \
  authentication/tests/test_account_lifecycle.py \
  permissions/tests/test_revocation_retry.py \
  -q --tb=line
```

First run: 3 failed, 7 passed. The human-resources group received 403 when creating an account and when changing account status. The view text says that group is allowed.

After `IsOrganizationalAccountAdmin` also accepts the `hr` group, and still refuses staff alone, the same command: **10 passed**.

Sign-out refuses refresh. The access token lifetime covered by `test_logout_refuses_refresh_and_access_expires_in_one_hour` is one hour. No secret value is copied here.

`permissions/tests/test_revocation_retry.py` passed in this run and in the earlier direct-request suite.
