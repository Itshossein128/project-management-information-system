# Data Model: Physical Progress & Periodic Reports (FR-PRG)

## Entities

### ActivityMeasurementDefinition

Current measurement setup for one activity.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| project | FK → Project | Denormalized for tenancy queries |
| activity | FK → Activity | Unique current definition per activity |
| method | enum | `quantity` \| `weighted_milestones` \| `evidence_percent` |
| status | enum | `draft` \| `approved` |
| total_quantity | decimal, null | Required when method=`quantity` and approved |
| unit_id | FK Unit, null | With quantity method |
| milestones | JSON / child rows | List `{name, weight}` for weighted method; weights must sum ≈ 1 when approved |
| evidence_rules | text/JSON, blank | For evidence_percent |
| current_version | FK → Version, null | Points at last approved version |
| approved_at / approved_by | datetime / user, null | |
| audit / soft-delete | standard | |

**Validation**: Cannot set `approved` if quantity method lacks total+unit, or milestones incomplete, or evidence_percent lacks rules text.

### ActivityMeasurementVersion

Immutable snapshot created on each approval (initial or method change).

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| definition | FK → Definition | |
| version_number | int | Monotonic per activity |
| method | enum | Copied |
| basis_snapshot | JSON | totals, milestones, rules at approve time |
| approved_at / approved_by | | |
| change_reason | text | Required when not first version |

Historical `ActivityProgress` rows keep `measurement_version_id` forever.

### ActivityQuantityChange (lightweight exception for >100%)

Optional approved increase of basis quantity.

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| activity | FK | |
| previous_total / new_total | decimal | |
| status | draft \| approved \| rejected | |
| reason | text | |
| approved_at / approved_by | | |

When **approved**, progress calc may exceed prior 100% relative to old total up to new total (still reject if >100% of **new** total).

### ActivityProgress (extended)

Existing table; additive fields:

| Field | Type | Notes |
|-------|------|-------|
| period_progress | decimal 0–1, null | Incremental for that `report_date` window (or derived at read time) |
| approved_progress | decimal 0–1, null | Technically approved cumulative as-of this row |
| measurement_version | FK, null | Method version that produced this row |
| technical_approved_at / by | datetime / user, null | |
| evidence_refs | JSON, blank | Photo/file ids — never alone set approved |

Existing: `planned_progress`, `actual_progress` (treat as cumulative recorded), `cumulative_quantity`, `source`, `notes`.

**Rules**:
- Write rejects if no **approved** measurement definition for activity (except read-only dashboard of zeros/nulls).
- Reject if computed cumulative > 1.0 without covering approved quantity change.
- Photo/evidence does not set `approved_progress` or `technical_approved_at`.

### ProjectPeriodReport

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| project | FK | |
| kind | weekly \| monthly | |
| period_start / period_end | date | |
| status | generated \| superseded | |
| generated_at / generated_by | | |
| superseded_by | FK self, null | |
| title | string | Localized display helper |

Unique active: one non-superseded report per (project, kind, period_start, period_end).

### PeriodReportFigure

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| report | FK | |
| section | string | e.g. `critical_activities`, `cost`, `baseline_variance` |
| label_key | string | i18n key |
| value | decimal/JSON/text, null | |
| value_status | recorded \| not_recorded | |
| source_type | string | `daily_report`, `activity_progress`, `baseline`, `cost`, … |
| source_id | UUID, null | |
| source_path | string | Client-resolvable path for one-step navigation |
| source_approved | bool | |
| last_updated_at | datetime, null | |

### PeriodReportFigureOverride

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | PK |
| figure | FK | |
| old_value / new_value | | |
| reason | text, required | |
| created_by / created_at | | |

Direct figure value mutation without override row is forbidden.

## Relationships

```text
Project 1──* Activity 1──1 ActivityMeasurementDefinition 1──* ActivityMeasurementVersion
Activity 1──* ActivityProgress *──1 ActivityMeasurementVersion
Activity 1──* ActivityQuantityChange
Project 1──* ProjectPeriodReport 1──* PeriodReportFigure 1──* PeriodReportFigureOverride
```

## State transitions

### Measurement definition / version

```text
draft ──approve──► approved (creates Version N)
approved ──submit change──► draft (new pending basis) ──approve──► approved (Version N+1)
                          └──reject/cancel──► remain on prior approved version
```

### Period report

```text
(generate) → generated
(generate same period again) → prior generated → superseded; new generated
```

### Progress approval

```text
recorded (actual/period) ──technical approve──► approved_progress updated
daily_report approved ──recalc──► may advance approved_progress when rules met
```

## Validation summary

| Rule | Code (suggested) |
|------|------------------|
| No approved measurement | `measurement_not_approved` |
| Incomplete milestones / missing total | `incomplete_measurement_basis` |
| % > 100 without approved qty change | `progress_exceeds_100` |
| Photo-only treat as approved | forbidden (`photo_not_technical_approval`) |
| Figure PATCH without override | `figure_immutable` |
| Method change without reason (non-first) | `method_change_reason_required` |
