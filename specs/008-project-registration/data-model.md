# Data Model: Project Registration & Kickoff (FR-PRJ)

**Feature**: `008-project-registration`  
**Date**: 2026-10-08

## Entities

### Project (extend existing)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | existing |
| project_code | Char(30) unique | FR-PRJ-007 |
| project_name | Char(200) | required |
| purpose | Text blank | NEW |
| scope_description | Text blank | NEW; required non-blank for activate |
| main_deliverables | Text blank | NEW |
| employer | Char(120) | protected when active |
| contractor / consultant | Char | existing; not protected by FR-PRJ-006 |
| project_manager | FK User null | required for activate |
| location | Text | execution location |
| start_date / planned_finish_date | Date null | protected when active |
| contract_type | Char | existing |
| contract_number | Char(60) blank | NEW |
| contract_amount | Decimal null | budget ceiling; protected when active |
| currency | Char | existing |
| owning_unit | FK OrganizationUnit null | existing |
| status | Char choices | see Status |
| budget_approved_at | DateTime null | NEW |
| budget_approved_by | FK User null | NEW |
| created_at / updated_at | | existing |

**Status values**: `draft` | `pending_approval` | `active` | `suspended` | `completed` | `archived`

**Default on create**: `draft`

**Migration**: `handed_over` → `completed`; existing `active` with amount → set `budget_approved_at` ≈ `created_at`

### ProjectKickoffCharter (new)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| project | OneToOne Project | CASCADE |
| justification | Text | |
| success_criteria | Text | |
| constraints | Text | |
| assumptions | Text | |
| key_stakeholders_summary | Text | |
| pm_authority | Text | |
| created_by / updated_by | FK User | audit pattern |
| created_at / updated_at | | |
| soft-delete fields | | if using AuditSoftDeleteModel |

### ProjectChangeRequest (new)

| Field | Type | Notes |
|-------|------|-------|
| id | UUID PK | |
| project | FK Project | CASCADE |
| reason | Text | min length 10 |
| status | Char | `draft` \| `submitted` \| `approved` \| `rejected` \| `cancelled` |
| proposed_changes | JSON | keys ⊆ protected set; values proposed |
| previous_values | JSON | snapshot at submit/approve time |
| requested_by | FK User | |
| requested_at | DateTime | |
| decided_by | FK User null | |
| decided_at | DateTime null | |
| decision_notes | Text blank | |
| audit / soft-delete | | preferred |

**Protected keys**: `start_date`, `planned_finish_date`, `contract_amount`, `employer`, `scope_description`

## Relationships

```text
Project 1 ── 0..1 ProjectKickoffCharter
Project 1 ── * ProjectChangeRequest
Project * ── 0..1 User (project_manager)
Project * ── 0..1 OrganizationUnit (owning_unit)
```

## Status transitions

```text
draft ──submit──► pending_approval ──approve──► active
  ▲                      │
  └──────reject──────────┘
active ──suspend──► suspended ──resume──► active
active|suspended ──complete──► completed
completed|active|suspended ──archive──► archived
```

- Illegal transitions → 400 `invalid_status_transition`
- `approve` → active requires: `project_manager_id`, `scope_description` strip nonempty, `contract_amount` not null, and sets/keeps `budget_approved_at`
- No transition into `draft` from `active` (use CR for field fixes; status reopen only via suspend/resume as above)

## Validation rules

1. `project_code` unique; strip; nonempty on create.
2. Create may omit PM/scope/budget; activate may not.
3. While `status in (active, suspended, completed, archived)`: PATCH of protected keys without approved CR path → `protected_field_requires_change_request`.
4. Draft/pending: protected keys editable via normal PATCH (not yet “approved identity”).
5. Open CR uniqueness: at most one `draft`/`submitted` CR per project.
6. Archived: mutations denied except system admin (status already archived; field/charter edits blocked).
7. Baseline lock / binding commitment: only `status == active` (see [commitment-and-baseline-gates.md](./contracts/commitment-and-baseline-gates.md)).

## Uniqueness / indexes

- Keep unique `project_code`
- Index `Project.status` for portfolio filters
- Partial unique optional: one open CR per project (enforce in service with select_for_update if DB partial unique not used)
