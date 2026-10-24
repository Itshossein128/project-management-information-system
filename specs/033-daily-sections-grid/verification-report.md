# Verification report — feature 033 remaining stories

Date: 2026-10-25

## What was implemented

- Concrete pour validation (`volume_must_be_positive`, sampling test information, foreign batching-plant reference) and idempotent linkage to `risk.Inspection`.
- Structured narrative validation and aggregation for issues, barriers, visits, HSE incidents, and general activities, including markup stripping and HSE notifications.
- Activity image attachment checks (hostile ZIP/EXE signatures, 10 MB limit, version and project scope) with a local storage key when MinIO is not configured.
- Aggregation fingerprint coverage for the new section families, ordered derived rows, and `GET …/provenance/{derived_kind}/{derived_row}/`.
- Unit-panel editors for concrete, general activities, issues, visits, and HSE, plus summary provenance and attachment-count components. Persian and English strings were added together.
- The daily-summary serializer now returns complete concrete fields (including sampling/test/QC-link information), ordered structured general/issue/visit/HSE rows, and per-section attachment counts. Attachment links are emitted only for an authorized project member and point to the permission-checked source attachment collection; storage keys are never exposed.
- The activity editor now provides JPEG/PNG attachment upload feedback and client-side type/size prechecks. It deliberately presents no attachment gallery or object-store URL.

## Evidence (2026-10-25)

All backend commands used the isolated `ipcas_h033` PostgreSQL database on port 5433 (`DATABASE_URL` was rewritten only for the command); the shared `test_ipcas` database was not used.

| Check | Result | What it proves |
|---|---:|---|
| `pnpm typecheck` | PASS | `react-router typegen && tsc` completed with no TypeScript errors. |
| `manage.py makemigrations --check --dry-run` | PASS | No model migration drift. Django emitted only the known `django_ratelimit.W001` Redis-cache support warning. |
| Concrete/narrative/attachment + summary-contract pytest selection | PASS — 56 passed in 3.68s | Concrete, structured narrative, attachment validation/authorization, serializer payload, and summary attachment-count behavior on PostgreSQL. |
| Aggregation pytest selection | PASS — 44 passed in 5.74s | Eligibility, provenance, completeness, idempotency, machinery dedupe, receipt-only rules, structured transfer, and attachment-count aggregation. |

The new serializer regression assertions specifically prove that a serialized summary has ordered general activities, issues/barriers, visits, HSE severity/notification data, and a count-only attachment payload when no request user is supplied.

## Boundaries

- This run does not prove browser behavior. Neither API (`:8000`) nor web (`:5173`) was running, so the required bilingual Playwright `daily-sections` path was not created or executed in this pass.
- MinIO and RabbitMQ are not part of this local run. Attachment tests prove refusal, metadata persistence, counts, and permission gating—not object-store retrieval, preview delivery, or a successful MinIO upload.
- The broad cross-domain suite requested by T061 (`sub_reports field_reports project_templates inventory risk -x`) was not run; the two focused feature selections above are the actual backend evidence.
- Usability criteria that need a person using the product are not claimed.
