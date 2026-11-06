# Data Model: A6-P4 module access

This phase mostly reuses existing entities. Changes are additive policy fields and catalog entries, not a new tenancy model.

## Entities

### ProjectMember (existing)

- Links a user to a project with status, roles, positions, and overrides.
- Only `active` grants operational authority.
- Roster reads for active members may show name, roles, and positions without mobile/email unless person-contact permission is present.

### Role / RolePermission / PermissionOverride (existing)

- Effective permission = roles ± grant/deny overrides (A6-P2 contract).
- New catalog codename for person contacts (design name `view_person_contacts`) is independent of `view_sensitive_contacts`.
- Existing `view_wage` / `edit_wage` remain the wage boundary.

### User (existing)

- Organizational account fields used by directory and lookup.
- Full organization directory remains behind explicit account-administration authority from A6-P3, not project-manager or bare HR/staff labels.

### RoleAccessChange (existing)

- Base history writer from A6-P2/P3.
- P4 must record: sensitive access denials where required, SoD refusals when useful for evidence, and every successful break-glass final approve with actor, project, record, reason, exception flag, before/after.
- Full history screen remains P5; durable write is required in P4.

### SoD-covered transactional records (existing domain models)

- Examples already calling or needing the helper: budget versions/changes, actual costs, IPC, workflow final steps, HR exceptions, commitments.
- Required attributes for new rows: non-null attributable creator (`created_by` or domain equivalent). System jobs use an explicit system actor identity, not a forged human.
- Legacy null creator: blocked from normal final approve until attribution repair is audited, or break-glass with reason `unknown_creator`.

### File / attachment / signed link (existing storage & documents)

- Access depends on source resource permission and project membership/policy, not generic project membership alone.
- Link issuance and download re-check current authority and link lifetime.

### Offline queue item (existing client queue)

- Bound to actor identity.
- On resume/retry, current session user and current effective permission are re-evaluated.
- Account switch must not submit another actor’s payload.

## Validation rules

1. Cross-project foreign keys on write/action are rejected; no partial save.
2. Person-contact fields are omitted server-side without `view_person_contacts`.
3. Stakeholder-contact fields remain gated by `view_sensitive_contacts` only.
4. Self final-approve raises `sod_self_approve` unless explicit superuser break-glass with reason and audit succeeds.
5. Null creator does not skip SoD.
6. Break-glass without durable audit write does not approve.

## State transitions (SoD final approve)

```text
draft/submitted --(second authorized approver)--> approved
draft/submitted --(same creator, no break-glass)--> rejected sod_self_approve
draft/submitted --(superuser + membership + approve perm + reason + audit)--> approved (break-glass)
null-creator legacy --(normal path)--> rejected
null-creator legacy --(attribution repair + audit)--> attributable --> normal path
null-creator legacy --(break-glass reason unknown_creator)--> approved
```

## Package matrix entity

Not a database table. Working artifact per package listing: module area, operation, methods/paths, roles tested, projects A/B, expected allow/deny, result, evidence, defect class, N/A reason.
