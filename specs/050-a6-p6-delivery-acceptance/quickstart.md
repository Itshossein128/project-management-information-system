# Quickstart: A6-P6 delivery acceptance

Validate the candidate tree. Do not treat an older green run as this run. Do not drop or recreate the development database. Keep Django on 4.2. Do not install the full API development requirements file.

Record the version before any check:

```bash
git rev-parse HEAD
git status --short
```

Write that commit and whether the tree is dirty on every evidence row. Evidence for this feature goes under `specs/050-a6-p6-delivery-acceptance/evidence/`. Do not change status fields in `output/a6-requirements-2026-11-04/`.

## Prerequisites

- PostgreSQL and Redis running
- API virtualenv at `apps/api/.venv`
- Repository `.env` sourced
- Synthetic users and two projects, plus one project the subject is not a member of
- Passwords and recovery links kept out of the evidence files

Local API checks can use `AUDIT_LOG_ASYNC=false` and `CELERY_TASK_ALWAYS_EAGER=true`. Say so in the report. That setting does not prove a later asynchronous worker.

## 1. History handoff

From `apps/api/core`, run the command in [../049-a6-p5-access-history/quickstart.md](../049-a6-p5-access-history/quickstart.md).

If those tests cannot be run or do not pass, stop and report A6-P5 as the missing prerequisite. Do not rebuild that feature here. A passing run is the U18 technical starting point, still on this version, not a customer signature.

## 2. Direct-request matrix

From `apps/api/core`, with `.env` sourced:

```bash
../.venv/bin/python -m pytest \
  permissions/tests/test_alternate_path_parity.py \
  permissions/tests/test_assert_same_project.py \
  permissions/tests/test_observation_exception.py \
  permissions/tests/test_permission_origin.py \
  permissions/tests/test_redaction.py \
  permissions/tests/test_revocation_retry.py \
  permissions/tests/test_sod.py \
  permissions/tests/test_ui_server_parity_fixtures.py \
  permissions/tests/test_creator_repair.py \
  projects/tests/test_module_access_project_scope.py \
  projects/tests/test_person_directory_acl.py \
  projects/tests/test_stakeholder_contacts_acl.py \
  projects/tests/test_nested_export_redaction.py \
  projects/tests/test_local_roles.py \
  projects/tests/test_team_lifecycle.py \
  projects/tests/test_member_role_atomicity.py \
  storage/tests/test_stored_file_access.py \
  documents/tests/test_attachment_signing_security.py \
  inventory/test_visitor_item_writes.py \
  sub_reports/tests/test_offline_sync_foundation.py \
  workflow/tests/test_sod_final_approve.py \
  cost_control/tests/test_commitment_sod.py \
  schedule/tests/test_activity_action_split.py
```

Map each failure to a matrix cell or a U-scenario. A skipped or expected-failure result is `not_run` or an explicit non-pass, never `pass`. Add focused tests for operations these modules do not cover, using the row shape in [data-model.md](./data-model.md). Do not mark the uncovered operation passed.

Group the written matrix as the existing three batches, only as an execution order:

1. M01–M10 and M14
2. M13 and M15–M21 and M26
3. M11, M12, and M22–M25 and M27–M29

## 3. Browser path

Add or extend a Playwright spec beside `e2e/tests/a6-p1-real.e2e.spec.ts`. It must call the running API, not a mocked response, in Persian and English.

The manager, without coaching in the test, uses the existing screens:

- sign in and sign out
- account or member create
- role and exception
- revoke membership
- access history

Confirm the screen outcome matches the direct request for the same action. Repeat the visible labels in the other language.

## 4. Live file service

Run `apps/api/core/storage/tests_integration.py` only when `AWS_S3_ENDPOINT_URL` is set and the object store answers. Include a private object from the other project and a download after revocation.

If the store is unavailable, set the file cells to `blocked_external`. Do not copy the unit ACL result into that cell.

## 5. Live invite or recovery send

Use the existing delivery helper. A send cell passes only when the result is `sent` to `TEAM_DELIVERY_TEST_RECIPIENT` on an operational channel.

Console email and console SMS stay `not_configured`. In that case run the secure account-creation path, record that no message was sent, and leave the live-send cell `blocked_external`.

Also check that a used recovery link is rejected and that a refresh after sign-out is rejected. The guide states the current one-hour access-token lifetime.

## 6. Blocking defect

For each in-scope failure:

1. Record the failing command and the requirement id.
2. Fix it in the existing owner of that behavior.
3. Re-run the failed check and the affected scenario on the new version id.
4. Leave the acceptance text unchanged.

Record out-of-scope gaps in the defect log and do not implement them.

## 7. Guide and minutes

Write the manager guide from the screens above: create, assign, revoke, recover. Then fill the minutes for this `version_id` with technical results and blank signer fields. The package label remains `ready_for_acceptance` until a person sets `decision`.

## Expected outcome

- P5 quickstart result is attached or the prerequisite is reported
- Every matrix cell is `pass`, `fail`, `not_applicable` with a reason, or `blocked_external`
- U01–U20 have technical results distinct from customer confirmation
- File and send evidence are either live or explicitly external
- No secret is in the shared files
- No employer signature is present

Details: [contracts/delivery-acceptance.md](./contracts/delivery-acceptance.md) and [data-model.md](./data-model.md).
