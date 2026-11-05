# A6-P2 traceability

Recorded 2026-11-05. This is technical readiness, not customer acceptance or a release.

Deletion policy: a custom role cannot be deleted while any assignment remains, including inactive and suspended memberships. Delete does not clear assignments. After the last assignment is removed or replaced, an authorized actor can delete the custom role. Built-in roles stay undeletable.

| Requirement | Result | What changed | Evidence |
|-------------|--------|--------------|----------|
| A6-R14 | اضافه شد | A role can belong to one project. Another project cannot see, edit, or assign it. The global role route also refuses retrieve, update, permission changes, delete, and impact for a local role id. A non-member no longer receives the local role from `GET /api/v1/roles/{id}/` | `projects/tests/test_local_roles.py` and the three review probes |
| A6-R11 | حفظ شد و اصلاح شد | Global custom roles stay with organization role administrators. Staff, the admin group, and HR do not gain management of a local role through the global route | `permissions/tests/test_roles_api.py`; `test_global_route_cannot_read_or_manage_local_role_and_rename_is_recorded` |
| A6-R12 | حفظ شد و به عضو وصل شد | Unknown permission codes are still rejected. Permission edits refresh the member result and write a base record | `permissions/tests/test_permission_origin.py` |
| A6-R13 | حفظ شد | Built-in roles still cannot be deleted | `projects/tests/test_local_roles.py` |
| A6-R15 | اصلاح شد | Selectable titles are active titles of this project or active public titles. Another project's title is rejected | `projects/tests/test_positions_and_history.py` |
| A6-R16 | اضافه شد | A member can keep several access roles and several job titles. Title defaults join the inherited permissions and do not clear roles | `projects/tests/test_positions_and_history.py` |
| A6-R17 | اضافه شد | Assigned custom roles are not deleted, including inactive and suspended memberships. The screen shows the assignment count before delete and does not clear assignments. Removal of one role keeps the other role's permission. Base history keeps actor, person, project, time, and the difference | `projects/tests/test_local_roles.py`, `projects/tests/test_positions_and_history.py`; browser toast: «این نقش هنوز 1 تخصیص دارد…» and no delete request |
| A6-R26 | حفظ شد | Role permissions union, and an explicit deny wins | `permissions/tests/test_permission_origin.py` |
| A6-R27 | اصلاح شد | Clearing an override restores `inherit` and does not store a deny | `permissions/tests/test_permission_origin.py` |
| A6-R28 | اصلاح شد | Each permission now reports `origin` as inherit, grant, or deny, and the member form uses that field | `permissions/tests/test_permission_origin.py` and `add-member-drawer.tsx` |
| A6-R09 | اضافه شد | Persian allow/deny matrix for the 13 base roles and 40 catalog permissions, with the owner of each role kind | `specs/046-a6-p2-project-roles/role-matrix.md` |
| PM-16, PM-17 | حل‌نشده | Contact directory and the emergency approval account stay outside this phase | No code change |
| History page | جزئی | Base records now include local and global role creation, name and description changes, and a role-level permission change even when no member's inherited set changes. Assignment, title replacement, and permission overrides were already recorded. The finished history screen remains a later phase | `RoleAccessChange` rows asserted in `projects/tests/test_local_roles.py`; `GET /access-changes/` |

The earlier claim of complete convergence was wrong. An independent review reproduced three failures, and those probes were run again here before the fix: non-member global read returned 200, staff changed a local role's permissions through the global route, and a local rename wrote zero history rows.

After the fix, the same three probes plus the role, origin, title, and global-role suites passed together: 23 passed. `pnpm typecheck` exited 0. The development database was not reset. Migration `master_data.0015_project_local_roles_and_titles` remains the schema change. A second convergence pass found no further gap in FR-001, FR-002, or FR-009 and did not add another task phase.

Browser on project `3164541f-810b-4a56-bb45-d6502b9b9914`, Persian UI: a local role was created, renamed through the project screen, assigned beside مدیر پروژه, and delete was refused with the assignment count. After the extra role was removed from the member, delete succeeded. The member row was left as مدیر پروژه / فعال. The temporary role was removed.
