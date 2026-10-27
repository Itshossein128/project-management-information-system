# Data Model: Discipline Sub-Reports Lifecycle and Validation

## Entities and Schema Extensions

### 1. `DisciplineSubReport` (Modified)
Table: `discipline_sub_reports`

| Field | Type | Modifiers | Description |
|---|---|---|---|
| `sub_discipline` | `CharField(max_length=20)` | `blank=True, default=''` | Secondary taxonomy tag under canonical unit. Under `mechanical`: `MECHANICAL`, `PLUMBING`, `HVAC`. Under `buildings`: `CIVIL`, `FINISHING`. |

#### Constraints & Business Rules:
- Canonical 6-unit architecture remains top-level (`unit` field: `buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, `security`).
- `sub_discipline` classifies specialized craft workflows without splitting master daily reporting rollups.

---

### 2. `DisciplineSubReportActivity` (Modified)
Table: `discipline_sub_report_activities`

| Field | Type | Modifiers | Description |
|---|---|---|---|
| `execution_percentage` | `DecimalField(max_digits=5, decimal_places=2)` | `null=True, blank=True` | Daily physical execution percentage. Must satisfy `0.00 <= execution_percentage <= 100.00`. Null indicates unmeasured progress. |
| `shift_hours` | `DecimalField(max_digits=4, decimal_places=2)` | `default=8.00` | Duration of the work shift in hours (defaults to 8.00 hours). |
| `is_hydrostatic_tested` | `BooleanField` | `default=False` | Flag indicating whether hydrostatic/pressure testing was conducted during this activity. |
| `test_pressure_bar` | `DecimalField(max_digits=6, decimal_places=2)` | `null=True, blank=True` | Applied pressure in Bar during the test. Required and must be > 0 if `is_hydrostatic_tested=True`. |
| `test_duration_minutes` | `PositiveIntegerField` | `null=True, blank=True` | Holding time of the test in minutes. |
| `test_outcome` | `CharField(max_length=10)` | `choices=['PASSED', 'FAILED'], blank=True, default=''` | Outcome of the pressure test. |
| `tested_segment` | `CharField(max_length=120)` | `blank=True, default=''` | Identification of the tested piping segment/riser/circuit. |
| `qc_inspection` | `ForeignKey('risk.Inspection')` | `on_delete=SET_NULL, null=True, blank=True, related_name='tested_sub_report_activities'` | Linkage to quality inspection record in QA module. |

#### Constraints & Validation Rules:
- **Range Check**: If `execution_percentage` is non-null, `0.00 <= execution_percentage <= 100.00`. Violation error code: `percent_must_be_between_0_and_100`.
- **Pressure Value Check**: If `is_hydrostatic_tested=True`, `test_pressure_bar` must be > 0. Violation error code: `invalid_test_pressure_value`.

---

### 3. `SubcontractorLaborLedgerEntry` (New)
Table: `subcontractor_labor_ledger_entries`

| Field | Type | Modifiers | Description |
|---|---|---|---|
| `id` | `UUIDField` | `primary_key=True, default=uuid4` | Unique ledger entry identifier. |
| `project` | `ForeignKey('projects.Project')` | `on_delete=CASCADE, related_name='subcontractor_labor_ledger'` | Project scope. |
| `contractor` | `ForeignKey('projects.Stakeholder')` | `on_delete=CASCADE, related_name='labor_ledger_entries'` | Referenced contractor stakeholder. |
| `sub_report` | `ForeignKey('sub_reports.DisciplineSubReport')` | `on_delete=CASCADE, related_name='contractor_labor_entries'` | Source approved sub-report. |
| `activity_row` | `ForeignKey('sub_reports.DisciplineSubReportActivity')` | `on_delete=CASCADE, related_name='labor_ledger_entries'` | Source activity row. |
| `report_date` | `DateField` | `db_index=True` | Date of the work shift. |
| `discipline` | `CharField(max_length=20)` | `blank=True, default=''` | Discipline or unit name. |
| `foreman_count` | `PositiveIntegerField` | `default=0` | Authoritative foreman count from activity row. |
| `worker_count` | `PositiveIntegerField` | `default=0` | Authoritative worker count from activity row. |
| `shift_hours` | `DecimalField(max_digits=4, decimal_places=2)` | `default=8.00` | Working shift duration in hours. |
| `total_person_hours` | `DecimalField(max_digits=8, decimal_places=2)` | `default=0.00` | Computed person-hours: `(foreman_count + worker_count) * shift_hours`. |
| `status` | `CharField(max_length=20)` | `choices=['PENDING', 'APPROVED'], default='APPROVED'` | Ledger status. |
| `created_at` | `DateTimeField` | `auto_now_add=True` | Record creation timestamp. |
| `updated_at` | `DateTimeField` | `auto_now=True` | Last update timestamp. |

#### Constraints:
- `UniqueConstraint(fields=['activity_row'], name='unique_subcontractor_ledger_per_activity_row')` ensures idempotency when re-approving or refreshing ledger entries.

---

## Operational Submission Guard

When submitting a sub-report (`submit_unit_report` / `submit_sub_report`), the system evaluates:

```python
active_rows_count = (
    report.activities.filter(is_deleted=False).count() +
    report.labor_entries.filter(is_deleted=False).count() +
    report.material_entries.filter(is_deleted=False).count() +
    report.concrete_entries.filter(is_deleted=False).count() +
    report.machinery_rows.filter(is_deleted=False).count() +
    report.general_activities.filter(is_deleted=False).count()
)
if active_rows_count == 0:
    raise UnitReportError(
        _('cannot_submit_empty_sub_report_detail'),
        code='cannot_submit_empty_sub_report',
    )
```

## State Machine & Transitions

```
[DRAFT]
   │
   ├─ submit (Guards: active_rows_count > 0, validate sections, link QC inspections)
   ▼
[SUBMITTED]
   │
   ├─ approve (Guards: SoD check, generates SubcontractorLaborLedgerEntry rows)
   ▼
[APPROVED]
   │
   ├─ correct (Creates version N+1 in DRAFT state, marks N superseded)
   ▼
[DRAFT (vN+1)]
```
