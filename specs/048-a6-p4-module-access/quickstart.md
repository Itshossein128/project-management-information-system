# Quickstart validation: A6-P4 module access

## Prerequisites

- PostgreSQL and Redis running for API tests
- API venv at `apps/api/.venv`, Django kept on 4.2.11
- Root `.env` sourced (`DATABASE_URL`, Redis). Prefer `AUDIT_LOG_ASYNC=false` and `CELERY_TASK_ALWAYS_EAGER=true` for local runs
- Two independent projects with synthetic members: allowed, denied, non-member, inactive, observer, multi-role, and observation-capable admin/superuser
- Do not reset or drop the real development database for routine validation

## Shared commands

```bash
cd apps/api/core
set -a && source /home/hossein/Desktop/projects/building-management/.env && set +a
../.venv/bin/python -m pytest permissions/tests projects/tests -q
```

Package-specific modules are added as tasks land. Always keep prior wage, stakeholder-contact, and attachment-signing tests green when those areas change.

## Package 1 — account, project, site

Validate:

1. Project A member cannot read/write project B ids on list, detail, create, update, and a representative action.
2. Inactive member and non-member are refused on selected project routes; observation account reads general data only.
3. `UserLookupView` with `manage_members` returns id/name without mobile/email unless person-contact permission is granted.
4. Roster omits person contacts without that permission.
5. A forbidden button stays forbidden on direct API call.
6. Offline/retry after permission revoke refuses submit and does not send under a switched account.

Record matrix rows for M01–M10 and M14.

## Package 2 — finance, contracts, resources

Validate:

1. Wage/rate hidden without `view_wage`; editable only with `edit_wage`.
2. Commitment/IPC/budget/actual final-approve: creator alone fails; second authorized approver succeeds.
3. `approve_commitment` path is included.
4. Superuser break-glass requires membership, approve permission, non-empty reason, and audit row; admin/staff/HR without superuser fail.
5. Null-creator legacy cannot normal-approve; break-glass with `unknown_creator` is the only emergency close.

Record matrix rows for M13, M15–M21, M26.

## Package 3 — documents, collaboration, management outputs

Validate:

1. Nested report/dashboard/export redaction for wage and contacts.
2. Stakeholder contacts vs person contacts independence.
3. Workflow step action outside stage/project refused.
4. File/link without source permission refused; post-revoke link behavior matches policy. Prefer real storage evidence; if unavailable, mark incomplete.
5. Sensitive events write to `RoleAccessChange` / access-history core; full history UI is out of scope.

Record matrix rows for M11, M12, M22–M25, M27–M29.

## Browser spot checks

On one project in Persian UI:

- Forbidden action control hidden for denied role; direct request still 403/400 as contracted
- Observation account can open allowed read surfaces without write controls that would succeed
- Team add-member search shows minimal fields

## Expected outcomes

- Each package exit: positive and negative evidence for active operations, two projects, or documented N/A
- No alternate path grants more than the canonical policy
- Traceability later maps each A6-R row to preserved / fixed / added / partial with final evidence
- Customer acceptance and release remain outside this feature

## Execution record (2026-11-06)

| Check | Result |
|-------|--------|
| Package-1 pytest suite (see `matrix/package-1.md`) | 46 passed |
| Package-2 pytest suite (see `matrix/package-2.md`) | 65 passed |
| Package-3 pytest suite (see `matrix/package-3.md`) | 16 passed |
| Phase 13 convergence focused suite | 47 passed |
| Live MinIO upload/download / post-revoke signed URL | **Skipped** — MinIO Docker-only in this environment; membership + source-permission ACL unit tests recorded instead |
| RabbitMQ async audit path | N/A — `AUDIT_LOG_ASYNC=false` local; sync audit + `RoleAccessChange` covered |
| Interactive Persian browser UAT | Deferred to P6; technical spot-check via UI/server parity fixtures |
| Customer acceptance (P6) | Not executed |
