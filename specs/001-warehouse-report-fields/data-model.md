# Data Model: Warehouse Report Fields

**Feature**: `001-warehouse-report-fields`  
**Date**: 2026-10-01

## Entities

### DepartmentActivityRecord (extended)

Project-scoped activity/movement log row keyed by `department`.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | UUID/PK (existing) | required | Unchanged |
| project | FK → Project | CASCADE | Unchanged |
| department | string enum | required, indexed | Includes `warehouse` |
| date | date | required | Shared |
| location | string(255) | blank allowed | **Required for non-warehouse**; empty for warehouse |
| activity_description | string(500) | blank allowed | **Required for non-warehouse**; empty for warehouse |
| contractor | string(255) | blank allowed | **Required for non-warehouse**; empty for warehouse |
| unit | string(64) | blank allowed | Required when `department_uses_unit` (includes warehouse); empty for security |
| description | text | blank | Optional notes (shared) |
| material_type | string(255) | blank allowed, default `''` | **Required for warehouse** |
| quantity_in | decimal(14,3) | default `0` | Warehouse inbound; ≥ 0 |
| quantity_out | decimal(14,3) | default `0` | Warehouse outbound; ≥ 0 |
| consumption_location | string(255) | blank allowed, default `''` | **Required for warehouse** |
| supplier | string(255) | blank allowed, default `''` | **Required for warehouse** |
| created_at / updated_at | datetime | auto | Unchanged |

**Indexes**: Keep existing `(project, department, date)` and `(project, department)`. No new uniqueness constraint (duplicate date+material allowed).

### Department (unchanged enum)

`buildings` | `mechanical` | `security` | `machinery` | `warehouse` | `electrical`

### Helpers (logical, not tables)

- `department_uses_unit(department)` — existing; warehouse → true
- `is_warehouse_department(department)` — new; true only for `warehouse`

## Validation Rules

### Non-warehouse (unchanged behavior)

- Required: `date`, `location`, `activity_description`, `contractor`
- `unit` required except security (cleared)
- Warehouse fields must be cleared to empty/`0` on write

### Warehouse

- Required: `date`, `material_type`, `unit`, `consumption_location`, `supplier`
- Optional: `description`
- `quantity_in` ≥ 0, `quantity_out` ≥ 0
- At least one of `quantity_in`, `quantity_out` must be > 0
- Generic fields `location`, `activity_description`, `contractor` cleared to `''` on write

### Shared length limits

- Reject values exceeding field max lengths with field errors (prefer reject over silent truncate at API boundary; import may still clamp after validation of non-empty required presence—prefer consistent reject in serializer).

## State Transitions

None. Records are created/updated/deleted; no approval workflow in this feature.

## Migration Strategy

1. Add warehouse columns with defaults (`''` / `0`).
2. Alter `location`, `activity_description`, `contractor` to allow blank.
3. No data backfill/remap for existing warehouse rows.
4. Rollback: reverse migration drops new columns and restores `blank=False` only if no blank generic values were persisted—document that post-deploy warehouse-created rows may block reverse without data cleanup.

## Relationships

```text
Project 1──* DepartmentActivityRecord
DepartmentActivityRecord.department ∈ Department choices
```
