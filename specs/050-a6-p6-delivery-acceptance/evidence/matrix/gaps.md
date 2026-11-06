# Operations that are not a pass

version_id: `a46161d3530edfb78c8ebf94b4786d991bea0ba7`

A representative direct read, or a named test, is recorded in the batch files. Every other existing action stays `not_run`. `not_run` is not a pass. Screen cells are `not_run` except the member, exception, and history journey in `evidence/browser.md`.

| module_id | operation | actor_kind | project_slot | surface | result | na_reason | evidence_ref |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M14 | superuser break-glass approve without membership | superuser who prepared the report | A | direct | not_run | | `test_superuser_break_glass_can_approve_as_preparer_and_submitter` returned 403. Recorded as D005. The POST open allow/deny tests passed and are the M14 row in batch-1. |
| M01–M29 | create, update, delete, import, approve, and export beyond the named tests | authorized and refused | A/B | direct | not_run | | Not each action was executed on this candidate. |
| M01–M29 | same actions | authorized and refused | A/B | screen | not_run | | Browser evidence covers creating a membership, assigning two roles, the inherit/grant/deny radios, revocation, and access history. Other module screens were not exercised. |

No cell is `not_applicable` without a reason. Combinations that do not exist as an action are not listed as passes.
