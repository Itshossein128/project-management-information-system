# Data model: A6-P6 delivery records

These records are files in this feature directory. They do not add tables. Product data stays in the existing account, membership, role, permission, file, and `RoleAccessChange` models.

## DeliveryPackage

The candidate handoff.

| Field | Rule |
| --- | --- |
| version_id | Git commit of the tree under test. Required. |
| tree_dirty | True when the tested tree had uncommitted changes. Required. |
| environment_name | Named acceptance environment. Empty means the package is not ready to send. |
| accounts_note | Names the synthetic roles used. No password, reset link, or session secret. |
| file_service | `operational` or `blocked_external`. |
| send_channel | `operational`, `not_configured`, or `blocked_external`. |
| acceptor | Customer role expected to answer. Empty until named. |
| sent_at | Empty until the package is actually sent. |
| response_due_at | `sent_at` plus two calendar days. Not a repair deadline. |
| response_at | Empty until a person answers. |
| report_label | `ready_for_acceptance` until `decision` is set. |
| decision | `pending`, `accepted`, or `rejected`. |

A `decision` of `accepted` is the only employer confirmation. It requires a non-empty human signer and `response_at`. The implementation agent cannot set it.

## MatrixCell

One existing operation, one actor situation, one project slot, one surface.

| Field | Rule |
| --- | --- |
| module_id | M01–M29 as named in the spec. |
| operation | Existing action. Not a new business capability. |
| actor_kind | Authorized member, member without the permission, non-member, inactive member, observer, multi-role, grant, deny, or organizational observation, as applicable. |
| project_slot | `A` or `B`. A third project is recorded on the U02 scenario, not as a new slot type. |
| surface | `screen` or `direct`. |
| input_ref | Identifier of the synthetic input. No customer payload and no secret. |
| expected | Allow or refuse, and what must not leak. |
| actual | Observed result. |
| result | `pass`, `fail`, `not_run`, or `not_applicable`. |
| na_reason | Required when `result` is `not_applicable`. |
| evidence_ref | Command, test name, or browser note for this version. |
| defect_id | Required when `result` is `fail`. |
| version_id | Same identity as the package under test. |

Roll-up rule: `not_run` is not a pass. `not_applicable` without `na_reason` is invalid. A direct surface must not be more permissive than the screen surface for the same operation and actor.

## ScenarioResult

One of U01–U20.

| Field | Rule |
| --- | --- |
| scenario_id | U01–U20. |
| requirement_ids | The A6-R identifiers in the spec. |
| technical_status | One of `ready_for_test`, `tested_by_developer`, `blocked_external`. |
| technical_result | `pass`, `fail`, or `not_run`. |
| customer_status | Stays open. `employer_confirmed` only after a human decision. |
| evidence_ref | Technical evidence only. |
| defect_id | Set when the technical result fails. |
| version_id | Candidate identity. |

Technical pass and customer confirmation are stored separately. Twenty groups are a minimum coverage list, not a limit on the number of checks.

## Defect

| Field | Rule |
| --- | --- |
| defect_id | Stable id inside this feature. |
| requirement_ids | At least one A6-R identifier. |
| scenario_ids | Matrix cell or U-scenario. |
| blocking | True when the A.6 commitment cannot be offered while it remains. |
| in_scope | False for commercial gaps outside A.6 and for A6-R54. |
| status | `open`, `fixed`, or `deferred_external`. |
| before_evidence | Failing check recorded before the change. |
| after_evidence | Recheck on the corrected version. Required before `fixed`. |
| criteria_unchanged | Must stay true. A fix that passes by deleting or weakening the scenario is not `fixed`. |

Out-of-scope defects are listed and not implemented.

## AcceptanceMinutes

| Field | Rule |
| --- | --- |
| version_id | Must match `DeliveryPackage.version_id`. |
| scenario_rows | U01–U20 technical result and empty customer decision. |
| limitations | Explicit `blocked_external` and `not_applicable` items. |
| signer | Empty. |
| signed_at | Empty. |

## GuideCheckpoint

The manager guide covers four actions on the existing screens: create an account or membership, assign a role or exception, revoke access, and recover sign-in. Each checkpoint records the screen, the Persian and English label the manager sees, and the direct request that must agree.

## State transitions

```text
ready_for_test
  -> tested_by_developer   when every required cell and scenario is pass, fail, not_applicable, or blocked_external
  -> blocked_external      when a required file or send check cannot run on the delivery environment
tested_by_developer
  -> employer_confirmed    only when a human acceptor accepts the same version_id
```

`employer_confirmed` is not reached by a green test run. A rejected human decision leaves the technical status unchanged and sets `decision` to `rejected`.

## Product data this phase must not reshape

Unless a blocking in-scope defect requires it:

- no new table
- no new permission codename
- no change to the one-hour access-token lifetime
- no deletion of `RoleAccessChange` rows
- no rewrite of membership history when an account or member is deactivated

If a migration is required, it is additive, reversible, and called out in the evidence channel for data preservation.
