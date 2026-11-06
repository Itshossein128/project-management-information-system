# Package 2 — finance, contracts, resources

Status: `closed`

Closed 2026-11-06 on shared ACL helpers + package-2 consumer fixes (cash-flow portfolio membership, procurement step-role no observation/staff write bypass, budget/commitment SoD, wage redaction). Revalidated 2026-11-06 Phase 13 (inventory project ACL, org catalog write authority, SoD approve_* / change-order). Method-level customer UAT remains A6-P6.

Evidence command:

```bash
cd apps/api/core && set -a && source ../../.env && set +a && \
../.venv/bin/python -m pytest \
  cost_control/tests/test_commitment_sod.py \
  cost_control/tests/test_budget_versions.py \
  hr/tests/test_wage_acl_and_cost_estimate.py \
  permissions/tests/test_creator_repair.py \
  cash_flow/tests \
  procurement/tests/test_approval_permissions.py \
  -q
```

Result: **65 passed** (2026-11-06).

| module | operation | methods/paths | roles | projects | expected | result | evidence | defect class | N/A reason |
|--------|-----------|---------------|-------|----------|----------|--------|----------|--------------|-----------|
| M13 | HR wage ACL | members + labor rates | ±view_wage | A | omit wage without view_wage | pass | test_wage_acl_and_cost_estimate | | |
| M15 | هزینه SoD | budget-versions approve, commitments | creator≠approver | A | sod_self_approve / break-glass | pass | test_budget_versions, test_commitment_sod | | |
| M16 | نقدینگی portfolio | cash-flow portfolio visibility | member±view_cashflow | A/B | no global-admin bypass | pass | cash_flow/tests + portfolio_access.py | | |
| M17 | قرارداد IPC SoD | ipc approve | creator≠approver | A | assert_not_self_final_approve | pass | contracts/services/ipc_service.py wired; shared sod tests | | |
| M18 | پیمانکار | subcontractors urls | member | A | IsProjectMember+HasProjectPermission | pass | subcontractors/views.py shared helpers | | |
| M19 | تدارکات step RBAC | requisitions submit/approve | step role only | A | staff/admin/superuser without step role denied | pass | test_approval_permissions | action/SoD | |
| M20 | انبار | `/api/` items (org catalog) + project-nested `space-material-requests/`, `department-activity-records/` (+ export/import/reports) via `inventory.project_urls` | member± / org writer | A/org | org item writes need account admin; project inventory uses IsProjectMember+HasProjectPermission | pass | test_alternate_path_parity; inventory views T061/T077 | | Org catalog remains shared; **9** project-nested inventory routes under `projects/<uuid>/` |
| M21 | منابع | materials/requests | member | A | IsProjectMember+HasProjectPermission | pass | resources/views.py shared helpers | | |
| M26 | اقتصادی | economic/* project routes | member | A | IsProjectMember+HasProjectPermission; org inflation IsAdminUser | pass | economic/views.py | | Org inflation upsert is staff-gated catalog, not project write |

Defect classes closed in package: procurement silent staff/admin write bypass (`action/SoD`); cash-flow portfolio global-admin visibility (`policy`). File-service real MinIO still package-3 M28 honesty note.
