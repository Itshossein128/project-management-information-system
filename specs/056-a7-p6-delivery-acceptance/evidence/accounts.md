# Role Matrix and Secret-Free Access Guide (`D04`)

**Phase**: `A.7-P6` (`specs/056-a7-p6-delivery-acceptance`)  
**Policy**: No raw passwords, session cookies, JWT tokens, or personal names are stored in this repository artifact.

## 1. Required Acceptance Personas (5 Roles)

| Persona ID (`role_persona`) | Persian Title | Role & Permission Scope | Primary Scenarios Exercised |
| --- | --- | --- | --- |
| `creator_planner` | ایجادکننده پروژه / برنامه‌ریز زمان‌بندی | Project member with `create_project`, `edit_project`, `manage_wbs`, `edit_schedule`, `import_schedule`, `submit_charter`, `create_change_request` (blocked from self-approving charter or own change requests by SoD). | `POS-01`, `POS-03`–`POS-09`, `NEG-01`–`NEG-09` |
| `independent_approver` | تصویب‌کننده مستقل (کنترل تفکیک وظایف) | Distinct user account from `creator_planner` with `approve_charter`, `approve_change_request`, `approve_baseline`, and project lifecycle management (`suspend`/`resume`/`complete`/`archive`). | `POS-02`, `POS-03`, `POS-08`–`POS-10` |
| `viewer` | مشاهده‌گر (`view_only`) | Project member with read-only permissions (`view_project`, `view_wbs`, `view_schedule`); denied all mutations, baseline changes, and schedule imports (`403`). | `NEG-12` |
| `system_admin` | مدیر سیستم (`Admin` / `is_staff`) | System administrator with read-only organizational observation (`A.6` exception even when not a project member) and exclusive authority for `undo-complete` (`بازگردانی تکمیل`) and `restore` from archive (`بازیابی از آرشیو`). | `POS-10`, `NEG-13`, `NEG-14` |
| `org_reference_steward` | متولی داده‌های مرجع سازمانی و الگوها | Authorized administrator for organizational units, contract types, measurement units, and reusable WBS/schedule templates (`/api/v1/project-templates/...` and reference catalogs). | `POS-01`, `POS-04` (`M01`–`M04`) |

## 2. Repeatable Provisioning & Reset Procedure

1. **Standard Local Seed**:
   ```bash
   pnpm db:migrate
   pnpm db:seed
   ```
   - Provisions synthetic development accounts in the local PostgreSQL database (`:5433`) using the local dev password defined in the operator's private environment setup (never committed to evidence files).
2. **Isolated `a7p5-import` Acceptance Stack (`:18000`)**:
   ```bash
   python3 ops/a7-p5/seed-browser.py
   ```
   - Generates mode-`0600` ignored auth fixtures in `ops/a7-p5/.runtime-auth.json` for isolated browser and worker testing without printing credentials to stdout.
3. **Clean Project Isolation Between Runs**:
   - Every automated and manual acceptance run uses a unique project code prefix (e.g., `A7P6-ACCEPT-`) or resets disposable test rows so repeated runs never collide on project code or WBS tree paths.
