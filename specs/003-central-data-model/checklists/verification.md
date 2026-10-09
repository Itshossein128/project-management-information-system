# Verification: Central Data Model (FR-DATA)

**Feature**: `003-central-data-model`  
**Date**: 2026-10-08

Maps success criteria to automated tests.

| SC | Criterion | Tests |
|----|-----------|-------|
| SC-001 | Activity/report drill-up to project | `schedule/tests/test_central_data_activity_embeds.py`, `field_reports/tests/test_central_data_navigation.py` |
| SC-002 | Portfolio ≥2 projects, currency-safe | `projects/tests/test_central_data_portfolio.py` |
| SC-003 | Partial IPC collections; original amounts immutable | `contracts/tests/test_ipc_collections.py` |
| SC-004 | CBS ≠ WBS; Commitment ≠ ActualCost ≠ Payment | `cost_control/tests/test_cbs.py`, `test_commitment_payment.py`, `test_cbs_links.py` |
| SC-005 | Org refs, ContractType, stakeholders, owning_unit | `master_data/tests/test_org_refs.py`, `test_contract_types.py`, `contracts/tests/test_contract_type_ref.py`, `projects/tests/test_central_data_stakeholders.py`, `test_central_data_owning_unit.py` |

## Soft-delete / money reuse (T051)

- `IPCCollection`, `Commitment`, `Payment`, `Stakeholder` extend `AuditSoftDeleteModel`
- `CostBreakdownNode` soft-delete via `soft_delete()`
- Portfolio totals use per-currency buckets (no silent FX mix)

## Manual UI smoke

- [x] `/projects` portfolio summary strip
- [x] Costs → CBS / تعهد tab (`CBSCommitmentTab`)
- [x] IPC detail → partial collections (`e2e/tests/contracts-ipc.spec.ts`)
- [x] Contract create → catalog type select
- [x] Project settings / create wizard → owning unit (`e2e/tests/project-registration.spec.ts`)
- [x] `/projects/:id/stakeholders`
- [x] `/settings/org-refs` create OrganizationUnit + ManagedContractType (`e2e/tests/org-refs-admin.spec.ts`)
- [x] Create wizard contract-type options come from ManagedContractType catalog (`e2e/tests/org-refs-admin.spec.ts`)
