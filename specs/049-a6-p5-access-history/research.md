# Research: A6-P5 access history

## Decision: Extend `RoleAccessChange` instead of a second history store

The base trail already lives in `master_data.RoleAccessChange` and is written by `permissions.role_services.record_access_change`. Project members already show the latest fifty rows from `GET /api/v1/projects/{id}/access-changes/`. Login, recovery, final approval, and sensitive export are not all represented there yet. Request `AuditLog` rows are a different record: they store redacted request bodies for successful writes and swallow write errors.

**Rationale**: The specification asks to consume the P2–P4 core, not to rebuild history or invent past rows. One store keeps before/after, actor, subject, project, and time in the place the later screen already reads.

**Alternatives considered**: Reading only `AuditLog` was rejected because a request body is not a before/after access change. A new table was rejected because it would split the trail the earlier phases already write.

## Decision: Sensitive access changes and their trail commit together

`record_access_change` today inserts outside a guaranteed transaction. `AuditLogMiddleware` logs an exception and still returns the business response. For role, override, membership-status, and account-status changes, the insert must run in the same database transaction as the change. If the insert fails, the transaction rolls back and the API reports failure. A change that did not happen must not insert a success row.

Ordinary request audit stays best-effort. This phase does not make every HTTP write fail when request logging fails.

**Rationale**: The specification forbids announcing a successful sensitive access change that has no recoverable trail, and forbids a success record for a change that did not happen. Applying that rule to every request log would turn unrelated logging faults into business failures.

**Alternatives considered**: Leaving the current swallow-and-continue behavior was rejected for sensitive access changes. A queue with later reconciliation was rejected because this phase has no new messaging system and the local eager-task mode would not prove delivery durability.

## Decision: Who may read

`manage_members` on an active membership authorizes the project history page and the project endpoint, including filters. An organizational administrator (`admin` group) or superuser may read an organization history endpoint, including rows whose project is null. That read does not grant project writes. Staff, the HR group, and the observation exception do not grant history by themselves. Another project's rows are absent, not returned empty as if the caller were authorized for that project.

**Rationale**: This matches the specification and Constitution I. Project managers already hold `manage_members` through the project-manager role. No new permission codename is required.

**Alternatives considered**: A new `view_access_history` codename was rejected as a parallel permission the specification does not ask for. Letting every project member read the full before/after trail was rejected because the audience is the audit officer and the team manager.

## Decision: Secrets are removed before save and again before display

Reuse the recursive key walk already used by audit middleware for password, token, secret, and recovery fields. Apply it to `before` and `after` inside `record_access_change`. The read serializer applies the same walk so older rows cannot leak a secret that was stored before this rule. Redaction replaces the secret value and keeps the surrounding access difference.

**Rationale**: Nested secrets are already the failure mode called out for request audit. Doing it only in the browser would leave the API and exports exposed.

**Alternatives considered**: Relying only on middleware redaction was rejected because access-history JSON is written by domain services, not only by that middleware.

## Decision: Sensitive events use explicit actions on the same row

Successful login writes `login_succeeded` with the signed-in account as subject and a null project. Failed login writes nothing. A recovery request writes `recovery_requested` with the requester as actor and the target account as subject, without the token. Final approval and a sensitive export write their own actions when those existing paths succeed. Coverage is a direct test of those paths, not an assumption from write middleware.

**Rationale**: The specification separates actor from target and refuses to treat ordinary write logging as proof of download coverage.

**Alternatives considered**: Logging every GET and every failed login was rejected by the specification.

## Decision: Unknown past values stay labeled unknown

Do not backfill missing before/after from current roles. The screen shows an explicit unknown label when a required value is absent. New writes must include the difference.

**Rationale**: The specification forbids fabricated reconstruction.

## Decision: Verification distinguishes sync tests from delivery durability

Pytest uses the test database and the current eager/sync settings. That evidence does not prove a future asynchronous audit worker. The plan states that limit in `quickstart.md`. Browser checks cover the Persian and English history screens, filters, and a direct forbidden request.
