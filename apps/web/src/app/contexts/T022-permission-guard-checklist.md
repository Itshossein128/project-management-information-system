# T022 — project effective permissions (UI parity checklist)

Manual spot checks after changing `project-context.tsx`, `usePermission`, or `useActiveProjectPermission`:

1. **Active member**  
   Open a project route that uses `usePermission` (e.g. project dashboard). Buttons and menus for a codename should match the effective permissions returned by  
   `GET /api/v1/projects/{id}/members/{user_id}/permissions/`.

2. **Inactive member**  
   Deactivate membership for the current user. The permission query should not show stale grants: write affordances must disappear (effective map is all false server-side).

3. **Organizational observer (admin group, not a project member)**  
   Read-only `view_*` affordances may appear for non-sensitive codenames only. `manage_members` and other writes must stay hidden. A 404 on the member-permissions endpoint must not look like “full write access.”

4. **Legacy global group**  
   Routes still using only `hasRole('manager')` / `hasRole('business-setup')` for project data (e.g. business table) should be migrated to `usePermission` or `useActiveProjectPermission` for the relevant project id.
