# Contract: A6-P6 delivery acceptance

This feature adds no endpoint and no screen. The employer-facing contract is the evidence package. Product behavior remains the contracts in `specs/045-a6-p1-access-policy/contracts/`, `specs/046-a6-p2-project-roles/contracts/`, `specs/047-a6-p3-team-lifecycle/contracts/`, `specs/048-a6-p4-module-access/contracts/module-access.md`, and `specs/049-a6-p5-access-history/contracts/access-history.md`.

## Package the customer receives

A single versioned folder containing:

- the operation matrix for M01–M29
- technical results for U01–U20
- the manager guide in Persian and English
- the accept/reject minutes
- the defect log
- the candidate `version_id`

The November 2026 requirements snapshot is not this package and is not updated.

## Status values

| Recorded status | Meaning |
| --- | --- |
| `ready_for_test` | Named, not yet executed on the candidate |
| `tested_by_developer` | Executed and recorded by the delivery team |
| `employer_confirmed` | A named person accepted this `version_id` |
| `blocked_external` | Needs the live file service, the real send channel, or another external action |

`ready_for_acceptance` is the package label while technical work is recorded and `decision` is still `pending`. It is not `employer_confirmed`.

## Matrix row

A row is valid only when `result` is `pass`, `fail`, `not_run`, or `not_applicable`, and:

- `pass` and `fail` cite evidence for the same `version_id`
- `not_applicable` cites a reason
- `not_run` is never rolled up as success
- `fail` cites a defect
- the direct request result is included beside the screen result for every operation that has both

Actor coverage for an existing operation follows the spec: authorized, lacking permission, non-member, inactive, observer, multi-role, and grant or deny, on two projects, unless the row explains why a combination cannot apply.

## Scenario row

U01–U20 each have a technical result and a customer result. The customer result stays unset in the authored package. Recording a customer pass without `signer` and `response_at` violates the contract.

## Surfaces the scenarios retest

| Scenario | Existing surface |
| --- | --- |
| U01, U08, U11 | Account administration and project member create/update |
| U02, U03, U04, U06 | Member roles and permission exceptions on two projects |
| U05 | Project-local role create/update |
| U07, U19 | Invite acceptance or secure account create; sign-in, refresh, sign-out, recovery |
| U09 | Organization account active flag and later requests |
| U10 | Visitor read versus create, change, delete, import, and approve, including the legacy items path |
| U12, U16 | Selected edit versus delete, approve, and sensitive export; second approver |
| U13, U14, U15 | Wage, stakeholder contact, person lookup, nested export, and file or link |
| U17 | Queued work after revoke and after account switch |
| U18 | Project and organization access-history reads |
| U20 | The full matrix plus these minutes |

Error text shown to the manager is the existing bilingual message for the rule that fired. The guide quotes those messages; it does not invent a second wording.

## File and send evidence

Live file evidence is an upload and download on the delivery object store, including a private file from the other project and a check after revocation. Permission-only tests remain API evidence and do not fill this cell.

Live send evidence is a real `sent` result from the existing account-message delivery to the agreed test recipient. `not_configured` and `not_sent` stay `blocked_external` for the send cell. The secure account path can still pass U07's equivalent branch, and the package must say the message was not sent.

## Secrets

Shared evidence, history rows, and the guide omit passwords, recovery links, access tokens, and refresh tokens. Synthetic users are named by role. The password is given to the acceptor outside the package.

## Fix contract

An in-scope blocking defect is fixed only by extending the current helper or screen that owns the failing behavior. The before-fail and after-pass are both stored. The scenario text stays the same. An out-of-scope item is stored with `in_scope: false` and no product change.

## Human decision

```text
decision = accepted
  requires signer, response_at, and the same version_id
decision = rejected
  requires signer, response_at, and the disagreed rows
decision = pending
  is the only authored state of this feature
```
