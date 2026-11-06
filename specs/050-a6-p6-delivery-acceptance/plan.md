# Implementation Plan: آزمون مستقل، راهنمای مدیر و پذیرش کارفرما (A6-P6)

**Branch**: `develop` (feature directory `050-a6-p6-delivery-acceptance`; this command did not create a git branch) | **Date**: 2026-11-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/050-a6-p6-delivery-acceptance/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Prove the non-optional A.6 commitment on one candidate version and hand the employer an unsigned package. Re-run the existing access, membership, file-permission, offline, and history checks; record a positive and negative matrix for all 29 existing areas on two projects; walk the current manager screens in Persian and English; and repair only blocking gaps inside A.6. Evidence is a versioned file package in this feature directory. No new access-control product, endpoint, or permission is added. Employer confirmation stays empty until a person answers. The response window is two calendar days from send and is not a repair promise.

## Technical Context

**Language/Version**: Python 3 with Django 4.2.11 and Django REST Framework; TypeScript on React Router 7 and Vite

**Primary Dependencies**: Existing project permission helpers, membership and local-role services, redaction and separation-of-duties guards, `RoleAccessChange`, account-message delivery, storage ACL, and the current member, role, history, and sign-in screens

**Storage**: PostgreSQL for product data. Redis for the API process. Acceptance records are files, not new tables. Object storage is required only for the live file channel.

**Testing**: pytest on the isolated test database; Playwright against the running API without mocked responses; MinIO integration only when the endpoint is configured; send-channel evidence only through the existing delivery gate

**Target Platform**: Linux API and a desktop browser for the manager path. The acceptance environment is not the customer's daily operational environment.

**Project Type**: Web application, `apps/api` and `apps/web`, plus a document package under this feature

**Performance Goals**: No new throughput target. History and member screens stay within their current interactive behavior.

**Constraints**: Constitution 1.1.0. Django stays on 4.2. Do not install the full development requirements file. Do not reset the development database. Do not edit the 14 Aban 1405 requirements snapshot. Do not put secrets in shared evidence. Do not sign for the employer. A6-R54 and out-of-scope commercial gaps are recorded, not built. Checked P5 tasks are not the history handoff.

**Scale/Scope**: Requirements A6-R01 through A6-R53 retested, with A6-R52 and A6-R53 as the delivery rows. Twenty scenario groups. Twenty-nine existing module areas. Three execution batches inherited from A6-P4.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Before research | After design |
| --- | --- | --- |
| I. Server-enforced authorization | Pass. Retest uses the server as the boundary. The guide does not treat a hidden button as authorization. Observation stays read-only. | Pass. The contract refuses a direct path that is more open than the screen and does not add a client-only rule. |
| II. Data integrity | Pass. No schema change is planned. A later blocking fix must preserve rows and provide a reverse migration. | Pass. The data model forbids deleting history or membership trail to obtain a pass. |
| III. Bilingual experience | Pass. The manager path and errors are checked in Persian and English. Permission codes stay stable. | Pass. The guide quotes the existing localized messages. |
| IV. Safe mutations | Pass. Acceptance does not run destructive checks on the customer environment. Revocation and deactivation keep recorded documents. | Pass. Live send is limited to the agreed test recipient. Minutes cannot be auto-signed. |
| V. Minimal coherent changes | Pass. Extend current helpers only when a blocking defect is reproduced. | Pass. Research rejects a new acceptance application, ACL, and history table. |
| VI. Evidence-based verification | Pass. API, browser, migration, live file, and customer confirmation are separate. Old green runs are not this version. | Pass. Quickstart names the commands and the non-pass rule for skipped tests. |
| VII. Practical UX | Pass. The guide follows the existing member, role, history, and recovery screens. | Pass. No new acceptance console is introduced. |

No gate violations. Complexity tracking is empty.

Post-design re-check: the same gates pass. Phase 1 adds records and a retest contract only.

## Project Structure

### Documentation (this feature)

```text
specs/050-a6-p6-delivery-acceptance/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/delivery-acceptance.md
├── checklists/requirements.md
├── spec.md
└── evidence/          # created during implementation, not by this plan
```

`tasks.md` is created later by `/speckit-tasks`.

### Source Code (repository root)

```text
apps/api/core/permissions/
apps/api/core/projects/
apps/api/core/authentication/
apps/api/core/storage/tests_integration.py
apps/api/core/notifications/services/delivery.py
apps/api/core/documents/
apps/api/core/sub_reports/
apps/web/src/app/routes/
e2e/tests/a6-p1-real.e2e.spec.ts
specs/048-a6-p4-module-access/matrix/
specs/049-a6-p5-access-history/quickstart.md
```

**Structure Decision**: Product code stays where it is. This phase writes evidence beside the spec and changes application code only to close a reproduced in-scope defect in the module that already owns that behavior. The P4 matrix is the operation inventory. The P5 quickstart is the history gate. Playwright follows the existing real-API spec rather than a mocked harness.

## Execution order

1. Record `version_id` and confirm the P5 quickstart on that tree.
2. Re-execute the direct-request matrix in the three existing batches. Fill cells from [data-model.md](./data-model.md).
3. Run the Persian and English manager path on the existing screens, and match each result to the direct request.
4. Run the live file and live send checks, or mark those cells `blocked_external`.
5. Fix blocking in-scope failures, retest the affected rows, and leave the acceptance text unchanged.
6. Publish the guide and the unsigned minutes. Leave the package at `ready_for_acceptance`.

## Migration, compatibility, and rollback

No migration is part of the planned design. Existing accounts, memberships, roles, and access-history rows remain readable.

If implementation finds a blocking defect that needs stored data, the migration is added in the app that owns the table, applies forward without deleting history, and documents the reverse migration in the evidence note. Rollback of a code fix is reverting that fix and its test, not resetting PostgreSQL. Evidence files are additive and can be deleted without affecting the product.

The candidate offered to the employer is the same commit, including the same dirty-tree flag, as the tree the checks ran on.

## Complexity Tracking

No constitution violation requires a justification.
