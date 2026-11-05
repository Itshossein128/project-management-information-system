# A6-P1 traceability

Version under test: working tree on `develop` after the selected-path access changes. This is not customer acceptance and not a release.

The installation has one authorization realm. Projects are not owned by an organization record, so the observation exception was not implemented by matching free-text organization names.

| Requirement | Result | What changed | Evidence |
|-------------|--------|--------------|----------|
| A6-R29 | اصلاح شد | Unknown and mixed role ids return `unknown_role` and do not create or clear memberships, roles, or overrides | `projects/tests/test_member_role_atomicity.py` |
| A6-R32 | اصلاح شد، جزئی برای بقیه محصول | Organization visitors cannot write `/api/items/`, including import. Other writers are unchanged. Project-wide viewer coverage remains P4 | `inventory/test_visitor_item_writes.py` |
| A6-R31 | اصلاح شد، جزئی برای بقیه محصول | Ordinary inactive members cannot read positions or the direct reads that use `CanViewProjectMembers`. Other URLs remain P4 | `business_meta/tests/test_position_access_policy.py` |
| A6-R10 | اصلاح شد روی مسیر منتخب | A project manager of one project cannot add members to another project | `permissions/tests/test_observation_exception.py` |
| A6-R37 | اصلاح شد روی مسیر منتخب | System administrator and superuser can read positions without membership and cannot write positions or members without active `manage_members`. Staff and HR cannot. `_is_global_admin` still bypasses unselected modules until P4 | `permissions/tests/test_observation_exception.py` |
| A6-R36 | جزئی | `delete_activities` is separate from `edit_activities`. Existing editors keep delete via migration `0014_grant_delete_activities`. Approval stays `approve_reports`. Other modules stay on their current shared edit checks until P4 | `schedule/tests/test_activity_action_split.py` |
| PM-16 | حل‌نشده | Who holds the independent contact permission was not decided | No code change |
| PM-17 | حل‌نشده | The emergency separation-of-duties account was not decided. Observation does not grant approval | No code change |
| A6-R54 | خارج از دامنه | Role templates were not added | No code change |

P4 still has to apply the read-only observation rule to every remaining caller of `_is_global_admin`. P6 is the independent final acceptance.
