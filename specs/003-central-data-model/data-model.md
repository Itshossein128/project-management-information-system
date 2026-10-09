# Data Model: Central Data Model

**Feature**: `003-central-data-model`  
**Date**: 2026-10-07

## New / extended entities

### 1. OrganizationUnit (OBS) — org-wide

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID PK | |
| code | CharField | max_length 30; unique |
| name | CharField | max_length 200; required |
| parent | FK self | null=True; PROTECT |
| status | CharField | `active`\|`inactive`; default active |
| created_at/updated_at | DateTime | |
| created_by/updated_by | FK User | |

**Rules**: No `project_id`. Cycle parent forbidden.

### 2. Project (extend)

| Field | Type | Constraints |
|-------|------|-------------|
| owning_unit | FK OrganizationUnit | null=True; SET_NULL |
| currency | (from 002) | IRR\|IRT |
| budget_ceiling | Decimal | null=True; optional alias of contract_amount policy — if omitted, use `contract_amount` as ceiling display |

### 3. Stakeholder — project-scoped

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID PK | |
| project | FK Project | CASCADE; required |
| name | CharField | max_length 200; required |
| organization_name | CharField | blank ok |
| role | CharField | max_length 120 |
| email | EmailField | blank |
| phone | CharField | blank |
| influence | PositiveSmallInteger | 1–5; null ok |
| interest | PositiveSmallInteger | 1–5; null ok |
| communication_need | TextField | blank |
| status | CharField | active\|inactive |
| audit + soft-delete | AuditSoftDeleteModel | |

### 4. CostBreakdownNode (CBS) — project-scoped tree

| Field | Type | Constraints |
|-------|------|-------------|
| project | FK | CASCADE |
| cbs_code | CharField | max_length 30; unique with project among non-deleted |
| cbs_name | CharField | max_length 200 |
| cost_type | CharField | labor\|material\|equipment\|subcontract\|overhead\|other (align CostCategory) |
| parent | treebeard | |
| description | Text | blank |
| audit + soft-delete | like WBS 002 | |

**Delete**: Block if non-deleted children or linked budget/commitment/actual_cost; else soft-delete.

### 5. ContractType — org-wide reference

| Field | Type | Constraints |
|-------|------|-------------|
| code | CharField | unique; max_length 40 |
| name_fa / name_en | CharField | |
| is_active | Bool | default True |

`contracts.Contract.contract_type` → migrate toward FK `contract_type_ref` (nullable during transition); keep char for back-compat until cutover task.

### 6. Commitment — project-scoped

| Field | Type | Constraints |
|-------|------|-------------|
| project | FK | required |
| commitment_number | CharField | max_length 60; unique per project |
| counterparty | CharField | max_length 200 |
| amount | Decimal | max_digits 18,dp 2; > 0 |
| currency | CharField | IRR\|IRT; default project.currency |
| fx_rate | Decimal | null; required if currency ≠ project.currency when aggregating |
| commitment_date | Date | required |
| due_date | Date | null |
| wbs | FK | null |
| cbs | FK CostBreakdownNode | null |
| status | CharField | draft\|approved\|closed\|cancelled |
| description | Text | blank |
| document_ref | CharField | blank |
| attachment | FK StoredFile | null |
| audit + soft-delete | | |

**Validation**: At least one of wbs or cbs required on approve (draft may omit).

### 7. Payment — project-scoped (outflow)

| Field | Type | Constraints |
|-------|------|-------------|
| project | FK | required |
| commitment | FK | null |
| actual_cost | FK | null |
| amount | Decimal | > 0 |
| currency | CharField | |
| fx_rate | Decimal | null |
| paid_at | Date | required |
| document_ref | CharField | blank |
| status | CharField | draft\|posted\|void |
| audit + soft-delete | | |

**Rules**: Append-only relative to commitment amount (sum payments ≤ commitment.amount unless corrective flag). Does not mutate commitment.amount.

### 8. IPCCollection — project via IPC

| Field | Type | Constraints |
|-------|------|-------------|
| ipc | FK IPC | CASCADE |
| amount | Decimal | > 0 |
| currency | CharField | default project/IPC currency |
| fx_rate | Decimal | null |
| collected_at | Date | required |
| reference | CharField | blank |
| notes | Text | blank |
| audit + soft-delete | | |

**Rules**: Never write to IPC submitted/approved/net amounts. Reject if sum(active collections) > approved payable (net) unless `acknowledge_over_collection` explicitly allowed (default reject).

### 9. Budget / ActualCost (extend)

| Change | Rule |
|--------|------|
| `cbs` FK | null=True on Budget and ActualCost |
| `commitment` FK | null=True on ActualCost |
| Financial field completeness | Prefer documenting gross/deduction/net on IPC (existing) + Payment/Collection; ActualCost keeps amount as net incurred |

### 10. Existing chains (no structural replace)

- Project ← WBS ← Activity ← DailyReportActivity / ActivityProgress — ensure FKs exposed.
- Project ← Contract ← IPC ← (approval workflow) ← IPCCollection.

## Relationships (target)

```text
OrganizationUnit 1──* OrganizationUnit (parent)
OrganizationUnit 1──* Project (owning_unit)
Project 1──* Stakeholder
Project 1──* CostBreakdownNode (CBS tree)
Project 1──* Commitment 1──* Payment
Commitment N──1 WBS / CBS
ActualCost N──1 Commitment / CBS / WBS
IPC 1──* IPCCollection
Contract N──1 ContractType (ref)
```

## Migration notes

- Additive only; backfill ContractType from distinct existing `contract_type` strings where feasible.
- Soft-delete CBS/Commitment/Payment/Collection/Stakeholder.
- No hard delete of approved IPC or posted payments.
