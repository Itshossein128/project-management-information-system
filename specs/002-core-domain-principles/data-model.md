# Data Model: Core Domain Principles & Glossary

**Feature**: `002-core-domain-principles`  
**Date**: 2026-10-07

## Entities

### 1. Project (extend existing `projects.Project`)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `currency` | CharField | choices `IRR`, `IRT`; default `IRR`; max_length 3 | Project base money unit (FR-006) |
| existing fields | — | unchanged | `project_code` unique, status, dates, etc. |

**Validation**:
- `currency` required on create after migration (default applied for legacy rows).
- Money aggregates for the project MUST use this currency unless an explicit conversion rate is supplied.

**State**: No new status machine in this feature (project lifecycle belongs to spec 03).

### 2. WBS (harden existing `projects.WBS`)

| Change | Rule |
|--------|------|
| Soft-delete + audit | Add `is_deleted`, `deleted_at`, `created_by`, `updated_by` (or migrate to `AuditSoftDeleteModel` pattern) |
| Delete policy | Soft-delete only; block if children/activities/cost/progress links require (align FR-007; extend existing child/activity guards) |

**Note**: Keep treebeard hierarchy; soft-delete filters default manager to `is_deleted=False`.

### 3. ProjectCapabilitySetting (new)

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | UUID PK | |
| `project` | FK → Project | CASCADE; indexed |
| `capability_key` | CharField | max_length 64; stable English code |
| `enabled` | Boolean | default True |
| `mode` | CharField | `required` \| `optional` \| `disabled`; default `optional` |
| `created_at` / `updated_at` | DateTime | |
| `created_by` / `updated_by` | FK User | PROTECT / SET_NULL |

**Unique**: (`project`, `capability_key`)

**Validation**:
- `capability_key` ∈ seeded catalog (see contracts).
- When `mode=disabled` or `enabled=False`: block create/mutate for that capability; allow read of historical records.

**Seed keys (initial)**: `risk`, `economic`, `procurement`, `cash_flow`, `documents`, `alerts`, `subcontractors` (adjust to nav keys during implement).

### 4. FiscalPeriodLock (new)

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | UUID PK | |
| `project` | FK → Project | CASCADE |
| `period_start` | Date | required |
| `period_end` | Date | required; ≥ period_start |
| `closed_at` | DateTime | required on create |
| `closed_by` | FK User | PROTECT |
| `reason` | Text | required; min length 3 |
| `is_active` | Boolean | default True (soft-unlock sets False with audit) |

**Validation**:
- No overlapping active locks for the same project (reject or merge policy: reject overlap).
- Mutations of in-scope financial records with document date ∈ [start, end] blocked unless corrective path.

### 5. Notification (extend existing)

| Field | Type | Constraints |
|-------|------|-------------|
| `responsible_user` | FK User | null=True; SET_NULL |
| `due_at` | DateTime | null=True |
| existing `link`, `user`, `project`, `title`, … | unchanged | |

**Validation**:
- Actionable types: `responsible_user` and `link` required; `due_at` required when type is time-bound.

### 6. Money helper (not a table)

Logical value object used in services:

- `amount: Decimal`
- `currency: IRR | IRT`
- Refuse `sum` across differing currencies without `rate: Decimal` and `target_currency`.

### 7. Glossary bindings (locale keys, not DB)

Canonical keys (examples):

| Key | FA | EN |
|-----|----|----|
| `glossary.wbs` | ساختار شکست کار (WBS) | Work Breakdown Structure (WBS) |
| `glossary.commitment` | تعهد مالی | Financial commitment |
| `glossary.actualCost` | هزینه واقعی | Actual cost |
| `glossary.ipc` | صورت‌وضعیت | Payment certificate (IPC) |
| `glossary.ev` | ارزش کسب‌شده (EV) | Earned value (EV) |

UI must reference these (or existing equivalent keys updated to match).

## Relationships

```text
Project 1──* ProjectCapabilitySetting
Project 1──* FiscalPeriodLock
Project 1──* WBS (soft-deletable)
User 1──* Notification (recipient)
User 1──* Notification.responsible_user
```

## Delete / correction rules

| Record class | Delete behavior |
|--------------|-----------------|
| Draft / non-final | Soft-delete allowed |
| Approved / final / paid | Soft-delete or reversal document only; hard delete forbidden |
| Capability disabled | No delete of history; mutate/create blocked |
| Fiscal locked period | Ordinary update/delete blocked; corrective flag + reason + audit required |

## Migration notes

- Additive columns preferred; backfill `Project.currency='IRR'`.
- WBS soft-delete migration must preserve tree integrity; default manager excludes deleted.
- No destructive drop of financial history.
