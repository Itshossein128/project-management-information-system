# A6-P1: isolated real-service acceptance checks

This suite maps the five user stories and their 16 numbered acceptance scenarios in `specs/045-a6-p1-access-policy/spec.md`. It runs against a real Django server, real PostgreSQL and a real browser/frontend. No API responses are mocked. Browser checks cover the member form in Persian and English, cross-project action visibility, and activity action visibility; API checks exercise the remaining server authorization scenarios. The policy document checks below are static checks, not browser E2E.

## Run

Requirements: installed pnpm dependencies and Playwright Chromium, `apps/api/.venv`, PostgreSQL reachable through the existing `DATABASE_URL` with permission to create a database, and the usual Django environment. From the repository root:

```bash
set -a
source .env
set +a
apps/api/.venv/bin/python e2e/a6-p1/run.py
```

The runner creates a new uniquely named `velora_a6_p1_e2e_*` database, applies migrations, creates synthetic users and records, starts its own API and web servers on temporary ports, and runs Playwright. It never resets an existing database and shuts down only its own servers. It retains the synthetic database for inspection and prints its name; remove it manually when no longer needed. Credentials and tokens for synthetic accounts are in a temporary file restricted to the current user and are removed after the run. The test server uses a local cache for isolated rate-limit counters; production shared-cache settings are unchanged. There is no claim that this tests a multi-process rate limiter.

## Scenario mapping

- US1.1: the two browser tests reject an unavailable role after it is deleted between selection and submission; messages and absence of a partial member are checked in Persian and English.
- US1.2–1.3: real API checks reject mixed valid/invalid roles on create and update, preserving status, roles and the existing effective override.
- US2.1–2.3: visitor reads the legacy catalogue but create, update, delete and import are rejected without altering the existing item; an authorized writer creates an item.
- US3.1–3.3: list, detail and direct helper callers reject an inactive member and accept an active authorized member.
- US4.1: a manager in project A cannot manage project B or organization users; the member page hides actions in project B.
- US4.2–4.3: staff, HR and an inactive member are rejected; a non-member admin and superuser can read public positions but cannot create, edit, delete or manage members.
- US4.4: selected position responses are checked for the named sensitive fields; the policy document records that comprehensive sensitive-data access is deferred to P4. The selected endpoint contains no such fields, so this is not a test of real sensitive-field authorization.
- US5.1 and US5.3: static policy-document checks retain the decision/proposal/unresolved distinctions. These requirements concern the policy artifact, not a fictitious browser screen.
- US5.2: direct API requests show that editing succeeds while deleting and approval fail; the browser checks action visibility for the same edit-only user.

This suite exercises the selected P1 paths, not every endpoint, organization boundary, sensitive field, edge case, or future phase. It is not customer acceptance. Test result artifacts are written under `test-results/a6-p1-real` and may include synthetic user data.
