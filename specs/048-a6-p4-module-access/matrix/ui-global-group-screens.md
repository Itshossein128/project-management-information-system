# Screens still gated by global group (org-level, not project permission)

A6-P4 T022 checklist. These use `hasRole(ADMIN/HR/…)` intentionally for **organization** administration. Project operational screens must use `usePermission` / `useActiveProjectPermission` instead.

| Screen | Gate | Verdict |
|--------|------|---------|
| `apps/web/src/app/routes/hr/users.tsx` | `ROLES.HR` / `ADMIN` / superuser | Keep — account administration (P3) |
| `apps/web/src/app/routes/settings-roles.tsx` | `ADMIN` / `HR` | Keep — global role catalog |
| `apps/web/src/app/routes/hr/home.tsx` | HR/ADMIN | Keep — org HR hub |
| `apps/web/src/config/navigation.config.ts` | ADMIN/HR/BUSINESS_SETUP | Keep — org nav |
| `apps/web/src/app/routes/business-setup*.tsx` | BUSINESS_SETUP | Keep — org schema |
| `apps/web/src/app/routes/project-members.tsx` | `usePermission('manage_members')` | OK — project effective |
| Project cost/contract/IPC routes | `usePermission(...)` | OK — project effective |

No project write screen in this sample still relies on global `admin` alone for mutations.
