# Quickstart: validate A6-P1 selected paths

## Prerequisites

PostgreSQL and Redis are running for the API test settings. Use the existing
API virtualenv and the repository `.env` only to point tests at the test
database. Do not drop or recreate the development database.

From the repository root:

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  projects/tests/test_member_role_atomicity.py \
  business_meta/tests/test_position_access_policy.py \
  inventory/test_visitor_item_writes.py \
  schedule/tests/test_activity_action_split.py
```

Django must stay on the 4.2 line. Do not install the full development
requirements file for this run.

## Scenarios

1. Member roles. As an active team manager, submit one unknown role id and
   then a mix of a real role and an unknown role, on create and on update.
   Expect HTTP 400, code `unknown_role`, a Persian message under the Persian
   locale and an English message under the English locale. Expect no new
   membership and unchanged previous roles.
2. Positions. With two projects, an ordinary inactive member of project A
   cannot list or retrieve A's positions. An active allowed member can. Staff
   alone and human resources alone cannot. A system administrator and a
   superuser can read without membership and cannot create, change, or delete
   a position without an active membership and `manage_members`.
3. Direct helper callers. The same inactive member is refused on the
   project-scoped reads that use `CanViewProjectMembers`, while the active
   member still receives those reads.
4. Legacy items. A visitor can list items and cannot create, update, delete,
   or import. A non-visitor writer still can.
5. Activity split. A member with `edit_activities` and without
   `delete_activities` or `approve_reports` can update an activity and cannot
   delete it or approve its measurement.
6. Team boundary. The system administrator without membership cannot add a
   project member. A project manager in project A does not gain management of
   project B through that role.

## Recorded result

On 2026-11-05 the five pytest modules in this guide passed: 13 tests. Nearby regressions `projects/tests/test_members.py`, `schedule/tests/test_activities.py`, and `permissions/tests/test_roles_api.py` also passed: 30 tests. The development database was not reset. Migration `master_data.0014_grant_delete_activities` was applied to it.

The member form was opened in the browser in Persian. Submitting an unknown role showed «یک یا چند نقش انتخاب‌شده وجود ندارد و هیچ تغییری ذخیره نشد.» The add dialog stayed open and the member list stayed unchanged.

## Expected evidence

Each scenario records one refusal and one allowed action. Passing pytest on
the final tree is backend evidence. It does not replace browser confirmation
of the member form, and it does not prove every module. Browser confirmation
is limited to the member form's visible error and unchanged list. Wage files,
contact files, and the full URL matrix remain later phases.

Details of fields and status rules are in [data-model.md](data-model.md).
Request and response rules are in [contracts/selected-access.md](contracts/selected-access.md).
