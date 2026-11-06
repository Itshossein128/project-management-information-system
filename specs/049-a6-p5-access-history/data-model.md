# Data model: A6-P5 access history

The stored row remains `RoleAccessChange` (`role_access_changes`). This phase does not add a second history entity.

## RoleAccessChange

| Field | Meaning | Rule |
| --- | --- | --- |
| id | Stable identifier | Unchanged. Preserved after the subject leaves a project. |
| actor | Person who performed the change | Null only when the actor is already unknown. Not rewritten to a later user. |
| project | Project scope | Null means an organizational event, including a global role change and a successful login. Never filled with an arbitrary project. |
| subject_user | Person the change is about | For recovery, this is the target account, not the requester. |
| role_id, role_name | Role involved, when there is one | `role_id` stays after a controlled role deletion. `role_name` keeps the name as it was. |
| action | What happened | Existing values stay valid. New writes use the vocabulary below. |
| before, after | Difference | JSON objects. Secrets redacted before save. Missing required values stay absent and are labeled unknown on read. |
| created_at | When the row was stored | Not updated when membership status later changes. |

Indexes to add, without rewriting old rows: `(project, created_at)`, `(subject_user, created_at)`, `(actor, created_at)`.

### Action vocabulary

Existing actions already written by earlier phases remain readable. Examples include `role_created`, `role_renamed`, `role_permissions_changed`, `role_deleted`, `roles_replaced`, `override_set`, `override_cleared`, `member_status_changed`, `invitation_created`, `invitation_cancelled`, `positions_replaced`, `sod_break_glass`, and `sod_refusal`.

This phase adds only where the event is not already written:

| Action | When | Project |
| --- | --- | --- |
| login_succeeded | Successful sign-in | Null |
| recovery_requested | Recovery requested | Null |
| sensitive_export | A sensitive export or download path that succeeds | That project |
| final_approval | A final approval path that does not already write a more specific row | That project |

Role versus individual exception is distinguished by action, not by a new column: role actions versus `override_set` and `override_cleared`.

### Redaction

Before save and again before display, walk nested objects and lists. Replace values whose keys are passwords, recovery tokens, access tokens, refresh tokens, or secrets with a fixed redacted marker. Keep sibling keys that describe the access change.

### Transaction

For a sensitive access change, the business update and `RoleAccessChange` insert commit or roll back together. The read API never creates rows.

## Read scopes

| Reader | Rows visible |
| --- | --- |
| Active member with `manage_members` | Rows for that project only |
| `admin` group or superuser | Organizational rows and project rows inside the organization they administer |
| Anyone else | No rows |

Organizational observation does not reveal redacted secrets, wages, rates, or confidential contact values inside `before` / `after`.

## What is not stored

Failed sign-in attempts, ordinary reads, and reconstructed guesses for old missing values.
