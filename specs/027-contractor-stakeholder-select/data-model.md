# Data Model: Contractor Stakeholder Select

## Classification — `projects.Stakeholder` (existing)

| Field | Change | Rules |
|-------|--------|-------|
| `role` | Behavior only | Canonical contractor code: `contractor`. Accept write aliases `پیمانکار`, `Contractor`, `contractor` → store `contractor`. Other roles remain free text or pre-defined UI options as today. |
| `status` | Unchanged | Only `active` contractors appear in new pickers. |
| Soft-delete | Unchanged | Soft-deleted excluded from pickers; historical FKs may SET_NULL or remain if not deleted. |

**Contractor predicate** (shared server helper):

```text
project_id = current project
AND is_deleted = false
AND status = active
AND role = 'contractor'
```

## Operational FKs (additive)

### `inventory.DepartmentActivityRecord`

| Field | Type | Rules |
|-------|------|-------|
| `contractor_ref` | FK → `Stakeholder`, null, SET_NULL | Required for non-warehouse create/update when contractor is required. Must satisfy contractor predicate and `stakeholder.project_id == record.project_id`. |
| `contractor` | CharField (existing) | Denormalized snapshot of `contractor_ref.name` on write; cleared when warehouse path clears contractor; retained for display/export when FK later null. |

**Legacy rows**: `contractor_ref` null with non-empty `contractor` string — readable; on edit must set `contractor_ref` (or clear per form rules).

### `field_reports.DailyReportActivity`

| Field | Type | Rules |
|-------|------|-------|
| `contractor_ref` | FK → `Stakeholder`, null, SET_NULL | Preferred identity for پیمانکار picker. Same-project contractor predicate. |
| `subcontractor_name` | CharField (existing) | Snapshot from `contractor_ref.name` when FK set. |
| `subcontractor_ref` | FK → `Contract` (existing) | Unchanged schema; picker no longer writes it in this feature. |

### Labor camp entries (`DailyReportLaborCamp` / shared base / `LaborCampReport` as applicable)

| Field | Type | Rules |
|-------|------|-------|
| `contractor_ref` | FK → `Stakeholder`, null, SET_NULL | Same rules when پیمانکار is collected. |
| `subcontractor_name` | CharField (existing) | Snapshot from FK when set. |

### `projects.Project`

| Field | Type | Rules |
|-------|------|-------|
| `contractor_ref` | FK → `Stakeholder`, null, SET_NULL | Optional main contractor party; same-project contractor predicate. |
| `contractor` | CharField (existing) | Snapshot from FK when set; blank allowed. |

## Validation rules

1. FK project must equal owning record’s project (IDOR-safe via project-scoped queryset + explicit check).
2. Role must be `contractor` at time of **new** selection; inactive/non-contractor rejected with field error.
3. Import of department activities: پیمانکار cell must resolve to exactly one active contractor by UUID or exact trimmed name; else row error (no silent create).
4. Warehouse department path continues to clear contractor fields (existing behavior).

## State / transitions

| Event | Effect on pickers | Effect on history |
|-------|-------------------|-------------------|
| Stakeholder created with role=contractor, status=active | Appears in options | — |
| Status → inactive or role changed away from contractor | Removed from options | Existing snapshots + FKs remain for display |
| Soft-delete stakeholder | Removed from options; FKs SET_NULL | Snapshot CharField still shows prior name |

## Relationships (conceptual)

```text
Project
  └── Stakeholder (role=contractor, status=active)  ← options source
        ↑
        ├── DepartmentActivityRecord.contractor_ref
        ├── DailyReportActivity.contractor_ref
        ├── LaborCamp*.contractor_ref
        └── Project.contractor_ref
```
