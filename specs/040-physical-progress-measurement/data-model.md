# Data Model: Physical Progress Measurement, Financial Governance & Technical Approval

## Feature: `specs/040-physical-progress-measurement`

### 1. Unified Enums

#### `MeasurementMethod` (Schedule Domain)
- `quantity_based`: Ratio of executed physical units to total estimated quantity (`quantity_actual / total_quantity`).
- `weighted_milestones`: Cumulative progress based on completed milestone steps whose weights sum to 100%.
- `evidence_based`: Documented and technical rule-governed progression with engineering sign-off.
- *Aliases for backward compatibility*:
  - `quantity` → normalizes to `quantity_based`
  - `evidence_percent` → normalizes to `evidence_based`

#### `MeasurementStatus`
- `draft`: Proposed or in-modification measurement definition. Not usable for progress writes until approved.
- `approved`: Officially stamped basis with an immutable snapshot version (`ActivityMeasurementVersion`).

#### `ActivityQuantityChangeStatus`
- `draft`: Requested quantity change pending approval.
- `approved`: Approved increase in total estimated quantity; increases the 100% ceiling.
- `rejected`: Rejected change request; original ceiling remains in force.

---

### 2. Entity Schemas & Relationships

#### `ActivityMeasurementDefinition`
```text
Table: activity_measurement_definitions
PK: id (UUID)
FK: project_id -> projects.Project (CASCADE)
OneToOne: activity_id -> projects.Activity (CASCADE)
Fields:
  - method: VARCHAR(30) (quantity_based | weighted_milestones | evidence_based)
  - status: VARCHAR(20) (draft | approved)
  - total_quantity: DECIMAL(18, 4), nullable
  - unit_id: FK -> master_data.Unit, nullable
  - milestones: JSONB (list of objects: [{"name": string, "weight": float}])
  - evidence_rules: TEXT, blank=True
  - pending_change_reason: TEXT, blank=True
  - current_version_id: FK -> ActivityMeasurementVersion, nullable
  - approved_at: TIMESTAMP WITH TIME ZONE, nullable
  - approved_by_id: FK -> auth.User, nullable
  - created_at, updated_at, created_by_id, updated_by_id
```

#### `ActivityMeasurementVersion`
```text
Table: activity_measurement_versions
PK: id (UUID)
FK: definition_id -> ActivityMeasurementDefinition (CASCADE)
Fields:
  - version_number: INTEGER (positive)
  - method: VARCHAR(30)
  - basis_snapshot: JSONB ({
      "method": string,
      "total_quantity": string | null,
      "unit_id": string | null,
      "unit_symbol": string,
      "milestones": list,
      "evidence_rules": string
    })
  - change_reason: TEXT, blank=True
  - approved_at: TIMESTAMP WITH TIME ZONE
  - approved_by_id: FK -> auth.User
Constraints:
  - UNIQUE (definition_id, version_number)
```

#### `ActivityQuantityChange`
```text
Table: activity_quantity_changes
PK: id (UUID)
FK: project_id -> projects.Project (CASCADE)
FK: activity_id -> projects.Activity (CASCADE)
Fields:
  - previous_total: DECIMAL(18, 4)
  - new_total: DECIMAL(18, 4)
  - status: VARCHAR(20) (draft | approved | rejected)
  - reason: TEXT
  - approved_at: TIMESTAMP WITH TIME ZONE, nullable
  - approved_by_id: FK -> auth.User, nullable
  - created_at, updated_at, created_by_id, updated_by_id
```

#### `ActivityProgress`
```text
Table: activity_progress
PK: id (UUID)
FK: activity_id -> projects.Activity (CASCADE)
Fields:
  - report_date: DATE
  - planned_progress: DECIMAL(6, 3), nullable (fraction 0..1)
  - actual_progress: DECIMAL(6, 3), nullable (fraction 0..1)
  - cumulative_quantity: DECIMAL(18, 4), nullable
  - period_progress: DECIMAL(6, 3), nullable (delta in period)
  - approved_progress: DECIMAL(6, 3), nullable (officially approved fraction 0..1)
  - source: VARCHAR(20) ('daily_report' | 'manual')
  - notes: TEXT
  - measurement_version_id: FK -> ActivityMeasurementVersion, nullable
  - technical_approved_at: TIMESTAMP WITH TIME ZONE, nullable
  - technical_approved_by_id: FK -> auth.User, nullable
  - evidence_refs: JSONB (key-value technical references)
  - updated_by_id: FK -> auth.User, nullable
Constraints:
  - UNIQUE (activity_id, report_date)
```

#### `IPCItem` (Contracts Domain)
```text
Table: ipc_items
PK: id (UUID)
FK: ipc_id -> contracts.IPC (CASCADE)
FK: contract_item_id -> contracts.ContractItem (CASCADE)
Fields:
  - description: VARCHAR(255)
  - unit: VARCHAR(40)
  - unit_price: DECIMAL(18, 2)
  - qty_previous: DECIMAL(18, 4)
  - qty_current: DECIMAL(18, 4)  <-- Computed strictly from approved_progress delta
  - qty_cumulative: DECIMAL(18, 4)
  - amount_current: DECIMAL(18, 2)
  - amount_cumulative: DECIMAL(18, 2)
```

---

### 3. Derived View Representation: Four-Way Progress + Physical Period Quantity

When querying `GET /api/v1/projects/:projectId/progress/activities/`:
Each row is serialized with:
- `activity_id`: UUID string
- `activity_code`: string
- `activity_name`: string
- `wbs_code`, `wbs_name`: string
- `weight`: float
- `planned_progress_pct`: float (0..100)
- `actual_progress_pct` / `cumulative_progress_pct`: float (0..100)
- `period_progress_pct`: float (0..100)
- `approved_progress_pct`: float (0..100)
- `variance_pct`: float (signed)
- `total_quantity`: float | null (effective total approved quantity)
- `cumulative_quantity`: float | null
- `period_quantity`: float | null (physical volume executed in [period_start, period_end])
- `unit`: string (measurement unit symbol or name)
- `measurement_method`: string (`quantity_based` | `weighted_milestones` | `evidence_based`)
- `measurement_status`: string (`draft` | `approved` | `not_defined`)
- `measurement_version_id`: UUID string | null
- `status`: string (`not_started` | `in_progress` | `suspended` | `completed`)
- `is_behind`: boolean

---

### 4. Integrity and Validation Invariants

1. **Approved Measurement Invariant**: Progress entries (`ActivityProgress`, `DailyReportActivity`, `DisciplineSubReportActivity`) referencing an activity MUST reject writes if the activity has no approved `ActivityMeasurementVersion` (`measurement_not_approved`).
2. **Weight Sum Invariant**: Weighted milestones MUST sum to 1.0 (100%) within `±0.01%` tolerance before approval (`incomplete_measurement_basis`).
3. **No Clamping Invariant**: Any progress submission that would cause cumulative progress to exceed 100% of the active approved total quantity ceiling without an approved `ActivityQuantityChange` MUST be synchronously rejected with HTTP 400 and error code `progress_exceeds_100`.
4. **Monetization Invariant**: In `auto_populate_ipc`, `qty_current = approved_progress_delta * total_quantity`. If `approved_progress` is null/0, `qty_current = 0` regardless of `actual_progress`.
5. **Technical Approval Invariant**: Photo-only basis (`basis: "photo"`) is rejected with HTTP 400 `photo_not_technical_approval`. Technical approval requires user permission `approve_reports`.
