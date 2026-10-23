# Data Model: Specialty Unit Reporting Source of Truth

**Feature**: `032-unit-report-source-truth`  
**Date**: 2026-10-22  
**Related contracts**: [unit-report-api.md](contracts/unit-report-api.md), [report-template-api.md](contracts/report-template-api.md), [daily-summary-api.md](contracts/daily-summary-api.md)

## Design Principles

1. Preserve existing report and source-row identifiers; evolve existing records instead of copying them to a parallel store.
2. Separate valid superseded history from deletion.
3. Resolve every project-scoped relation inside the project boundary.
4. Snapshot mutable template configuration before using it for historical completeness.
5. Represent provenance as a set of normalized sources, not a last-source field.
6. Normalize legacy data before adding canonical uniqueness constraints.

## Entities

### 1. `SpecialtyUnit` — canonical value object

Neutral stable vocabulary shared by reporting, department activity, template configuration, API contracts, and frontend routing:

| Value | Meaning |
|---|---|
| `buildings` | Buildings / ابنیه |
| `electrical` | Electrical / برق |
| `mechanical` | Mechanical / مکانیک |
| `machinery` | Machinery / ماشین‌آلات |
| `warehouse` | Warehouse / انبار |
| `security` | Security/HSE / حراست و HSE |

Rules:

- Values are language-independent and never user-editable.
- `inventory.Department` uses this same choice source during compatibility; it is not a second enum.
- Labels are localized by clients.

### 2. `ProjectTemplateRequiredUnit`

Declares the reporting-unit configuration offered by a reusable project template.

| Field | Meaning |
|---|---|
| `id` | Stable identifier |
| `template` | Parent `ProjectTemplate` |
| `unit` | Canonical `SpecialtyUnit` |
| `display_order` | Optional stable order for presentation |

Constraints:

- Unique `(template, unit)`.
- A newly created/updated template intended for reporting must contain at least one required unit.
- Editing this reusable configuration never changes an already activated project configuration.

### 3. `ProjectReportingConfiguration`

Immutable, effective-dated snapshot of a project’s reporting template.

| Field | Meaning |
|---|---|
| `id` | Configuration/version identifier returned in completeness metadata |
| `project` | Owning project |
| `source_template` | Template from which the configuration was activated |
| `effective_from` | First report date governed by this configuration |
| `activated_by`, `activated_at` | Audit identity and time |
| `supersedes` | Previous configuration for the project, if any |
| `source_template_name_snapshot` | Human-readable audit snapshot |

Related `ProjectReportingConfigurationUnit` rows snapshot the required canonical units and display order at activation.

Constraints and resolution:

- Unique `(project, effective_from)`.
- Configuration rows and their required-unit children are immutable after activation.
- Normal activation is append-only and must use a date later than the project’s latest activation. Backdated correction requires an explicit privileged migration/correction flow, impact preview, and audited rebuild of affected summaries.
- For a new summary, resolve the latest configuration where `effective_from <= report_date`; bind its identifier to the summary.
- Once bound, ordinary rebuilds use the bound configuration so later template edits cannot change historical completeness.
- If no configuration resolves, the summary has no configuration FK and reports `configuration_incomplete`.

### 4. Unit Daily Report — evolved `DisciplineSubReport`

The existing table and UUID are retained, while product/API naming becomes Unit Daily Report.

| Field | Meaning / migration behavior |
|---|---|
| `id` | Existing stable UUID; also the version identifier |
| `project`, `report_date` | Existing scope |
| `unit` | New canonical unit; nullable only during migration/quarantine |
| `legacy_discipline` | Preserved original discipline evidence; initially copied from existing `discipline` |
| `lineage_id` | Stable UUID shared by all versions of one project/date/unit report lineage |
| `version_number` | Monotonic integer starting at 1 within the lineage |
| `is_current` | Exactly one current version for a canonical project/date/unit key |
| `supersedes` | Previous version in the same lineage |
| `status` | `draft`, `submitted`, `approved`, or `rejected` |
| `created_by`, `created_at` | Preparer and preparation time from existing audit fields |
| `updated_by`, `updated_at` | Last change actor/time |
| `submitted_by`, `submitted_at` | Existing submission audit |
| `approved_by`, `approved_at` | Existing approval audit |
| `rejected_by`, `rejected_at`, `rejection_reason` | Complete rejection audit |
| `linked_daily_report` | Internal, server-owned link to project-day summary |
| `is_deleted`, `deleted_at` | Soft-delete evidence; deletion does not mean supersession |

