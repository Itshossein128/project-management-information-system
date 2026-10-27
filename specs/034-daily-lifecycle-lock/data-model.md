# Data Model: Daily Report Lifecycle Lock

## Schema impact

No migration is planned. The feature uses existing report, correction-request, child-row, approval, and provenance fields. A migration-drift check proves this remains true after implementation.

## Entities and relationships

### DailyReport

| Field / relation | Lifecycle rule |
|---|---|
| `lineage_id` | Stable identity shared by every version of one report history. |
| `version_number` | Starts at 1 and increments by exactly one for a correction. |
| `supersedes` | Points from a correction draft to its approved predecessor. |
| `status` | Governs submit/review/approve/reject. Approved reports are locked. |
| `is_current` | Exactly one non-deleted version is current; it moves to the draft on correction and back to the predecessor on cancellation. |
| `created_by` / `updated_by` | Supply version modifier identity under the selected existing audit semantics. |
| `approved_at` | Formal approval time; nullable for unapproved versions. |

### DailyReportCorrectionRequest

| Field / relation | Lifecycle rule |
|---|---|
| `source_report` | Approved predecessor from which correction begins and to which cancellation restores current status. |
| `result_report` | Temporary next-version draft; soft-deleted on successful cancellation. |
| `reason` | Belongs to the result version’s metadata, never retroactively to source. |
| `status` | Open statuses may be cancelled; approving the result closes it as approved. |
| `project` | Authorization boundary for list/open/cancel. |

### Child rows copied into a correction

| Row family | Data preserved | Excluded |
|---|---|---|
| Activity | Existing activity/details, subcontractor and contractor references, crew name, foreman/worker counts, parcel/location, quantity/measurement state, responsible person, notes, photo, and persisted `source_discipline`. | Row/report ids, audit/deletion fields, derived ownership/state. |
| Machinery | Active machinery operational/status/hours/stoppage data and supported references. | Identity/audit/deletion/report ownership. |
| General activity | Active description, location, quantity/unit, notes, display order, and user-entered values. | Identity/audit/deletion/report ownership. |
| Visit | Active visit text/order and user-entered values. | Identity/audit/deletion/report ownership. |
| Incident | Active incident content, severity, corrective/follow-up information, and existing source provenance. | Identity/audit/deletion/report ownership. |

Soft-deleted rows remain absent. `source_discipline` is an existing activity field, not an incident column.

## Lifecycle transitions and invariants

```text
approved + current --open correction--> draft + current (version n+1)
      |                                      |
      |                                      +--cancel--> source approved + current
      |                                      +--submit/review/approve--> approved + current
      +--an open correction exists--> 400 correction_already_open
```

1. Lock and re-read authoritative state before changing a lineage.
2. Source must be approved/current; result must be a current draft before cancellation.
3. Cancellation marks only its result non-current/soft-deleted, restores source current, and marks the request cancelled.
4. Null/not-measured quantity is never rewritten to zero. Explicit zero remains numeric.
5. Measured/null quantity may exist in draft editing but blocks submit with `quantity_unset_invalid`.

## Version-history projection

| Field | Source / semantics |
|---|---|
| `report_id`, `report_date`, `shift`, `version_number`, `is_current`, `status`, `is_locked`, `approved_at`, `created_at` | Existing version state. |
| `modifier_name` | Full display name chosen by existing version audit semantics; null if no identity retained. |
| `correction_reason` | Reason on request whose `result_report` is this version; null for root/no-associated version. |

## Validation rules

| Condition | Required result |
|---|---|
| Submit status is not draft or rejected | 400, `report_not_in_submittable_state` |
| Rejection reason omitted/whitespace | 400, `rejection_reason_required` |
| Trimmed rejection reason is under 10 characters | 400, `rejection_reason_min_length_10` |
| Measured activity has null quantity at submit | 400, `quantity_unset_invalid` and approved Persian message |
| Existing open correction in lineage | 400, `correction_already_open`; no new version/request |
| Explicit activity quantity is zero | Valid save and submit; rendered as numeric zero |
