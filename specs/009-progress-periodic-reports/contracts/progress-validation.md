# Contract: Progress validation rules

Applies to: manual progress, daily-report recalculation, technical approve, measurement approve.

## Rules

| Rule | Error code | HTTP | Behavior |
|------|------------|------|----------|
| No approved measurement definition | `measurement_not_approved` | 400 | Block progress write / recalc apply |
| Quantity method without approved total+unit | `incomplete_measurement_basis` | 400 | Block approve & progress write |
| Weighted milestones incomplete or weights sum ≠ 1 (±0.01) | `incomplete_measurement_basis` | 400 | Block approve & progress write |
| Computed cumulative % > 100 without covering approved quantity change | `progress_exceeds_100` | 400 | **Reject** — do not clamp and return 200 |
| Attempt to treat photo-only as technical approval | `photo_not_technical_approval` | 400 | Reject approve action if only evidence is photo and no approve permission path |
| Figure value change without override trail | `figure_immutable` | 400/403 | Block |

## >100% with approved quantity change

If an `ActivityQuantityChange` is **approved** and new total > old total:

- Percent is computed against **new** total.
- Still reject if quantity implies % > 100 of new total.

## Daily-report recalculation

On daily report approve: existing recalc path MUST adopt reject semantics (fail or skip activity with error logged / surfaced) instead of silent cap-as-success. Prefer fail the recalc for that activity with `progress_exceeds_100` visible to operator.

## Compatibility

- Existing clients that relied on clamp MUST see 400 after this feature; document in ENDPOINTS / changelog.
- S-curve reads remain; values never invent 100% for incomplete milestone method.