Constraints:

- Unique current report on `(project, report_date, unit)` where `is_current=true`. Deleted current rows must be explicitly superseded or made non-current before another current row is created.
- Unique `(lineage_id, version_number)`.
- `supersedes` must share project/date/unit/lineage and have a lower version number.
- Product-visible rows require a valid canonical unit; quarantined migration rows are excluded.
- Submitted/approved content is immutable.
- Only the current version may transition or contribute.
- `linked_daily_report` is read-only to clients and must match project/date.

### 5. `UnitReportStatusEvent`

Append-only domain transition history.

| Field | Meaning |
|---|---|
| `report_version` | Unit-report version affected |
| `from_status`, `to_status` | Previous and next state; `from_status` may be empty for initial creation |
| `actor`, `occurred_at` | Decision identity and time |
| `reason` | Required for rejection; optional for correction/administrative actions |
| `event_type` | `created`, `submitted`, `approved`, `rejected`, `corrected`, `deleted`, `superseded` |

Rules:

- Events cannot be updated or deleted through product APIs.
- Historical pre-feature transitions are not fabricated. Migration creates a baseline event describing only the evidence present at migration time.

### 6. Report-owned source rows

#### `DepartmentActivityRecord`

Add nullable `unit_report` during migration, then require it for every new or mutable product row.

Rules:

- `project`, `department`, and `date` must equal parent report `project`, `unit`, and `report_date`.
- Create/update/delete/import is allowed only for the current parent in `draft` or `rejected` state, with active project membership, the corresponding report permission, and URL/object unit consistency.
- Existing unlinked rows are grouped and attached during migration or retained in quarantine/trace if no safe attachment is possible.
- Existing row identifiers remain unchanged.

#### Existing specialty child rows

`DisciplineSubReportActivity`, labor, material, concrete, general-activity, and note rows remain children of the evolved parent and retain identifiers. New detailed contracts for those section types are deferred. ID-aware updates preserve unchanged row IDs; blanket soft-delete/recreate updates are prohibited.

### 7. Project Daily Summary — existing `DailyReport`

Retain the existing full-shift materialized summary. Add/bind:

| Field | Meaning |
|---|---|
| `reporting_configuration` | Immutable configuration used for expected-unit completeness; null means configuration incomplete |
| `aggregation_fingerprint` | Stable fingerprint of current eligible source versions, source rows, configuration, and aggregation-owned inputs |
| `aggregated_at` | Existing last successful rebuild time |

Summary-owned values such as management opinion, weather override, and site-status override remain outside the aggregation fingerprint portion that could overwrite them. Their values participate in idempotency comparisons but are never replaced by rebuild.

### 8. `DailyReportDerivedSource`

Normalized provenance for every derived row or combined value.

| Field | Meaning |
|---|---|
| `daily_report` | Owning project daily summary |
| `derived_kind` | Stable section type, e.g. activity/labor/material/concrete |
| `derived_row_id` | Identifier of the derived row within that summary |
| `source_report` | Nullable FK to unit-report version for navigation/integrity |
| `source_report_id_snapshot` | Immutable source UUID even if a future retention action nulls the FK |
| `source_report_version` | Immutable version number snapshot |
| `source_unit` | Canonical unit snapshot |
| `source_row_kind` | Stable source collection/type |
| `source_row_id` | Stable string representation supporting both UUID and existing integer source IDs |
| `contribution_value` | Optional numeric contribution for explainable totals |
| `ordinal` | Deterministic presentation order |

Constraints:

- Unique `(derived_kind, derived_row_id, source_report_id_snapshot, source_row_kind, source_row_id)`.
- Source report must match the summary project/date at creation.
- Derived row must belong to the stated summary and kind.
- A single-source row has exactly one source; a combined value has all contributing sources.
- `can_view_source` is computed per requester and is never persisted as authorization state.

### 9. `UnitReportMigrationTrace`

Permanent accounting and rollback ledger.

| Field | Meaning |
|---|---|
| `source_system`, `source_model`, `source_id` | Original identity (`legacy_sub_report`, `department_activity`, etc.) |
| `original_category`, `original_deleted`, `original_link_id` | Pre-migration evidence |
| `canonical_unit` | Mapped unit, nullable for quarantine |
| `target_report` | Resulting report version, if resolved |
| `lineage_id`, `version_number`, `selected_current` | Collision/version outcome |
| `disposition` | `migrated`, `historical`, `duplicate_alias`, `quarantined` |
| `resolution_reason` | Human/audit explanation |
| `source_checksum`, `snapshot` | Accounting and rollback evidence |

