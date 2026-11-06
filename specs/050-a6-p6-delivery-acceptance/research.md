# Research: A6-P6 delivery acceptance

## Decision: Keep acceptance records in this feature folder

The delivery matrix, scenario results, defect log, manager guide, and unsigned minutes are files under `specs/050-a6-p6-delivery-acceptance/`. They are not Django models and not a second access-control product.

**Rationale**: A6-P6 proves and hands over behavior that A6-P1 through A6-P5 already specify. A new acceptance application would duplicate the product and would not be what the employer signs.

**Alternatives considered**: A database of matrix cells inside the product was rejected because the employer package is a versioned report, not an operational module. Editing `output/a6-requirements-2026-11-04/` was rejected because that directory is the 14 Aban 1405 snapshot and must stay unchanged.

## Decision: Reuse the A6-P4 operation inventory, then re-execute it

`specs/048-a6-p4-module-access/matrix/` is the inventory of active operations for M01–M29. P6 copies that row shape into its own evidence files and runs the rows again on the candidate tree. A P4 pass, a skipped test, or an expected failure is not an acceptance pass.

**Rationale**: The 29 areas and their routes already exist. Rebuilding the inventory would hide gaps. Historical counts, including the 126-test snapshot, do not identify the candidate version.

**Alternatives considered**: Generating a fresh route list from scratch was rejected as a parallel catalog. Treating the P4 execution record as final was rejected because P4 explicitly left customer UAT and live file evidence to P6.

## Decision: Do not add an API or a screen for the package

Acceptance uses the existing API and the existing screens: account administration, project members, local roles, permission exceptions, access history, sign-in, recovery, and sign-out. Contracts in `specs/045` through `specs/049` remain the behavior contracts. P6 records whether those contracts hold on the candidate version.

**Rationale**: The manager guide is valuable only if it walks the product the customer will use. A new acceptance UI would not prove that product.

**Alternatives considered**: A dedicated UAT console was rejected. New permission codenames or a second history table were rejected.

## Decision: Prove the A6-P5 handoff by re-running its quickstart

Before U18 can be marked tested by the developer, the command in `specs/049-a6-p5-access-history/quickstart.md` is run on the current tree and the result is copied into this feature's evidence. Checked tasks in P5 are not that evidence. If the required P5 behavior is absent, P6 stops and reports the prerequisite. It does not recreate the P5 feature.

**Rationale**: The P6 spec depends on a testable history handoff. The P5 folder and checked tasks exist, and this planning step did not re-run those tests.

**Alternatives considered**: Trusting `tasks.md` checkboxes was rejected. Re-implementing history inside P6 was rejected.

## Decision: Separate the five evidence channels

Each report states, separately:

- data-preservation check, only if a blocking fix adds a migration
- direct API requests, via pytest against the isolated test database
- browser, via Playwright against the running API without mocked responses
- real file and real send channel
- customer confirmation, which stays empty until a person answers

Pytest, typecheck, and a browser trace do not substitute for one another.

**Rationale**: The spec requires these results to stay distinct. The repository already has pytest modules for the access rules and a real-stack Playwright pattern in `e2e/tests/a6-p1-real.e2e.spec.ts`.

**Alternatives considered**: One green suite as the acceptance result was rejected.

## Decision: Live file evidence is the MinIO integration test, or an explicit external block

`apps/api/core/storage/tests_integration.py` runs only when `AWS_S3_ENDPOINT_URL` is set and MinIO answers. `apps/api/core/storage/tests/test_stored_file_access.py` and the attachment-signing tests prove the permission decision without the object store. Those unit results stay in the API channel. The file channel remains `blocked_external` until the integration test, or an equivalent upload and download on the delivery environment, is recorded. A mocked presign is not that record.

**Rationale**: P4 already recorded live MinIO as skipped in this environment. The P6 spec forbids promoting that skip to a pass.

**Alternatives considered**: Calling the unit ACL tests "real file service" was rejected. Standing up object storage inside the acceptance record was rejected; availability is an environment fact, not a new subsystem.

## Decision: A real invite or recovery send uses the existing delivery gate

`notifications.services.delivery.email_is_operational` and `sms_is_operational` define an operational channel. `deliver_account_message` sends only to `TEAM_DELIVERY_TEST_RECIPIENT`. The default email backend is the console backend, and the default SMS provider is console; both mean `not_configured`. P6 does not choose a new provider. When the channel is not operational, the secure account-creation path from A6-P3 is the tested equivalent, and the package must not say the message was sent. Recovery links stay one-time. Issued access lasts at most the current one-hour access-token lifetime and is not refreshed after sign-out.

**Rationale**: A6-P3 already fixed this rule. Console output is not a customer channel.

**Alternatives considered**: Adding an email or SMS provider in this phase was rejected. Treating a patched `send_mail` in unit tests as delivery evidence was rejected.

## Decision: Blocking fixes extend current helpers and start from a failing test

A blocking defect is fixed in the existing permission, membership, redaction, approval, storage, or history code. The failing test is recorded before the fix, and the same test plus the affected scenario are recorded after it. The acceptance wording is not weakened. Defects outside A.6 are listed and not built. A6-R54 stays out.

Expected schema change is none. If a fix needs stored data, the migration is additive, keeps existing rows, and has a reverse path. The development database is not dropped. Historical access rows are not deleted to make a test pass.

**Rationale**: Constitution principles IV, V, and VI, and the P6 boundary, allow repair of A.6 gaps and forbid a parallel implementation.

**Alternatives considered**: A new authorization layer was rejected. Resetting the development database was rejected.

## Decision: Version identity is the git commit plus a dirty-tree flag

The candidate version written on every evidence row is `git rev-parse HEAD` and whether the tree was dirty. The offered package and the tested tree must be that same identity. Employer response is due two calendar days after the recorded send time, including all weekdays, and that due time is not a promise that defects will be fixed by then. The minutes keep the signer and signature time empty until a human response is recorded. No automation fills them.

**Rationale**: The spec separates technical readiness from employer confirmation and counts the response window from the actual send.

**Alternatives considered**: A marketing version number with no commit identity was rejected. Auto-signing the minutes when tests pass was rejected.
