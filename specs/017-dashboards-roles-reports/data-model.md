# Data Model: Dashboards, Roles & Reports

## Existing (unchanged SoR)

Domain entities remain the system of record: daily reports, progress figures, budgets, commitments, payments, IPCs, cash transactions, risks/issues, stakeholders, workflow decisions, etc. Dashboards and standard reports **read** them.

### Provenance shape (canonical for figures)

Used on progress report figures today; extended to KPI/pack figures and drill rows:

| Field | Type | Rules |
|-------|------|-------|
| figure_key | string | Stable id e.g. `evm.spi`, `finance.commitment_total` |
| source_type | string | Domain type e.g. `progress_entry`, `commitment`, `ipc` |
| source_id | UUID \| null | Primary record when singular |
| source_path | string | API/UI path hint for navigation |
| source_approved | bool | Whether source counts as approved |
| last_updated_at | datetime \| null | Last update of source (or aggregate max) |
| value | number \| null | Null when `status=inactive` |
| status | ok \| inactive \| unavailable | `inactive` when capability disabled |
| label_unapproved | bool | True when figure includes/shows unapproved data |

### Drill row

| Field | Type | Rules |
|-------|------|-------|
| id | UUID | Source record id |
| display | string | Human label |
| amount / qty | number \| null | As applicable |
| approval_status | string | Domain status |
| approved | bool | |
| last_updated_at | datetime \| null | |
| source_path | string | Deep link |

---

## Existing (extended): Roles (`master_data.Role` via seed / `permissions.constants`)

| FR role | System `role_name` | Notes |
|---------|-------------------|-------|
| System admin | Django `admin` group / superuser | Global |
| Executive / approver | `executive_approver` | **New** system role |
| Project manager | `project_manager` | Existing |
| Project controls | `project_controls` | **New** (planning_engineer remains; map or grant similar + dashboard) |
| Site specialist | `site_specialist` | **New** or alias of `site_supervisor` |
| Finance | `finance_manager` | Existing |
| HR | reuse / extend HR-capable role or `hr_officer` **New** if missing |
| Procurement / contracts | `procurement_officer` (+ finance_manager for contracts) | Existing |
| Supervisor / consultant | `supervisor_consultant` | **New** view-heavy |
| Viewer | `viewer` | Existing |

Project scope continues via `ProjectMember` + `ProjectMemberRole`.

---

## Config (code): Role dashboard pack catalog

Not necessarily DB rows in v1 — Python catalog keyed by role:

| Pack id | Roles | Indicator groups (summary) |
|---------|-------|------------------------------|
| executive | executive_approver, project_manager (portfolio) | portfolio status, budget/EAC, profitability, liquidity need, high risks, milestone delays, overdue decisions |
| project_manager | project_manager | scope, milestones, plan vs actual, critical activities, unapproved daily reports, risks, open changes, contract status, overdue actions |
| project_controls | project_controls, planning_engineer | WBS, baseline, physical progress, EVM, variances, finish forecast, schedule data quality |
| finance | finance_manager | budget, commitment, cost, payment, IPC, receivables, collections, projected cash |
| hr_site | site_specialist, site_supervisor, hr_* | capacity, assignment, attendance, machinery, materials, stoppages, barriers |
| unit_manager | (unit leads) | unit requests/approvals, pending work, unit performance |

Each indicator references `figure_key`, capability dependency, and drill builder.

---

## New: `projects.ReportExportVersion` (or `reporting.ReportExportVersion`)

| Field | Type | Rules |
|-------|------|-------|
| id | UUID | PK |
| report_type | string | Catalog key e.g. `weekly_progress`, `portfolio_cash`, `budget_variance` |
| project | FK Project \| null | Null for portfolio-level |
| filters | JSON | Exact filter dict applied |
| extracted_at | datetime | Required |
| extracted_by | FK User | Required |
| approved_only | bool | Default true |
| file_url | string | Blank if inline JSON stored |
| payload_sha256 | string | Optional integrity |
| created_at | datetime | Audit |

**Immutable** after create (no update API).

---

## Optional: `projects.UserDashboardPref`

| Field | Type | Rules |
|-------|------|-------|
| user | FK User | |
| default_pack | string | Pack id |
| project | FK \| null | Last project context |

v1 may skip and infer pack from roles only.

---

## SoD rules (behavioral)

| Material action | Creator field | Final approve blocked if |
|-----------------|---------------|---------------------------|
| IPC approve | `ipc.created_by` | actor == creator |
| Cost/payment final approve | payment/actual created_by | actor == creator |
| Project change request approve | `cr.created_by` | actor == creator |
| Workflow instance → approved (budget_change etc.) | `instance.started_by` or subject creator | actor == creator for final stage that sets approved |
| Capacity exception approve | `exc.created_by` | Hard-block (upgrade from soft warn) |

Error code: `sod_self_approve`.

---

## State / transitions

- Report export: create-only → downloadable.
- Dashboard figures: no persisted state (computed).
- Capability inactive → figure `status=inactive` without inventing value `0` as success metric.