Unique `(source_system, source_model, source_id)` makes the backfill resumable/idempotent.

### 10. `UnitReportMigrationQuarantine`

References a migration trace that cannot be mapped safely.

Fields include stable reason code, raw category/payload, detected time, optional resolution actor/time, and resolution notes. Quarantined rows remain readable to authorized migration operators, are not current, and never contribute to a project daily summary.

## Relationships

```text
ProjectTemplate
  └─ ProjectTemplateRequiredUnit

Project
  ├─ ProjectReportingConfiguration (effective-dated, immutable)
  │    └─ ProjectReportingConfigurationUnit (snapshot)
  ├─ Unit Daily Report lineage (existing DisciplineSubReport table)
  │    ├─ Unit Report Version(s)
  │    │    ├─ UnitReportStatusEvent
  │    │    ├─ DepartmentActivityRecord
  │    │    └─ existing specialty child rows
  │    └─ exactly one current version per project/date/unit
  └─ DailyReport (one current full-shift summary per date)
       ├─ derived child rows
       └─ DailyReportDerivedSource (one or many sources per derived row)
```

## State Transitions

```text
create/open ──> draft ──submit──> submitted ──approve──> approved
                  ^                    └─reject──> rejected
                  │                                  │
                  └──── edit while current ──────────┘

approved ──correct──> new current draft (version n+1)
                      prior approved version remains historical
```

Rules:

- `draft → submitted`: `edit_reports`, active project membership, and URL/object unit consistency.
- `submitted → approved`: `approve_reports`, active membership, SoD passes.
- `submitted → rejected`: `approve_reports`, non-empty reason.
- `rejected → submitted`: corrections saved, then `edit_reports` resubmits.
- `approved → correction`: explicit correction action creates a new version; it does not mutate the approved version.
- Delete is soft and allowed only for current draft/rejected versions; service removes/supersedes current status deterministically and triggers rebuild where prior eligible data existed.
- All transition checks reload and lock the current version before validating state.

## Aggregation Eligibility and Completeness

A report contributes only when all are true:

1. Same project and date as the summary.
2. Valid canonical unit.
3. `is_current=true`.
4. `is_deleted=false`.
5. Status is `submitted` or `approved`.
6. Not quarantined.

Completeness payload derives from the summary-bound reporting configuration:

- `expected_units`: required-unit snapshot.
- `contributing_units`: distinct eligible canonical units, including eligible non-required units.
- `missing_units`: expected minus contributing.
- `state=configuration_incomplete`: no bound/effective configuration.
- `state=partial`: configuration exists and missing is non-empty.
- `state=complete`: configuration exists and missing is empty.

An eligible report with zero detail rows counts as a contributing unit; detailed section validation is outside this feature.

## Deterministic Rebuild Rules

1. Acquire locks in the order Project → current unit report(s) → current full-shift DailyReport.
2. Select eligible reports ordered by `(unit, version_number, id)` and source rows by their domain order then stable ID.
3. Validate every source relation against project/date/unit scope.
4. Compute desired derived rows and complete provenance in memory using exact decimal operations.
5. Assign stable `derivation_key` values from section/business key/source identity.
6. Upsert desired derived rows, replace their provenance set, and remove obsolete derived keys only.
7. Update aggregation metadata/fingerprint with explicit `update_fields`; never blanket-save stale summary-owned values.
8. Repeated identical inputs produce identical logical derived rows, ordered provenance, completeness, and preserved overrides.

## Migration and Rollback Invariants

Before canonical constraints are enabled:

- Every source report/row ID is present in the trace exactly once.
- Every valid legacy report is mapped to a version or explicitly quarantined.
- All child IDs, states, known actors/times, rejection text, and summary links are unchanged or traceably repointed.
- Every canonical project/date/unit group has at most one current version.
- Unknown categories are not guessed.
- Exact duplicate aliases cannot contribute twice.

Rollback:

- During the compatibility window, reconstruct original categories, links, and pre-feature current interpretation from the permanent trace; new columns/tables may remain during expand rollback.
- Before canonical-only unit reports exist, forward/backward/forward migration rehearsal must preserve all stable ID sets.
- After Machinery/Warehouse/Security reports exist, rollback to the legacy taxonomy requires verified backup restore plus controlled export/replay; a reverse enum mapping is invalid.
