# Data Model: HR & Capacity Gap Closure

**Feature**: `006-hr-capacity`  
**Date**: 2026-10-08

## Entities

### User / Person dossier (existing — extend)

| Field | Type | Notes |
|-------|------|-------|
| id, full_name, email, mobile, status, is_active | existing | identity / contact / status |
| organization | Char, existing | free-text org label (retain) |
| **skills** | JSON list, default `[]` | **NEW** — skill tags/names |
| **qualifications** | JSON list, default `[]` | **NEW** |
| **org_unit** | FK → OrganizationUnit, null | **NEW** — OBS unit |
| **supervisor** | FK → User, null, SET_NULL | **NEW** — dossier supervisor |
| **default_capacity_percent** | Decimal, default 100 | **NEW** — optional; v1 may hardcode 100 if deferred |

**Invariants**:

- New `ResourceAllocation` requires person `is_active` and status not inactive/suspended.
- Soft-deleted users (if applicable) cannot receive new allocations.

### ProjectMember (existing — ACL only)

No new allocation fields. Wage / wage_type remain on membership for payroll-ish project context but **serialization gated** by `view_wage`. Membership does not imply ResourceAllocation and vice versa.

### ResourceAllocation (new — `hr`)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| project | FK → Project | CASCADE |
| person | FK → User | PROTECT |
| wbs | FK → WBSNode, null | SET_NULL; must belong to project |
| activity | FK → Activity, null | SET_NULL; must belong to project; if set, WBS should match activity.wbs |
| start_date / end_date | Date | end ≥ start |
| role | Char | assignment role label |
| capacity_percent | Decimal | ≥ 0; primary capacity unit |
| capacity_hours | Decimal, null | optional; if set without %, derive % via 8h day |
| work_location | Char, blank | |
| supervisor | FK → User, null | allocation supervisor |
| status | Char | `planned` \| `active` \| `completed` \| `cancelled` |
| has_capacity_exception | Bool, default False | |
| capacity_exception | FK → CapacityException, null | set when over-capacity approved |
| soft-delete / audit | Yes | `AuditSoftDeleteModel` |

**Invariants**:

- WBS/activity must be in same project when set.
- Inactive person → reject create/reactivate.
- Overlap sum + this row > available ⇒ require approved exception (see CapacityException).
- Soft-deleted rows excluded from capacity sums.

### CapacityException (new — `hr`)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| project | FK → Project | |
| person | FK → User | |
| allocation | FK → ResourceAllocation, null | may be set after allocation create, or pending payload |
| reason | Text | required on submit |
| status | Char | `draft` \| `submitted` \| `approved` \| `rejected` |
| requested_capacity_percent | Decimal | what would be allocated |
| overlapping_snapshot | JSON | optional ids / committed sum at decision time |
| created_by / submitted_at | audit | |
| decided_by / decided_at / decision_notes | | set on approve/reject |
| soft-delete / audit | Yes | retain approved history (no silent hard-delete) |

**State transitions**:

```text
draft → submitted → approved
                 ↘ rejected
```

Only `approved` authorizes over-capacity allocation persistence with `has_capacity_exception=True`.

### ApprovedLaborRate (new — `hr`)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| project | FK → Project | |
| person | FK → User, null | null = project default rate band (optional v1) |
| amount | Decimal | monetary |
| currency | Char | align with project currency rules (002) |
| effective_from / effective_to | Date | to null = open-ended |
| soft-delete / audit | Yes | |

**Visibility**: amount only in responses when caller has `view_wage`.

## Relationships

```text
User ──< ResourceAllocation >── Project
              │         │
              │         ├── WBSNode?
              │         └── Activity?
              └── CapacityException?
User ── org_unit → OrganizationUnit
User ── supervisor → User
Project + User ──< ApprovedLaborRate
```

## Validation rules (service layer)

1. `end_date >= start_date`.
2. Derive `capacity_percent` from hours when % omitted: `hours / 8 * 100`.
3. Capacity conflict query: overlapping date ranges for same person, non-deleted, status not `cancelled`.
4. Exception approve requires `approve_hr`; requester should preferably differ from approver (soft SoD; hard SoD deferred).
5. Wage/rate fields stripped in serializers without `view_wage`.

## Migration notes

- Additive User columns nullable/default-safe.
- New `hr` tables; seed permission codes.
- Backfill: no automatic ResourceAllocation from ProjectMember (explicit create only).
